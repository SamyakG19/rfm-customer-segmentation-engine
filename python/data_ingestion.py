import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

# ==========================================
# 1. AUTHENTICATION & CLOUD SETUP
# ==========================================
key_path = 'gcp_key.json' 
project_id = 'rfm-analytics-engine'

credentials = service_account.Credentials.from_service_account_file(key_path)
client = bigquery.Client(credentials=credentials, project=project_id)

# Pointing to the dataset you created in Google Cloud
table_id = f"{project_id}.rfm_data.raw_transactions"

# ==========================================
# 2. DATA EXTRACTION & CLEANING
# ==========================================
print("Loading Kaggle CSV file... ")
df = pd.read_csv('online_retail.csv', encoding='unicode_escape')
print(f"Original Row Count: {len(df)}")

# Drop ghost customers and refunds
df = df.dropna(subset=['CustomerID'])
df = df[df['Quantity'] > 0]

# Standardize IDs and calculate revenue
df['CustomerID'] = df['CustomerID'].astype(int).astype(str)
df['TotalSales'] = df['Quantity'] * df['UnitPrice']
print(f"Cleaned Row Count: {len(df)}")

# ==========================================
# 3. DATA LOADING (BIGQUERY)
# ==========================================
print("Uploading clean data to Google BigQuery...")
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result() 

print(f"Success! {len(df)} rows have been securely loaded into BigQuery.")