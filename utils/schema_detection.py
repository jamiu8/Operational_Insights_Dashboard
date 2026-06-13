import pandas as pd

# function to automatically detect column data type
def detect_schema(df):

    # list for types of data types
    numeric_columns = []
    categorical_columns = []
    datetime_columns = []
    boolean_columns = []

    # loop through all the columns and detect data type
    for col in df.columns:

        series = df[col] # store the selected column as a seperate series

        # test for bool data_type
        if pd.api.types.is_bool_dtype(series):
            boolean_columns.append(col)
            continue
        
        # Test for datetime data type

        if pd.api.types.is_datetime64_any_dtype(series):
            datetime_columns.append(col)
            continue # if the column is already in datetime format

        # detect datetime column stored as stringe
        try:

            date_keywords = [ 
                  "date",
                  "time",
                  "timestamp",
                  "created",
                  "updated",
                  "month"
                ] # match common datetime column names to select likely datetime columns
                # list is important for efficient computational operations

            # loop through common datetime column names
            if any(
                keyword in col.lower()
                for keyword in date_keywords
            ):


                sample = (
                    series.dropna()
                    .astype(str)
                    .head(100)
                )

                # convert to datetime, and use success rate to determine if it is a date time column.
                converted = pd.to_datetime(
                    sample,
                    errors="coerce"
                )

                success_rate = converted.notna().mean()

                if success_rate >= 0.80:
                    datetime_columns.append(col)
                    continue

        except Exception:
            pass

        # detect numerical columns
        if pd.api.types.is_numeric_dtype(series):
            
            # this block of code is to seperate ID columns from numerical columns
            score = 0
            
            if "id" in col.lower():
                score += 5
            
            if series.nunique() / len(series) > 0.98:
                score += 3
            
            if (
                len(series) > 20
                and series.diff().dropna().nunique() < 3
            ):
                score += 2

            if score >= 5:
                categorical_columns.append(col)
            
            else:
                numeric_columns.append(col)
            continue

        categorical_columns.append(col)

    return {
        "numeric": numeric_columns,
        "categorical": categorical_columns,
        "datetime": datetime_columns,
        "boolean": boolean_columns
    }


        
