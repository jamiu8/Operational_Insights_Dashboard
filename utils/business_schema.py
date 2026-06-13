import pandas as pd

def infer_business_schema(df):

    schema = {
        "status": [],
        "satisfaction": [],
        "revenue": [],
        "response": []
    }

    dimension_schema = {
        "date": [],
        "priority": [],
        "department": [],
        "region": []
    
    }

    STATUS_KEYWORDS = [
        "status",
        "state",
        "resolution_status",
        "ticket_status",
        "completion"
    ]
    
    SATISFACTION_KEYWORDS = [
        "satisfaction",
        "csat",
        "rating",
        "score",
        "star",
        "point"
    ]
    
    REVENUE_KEYWORDS = [
    "revenue",
    "sales",
    "profit",
    "income",
    "gains",
    "payment"
    ]

    RESPONSE_KEYWORDS = [
        "response",
        "minutes",
        "speed",
        "duration"
    ]

    DATE_KEYWORDS = [
        "date",
        "time",
        "started",
        "ended",
    ]

    PRIORITY_KEYWORDS = [
        "priority",
        "risk",
        "level",
        "attention"
    ]

    DEPARTMENT_KEYWORDS = [
        "department",
        "ward",
        "division",
        "unit",
        "domain",
        "field"
    ]

    REGION_KEYWORDS = [
        "region",
        "district",
        "country",
        "state",
        "province",
        "nation",
        "soceity",
        "county"
    ]

    for col in df.columns:

        col_name = col.lower()

        if any(
            keyword in col_name
            for keyword in STATUS_KEYWORDS):
            schema["status"].append(col)
            continue
            
        if any(
            keyword in col_name
            for keyword in RESPONSE_KEYWORDS):
            schema["response"].append(col)
            continue

        if any(
            keyword in col_name
            for keyword in REVENUE_KEYWORDS):
            schema["revenue"].append(col)
            continue

        if any(
            keyword in col_name
            for keyword in SATISFACTION_KEYWORDS):
            schema["satisfaction"].append(col)
            continue

        if any(
            keyword in col_name
            for keyword in DATE_KEYWORDS):
            dimension_schema["date"].append(col)
            continue

        if any(
            keyword in col_name
            for keyword in PRIORITY_KEYWORDS):
            dimension_schema["priority"].append(col)
            continue

        if any(
            keyword in col_name
            for keyword in DEPARTMENT_KEYWORDS):
            dimension_schema["department"].append(col)
            continue

        if any(
            keyword in col_name
            for keyword in REGION_KEYWORDS):
            dimension_schema["region"].append(col)
            continue

        else:
            pass

    return schema, dimension_schema