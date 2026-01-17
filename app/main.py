import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

# استيراد الراوتر
from routers.chat import router

# استيراد خدمات RAG وقاعدة البيانات
from services.retriever_service import register_pdf
from services.db import Database
from config import DATA_DIR, DB_CONFIG


# ======================================================
# إدارة دورة حياة التطبيق (Lifespan)
# ======================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("🚀 بدء تشغيل التطبيق...")

    # 1️⃣ تحميل ملفات الـ PDF لنظام الذكاء الاصطناعي (RAG)
    for pdf in DATA_DIR.glob("*.pdf"):
        register_pdf(pdf.stem, str(pdf))

    # 2️⃣ إنشاء اتصال واحد بقاعدة البيانات
    app.state.db_gps = Database(DB_CONFIG)
    logging.info("✅ تم الاتصال بقاعدة البيانات")

    yield

    # 3️⃣ عند الإغلاق: إغلاق الاتصال بقاعدة البيانات
    if hasattr(app.state, "db_gps"):
        app.state.db_gps.close()
        logging.info("🔒 تم إغلاق اتصال قاعدة البيانات")


# ======================================================
# إنشاء تطبيق FastAPI
# ======================================================
app = FastAPI(title="Smart Kiosk - Protected Zones", lifespan=lifespan)

# تضمين الراوتر
app.include_router(router)

# إعادة توجيه الجذر إلى واجهة الدردشة
@app.get("/")
def read_root():
    return RedirectResponse(url="/llm/chat")