# google-cloud-ai client setup
from google.cloud import aiplatform
from models.schema import FormSchema

async def analyze_form(form_id: str) -> FormSchema:
    # 1. download form + instruction PDFs
    # 2. send prompt to gemini-2.5-flash-preview-04-17
    # 3. parse response JSON → FormSchema
    ...
