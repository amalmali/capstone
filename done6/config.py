from pathlib import Path

# المسار الرئيسي للمشروع (سيشير تلقائياً إلى مجلد done6)
BASE_DIR = Path(__file__).resolve().parent


DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstores"


DATA_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)


EMBEDDING_MODEL = r"C:\Users\HP\.cache\huggingface\hub\models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2\snapshots\86741b4e3f5cb7765a600d3a3d55a0f6a6cb443d"
LLM_MODEL = "qwen2.5:1.5b"


VOSK_MODEL_PATH = str(BASE_DIR / "models" /"vosk"/"vosk-model-ar-mgb2-0.4")

PIPER_MODEL_PATH = str(BASE_DIR / "models" / "piper" / "ar-jo-medium.onnx")

TEMP_AUDIO_OUTPUT = str(BASE_DIR / "out.wav")
TEMP_VOICE_INPUT = str(BASE_DIR / "voice.wav")

SAMPLERATE = 16000