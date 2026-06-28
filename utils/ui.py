import streamlit as st

def format_kpi_value(value, format_type):

    if value is None:
        return "N/A"

    if format_type == "currency":
        return f"${value:,.2f}"

    if format_type == "percentage":
        return f"{value:.2f}%"

    if format_type == "integer":
        return f"{int(value)}"

    if format_type == "decimal":
        return f"{value:.2f}"

    return value


def display_kpis(kpis):

    kpi_items = list(kpis.items())

    cols_per_row = 2

    for i in range(0, len(kpi_items), cols_per_row):

        row = kpi_items[i:i + cols_per_row]

        cols = st.columns(len(row))

        for col, (label, details) in zip(cols, row):

            value = details["value"]
            format_type = details["format"]

            display_value = format_kpi_value(
                value,
                format_type
            )

            col.metric(
                label,
                display_value,
                border=True,
            )