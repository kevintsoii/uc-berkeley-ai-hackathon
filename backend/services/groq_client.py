import httpx

async def explain_field(field_id: str, question: str, language: str):
    prompt = f"""You are a form helper...
    Field: {question}
    Language: {language}
    ...
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.groq.cloud/v1/generate", json={...})
    data = resp.json()
    return {"explanation": data["..."], "example": data["..."]}
