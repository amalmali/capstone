import psycopg2
import logging
from datetime import datetime

class Database:
    def __init__(self, db_config):
        try:
            self.conn = psycopg2.connect(**db_config)
            self.conn.autocommit = True
            logging.info("✅ تم الاتصال بقاعدة البيانات بنجاح")
        except Exception as e:
            logging.error(f"❌ فشل الاتصال بقاعدة البيانات: {e}")
            raise e

    def get_location_info(self, lat, lon):
        
        try:
            with self.conn.cursor() as cur:
                
                cur.execute("""
                    SELECT "protected_area" 
                    FROM "combined_protected_areas_copy"
                    WHERE ST_Contains(ST_Transform(geom, 4326), ST_SetSRID(ST_MakePoint(%s, %s), 4326)) 
                    LIMIT 1;
                """, (lon, lat))
                res = cur.fetchone()
                
                if not res: return None
                
                full_name = res[0]
                
                keyword = self._simplify_name(full_name)
                
                
                report = self.generate_area_report(keyword)
                
                return {"region": full_name, "report": report}
        except Exception as e:
            logging.error(f"❌ خطأ في get_location_info: {e}")
            return None

    def generate_area_report(self, keyword):
        

        
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CAST("Fine_Amount" AS NUMERIC)) as total_fines,
                ROUND(AVG(CAST("Fine_Amount" AS NUMERIC)), 2) as avg_fine,
                MODE() WITHIN GROUP (ORDER BY "Violation_Type") as common,
                MAX(CAST("Fine_Amount" AS NUMERIC)) as max_fine
            FROM "Smart_Environmental_Dataset"
            WHERE "Protected_Area" ILIKE %s;
        """
        try:
            with self.conn.cursor() as cur:
                search_term = f"%{keyword}%"
                cur.execute(query, (search_term,))
                row = cur.fetchone()
                
                if row and row[0] > 0:
                    return {
                        "total_violations": row[0],
                        "total_fines": float(row[1]) if row[1] else 0,
                        "avg_fine": float(row[2]) if row[2] else 0,
                        "common_type": row[3],
                        "max_fine": float(row[4]) if row[4] else 0
                    }
                return None
        except Exception as e:
            logging.error(f"❌ فشل الاستعلام الإحصائي: {e}")
            return None

    def _simplify_name(self, name):
        
        if not name: return ""
        
        keywords = ["الإمام تركي", "الملك عبدالعزيز", "الملك خالد", "التنهات", "الامام عبدالعزيز"]
        for k in keywords:
            if k in name: return k
        return name.replace("محمية", "").strip()

    def save_point(self, lat, lon, region_name):
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO "gps_points" (geom, timestamp, region_name)
                    VALUES (ST_SetSRID(ST_MakePoint(%s, %s), 4326), CURRENT_TIMESTAMP, %s);
                """, (lon, lat, region_name))
        except Exception as e:
            logging.error(f"❌ خطأ حفظ النقطة: {e}")

    def close(self):
        if self.conn: self.conn.close()