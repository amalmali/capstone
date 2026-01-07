from fastapi import FastAPI, UploadFile, File
import shutil
import os

from ai.stt import speech_to_text
from rag.rag_engine import retrieve_context
from ai.llm import llama_answer
from ai.tts import text_to_speech

app = FastAPI()

TMP_INPUT = "temp/input.wav"
TMP_OUTPUT = "temp/output.wav"

@app.post("/ask")
async def ask(file: UploadFile = File(...)):

    # 1) حفظ الصوت
    with open(TMP_INPUT, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2) STT (تحويل الصوت إلى نص)
    question = speech_to_text(TMP_INPUT)
    print("QUESTION:", question)

    # 3) RAG (بحث في الـ PDF)
    contexts = retrieve_context(question)
    print("CONTEXTS:", contexts)

    # 4) LLaMA (توليد الإجابة)
    answer = llama_answer(question, contexts)
    print("ANSWER FROM MODEL:", answer)

    # 5) TTS (تحويل النص إلى صوت)
    text_to_speech(answer, TMP_OUTPUT)

    # 6) إرجاع الجواب كنص
    return {"answer": answer}

