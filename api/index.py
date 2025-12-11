# Vercel serverless function for FastAPI
import json
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from typing import Optional
from datetime import datetime, timedelta
import random
import io
from PIL import Image

# Create FastAPI app
app = FastAPI(title="Financial Data API")

# Configure CORS
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
            "/process-image/": "POST endpoint to generate dummy financial data"
        }
    }

def generate_daybook_data():
    """Generate dummy data for Daybook document type."""
    base_date = datetime.now()
    days_data = {}
    
    # Generate data for 31 days (full month)
    for i in range(1, 32):
        date = base_date + timedelta(days=i-1)
        days_data[f"Day {i}"] = {
            "Date": date.strftime("%d/%m/%Y"),
            "Cash Sale": round(random.uniform(1000, 10000), 2),
            "Credit Sale": round(random.uniform(500, 5000), 2),
            "Cash Collection": round(random.uniform(500, 3000), 2),
            "Cash Purchase": round(random.uniform(1000, 8000), 2),
            "Credit Purchase": round(random.uniform(300, 4000), 2),
            "Cash Paid to Suppliers": round(random.uniform(800, 5000), 2),
            "Transportation": round(random.uniform(100, 1000), 2),
            "Owner's Wages": round(random.uniform(200, 1500), 2),
            "Workers' Wages": round(random.uniform(500, 3000), 2),
            "Electricity": round(random.uniform(100, 800), 2),
            "Repairs": round(random.uniform(50, 500), 2),
            "Other Cost": round(random.uniform(50, 300), 2),
            "Other Income": round(random.uniform(0, 200), 2),
            "Loan": round(random.uniform(0, 2000), 2),
            "Interest": round(random.uniform(0, 100), 2),
            "Amount": round(random.uniform(500, 5000), 2)
        }
    
    return days_data

def generate_pt_sheet_old_data():
    """Generate dummy data for PT Sheet Old document type."""
    base_date = datetime.now()
    periods_data = {}
    
    # Generate data for 3 periods
    for i in range(1, 4):
        start_date = base_date + timedelta(days=(i-1)*30)
        end_date = start_date + timedelta(days=29)
        
        periods_data[f"Period {i}"] = {
            "Time Period Information": {
                "Start Date": start_date.strftime("%d/%m/%Y"),
                "End Date": end_date.strftime("%d/%m/%Y")
            },
            "Fixed Particulars": {
                "Cash Sales": round(random.uniform(20000, 50000), 2),
                "Credit Sales": round(random.uniform(5000, 20000), 2),
                "Cash Received from Debtors": round(random.uniform(3000, 15000), 2),
                "Cash Purchase": round(random.uniform(15000, 40000), 2),
                "Credit Purchase": round(random.uniform(5000, 25000), 2),
                "Cash Given to Creditors": round(random.uniform(10000, 30000), 2),
                "Owner's Wages": round(random.uniform(1000, 5000), 2),
                "Transportation": round(random.uniform(500, 2000), 2),
                "Room Rent": round(random.uniform(2000, 8000), 2),
                "Worker's Salary or Wages": round(random.uniform(3000, 12000), 2),
                "Electricity or Fuel": round(random.uniform(500, 2500), 2),
                "Repair and Maintenance": round(random.uniform(300, 1500), 2),
                "Other Cost": round(random.uniform(200, 1000), 2),
                "Other Income": round(random.uniform(0, 1000), 2),
                "Loan Repayment": round(random.uniform(0, 5000), 2),
                "Interest on Loan": round(random.uniform(0, 500), 2),
                "Owner's Investment": round(random.uniform(0, 10000), 2)
            },
            "Summary Particulars": {
                "Closing Cash Balance": round(random.uniform(5000, 20000), 2),
                "Closing Bank Balance": round(random.uniform(10000, 50000), 2),
                "Purchase of Fixed Asset": round(random.uniform(0, 10000), 2),
                "Sale of Fixed Asset": round(random.uniform(0, 5000), 2),
                "Security Deposit Given": round(random.uniform(0, 3000), 2),
                "Security Deposit Returned": round(random.uniform(0, 2000), 2),
                "Loan Taken": round(random.uniform(0, 15000), 2),
                "Source of Loan": random.choice(["Bank", "SHG", "Friend", "Family", "None"]),
                "Closing Inventory": round(random.uniform(5000, 25000), 2)
            }
        }
    
    return periods_data

