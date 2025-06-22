from fastapi import APIRouter, HTTPException
from models.schema          import UserResponse
from services.pdf_worker import generate_filled_pdf
from routes.session         import _SESSIONS

# In‐memory storage of answers
_RESPONSES: dict[str, dict[str,str]] = {}

router = APIRouter(prefix="/sessions", tags=["submit"])

@router.post("/{session_id}/responses")
async def submit_response(session_id: str, resp: UserResponse):
    if session_id not in _SESSIONS:
        raise HTTPException(404, "Session not found")
    _RESPONSES.setdefault(session_id, {})[resp.field_id] = resp.answer
    return {"status": "saved"}

@router.get("/{session_id}/pdf")
async def get_filled_pdf(session_id: str):
    if session_id not in _SESSIONS:
        raise HTTPException(404, "Session not found")
    answers = _RESPONSES.get(session_id, {})
    pdf_url = await generate_filled_pdf(session_id, answers)
    return {"pdf_url": pdf_url}
