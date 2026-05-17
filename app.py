import streamlit as st
import pandas as pd
from utils.load_data import load_data
from utils.metrics import kpi_display
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

#set page orientation
st.set_page_config(layout="wide")

# set background color
st.markdown("""<style> .stApp {background-color : cadetblue}""", unsafe_allow_html=True)

# Title of the Page
st.markdown(
    "<h1 style= 'text-align: center;  color: darkslategray;'> Operational Insights Dashboard with Automatic KPI Monitoring </h1>",
            unsafe_allow_html=True)
# Load table
df = load_data("data/operational_data.csv")
deparments = sorted(df["department"].dropna().unique())
regions = sorted(df["region"].unique())
priorities = sorted(df["priority"].unique())
statuses = sorted(df["status"].dropna().unique())


with st.sidebar:
    st.header("Dashboard Filters")
    selected_departments = st.multiselect(
        "Select a department", deparments, default=deparments)

    selected_regions = st.multiselect("Select a region", regions, default= regions)

    selected_status = st.multiselect("Select a status", statuses, default= statuses) 

    selected_priority = st.multiselect("Select a priority", priorities, default= priorities)

filtered_df = df[
    (df["department"].isin(selected_departments)&
     df["region"].isin(selected_regions)&
     df["status"].isin(selected_status)&
     df["priority"].isin(selected_priority))
]
if filtered_df.empty:
    st.warning("no data to display")
    st.stop()

# using a container show number f rws and columns and first 5 rows of data
data_peek = st.container()

with data_peek:
    row = filtered_df.shape[0]
    column = filtered_df.shape[1]
    col1, col2= st.columns([3, 3])
    col1.metric("rows", row)
    col2.metric("columns", column)
    st.dataframe(filtered_df.head(5))

kpis = kpi_display(filtered_df)

st.markdown(
    "<h3 style= 'text-align: center;  color: darkslategray;'> KPIs Summary </h3>",
            unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns([1,1,1,1,1,2])
col1.metric("Total Tickets", kpis["Total Tickets"])
col2.metric("Resolved", kpis["Resolved"])
col3.metric("Resolution Rate", f"{round(kpis["Resolved percentage"], 2)}%")
col4.metric("Avg Response", round(kpis["Avg Response"], 2))
col5.metric("Satisfaction", round(kpis["Avg Satisfaction"], 2))
col6.metric("Revenue", f"${kpis["Total Revenue"]:,.2f}" )


fig = px.pie(
    filtered_df["status"], 
    names= "status", color= "status", color_discrete_map= {"Resolved": "blues", "Unresolved": "coral"}, 
    labels="status")
fig.update_layout(height= 300)

df2 = filtered_df["department"].value_counts().reset_index()
df2.columns = ["department", "counts"]
sorted_df2 = df2.sort_values("counts", ascending=False)
fig2 = px.bar(sorted_df2, x="department", y="counts", color= "counts",
               color_continuous_scale = "haline")
fig2.update_layout(height= 300,
                  xaxis_title="departments",
                  yaxis_title="tickets",
                  font=dict(size=10))

df3 = filtered_df[["region", "revenue_impact"]].groupby("region").sum().reset_index()
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
filtered_df["month"] = filtered_df["date_raised"].dt.to_period("M").dt.to_timestamp()
df4 = filtered_df.groupby(["month", "department"]).size().reset_index()
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

df5_1 = filtered_df.groupby(["month", "region"])["response_time_minutes"].mean().reset_index()
df5_1.columns = ["month", "region", "average_response"]
df5_1 = df5_1.sort_values("month", ascending=False)
fig5_1 = px.line(df5_1, x = "month", y ="average_response", color="region", markers=True)
fig5_1.update_layout(height= 300,
                  xaxis_title="Months",
                  yaxis_title="Average Resolution Time(min)",
                  font=dict(size=10))
fig5_1.update_traces(hovertemplate= "region: %{fullData.name} <br> month: %{x} average_response: %{y:.2f} <extra></extra>",
                   line_shape="spline")

df5_2 = filtered_df.groupby(["month", "department"])["response_time_minutes"].mean().reset_index()
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
    st.subheader("Avg Response time (region)")
    st.plotly_chart(fig5_1, width="stretch")

with col12:
    st.subheader("Avg Response time (department)")
    st.plotly_chart(fig5_2, width="stretch")

# Average customer satisfaction by department
df6_1 = (
    filtered_df
    .groupby("department")["customer_satisfaction_score"]
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
    .groupby("priority")["customer_satisfaction_score"]
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
    st.subheader("Department satisfaction chart")
    st.plotly_chart(fig6_1, width="stretch")

with col14:
    st.subheader("Priority satisfaction chart")
    st.plotly_chart(fig6_2, width="stretch")


aggregated_table = (filtered_df.groupby
                ("month")
                 [["response_time_minutes", "customer_satisfaction_score"]].mean().reset_index())
aggregated_table.columns = ["month","avg_response", "avg_satisfaction"]

temp_selected = (filtered_df.groupby
                ("month")
                 ["revenue_impact"].sum()
                 .reset_index()
                 .rename(columns={"revenue_impact": "total_revenue"}))
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
st.dataframe(aggregated_table)


def run_isolation_forest(data, features, contamination):
    # select trainning data.
    trainning_data = data[features]

    # scale the data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(trainning_data)

    # initialise the model
    model = IsolationForest(
        n_estimators= 100,
        contamination= contamination,
        random_state= 42
    )
    
    model.fit(scaled_data) # train the model

    output_data = data.copy()  # Create copy to avoid modifying original dataframe
    
    output_data["anomaly"] = model.predict(scaled_data)
    output_data["anomaly_score"] = model.decision_function(scaled_data)
    output_data["anomaly_value"] = output_data["anomaly"].map({1: "Normal", -1: "Anomaly"})

    return output_data

def plot_anomalies(
        data,
        x_col,
        y_col,
        title,
        height=400
):

    # Main trend line
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        title=title,
        markers=True
    )

    # Smooth line
    fig.update_traces(line_shape="spline")

    # Select anomalies only
    anomalies_only = data[
        data["anomaly"] == -1
    ]

    # Add anomaly markers
    fig.add_scatter(
        x=anomalies_only[x_col],
        y=anomalies_only[y_col],
        mode="markers",
        marker=dict(size=12, symbol="x"),
        name="Detected Anomaly"
    )

    # Layout improvements
    fig.update_layout(
        height=height,
        xaxis_title=x_col,
        yaxis_title=y_col,
        hovermode="x unified"
    )

    # Custom hover
    fig.update_traces(
        hovertemplate=
        f"{x_col}: %{{x}}<br>"
        f"{y_col}: %{{y:.2f}}"
        "<extra></extra>"
    )

    return fig

features = [
    "avg_response",
    "avg_satisfaction",
    "total_revenue",
    "total_tickets"
]


aggregated_table = run_isolation_forest(
    aggregated_table,
    features,
    0.001
)


st.subheader("AI-Powered KPI Monitoring")

st.dataframe(aggregated_table)


fig_anomaly = plot_anomalies(
    data=aggregated_table,
    x_col="month",
    y_col="avg_response",
    title="Operational Response Time Anomaly Detection"
)

st.plotly_chart(
    fig_anomaly
)

anomaly_count = len(
    aggregated_table[
        aggregated_table["anomaly"] == -1
    ]
)

st.warning(
    f"{anomaly_count} anomalous operational periods detected."
)