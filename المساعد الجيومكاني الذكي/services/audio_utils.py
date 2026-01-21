import sounddevice as sd
import vosk
import queue
import json
import logging
import time
import pygame
import asyncio
import edge_tts
import os

from pathlib import Path
from config import (
    VOSK_MODEL_PATH,
    SAMPLERATE,
    TEMP_AUDIO_OUTPUT,
    EDGE_TTS_VOICE,
    EDGE_TTS_RATE,
    EDGE_TTS_VOLUME
)

logging.basicConfig(level=logging.INFO)
audio_queue = queue.Queue()

try:
    vosk_model = vosk.Model(str(VOSK_MODEL_PATH))
except Exception as e:
    logging.error(f"❌ خطأ في تحميل موديل Vosk: {e}")
    vosk_model = None

def callback(indata, frames, time_info, status):
    if status:
        logging.warning(status)
    audio_queue.put(bytes(indata))

def listen_to_mic(timeout: int = 5) -> str:
    if not vosk_model:
        logging.error("❌ موديل Vosk غير متاح.")
        return ""

    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            break

    logging.info(f"🎤 جاري الاستماع (Timeout: {timeout}s)...")
    rec = vosk.KaldiRecognizer(vosk_model, SAMPLERATE)

    try:
        with sd.RawInputStream(samplerate=SAMPLERATE, blocksize=8000, dtype="int16",
                               channels=1, callback=callback):
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data = audio_queue.get(timeout=0.2)
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").strip()
                        if text:
                            logging.info(f"✅ تم التقاط: {text}")
                            return text
                except queue.Empty:
                    pass

            return json.loads(rec.FinalResult()).get("text", "").strip()
    except Exception as e:
        logging.error(f"❌ خطأ في الميكروفون: {e}")
        return ""

async def _edge_tts_async(text: str):
    try:
        communicate = edge_tts.Communicate(
            text=text, voice=EDGE_TTS_VOICE,
            rate=EDGE_TTS_RATE, volume=EDGE_TTS_VOLUME
        )
        await communicate.save(TEMP_AUDIO_OUTPUT)
    except Exception as e:
        logging.error(f"❌ خطأ في توليد الملف الصوتي: {e}")

def speak_text(text: str):
    if not text: return
    try:
        # 1. إنشاء ملف الصوت (سيتم استبدال الملف الحالي)
        asyncio.run(_edge_tts_async(text))
        
        # 2. التأكد من وجود الملف قبل التشغيل
        if not os.path.exists(TEMP_AUDIO_OUTPUT):
            logging.error("❌ ملف الصوت لم يتم إنشاؤه")
            return

        # 3. تشغيل الصوت باستخدام pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        pygame.mixer.music.load(TEMP_AUDIO_OUTPUT)
        pygame.mixer.music.play()
        
        # الانتظار حتى ينتهي الصوت
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # 4. التحرير الضروري جداً للملف
        pygame.mixer.music.unload() 
        
    except Exception as e:
        logging.error(f"❌ خطأ في تشغيل الصوت: {e}")