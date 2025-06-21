# main.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# === Models ===
class FormUploadRequest(BaseModel):
    form_id: str  # e.g. "I-765"

class FieldExplainRequest(BaseModel):
    field_label: str
    field_question: str
    language: Optional[str] = "en"

class UserResponse(BaseModel):
    session_id: str
    field_id: str
    response: str

# === Endpoints ===

@app.post("/upload-form")
async def upload_form(req: FormUploadRequest):
    # TODO: Call Gemini here to analyze form
    return {"status": "processing", "form_id": req.form_id}

@app.get("/form-schema/{form_id}")
async def get_form_schema(form_id: str):
    # TODO: Fetch parsed form schema
    return {"form_id": form_id, "fields": []}

@app.post("/explain-field")
async def explain_field(req: FieldExplainRequest):
    # TODO: Call Groq here and return explanation
    return {
        "field": req.field_question,
        "explanation": "This means ...",
        "example": "For example ..."
    }

@app.post("/submit-response")
async def submit_response(resp: UserResponse):
    # TODO: Save response to DB or memory
    return {"status": "saved", "field_id": resp.field_id}

@app.get("/generate-pdf/{session_id}")
async def generate_pdf(session_id: str):
    # TODO: Use saved responses to fill out PDF
    return {"pdf_url": f"/downloads/{session_id}.pdf"}
