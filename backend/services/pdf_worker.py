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

def i765_field_context() -> Dict:
    """
    Hard-coded context descriptions for I-765 form fields.
    This ensures 100% accuracy for legal document processing.
    """

    # I-765 Field Context Database - COMPLETE MAPPING
    FIELD_CONTEXTS = {
        # PART 1: REASON FOR APPLYING
        "Part1_Checkbox[0]": {
            "legal_purpose": "Application reason - Initial permission",
            "context_description": "Initial permission to accept employment - First time applying for work authorization",
            "field_category": "application_type",
            "required": True,
            "mutually_exclusive_group": "application_reason",
            "legal_note": "Select this if you have never had US work authorization before",
            "user_guidance": "Choose this option if this is your first time requesting permission to work in the United States"
        },
        "Part1_Checkbox[1]": {
            "legal_purpose": "Application reason - Replacement",
            "context_description": "Replacement of lost/stolen/damaged employment authorization document (not due to USCIS error)",
            "field_category": "application_type",
            "required": True,
            "mutually_exclusive_group": "application_reason",
            "legal_note": "For replacing lost, stolen, or damaged work cards - requires filing fee",
            "user_guidance": "Choose this if you need to replace a work authorization card that was lost, stolen, or damaged"
        },
        "Part1_Checkbox[2]": {
            "legal_purpose": "Application reason - Renewal",
            "context_description": "Renewal of existing employment authorization permission",
            "field_category": "application_type",
            "required": True,
            "mutually_exclusive_group": "application_reason",
            "legal_note": "Must attach copy of previous employment authorization document",
            "user_guidance": "Choose this if you currently have work authorization that is expiring and you need to renew it"
        },
        "CheckBox1[0]": {
            "legal_purpose": "Attorney representation indicator",
            "context_description": "Indicates Form G-28 (attorney representation form) is attached",
            "field_category": "legal_representation",
            "required": False,
            "legal_note": "Only check if you have an attorney and Form G-28 is included",
            "user_guidance": "Check this box only if you have a lawyer helping you and they have filed Form G-28"
        },
        
        # PART 2: PRIMARY LEGAL IDENTITY
        "Line1a_FamilyName[0]": {
            "legal_purpose": "Primary legal identity - family name",
            "context_description": "Your current legal family name (last name) as shown on passport",
            "field_category": "legal_identity_primary",
            "required": True,
            "legal_note": "Must match passport exactly - this is your official legal name",
            "user_guidance": "Enter your family name (last name) exactly as it appears on your passport"
        },
        "Line1b_GivenName[0]": {
            "legal_purpose": "Primary legal identity - given name",
            "context_description": "Your current legal given name (first name) as shown on passport",
            "field_category": "legal_identity_primary",
            "required": True,
            "legal_note": "Must match passport exactly",
            "user_guidance": "Enter your given name (first name) exactly as it appears on your passport"
        },
        "Line1c_MiddleName[0]": {
            "legal_purpose": "Primary legal identity - middle name",
            "context_description": "Your current legal middle name as shown on passport (if any)",
            "field_category": "legal_identity_primary",
            "required": False,
            "legal_note": "Leave blank if you don't have a middle name on your passport",
            "user_guidance": "Enter your middle name if you have one on your passport, otherwise leave blank"
        },
        
        # OTHER NAMES USED (ALIASES) - Set 1
        "Line2a_FamilyName[0]": {
            "legal_purpose": "Alias family name #1",
            "context_description": "Other family name you have used (alias, maiden name, previous name)",
            "field_category": "legal_identity_aliases",
            "required": False,
            "legal_note": "Include all other names you have ever used legally",
            "user_guidance": "If you have used a different last name before (maiden name, previous marriage, etc.), enter it here"
        },
        "Line2b_GivenName[0]": {
            "legal_purpose": "Alias given name #1",
            "context_description": "Other given name you have used (alias, nickname with legal use)",
            "field_category": "legal_identity_aliases",
            "required": False,
            "legal_note": "Include any first names used on official documents",
            "user_guidance": "If you have used a different first name on official documents, enter it here"
        },
        "Line2c_MiddleName[0]": {
            "legal_purpose": "Alias middle name #1",
            "context_description": "Other middle name you have used",
            "field_category": "legal_identity_aliases",
            "required": False,
            "legal_note": "Any middle names used on official documents",
            "user_guidance": "If you have used a different middle name on official documents, enter it here"
        },
        
        # OTHER NAMES USED (ALIASES) - Set 2
        "Line3a_FamilyName[0]": {
            "legal_purpose": "Alias family name #2",
            "context_description": "Additional other family name you have used",
            "field_category": "legal_identity_aliases",
            "required": False,
            "legal_note": "Continue listing all other names used",
            "user_guidance": "If you have used another different last name, enter it here"
        },
        "Line3b_GivenName[0]": {
            "legal_purpose": "Alias given name #2",
            "context_description": "Additional other given name you have used",
            "field_category": "legal_identity_aliases",
            "required": False,
            "user_guidance": "If you have used another different first name, enter it here"
        },
        "Line3c_MiddleName[0]": {
            "legal_purpose": "Alias middle name #2",
            "context_description": "Additional other middle name you have used",
            "field_category": "legal_identity_aliases",
            "required": False,
            "user_guidance": "If you have used another different middle name, enter it here"
        },
        
        # OTHER NAMES USED (ALIASES) - Set 3
        "Line3a_FamilyName[1]": {
            "legal_purpose": "Alias family name #3",
            "context_description": "Additional other family name you have used",
            "field_category": "legal_identity_aliases",
            "required": False,
            "user_guidance": "If you have used yet another different last name, enter it here"
        },
        "Line3b_GivenName[1]": {
            "legal_purpose": "Alias given name #3",
            "context_description": "Additional other given name you have used",
            "field_category": "legal_identity_aliases",
            "required": False,
            "user_guidance": "If you have used yet another different first name, enter it here"
        },
        "Line3c_MiddleName[1]": {
            "legal_purpose": "Alias middle name #3",
            "context_description": "Additional other middle name you have used",
            "field_category": "legal_identity_aliases",
            "required": False,
            "user_guidance": "If you have used yet another different middle name, enter it here"
        },
        
        # USCIS ACCOUNT INFORMATION
        "USCISELISAcctNumber[0]": {
            "legal_purpose": "USCIS online account number",
            "context_description": "Your USCIS online account number (if you have one)",
            "field_category": "uscis_account",
            "required": False,
            "legal_note": "Only provide if you have created a USCIS online account",
            "user_guidance": "Enter your USCIS online account number if you have one, otherwise leave blank"
        },
        
        # MAILING ADDRESS
        "Line4a_InCareofName[0]": {
            "legal_purpose": "Mailing address - Care of",
            "context_description": "In care of name for mailing address (if applicable)",
            "field_category": "address_mailing",
            "required": False,
            "user_guidance": "If your mail goes to someone else's attention, enter their name here"
        },
        "Line4b_StreetNumberName[0]": {
            "legal_purpose": "Mailing address - Street",
            "context_description": "Street number and name for your mailing address",
            "field_category": "address_mailing",
            "required": True,
            "user_guidance": "Enter the street address where you want to receive mail from USCIS"
        },
        "Pt2Line5_CityOrTown[0]": {
            "legal_purpose": "Mailing address - City",
            "context_description": "City or town for your mailing address",
            "field_category": "address_mailing",
            "required": True,
            "user_guidance": "Enter the city for your mailing address"
        },
        "Pt2Line5_State[0]": {
            "legal_purpose": "Mailing address - State",
            "context_description": "State for your mailing address",
            "field_category": "address_mailing",
            "required": True,
            "user_guidance": "Enter the state for your mailing address (2-letter abbreviation)",
            "data_format": "2-letter state code"
        },
        "Pt2Line5_ZipCode[0]": {
            "legal_purpose": "Mailing address - ZIP Code",
            "context_description": "ZIP code for your mailing address",
            "field_category": "address_mailing",
            "required": True,
            "user_guidance": "Enter the ZIP code for your mailing address",
            "data_format": "5-digit ZIP code"
        },
        "Pt2Line5_Unit[0]": {
            "legal_purpose": "Mailing address - Unit type",
            "context_description": "Unit type indicator for mailing address (Apt/Ste/Flr)",
            "field_category": "address_mailing",
            "required": False,
            "mutually_exclusive_group": "mailing_unit_type",
            "user_guidance": "Check 'Apt' if your mailing address includes an apartment number"
        },
        "Pt2Line5_Unit[1]": {
            "legal_purpose": "Mailing address - Unit type",
            "context_description": "Unit type indicator for mailing address (Suite)",
            "field_category": "address_mailing",
            "required": False,
            "mutually_exclusive_group": "mailing_unit_type",
            "user_guidance": "Check 'Ste' if your mailing address includes a suite number"
        },
        "Pt2Line5_Unit[2]": {
            "legal_purpose": "Mailing address - Unit type",
            "context_description": "Unit type indicator for mailing address (Floor)",
            "field_category": "address_mailing",
            "required": False,
            "mutually_exclusive_group": "mailing_unit_type",
            "user_guidance": "Check 'Flr' if your mailing address includes a floor number"
        },
        "Pt2Line5_AptSteFlrNumber[0]": {
            "legal_purpose": "Mailing address - Unit number",
            "context_description": "Apartment, suite, or floor number for mailing address",
            "field_category": "address_mailing",
            "required": False,
            "user_guidance": "Enter the apartment, suite, or floor number for your mailing address"
        },
        
        # MAILING vs PHYSICAL ADDRESS CHECK
        "Part2Line5_Checkbox[0]": {
            "legal_purpose": "Address comparison - Yes",
            "context_description": "Is your current mailing address the same as your physical address? - Yes",
            "field_category": "address_comparison",
            "required": True,
            "mutually_exclusive_group": "address_same",
            "user_guidance": "Select Yes if you receive mail at the same address where you live"
        },
        "Part2Line5_Checkbox[1]": {
            "legal_purpose": "Address comparison - No",
            "context_description": "Is your current mailing address the same as your physical address? - No",
            "field_category": "address_comparison",
            "required": True,
            "mutually_exclusive_group": "address_same",
            "user_guidance": "Select No if you receive mail at a different address than where you live"
        },
        
        # PHYSICAL ADDRESS (if different from mailing)
        "Pt2Line7_StreetNumberName[0]": {
            "legal_purpose": "Physical address - Street",
            "context_description": "Street number and name of your physical address in the US",
            "field_category": "address_physical",
            "required": False,
            "conditional_requirement": "Required if mailing address is different from physical address",
            "legal_note": "This is where you actually live, not where you receive mail",
            "user_guidance": "Enter the street number and street name where you physically live"
        },
        "Pt2Line7_CityOrTown[0]": {
            "legal_purpose": "Physical address - City",
            "context_description": "City or town of your physical address in the US",
            "field_category": "address_physical",
            "required": False,
            "conditional_requirement": "Required if mailing address is different from physical address",
            "user_guidance": "Enter the city or town where you physically live"
        },
        "Pt2Line7_State[0]": {
            "legal_purpose": "Physical address - State",
            "context_description": "State of your physical address in the US",
            "field_category": "address_physical",
            "required": False,
            "conditional_requirement": "Required if mailing address is different from physical address",
            "user_guidance": "Enter the state where you physically live (2-letter abbreviation)",
            "data_format": "2-letter state code"
        },
        "Pt2Line7_ZipCode[0]": {
            "legal_purpose": "Physical address - ZIP Code",
            "context_description": "ZIP code of your physical address in the US",
            "field_category": "address_physical",
            "required": False,
            "conditional_requirement": "Required if mailing address is different from physical address",
            "user_guidance": "Enter the ZIP code where you physically live",
            "data_format": "5-digit ZIP code"
        },
        "Pt2Line7_Unit[0]": {
            "legal_purpose": "Physical address - Unit type (Apt)",
            "context_description": "Unit type indicator for physical address - Apartment",
            "field_category": "address_physical",
            "required": False,
            "mutually_exclusive_group": "physical_unit_type",
            "user_guidance": "Check 'Apt' if your physical address includes an apartment number"
        },
        "Pt2Line7_Unit[1]": {
            "legal_purpose": "Physical address - Unit type (Ste)",
            "context_description": "Unit type indicator for physical address - Suite",
            "field_category": "address_physical",
            "required": False,
            "mutually_exclusive_group": "physical_unit_type",
            "user_guidance": "Check 'Ste' if your physical address includes a suite number"
        },
        "Pt2Line7_Unit[2]": {
            "legal_purpose": "Physical address - Unit type (Flr)",
            "context_description": "Unit type indicator for physical address - Floor",
            "field_category": "address_physical",
            "required": False,
            "mutually_exclusive_group": "physical_unit_type",
            "user_guidance": "Check 'Flr' if your physical address includes a floor number"
        },
        "Pt2Line7_AptSteFlrNumber[0]": {
            "legal_purpose": "Physical address - Unit number",
            "context_description": "Apartment, suite, or floor number for physical address",
            "field_category": "address_physical",
            "required": False,
            "user_guidance": "Enter the apartment, suite, or floor number for your physical address"
        },
        
        # IMMIGRATION NUMBERS AND IDS
        "Line7_AlienNumber[0]": {
            "legal_purpose": "USCIS tracking number",
            "context_description": "Your Alien Registration Number (A-Number) assigned by USCIS",
            "field_category": "immigration_status",
            "required": False,
            "legal_note": "9-digit number starting with 'A' - only if you have one",
            "user_guidance": "Enter your A-Number if USCIS has assigned you one (format: A123456789)",
            "data_format": "A + 8 or 9 digits"
        },
        "Line8_ElisAccountNumber[0]": {
            "legal_purpose": "USCIS ELIS account number",
            "context_description": "Your USCIS ELIS (Electronic Immigration System) account number",
            "field_category": "uscis_account",
            "required": False,
            "user_guidance": "Enter your ELIS account number if you have one, otherwise leave blank"
        },
        
        # GENDER SELECTION
        "Line9_Checkbox[0]": {
            "legal_purpose": "Gender identification - Male",
            "context_description": "Gender marker: Male",
            "field_category": "demographics",
            "required": True,
            "mutually_exclusive_group": "gender",
            "user_guidance": "Select if you identify as male"
        },
        "Line9_Checkbox[1]": {
            "legal_purpose": "Gender identification - Female",
            "context_description": "Gender marker: Female",
            "field_category": "demographics",
            "required": True,
            "mutually_exclusive_group": "gender",
            "user_guidance": "Select if you identify as female"
        },
        
        # MARITAL STATUS
        "Line10_Checkbox[0]": {
            "legal_purpose": "Marital status - Single",
            "context_description": "Current marital status: Single/Never married",
            "field_category": "demographics",
            "required": True,
            "mutually_exclusive_group": "marital_status",
            "user_guidance": "Select if you have never been married"
        },
        "Line10_Checkbox[1]": {
            "legal_purpose": "Marital status - Married",
            "context_description": "Current marital status: Married",
            "field_category": "demographics",
            "required": True,
            "mutually_exclusive_group": "marital_status",
            "user_guidance": "Select if you are currently married"
        },
        "Line10_Checkbox[2]": {
            "legal_purpose": "Marital status - Divorced",
            "context_description": "Current marital status: Divorced",
            "field_category": "demographics",
            "required": True,
            "mutually_exclusive_group": "marital_status",
            "user_guidance": "Select if you are divorced"
        },
        "Line10_Checkbox[3]": {
            "legal_purpose": "Marital status - Widowed",
            "context_description": "Current marital status: Widowed",
            "field_category": "demographics",
            "required": True,
            "mutually_exclusive_group": "marital_status",
            "user_guidance": "Select if you are widowed"
        },
        
        # PREVIOUS I-765 FILING
        "Line12a_Checkbox[0]": {
            "legal_purpose": "Previous I-765 filing history - Yes",
            "context_description": "Have you previously filed Form I-765? - Yes",
            "field_category": "filing_history",
            "required": True,
            "mutually_exclusive_group": "previous_i765_filing",
            "legal_note": "Answer honestly - USCIS has records of previous filings",
            "user_guidance": "Select Yes if you have ever submitted Form I-765 before"
        },
        "Line12a_Checkbox[1]": {
            "legal_purpose": "Previous I-765 filing history - No",
            "context_description": "Have you previously filed Form I-765? - No",
            "field_category": "filing_history",
            "required": True,
            "mutually_exclusive_group": "previous_i765_filing",
            "user_guidance": "Select No if this is your first time filing Form I-765"
        },
        
        # SOCIAL SECURITY ADMINISTRATION HISTORY
        "Line13_Checkbox[0]": {
            "legal_purpose": "SSA card issuance history - Yes",
            "context_description": "Has the Social Security Administration ever issued you a Social Security card? - Yes",
            "field_category": "social_security",
            "required": True,
            "mutually_exclusive_group": "ssa_card_history",
            "legal_note": "This includes replacement cards - any SSN card ever issued to you",
            "user_guidance": "Select Yes if you have ever received a Social Security card from the US government"
        },
        "Line13_Checkbox[1]": {
            "legal_purpose": "SSA card issuance history - No",
            "context_description": "Has the Social Security Administration ever issued you a Social Security card? - No",
            "field_category": "social_security",
            "required": True,
            "mutually_exclusive_group": "ssa_card_history",
            "user_guidance": "Select No if you have never received a Social Security card"
        },
        "Line12b_SSN[0]": {
            "legal_purpose": "Social Security Number disclosure",
            "context_description": "Your Social Security Number (if you have one)",
            "field_category": "social_security",
            "required": False,
            "conditional_requirement": "Required if you answered Yes to having received an SSN card",
            "legal_note": "Only provide if you have been issued an SSN",
            "user_guidance": "Enter your 9-digit Social Security Number only if you have one",
            "data_format": "XXX-XX-XXXX"
        },
        
        # SOCIAL SECURITY CARD REQUEST
        "Line14_Checkbox_Yes[0]": {
            "legal_purpose": "SSN card request - Yes",
            "context_description": "Do you want the SSA to issue you a Social Security card? - Yes",
            "field_category": "social_security",
            "required": True,
            "mutually_exclusive_group": "ssn_card_request",
            "legal_note": "Must also consent to disclosure (Item 15) to receive card",
            "user_guidance": "Select Yes if you want to receive a Social Security card"
        },
        "Line14_Checkbox_No[0]": {
            "legal_purpose": "SSN card request - No",
            "context_description": "Do you want the SSA to issue you a Social Security card? - No",
            "field_category": "social_security",
            "required": True,
            "mutually_exclusive_group": "ssn_card_request",
            "user_guidance": "Select No if you do not want to receive a Social Security card"
        },
        
        # PARENT INFORMATION
        "Line15a_FamilyName[0]": {
            "legal_purpose": "Father's family name",
            "context_description": "Your father's family name (last name)",
            "field_category": "parent_info",
            "required": False,
            "conditional_requirement": "Required if you answered Yes to wanting SSN card and consent to disclosure",
            "user_guidance": "Enter your father's last name as it appears on his birth certificate"
        },
        "Line15b_GivenName[0]": {
            "legal_purpose": "Father's given name",
            "context_description": "Your father's given name (first name)",
            "field_category": "parent_info",
            "required": False,
            "conditional_requirement": "Required if you answered Yes to wanting SSN card and consent to disclosure",
            "user_guidance": "Enter your father's first name as it appears on his birth certificate"
        },
        "Line16a_FamilyName[0]": {
            "legal_purpose": "Mother's family name",
            "context_description": "Your mother's birth family name (maiden name)",
            "field_category": "parent_info",
            "required": False,
            "conditional_requirement": "Required if you answered Yes to wanting SSN card and consent to disclosure",
            "legal_note": "Use mother's birth name, not married name",
            "user_guidance": "Enter your mother's maiden name (family name at birth)"
        },
        "Line16b_GivenName[0]": {
            "legal_purpose": "Mother's given name",
            "context_description": "Your mother's given name (first name)",
            "field_category": "parent_info",
            "required": False,
            "conditional_requirement": "Required if you answered Yes to wanting SSN card and consent to disclosure",
            "user_guidance": "Enter your mother's first name as it appears on her birth certificate"
        },
        
        # CITIZENSHIP/NATIONALITY
        "Line17a_CountryOfBirth[0]": {
            "legal_purpose": "Your country of citizenship/nationality #1",
            "context_description": "First country where you are currently a citizen or national",
            "field_category": "citizenship",
            "required": True,
            "legal_note": "List all countries where you hold citizenship",
            "user_guidance": "Enter the first country where you are a citizen or national"
        },
        "Line17b_CountryOfBirth[0]": {
            "legal_purpose": "Your country of citizenship/nationality #2",
            "context_description": "Second country where you are currently a citizen or national",
            "field_category": "citizenship",
            "required": False,
            "user_guidance": "If you have citizenship in multiple countries, enter the second country here"
        },
        
        # BIRTH INFORMATION
        "Line18a_CityTownOfBirth[0]": {
            "legal_purpose": "Place of birth - City/Town/Village",
            "context_description": "City, town, or village where you were born",
            "field_category": "birth_info",
            "required": True,
            "legal_note": "As shown on birth certificate or passport",
            "user_guidance": "Enter the city, town, or village where you were born"
        },
        "Line18b_CityTownOfBirth[0]": {
            "legal_purpose": "Place of birth - State/Province",
            "context_description": "State or province where you were born",
            "field_category": "birth_info",
            "required": False,
            "user_guidance": "Enter the state or province where you were born (if applicable)"
        },
        "Line18c_CountryOfBirth[0]": {
            "legal_purpose": "Place of birth - Country",
            "context_description": "Country where you were born",
            "field_category": "birth_info",
            "required": True,
            "legal_note": "Use current country name, not historical names",
            "user_guidance": "Enter the country where you were born (use current country name)"
        },
        "Line19_DOB[0]": {
            "legal_purpose": "Birth date for identity verification",
            "context_description": "Your date of birth as shown on passport/birth certificate",
            "field_category": "birth_info",
            "required": True,
            "legal_note": "Must match passport exactly",
            "user_guidance": "Enter your birth date exactly as shown on your passport",
            "data_format": "MM/DD/YYYY"
        },
        
        # CONSENT FOR DISCLOSURE
        "Line19_Checkbox[0]": {
            "legal_purpose": "SSA disclosure consent - Yes",
            "context_description": "Consent for disclosure of information to SSA for SSN assignment - Yes",
            "field_category": "social_security",
            "required": True,
            "mutually_exclusive_group": "ssa_disclosure_consent",
            "legal_note": "Required if you want to receive a Social Security card",
            "user_guidance": "Select Yes to authorize USCIS to share your information with Social Security Administration"
        },
        "Line19_Checkbox[1]": {
            "legal_purpose": "SSA disclosure consent - No",
            "context_description": "Consent for disclosure of information to SSA for SSN assignment - No",
            "field_category": "social_security",
            "required": True,
            "mutually_exclusive_group": "ssa_disclosure_consent",
            "user_guidance": "Select No if you do not authorize USCIS to share your information with SSA"
        },
        
        # TRAVEL DOCUMENT INFORMATION
        "Line20a_I94Number[0]": {
            "legal_purpose": "I-94 arrival record number",
            "context_description": "Form I-94 Arrival-Departure Record Number from your last entry to the US",
            "field_category": "travel_documents",
            "required": False,
            "legal_note": "Found on your I-94 arrival record or passport stamp",
            "user_guidance": "Enter your I-94 number from when you last entered the United States"
        },
        "Line20b_Passport[0]": {
            "legal_purpose": "Passport number",
            "context_description": "Passport number of your most recently issued passport",
            "field_category": "travel_documents",
            "required": True,
            "legal_note": "Use current valid passport",
            "user_guidance": "Enter the passport number from your current valid passport"
        },
        "Line20c_TravelDoc[0]": {
            "legal_purpose": "Travel document number",
            "context_description": "Travel document number (if you don't have a passport)",
            "field_category": "travel_documents",
            "required": False,
            "legal_note": "Only if you don't have a passport",
            "user_guidance": "If you don't have a passport, enter your travel document number here"
        },
        "Line20d_CountryOfIssuance[0]": {
            "legal_purpose": "Document issuing country",
            "context_description": "Country that issued your passport or travel document",
            "field_category": "travel_documents",
            "required": True,
            "user_guidance": "Enter the country that issued your passport or travel document"
        },
        "Line20e_ExpDate[0]": {
            "legal_purpose": "Document expiration date",
            "context_description": "Expiration date for your passport or travel document",
            "field_category": "travel_documents",
            "required": True,
            "user_guidance": "Enter the expiration date of your passport or travel document",
            "data_format": "MM/DD/YYYY"
        },
        
        # US ARRIVAL INFORMATION
        "Line21_DateOfLastEntry[0]": {
            "legal_purpose": "Last US entry date",
            "context_description": "Date of your last arrival into the United States",
            "field_category": "us_entry",
            "required": True,
            "legal_note": "Date you most recently entered the US",
            "user_guidance": "Enter the date when you last entered the United States",
            "data_format": "MM/DD/YYYY"
        },
        "place_entry[0]": {
            "legal_purpose": "Place of last US entry",
            "context_description": "Place where you last arrived into the United States",
            "field_category": "us_entry",
            "required": True,
            "user_guidance": "Enter the city and state where you last entered the United States (e.g., New York, NY)"
        },
        "Line23_StatusLastEntry[0]": {
            "legal_purpose": "Immigration status at last entry",
            "context_description": "Your immigration status when you last entered the US",
            "field_category": "us_entry",
            "required": True,
            "legal_note": "Status shown on your I-94 or passport stamp",
            "user_guidance": "Enter your status when you last entered the US (e.g., F-1, B-2, H-1B)"
        },
        "Line24_CurrentStatus[0]": {
            "legal_purpose": "Current immigration status",
            "context_description": "Your current immigration status or category",
            "field_category": "immigration_status",
            "required": True,
            "legal_note": "Your current legal status in the US",
            "user_guidance": "Enter your current immigration status (e.g., F-1 student, H-1B worker, asylum applicant)"
        },
        
        # ELIGIBILITY AND SPECIAL CATEGORIES
        "Line26_SEVISnumber[0]": {
            "legal_purpose": "SEVIS number",
            "context_description": "Student and Exchange Visitor Information System (SEVIS) number",
            "field_category": "student_info",
            "required": False,
            "conditional_requirement": "Required for F and M students",
            "legal_note": "Found on your Form I-20 or DS-2019",
            "user_guidance": "If you are an F or M student, enter your SEVIS number from your I-20"
        },
        "Line27a_Degree[0]": {
            "legal_purpose": "Academic degree",
            "context_description": "Your degree for STEM OPT eligibility",
            "field_category": "education",
            "required": False,
            "conditional_requirement": "Required for STEM OPT applications",
            "user_guidance": "If applying for STEM OPT, enter your qualifying degree"
        },
        "Line27b_Everify[0]": {
            "legal_purpose": "Employer name in E-Verify",
            "context_description": "Employer's name as listed in E-Verify system",
            "field_category": "employment",
            "required": False,
            "conditional_requirement": "Required for STEM OPT applications",
            "user_guidance": "If applying for STEM OPT, enter your employer's name as shown in E-Verify"
        },
        "Line27c_EverifyIDNumber[0]": {
            "legal_purpose": "E-Verify company ID",
            "context_description": "Employer's E-Verify Company Identification Number",
            "field_category": "employment",
            "required": False,
            "conditional_requirement": "Required for STEM OPT applications",
            "user_guidance": "If applying for STEM OPT, enter your employer's E-Verify ID number"
        },
        "Line28_ReceiptNumber[0]": {
            "legal_purpose": "USCIS receipt number",
            "context_description": "Receipt number for pending USCIS application",
            "field_category": "uscis_cases",
            "required": False,
            "conditional_requirement": "Required for certain eligibility categories",
            "user_guidance": "Enter the receipt number for your pending USCIS case (if applicable)"
        },
        "Line30a_ReceiptNumber[0]": {
            "legal_purpose": "I-797 receipt number",
            "context_description": "Receipt number from Form I-797 Notice",
            "field_category": "uscis_cases",
            "required": False,
            "conditional_requirement": "Required for certain eligibility categories",
            "user_guidance": "Enter the receipt number from your I-797 approval notice (if applicable)"
        },
        
        # YES/NO QUESTIONS FOR ELIGIBILITY CATEGORIES
        "PtLine29_YesNo[0]": {
            "legal_purpose": "Eligibility category question - Yes",
            "context_description": "Response to eligibility category specific question - Yes",
            "field_category": "eligibility_questions",
            "required": False,
            "conditional_requirement": "Required for certain eligibility categories",
            "mutually_exclusive_group": "eligibility_yes_no_29",
            "user_guidance": "Answer the eligibility-specific question based on your circumstances"
        },
        "PtLine29_YesNo[1]": {
            "legal_purpose": "Eligibility category question - No",
            "context_description": "Response to eligibility category specific question - No",
            "field_category": "eligibility_questions",
            "required": False,
            "conditional_requirement": "Required for certain eligibility categories",
            "mutually_exclusive_group": "eligibility_yes_no_29",
            "user_guidance": "Answer the eligibility-specific question based on your circumstances"
        },
        "PtLine30b_YesNo[0]": {
            "legal_purpose": "Criminal history question - Yes",
            "context_description": "Have you ever been arrested for and/or convicted of any crime? - Yes",
            "field_category": "criminal_history",
            "required": False,
            "conditional_requirement": "Required for certain eligibility categories",
            "mutually_exclusive_group": "criminal_history_30b",
            "legal_note": "Answer honestly - background checks will be conducted",
            "user_guidance": "Select Yes if you have ever been arrested or convicted of any crime"
        },
        "PtLine30b_YesNo[1]": {
            "legal_purpose": "Criminal history question - No",
            "context_description": "Have you ever been arrested for and/or convicted of any crime? - No",
            "field_category": "criminal_history",
            "required": False,
            "conditional_requirement": "Required for certain eligibility categories",
            "mutually_exclusive_group": "criminal_history_30b",
            "user_guidance": "Select No if you have never been arrested or convicted of any crime"
        },
        
        # FORM SECTIONS FOR ADDITIONAL INFO
        "section_1[0]": {
            "legal_purpose": "Form section identifier",
            "context_description": "Section identifier for additional information",
            "field_category": "form_structure",
            "required": False,
            "skip_in_ui": True,
            "user_guidance": "This field is for form organization - not fillable by applicant"
        },
        "section_2[0]": {
            "legal_purpose": "Form section identifier",
            "context_description": "Section identifier for additional information",
            "field_category": "form_structure",
            "required": False,
            "skip_in_ui": True,
            "user_guidance": "This field is for form organization - not fillable by applicant"
        },
        "section_3[0]": {
            "legal_purpose": "Form section identifier",
            "context_description": "Section identifier for additional information",
            "field_category": "form_structure",
            "required": False,
            "skip_in_ui": True,
            "user_guidance": "This field is for form organization - not fillable by applicant"
        },
        
        # PART 3: APPLICANT STATEMENT AND LANGUAGE
        "Pt3Line1Checkbox[0]": {
            "legal_purpose": "Form completion method - Self",
            "context_description": "I can read and understand English and completed this form myself",
            "field_category": "form_completion",
            "required": True,
            "mutually_exclusive_group": "completion_method",
            "legal_note": "Select this if you read and understood the form yourself",
            "user_guidance": "Check this if you can read English and filled out this form by yourself"
        },
        "Pt3Line1Checkbox[1]": {
            "legal_purpose": "Form completion method - Interpreter",
            "context_description": "An interpreter read and explained this form to me in my language",
            "field_category": "form_completion",
            "required": True,
            "mutually_exclusive_group": "completion_method",
            "legal_note": "Must provide interpreter information in Part 4 if selected",
            "user_guidance": "Check this if an interpreter helped you understand and complete this form"
        },
        "Pt3Line1b_Language[0]": {
            "legal_purpose": "Interpreter language",
            "context_description": "Language in which interpreter assisted you",
            "field_category": "interpreter_info",
            "required": False,
            "conditional_requirement": "Required if you used an interpreter",
            "user_guidance": "Enter the language your interpreter used to help you"
        },
        "Part3_Checkbox[0]": {
            "legal_purpose": "Preparer assistance acknowledgment",
            "context_description": "A preparer helped me complete this application",
            "field_category": "form_completion",
            "required": False,
            "legal_note": "Check if someone helped prepare this form",
            "user_guidance": "Check this box if someone else helped you prepare this application"
        },
        "Pt3Line2_RepresentativeName[0]": {
            "legal_purpose": "Preparer name",
            "context_description": "Name of person who prepared this application",
            "field_category": "preparer_info",
            "required": False,
            "conditional_requirement": "Required if preparer assisted",
            "user_guidance": "Enter the name of the person who helped prepare this form"
        },
        
        # CONTACT INFORMATION
        "Pt3Line3_DaytimePhoneNumber1[0]": {
            "legal_purpose": "Applicant daytime phone",
            "context_description": "Your daytime telephone number",
            "field_category": "contact_info",
            "required": True,
            "user_guidance": "Enter your daytime phone number where USCIS can reach you",
            "data_format": "(XXX) XXX-XXXX"
        },
        "Pt3Line4_MobileNumber1[0]": {
            "legal_purpose": "Applicant mobile phone",
            "context_description": "Your mobile telephone number",
            "field_category": "contact_info",
            "required": False,
            "user_guidance": "Enter your mobile phone number (if different from daytime number)"
        },
        "Pt3Line5_Email[0]": {
            "legal_purpose": "Applicant email address",
            "context_description": "Your email address for USCIS communications",
            "field_category": "contact_info",
            "required": False,
            "legal_note": "USCIS may send important notices to this email",
            "user_guidance": "Enter your email address for important updates from USCIS"
        },
        
        # SPECIAL CIRCUMSTANCES
        "Pt4Line6_Checkbox[0]": {
            "legal_purpose": "ABC settlement eligibility",
            "context_description": "Salvadoran or Guatemalan national eligible for ABC settlement benefits",
            "field_category": "special_programs",
            "required": False,
            "legal_note": "Only for eligible Salvadoran or Guatemalan nationals",
            "user_guidance": "Check this only if you are a Salvadoran or Guatemalan national eligible for ABC settlement"
        },
        
        # PART 4: INTERPRETER INFORMATION
        "Pt4Line1a_InterpreterFamilyName[0]": {
            "legal_purpose": "Interpreter family name",
            "context_description": "Family name (last name) of your interpreter",
            "field_category": "interpreter_info",
            "required": False,
            "conditional_requirement": "Required if you used an interpreter",
            "user_guidance": "Enter your interpreter's last name"
        },
        "Pt4Line1b_InterpreterGivenName[0]": {
            "legal_purpose": "Interpreter given name",
            "context_description": "Given name (first name) of your interpreter",
            "field_category": "interpreter_info",
            "required": False,
            "conditional_requirement": "Required if you used an interpreter",
            "user_guidance": "Enter your interpreter's first name"
        },
        "Pt4Line2_InterpreterBusinessorOrg[0]": {
            "legal_purpose": "Interpreter business/organization",
            "context_description": "Business or organization name of your interpreter",
            "field_category": "interpreter_info",
            "required": False,
            "user_guidance": "Enter your interpreter's business or organization name (if any)"
        },
        "Pt4Line4_InterpreterDaytimeTelephone[0]": {
            "legal_purpose": "Interpreter phone number",
            "context_description": "Daytime telephone number of your interpreter",
            "field_category": "interpreter_info",
            "required": False,
            "conditional_requirement": "Required if you used an interpreter",
            "user_guidance": "Enter your interpreter's daytime phone number"
        },
        "Pt4Line5_MobileNumber[0]": {
            "legal_purpose": "Interpreter mobile number",
            "context_description": "Mobile telephone number of your interpreter",
            "field_category": "interpreter_info",
            "required": False,
            "user_guidance": "Enter your interpreter's mobile phone number (if any)"
        },
        "Pt4Line6_Email[0]": {
            "legal_purpose": "Interpreter email",
            "context_description": "Email address of your interpreter",
            "field_category": "interpreter_info",
            "required": False,
            "user_guidance": "Enter your interpreter's email address (if any)"
        },
        "Part4_NameofLanguage[0]": {
            "legal_purpose": "Interpreter language certification",
            "context_description": "Language the interpreter used to assist you",
            "field_category": "interpreter_info",
            "required": False,
            "conditional_requirement": "Required if you used an interpreter",
            "user_guidance": "Enter the language your interpreter used to help you"
        },
        
        # PART 5: PREPARER INFORMATION
        "Pt5Line1a_PreparerFamilyName[0]": {
            "legal_purpose": "Preparer family name",
            "context_description": "Family name (last name) of person who prepared this application",
            "field_category": "preparer_info",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "user_guidance": "Enter the last name of the person who prepared this form"
        },
        "Pt5Line1b_PreparerGivenName[0]": {
            "legal_purpose": "Preparer given name",
            "context_description": "Given name (first name) of person who prepared this application",
            "field_category": "preparer_info",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "user_guidance": "Enter the first name of the person who prepared this form"
        },
        "Pt5Line2_BusinessName[0]": {
            "legal_purpose": "Preparer business name",
            "context_description": "Business or organization name of the preparer",
            "field_category": "preparer_info",
            "required": False,
            "user_guidance": "Enter the business name of the person who prepared this form (if applicable)"
        },
        
        # PREPARER ADDRESS
        "Pt5Line3a_StreetNumberName[0]": {
            "legal_purpose": "Preparer street address",
            "context_description": "Street number and name of preparer's mailing address",
            "field_category": "preparer_address",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "user_guidance": "Enter the street address of the person who prepared this form"
        },
        "Pt5Line3b_Unit[0]": {
            "legal_purpose": "Preparer address unit type (Apt)",
            "context_description": "Apartment unit indicator for preparer's address",
            "field_category": "preparer_address",
            "required": False,
            "mutually_exclusive_group": "preparer_unit_type",
            "user_guidance": "Check 'Apt' if preparer's address includes an apartment number"
        },
        "Pt5Line3b_Unit[1]": {
            "legal_purpose": "Preparer address unit type (Ste)",
            "context_description": "Suite unit indicator for preparer's address",
            "field_category": "preparer_address",
            "required": False,
            "mutually_exclusive_group": "preparer_unit_type",
            "user_guidance": "Check 'Ste' if preparer's address includes a suite number"
        },
        "Pt5Line3b_Unit[2]": {
            "legal_purpose": "Preparer address unit type (Flr)",
            "context_description": "Floor unit indicator for preparer's address",
            "field_category": "preparer_address",
            "required": False,
            "mutually_exclusive_group": "preparer_unit_type",
            "user_guidance": "Check 'Flr' if preparer's address includes a floor number"
        },
        "Pt5Line3b_AptSteFlrNumber[0]": {
            "legal_purpose": "Preparer unit number",
            "context_description": "Apartment, suite, or floor number for preparer's address",
            "field_category": "preparer_address",
            "required": False,
            "user_guidance": "Enter the apartment, suite, or floor number for preparer's address"
        },
        "Pt5Line3c_CityOrTown[0]": {
            "legal_purpose": "Preparer city",
            "context_description": "City or town of preparer's mailing address",
            "field_category": "preparer_address",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "user_guidance": "Enter the city of the person who prepared this form"
        },
        "Pt5Line3d_State[0]": {
            "legal_purpose": "Preparer state",
            "context_description": "State of preparer's mailing address",
            "field_category": "preparer_address",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "user_guidance": "Enter the state of the person who prepared this form",
            "data_format": "2-letter state code"
        },
        "Pt5Line3e_ZipCode[0]": {
            "legal_purpose": "Preparer ZIP code",
            "context_description": "ZIP code of preparer's mailing address",
            "field_category": "preparer_address",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "user_guidance": "Enter the ZIP code of the person who prepared this form",
            "data_format": "5-digit ZIP code"
        },
        "Pt5Line3f_Province[0]": {
            "legal_purpose": "Preparer province",
            "context_description": "Province of preparer's address (for international addresses)",
            "field_category": "preparer_address",
            "required": False,
            "user_guidance": "Enter the province if preparer lives outside the US"
        },
        "Pt5Line3g_PostalCode[0]": {
            "legal_purpose": "Preparer postal code",
            "context_description": "Postal code of preparer's address (for international addresses)",
            "field_category": "preparer_address",
            "required": False,
            "user_guidance": "Enter the postal code if preparer lives outside the US"
        },
        "Pt5Line3h_Country[0]": {
            "legal_purpose": "Preparer country",
            "context_description": "Country of preparer's mailing address",
            "field_category": "preparer_address",
            "required": False,
            "user_guidance": "Enter the country where the preparer lives"
        },
        
        # PREPARER CONTACT INFO
        "Pt5Line4_DaytimePhoneNumber1[0]": {
            "legal_purpose": "Preparer phone number",
            "context_description": "Daytime telephone number of the preparer",
            "field_category": "preparer_contact",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "user_guidance": "Enter the phone number of the person who prepared this form"
        },
        "Pt5Line5_PreparerFaxNumber[0]": {
            "legal_purpose": "Preparer fax number",
            "context_description": "Fax number of the preparer",
            "field_category": "preparer_contact",
            "required": False,
            "user_guidance": "Enter the fax number of the person who prepared this form (if any)"
        },
        "Pt5Line6_Email[0]": {
            "legal_purpose": "Preparer email",
            "context_description": "Email address of the preparer",
            "field_category": "preparer_contact",
            "required": False,
            "user_guidance": "Enter the email address of the person who prepared this form"
        },
        
        # PREPARER STATEMENT
        "Part5Line7_Checkbox[0]": {
            "legal_purpose": "Preparer type - Not attorney",
            "context_description": "Preparer is not an attorney but prepared this application",
            "field_category": "preparer_status",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "mutually_exclusive_group": "preparer_type",
            "user_guidance": "Check if the preparer is not an attorney or accredited representative"
        },
        "Part5Line7_Checkbox[1]": {
            "legal_purpose": "Preparer type - Attorney",
            "context_description": "Preparer is an attorney or accredited representative",
            "field_category": "preparer_status",
            "required": False,
            "conditional_requirement": "Required if someone else prepared this form",
            "mutually_exclusive_group": "preparer_type",
            "user_guidance": "Check if the preparer is an attorney or accredited representative"
        },
        "Part5Line7b_Checkbox[0]": {
            "legal_purpose": "Attorney representation scope - Extends",
            "context_description": "Attorney representation extends beyond preparation of this application",
            "field_category": "attorney_scope",
            "required": False,
            "conditional_requirement": "Required if preparer is an attorney",
            "mutually_exclusive_group": "attorney_representation_scope",
            "user_guidance": "Check if attorney will represent you beyond just preparing this form"
        },
        "Part5Line7b_Checkbox[1]": {
            "legal_purpose": "Attorney representation scope - Limited",
            "context_description": "Attorney representation does not extend beyond preparation",
            "field_category": "attorney_scope",
            "required": False,
            "conditional_requirement": "Required if preparer is an attorney",
            "mutually_exclusive_group": "attorney_representation_scope",
            "user_guidance": "Check if attorney is only helping prepare this form and not providing ongoing representation"
        },
        
        # PART 6: ADDITIONAL INFORMATION FIELDS
        "Pt6Line3a_StreetNumberName[0]": {
            "legal_purpose": "Additional preparer address (international)",
            "context_description": "International street address for preparer",
            "field_category": "preparer_address_intl",
            "required": False,
            "user_guidance": "Enter international street address if preparer lives outside the US"
        },
        "Pt6Line3b_Unit[0]": {
            "legal_purpose": "International preparer address unit (Apt)",
            "context_description": "Apartment unit for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "mutually_exclusive_group": "preparer_intl_unit_type",
            "user_guidance": "Check 'Apt' for international preparer apartment"
        },
        "Pt6Line3b_Unit[1]": {
            "legal_purpose": "International preparer address unit (Ste)",
            "context_description": "Suite unit for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "mutually_exclusive_group": "preparer_intl_unit_type",
            "user_guidance": "Check 'Ste' for international preparer suite"
        },
        "Pt6Line3b_Unit[2]": {
            "legal_purpose": "International preparer address unit (Flr)",
            "context_description": "Floor unit for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "mutually_exclusive_group": "preparer_intl_unit_type",
            "user_guidance": "Check 'Flr' for international preparer floor"
        },
        "Pt6Line3b_AptSteFlrNumber[0]": {
            "legal_purpose": "International preparer unit number",
            "context_description": "Unit number for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "user_guidance": "Enter apartment, suite, or floor number for international preparer"
        },
        "Pt6Line3c_CityOrTown[0]": {
            "legal_purpose": "International preparer city",
            "context_description": "City for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "user_guidance": "Enter city for international preparer address"
        },
        "Pt6Line3d_State[0]": {
            "legal_purpose": "International preparer state/region",
            "context_description": "State or region for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "user_guidance": "Enter state or region for international preparer"
        },
        "Pt6Line3e_ZipCode[0]": {
            "legal_purpose": "International preparer ZIP/postal code",
            "context_description": "ZIP or postal code for international preparer",
            "field_category": "preparer_address_intl",
            "required": False,
            "user_guidance": "Enter ZIP or postal code for international preparer"
        },
        "Pt6Line3f_Province[0]": {
            "legal_purpose": "International preparer province",
            "context_description": "Province for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "user_guidance": "Enter province for international preparer address"
        },
        "Pt6Line3g_PostalCode[0]": {
            "legal_purpose": "International preparer postal code",
            "context_description": "Postal code for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "user_guidance": "Enter postal code for international preparer address"
        },
        "Pt6Line3h_Country[0]": {
            "legal_purpose": "International preparer country",
            "context_description": "Country for international preparer address",
            "field_category": "preparer_address_intl",
            "required": False,
            "user_guidance": "Enter country for international preparer address"
        },
        
        # PART 6: ADDITIONAL INFORMATION CONTINUATION FIELDS
        "Line1a_FamilyName[0]": {  # Note: This appears on page 7 as well
            "legal_purpose": "Additional information - Family name reference",
            "context_description": "Family name reference for additional information section",
            "field_category": "additional_info",
            "required": False,
            "user_guidance": "Enter your family name for reference in additional information section"
        },
        "Line1b_GivenName[0]": {  # Note: This appears on page 7 as well
            "legal_purpose": "Additional information - Given name reference",
            "context_description": "Given name reference for additional information section",
            "field_category": "additional_info",
            "required": False,
            "user_guidance": "Enter your given name for reference in additional information section"
        },
        "Line1c_MiddleName[0]": {  # Note: This appears on page 7 as well
            "legal_purpose": "Additional information - Middle name reference",
            "context_description": "Middle name reference for additional information section",
            "field_category": "additional_info",
            "required": False,
            "user_guidance": "Enter your middle name for reference in additional information section"
        },
        
        # ADDITIONAL INFORMATION FORM REFERENCES
        "Pt6Line3a_PageNumber[0]": {
            "legal_purpose": "Additional info page reference",
            "context_description": "Page number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter the page number you are referring to for additional information"
        },
        "Pt6Line3b_PartNumber[0]": {
            "legal_purpose": "Additional info part reference",
            "context_description": "Part number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter the part number you are referring to for additional information"
        },
        "Pt6Line3c_ItemNumber[0]": {
            "legal_purpose": "Additional info item reference",
            "context_description": "Item number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter the item number you are referring to for additional information"
        },
        "Pt6Line4a_PageNumber[0]": {
            "legal_purpose": "Additional info page reference #2",
            "context_description": "Second page number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter another page number for additional information (if needed)"
        },
        "Pt6Line4b_PartNumber[0]": {
            "legal_purpose": "Additional info part reference #2",
            "context_description": "Second part number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter another part number for additional information (if needed)"
        },
        "Pt6Line4c_ItemNumber[0]": {
            "legal_purpose": "Additional info item reference #2",
            "context_description": "Second item number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter another item number for additional information (if needed)"
        },
        "Pt6Line4d_AdditionalInfo[0]": {
            "legal_purpose": "Additional information text area",
            "context_description": "Text area for providing additional information",
            "field_category": "additional_info",
            "required": False,
            "user_guidance": "Use this space to provide any additional information needed to complete your application"
        },
        "Pt6Line4d_AdditionalInfo[1]": {
            "legal_purpose": "Additional information text area (continued)",
            "context_description": "Continuation text area for additional information",
            "field_category": "additional_info",
            "required": False,
            "user_guidance": "Continue additional information here if needed"
        },
        "Pt6Line5a_PageNumber[0]": {
            "legal_purpose": "Additional info page reference #3",
            "context_description": "Third page number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a third page number for additional information (if needed)"
        },
        "Pt6Line5b_PartNumber[0]": {
            "legal_purpose": "Additional info part reference #3",
            "context_description": "Third part number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a third part number for additional information (if needed)"
        },
        "Pt6Line5c_ItemNumber[0]": {
            "legal_purpose": "Additional info item reference #3",
            "context_description": "Third item number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a third item number for additional information (if needed)"
        },
        "Pt6Line5d_AdditionalInfo[0]": {
            "legal_purpose": "Additional information text area #3",
            "context_description": "Third text area for additional information",
            "field_category": "additional_info",
            "required": False,
            "user_guidance": "Use this space for more additional information if needed"
        },
        "Pt6Line6a_PageNumber[0]": {
            "legal_purpose": "Additional info page reference #4",
            "context_description": "Fourth page number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a fourth page number for additional information (if needed)"
        },
        "Pt6Line6b_PartNumber[0]": {
            "legal_purpose": "Additional info part reference #4",
            "context_description": "Fourth part number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a fourth part number for additional information (if needed)"
        },
        "Pt6Line6c_ItemNumber[0]": {
            "legal_purpose": "Additional info item reference #4",
            "context_description": "Fourth item number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a fourth item number for additional information (if needed)"
        },
        "Pt6Line6d_AdditionalInfo[0]": {
            "legal_purpose": "Additional information text area #4",
            "context_description": "Fourth text area for additional information",
            "field_category": "additional_info",
            "required": False,
            "user_guidance": "Use this space for even more additional information if needed"
        },
        "Pt6Line7a_PageNumber[0]": {
            "legal_purpose": "Additional info page reference #5",
            "context_description": "Fifth page number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a fifth page number for additional information (if needed)"
        },
        "Pt6Line7b_PartNumber[0]": {
            "legal_purpose": "Additional info part reference #5",
            "context_description": "Fifth part number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a fifth part number for additional information (if needed)"
        },
        "Pt6Line7c_ItemNumber[0]": {
            "legal_purpose": "Additional info item reference #5",
            "context_description": "Fifth item number reference for additional information",
            "field_category": "form_references",
            "required": False,
            "user_guidance": "Enter a fifth item number for additional information (if needed)"
        },
        "Pt6Line7d_AdditionalInfo[0]": {
            "legal_purpose": "Additional information text area #5",
            "context_description": "Fifth text area for additional information",
            "field_category": "additional_info",
            "required": False,
            "user_guidance": "Use this final space for any remaining additional information"
        }
    }
    return FIELD_CONTEXTS

