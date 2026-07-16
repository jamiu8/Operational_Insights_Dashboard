# Operational Insights Dashboard with Natural Language Querying

## Overview

The Operational Insights Dashboard is a self-service analytics platform built with Streamlit that allows users to upload datasets, automatically detect business metrics and dimensions, visualize KPIs, and query their data using natural language.

Unlike traditional dashboards that require predefined schemas and hardcoded metrics, this project dynamically adapts to uploaded datasets by detecting numerical, categorical, and datetime fields and mapping them to business concepts such as revenue, customer satisfaction, response time, status, region, and department.

The platform combines business intelligence, analytics engineering, and natural language processing techniques to create a flexible analytics experience.

---

## Features

### Dynamic Dataset Upload

* Supports CSV and Excel files.
* Automatically profiles uploaded datasets.
* Works with datasets without requiring manual code changes.

### Automatic Schema Detection

Detects:

* Numerical columns
* Categorical columns
* Datetime columns
* Boolean columns

Business concepts are automatically inferred from column names and values.

---

### Dynamic KPI Generation

Automatically generates KPIs such as:

* Total Revenue
* Total Tickets
* Resolution Rate
* Average Response Time
* Customer Satisfaction Score

No hardcoded column names are required.

---

### Interactive Dashboard

Includes:

* KPI cards
* Regional analysis
* Department analysis
* Status distributions
* Revenue trends
* Customer satisfaction trends

Built using:

* Streamlit
* Plotly

---

### Natural Language Query Engine

Users can ask questions such as:

```text
total revenue
average satisfaction
highest revenue region
top 5 regions by revenue
revenue in Middle East
count of closed tickets
revenue this year
```

The engine supports:

#### Aggregations

* Sum
* Average
* Count

#### Dimensions

* Region
* Department
* Priority
* Status
* Any detected categorical field

#### Ranking Queries

* Top N
* Bottom N

#### Selection Queries

* Highest
* Lowest

#### Filtering

* Regional filters
* Department filters
* Priority filters
* Status filters

#### Date Filtering

* Today
* Yesterday
* This Year

---

## Project Architecture

```text
Dataset Upload
      ↓
Schema Detection
      ↓
Business Schema Resolution
      ↓
KPI Generation
      ↓
Visualization Layer
      ↓
Natural Language Query Engine
```

Natural language queries follow the pipeline:

```text
User Query
    ↓
Query Parsing
    ↓
Filter Extraction
    ↓
Date Extraction
    ↓
Aggregation Engine
    ↓
Result Generation
```

---

## Technologies Used

* Python
* Streamlit
* Pandas
* Plotly
* NumPy

---

## Object-Oriented Design

The NLP component was refactored into a `QueryEngine` class responsible for:

* Query parsing
* Filter extraction
* Date extraction
* Aggregation execution
* Result generation

This separation improves maintainability and extensibility.

---

## Example Queries

```text
top 5 regions by revenue

average satisfaction in Europe

highest revenue department

count of closed tickets

revenue this year
```

---

## Future Improvements

Potential future enhancements include:

* Multi-metric queries
* Automatic chart generation from natural language
* Forecasting
* Anomaly detection
* LLM-powered query interpretation
* Database connectivity

---

## Motivation

Traditional dashboards often require analysts to manually create reports for every business question. This project explores the idea of self-service analytics by allowing users to interact with their data using natural language rather than predefined filters and reports.

The goal was to bridge the gap between business users and data by making analytics more accessible and flexible.

---

## Author

Developed as part of a data science and analytics portfolio project focused on analytics engineering, business intelligence, and natural language interfaces.
