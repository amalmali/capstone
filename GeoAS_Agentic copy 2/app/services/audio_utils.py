import sounddevice as sd
import queue
import json
import logging
import time
import pygame
import asyncio
import edge_tts
import os
import numpy as np

from faster_whisper import WhisperModel
from pathlib import Path
from config import (
    SAMPLERATE,
    TEMP_AUDIO_OUTPUT,
    EDGE_TTS_VOICE,
    EDGE_TTS_RATE,
    EDGE_TTS_VOLUME
)

STOP_LISTENING = False

logging.basicConfig(level=logging.INFO)
audio_queue = queue.Queue()

# ============================
# تحميل موديل Whisper
# ============================
try:
    whisper_model = WhisperModel("small", compute_type="int8")  
    # ممكن تغيره إلى: tiny / base / medium
    logging.info("✅ Whisper model loaded successfully")
except Exception as e:
    logging.error(f"❌ خطأ في تحميل موديل Whisper: {e}")
    whisper_model = None


# ============================
# استقبال الصوت من المايك
# ============================
def callback(indata, frames, time_info, status):
    if status:
        logging.warning(status)
    audio_queue.put(indata.copy())


def listen_to_mic(timeout: int = 5) -> str:
    global STOP_LISTENING
    STOP_LISTENING = False

    if not whisper_model:
        logging.error("❌ موديل Whisper غير متاح.")
        return ""

    # تفريغ أي صوت قديم
    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            break

    logging.info("🎤 بدء الاستماع...")

    audio_buffer = []

    try:
        with sd.InputStream(
            samplerate=SAMPLERATE,
            channels=1,
            dtype="float32",
            callback=callback
        ):
            start_time = time.time()

            while time.time() - start_time < timeout:

                # ⛔ إيقاف فوري من الواجهة
                if STOP_LISTENING:
                    logging.info("⏹️ تم إيقاف الاستماع من الواجهة")
                    break

                try:
                    data = audio_queue.get(timeout=0.2)
                    audio_buffer.append(data)
                except queue.Empty:
                    pass

        if not audio_buffer:
            logging.warning("⚠ لم يتم التقاط أي صوت.")
            return ""

        audio_np = np.concatenate(audio_buffer, axis=0).flatten()

        segments, _ = whisper_model.transcribe(audio_np, language="ar")
        text = " ".join([s.text for s in segments]).strip()

        logging.info(f"✅ النص: {text}")
        return text

    except Exception as e:
        logging.error(f"❌ خطأ في الاستماع: {e}")
        return ""

def stop_listening():
    global STOP_LISTENING
    STOP_LISTENING = True



# ============================
# تحويل النص إلى صوت (Edge TTS)
# ============================
async def _edge_tts_async(text: str):
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=EDGE_TTS_VOICE,
            rate=EDGE_TTS_RATE,
            volume=EDGE_TTS_VOLUME
        )
        await communicate.save(TEMP_AUDIO_OUTPUT)
    except Exception as e:
        logging.error(f"❌ خطأ في توليد الملف الصوتي: {e}")


def speak_text(text: str):
    if not text:
        return

    try:
        # 1. توليد الصوت
        asyncio.run(_edge_tts_async(text))

        # 2. التأكد من وجود الملف
        if not os.path.exists(TEMP_AUDIO_OUTPUT):
            logging.error("❌ ملف الصوت لم يتم إنشاؤه")
            return

        # 3. تشغيل الصوت
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(TEMP_AUDIO_OUTPUT)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        # 4. تحرير الملف
        pygame.mixer.music.unload()

    except Exception as e:
        logging.error(f"❌ خطأ في تشغيل الصوت: {e}")