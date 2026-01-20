from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file
from fastapi import FastAPI
from app.api.routes import router as vlm_router

app = FastAPI(title="Environmental VLM API")

app.include_router(vlm_router)


@app.get("/")
def root():
    return {"status": "running"}