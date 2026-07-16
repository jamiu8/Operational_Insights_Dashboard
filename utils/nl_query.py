from datetime import datetime, timedelta

class QueryEngine():
    
    def __init__(self, df, resolved_business_schema, dimension_schema, date_time):
        self.df = df
        self.resolved_business_schema = resolved_business_schema
        self.dimension_schema = dimension_schema
        self.date_time = date_time


    def parse_query(self, query):

        query = query.strip().lower()

        parsed = {
            "metric": None,
            "dimension": None,
            "aggregation": None,
            "selection": None,
            "top N": {
                "direction": None,
                "size": None
            }
        }

        aggregation_keywords = {
            "sum": ["sum", "total", "add", "addition"],
            "mean": ["average", "avg", "mean"],
            "count": ["count", "number"]
        }

        selection_keywords = {
            "max": ["highest", "largest", "most", "maximum", "max"],
            "min": ["lowest", "least", "minimum", "min"]
        }

        rank_keywords = {
            "top": ["top", "first"],
            "bottom": ["bottom", "last"]
        }

        # Detect metric
        for concept in self.resolved_business_schema:
            if concept in query:
                parsed["metric"] = concept
                break

        # Detect dimension
        for concept in self.dimension_schema:
            if concept in query:
                parsed["dimension"] = concept
                break

        # Detect aggregation
        for agg, keywords in aggregation_keywords.items():
            if any(word in query for word in keywords):
                parsed["aggregation"] = agg
                break

        # Detect selection
        for sel, keywords in selection_keywords.items():
            if any(word in query for word in keywords):
                parsed["selection"] = sel
                break

        # Detect ranking
        words = query.split(" ")

        for index, word in enumerate(words):
            
            for direction, keywords in rank_keywords.items():

                if word in keywords:
                    parsed["top N"]["direction"] = direction
                    
                    if index + 1 < len(words):
                        next_word = words[index + 1]

                        if next_word.isdigit():
                            parsed["top N"]["size"] = int(next_word)
                    break


        # Defaults
        if parsed["aggregation"] is None:
            parsed["aggregation"] = "sum"

        return parsed

    def extract_filters(self, query):
        
        filters = {}
        query = query.lower()
        all_schema = {
            **self.resolved_business_schema,
            **self.dimension_schema
        }
        for concept, columns in all_schema.items():
            
            if isinstance(columns, str):
                columns = [columns]

            for column in columns:
                unique_values = (self.df[column].dropna()
                        .astype(str)
                        .unique())
                
                for values in unique_values:
                    if values.lower() in query:
                        filters[concept] = {
                            "column": column,
                            "value": values
                        }

                        break

        return filters
    
    def extract_date_filter(self, query):

        query = query.lower()

        filter_date = {
            "start date": None,
            "end date": None
        }

        today = datetime.today()

        if "today" in query:
            filter_date["start date"] = today.date()
            filter_date["end date"] = today.date()

        elif "yesterday" in query:
            yesterday = today - timedelta(days=1)

            filter_date["start date"] = yesterday.date()
            filter_date["end date"] = yesterday.date()

        elif "this year" in query:
            filter_date["start date"] = datetime(
                today.year,
                1,
                1
            )

            filter_date["end date"] = today.date()

        return filter_date
  

    def execute_query(
        self,
        query,
        parsed_query
    ):
        
        filters = self.extract_filters(query)
        date_filter = self.extract_date_filter(query)
        print(filters)
        working_df = self.df.copy()

        for _, details in filters.items():
            working_df = working_df[
                working_df[
                    details["column"]] == details["value"]         
            ]

        if date_filter["start date"] is not None:
            date_column = self.date_time[0]
            working_df = working_df[
                (working_df[date_column] >= date_filter["start date"])
                &
                (working_df[date_column] <= date_filter["end date"])
            ]
        
        if working_df.empty:
            return "No records match the selected filters."

        if parsed_query["metric"] is None:
            return "I couldn't understand your question. Ask Relevant questions"

        metric_col = self.resolved_business_schema[
            parsed_query["metric"]
        ]

        dimension = parsed_query["dimension"]

        aggregation = parsed_query["aggregation"]

        direction = parsed_query["top N"]["direction"]
        size = parsed_query["top N"]["size"]


        if dimension:

            dimension_col = self.dimension_schema[dimension][0]

            grouped = (
                working_df
                .groupby(dimension_col)[metric_col]
            )

            if aggregation == "sum" and parsed_query["metric"] != "status":
                result = grouped.sum().reset_index()

            elif aggregation == "mean" and parsed_query["metric"] != "status":
                result = grouped.mean().reset_index()


            elif aggregation == "count":
                result = grouped.count().reset_index()

            else:
                return "Unsupported aggregation."
            
            if direction:
                if direction == "bottom":
                    result = result.sort_values(metric_col)

                if direction == "top":
                    result = result.sort_values(metric_col, ascending= False)

            if size:
                result = result.head(size)
            
        elif dimension is None:

            if aggregation == "sum" and parsed_query["metric"] != "status":
                solution = working_df[metric_col].sum()
                return (
                    f"Total {parsed_query['metric']} "
                    f"is {solution:,.2f}")

            elif aggregation == "mean" and parsed_query["metric"] != "status":
                solution = working_df[metric_col].mean()
                return (
                    f"Average {parsed_query['metric']} "
                    f"is {solution:,.2f}")

            elif aggregation == "count":
                return (
                    f"Total number of {parsed_query['metric']} "
                    f"is {solution:,}")

            else:
                return "Unsupported aggregation."
        
        if result.empty:
            return "no result found"
            

        selection = parsed_query["selection"]

        if selection == "max":

            answer = result.loc[
                result[metric_col].idxmax()
            ]

            return (
                f"{answer[dimension_col]} has the highest "
                f"{parsed_query['metric']} "
                f"({answer[metric_col]:,.2f})"
            )

        elif selection == "min":

            answer = result.loc[
                result[metric_col].idxmin()
            ]

            return (
                f"{answer[dimension_col]} has the lowest "
                f"{parsed_query['metric']} "
                f"({answer[metric_col]:,.2f})"
                )

        return result
    
    def ask(self, query):

        parsed = self.parse_query(query)

        return self.execute_query(query, parsed)

