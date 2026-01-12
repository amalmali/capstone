
# إعدادات GPS
# =======================
SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 9600

# إعدادات قاعدة البيانات

DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": 5432
}


# إعدادات تتبع الحركة

SAVE_INTERVAL = 5
MOVE_THRESHOLD = 0.00005

GEOFENCE_NAME = "Riyadh"

# Audio alert file
ALERT_SOUND = "/home/pi/gps_alert.mp3"
