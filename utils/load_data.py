import pandas as pd

# load operational data
def load_data(file_path="data/operational_data.csv"):
    df = pd.read_csv(file_path)

    # covert the datetime columns back to datetime
    df["date_raised"] = pd.to_datetime(df["date_raised"])
    df["date_resolved"] = pd.to_datetime(df["date_resolved"])

    return df