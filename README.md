# Financial Document Processing API

This FastAPI-based API generates dummy financial data for testing purposes. The API supports various financial document types and returns sample data in JSON format.

## Features

- Image upload (validated but not processed)
- Support for multiple document types:
  - PT Sheet (Old and New formats)
  - Daybook
  - One Time Info Sheet
- Robust JSON correction and validation
- CORS enabled for cross-origin requests
- Ready for Vercel deployment

## Prerequisites

- Python 3.8 or higher

## Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root (optional):
```env
# GOOGLE_API_KEY is no longer required
```

5. Run the API locally:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### GET /
- Welcome message and API information
- Returns: List of available endpoints and their descriptions

### POST /process-image/
Process an image and extract information based on document type.

**Parameters:**
- `file`: Image file (form-data)
- `document_type`: (Optional) Type of document to process
  - Options: "PT Sheet Old", "PT Sheet New", "Daybook", "One Time Info Sheet"

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/process-image/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg" \
  -F "document_type=Daybook"
```

**Example using Python requests:**
```python
import requests

url = "http://localhost:8000/process-image/"
files = {
    'file': open('your_image.jpg', 'rb')
}
data = {
    'document_type': 'Daybook'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Example Responses

### Daybook Document
```json
{
  "Day 1": {
    "Date": "15/10/2025",
    "Cash Sale": 5000.0,
    "Credit Sale": 2000.0,
    "Cash Collection": 1500.0,
    "Cash Purchase": 3000.0,
    "Credit Purchase": 1000.0,
    "Cash Paid to Suppliers": 2500.0,
    "Transportation": 200.0,
    "Owner's Wages": 500.0,
    "Workers' Wages": 1000.0,
    "Electricity": 300.0,
    "Repairs": 150.0,
    "Other Cost": 100.0,
    "Other Income": 50.0,
    "Loan": 0.0,
    "Interest": 0.0,
    "Amount": 750.0
  }
}
```

## Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set up environment variables in Vercel:
- Go to your project settings
- Add the `GOOGLE_API_KEY` environment variable

## Testing the API

1. Start the API locally:
```bash
uvicorn main:app --reload
```

2. Open the interactive Swagger documentation:
- Visit `http://localhost:8000/docs` in your browser
- Test the endpoints using the interactive interface

3. Try different document types:
- Upload sample images for each document type
- Verify the JSON output matches the expected structure
- Check error handling by uploading invalid files

## Error Handling

The API includes comprehensive error handling:
- Invalid file types
- Malformed images
- Invalid document types
- AI processing errors
- JSON parsing errors

Error responses include detailed messages to help identify and resolve issues.

## CORS

CORS is enabled for all origins by default. Modify the CORS settings in `main.py` if you need to restrict access.