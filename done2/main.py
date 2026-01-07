from fastapi import FastAPI
from routers.chat import router
from services.retriever_service import register_pdf
from config import DATA_DIR

app = FastAPI(title="Arabic Local RAG (Raspberry Ready)")

for pdf in DATA_DIR.glob("*.pdf"):
    register_pdf(pdf.stem, str(pdf))

app.include_router(router)
