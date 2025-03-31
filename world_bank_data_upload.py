import zipfile
import requests
import io
import pandas as pd
from pandas_gbq import to_gbq
import json
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

# ACCESS TO BIG QUEERY : TO DO - create 
credentials_info = json.loads(st.secrets['bigquery']['credentials_json'])
credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# CONFIG : TO DO - Hiro: access to big queery
PROJECT_ID = 'sipa-adv-c-charlotte-hiro-sam'
DATASET_ID = 
TABLE_ID = TBD
TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

# WORLD BANK DATA SOURCES
urls = {
    "immigration": "https://api.worldbank.org/v2/en/indicator/SM.POP.NETM?downloadformat=csv",
    "population": "https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"
}

# Step 1: Download and extract the raw CSV from the zipped World Bank file (no skipping rows)
def download_and_extract_csv(url):
    response = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(response.content))
    
    # Find the main data file in the ZIP (skip metadata files)
    target_file = [f for f in z.namelist() if f.startswith("API_") and f.endswith(".csv") and "Metadata" not in f][0]
    
    # Load full CSV (with headers, no row skipping)
    df = pd.read_csv(z.open(target_file))
    return df

# Step 2: Upload the full DataFrame to BigQuery, replacing any existing table
def truncate_and_upload(file_key, url):

    df = download_and_extract_csv(url)  # Download and load data
    table_id = f"{dataset_id}.{file_key}"  # Format: your_dataset_name.immigration or population
    
    # Replace entire table in BigQuery
    to_gbq(df, table_id, project_id=project_id, if_exists="replace")

# Step 3: Loop through all URLs and update each table
def update_worldbank_data():
    for key, url in urls.items():
        truncate_and_upload(key, url)

# Execute the upload process
update_worldbank_data()
