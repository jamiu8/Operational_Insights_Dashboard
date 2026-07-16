import streamlit as st
import pandas as pd
from utils.load_data import load_data
from utils.schema_detection import detect_schema
from utils.data_quality import missing_values_report, duplicate_report, high_cardinality_report, constant_columns_report
from utils.business_schema import infer_business_schema
from utils.schema_resolution import resolve_schema
from utils.Kpi_Registry import calculate_kpis
from utils.ui import display_kpis
from utils import nl_query
from datetime import datetime, timedelta
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
from utils.isolation_model import run_isolation_forest, plot_anomalies

# set page orientation
st.set_page_config(layout="wide")

# set background color
st.markdown("""<style> .stApp {background-color : cadetblue}""", unsafe_allow_html=True)

# Title of the Page
st.markdown(
    "<h1 style= 'text-align: center;  color: darkslategray;'> Operational Insights Dashboard with Automatic KPI Monitoring </h1>",
            unsafe_allow_html=True)

# upload your file
uploaded_file = st.sidebar.file_uploader(
    "upload your file (csv, xlsx)",
    type= ["csv", "xlsx"]
)
# use uploaded dataset if available
if uploaded_file is not None:
    df = load_data(uploaded_file)

    st.sidebar.success("Custom dataset loaded successfully!")

# Fallback to default dataset
else:
    df = load_data("data/operational_data.csv")

    st.sidebar.info("Using default operational dataset.")

 
# detect and select column types
schema = detect_schema(df)

numeric_columns = schema["numeric"]
categorical_columns = schema["categorical"]
datetime_columns = schema["datetime"]
bool_columns = schema["boolean"]

container = st.container()

with container:
# Display selected column
    with st.expander("Detected Dataset Schema"):

        st.write("#### Numeric Columns")
        if numeric_columns:
            st.write(numeric_columns)
        else:
            st.info("No numeric columns detected")

        st.write("#### Categorical Columns")
        if categorical_columns:
            st.write(categorical_columns)
        else:
            st.info("No categorical columns detected")

        st.write("#### Datetime Columns")
        if datetime_columns:
            st.write(datetime_columns)
        else:
            st.info("No datetime columns detected")

        st.write("#### boolean Columns")
        if bool_columns:
            st.write(bool_columns)
        else:
            st.info("no bool columns detected")

    selected_category = st.sidebar.multiselect(
            "Select a Category",
            categorical_columns,
            default= categorical_columns[:3]
    )

filtered_df = df.copy()

for col in selected_category:
    options = sorted(
        filtered_df[col]
        .dropna()
        .unique()
        .tolist()
    )

    selected_values = st.sidebar.multiselect(
        f"filter {col}",
        options,
        default= options
    )

    filtered_df = filtered_df[
        filtered_df[col]
        .isin(selected_values)
    ]

if filtered_df.empty:
    st.warning("no data to display")
    st.stop()

if datetime_columns:
    for col in datetime_columns:
        filtered_df[col] = pd.to_datetime(
            filtered_df[col],
            errors="coerce"
        )

null_counts = missing_values_report(filtered_df)
duplicates = duplicate_report(filtered_df)
cardinality = high_cardinality_report(filtered_df, categorical_columns)
const_columns = constant_columns_report(filtered_df)


with container:
    with st.expander("Null_Count report"):
        if null_counts.empty:
            st.success("No missing values detected")
        else:
            st.dataframe(null_counts)
            st.write(F"There are {null_counts["Null_values"].sum()} null values in total")

    with st.expander("Duplicated rows"):
        if duplicates.empty:
            st.success("No Duplicate Row Found")
        else:
            st.dataframe(duplicates)
            st.write(F"There are {duplicates["ticket_id"].count()} duplicated rows in total")

    with st.expander("Cardinality Report"):
        if cardinality.empty:
            st.success("There are no High Cardinal Rows")
        else:
            st.dataframe(cardinality)
            st.write(F"There are {cardinality["Unique_Values"].count()} columns with high cardinality")

    with st.expander("Constant Columns"):
        if const_columns.empty:
            st.success("There are no Constant Columns")
        else:
            st.dataframe(const_columns)
            st.write(F"There are {const_columns["Columns"].count()} Constant columns")

data_peek = st.container()

with data_peek:
    row = filtered_df.shape[0]
    column = filtered_df.shape[1]
    col1, col2, col3= st.columns(3)
    col1.metric("rows", row, border= True)
    col3.metric("columns", column, border= True)
    st.dataframe(filtered_df.head(5))

business_schema, dimension_schema = infer_business_schema(filtered_df)
resolved_business_schema = resolve_schema(business_schema)

kpis = calculate_kpis(filtered_df, resolved_business_schema)

st.markdown(
    "<h3 style= 'text-align: center;  color: gainsboro;'> KPIs</h1>",
            unsafe_allow_html=True)

display_kpis(kpis)

