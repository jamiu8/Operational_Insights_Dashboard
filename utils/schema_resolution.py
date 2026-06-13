import pandas as pd

def resolve_schema(
    business_schema
):
    business = {}

    for col in business_schema.keys():

        values = business_schema[col]

        if len(values) == 0:
            business[col] = None
        
        else:
            business[col] = values[0]

    return business
    
    