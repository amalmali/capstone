# routers/chat.py
from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel

from services.audio_utils import listen_to_mic, speak_text
from services.rag_service import answer
from services.retriever_service import retrievers
from services.db import Database

from fastapi import UploadFile, File
import httpx
import json

router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

# ======================================================
# 🔑 مفاتيح ملفات الـ RAG
# ======================================================
GENERAL_RULES_KEY = "مشروع اللائحة التنفيذية للمناطق المحمية"
PROTECTED_RULES_KEY = "protected_areas_rules"

# ======================================================
# 🎨 Agent Decision Logic
# ======================================================
def agent_decide_visual(
    inside: bool,
    zone_name: Optional[str] = None,
    protection_level: Optional[str] = None
):
    if inside:
        return {
            "color": "#22c55e",
            "radius": 6,
            "popup": f"داخل {zone_name} — مستوى الحماية: {protection_level}",
            "zone_name": zone_name,
            "protection_level": protection_level
        }
    else:
        return {
            "color": "#ef4444",
            "radius": 6,
            "popup": "خارج نطاق محمي",
            "zone_name": None,
            "protection_level": None
        }

# ======================================================
# 🧠 بناء سؤال مقيّد حسب مستوى الحماية
# ======================================================
def build_zone_aware_query(user_query: str, protection_level: Optional[str]) -> str:
    level_map = {
        "low": "المناطق ذات الحماية المنخفضة",
        "medium": "المناطق ذات الحماية المتوسطة",
        "high": "المناطق ذات الحماية العالية"
    }

    if not protection_level:
        return user_query

    section_name = level_map.get(str(protection_level).lower())
    if not section_name:
        return user_query

    return (
        f"أجب فقط بالاعتماد على قسم \"{section_name}\" من المرجع.\n\n"
        f"السؤال: {user_query}"
    )

# ======================================================
# 📍 إضافة سياق مكاني للجواب
# ======================================================
def prepend_location_context(
    response_text: str,
    zone_name: Optional[str],
    protection_level: Optional[str]
) -> str:
    if not zone_name or not protection_level:
        return response_text

    level_map = {
        "low": "منخفضة",
        "medium": "متوسطة",
        "high": "عالية"
    }

    level_ar = level_map.get(str(protection_level).lower(), protection_level)

    return (
        f" بحسب تواجدك في محمية {zone_name} "
        f"ذات مستوى الحماية {level_ar}:\n\n"
        + response_text
    )

# ======================================================
# صفحة الواجهة
# ======================================================
@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# ======================================================
# بيانات الخريطة
# ======================================================
@router.get("/map-data")
async def map_data(request: Request):
    db: Database = request.app.state.db_gps

    zones = db.get_zones_geojson()
    points = db.get_points_geojson()

    for feature in points.get("features", []):
        props = feature.get("properties", {})
        feature["properties"]["visual"] = agent_decide_visual(
            bool(props.get("inside_geofence")),
            props.get("zone_name"),
            props.get("protection_level")
        )

    return {"zones": zones, "points": points}

# ======================================================
# إضافة نقطة GPS
# ======================================================
class PointIn(BaseModel):
    lat: float
    lng: float

@router.post("/add-point")
async def add_point(point: PointIn, request: Request):
    db: Database = request.app.state.db_gps

    inside = False
    zone_name = None
    protection_level = None

    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT name, protection_level
            FROM protected_zones
            WHERE ST_Contains(
                geom,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            );
        """, (point.lng, point.lat))

        rows = cur.fetchall()
        if rows:
            inside = True
            zone_name, protection_level = rows[0]

    # حفظ النقطة في قاعدة البيانات
    db.save_point(
        lat=point.lat,
        lon=point.lng,
        inside_geofence=inside,
        officer_id=None
    )

    # ==================================================
    # ✅ FIX: حفظ آخر نقطة في الذاكرة (إزالة التجميد)
    # ==================================================
    request.app.state.last_location = {
        "inside": inside,
        "zone_name": zone_name,
        "protection_level": protection_level
    }

    return {
        "status": "saved",
        "inside": inside,
        "zone_name": zone_name,
        "protection_level": protection_level
    }

# ======================================================
# 🎙️ Voice + Agentic RAG
# ======================================================
@router.post("/voice")
async def voice_interaction(
    request: Request,
    background_tasks: BackgroundTasks,
    query: Optional[str] = Form(None),
    use_voice: bool = Form(True)
):
    # 1️⃣ السؤال
    user_query = query.strip() if query and query.strip() else listen_to_mic(timeout=5)
    if not user_query:
        return {"status": "no_speech"}

    # ==================================================
    # ✅ FIX: القرار المكاني من آخر نقطة (بدون DB)
    # ==================================================
    last_location = getattr(request.app.state, "last_location", None)

    inside_geofence = False
    zone_name = None
    protection_level = None

    if last_location:
        inside_geofence = last_location.get("inside", False)
        zone_name = last_location.get("zone_name")
        protection_level = last_location.get("protection_level")

    response_text = None
    source_used = None

    # ==================================================
    # Agentic RAG Decision
    # ==================================================
    if inside_geofence and PROTECTED_RULES_KEY in retrievers:
        enriched_query = build_zone_aware_query(user_query, protection_level)
        response_text, _ = answer(enriched_query, PROTECTED_RULES_KEY)
        source_used = "protected"

    elif (not inside_geofence) and GENERAL_RULES_KEY in retrievers:
        response_text, _ = answer(user_query, GENERAL_RULES_KEY)
        source_used = "general"

    # fallback آمن
    if (not response_text or not response_text.strip()) and GENERAL_RULES_KEY in retrievers:
        response_text, _ = answer(user_query, GENERAL_RULES_KEY)
        source_used = source_used or "general"

    # إضافة السياق المكاني فقط لو داخل محمية
    if inside_geofence and zone_name and protection_level and response_text:
        response_text = prepend_location_context(
            response_text, zone_name, protection_level
        )

    if not response_text:
        response_text = "لم يتم العثور على إجابة مناسبة."

    if use_voice:
        background_tasks.add_task(speak_text, response_text)

    return {
        "status": "success",
        "query": user_query,
        "response": response_text,
        "source": source_used,
        "inside_geofence": bool(inside_geofence),
        "zone_name": zone_name,
        "protection_level": protection_level
    }

# ======================================================
# تحليل صورة عبر VLM وحفظ المخالفات
# ======================================================
VLM_API_URL = "http://127.0.0.1:9000/vlm/analyze"

@router.post("/analyze-image")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    db: Database = request.app.state.db_gps

    img = await file.read()

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            VLM_API_URL,
            files={"file": (file.filename, img, file.content_type or "image/jpeg")}
        )

    if resp.status_code != 200:
        return {"status": "error", "details": resp.text}

    raw_report = resp.json()

    if isinstance(raw_report, str):
        try:
            report = json.loads(raw_report)
        except json.JSONDecodeError:
            report = {"violation_type": raw_report}
    elif isinstance(raw_report, dict):
        report = raw_report
    else:
        report = {"violation_type": "Unknown"}

    db.save_violation(
        violation_type=report.get("violation_type", "Unknown"),
        violation_severity=report.get("violation_severity"),
        people_count=report.get("people_count"),
        detected_objects=report.get("detected_objects") or [],
        confidence=report.get("confidence")
    )

    return {"status": "success"}