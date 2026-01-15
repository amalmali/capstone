# services/map_service.py
import folium
import json
import os
from services.spatial_db import get_officer_points, get_protected_zones


def generate_spatial_map():
    """
    يرسم:
    - نقاط الضباط من قاعدة البيانات
    - حدود المناطق المحمية (البوليقون)
    ويحفظ الخريطة داخل static/maps
    ويرجع مسار ويب لعرضها في HTML
    """

    points = get_officer_points()
    zones = get_protected_zones()

    # إنشاء مجلد static/maps لو غير موجود
    os.makedirs("static/maps", exist_ok=True)

    # مسار حفظ الخريطة
    file_path = "static/maps/map.html"

    # إنشاء الخريطة
    m = folium.Map(location=[24.7, 46.7], zoom_start=10)

    # نقاط الضباط
    for _, row in points.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4,
            color="red",
            fill=True,
            fill_opacity=0.8,
            popup=f"Officer: {row['officer_id']}"
        ).add_to(m)

    # حدود المناطق المحمية
    for _, row in zones.iterrows():
        geojson = json.loads(row["geojson"])
        folium.GeoJson(
            geojson,
            name=row["name"],
            style_function=lambda x: {
                "fillColor": "green",
                "color": "green",
                "weight": 2,
                "fillOpacity": 0.2,
            },
            tooltip=f"{row['name']} ({row['protection_level']})"
        ).add_to(m)

    folium.LayerControl().add_to(m)

    # حفظ الخريطة
    m.save(file_path)

    # نرجع مسار ويب
    return "/static/maps/map.html"
