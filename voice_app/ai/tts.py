# ai/tts.py
from gtts import gTTS
import os

def text_to_speech(text, output_path):
    tts = gTTS(text=text, lang="ar")
    tts.save(output_path)
