from fastapi import APIRouter, UploadFile, File
from models.schema import FormUploadRequest, FormSchema
from services.gemini_client import analyze_form

router = APIRouter()

@router.post("/upload", response_model=FormSchema)
async def upload_form(req: FormUploadRequest):
    schema = await analyze_form(req.form_id)
    # persist schema in-memory or DB
    return schema

@router.get("/schema/{form_id}", response_model=FormSchema)
async def get_schema(form_id: str):
    # retrieve persisted schema
    ...
