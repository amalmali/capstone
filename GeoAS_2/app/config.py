import logging
from pathlib import Path

# 1. إعدادات المسارات الأساسية (Paths)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstores"
MODELS_DIR = BASE_DIR / "models"

# إنشاء المجلدات إذا لم تكن موجودة
DATA_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)

# 2. إعدادات نظام GPS (من config1.py)

SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 9600
GEOFENCE_NAME = "Riyadh"
SAVE_INTERVAL = 5
MOVE_THRESHOLD = 0.00005

# مسار صوت التنبيه (تم تغييره ليكون مرناً داخل مجلد المشروع)
ALERT_SOUND = str(BASE_DIR / "gps_alert.mp3") 

# 3. إعدادات قاعدة البيانات (من config1.py)

DB_CONFIG = {
    "dbname": "data",
    "user": "postgres",
    "password": "Ee0590113914",
    "host": "localhost",
    "port": 5432
}

# 4. إعدادات الصوت والذكاء الاصطناعي (من config.py)

# موديل الـ Embeddings للبحث في الـ PDF
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# موديل للتعرف على الكلام (تحويل الصوت لنص)
WHISPER_MODEL_SIZE = "small"   # أو "base" أو "medium" حسب قوة جهازك
WHISPER_DEVICE = "cpu"         # "cuda" لو عندك كرت شاشة
WHISPER_COMPUTE_TYPE = "int8"  # سريع وخفيف على الـ CPU

# إعدادات تحويل النص إلى صوت (Edge-TTS)
TEMP_AUDIO_OUTPUT = str(BASE_DIR / "out.mp3") 
SAMPLERATE = 16000
EDGE_TTS_VOICE = "ar-SA-HamedNeural"
EDGE_TTS_RATE = "+0%"
EDGE_TTS_VOLUME = "+0%"

# 5. إعدادات عامة
LOG_LEVEL = logging.INFO

