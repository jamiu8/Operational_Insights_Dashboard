from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px

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