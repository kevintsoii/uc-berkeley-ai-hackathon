from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from ..models.schema import UserResponse
from ..services.pdf_worker import (
    generate_filled_pdf,
    validate_required_fields,
    get_filled_pdf_path
)
from .session import _SESSIONS
import os

# In‐memory storage of answers
_RESPONSES: dict[str, dict[str,str]] = {}

router = APIRouter(prefix="/sessions", tags=["submit"])

@router.post("/{session_id}/responses")
async def submit_response(session_id: str, resp: UserResponse):
    """Submit a response for a specific field in the form."""
    if session_id not in _SESSIONS:
        raise HTTPException(404, "Session not found")

    # Store the response
    _RESPONSES.setdefault(session_id, {})[resp.field_id] = resp.answer

    # Get current progress
    answers = _RESPONSES.get(session_id, {})
    validation = validate_required_fields(session_id, answers)

    return {
        "status": "saved",
        "field_id": resp.field_id,
        "progress": {
            "completion_percentage": validation.get("completion_percentage", 0),
            "filled_fields": validation.get("filled_fields", 0),
            "total_fields": validation.get("total_fields", 0)
        }
    }


@router.get("/{session_id}/responses")
async def get_responses(session_id: str):
    """Get all responses for a session."""
    if session_id not in _SESSIONS:
        raise HTTPException(404, "Session not found")

    answers = _RESPONSES.get(session_id, {})
    validation = validate_required_fields(session_id, answers)

    return {
        "session_id": session_id,
        "responses": answers,
        "validation": validation
    }

@router.get("/{session_id}/pdf")
async def get_filled_pdf(session_id: str):
    """Generate and return URL to the filled PDF."""
    if session_id not in _SESSIONS:
        raise HTTPException(404, "Session not found")

    answers = _RESPONSES.get(session_id, {})

    if not answers:
        raise HTTPException(400, "No responses found for this session")

    try:
        pdf_url = await generate_filled_pdf(session_id, answers)
        validation = validate_required_fields(session_id, answers)

        return {
            "pdf_url": pdf_url,
            "validation": validation,
            "ready_for_download": True
        }
    except Exception as e:
        raise HTTPException(500, f"Error generating PDF: {str(e)}")


@router.get("/{session_id}/pdf/download")
async def download_filled_pdf(session_id: str):
    """Directly download the filled PDF file."""
    if session_id not in _SESSIONS:
        raise HTTPException(404, "Session not found")

    answers = _RESPONSES.get(session_id, {})

    if not answers:
        raise HTTPException(400, "No responses found for this session")

    try:
        # Generate the PDF
        pdf_url = await generate_filled_pdf(session_id, answers)

        # Extract filename from URL
        filename = pdf_url.split("/")[-1]
        file_path = get_filled_pdf_path(filename)

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(404, "Generated PDF file not found")

        return FileResponse(
            path=file_path,
            filename=f"completed_form_{session_id}.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        raise HTTPException(500, f"Error downloading PDF: {str(e)}")


@router.post("/{session_id}/validate")
async def validate_form(session_id: str):
    """Validate the current form completion status."""
    if session_id not in _SESSIONS:
        raise HTTPException(404, "Session not found")

    answers = _RESPONSES.get(session_id, {})
    validation = validate_required_fields(session_id, answers)

    return {
        "session_id": session_id,
        "validation": validation,
        "is_complete": validation.get("valid", False),
        "can_generate_pdf": len(answers) > 0
    }


@router.delete("/{session_id}/responses")
async def clear_responses(session_id: str):
    """Clear all responses for a session."""
    if session_id not in _SESSIONS:
        raise HTTPException(404, "Session not found")

    if session_id in _RESPONSES:
        del _RESPONSES[session_id]

    return {"status": "cleared", "session_id": session_id}
