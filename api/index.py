# Vercel serverless function using ASGI handler
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Financial Data API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# For Vercel, we need to expose the app directly
# Vercel will automatically wrap it with their handler