from typing import Dict, List, Optional

def generate_multilingual_questions(fields: List[Dict], target_language: str = "en", 
                                   source_language: str = "en") -> List[Dict]:
    """
    Generate user-friendly questions with multi-language support and cultural context.
    
    Args:
        fields: List of enriched field dictionaries
        target_language: Target language code (e.g., "es", "zh", "ar")
        source_language: Source language code (default "en")
    
    Returns:
        List of fields with generated questions and cultural guidance
    """
    
    # Process fields in batches for Gemini
    question_fields = []
    batch_size = 5
    
    for i in range(0, len(fields), batch_size):
        batch = fields[i:i+batch_size]
        batch_questions = generate_questions_batch(batch, target_language, source_language)
        question_fields.extend(batch_questions)
    
    return question_fields

def generate_questions_batch(fields_batch: List[Dict], target_language: str, 
                           source_language: str) -> List[Dict]:
    """Generate questions for a batch of fields using Gemini."""
    
    # Language names for Gemini
    language_names = {
        "en": "English",
        "es": "Spanish", 
        "zh": "Chinese (Simplified)",
        "ar": "Arabic",
        "fr": "French",
        "pt": "Portuguese",
        "ko": "Korean",
        "vi": "Vietnamese",
        "ru": "Russian",
        "hi": "Hindi"
    }
    
    target_lang_name = language_names.get(target_language, target_language)
    
    # Create field summaries for Gemini
    field_summaries = []
    for field in fields_batch:
        # Skip non-input fields
        if "barcode" in field["field_id"].lower() or "pdf417" in field["field_id"].lower():
            continue
            
        field_summaries.append({
            "field_id": field["field_id"],
            "legal_purpose": field.get("legal_purpose", ""),
            "context_description": field.get("context_description", ""),
            "field_category": field.get("field_category", ""),
            "required": field.get("required", False),
            "user_guidance": field.get("user_guidance", ""),
            "legal_note": field.get("legal_note", ""),
            "data_format": field.get("data_format", "")
        })
    
    if not field_summaries:
        return fields_batch
    
    prompt = f"""
You are creating user-friendly questions for a US immigration form (I-765 Employment Authorization) for foreign immigrants.

Target Language: {target_lang_name}
Context: These are legal immigration form fields that must be completed accurately.

Field Information:
{json.dumps(field_summaries, indent=2)}

For each field, create:
1. A clear, simple question in {target_lang_name}
2. Helpful explanation of what information is needed
3. Cultural context notes for non-US natives (if applicable)
4. Translation confidence notes (potential misunderstandings)
5. Examples when helpful

Guidelines:
- Use simple, clear language appropriate for foreign immigrants
- Explain US-specific concepts (SSN, ZIP codes, etc.)
- Be respectful and encouraging, not intimidating
- Include format requirements clearly
- For required fields, emphasize importance
- For {target_lang_name}: Consider cultural context and potential translation issues

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "field_id": "exact_field_id",
      "question": "Clear question in {target_lang_name}",
      "explanation": "Helpful explanation in {target_lang_name}",
      "cultural_notes": "US context explanation in {target_lang_name}",
      "translation_notes": "Potential misunderstandings or clarifications in {target_lang_name}",
      "examples": ["example1", "example2"],
      "format_hint": "Expected format if applicable",
      "required": true/false
    }}
  ]
}}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        
        result = json.loads(response.text)
        questions_data = result.get("questions", [])
        
        # Merge questions back into fields
        for field in fields_batch:
            field_question = next(
                (q for q in questions_data if q["field_id"] == field["field_id"]), 
                None
            )
            
            if field_question:
                field.update({
                    "user_question": field_question["question"],
                    "explanation": field_question["explanation"], 
                    "cultural_notes": field_question["cultural_notes"],
                    "translation_notes": field_question["translation_notes"],
                    "examples": field_question["examples"],
                    "format_hint": field_question.get("format_hint", ""),
                    "target_language": target_language
                })
        
        return fields_batch
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        # Fallback to basic questions
        for field in fields_batch:
            field.update({
                "user_question": field.get("user_guidance", f"Please provide {field['field_id']}"),
                "explanation": field.get("context_description", ""),
                "cultural_notes": "",
                "translation_notes": "",
                "examples": [],
                "format_hint": field.get("data_format", ""),
                "target_language": target_language
            })
        
        return fields_batch
    
def get_supported_languages() -> List[Dict[str, str]]:
    """Get list of supported languages for the application."""
    return [
        {"code": "en", "name": "English", "native_name": "English"},
        {"code": "es", "name": "Spanish", "native_name": "Español"},
        {"code": "zh", "name": "Chinese (Simplified)", "native_name": "中文"},
        {"code": "ar", "name": "Arabic", "native_name": "العربية"},
        {"code": "fr", "name": "French", "native_name": "Français"},
        {"code": "pt", "name": "Portuguese", "native_name": "Português"},
        {"code": "ko", "name": "Korean", "native_name": "한국어"},
        {"code": "vi", "name": "Vietnamese", "native_name": "Tiếng Việt"},
        {"code": "ru", "name": "Russian", "native_name": "Русский"},
        {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"}
    ]