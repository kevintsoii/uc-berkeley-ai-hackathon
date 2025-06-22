from google import genai
import json, textwrap
from google.genai import types

# ── 1️⃣ System-prompt template (unchanged) ────────────────────────────────
QUESTION_SYSTEM_TMPL = textwrap.dedent("""
  You are an assistant that writes user-friendly questions for the {immigration_doc_id}
  Employment Authorization form.

  Target language: {lang}

  ## … rules omitted …

  ## Return value (minified JSON only)
  {{
    "questions": [
      {{
        "field_id": "base_id",
        "input_type": "text" | "radio_single" | "checkbox_multi",
        "options": [
          {{
            "option_id": "USCitizen_Y[0]",
            "label": "Yes",
            "coords": [260.161, 514.001, 270.161, 524.001]
          }},
          {{
            "option_id": "USCitizen_N[0]",
            "label": "No",
            "coords": [...]
          }}
        ],
        "question": "...",
        "explanation": "...",
        "cultural_notes": "...",
        "translation_notes": "...",
        "examples": [],
        "format_hint": "",
        "required": true
      }}
    ]
  }}
""").strip()

# ── 2️⃣ Gemini call (instructions now optional / ignored) ─────────────────
def match_fields(
    fields: list[dict],
    form_id: str,
    target_lang: str = "English",
) -> dict:
    system_prompt = QUESTION_SYSTEM_TMPL.format(
        lang=target_lang,
        immigration_doc_id=form_id,
    )

    # Payload is now just the widgets JSON
    payload = json.dumps(fields, ensure_ascii=False)

    resp = genai.Client().models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        contents=payload,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )

    if not resp.text:
        raise RuntimeError("Model returned no text; cannot parse JSON")

    return json.loads(resp.text)
