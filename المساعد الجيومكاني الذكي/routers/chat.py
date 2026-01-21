from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging


from services.audio_utils import speak_text
from services.rag_service import answer
from services.retriever_service import retrievers


router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

@router.get("/chat", response_class=HTMLResponse)
async def get_kiosk_page(request: Request):
    """عرض صفحة الدردشة"""
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/check-manual-location")
async def check_manual_location(
    request: Request,
    background_tasks: BackgroundTasks,
    lat: float = Form(...), 
    lon: float = Form(...)
):
    """تحديد المحمية وتقديم تقرير إحصائي من جدول Smart_Environmental_Dataset"""
    db_gps = getattr(request.app.state, "db_gps", None)
    if not db_gps:
        return JSONResponse({"status": "error", "message": "نظام قاعدة البيانات غير متصل"})

    try:
        # 1. جلب معلومات الموقع والتقرير (الذي يحلل الـ 1490 سجل)
        info = db_gps.get_location_info(lat, lon)
        
        if info and info.get("region"):
            region_name = info["region"]
            # تنظيف المسمى للعرض الصوتي (إزالة 'محمية' أو 'التي تم توحيدها') لمنع التكرار
            display_name = region_name.replace("محمية ", "").replace("الملكية ", "").strip()
            report = info.get("report")
            
            if report and report.get("total_violations", 0) > 0:
                
                message = (
                    f"أنت الآن في منطقة {display_name}. "
                    f"تم تحليل {report['total_violations']} مخالفة بيئية في هذه المنطقة. "
                    f"إجمالي الغرامات المرصودة بلغ {report['total_fines']:,} ريال، "
                    f"وأكثر أنواع التعديات شيوعاً هي {report['common_type']}."
                )
            else:
                message = f"أنت الآن داخل نطاق {region_name}. لا توجد إحصائيات تعديات مسجلة لهذه المنطقة حالياً."
            
            is_inside = True
            # تشغيل التقرير الصوتي فوراً
            background_tasks.add_task(speak_text, message)
        else:
            message = "الموقع المحدد خارج حدود المناطق المحمية."
            is_inside = False
            region_name = None

        
        db_gps.save_point(lat, lon, region_name)
        
        return {
            "status": "success", 
            "is_inside": is_inside, 
            "region": region_name,
            "message": message, 
            "report": report if is_inside else None,
            "coords": {"lat": lat, "lon": lon}
        }
    except Exception as e:
        logging.error(f"❌ خطأ في فحص الموقع والتقرير: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.post("/voice-interaction")
async def voice_interaction(
    request: Request,
    background_tasks: BackgroundTasks,
    query: Optional[str] = Form(None), 
    use_voice: bool = Form(True)
):
    """التفاعل الصوتي: تحليل الإحصائيات من الجدول أو الإجابة من اللوائح (RAG)"""
    if not query: return JSONResponse({"status": "no_speech", "message": "لم أسمع سؤالك"})
    db_gps = request.app.state.db_gps

    
    current_area_context = None
    try:
        with db_gps.conn.cursor() as cur:
            cur.execute("SELECT region_name FROM gps_points ORDER BY timestamp DESC LIMIT 1;")
            row = cur.fetchone()
            if row: current_area_context = row[0]
    except Exception as e:
        logging.error(f"خطأ في جلب السياق الجغرافي: {e}")

    
    stat_keywords = ["كم عدد", "إحصائية", "أكثر مخالفة", "غرامات", "أرقام", "مخالفات", "تقرير", "بيانات"]
    
    
    if any(k in query for k in stat_keywords):
        target_keyword = None
        
        for name in ["تركي", "عبدالعزيز", "خالد", "التنهات", "النبقية"]:
            if name in query: target_keyword = name; break
        
       
        if not target_keyword and current_area_context:
            target_keyword = db_gps._simplify_name(current_area_context)

       
        stats = db_gps.generate_area_report(target_keyword)
        
        if stats:
            response_text = (
                f"بالنسبة لبيانات {target_keyword if target_keyword else 'المنطقة الحالية'}: "
                f"سجلنا {stats['total_violations']} مخالفة، "
                f"بإجمالي غرامات بلغت {stats['total_fines']:,} ريال. "
                f"المخالفة الأكثر تكراراً هي {stats['common_type']}."
            )
        else:
            response_text = f"عذراً، لا تتوفر حالياً إحصائيات دقيقة لمحمية {target_keyword if target_keyword else 'هذه المنطقة'}."
    
    
    else:
        pdf_name = list(retrievers.keys())[0] if retrievers else None
        if not pdf_name:
            response_text = "نظام اللوائح والأنظمة غير متاح حالياً."
        else:
            response_text, _ = answer(query, pdf_name)

    if use_voice: 
        background_tasks.add_task(speak_text, response_text)

    return {"status": "success", "response": response_text}

@router.get("/map-data")
async def get_map_data(request: Request):
    """توفير حدود المحميات للخريطة بدقة عالية"""
    db = getattr(request.app.state, "db_gps", None)
    if not db: return {"areas": {"type": "FeatureCollection", "features": []}}
    try:
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT jsonb_build_object(
                    'type', 'FeatureCollection',
                    'features', jsonb_agg(feature)
                ) FROM (
                    SELECT jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON(ST_Transform(geom, 4326))::jsonb,
                        'properties', jsonb_build_object('name', "protected_area")
                    ) AS feature FROM combined_protected_areas_copy
                ) row;
            """)
            result = cur.fetchone()
            return {"areas": result[0] or {"type": "FeatureCollection", "features": []}}
    except Exception as e:
        logging.error(f"❌ خطأ في جلب بيانات الخريطة: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/gps-status")
async def get_gps_status(request: Request):
    """التحقق من حالة الموقع وسياق المحمية الحالية"""
    db_gps = getattr(request.app.state, "db_gps", None)
    if not db_gps: return {"status": "error", "message": "قاعدة البيانات غير متصلة"}
    try:
        with db_gps.conn.cursor() as cur:
            cur.execute("SELECT region_name FROM gps_points ORDER BY timestamp DESC LIMIT 1;")
            res = cur.fetchone()
            region = res[0] if res else None
        return {"status": "success", "region": region, "is_inside": bool(region)}
    except: return {"status": "error"}