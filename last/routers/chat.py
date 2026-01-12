from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from services.audio_utils import listen_to_mic, speak_text
from services.rag_service import answer
from services.retriever_service import retrievers
from typing import Optional
import logging

# إعداد الراوتر والقوالب
router = APIRouter(prefix="/llm")
templates = Jinja2Templates(directory="templates")

@router.get("/chat", response_class=HTMLResponse)
async def get_kiosk_page(request: Request):
    """عرض صفحة الدردشة الخاصة بنظام الكشك"""
    return templates.TemplateResponse("chat.html", {"request": request})

@router.post("/voice-interaction")
async def voice_interaction(
    background_tasks: BackgroundTasks,
    query: Optional[str] = Form(None), # استلام السؤال المكتوب (إن وجد)
    use_voice: bool = Form(True)      # خيار تفعيل الرد الصوتي
):
    # 1. تحديد مصدر السؤال: نصي أم صوتي
    if query and query.strip():
        user_query = query.strip()
        logging.info(f"⌨️ سؤال مكتوب تم استلامه: {user_query}")
    else:
        # تشغيل الميكروفون للاستماع
        user_query = listen_to_mic(timeout=5)
        logging.info(f"🎤 سؤال صوتي تم التقاطه: {user_query}")
    
    # 2. التحقق من وجود نص صالح للمعالجة
    if not user_query:
        return JSONResponse({
            "status": "no_speech", 
            "message": "لم أتمكن من سماعك بوضوح، يرجى المحاولة مرة أخرى أو الكتابة."
        })

    # 3. التأكد من جاهزية الفهارس القانونية (FAISS)
    if not retrievers:
        logging.warning("⚠️ محرك البحث (Retrievers) غير جاهز بعد.")
        return JSONResponse({
            "status": "error", 
            "message": "نظام اللوائح قيد التحميل، يرجى المحاولة بعد لحظات."
        })
    
    # الحصول على اسم أول لائحة محملة (الملف الافتراضي)
    pdf_name = list(retrievers.keys())[0]

    try:
        # 4. استخراج الإجابة القانونية من خلال خدمة RAG
        # تم تعديل answer لتعيد النص والسياق، هنا نهتم بالنص فقط للرد
        response_text, context = answer(user_query, pdf_name)
        
        # 5. تشغيل الرد الصوتي في الخلفية (Asynchronous Task)
        # هذا يضمن استجابة فورية للواجهة بينما يستمر الصوت في العمل
        if use_voice and response_text:
            logging.info("📢 إضافة مهمة نطق الرد إلى الخلفية...")
            background_tasks.add_task(speak_text, response_text)

        # 6. الرد النهائي للواجهة الأمامية
        return JSONResponse({
            "status": "success", 
            "query": user_query, 
            "response": response_text,
            "has_voice": use_voice
        })
        
    except Exception as e:
        logging.error(f"❌ خطأ فني أثناء معالجة الطلب القانوني: {e}")
        return JSONResponse({
            "status": "error", 
            "message": "عذراً، حدث خطأ فني أثناء استخراج المعلومة، يرجى المحاولة مجدداً."
        })