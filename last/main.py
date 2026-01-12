from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers.chat import router
from services.retriever_service import register_pdf
from config import DATA_DIR

app = FastAPI(title="Arabic Local RAG")

# تسجيل الملفات تلقائياً عند التشغيل
for pdf in DATA_DIR.glob("*.pdf"):
    register_pdf(pdf.stem, str(pdf))

app.include_router(router)

@app.get("/")
def read_root():
    # توجيه المستخدم مباشرة لصفحة الدردشة
    return RedirectResponse(url="/llm/chat")