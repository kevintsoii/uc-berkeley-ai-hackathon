import uuid
from fastapi import APIRouter, Form, HTTPException
from models.schema   import FormSchema, SessionSchema
from services.gemini_client import analyze_form

# In‐memory store (swap out for Redis/Postgres later)
_SESSIONS: dict[str, SessionSchema] = {}

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", response_model=SessionSchema)
async def create_session(
    form_id:  str = Form(..., description="USCIS form ID, e.g. I-765"),
    language: str = Form("en", description="Output language code")
):
    # 1) load form + instruction bytes from disk
    #    (you could also support file-upload here)
    schema: FormSchema = await analyze_form(form_id, language)

    # 2) wrap with a session_id
    session_id = str(uuid.uuid4())
    session = SessionSchema(session_id=session_id, **schema.dict())

    # 3) store
    _SESSIONS[session_id] = session
    return session

@router.get("/{session_id}", response_model=SessionSchema)
async def read_session(session_id: str):
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session
