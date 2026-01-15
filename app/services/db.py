# db.py
import psycopg2
from datetime import datetime

class Database:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.conn.autocommit = True

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

    def get_intersecting_zone_info(self, lat, lon):
        """
        تُرجع (name, protection_level) إذا كانت النقطة داخل أي محمية
        وإلا تُرجع (None, None)
        """
        query = """
            SELECT p.name, p.protection_level
            FROM protected_zones p
            WHERE ST_Intersects(
                p.geom,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            )
            ORDER BY p.id
            LIMIT 1;
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (lon, lat))
            result = cur.fetchone()
            return result if result else (None, None)

    def close(self):
        self.conn.close()
