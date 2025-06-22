from pypdf import PdfReader
import json

file_name = "forms/defualt/PERM.pdf"

reader = PdfReader(file_name)


raw_fields = reader.get_fields()
full_text = "\n".join(
    page.extract_text() or ""  # fallback to empty string if extract_text() fails
    for page in reader.pages
)
fields = []
for name, field in raw_fields.items():
    field_type = field.get("/FT")
    if field_type == "/Tx":  # Only include text fields
        fields.append({
            "name": name,
            "value": str(field.get("/V", "")),
            "type": str(field_type),
            "label": str(field.get("/TU", "")),
        })


input(fields)