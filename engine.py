import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def get_market_answer(question: str):
    # 1. Load the PERSISTENT database we created in experiment.py
    # Note: Ensure this path matches the folder name in your /db/ directory
    persist_dir = "./db/chunk_500_overlap_50"
    
    embeddings = OpenAIEmbeddings()
    
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )

    # 2. Define the Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 3. Create the LCEL Prompt Template
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # 4. Setup the LLM
    model = ChatOpenAI(model="gpt-5-nano", temperature=0)

    # 5. Build the LCEL Chain
    # This retrieves context, passes it to the prompt, then to the model
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    # 6. Run the chain
    # In LCEL, .invoke() returns the string directly because of StrOutputParser
    return chain.invoke(question)