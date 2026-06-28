import pandas as pd


def total_revenue(data, schema):

    revenue_col = schema.get("revenue")

    if revenue_col is None:
        return None

    return data[revenue_col].sum()


def average_satisfaction(data, schema):

    satisfaction_col = schema.get("satisfaction")

    if satisfaction_col is None:
        return None

    return data[satisfaction_col].mean()


def average_response(data, schema):

    response_col = schema.get("response")

    if response_col is None:
        return None

    return data[response_col].mean()


def resolution_rate(data, schema):

    status_col = schema.get("status")

    if status_col is None:
        return None

    resolved_values = [
        "resolved",
        "closed",
        "completed",
        "done",
        "finished"
    ]

    resolved_count = len(
        data[
            data[status_col]
            .astype(str)
            .str.lower()
            .isin(resolved_values)
        ]
    )

    total_count = len(data)

    if total_count == 0:
        return 0

    return (resolved_count / total_count) * 100


KPI_REGISTRY = {

    "Total Revenue Impact": {
        "function": total_revenue,
        "format": "currency"
    },

    "Average Satisfaction": {
        "function": average_satisfaction,
        "format": "decimal"
    },

    "Average Response": {
        "function": average_response,
        "format": "decimal"
    },

    "Resolution Rate": {
        "function": resolution_rate,
        "format": "percentage"
    }
}



def calculate_kpis(data, schema):

    results = {}


    for kpi_name, Kpi_function in KPI_REGISTRY.items():
       
        Kpi_func = Kpi_function["function"]

        try:
            results[kpi_name] = {
                "value": Kpi_func(data, schema), 
                "format": Kpi_function["format"]
            }

        except Exception:
            results[kpi_name] = None

    return results