import threading
import time
import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

# استيراد الراوتر الخاص بالدردشة
from routers.chat import router

# استيراد المكونات اللازمة لـ GPS و RAG
from services.retriever_service import register_pdf
from services.gps_reader import GPSReader
from services.db import Database
from services.utils import moved_enough, play_alert
from config import DATA_DIR, DB_CONFIG, SERIAL_PORT, BAUD_RATE, MOVE_THRESHOLD, GEOFENCE_NAME, ALERT_SOUND

# 1. تعريف وظيفة تتبع الموقع (Background GPS Task)
def gps_background_tracker(app_state):
    logging.info("🚀 بدء تشغيل متتبع GPS في الخلفية...")
    try:
        gps = GPSReader(SERIAL_PORT, BAUD_RATE)
        db = Database(DB_CONFIG)
        app_state.db_gps = db # مشاركة الكائن مع التطبيق لتجنب فتح اتصالات متعددة
        
        last_lat, last_lon = None, None
        inside_geofence = False

        while True:
            try:
                lat, lon = gps.read_point()
                if lat and lon:
                    if moved_enough(last_lat, last_lon, lat, lon, MOVE_THRESHOLD):
                        now_inside = db.is_inside_geofence(lat, lon, GEOFENCE_NAME)

                        # منطق التنبيه الصوتي عند تغيير الحالة (دخول/خروج)
                        if now_inside != inside_geofence:
                            play_alert(ALERT_SOUND)
                            inside_geofence = now_inside

                        db.save_point(lat, lon, inside_geofence)
                        
                        # تحديث حالة التطبيق ليراها المستخدم في الواجهة
                        app_state.current_gps = {
                            "lat": lat,
                            "lon": lon,
                            "is_inside": inside_geofence,
                            "last_update": time.time()
                        }
                        
                        last_lat, last_lon = lat, lon
            except Exception as e:
                logging.error(f"⚠️ خطأ أثناء قراءة GPS: {e}")
            
            time.sleep(1) # فحص كل ثانية لتوفير الطاقة
    except Exception as e:
        logging.critical(f"❌ فشل تشغيل نظام GPS: {e}")

# 2. إدارة دورة حياة التطبيق (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # عند التشغيل:
    # أ- تسجيل ملفات PDF للذكاء الاصطناعي
    for pdf in DATA_DIR.glob("*.pdf"):
        register_pdf(pdf.stem, str(pdf))
    
    # ب- تشغيل خيط الـ GPS في الخلفية
    app.state.current_gps = {"is_inside": False, "lat": 0, "lon": 0}
    gps_thread = threading.Thread(target=gps_background_tracker, args=(app.state,), daemon=True)
    gps_thread.start()
    
    yield
    # عند الإغلاق:
    if hasattr(app.state, "db_gps"):
        app.state.db_gps.close()

# 3. إنشاء تطبيق FastAPI
app = FastAPI(title="Smart Kiosk AI & GPS", lifespan=lifespan)

# تضمين الراوتر
app.include_router(router)

@app.get("/")
def read_root():
    return RedirectResponse(url="/llm/chat")