import folium
import psycopg2
from config import DB_CONFIG

def generate_map(output_file="gps_map.html"):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT ST_Y(geom), ST_X(geom), inside_riyadh FROM gps_points ORDER BY data;")
    points = cur.fetchall()
    conn.close()

    if not points:
        print("No GPS data available.")
        return

    m = folium.Map(location=[points[0][0], points[0][1]], zoom_start=12)

    for lat, lon, inside in points:
        color = "green" if inside else "blue"
        folium.CircleMarker([lat, lon], radius=5, color=color, fill=True).add_to(m)

    m.save(output_file)
    print(f"🌐 Map saved as {output_file}")

if __name__ == "__main__":
    generate_map()