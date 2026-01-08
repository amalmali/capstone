from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
from sqlalchemy import text
from ai.stt import speech_to_text
from rag.rag_engine import retrieve_context
from ai.llm import llama_answer
from ai.tts import text_to_speech

app = FastAPI()

#path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "temp")
STATIC_DIR = os.path.join(BASE_DIR, "static")

TMP_INPUT = os.path.join(TMP_DIR, "input.wav")
TMP_OUTPUT = os.path.join(STATIC_DIR, "audio", "answer.mp3")

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "audio"), exist_ok=True)

# ربط مجلد static بالويب
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# الصفحة الرئيسية
@app.get("/")
def read_root():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.post("/ask")
async def ask(file: UploadFile = File(...)):

    # 1) حفظ الصوت المرفوع
    with open(TMP_INPUT, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2) STT
    question = speech_to_text(TMP_INPUT)

    # 3) RAG
    contexts = retrieve_context(question)

    # 4) LLM
    answer = llama_answer(question, contexts)

    # 5) TTS
    text_to_speech(answer, TMP_OUTPUT)

    # 6) إرجاع رابط ملف الصوت
    return {
        "answer_text": answer,
        "audio_url": "/static/audio/answer.mp3"
    }

