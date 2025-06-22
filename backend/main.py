from fastapi import FastAPI, HTTPException, File, UploadFile, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import shutil
import uuid
import json
import requests
from dotenv import load_dotenv
import os
import logging
import asyncio
from deep_translator import GoogleTranslator
import base64
import os
from pypdf import PdfReader
from google import genai
from pydantic import BaseModel
from google.genai import types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

language = "en"
file_name = "form.pdf"
default_form = False
processing = False
activated_assistant = False

# Create upload directory
os.makedirs("uploads", exist_ok=True)

VAPI_API_URL = "https://api.vapi.ai/assistant"
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


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


    # Default form fields - in a real app, this could be determined by the uploaded PDF
form_fields = [
    {
        "id": 1,
        "field": "First Name",
        "description": "Please provide your first name as it appears on your official documents.",
        "type": "text",
        "required": True,
        "value": "",
    },
    {
        "id": 2,
        "field": "Middle Name",
        "description": "Please provide your middle name as it appears on your official documents.",
        "type": "text",
        "required": False,
        "value": "",
    },
    {
        "id": 3,
        "field": "Last Name",
        "description": "Please provide your last name as it appears on your official documents.",
        "type": "text",
        "required": True,
        "value": "",
    },
]

# Pydantic model for request validation
class AssistantUpdateRequest(BaseModel):
    language: str
    heading: str
    form_type: str

class LanguageUpdateRequest(BaseModel):
    language: str

class FieldValueRequest(BaseModel):
    value: str

@app.get("/")
def read_root():
    return {"language": language, "file_name": file_name, "default_form": default_form}

@app.get("/language")
def get_language():
    return {"language": language}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Use original filename
    filename = file.filename
    file_path = f"uploads/{filename}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "message": "File uploaded successfully"
    }

@app.post("/process")
async def process_form(request: Request, background_tasks: BackgroundTasks):
    global language, file_name, default_form, processing
    data = await request.json()
    language = data.get("language", "en")
    file_name = data.get("file_name", "form.pdf")
    default_form = data.get("default_form", False)
    for field in form_fields:
        field["value"] = ""

    processing = True
    
    # Start background processing task
    # run the process function
    background_tasks.add_task(process)

    return {
        "message": "Form processing started"
    }

async def process():
    global processing, file_name
    if default_form:
        file_name = "forms/defualt/" + file_name
    else:
        file_name = "uploads/" +file_name

    # read file
    print("Current working directory:", os.getcwd())
    reader = PdfReader(file_name)
    
    raw_fields = reader.get_fields()
    full_text = "\n".join(
        page.extract_text() or ""  # fallback to empty string if extract_text() fails
        for page in reader.pages
    )
    fields = []
    for name, field in raw_fields.items():
        field_type = field.get("/FT")
        if field_type == "/Tx":  # Only include text fields
            fields.append({
                "name": name,
                #"value": str(field.get("/V", "")),
                #"type": str(field_type),
                "label": str(field.get("/TU", "")),
            })


    # gemini hydration
    temp_file = "abc.txt"
    with open(temp_file, "w") as f:
        json.dump(fields, f)

    file = await client.aio.files.upload(file=temp_file)
    file_name = file.name
    myfile = await client.aio.files.get(name=file_name)

    prompt = f"""
        You are a helpful assistant for immigration documents, helping foreign migrants fill out forms and understand the instructions.
        I want you to hydrate each of the form fields with a human label and human description, and return the 
        full hydrated object in the provided format.

        The form fields with values [name, value, type, label] is attached.

    """
       # I also have the full text of the pdf form for context:
       # {full_text}

    class FormField(BaseModel):
        name: str
        value: str
        type: str
        label: str
        human_label: str
        human_description: str

    print('gemini starting')
    response = await client.aio.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            prompt, myfile
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": list[FormField],
        },
    )
    print('gemini done')

    # 4) Parse & return
    result = response.text
    input(result)
    #result = json.loads(response.text)
    print(result)

    
    processing = False
    return

@app.get("/fill/{page_id}")
def get_page_info(page_id: str):
    if processing:
        return {"message": "Form is being processed"}
    
    
    try:
        page_num = int(page_id)
        if page_num < 1 or page_num > len(form_fields):
            raise HTTPException(status_code=404, detail="Page not found")
        
        current_field = form_fields[page_num - 1]
        
        return {
            "current_field": current_field,
            "total_pages": len(form_fields),
            "current_page": page_num,
            "progress": (page_num / len(form_fields)) * 100
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid page ID")

@app.post("/fill/{page_id}")
def save_field_value(page_id: str, request: FieldValueRequest):
    try:
        page_num = int(page_id)

        if page_num < 1 or page_num > len(form_fields):
            raise HTTPException(status_code=404, detail="Page not found")

        current_field = form_fields[page_num - 1]
        current_field["value"] = request.value

        return {"message": "Value saved successfully"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid page ID")



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
        
        if not globals().get('activated_assistant', False):
            first_message_template = "Hello! I am Bridge, your immigration form assistant. What did you want me to explain?"
            globals()['activated_assistant'] = True
        else: 
            first_message_template = "How can I help you?"
        
        # Translate the first message to the user's language
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
            "silenceTimeoutSeconds": 30,
            "startSpeakingPlan": {
                "waitSeconds": 0
            }   
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


# Update the language of the assistant
@app.post("/update-language")
async def update_language(request: LanguageUpdateRequest):
    global language
    language = request.language
    return {
        "message": f"Language updated to {language}",
        "language": language
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)