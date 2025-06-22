from fpdf import FPDF
import os

STATIC_ROOT = "static/forms"

async def generate_filled_pdf(session_id: str, answers: dict[str,str]) -> str:
    # 1) Load the original form PDF for this session
    # 2) Use FPDF or pypdf to write answers into AcroForm fields
    # 3) Save to /tmp/{session_id}.pdf or upload to S3
    # 4) Return a URL or file path for download
    #
    out_path = f"/tmp/{session_id}-filled.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    y = 50
    for fid, ans in answers.items():
        pdf.text(10, y, f"{fid}: {ans}")
        y += 10
    pdf.output(out_path)
    return f"file://{os.path.abspath(out_path)}"
