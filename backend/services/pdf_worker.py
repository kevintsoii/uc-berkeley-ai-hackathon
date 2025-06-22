import os
import uuid
from pathlib import Path
from typing import Dict, Optional
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject, BooleanObject

STATIC_FORMS_DIR = Path("static/forms")  # Where USCIS forms are stored
OUTPUT_DIR = Path("output/filled_pdfs")  # Where filled PDFs are saved
BASE_URL = "http://localhost:8000"  # Your FastAPI server URL

def extract_fields_with_coords(pdf_path):
    reader = PdfReader(pdf_path)
    fields = []
    for page_num, page in enumerate(reader.pages, start=1):
        for annot in page.get("/Annots", []):
            obj = annot.get_object()
            name = obj.get("/T")
            rect = obj.get("/Rect")
            if name and rect:
                x1, y1, x2, y2 = rect
                fields.append({
                    "field_id": name,
                    "page":     page_num,
                    "coords":   [x1, y1, x2, y2],
                })
    return fields


def fill_pdf_form(input_pdf_path: str, output_pdf_path: str, field_data: Dict[str, str]) -> bool:
    """
    Fill PDF form fields with provided data using pypdf.

    Args:
        input_pdf_path: Path to the original PDF form
        output_pdf_path: Path where filled PDF will be saved
        field_data: Dictionary mapping field_id to field_value

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        # Process each page
        for page_num, page in enumerate(reader.pages):
            # Check if page has annotations (form fields)
            if "/Annots" in page:
                annotations = page["/Annots"]

                # Process each annotation
                for annot in annotations:
                    field = annot.get_object()

                    # Check if this is a form field with a name
                    if "/T" in field:
                        field_name = field["/T"]

                        # If we have data for this field, fill it
                        if field_name in field_data:
                            field_value = field_data[field_name]
                            field_type = field.get("/FT")

                            # Handle different field types
                            if field_type == "/Tx":  # Text field
                                field.update({
                                    NameObject("/V"): TextStringObject(field_value)
                                })
                            elif field_type == "/Ch":  # Choice field (dropdown/listbox)
                                field.update({
                                    NameObject("/V"): TextStringObject(field_value)
                                })
                            elif field_type == "/Btn":  # Button field (checkbox/radio)
                                # For checkboxes, expect "true"/"false" or "yes"/"no"
                                is_checked = field_value.lower() in ["true", "yes", "1", "on"]
                                if is_checked:
                                    # Find the "Yes" value for this checkbox
                                    if "/AP" in field and "/N" in field["/AP"]:
                                        ap_dict = field["/AP"]["/N"]
                                        if isinstance(ap_dict, dict):
                                            # Usually checkboxes have keys like "Yes", "Off", etc.
                                            yes_keys = [k for k in ap_dict.keys() if k != "/Off"]
                                            if yes_keys:
                                                field.update({
                                                    NameObject("/V"): NameObject(yes_keys[0]),
                                                    NameObject("/AS"): NameObject(yes_keys[0])
                                                })
                                else:
                                    field.update({
                                        NameObject("/V"): NameObject("/Off"),
                                        NameObject("/AS"): NameObject("/Off")
                                    })

                            # Make field read-only (optional)
                            # field.update({NameObject("/Ff"): 1})  # Read-only flag

            # Add the page to the writer
            writer.add_page(page)

        # Copy form information
        if "/AcroForm" in reader.trailer["/Root"]:
            writer._root_object.update({
                NameObject("/AcroForm"): reader.trailer["/Root"]["/AcroForm"]
            })

        # Write the filled PDF
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)

        return True

    except Exception as e:
        print(f"Error filling PDF: {e}")
        return False


def validate_required_fields(session_id: str, answers: Dict[str, str]) -> Dict[str, any]:
    """
    Validate that all required fields are filled.

    Args:
        session_id: The session ID
        answers: Dictionary of user answers

    Returns:
        dict: Validation result with missing fields and completion status
    """
    from ..routes.session import _SESSIONS

    if session_id not in _SESSIONS:
        return {"valid": False, "error": "Session not found"}

    session_info = _SESSIONS[session_id]
    required_fields = session_info.get("required_fields", [])

    missing_fields = [field for field in required_fields if field not in answers or not answers[field].strip()]

    completion_percentage = len(answers) / len(session_info.get("all_fields", [])) * 100 if session_info.get(
        "all_fields") else 0

    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "completion_percentage": round(completion_percentage, 2),
        "total_fields": len(session_info.get("all_fields", [])),
        "filled_fields": len(answers)
    }

def get_form_path(session_id: str, sessions_data: dict) -> Optional[str]:
    """
    Get the path to the original form PDF based on session data.

    Args:
        session_id: The session ID
        sessions_data: The _SESSIONS dictionary containing session info

    Returns:
        str: Path to the form PDF, or None if not found
    """
    if session_id not in sessions_data:
        return None

    session_info = sessions_data[session_id]
    form_name = session_info.get("form_name")  # e.g., "i-94.pdf"

    if form_name:
        form_path = STATIC_FORMS_DIR / form_name
        if form_path.exists():
            return str(form_path)

    return None


async def generate_filled_pdf(session_id: str, answers: Dict[str, str]) -> str:
    """
    Generate a filled PDF based on user responses.

    Args:
        session_id: The session ID
        answers: Dictionary mapping field_id to user answers

    Returns:
        str: URL to the filled PDF
    """
    from ..routes.session import _SESSIONS  # Import here to avoid circular imports

    # Get the original form path
    form_path = get_form_path(session_id, _SESSIONS)
    if not form_path:
        raise ValueError(f"Form not found for session {session_id}")

    # Generate unique filename for filled PDF
    filled_filename = f"filled_{session_id}_{uuid.uuid4().hex[:8]}.pdf"
    output_path = OUTPUT_DIR / filled_filename

    # Fill the PDF
    success = fill_pdf_form(str(form_path), str(output_path), answers)

    if not success:
        raise RuntimeError("Failed to fill PDF form")

    # Return URL to access the filled PDF
    return f"{BASE_URL}/files/filled_pdfs/{filled_filename}"


def get_filled_pdf_path(filename: str) -> Optional[str]:
    """
    Get the full path to a filled PDF file.

    Args:
        filename: The filename of the filled PDF

    Returns:
        str: Full path to the file, or None if not found
    """
    file_path = OUTPUT_DIR / filename
    return str(file_path) if file_path.exists() else None

