import os
from dotenv import load_dotenv

# Loaders & Splitters
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Models & Embeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Vector Store (Keeping it in-memory for Sprint 2)
from langchain_community.vectorstores import DocArrayInMemorySearch

# The Modern LCEL Components
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def get_market_answer(question: str):
    # --- 1. Load Data ---
    # loader = TextLoader("./data/sample_news.txt")
    loader = TextLoader("./data/sample_news.txt", encoding="utf-8")
    documents = loader.load()

    # --- 2. Split Data ---
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)

    # --- 3. Index (Embeddings + Vector Store) ---
    # We use DocArrayInMemorySearch to avoid installing Chroma/SQLite drivers right now.
    embeddings = OpenAIEmbeddings()
    vectorstore = DocArrayInMemorySearch.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()

    # --- 4. The Prompt ---
    template = """Answer the question based ONLY on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # --- 5. The Model ---
    model = ChatOpenAI(model="gpt-5-nano", temperature=0)

    # --- 6. The Chain (LCEL) ---
    # This implies: Retriever -> Prompt -> LLM -> String Output
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    # Invoke
    return chain.invoke(question)

# --- Test Block ---
if __name__ == "__main__":
    print(get_market_answer("What is the revenue growth?"))