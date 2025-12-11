# Vercel serverless function - Simplified FastAPI implementation without PIL
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from typing import Optional
import random
from datetime import datetime, timedelta

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Financial Data API"}

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...), document_type: Optional[str] = Form(None)):
    # Simple file validation (just check filename extension)
    filename = file.filename.lower()
    if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']):
        raise HTTPException(status_code=400, detail="Invalid image file extension")
    
    # Return simple dummy data based on document type
    if document_type == "Daybook":
        return {"Day 1": {"Date": "01/01/2024", "Amount": 1000.0}}
    elif document_type == "PT Sheet Old":
        return {"Period 1": {"Start Date": "01/01/2024", "End Date": "31/01/2024"}}
    elif document_type == "PT Sheet New":
        return {"Period 1": {"Period From": "01/01/2024", "Period To": "31/01/2024"}}
    elif document_type == "One Time Info Sheet":
        return {"Profile Information": {"Name": "Test Enterprise"}}
    else:
        return {"Day 1": {"Date": "01/01/2024", "Amount": 1000.0}}

# Create the handler for Vercel
handler = Mangum(app, lifespan="off")