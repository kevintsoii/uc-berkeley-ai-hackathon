from fastapi import APIRouter, HTTPException
from models.schema           import FieldExplainRequest, FieldExplainResponse
from services.groq_client    import explain_field as groq_explain
from routes.session          import _SESSIONS

router = APIRouter(prefix="/sessions", tags=["explain"])

@router.post(
    "/{session_id}/fields/{field_id}/explain",
    response_model=FieldExplainResponse
)
async def explain_field(
    session_id: str,
    field_id:   str,
    req:        FieldExplainRequest
):
    # verify session & field exist
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    if field_id not in {f.field_id for f in session.fields}:
        raise HTTPException(404, "Field not found in session")

    # delegate to Groq
    return await groq_explain(field_id, req.language)
