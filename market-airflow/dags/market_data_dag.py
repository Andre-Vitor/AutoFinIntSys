from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from google.cloud import storage
import yfinance as yf
import io


def scrape_and_upload_to_gcs(tickers):
    # Use the path relative to the Airflow container
    # client = storage.Client.from_service_account_json(r"C:\Users\...\Documents\_Projects\_Automated Financial Intelligence System\AutoFinIntSys\market-airflow\include\market-intel-project-a079b6a5c47c.json")
    # CORRECT: This points to the location INSIDE the container
    # client = storage.Client.from_service_account_json("/usr/local/airflow/include/market-intel-project-a079b6a5c47c.json")
    client = storage.Client() 
    bucket = client.get_bucket('market-news-raw-data')
    
    all_news = []
    for ticker in tickers:
        tkr = yf.Ticker(ticker)
        news = tkr.news
        for item in news:
            # The new nested logic
            content = item.get('content', {})
            all_news.append({
                "ticker": ticker,
                "title": content.get('title'),
                "summary": content.get('summary'),
                "publisher": content.get('provider', {}).get('displayName'),
                "publish_date": content.get('pubDate'),
                "url": content.get('canonicalUrl', {}).get('url'),
                "extracted_at": datetime.now().isoformat()
            })

    df = pd.DataFrame(all_news)
    
    # Push to GCS
    parquet_buffer = io.BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    file_name = f"market_news_{datetime.now().strftime('%Y%m%d_%H%M')}.parquet"
    blob = bucket.blob(file_name)
    blob.upload_from_string(parquet_buffer.getvalue(), content_type='application/octet-stream')
    print(f"Uploaded {len(all_news)} items to GCS.")

from langchain_community.document_loaders import PySparkDataFrameLoader # Or just use Pandas
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

def gcs_to_chroma():
    # 1. Download from GCS
    client = storage.Client()
    bucket = client.get_bucket('market-news-raw-data')
    blobs = list(bucket.list_blobs())
    latest_blob = max(blobs, key=lambda x: x.updated) # Get the newest file
    print(f"Downloading {latest_blob.name}")
    
    # Read parquet into memory
    buffer = io.BytesIO()
    latest_blob.download_to_file(buffer)
    df = pd.read_parquet(buffer)

    # 2. Convert to LangChain Documents
    documents = []
    for _, row in df.iterrows():
        # INDUSTRY STANDARD: Formatting content for better retrieval
        content = f"Ticker: {row['ticker']}\nTitle: {row['title']}\nSummary: {row['summary']}"
        doc = Document(
            page_content=content,
            metadata={"ticker": row['ticker'], "date": row['publish_date']}
        )
        documents.append(doc)

    # 3. Chunking (Industry Standard: 500-1000 characters)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # 4. Vector Store (Chroma)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(),
        persist_directory="./db/chunk_500"
    )
    print(f"Success: Indexed {len(chunks)} chunks to Chroma.")

with DAG(
    'market_intelligence_pipeline',
    default_args={'retries': 1},
    schedule='@daily', # Run every night
    start_date=datetime(2023, 1, 1),
    catchup=False
) as dag:

    t1 = PythonOperator(
    task_id='scrape_market_news',
    python_callable=scrape_and_upload_to_gcs,
    # This is the "bridge" that passes the list to your function
    op_kwargs={'tickers': ['NVDA', 'AAPL', 'TSLA', 'MSFT']} 
)
    t2 = PythonOperator(task_id='update_vector_store', python_callable=gcs_to_chroma)

    t1 >> t2  # Set dependencies