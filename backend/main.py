from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests
from dotenv import load_dotenv
import os
import logging
from deep_translator import GoogleTranslator


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VAPI_API_URL = "https://api.vapi.ai/assistant"
VAPI_API_KEY = os.getenv("VAPI_API_KEY")

# Language code to full language name mapping for Vapi API
LANGUAGE_MAPPING = {
    "en": "English",
    "es": "Spanish", 
    "zh": "Chinese",
    "hi": "Hindi",
    "ar": "Arabic",
    "pt": "Portuguese",
    "ru": "Russian",
    "fr": "French",
    "de": "German",
    "ja": "Japanese",
    "ko": "Korean",
    "it": "Italian",
    "nl": "Dutch",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "pl": "Polish",
    "tr": "Turkish",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "he": "Hebrew",
    "el": "Greek",
    "cs": "Czech",
    "sk": "Slovak",
    "hu": "Hungarian",
    "ro": "Romanian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "sl": "Slovenian",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "sr": "Serbian",
    "bn": "Bengali",
    "sw": "Swahili",
    "uk": "Ukrainian"
}

# Pydantic model for request validation
class AssistantUpdateRequest(BaseModel):
    language: str
    heading: str
    form_type: str

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Update the Vapi Assistant to help with the specific section of the form
@app.patch("/assistant/{assistant_id}")
def update_assistant(assistant_id: str, request: AssistantUpdateRequest):
    try:
        logger.info(f"Updating assistant {assistant_id} with language: {request.language}, heading: {request.heading}, form_type: {request.form_type}")
        
        # Check if API key is available
        if not VAPI_API_KEY:
            logger.error("VAPI_API_KEY not found in environment variables")
            raise HTTPException(status_code=500, detail="VAPI API key not configured")
        
        # Convert language code to full language name
        language_name = LANGUAGE_MAPPING.get(request.language.lower(), "English")
        logger.info(f"Converted language code '{request.language}' to '{language_name}'")
        
        # Translate the first message to the user's language
        first_message_template = f"Hello! I am Bridge, your immigration form assistant. I see that you are filling out the {request.heading} section of the {request.form_type} form. What did you want me to explain?"
        translated_message = GoogleTranslator(source='auto', target=request.language).translate(first_message_template)
        logger.info(f"Translated first message to '{request.language}': {translated_message}")

        payload = {
            "transcriber": {
                "provider": "google",
                "language": language_name,
                "model": "gemini-2.5-flash-preview-05-20"
            },
            "backgroundDenoisingEnabled": True,
            "model": {
                "provider": "google",
                "model": "gemini-2.5-pro-preview-05-06",
                "maxTokens": 10000,
                "emotionRecognitionEnabled": True,
                "systemPrompt": f'''
                        You are a multilingual, empathetic, and knowledgeable AI voice assistant that helps immigrants understand and complete U.S. immigration forms. 
                        You provide clear, step-by-step support in the user's preferred language, using simple and culturally respectful language.
                        You are currently helping the user understand and fill out the {request.form_type} form.
                        You are currently helping the user with the section: {request.heading}.
                        '''
            },
            "firstMessage": translated_message,
            "endCallMessage": "Have a great day! Let me know if you need any more help.",
            "firstMessageMode": "assistant-speaks-first",
            "maxDurationSeconds": 43200, 
            "silenceTimeoutSeconds": 30   
        }

        headers = {
            "Authorization": f"Bearer {VAPI_API_KEY}",
            "Content-Type": "application/json"
        }

        logger.info(f"Making PATCH request to {VAPI_API_URL}/{assistant_id}")
        logger.info(f"Payload: {payload}")
        
        response = requests.patch(f"{VAPI_API_URL}/{assistant_id}", headers=headers, json=payload)
        
        logger.info(f"Vapi API response status: {response.status_code}")
        logger.info(f"Vapi API response: {response.text}")
        
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error from Vapi API: {http_err}")
        logger.error(f"Response status: {response.status_code}")
        logger.error(f"Response text: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=f"Vapi API error: {response.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)