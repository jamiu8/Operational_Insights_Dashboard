import pandas as pd

# load operational data
def load_data(file_path="data/operational_data.csv"):
    df = pd.read_csv(file_path)
    
    return df