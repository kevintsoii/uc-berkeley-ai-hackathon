import uvicorn

from fastapi import FastAPI
from routes.form_upload import router as form_router
from routes.explain     import router as explain_router
from routes.submit      import router as submit_router

app = FastAPI(title="Immigration Form Helper")

# mount routers
app.include_router(form_router,    prefix="/form",    tags=["form"])
app.include_router(explain_router, prefix="/explain", tags=["explain"])
app.include_router(submit_router,  prefix="/submit",  tags=["submit"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",       
        port=8000,
        reload=False      
    )
