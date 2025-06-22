# Backend Server Setup

This backend server provides an API endpoint to update Vapi assistants with context and language settings.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the backend directory with:
   ```
   VAPI_API_KEY=your_vapi_api_key_here
   ```
   
   Get your Vapi API key from: https://console.vapi.ai/

3. **Run the server:**
   ```bash
   python main.py
   ```
   
   The server will start on http://localhost:8000

## API Endpoints

### PATCH /assistant/{assistant_id}

Updates a Vapi assistant with new context and language settings.

**Request Body:**
```json
{
  "language": "es",
  "heading": "First Name", 
  "form_type": "I-130"
}
```

**Response:**
- `200 OK`: Assistant updated successfully
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Server error or Vapi API error

## Testing

Run the test script to verify the endpoint works:

```bash
python test_endpoint.py
```

This will:
1. Check if the backend is running
2. Verify environment variables are set
3. Test the assistant update endpoint
4. Show detailed error information if something fails

## Troubleshooting

### Common Issues:

1. **"VAPI_API_KEY not found"**
   - Make sure you have a `.env` file with your Vapi API key
   - Get your API key from https://console.vapi.ai/

2. **"Connection error"**
   - Make sure the backend server is running on port 8000
   - Check if another process is using the port

3. **"Vapi API error"**
   - Check your API key is valid
   - Verify the assistant ID exists in your Vapi account
   - Check the Vapi API documentation for error details

4. **CORS errors from frontend**
   - The backend is configured to allow requests from localhost:3000
   - If using a different port, update the CORS settings in main.py 