with container:
    with st.expander("Business Schema Detection"):
        st.write(business_schema)

status_col = resolved_business_schema.get("status")
revenue_col = resolved_business_schema.get("revenue")
response_col = resolved_business_schema.get("response")
satisfaction_col = resolved_business_schema.get("satisfaction")


dimension_mapping = {}

for concept, candidates in dimension_schema.items():

    if len(candidates) == 1:

        dimension_mapping[concept] = candidates[0]

    elif len(candidates) > 1:

        dimension_mapping[concept] = st.sidebar.selectbox(
            f"{concept.title()} Column",
            candidates
        )

department_col = dimension_mapping.get("department")
date_col = dimension_mapping.get("date")
region_col = dimension_mapping.get("region")
priority_col = dimension_mapping.get("priority")

with container:
    with st.expander("Dimension Schema Detection"):
        st.write(dimension_schema)


st.markdown(
    "<h3 style= 'text-align: center;  color: gainsboro;'> Inquiry into your Dataset</h1>",
            unsafe_allow_html=True)

st.subheader("Ask Your Dataset")

queried = st.text_input("Enter Query relevant to the Dataset (use schema detection above for keywords)")

engine = nl_query.QueryEngine(filtered_df, resolved_business_schema, dimension_schema, datetime_columns)
if st.button("analyze"):
    answer = engine.ask(queried)
    st.write(answer)
    

st.markdown(
    "<h3 style= 'text-align: center;  color: gainsboro;'> Charts and Analysis</h1>",
            unsafe_allow_html=True)

fig = px.pie(
    filtered_df[status_col], 
    names= status_col, color= status_col, color_discrete_map= {"Resolved": "blues", "Unresolved": "coral"}, 
    labels= status_col)
fig.update_layout(height= 300)

df2 = filtered_df[department_col].value_counts().reset_index()
df2.columns = ["department", "counts"]
sorted_df2 = df2.sort_values("counts", ascending=False)
fig2 = px.bar(sorted_df2, x="department", y="counts", color= "counts",
               color_continuous_scale = "haline")
fig2.update_layout(height= 300,
                  xaxis_title="departments",
                  yaxis_title="tickets",
                  font=dict(size=10))


df3 = filtered_df[[region_col, revenue_col]].groupby(region_col).sum().reset_index()
df3.columns = ["regions", "revenue"]
sort_df3 = df3.sort_values("revenue", ascending=False)
fig3 = px.bar(sort_df3, x= "regions", y= "revenue", color= "revenue", color_continuous_scale="thermal")
fig3.update_layout(height= 300,
                  xaxis_title="regions",
                  yaxis_title="revenue",
                  yaxis_tickprefix= "$",
                  yaxis_tickformat= ",.0f",
                  font=dict(size=10))
fig3.update_traces(hovertemplate= "region: %{x} <br> revenue: $%{y:,.2f} <extra></extra>")

col8, col9, col10 = st.columns([1,1,1])

with col8:
    st.subheader("Status Completion(%)")
    st.plotly_chart(fig, width="stretch")

with col9:
    st.subheader("Tickets Per Department")
    st.plotly_chart(fig2, width="stretch")

with col10:
    st.subheader("Regional Revenue($)")
    st.plotly_chart(fig3, width="stretch")

st.subheader("Operational Impact per Department")
filtered_df["month"] = filtered_df[date_col].dt.to_period("M").dt.to_timestamp()
df4 = filtered_df.groupby(["month", department_col]).size().reset_index()
df4.columns = ["month_raised", "department", "ticket_count"]
sort_df4 = df4.sort_values("month_raised", ascending=False)
fig4 = px.line(sort_df4, x= "month_raised", y= "ticket_count", color= "department", markers=True)

fig4.update_layout(height= 300,
                  xaxis_title="Date",
                  yaxis_title="Tickets Issued",
                  font=dict(size=10))
fig4.update_traces(hovertemplate= "department: %{fullData.name} <br> month_raised: %{x} <br> ticket_count: %{y} <extra></extra>",
                   line_shape="spline")
st.plotly_chart(fig4)

st.subheader("Avg Response Time per Department & Region")
col11, col12 = st.columns(2)

df5_1 = filtered_df.groupby(["month", region_col])[response_col].mean().reset_index()
df5_1.columns = ["month", "region", "average_response"]
df5_1 = df5_1.sort_values("month", ascending=False)
fig5_1 = px.line(df5_1, x = "month", y ="average_response", color="region", markers=True)
fig5_1.update_layout(height= 300,
                  xaxis_title="Months",
                  yaxis_title="Average Resolution Time(min)",
                  font=dict(size=10))
fig5_1.update_traces(hovertemplate= "region: %{fullData.name} <br> month: %{x} average_response: %{y:.2f} <extra></extra>",
                   line_shape="spline")

