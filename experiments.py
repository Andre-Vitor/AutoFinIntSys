# experiment.py
import os
import shutil
import mlflow
from dotenv import load_dotenv

# Loaders & Splitters
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Models & Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# 1. Setup MLflow
# This sets the "folder" name in the MLflow UI
mlflow.set_experiment("Market_Intel_RAG_Testing")

def run_rag_experiment(chunk_size, chunk_overlap):
    # Name the run so it's easy to read in the UI
    run_name = f"chunk_{chunk_size}_overlap_{chunk_overlap}"
    
    with mlflow.start_run(run_name=run_name):
        print(f"--- Starting Run: {run_name} ---")
        
        # Log parameters (The "Input" variables)
        mlflow.log_param("chunk_size", chunk_size)
        mlflow.log_param("chunk_overlap", chunk_overlap)

        # 2. Process Data
        # Ensure encoding is utf-8 to avoid Windows charmap errors
        loader = TextLoader("./data/sample_news.txt", encoding="utf-8")
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        docs = text_splitter.split_documents(documents)
        print(f"Created {len(docs)} chunks.")

        # 3. Create/Save Vector Store
        # We create a specific folder for THIS chunk size so we can compare them later
        persist_dir = f"./db/{run_name}"
        
        # Clean up existing DB if it exists (for clean experiments)
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)

        embeddings = OpenAIEmbeddings()
        
        # This writes the data to the hard drive
        vectorstore = Chroma.from_documents(
            documents=docs, 
            embedding=embeddings, 
            persist_directory=persist_dir
        )
        
        # 4. Log Metrics
        # How many chunks did this strategy create?
        mlflow.log_metric("num_chunks", len(docs))
        
        print(f"Saved to {persist_dir}")
        print("--------------------------------------------------")

if __name__ == "__main__":
    # Test two different "Physics" setups
    # Run 1: Smaller chunks (Detailed retrieval)
    run_rag_experiment(chunk_size=500, chunk_overlap=50)
    
    # Run 2: Larger chunks (More context, less precision)
    run_rag_experiment(chunk_size=1000, chunk_overlap=100)