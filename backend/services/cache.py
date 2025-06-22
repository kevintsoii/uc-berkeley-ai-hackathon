import json, pathlib
from typing import Dict
from pathlib import Path

def _path(form_id: str, lang: str) -> Path:
    return Path(f"static/forms/{form_id}/cache_{lang}.json")

def load_cached(form_id: str, lang: str) -> Dict | None:
    path = pathlib.Path(f"static/forms/{form_id}/cache_{lang}.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None

def save_cache(form_id: str, data: Dict, lang: str) -> None:
    path = pathlib.Path(f"static/forms/{form_id}/cache_{lang}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
