from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel

from services.audio_utils import listen_to_mic, speak_text
from services.rag_service import answer
from services.retriever_service import retrievers
from services.db import Database

router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

# ======================================================
# 🔑 مفاتيح ملفات الـ RAG (ثابتة)
# ======================================================
GENERAL_RULES_KEY = "مشروع اللائحة التنفيذية للمناطق المحمية"
PROTECTED_RULES_KEY = "protected_areas_rules"

# ======================================================
# 🎨 Agent Decision Logic (للخريطة)
# ======================================================
def agent_decide_visual(
    inside: bool,
    zone_name: Optional[str] = None,
    protection_level: Optional[str] = None
):
    if inside:
        level_text = protection_level.upper() if protection_level else "غير معروف"
        return {
            "color": "#22c55e",
            "radius": 6,
            "popup": f"داخل {zone_name} — مستوى الحماية: {level_text}",
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
# 🧠 بناء سؤال ذكي حسب مستوى الحماية
# ======================================================
def build_zone_aware_query(user_query: str, protection_level: str) -> str:
    level_map = {
        "low": "المناطق ذات الحماية المنخفضة",
        "medium": "المناطق ذات الحماية المتوسطة",
        "high": "المناطق ذات الحماية القصوى"
    }

    section_name = level_map.get(protection_level)
    if not section_name:
        return user_query

    return (
        f"أجب فقط بالاعتماد على قسم \"{section_name}\" من القوانين.\n\n"
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
        "high": "قصوى"
    }

    level_ar = level_map.get(protection_level, protection_level)

    header = (
        f"📍 بحسب تواجدك في محمية {zone_name} "
        f"ذات مستوى الحماية {level_ar}:\n\n"
    )

    return header + response_text

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

    inside = db.is_inside_protected_zone(point.lat, point.lng)
    zone_name = None
    protection_level = None

    if inside:
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT name, protection_level
                FROM protected_zones
                WHERE ST_Intersects(
                    geom,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                )
                ORDER BY
                    CASE protection_level
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END
                LIMIT 1;
            """, (point.lng, point.lat))
            row = cur.fetchone()
            if row:
                zone_name, protection_level = row

    db.save_point(
        lat=point.lat,
        lon=point.lng,
        inside_geofence=inside,
        officer_id=None
    )

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

    # 2️⃣ آخر موقع
    db: Database = request.app.state.db_gps
    inside = False
    zone_name = None
    protection_level = None

    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT t.inside_geofence, z.name, z.protection_level
            FROM officer_tracking t
            LEFT JOIN LATERAL (
                SELECT name, protection_level
                FROM protected_zones
                WHERE ST_Intersects(protected_zones.geom, t.geom)
                ORDER BY
                    CASE protection_level
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                        ELSE 4
                    END
                LIMIT 1
            ) z ON TRUE
            ORDER BY t.timestamp DESC
            LIMIT 1;
        """)
        row = cur.fetchone()
        if row:
            inside, zone_name, protection_level = row

    response_text = None
    source_used = None

    # 3️⃣ Agentic RAG
    if inside and PROTECTED_RULES_KEY in retrievers:
        enriched_query = build_zone_aware_query(user_query, protection_level)
        response_text, _ = answer(enriched_query, PROTECTED_RULES_KEY)
        if response_text and response_text.strip():
            source_used = "protected"

    if not response_text and GENERAL_RULES_KEY in retrievers:
        response_text, _ = answer(user_query, GENERAL_RULES_KEY)
        source_used = "general"

    if inside and source_used == "general":
        response_text = (
            "⚠️ لم يتم العثور على نص خاص بهذه المحمية.\n"
            "📘 فيما يلي القوانين العامة:\n\n" + response_text
        )

    if inside:
        response_text = prepend_location_context(
            response_text, zone_name, protection_level
        )

    if not response_text:
        response_text = "لم يتم العثور على إجابة مناسبة."

    # 4️⃣ إخراج صوتي
    if use_voice:
        background_tasks.add_task(speak_text, response_text)

    return {
        "status": "success",
        "query": user_query,
        "response": response_text,
        "source": source_used
    }