import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from pathlib import Path

from routers.chat import router
from services.retriever_service import register_pdf
from services.db import Database
from config import DATA_DIR, DB_CONFIG


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("🚀 بدء تشغيل التطبيق...")

    for pdf in DATA_DIR.glob("*.pdf"):
        register_pdf(pdf.stem, str(pdf))

    app.state.db_gps = Database(DB_CONFIG)
    logging.info("✅ تم الاتصال بقاعدة البيانات")

    yield

    app.state.db_gps.close()
    logging.info("🔒 تم إغلاق اتصال قاعدة البيانات")


app = FastAPI(title="Smart Kiosk - Protected Zones", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1️⃣ API أولًا (مهم جدًا)
app.include_router(router)

# 2️⃣ ملفات static
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3️⃣ React SPA — فقط لغير /llm
UI_INDEX = Path("static/ui/index.html")

@app.get("/")
@app.get("/{path:path}")
async def serve_spa(path: str = ""):
    if path.startswith("llm"):
        return {"error": "Invalid route"}  # ما يوصل هنا أصلاً
    return HTMLResponse(UI_INDEX.read_text(encoding="utf-8"))