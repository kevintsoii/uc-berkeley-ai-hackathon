from pydantic import BaseModel
from typing import List, Optional

class FormUploadRequest(BaseModel):
    form_id: str

class FieldSchema(BaseModel):
    field_id:     str
    label:        str
    type:         str
    page:         int
    dependencies: List[str] = []
    gemini_note:  Optional[str]
    examples:     List[str] = []

class FormSchema(BaseModel):
    form_id: str
    fields:  List[FieldSchema]

class FieldExplainRequest(BaseModel):
    field_id: str
    question: str
    language: str = "en"

class FieldExplainResponse(BaseModel):
    explanation: str
    example:     str

class UserResponse(BaseModel):
    session_id: str
    field_id:   str
    answer:     str
