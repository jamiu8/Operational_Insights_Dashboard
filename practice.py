import streamlit as st
import pandas as pd
from utils.load_data import load_data
from utils.metrics import kpi_display
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

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