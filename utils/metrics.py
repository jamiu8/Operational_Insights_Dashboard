import pandas as pd
import numpy as np

# function to autmatically calculate all kpis
def kpi_display(data):
    total_tickets = len(data) # total tickets raised
    resolved = len(data[data["status"] == "Resolved"])
    resolved_rate = resolved/total_tickets * 100
    avg_response = data["response_time_minutes"].mean()
    avg_satisfaction = data["customer_satisfaction_score"].mean()
    total_revenue = data["revenue_impact"].mean()
    output = {
   "Total Tickets": total_tickets,
   "Resolved": resolved,
   "Avg Response": avg_response,
   "Resolved percentage": resolved_rate,
   "Avg Satisfaction": avg_satisfaction,
   "Total Revenue": total_revenue
}
    return output
    

