
def parse_query(
    query,
    resolved_business_schema,
    resolved_dimension_schema,
):

    query = query.strip().lower()

    parsed = {
        "metric": None,
        "dimension": None,
        "aggregation": None,
        "selection": None,
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

    # Detect metric
    for concept in resolved_business_schema:
        if concept in query:
            parsed["metric"] = concept
            break

    # Detect dimension
    for concept in resolved_dimension_schema:
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

    # Defaults
    if parsed["aggregation"] is None:
        parsed["aggregation"] = "sum"

    return parsed

def execute_query(
    parsed_query,
    df,
    resolved_business_schema,
    resolved_dimension_schema
):

    if any(v is None for v in (
        parsed_query["metric"],
        parsed_query["dimension"]
    )):
        return "I couldn't understand your question. Ask Relevant questions"

    metric_col = resolved_business_schema[
        parsed_query["metric"]
    ]

    dimension_col = resolved_dimension_schema[
        parsed_query["dimension"]
    ][0]

    grouped = (
        df
        .groupby(dimension_col)[metric_col]
    )

    aggregation = parsed_query["aggregation"]

    if aggregation == "sum" and parsed_query["metric"] != "status":
        result = grouped.sum().reset_index()

    elif aggregation == "mean" and parsed_query["metric"] != "status":
        result = grouped.mean().reset_index()


    elif aggregation == "count":
        result = grouped.count().reset_index()

    else:
        return "Unsupported aggregation."
    

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
    
    return result.sort_values(dimension_col)

