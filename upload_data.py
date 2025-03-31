import zipfile
import requests
import io
import pandas as pd
from pandas_gbq import to_gbq


# Step 1: Download and extract the raw CSV from the zipped World Bank file (no skipping rows)
def download_and_extract_csv(url):
    response = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(response.content))
    
    # Find the main data file in the ZIP (skip metadata files)
    target_file = [f for f in z.namelist() if f.startswith("API_") and f.endswith(".csv") and "Metadata" not in f][0]
    
    # Load full CSV (with headers, no row skipping)
    df = pd.read_csv(z.open(target_file), skiprows=4, encoding='latin1', delimiter=',', engine='python')
    return df

# Step 2: Upload the full DataFrame to BigQuery, replacing any existing table
def truncate_and_upload(PROJECT_ID, TABLE_FULL_ID, url):

    df = download_and_extract_csv(url)  # Download and load data
    
    # Replace entire table in BigQuery
    to_gbq(df, TABLE_FULL_ID, project_id=PROJECT_ID, if_exists="replace")

