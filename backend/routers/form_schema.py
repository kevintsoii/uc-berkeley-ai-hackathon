from fastapi import APIRouter, HTTPException, Query, status
from services import pdf_utils, gemini_qna, cache
from pathlib import Path

router = APIRouter(prefix="/form-schema", tags=["Form schema"])

@router.get("/{form_id}")
async def get_schema(
    form_id: str,
    lang: str = Query("English", description="Target language, e.g. Spanish")
):
    cached = cache.load_cached(form_id, lang)
    if cached:
        return cached

    return _generate_schema(form_id, lang)

def _generate_schema(form_id: str, lang: str) -> dict:
    """
    Build the questions JSON with Gemini, save it to disk-cache,
    and return the result.  Raises 404 if the PDFs aren't found.
    """
    try:
        base_dir = Path(f"static/forms/{form_id}")

        raw = pdf_utils.extract_fields_with_coords(f"static/forms/{form_id}/form.pdf")
        grouped = pdf_utils.group_widgets(raw)

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form {form_id} not found",
        )

    schema = gemini_qna.match_fields(grouped, form_id, lang)
    schema["lang"] = lang
    cache.save_cache(form_id, schema, lang)
    return schema
