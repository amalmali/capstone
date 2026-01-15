from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

# استيراد الخدمات الخاصة بالمشروع (الذكاء الاصطناعي والصوت)
from services.audio_utils import listen_to_mic, speak_text
from services.rag_service import answer
from services.retriever_service import retrievers

# إعداد الراوتر والقوالب
router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

# ملاحظة: سيتم تمرير قاعدة البيانات من التطبيق الأساسي (app)
# عبر request.app.state.db_gps


# ============================
# واجهة الدردشة
# ============================
@router.get("/chat", response_class=HTMLResponse)
async def get_kiosk_page(request: Request):
    """عرض صفحة الدردشة الخاصة بنظام الكشك"""
    return templates.TemplateResponse("chat.html", {"request": request})


# ============================
# جلب آخر حالة محفوظة (اختياري)
# ============================
@router.get("/gps-status")
async def get_gps_status(request: Request):
    """جلب آخر حالة داخل/خارج من قاعدة البيانات"""
    db_gps = getattr(request.app.state, "db_gps", None)
    
    if not db_gps:
        return {"status": "error", "message": "قاعدة البيانات غير متصلة"}
    
    try:
        with db_gps.conn.cursor() as cur:
            cur.execute("""
                SELECT inside_geofence
                FROM officer_tracking
                ORDER BY timestamp DESC
                LIMIT 1;
            """)
            result = cur.fetchone()
            is_inside = result[0] if result else False
            
        return {
            "status": "success",
            "is_inside": is_inside,
            "message": f"حالتك الآن: {'داخل' if is_inside else 'خارج'} إحدى المناطق المحمية"
        }

    except Exception as e:
        logging.error(f"❌ خطأ في جلب بيانات الموقع: {e}")
        return {"status": "error", "message": "حدث خطأ أثناء فحص الموقع"}


# ============================
# 🔹 فحص نقطة من الفورم وحفظها
# ============================
@router.post("/check-point")
async def check_point(
    request: Request,
    latitude: float = Form(...),
    longitude: float = Form(...),
    officer_id: Optional[int] = Form(None)
):
    """
    يستقبل إحداثيات من المستخدم:
    - يفحص هل النقطة داخل أي محمية (protected_zones)
    - يحفظ النتيجة في officer_tracking (inside_geofence فقط)
    - يرجّع الاسم ومستوى الحماية في الاستجابة (بدون تخزينهم)
    """
    db = getattr(request.app.state, "db_gps", None)

    if not db:
        return JSONResponse({"status": "error", "message": "قاعدة البيانات غير متصلة"})

    try:
        # فحص هل النقطة داخل أي محمية
        zone_name, protection_level = db.get_intersecting_zone_info(latitude, longitude)
        inside = True if zone_name else False

        # حفظ النقطة في قاعدة البيانات (بدون تغيير بنية الجدول)
        db.save_point(latitude, longitude, inside, officer_id)

        return JSONResponse({
            "status": "success",
            "inside": inside,
            "zone_name": zone_name,
            "protection_level": protection_level,
            "message": "داخل منطقة محمية" if inside else "خارج جميع المناطق المحمية"
        })

    except Exception as e:
        logging.error(f"❌ خطأ في فحص النقطة: {e}")
        return JSONResponse({
            "status": "error",
            "message": "حدث خطأ أثناء التحقق من الموقع"
        })


# ============================
# مسار الصوت والـ RAG (كما هو)
# ============================
@router.post("/voice-interaction")
async def voice_interaction(
    background_tasks: BackgroundTasks,
    query: Optional[str] = Form(None), 
    use_voice: bool = Form(True)
):
    """المعالجة الذكية للسؤال والرد"""
    
    # 1. تحديد مصدر السؤال
    if query and query.strip():
        user_query = query.strip()
    else:
        user_query = listen_to_mic(timeout=5)
    
    # 2. التحقق من صحة السؤال
    if not user_query:
        return JSONResponse({
            "status": "no_speech", 
            "message": "لم أتمكن من سماعك بوضوح."
        })

    # 3. التحقق من تحميل الملفات
    if not retrievers:
        return JSONResponse({
            "status": "error", 
            "message": "نظام اللوائح قيد التحميل..."
        })
    
    pdf_name = list(retrievers.keys())[0]

    try:
        # 4. توليد الإجابة (RAG)
        response_text, context = answer(user_query, pdf_name)
        
        # 5. نطق الرد في الخلفية
        if use_voice and response_text:
            background_tasks.add_task(speak_text, response_text)

        # 6. إرسال الرد للواجهة
        return JSONResponse({
            "status": "success", 
            "query": user_query, 
            "response": response_text
        })
        
    except Exception as e:
        logging.error(f"❌ خطأ في المعالجة: {e}")
        return JSONResponse({
            "status": "error", 
            "message": "حدث خطأ فني أثناء استخراج المعلومة."
        })