from pypdf import PdfReader, PdfWriter
import json
from pypdf.generic import NameObject
import os

file_name = "btest.pdf"

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
            #"value": str(field.get("/V", "")),
            #"type": str(field_type),
            "label": str(field.get("/TU", "")),
        })



writer = PdfWriter()

# Copy all pages to writer
for page in reader.pages:
    writer.add_page(page)

# Copy the form structure if it exists
if "/AcroForm" in reader.trailer["/Root"]:
    writer._root_object.update({
        NameObject("/AcroForm"): reader.trailer["/Root"]["/AcroForm"]
    })
    print("Copied AcroForm structure")
else:
    print("Warning: No AcroForm found in PDF")

# Create field values for testing
field_values = {}
for f in fields:
    test_value = f"Test value for {f['label'] or f['name']}"
    field_values[f["name"]] = test_value
    print(f"Setting {f['name']} = {test_value}")

print(f"Field values to update: {field_values}")

# Try to update form fields on all pages
if field_values:
    for page_index, page in enumerate(writer.pages):
        try:
            writer.update_page_form_field_values(page, field_values)
            print(f"Successfully updated fields on page {page_index + 1}")
        except Exception as e:
            print(f"Error updating page {page_index + 1}: {e}")
            continue
else:
    print("No field values to update")

# Write new PDF
output_file = "filled_output.pdf"
with open(output_file, "wb") as out:
    writer.write(out)

print(f"Successfully created {output_file}")
print(f"Original file size: {os.path.getsize(file_name)} bytes")
print(f"Output file size: {os.path.getsize(output_file)} bytes")

print("\nExtracted fields:")
for field in fields:
    print(f"  {field}")

print(fields)