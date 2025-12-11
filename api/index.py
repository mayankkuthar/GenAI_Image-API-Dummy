import os
import json
import re
import logging
import base64
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from dotenv import load_dotenv
import random
from datetime import timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Document configurations
DAYBOOK_SHEET_OUTPUT_STRUCTURE = '''
{
  "Day 1": {
    "Date": "date",
    "Cash Sale": "float",
    "Credit Sale": "float",
    "Cash Collection": "float",
    "Cash Purchase": "float",
    "Credit Purchase": "float",
    "Cash Paid to Suppliers": "float",
    "Transportation": "float",
    "Owner's Wages": "float", 
    "Workers' Wages": "float",
    "Electricity": "float",
    "Repairs": "float",
    "Other Cost": "float",
    "Other Income": "float",
    "Loan": "float",
    "Interest": "float",
    "Amount": "float"
  }
}
'''

PT_SHEET_OLD_OUTPUT_STRUCTURE = '''
{
  "Period 1": {
    "Time Period Information": {
      "Start Date": "date",
      "End Date": "date"
    },
    "Fixed Particulars": {
      "Cash Sales": "float",
      "Credit Sales": "float",
      "Cash Received from Debtors": "float",
      "Cash Purchase": "float",
      "Credit Purchase": "float",
      "Cash Given to Creditors": "float",
      "Owner's Wages": "float",
      "Transportation": "float",
      "Room Rent": "float",
      "Worker's Salary or Wages": "float",
      "Electricity or Fuel": "float",
      "Repair and Maintenance": "float",
      "Other Cost": "float",
      "Other Income": "float",
      "Loan Repayment": "float",
      "Interest on Loan": "float",
      "Owner's Investment": "float"
    },
    "Summary Particulars": {
      "Closing Cash Balance": "float",
      "Closing Bank Balance": "float",
      "Purchase of Fixed Asset": "float",
      "Sale of Fixed Asset": "float",
      "Security Deposit Given": "float",
      "Security Deposit Returned": "float",
      "Loan Taken": "float",
      "Source of Loan": "string",
      "Closing Inventory": "float"
    }
  }
}
'''

PT_SHEET_NEW_OUTPUT_STRUCTURE = '''
{
  "Period 1": {
    "Time Period Information": {
      "Period From": "date",
      "Period To": "date"
    },
    "Details": {
      "Cash Sales": "float",
      "Credit Sales": "float",
      "Cash Received (from Customers)": "float",
      "Cash Purchase": "float",
      "Credit Purchase": "float",
      "Cash Paid to Suppliers": "float",
      "Owner's Wages": "float",
      "Workers' Wages": "float",
      "Transportation": "float",
      "Electricity": "float",
      "Repairs": "float",
      "Other Expenses": "float",
      "Interest Paid": "float",
      "Loan Repaid": "float",
      "Other Income": "float"
    },
    "Details on Capital": {
      "Fixed Assets Purchased": "float",
      "Fixed Assets Sold": "float",
      "Owner Reinvested": "float",
      "Owner's Withdrawals": "float",
      "Loan Taken": "float",
      "Source of Loan": "string",
      "Inventory (Goods / Stock)": "float"
    }
  }
}
'''

ONETIME_INFO_SHEET_OUTPUT_STRUCTURE = '''
{
  "Profile Information": {
    "Enterprise ID Number": "string",
    "Name of the Enterprise": "string",
    "Name of the Entrepreneur": "string",
    "Types of Enterprise": "string",
    "Date of Starting the Enterprise": "string",
    "New or Existing": "string",
    "Intervention Date by GUM": "string",
    "Mobile Number": "integer"
  },
  "Financial Information": {
    "Total Investment": "float",
    "Total Fixed Capital": "float",
    "Owner's Investment": "float",
    "Loan from SHG": "float",
    "Loan from Bank": "float",
    "Other Source": "float"
  },
  "Geography Information": {
    "Name of SHG": "string",
    "Name of VO": "string",
    "Name of CLF": "string",
    "Name of Village": "string",
    "Name of Panchayat": "string",
    "Name of Block": "string"
  },
  "Gram Vikas Internal Information": {
    "Name of GUM": "string",
    "GUM Mobile Number": "integer",
    "Date of Submission": "string",
    "Verified By": "string"
  }
}
'''

