# db.py

import psycopg2
from datetime import datetime

class Database:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.conn.autocommit = True

    def save_point(self, lat, lon, inside_geofence=None):
        query = """
            INSERT INTO gps_points (geom, data, inside_riyadh)
            VALUES (
                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                %s,
                %s
            );
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (lon, lat, datetime.utcnow(), inside_geofence))

    def is_inside_geofence(self, lat, lon, fence_name="Riyadh"):
        query = """
            SELECT ST_Contains(
                g.geom,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
            FROM geofences g
            WHERE g.name = %s;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (lon, lat, fence_name))
            result = cur.fetchone()
            return result[0] if result else False

    def close(self):
        self.conn.close()
