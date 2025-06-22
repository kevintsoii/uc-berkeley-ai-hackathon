from models.schema import FormSchema
from google.cloud import aiplatform

async def analyze_form(form_id: str, language: str) -> FormSchema:
    # 1) Load PDFs from `static/forms/{form_id}/form.pdf` + `inst.pdf`
    # 2) Build prompt for gemini-2.5-flash-preview
    # 3) Call aiplatform.TextGenerationModel then parse JSON
    #
    # TODO: replace with real download & API logic
    dummy_fields = [{
        "field_id":    "f1_01",
        "label":       "Example Field",
        "type":        "text",
        "page":        1,
        "dependencies": [],
        "gemini_note": "This is a dummy explanation.",
        "examples":    ["Example answer"]
    }]
    return FormSchema(form_id=form_id, fields=dummy_fields)
