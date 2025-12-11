# Deploy to Vercel

This API can be deployed to Vercel as a serverless function.

## Deployment Steps

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy the project:
   ```bash
   vercel
   ```

3. During deployment, Vercel will automatically detect the [vercel.json](file:///c:/Users/mayan/Downloads/GenAI_Image-API-main/GenAI_Image-API-main/vercel.json) configuration file and deploy accordingly.

## Configuration

- The [vercel.json](file:///c:/Users/mayan/Downloads/GenAI_Image-API-main/GenAI_Image-API-main/vercel.json) file tells Vercel how to build and route requests to the API
- The [api/index.py](file:///c:/Users/mayan/Downloads/GenAI_Image-API-main/GenAI_Image-API-main/api/index.py) file contains the FastAPI application with a Mangum wrapper for Vercel compatibility
- The [requirements.txt](file:///c:/Users/mayan/Downloads/GenAI_Image-API-main/GenAI_Image-API-main/requirements.txt) file includes all necessary dependencies including `mangum` for Vercel integration

## Endpoints

Once deployed, the API will have the following endpoints:
- `GET /` - Welcome message and API information
- `POST /process-image/` - Process an image and generate dummy financial data

The `document_type` parameter can be passed as form data with the following values:
- "Daybook"
- "PT Sheet Old"
- "PT Sheet New"
- "One Time Info Sheet"

## Notes

- This API generates dummy data for testing purposes and does not require any external API keys
- All processing happens server-side with no external dependencies
- The API supports CORS from any origin