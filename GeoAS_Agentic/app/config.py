# config.py

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
MODELS_DIR.mkdir(exist_ok=True)

# مسار حفظ Chunks النصية (للتدقيق و Agentic RAG)
CHUNKS_DIR = VECTORSTORE_DIR / "chunks"
CHUNKS_DIR.mkdir(exist_ok=True)

# 2. إعدادات نظام GPS
SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 9600

# حدّ الحركة (لتقليل التسجيل المتكرر)
MOVE_THRESHOLD = 0.00005

# (اختياري) فترة الحفظ إن أردتِ استخدامها بدل رقم ثابت في main.py
SAVE_INTERVAL = 5

# مسار صوت التنبيه (مرن داخل مجلد المشروع)
ALERT_SOUND = str(BASE_DIR / "app/gps_alert.mp3")

# 3. إعدادات قاعدة البيانات
DB_CONFIG = {
    "host": "localhost", #hostname
    "port": , #port number         
    "dbname": "", # database name    
    "user": "", #username 
    "password": "" #password
}

# 4. إعدادات الصوت والذكاء الاصطناعي

# موديل الـ Embeddings للبحث في الـ PDF
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# إعدادات التعرف على الكلام (Whisper)
WHISPER_MODEL_SIZE = "small"   # أو "base" أو "medium"
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
