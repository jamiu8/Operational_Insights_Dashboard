import pandas as pd
import streamlit as st

def missing_values_report(df):
    null_values = df.isnull().sum()
    null_percent = (df.isnull().mean() * 100)
    null_table = pd.DataFrame(
        {
            "Column": df.columns,
            "Null_values": null_values.values,
            "Null_percent": null_percent.values
        }
    )
    null_table = null_table[null_table["Null_values"] > 0]

    null_table["Null_percent"]  = null_table["Null_percent"].round(2)

    return null_table


def duplicate_summary(df):
    duplicate = df.duplicated()
    duplicate_counts = duplicate.sum()
    duplicate_percentage = (duplicate.mean() *100)
    return {"duplicate_counts": duplicate_counts,
            "duplicate_percentage": duplicate_percentage}

def duplicate_report(df):
    report = df.copy()
    report["duplicate_status"] = df.duplicated(keep= False)
  
    report2 = report[report["duplicate_status"]]

    return report2.drop(columns=("duplicate_status"))


def high_cardinality_report(
    df,
    categorical_columns,
    threshold=0.8
):
    cardinality = []

  

    for col in categorical_columns:
        ratio = df[col].nunique() / len(df[col])

        if ratio > threshold:
            cardinality.append({
            "Column_name" : col,
            "Unique_Values": df[col].nunique(),
            "Cardinality%": ratio * 100})
 
    return pd.DataFrame(cardinality)

def constant_columns_report(df):

    report = []

    for col in df.columns:

        unique_count = df[col].nunique(dropna=True)

        if unique_count == 1:

            constant_value = (
                df[col]
                .dropna()
                .iloc[0]
            )

            report.append({
                "Column": col,
                "Unique_Values": unique_count,
                "Constant_Value": constant_value
            })

    return pd.DataFrame(report)
    