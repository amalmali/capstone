from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

# استيراد الخدمات الخاصة بالمشروع الأول (الذكاء الاصطناعي والصوت)
from services.audio_utils import listen_to_mic, speak_text
from services.rag_service import answer
from services.retriever_service import retrievers


# استيراد الإعدادات لجلب اسم النطاق الجغرافي
from config import GEOFENCE_NAME

# إعداد الراوتر والقوالب
router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

# ملاحظة: سيتم تمرير قاعدة البيانات من التطبيق الأساسي (app) 
# لضمان عدم فتح اتصالات متعددة بلا داعي

@router.get("/chat", response_class=HTMLResponse)
async def get_kiosk_page(request: Request):
    """عرض صفحة الدردشة الخاصة بنظام الكشك"""
    return templates.TemplateResponse("chat.html", {"request": request})

@router.get("/gps-status")
async def get_gps_status(request: Request):
    """جلب حالة الموقع الحالية من قاعدة البيانات المشتركة"""
    # الوصول إلى قاعدة البيانات المعرفة في main.py عبر request.app
    db_gps = getattr(request.app.state, "db_gps", None)
    
    if not db_gps:
        return {"status": "error", "message": "نظام GPS غير مفعل"}
    
    try:
        # استعلام لجلب آخر حالة تم تسجيلها بواسطة الخيط الخلفي
        with db_gps.conn.cursor() as cur:
            cur.execute("SELECT inside_riyadh FROM gps_points ORDER BY data DESC LIMIT 1;")
            result = cur.fetchone()
            is_inside = result[0] if result else False
            
        return {
            "status": "success",
            "is_inside": is_inside,
            "message": f"حالتك الآن: {'داخل' if is_inside else 'خارج'} حدود {GEOFENCE_NAME}"
        }
    except Exception as e:
        logging.error(f"❌ خطأ في جلب بيانات الموقع: {e}")
        return {"status": "error", "message": "حدث خطأ أثناء فحص الموقع"}

@router.post("/voice-interaction")
async def voice_interaction(
    background_tasks: BackgroundTasks,
    query: Optional[str] = Form(None), 
    use_voice: bool = Form(True)
):
    """المعالجة الذكية للسؤال والرد القانوني"""
    
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

    # 3. التحقق من تحميل الملفات القانونية
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
        logging.error(f"❌ خطأ في المعالجة القانونية: {e}")
        return JSONResponse({
            "status": "error", 
            "message": "حدث خطأ فني أثناء استخراج المعلومة."
        })