# main.py

import time
from config import *
from gps_reader import GPSReader
from db import Database
from utils import moved_enough, play_alert

def main():
    print("🚀 GPS Tracker Offline Started")

    gps = GPSReader(SERIAL_PORT, BAUD_RATE)
    db = Database(DB_CONFIG)

    last_lat = None
    last_lon = None
    inside_geofence = False

    try:
        while True:
            lat, lon = gps.read_point()

            if moved_enough(last_lat, last_lon, lat, lon, MOVE_THRESHOLD):
                now_inside = db.is_inside_geofence(lat, lon, GEOFENCE_NAME)

                # التنبيه الصوتي عند الدخول والخروج
                if now_inside and not inside_geofence:
                    print(f"🚨 أنت داخل منطقة {GEOFENCE_NAME}")
                    play_alert(ALERT_SOUND)
                elif not now_inside and inside_geofence:
                    print(f"📤 خرجت من منطقة {GEOFENCE_NAME}")
                    play_alert(ALERT_SOUND)

                inside_geofence = now_inside
                db.save_point(lat, lon, inside_geofence)
                last_lat, last_lon = lat, lon

                print(f"📍 GPS Saved: {lat:.6f}, {lon:.6f}, inside: {inside_geofence}")

            else:
                print("⏸ No significant movement")

            time.sleep(SAVE_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Stopping GPS Tracker")

    finally:
        gps.close()
        db.close()


if __name__ == "__main__":
    main()
