# NYC Taxi Analytics — Modern Data Stack

An end-to-end analytics engineering project built with dbt, DuckDB, and Streamlit.

## Stack
| Tool | Purpose |
|---|---|
| **DuckDB** | Local OLAP database — processes 2.7M records in <1 second |
| **dbt Core** | SQL transformation layer with staging + mart models |
| **Streamlit** | Interactive analytics dashboard |

## What I Built
- Staging model that cleans and filters 2.7M+ NYC Yellow Taxi records
- `mart_hourly_trips` — trip volume, revenue, and fare trends by hour
- `mart_payment_summary` — revenue and tip analysis by payment method
- 4 dbt data quality tests (all passing)
- Interactive Streamlit dashboard with 5 charts and 4 KPI metrics

## Key Findings
- **Peak demand:** 6–9pm on weekdays (Wednesday highest at 450K+ trips)
- **Highest fares:** 4–5am (~$27 avg — likely airport runs)
- **Payment split:** Credit card drives 85.6% of revenue
- **Tip behavior:** Credit card riders tip 4x more than cash riders ($4 vs ~$0)

## Project Structure
nyc_taxi_analytics/

├── data/raw/                          # Source parquet file

├── dbt_project/

│   ├── models/

│   │   ├── staging/stg_taxi_trips.sql

│   │   └── marts/

│   │       ├── mart_hourly_trips.sql

│   │       └── mart_payment_summary.sql

│   └── dbt_project.yml

└── dashboard.py                       # Streamlit dashboard


## Run It Yourself
```bash
# 1. Clone the repo
git clone https://github.com/ayushid543/nyc-taxi-analytics.git
cd nyc-taxi-analytics

# 2. Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install dbt-duckdb streamlit plotly

# 3. Download data
python download_data.py

# 4. Run dbt models
cd dbt_project
dbt run
dbt test

# 5. Launch dashboard
cd ..
streamlit run dashboard.py
```