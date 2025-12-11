# Vercel serverless function - Minimal working implementation
from fastapi import FastAPI
from mangum import Mangum

# Create FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Financial Data API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Create the handler for Vercel
handler = Mangum(app)
