# routers/chat.py
from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel

from services.audio_utils import listen_to_mic, speak_text
from services.rag_service import answer
from services.retriever_service import retrievers
from services.db import Database

router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

# =========================
# صفحة الواجهة
# =========================
@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# =========================
# بيانات الخريطة
# =========================
@router.get("/map-data")
async def map_data(request: Request):
    db: Database = request.app.state.db_gps
    return {
        "zones": db.get_zones_geojson(),
        "points": db.get_points_geojson()
    }

# =========================
# إضافة نقطة (من الخريطة)
# =========================
class PointIn(BaseModel):
    lat: float
    lng: float

@router.post("/add-point")
async def add_point(point: PointIn, request: Request):
    db: Database = request.app.state.db_gps

    # نحدد هل داخل محمية
    inside = db.is_inside_protected_zone(point.lat, point.lng)

    # نحفظ فورًا
    db.save_point(
        lat=point.lat,
        lon=point.lng,
        inside_geofence=inside,
        officer_id=None
    )

    # نرجّع النتيجة للواجهة
    return {
        "status": "saved",
        "inside": inside
    }

# =========================
# صوت + RAG (ما لمسناه)
# =========================
@router.post("/voice-interaction")
async def voice_interaction(
    background_tasks: BackgroundTasks,
    query: Optional[str] = Form(None),
    use_voice: bool = Form(True)
):
    if query and query.strip():
        user_query = query.strip()
    else:
        user_query = listen_to_mic(timeout=5)

    if not user_query:
        return {"status": "no_speech"}

    pdf_name = list(retrievers.keys())[0]
    response_text, _ = answer(user_query, pdf_name)

    if use_voice:
        background_tasks.add_task(speak_text, response_text)

    return {
        "status": "success",
        "query": user_query,
        "response": response_text
    }
