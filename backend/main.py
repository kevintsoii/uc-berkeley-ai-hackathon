# main.py

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import shutil
import uuid
import json

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

# Create upload directory
os.makedirs("uploads", exist_ok=True)

@app.get("/")
def read_root():
    return {"language": language, "file_name": file_name, "default_form": default_form}

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
async def process_form(request: Request):
    global language, file_name, default_form
    data = await request.json()
    language = data.get("language", "en")
    file_name = data.get("file_name", "form.pdf")
    default_form = data.get("default_form", False)

    return {
        "message": "Form processed successfully"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
