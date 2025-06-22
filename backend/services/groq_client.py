import httpx

async def explain_field(field_id: str, language: str) -> dict:
    prompt = f"""
You are a user-friendly form assistant.
Field ID: {field_id}
Language: {language}

Provide:
1) A one-sentence plain-English explanation.
2) A single example.
Return JSON: {{ "explanation":..., "example":... }}
"""
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.groq.cloud/v1/generate",
            json={"prompt": prompt}
        )
    data = res.json()
    return {
        "explanation": data["completions"][0]["text"],  # adjust per actual API
        "example":     data["completions"][1]["text"]
    }
