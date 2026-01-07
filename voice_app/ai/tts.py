import pyttsx3

def text_to_speech(text: str, out_path: str):
    engine = pyttsx3.init()
    engine.save_to_file(text, out_path)
    engine.runAndWait()
