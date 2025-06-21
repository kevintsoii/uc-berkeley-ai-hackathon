from fpdf import FPDF

async def generate_filled_pdf(session_id: str) -> str:
    # 1. load schema + user answers
    # 2. open original PDF template
    # 3. write answers into form fields
    # 4. save to disk or S3
    # 5. return public URL
    ...
