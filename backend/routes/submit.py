from fastapi import APIRouter
from models.schema import UserResponse
from services.pdf_generator import generate_filled_pdf

router = APIRouter()

@router.post("/response")
async def submit_response(resp: UserResponse):
    # save resp under resp.session_id+resp.field_id
    return {"status": "saved"}

@router.get("/pdf/{session_id}")
async def get_pdf(session_id: str):
    url = await generate_filled_pdf(session_id)
    return {"pdf_url": url}
