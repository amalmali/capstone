# services/db.py
import psycopg2
from datetime import datetime
import json

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
    # هل النقطة داخل أي محمية؟
    # =========================
    def is_inside_protected_zone(self, lat, lon):
        query = """
        SELECT EXISTS (
            SELECT 1
            FROM protected_zones
            WHERE ST_Intersects(
                geom,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (lon, lat))
            return cur.fetchone()[0]

    # =========================
    # GeoJSON للمحميات (البوليقان)
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
    # GeoJSON للنقاط (مع أعلى مستوى حماية)
    # =========================
    def get_points_geojson(self, limit=500):
        query = """
        SELECT jsonb_build_object(
            'type','FeatureCollection',
            'features', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'type','Feature',
                    'geometry', ST_AsGeoJSON(t.geom)::jsonb,
                    'properties', jsonb_build_object(
                        'id', t.id,
                        'inside_geofence', t.inside_geofence,
                        'officer_id', t.officer_id,
                        'timestamp', t.timestamp,
                        'zone_name', z.name,
                        'protection_level', z.protection_level
                    )
                )
            ), '[]'::jsonb)
        )
        FROM (
            SELECT *
            FROM officer_tracking
            ORDER BY timestamp DESC
            LIMIT %s
        ) t
        LEFT JOIN LATERAL (
            SELECT name, protection_level
            FROM protected_zones
            WHERE ST_Intersects(protected_zones.geom, t.geom)
            ORDER BY
                CASE protection_level
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END
            LIMIT 1
        ) z ON TRUE;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (limit,))
            return cur.fetchone()[0]
    
    def save_violation_report(
        self,
        report: dict,
        inside_geofence: bool,
        zone_name: str | None,
        protection_level: str | None
):
        query = """
            INSERT INTO violation_reports
            (violation_type, violation_severity, people_count, detected_objects, confidence, raw_report,
            zone_name, protection_level, inside_geofence)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """
        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    report.get("violation_type"),
                    report.get("violation_severity"),
                    report.get("people_count"),
                    json.dumps(report.get("detected_objects", [])),
                    report.get("confidence"),
                    json.dumps(report),  # raw json
                    zone_name,
                    protection_level,
                    inside_geofence
                )
            )

    def close(self):
        self.conn.close()
