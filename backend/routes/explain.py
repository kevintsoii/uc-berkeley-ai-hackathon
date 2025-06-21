from fastapi import APIRouter
from models.schema import FieldExplainRequest, FieldExplainResponse
from services.groq_client import explain_field

router = APIRouter()

@router.post("/field", response_model=FieldExplainResponse)
async def explain_field_endpoint(req: FieldExplainRequest):
    return await explain_field(req.field_id, req.question, req.language)
