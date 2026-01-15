# utils.py

from playsound import playsound

def moved_enough(last_lat, last_lon, lat, lon, threshold):
    if last_lat is None or last_lon is None:
        return True
    return abs(lat - last_lat) > threshold or abs(lon - last_lon) > threshold

def play_alert(sound_file):
    """تشغيل صوت التنبيه محليًا"""
    try:
        playsound(sound_file)
    except Exception as e:
        print(f"❌ Audio Error: {e}")