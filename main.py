### Step 2: The Imports
# We need `FastAPI` (the web framework) and 
# `pydantic` (the data validator). We also need to import the function you just built.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import get_market_answer  # This imports your logic from Sprint 2

# Initialize the App
app = FastAPI(title="Market Intelligence API")

### Step 3: Define the Data Model
# This is "Senior" level best practice. Instead of accepting random JSON, we define exactly what we expect.
class QueryRequest(BaseModel):
    ticker: str
    question: str


### Step 4: The Endpoints
# We need two endpoints:
# 1.  `/health`: Just to check if the server is running.
# 2.  `/query`: The main endpoint that calls your AI logic.

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/query")
async def ask_market_bot(request: QueryRequest):
    try:
        # call the function from engine.py
        answer = get_market_answer(request.question)
        
        return {
            "ticker": request.ticker,
            "answer": answer,
            "source": "Local Golden File"
        }
    except Exception as e:
        # If something breaks, return a 500 error with details
        raise HTTPException(status_code=500, detail=str(e))


