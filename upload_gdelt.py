import streamlit as st
import json
from pandas_gbq import to_gbq, read_gbq
from datetime import datetime, timedelta, timezone
from google.cloud import bigquery
from google.oauth2 import service_account

# Access to BigQuery
credentials_info = json.loads(st.secrets['bigquery']['credentials_json'])
credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Config
PROJECT_ID = 'political-weather-map'
DATASET_ID = 'articles'
TABLE_ID = 'immigration'
TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

# Step 1: Find the last date in our cleaned table.
start_date = datetime.strptime('2023-01-01', "%Y-%m-%d").date()
end_date = (datetime.now(timezone.utc) - timedelta(days=1)).date()

try:
    existing_dates_query = f"""
    SELECT DISTINCT DATE(DateTime) AS existing_date
    FROM `{TABLE_FULL_ID}`
    WHERE DATE(DateTime) BETWEEN DATE('2015-01-01') AND DATE(CURRENT_DATE() - 1)
    """
    existing_dates_result = read_gbq(existing_dates_query, project_id=PROJECT_ID)
    existing_dates = set(existing_dates_result['existing_date'].dt.date)
except Exception:
    existing_dates = set()
    
missing_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1) if (start_date + timedelta(days=i)) not in existing_dates]

if missing_dates:
    query = f"""
    SELECT DateTime, Title, DocTone, CountryCode, ContextualText 
    FROM `gdelt-bq.gdeltv2.ggg` 
    WHERE DATE(DateTime) IN ({', '.join([f"DATE('{date}') " for date in missing_dates])})
    AND ContextualText LIKE '%immigra%'
    """
    df = client.query(query).to_dataframe()
else:
    df = None

# Upload articles to our BigQuery
def load_to_gbq(df):
    to_gbq(
        df, TABLE_FULL_ID, project_id=PROJECT_ID,
        if_exists='append'
    )
    
if __name__ == '__main__':
    if not df.empty:
        load_to_gbq(df)
        print(f'Uploaded {len(df)} new records.')
    else:
        print('No new data to upload.')