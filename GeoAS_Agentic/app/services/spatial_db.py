# services/spatial_db.py
# ======================================================
# DATABASE ACCESS LAYER (PostGIS)
# مسؤول فقط عن جلب البيانات من قاعدة البيانات
# ======================================================

import psycopg2
from psycopg2.extras import RealDictCursor

# بيانات الاتصال
DB_CONFIG = {
    "host": "localhost", #hostname
    "port": , #port number         
    "dbname": "", # database name    
    "user": "", #username 
    "password": "" #password
}


def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    return psycopg2.connect(**DB_CONFIG)


# ======================================================
# جلب نقاط تحركات العسكريين
# ======================================================
def get_officer_points():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    officer_id,
                    ST_Y(geom) AS lat,
                    ST_X(geom) AS lon,
                    inside_geofence
                FROM public.officer_tracking
                ORDER BY id ASC;
            """)
            return cur.fetchall()
    finally:
        conn.close()


# ======================================================
# جلب البوليقونات (المناطق المحمية)
# ======================================================
def get_protected_zones():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    name,
                    protection_level,
                    ST_AsGeoJSON(geom) AS geojson
                FROM public.protected_zones
                ORDER BY id ASC;
            """)
            return cur.fetchall()
    finally:
        conn.close()
