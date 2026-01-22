# routers/chat.py
from fastapi import APIRouter, Request, Form, BackgroundTasks, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel
import httpx
import json

from services.audio_utils import listen_to_mic, speak_text
from services.retriever_service import retrievers
from services.db import Database

# 🧠 Agents
from services.agents.agent_router import AgentRouter

router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

agent_router = AgentRouter()

#  مفاتيح ملفات RAG
GENERAL_RULES_KEY = "مشروع اللائحة التنفيذية للمناطق المحمية"
PROTECTED_RULES_KEY = "protected_areas_rules"


# map agent visual based on location

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


# key functions for zone-aware querying

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
        f"بحسب تواجدك في محمية {zone_name} "
        f"ذات مستوى الحماية {level_ar}:\n\n"
        + response_text
    )


# interface route

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


# map data route 

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


# add point route 

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

    db.save_point(
        lat=point.lat,
        lon=point.lng,
        inside_geofence=inside,
        officer_id=None
    )

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


# voice interaction route

@router.post("/voice")
async def voice_interaction(
    request: Request,
    background_tasks: BackgroundTasks,
    query: Optional[str] = Form(None),
    use_voice: bool = Form(True)
):
    user_query = query.strip() if query and query.strip() else listen_to_mic(timeout=5)
    if not user_query:
        return {"status": "no_speech"}

 
    result = agent_router.route_text(request, user_query)

    response_text = result["response"]
    inside_geofence = result["inside_geofence"]
    zone_name = result["zone_name"]
    protection_level = result["protection_level"]

    source_used = "protected" if inside_geofence else "general"

    if use_voice and response_text:
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


# VLM image analysis route

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