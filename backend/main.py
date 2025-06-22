from fastapi import FastAPI
from routes.session   import router as session_router
from routes.explain   import router as explain_router
from routes.submit    import router as submit_router

app = FastAPI(
    title="Immigration Form Helper",
    description="Create sessions to parse USCIS forms with Gemini + Groq"
)

app.include_router(session_router)
app.include_router(explain_router)
app.include_router(submit_router)