df5_2 = filtered_df.groupby(["month", department_col])[response_col].mean().reset_index()
df5_2.columns = ["month", "department", "average_res"]
df5_2 = df5_2.sort_values("month", ascending=False)
fig5_2 = px.line(df5_2, x = "month", y ="average_res", color="department", markers=True)
fig5_2.update_layout(height= 300,
                  xaxis_title="Months",
                  yaxis_title="Average Resolution Time(min)",
                  font=dict(size=10))
fig5_2.update_traces(hovertemplate= "department: %{fullData.name} <br> month: %{x} average_res: %{y:.2f} <extra></extra>",
                   line_shape="spline")

with col11:
    st.subheader("Region")
    st.plotly_chart(fig5_1, width="stretch")

with col12:
    st.subheader("Department")
    st.plotly_chart(fig5_2, width="stretch")

# Satisfaction impact charts
st.subheader("Avg Satisfaction per Department & Priority")
# Average customer satisfaction by department
df6_1 = (
    filtered_df
    .groupby(department_col)[satisfaction_col]
    .mean()
    .reset_index()
)

df6_1.columns = ["department", "avg_satisfaction"]

# Sort highest satisfaction first
df6_1 = df6_1.sort_values("avg_satisfaction", ascending=False)

# Department satisfaction chart
fig6_1 = px.bar(
    df6_1,
    x="department",
    y="avg_satisfaction",
    color="avg_satisfaction",
    color_continuous_scale="haline",
    title="Average Customer Satisfaction by Department"
)

fig6_1.update_layout(
    height=300,
    xaxis_title="Department",
    yaxis_title="Average Satisfaction Score",
    font=dict(size=10)
)

fig6_1.update_traces(
    hovertemplate=
    "Department: %{x}<br>"
    "Average Satisfaction: %{y:.2f}"
    "<extra></extra>"
)

# SATISFACTION BY PRIORITY
df6_2 = (
    filtered_df
    .groupby(priority_col)[satisfaction_col]
    .mean()
    .reset_index()
)

df6_2.columns = ["priority", "avg_satisfaction"]

# Sort logically
priority_order = ["Low", "Medium", "High", "Critical"]

df6_2["priority"] = pd.Categorical(
    df6_2["priority"],
    categories=priority_order,
    ordered=True
)

df6_2 = df6_2.sort_values("priority")

# Priority satisfaction chart
fig6_2 = px.line(
    df6_2,
    x="priority",
    y="avg_satisfaction",
    markers=True,
    title="Customer Satisfaction by Ticket Priority"
)

fig6_2.update_layout(
    height=300,
    xaxis_title="Priority Level",
    yaxis_title="Average Satisfaction Score",
    font=dict(size=10)
)

fig6_2.update_traces(
    hovertemplate=
    "Priority: %{x}<br>"
    "Average Satisfaction: %{y:.2f}"
    "<extra></extra>",
    line_shape="spline"
)

# DISPLAY CHARTS
col13, col14 = st.columns(2)

with col13:
    st.subheader("Department")
    st.plotly_chart(fig6_1, width="stretch")

with col14:
    st.subheader("Priority")
    st.plotly_chart(fig6_2, width="stretch")

aggregated_table = (filtered_df.groupby
                ("month")
                 [[response_col, satisfaction_col]].mean().reset_index())
aggregated_table.columns = ["month","avg_response", "avg_satisfaction"]

temp_selected = (filtered_df.groupby
                ("month")
                 [revenue_col].sum()
                 .reset_index()
                 .rename(columns={revenue_col: "total_revenue"}))
aggregated_table = aggregated_table.merge(
    temp_selected,
    on="month",
    how="left"
)

temp_selected2 = (filtered_df.groupby
                ("month").size()
                 .reset_index())

temp_selected2.columns = ["month", "total_tickets"]


aggregated_table = aggregated_table.merge(
    temp_selected2,
    on="month",
    how="left"
)

for col in aggregated_table.columns:
    if aggregated_table[col].dtype in ["float64", "float32", "int64"]:
        aggregated_table[col] = aggregated_table[col].round(2) 

features = [
    "avg_response",
    "avg_satisfaction",
    "total_revenue",
    "total_tickets"
]

predicted_table = run_isolation_forest(
    aggregated_table,
    features,
    0.001
)


st.markdown(
    "<h3 style= 'text-align: center;  color: gainsboro;'> KPIs Anomalies Overview</h1>",
            unsafe_allow_html=True)

st.subheader("Anomaly Detection Table Results")
st.dataframe(predicted_table.head(5))


fig_anomaly = plot_anomalies(
    data=predicted_table,
    x_col="month",
    y_col="avg_response",
    title="Operational Response Time Anomaly Detection"
)

st.plotly_chart(
    fig_anomaly
)

anomaly_count = len(
    predicted_table[
        predicted_table["anomaly"] == -1
    ]
)

st.warning(
    f"{anomaly_count} anomalous operational periods detected."
)