def generate_pt_sheet_new_data():
    """Generate dummy data for PT Sheet New document type."""
    base_date = datetime.now()
    periods_data = {}
    
    # Generate data for 3 periods
    for i in range(1, 4):
        start_date = base_date + timedelta(days=(i-1)*30)
        end_date = start_date + timedelta(days=29)
        
        periods_data[f"Period {i}"] = {
            "Time Period Information": {
                "Period From": start_date.strftime("%d/%m/%Y"),
                "Period To": end_date.strftime("%d/%m/%Y")
            },
            "Details": {
                "Cash Sales": round(random.uniform(20000, 50000), 2),
                "Credit Sales": round(random.uniform(5000, 20000), 2),
                "Cash Received (from Customers)": round(random.uniform(3000, 15000), 2),
                "Cash Purchase": round(random.uniform(15000, 40000), 2),
                "Credit Purchase": round(random.uniform(5000, 25000), 2),
                "Cash Paid to Suppliers": round(random.uniform(10000, 30000), 2),
                "Owner's Wages": round(random.uniform(1000, 5000), 2),
                "Workers' Wages": round(random.uniform(3000, 12000), 2),
                "Transportation": round(random.uniform(500, 2000), 2),
                "Electricity": round(random.uniform(500, 2500), 2),
                "Repairs": round(random.uniform(300, 1500), 2),
                "Other Expenses": round(random.uniform(200, 1000), 2),
                "Interest Paid": round(random.uniform(0, 500), 2),
                "Loan Repaid": round(random.uniform(0, 5000), 2),
                "Other Income": round(random.uniform(0, 1000), 2)
            },
            "Details on Capital": {
                "Fixed Assets Purchased": round(random.uniform(0, 10000), 2),
                "Fixed Assets Sold": round(random.uniform(0, 5000), 2),
                "Owner Reinvested": round(random.uniform(0, 10000), 2),
                "Owner's Withdrawals": round(random.uniform(0, 5000), 2),
                "Loan Taken": round(random.uniform(0, 15000), 2),
                "Source of Loan": random.choice(["Bank", "SHG", "Friend", "Family", "None"]),
                "Inventory (Goods / Stock)": round(random.uniform(5000, 25000), 2)
            }
        }
    
    return periods_data

def generate_one_time_info_data():
    """Generate dummy data for One Time Info Sheet document type."""
    return {
        "Profile Information": {
            "Enterprise ID Number": f"ENT{random.randint(10000, 99999)}",
            "Name of the Enterprise": random.choice(["ABC Traders", "XYZ Enterprises", "PQR Services", "LMN Retail"]),
            "Name of the Entrepreneur": f"{random.choice(['Raj', 'Priya', 'Amit', 'Sneha', 'Vikram'])} {random.choice(['Kumar', 'Sharma', 'Patel', 'Singh', 'Reddy'])}",
            "Types of Enterprise": random.choice(["Manufacturing", "Trading", "Service", "Retail"]),
            "Date of Starting the Enterprise": (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime("%d/%m/%Y"),
            "New or Existing": random.choice(["New", "Existing"]),
            "Intervention Date by GUM": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%d/%m/%Y"),
            "Mobile Number": random.randint(9000000000, 9999999999)
        },
        "Financial Information": {
            "Total Investment": round(random.uniform(50000, 500000), 2),
            "Total Fixed Capital": round(random.uniform(20000, 200000), 2),
            "Owner's Investment": round(random.uniform(30000, 300000), 2),
            "Loan from SHG": round(random.uniform(0, 100000), 2),
            "Loan from Bank": round(random.uniform(0, 200000), 2),
            "Other Source": round(random.uniform(0, 50000), 2)
        },
        "Geography Information": {
            "Name of SHG": random.choice(["Progressive Women's SHG", "Unity SHG", "Empowerment Circle", "Self-Help Group A"]),
            "Name of VO": random.choice(["Village Organization 1", "VO Unity", "Community VO", "Local VO"]),
            "Name of CLF": random.choice(["Cluster Level Federation", "Women's Federation", "Community CLF", "Local CLF"]),
            "Name of Village": random.choice(["Green Valley", "Sunset Village", "River Side", "Hill Top"]),
            "Name of Panchayat": random.choice(["Central Panchayat", "North Panchayat", "South Panchayat", "East Panchayat"]),
            "Name of Block": random.choice(["Main Block", "North Block", "South Block", "West Block"])
        },
        "Gram Vikas Internal Information": {
            "Name of GUM": random.choice(["GUM A", "GUM B", "GUM C", "GUM D"]),
            "GUM Mobile Number": random.randint(9000000000, 9999999999),
            "Date of Submission": datetime.now().strftime("%d/%m/%Y"),
            "Verified By": random.choice(["Officer A", "Officer B", "Officer C", "Officer D"])
        }
    }

@app.post("/process-image/")
async def process_image(
    file: UploadFile = File(...), 
    document_type: Optional[str] = Form(None)
):
    """
    Generate dummy financial data based on document type.
    
    Args:
        file: The uploaded image file (not actually processed, just validated)
        document_type: Optional document type ("PT Sheet Old", "PT Sheet New", "Daybook", "One Time Info Sheet")
    """
    try:
        # Read and validate the image file
        image_data = await file.read()
        try:
            # Validate that it's a valid image file
            Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

        # Generate dummy data based on document type
        if not document_type or document_type == "Daybook":
            result = generate_daybook_data()
        elif document_type == "PT Sheet Old":
            result = generate_pt_sheet_old_data()
        elif document_type == "PT Sheet New":
            result = generate_pt_sheet_new_data()
        elif document_type == "One Time Info Sheet":
            result = generate_one_time_info_data()
        else:
            # Default to Daybook if unknown document type
            result = generate_daybook_data()

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel handler
handler = Mangum(app)