import json, pathlib
from pypdf import PdfReader

# ─── PDF Parse ────────────────────────────────────────────────────────────────
def extract_fields_with_coords(pdf_path):
    """
    This is will extra all fillable entries in the PDF. 
    """
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

def group_widgets(widgets: list[dict]) -> list[dict]:
    groups = {}
    for w in widgets:
        base = w["field_id"].split("[")[0]
        groups.setdefault(base, []).append(w)

    out = []
    for base_id, sub in groups.items():
        out.append(sub[0] if len(sub) == 1 else {
            "field_id": base_id,
            "widgets":  sub
        })
    return out