DOCUMENT_CONFIG = {
    "PT Sheet Old": {
        "output_structure": PT_SHEET_OLD_OUTPUT_STRUCTURE,
    },
    "PT Sheet New": {
        "output_structure": PT_SHEET_NEW_OUTPUT_STRUCTURE,
    },
    "Daybook": {
        "output_structure": DAYBOOK_SHEET_OUTPUT_STRUCTURE,
    },
    "One Time Info Sheet": {
        "output_structure": ONETIME_INFO_SHEET_OUTPUT_STRUCTURE,
    }
}

BASE_SYSTEM_MESSAGE_COMMON = """
You are an advanced AI system specialized in analyzing enterprise financial document images and extracting specific information. Your task is to carefully examine the provided image and extract data according to a given output structure. This task requires you to handle various financial document types, including invoices, receipts, bank statements, financial reports, and handwritten or semi-structured forms.

First, review the output structure that specifies the information you need to extract:

<output_structure>
{{OUTPUT_STRUCTURE}}
</output_structure>

This output structure is in JSON format. Each key represents a piece of financial information to look for in the image, and the corresponding value indicates the expected data type.

Instructions:
1. Analyze the financial document image thoroughly.
2. Pay special attention to the alignment of columns and rows, especially if the image appears tilted or angled.
3. Extract all relevant information as specified in the output structure.
4. Double-check the correspondence between particulars and their associated values to ensure accurate matching.
5. Format your response as a JSON object that exactly matches the given output structure.
6. Use appropriate data types (strings, numbers, booleans, null) for each field.
7. If information for a field is not present in the image, use null for numbers and booleans, or an empty string for strings.
8. If any content is unreadable, use "##UNREADABLE##" in place of that content.
9. Include all specified fields, even if some are not present in the image.

Remember:
- Pay special attention to handwriting interpretation. If unsure about a value, mark it "##UNREADABLE##".
- Only output the JSON data. Do not include any explanations or additional text
- Adhere strictly to the provided output structure.
- Use appropriate data types (strings, numbers, booleans, null) for each field
- Include all specified fields, even if some information is not present or illegible in the image.

Now, proceed with your examination and data extraction from the provided enterprise financial document image.
"""

# Initialize environment variables
load_dotenv()

