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

router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

# ======================================================
# Agent Decision Logic
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
# صفحة الواجهة
# ======================================================
@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# ======================================================
# بيانات الخريطة (Zones + Points)
# ======================================================
@router.get("/map-data")
async def map_data(request: Request):
    db: Database = request.app.state.db_gps

    zones = db.get_zones_geojson()
    points = db.get_points_geojson()

    for feature in points.get("features", []):
        props = feature.get("properties", {})
        inside = bool(props.get("inside_geofence"))
        zone_name = props.get("zone_name")
        protection_level = props.get("protection_level")

        feature["properties"]["visual"] = agent_decide_visual(
            inside,
            zone_name,
            protection_level
        )

    return {
        "zones": zones,
        "points": points
    }

# ======================================================
# إضافة نقطة من الخريطة
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
        query = """
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
        """
        with db.conn.cursor() as cur:
            cur.execute(query, (point.lng, point.lat))
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
# Voice + RAG
# ======================================================
@router.post("/voice")
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
