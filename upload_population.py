import json
from google.cloud import bigquery
from google.oauth2 import service_account
from upload_functions import truncate_and_upload
import os


# ACCESS TO BIG QUEERY
bq_credentials = os.environ.get('BIGQUERY')
credentials_info = json.loads(bq_credentials)
credentials = service_account.Credentials.from_service_account_info(credentials_info)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# CONFIG
PROJECT_ID = 'political-weather-map'
DATASET_ID = 'WorldBankData'
TABLE_ID = 'Population'
TABLE_FULL_ID = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

url = 'https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv'

# Truncate and upload the data
truncate_and_upload(PROJECT_ID, TABLE_FULL_ID, url, credentials)