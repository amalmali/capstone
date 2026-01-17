# services/db.py
import psycopg2
from datetime import datetime

class Database:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.conn.autocommit = True

    # =========================
    # حفظ نقطة GPS
    # =========================
    def save_point(self, lat, lon, inside_geofence, officer_id=None):
        query = """
            INSERT INTO officer_tracking (geom, timestamp, inside_geofence, officer_id)
            VALUES (
                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                %s,
                %s,
                %s
            );
        """
        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (lon, lat, datetime.utcnow(), inside_geofence, officer_id)
            )

    # =========================
    # فحص هل النقطة داخل محمية (True / False)
    # =========================
    def is_inside_protected_zone(self, lat, lon):
        query = """
        SELECT EXISTS (
            SELECT 1
            FROM protected_zones
            WHERE ST_Contains(
                geom,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (lon, lat))
            return cur.fetchone()[0]

    # =========================
    # جلب اسم المحمية ومستوى الحماية (اختياري)
    # =========================
    def get_intersecting_zone_info(self, lat, lon):
        query = """
            SELECT name, protection_level
            FROM protected_zones
            WHERE ST_Intersects(
                geom,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
            LIMIT 1;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (lon, lat))
            result = cur.fetchone()
            return result if result else (None, None)

    # =========================
    # GeoJSON للمحميات (Polygon)
    # =========================
    def get_zones_geojson(self):
        query = """
        SELECT jsonb_build_object(
            'type','FeatureCollection',
            'features', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'type','Feature',
                    'geometry', ST_AsGeoJSON(geom)::jsonb,
                    'properties', jsonb_build_object(
                        'id', id,
                        'name', name,
                        'protection_level', protection_level
                    )
                )
            ), '[]'::jsonb)
        )
        FROM protected_zones;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchone()[0]

    # =========================
    # GeoJSON لنقاط التتبع (Point)
    # =========================
    def get_points_geojson(self, limit=500):
        query = """
        SELECT jsonb_build_object(
            'type','FeatureCollection',
            'features', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'type','Feature',
                    'geometry', ST_AsGeoJSON(geom)::jsonb,
                    'properties', jsonb_build_object(
                        'id', id,
                        'inside_geofence', inside_geofence,
                        'officer_id', officer_id,
                        'timestamp', timestamp
                    )
                )
            ), '[]'::jsonb)
        )
        FROM (
            SELECT *
            FROM officer_tracking
            ORDER BY timestamp DESC
            LIMIT %s
        ) t;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (limit,))
            return cur.fetchone()[0]

    def close(self):
        self.conn.close()
