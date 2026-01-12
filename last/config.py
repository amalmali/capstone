from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstores"

DATA_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)

# مسار الموديلات (تأكد من صحتها في جهازك)
EMBEDDING_MODEL = r"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
VOSK_MODEL_PATH = str(BASE_DIR / "models" / "vosk" / "vosk-model-ar-mgb2-0.4")

# التعديل الهام: تحويل الامتداد إلى mp3
TEMP_AUDIO_OUTPUT = str(BASE_DIR / "out.mp3") 

SAMPLERATE = 16000
EDGE_TTS_VOICE = "ar-SA-HamedNeural"
EDGE_TTS_RATE = "+0%"
EDGE_TTS_VOLUME = "+0%"