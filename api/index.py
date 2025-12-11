# Vercel serverless function for financial data generation
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import random

app = FastAPI(title="Financial Data API")

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
    return {
        "message": "Welcome to the Financial Data API",
        "endpoints": {
            "/": "This welcome message",
            "/health": "Health check endpoint",
            "/process-image/": "POST endpoint to generate dummy financial data"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

def generate_daybook_data(filename: str):
    """Generate dummy data for Daybook document type in the specified format."""
    days_data = {}
    
    # Define the structure for each day
    fields = [
        "Sale in cash",
        "Sale on credit", 
        "Cash Received from customers",
        "Advance received from customer",
        "Buy raw material in cash",
        "Buy raw material on credit",
        "Cash Paid to suppliers",
        "Advance paid to suppliers",
        "Amount paid for transportation",
        "Salary / Wages to Workers",
        "Salary / wages / withdrawal by Owners",
        "Electricity charges",
        "Rent paid",
        "Fuel / expenses paid",
        "Repayment of loan",
        "Other income",
        "Other cost",
        "Investment by Owner",
        "Loan borrowed",
        "Purchased Asset"
    ]
    
    # Generate data for 31 days (full month)
    for i in range(1, 32):
        day_entry = {}
        # For each day, randomly populate 3-6 fields with values, rest are empty strings
        fields_to_populate = random.sample(fields, random.randint(3, 6))
        
        for field in fields:
            if field in fields_to_populate:
                if field == "Purchased Asset":
                    day_entry[field] = "null"  # Always null as in your example
                else:
                    # Generate appropriate values based on field type
                    if "cash" in field.lower() or "credit" in field.lower() or "received" in field.lower():
                        day_entry[field] = round(random.uniform(50, 100000), 2)
                    elif "salary" in field.lower() or "wages" in field.lower():
                        day_entry[field] = round(random.uniform(100, 5000), 2)
                    elif "transportation" in field.lower() or "fuel" in field.lower():
                        day_entry[field] = round(random.uniform(50, 1000), 2)
                    elif "electricity" in field.lower():
                        day_entry[field] = round(random.uniform(100, 2000), 2)
                    elif "rent" in field.lower():
                        day_entry[field] = round(random.uniform(1000, 10000), 2)
                    elif "loan" in field.lower():
                        day_entry[field] = round(random.uniform(0, 5000), 2)
                    elif "income" in field.lower():
                        day_entry[field] = round(random.uniform(0, 2000), 2)
                    elif "cost" in field.lower():
                        day_entry[field] = round(random.uniform(0, 1000), 2)
                    elif "investment" in field.lower():
                        day_entry[field] = round(random.uniform(0, 20000), 2)
                    else:
                        day_entry[field] = round(random.uniform(0, 1000), 2)
            else:
                day_entry[field] = ""  # Empty string for unpopulated fields
        
        days_data[f"Day {i}"] = day_entry
    
    # Return in the specified format
    return {
        filename: {
            "filename": filename,
            "data": days_data
        }
    }

# For other document types, we can keep simpler structures
def generate_pt_sheet_old_data(filename: str):
    """Generate dummy data for PT Sheet Old document type."""
    return {
        filename: {
            "filename": filename,
            "data": {
                "Period 1": {
                    "Time Period Information": {
                        "Start Date": "01/01/2024",
                        "End Date": "31/01/2024"
                    }
                }
            }
        }
    }

def generate_pt_sheet_new_data(filename: str):
    """Generate dummy data for PT Sheet New document type."""
    return {
        filename: {
            "filename": filename,
            "data": {
                "Period 1": {
                    "Time Period Information": {
                        "Period From": "01/01/2024",
                        "Period To": "31/01/2024"
                    }
                }
            }
        }
    }

def generate_one_time_info_data(filename: str):
    """Generate dummy data for One Time Info Sheet document type."""
    return {
        filename: {
            "filename": filename,
            "data": {
                "Profile Information": {
                    "Name": "Test Enterprise"
                }
            }
        }
    }

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...), document_type: Optional[str] = Form(None)):
    """
    Generate dummy financial data based on document type.
    
    Args:
        file: The uploaded file (validation only, not processed)
        document_type: Optional document type ("PT Sheet Old", "PT Sheet New", "Daybook", "One Time Info Sheet")
    """
    filename = file.filename
    
    # Generate dummy data based on document type
    if not document_type or document_type == "Daybook":
        result = generate_daybook_data(filename)
    elif document_type == "PT Sheet Old":
        result = generate_pt_sheet_old_data(filename)
    elif document_type == "PT Sheet New":
        result = generate_pt_sheet_new_data(filename)
    elif document_type == "One Time Info Sheet":
        result = generate_one_time_info_data(filename)
    else:
        # Default to Daybook if unknown document type
        result = generate_daybook_data(filename)

    return JSONResponse(content=result)