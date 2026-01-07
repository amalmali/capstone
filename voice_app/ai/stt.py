from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")

def speech_to_text(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path, language="ar")
    text = " ".join([seg.text for seg in segments]).strip()
    return text
