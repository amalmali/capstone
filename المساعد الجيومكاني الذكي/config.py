import hashlib
import logging
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstores"
MODELS_DIR = BASE_DIR / "models"


DATA_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)


SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 9600
GEOFENCE_NAME = "Riyadh"
SAVE_INTERVAL = 5
MOVE_THRESHOLD = 0.00005


ALERT_SOUND = str(BASE_DIR / "gps_alert.mp3") 


DB_CONFIG = {
    "dbname": "data",
    "user": "postgres",
    "password": "Ee0590113914", 
    "host": "localhost",
    "port": 5432
}


EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


VOSK_MODEL_PATH = str(MODELS_DIR / "vosk" / "vosk-model-ar-mgb2-0.4")

)
TEMP_AUDIO_OUTPUT = str(BASE_DIR / "out.mp3") 
SAMPLERATE = 16000
EDGE_TTS_VOICE = "ar-SA-HamedNeural"
EDGE_TTS_RATE = "+0%"
EDGE_TTS_VOLUME = "+0%"


LOG_LEVEL = logging.INFO