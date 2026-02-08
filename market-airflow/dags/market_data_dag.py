from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import storage

# This is a simplified logic for your DAG
def scrape_and_upload():
    # 1. Scrape (Use yfinance or a simple dummy scraper for now)
    data = {"ticker": "NVDA", "news": "Earnings are up 200%", "date": str(datetime.now())}
    df = pd.DataFrame([data])
    
    # 2. Upload to GCS
    client = storage.Client.from_service_account_json("/path/to/your/key.json")
    bucket = client.get_bucket('market-news-raw-data')
    blob = bucket.blob(f"news_{datetime.now().strftime('%Y%m%d')}.parquet")
    blob.upload_from_string(df.to_parquet(), content_type='application/octet-stream')
    print("Uploaded to GCS!")

def update_chroma_from_gcs():
    # Logic to download from GCS, chunk the text, and add to ChromaDB
    print("ChromaDB updated with new news!")

with DAG(
    'market_intelligence_pipeline',
    default_args={'retries': 1},
    schedule_interval='@daily', # Run every night
    start_date=datetime(2023, 1, 1),
    catchup=False
) as dag:

    t1 = PythonOperator(task_id='scrape_news', python_callable=scrape_and_upload)
    t2 = PythonOperator(task_id='update_vector_store', python_callable=update_chroma_from_gcs)

    t1 >> t2  # Set dependencies