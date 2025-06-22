import requests, os
from bs4 import BeautifulSoup

BASE = "https://www.uscis.gov/forms/all-forms"
resp = requests.get(BASE)
soup = BeautifulSoup(resp.text, "html.parser")

# map form IDs to their download links
forms = {
    "I-765": {
        "form": "https://www.uscis.gov/sites/default/files/document/forms/i-765.pdf",
        "inst": "https://www.uscis.gov/sites/default/files/document/forms/i-765instr.pdf"
    },
    "I-130": {
        "form": "https://www.uscis.gov/sites/default/files/document/forms/i-130.pdf",
        "inst": "https://www.uscis.gov/sites/default/files/document/forms/i-130instr.pdf"
    },
    "N-400": {
        "form": "https://www.uscis.gov/sites/default/files/document/forms/n-400.pdf",
        "inst": "https://www.uscis.gov/sites/default/files/document/forms/n-400instr.pdf"
    },
    "I-90": {
        "form": "https://www.uscis.gov/sites/default/files/document/forms/i-90.pdf",
        "inst": "https://www.uscis.gov/sites/default/files/document/forms/i-90instr.pdf"
    },
    "I-485": {
        "form": "https://www.uscis.gov/sites/default/files/document/forms/i-485.pdf",
        "inst": "https://www.uscis.gov/sites/default/files/document/forms/i-485instr.pdf"
    }
}

for fid, links in forms.items():
    os.makedirs(f"static/forms/{fid}", exist_ok=True)
    for kind, url in links.items():
        r = requests.get(url)
        with open(f"static/forms/{fid}/{kind}.pdf", "wb") as f:
            f.write(r.content)