app = FastAPI(title="Image Processing API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Dummy data configuration
DUMMY_DATA_ENABLED = True  # Set to True to use dummy data instead of GenAI model

class JsonCorrector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_nested_json(self, text: str) -> str:
        """Extract the most complete JSON structure from text."""
        start = text.find('{')
        if start == -1:
            return text
        
        depth = 0
        in_string = False
        escape_char = False
        
        for i, char in enumerate(text[start:], start):
            if char == '\\' and not escape_char:
                escape_char = True
                continue
            
            if char == '"' and not escape_char:
                in_string = not in_string
            
            if not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start:i+1]
            
            escape_char = False
        
        return text[start:]

    def balance_braces(self, text: str) -> str:
        """Balance opening and closing braces in the JSON string."""
        text = self.extract_nested_json(text)
        open_count = text.count('{')
        close_count = text.count('}')
        
        if open_count > close_count:
            text += '}' * (open_count - close_count)
        elif close_count > open_count:
            text = '{' * (close_count - open_count) + text
            
        return text

    def fix_trailing_commas(self, text: str) -> str:
        """Remove trailing commas in objects and arrays."""
        text = re.sub(r',(\s*})', r'\1', text)
        text = re.sub(r',(\s*])', r'\1', text)
        return text

    def add_missing_quotes(self, text: str) -> str:
        """Add missing quotes around property names."""
        def replace_unquoted(match):
            return f'"{match.group(1)}":'
        return re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:', replace_unquoted, text)

    def fix_missing_values(self, text: str) -> str:
        """Replace empty values with appropriate defaults."""
        text = re.sub(r':\s*,', ': "",', text)
        text = re.sub(r':\s*}', ': ""}', text)
        text = re.sub(r':\s*null\s*([,}])', ': ""\\1', text)
        text = re.sub(r'\[\s*([^]\}]*?)(?:\s*$|\s*})', r'[\1]', text)
        return text

    def correct_json(self, text: str) -> dict:
        """Attempt to correct malformed JSON and return a valid dictionary."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                corrected = text
                corrected = self.extract_nested_json(corrected)
                corrected = self.balance_braces(corrected)
                corrected = self.fix_trailing_commas(corrected)
                corrected = self.add_missing_quotes(corrected)
                corrected = self.fix_missing_values(corrected)
                
                return json.loads(corrected)
            except json.JSONDecodeError as e:
                try:
                    # Extract key-value pairs for partial structure
                    partial_structure = {}
                    pattern = r'"([^"]+)"\s*:\s*(?:"([^"]*)"|\[([^\]]*)\]|(\d+\.?\d*)|(\{[^}]*\})|([^,}\]]*))(?:,|\}|\]|$)'
                    matches = re.finditer(pattern, corrected)
                    
                    for match in matches:
                        key = match.group(1)
                        value = next((v for v in match.groups()[1:] if v is not None), "")
                        
                        try:
                            if re.match(r'^\d+\.?\d*$', value):
                                value = float(value)
                            elif value.startswith('[') or value.startswith('{'):
                                try:
                                    value = json.loads(value)
                                except:
                                    pass
                        except:
                            pass
                        
                        current = partial_structure
                        key_parts = key.split('.')
                        for part in key_parts[:-1]:
                            if part not in current:
                                current[part] = {}
                            current = current[part]
                        current[key_parts[-1]] = value
                    
                    if partial_structure:
                        return partial_structure
                except Exception as e:
                    return {
                        "error": "JSON parsing failed",
                        "partial_content": text[:2000] + "..." if len(text) > 2000 else text
                    }
                return {
                    "error": "JSON parsing failed",
                    "partial_content": text[:2000] + "..." if len(text) > 2000 else text
                }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Image Processing API",
        "endpoints": {
            "/": "This welcome message",
            "/process-image/": "POST endpoint to process an image and extract information"
        }
    }

class ImageProcessor:
    def __init__(self, model_type="dummy"):
        """Initialize the image processor with dummy data generator."""
        self.model_type = model_type.lower()
        self.json_corrector = JsonCorrector()

    def generate_dummy_data(self, document_type: Optional[str] = None) -> Dict:
        """Generate dummy data based on document type."""
        logging.info(f"Generating dummy data for document type: {document_type}")
        
        if not document_type or document_type not in DOCUMENT_CONFIG:
            # Default to Daybook if no valid document type provided
            logging.warning(f"Invalid document type '{document_type}', defaulting to Daybook")
            document_type = "Daybook"
        
        # Get the structure for the document type
        structure = DOCUMENT_CONFIG[document_type]["output_structure"]
        
        # Parse the structure to understand the fields
        # We'll generate realistic dummy data based on the structure
        if document_type == "Daybook":
            logging.info("Generating Daybook dummy data")
            return self._generate_daybook_dummy()
        elif document_type == "PT Sheet Old":
            logging.info("Generating PT Sheet Old dummy data")
            return self._generate_pt_sheet_old_dummy()
        elif document_type == "PT Sheet New":
            logging.info("Generating PT Sheet New dummy data")
            return self._generate_pt_sheet_new_dummy()
        elif document_type == "One Time Info Sheet":
            logging.info("Generating One Time Info Sheet dummy data")
            return self._generate_one_time_info_dummy()
        else:
            # Fallback to a generic structure
            logging.info("Generating generic dummy data")
            return self._generate_generic_dummy(structure)
    
    def _generate_daybook_dummy(self) -> Dict:
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
    
    def _generate_pt_sheet_old_dummy(self) -> Dict:
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
    
    def _generate_pt_sheet_new_dummy(self) -> Dict:
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
    
    def _generate_one_time_info_dummy(self) -> Dict:
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
    
    def _generate_generic_dummy(self, structure: str) -> Dict:
        """Generate generic dummy data based on structure."""
        # Simple fallback that generates a basic structure

    async def process_single_image(self, image_data: bytes, document_type: Optional[str] = None) -> Dict:
        """Process a single image using dummy data generation."""
        try:
            # Generate dummy data instead of processing with AI model
            return self.generate_dummy_data(document_type)

        except Exception as e:
            error_msg = f"Error generating dummy data: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

# Initialize the image processor
image_processor = ImageProcessor(model_type="dummy")

@app.post("/process-image/")
async def process_image(
    file: UploadFile = File(...), 
    document_type: Optional[str] = Form(None)
):
    """
    Process an uploaded image and extract information based on document type.
    
    Args:
        file: The uploaded image file
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

        # Process the image
        result = await image_processor.process_single_image(image_data, document_type)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel, we need to export the app as a handler
from mangum import Mangum

# For Vercel, we need to create a handler
handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)