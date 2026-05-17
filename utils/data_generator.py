from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta

fake = Faker() # instance of the Faker class 

# Name of the teams of the company
DEPARTMENTS = [
    "Customer Support",
    "Technical Support",
    "Billing",
    "Sales",
    "Operations"
]

# regions of the company
REGIONS = [
    "North America",
    "Europe",
    "Africa",
    "Asia Pacific",
    "Middle East"
]

PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]

# function to generate fake data to work with.
def generate_ticket_data(n_rows = 500):
    Data = []
    start_date = datetime(2024, 1, 1)

    # loops 500 times, generating 500 rows.
    for _ in range(n_rows):
        date_raised = start_date + timedelta(days=random.randint(0, 365))
        is_resolved = random.choices([True, False], weights=[75, 25])[0]
        
        if is_resolved:
            date_resolved = date_raised + timedelta(
                minutes=random.randint(30, 4320)
            )
            response_time = round(
                (date_resolved - date_raised).total_seconds() / 60, 2
            )
            satisfaction = round(random.uniform(1.0, 5.0), 2)
            status = "Resolved"
        else:
            date_resolved = None
            response_time = None
            satisfaction = None
            status = "Unresolved"

        row = {
            "ticket_id": fake.uuid4()[:8].upper(),
            "date_raised": date_raised.strftime("%Y-%m-%d"),
            "date_resolved": date_resolved.strftime("%Y-%m-%d") if date_resolved else None,
            "department": random.choice(DEPARTMENTS),
            "region": random.choice(REGIONS),
            "agent_name": fake.name(),
            "customer_name": fake.name(),
            "customer_email": fake.email(),
            "priority": random.choice(PRIORITY_LEVELS),
            "status": status,
            "response_time_minutes": response_time,
            "customer_satisfaction_score": satisfaction,
            "revenue_impact": round(random.uniform(100.0, 50000.0), 2)
        }

        Data.append(row)

    return pd.DataFrame(Data)

# functin to call the faker function and save the data in csv format
def save_data(filepath="data/operational_data.csv"):
    df = generate_ticket_data()
    df = df.sort_values("date_raised").reset_index(drop=True)
    print(f"{len(df)} tickets generated")
    print(f"Resolved: {df[df['status'] == 'Resolved'].shape[0]}")
    print(f"Unresolved: {df[df['status'] == 'Unresolved'].shape[0]}")
    df.to_csv(filepath, index=False)
    print(f"Saved to {filepath}")

if __name__ == "__main__":
    save_data()
