import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap, MarkerCluster, MeasureControl
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np
from shapely import wkb


st.set_page_config(page_title="ذكاء التأثير البيئي", layout="wide")

COLOR_PALETTE = {
    "bg_creamy": "#F1F3E0",
    "light_green": "#D2DCB6",
    "mid_green": "#A1BC98",
    "dark_green": "#778873",
    "white": "#ffffff",
    "accent_orange": "#E67E51",
    "text_dark": "#102A43"
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
html, body, [class*="st-"] {{
    font-family: 'Cairo', sans-serif;
    direction: rtl;
    text-align: right;
}}
.stApp {{ background-color: {COLOR_PALETTE['bg_creamy']}; }}
.card {{
    background: {COLOR_PALETTE['white']};
    padding: 24px;
    border-radius: 14px;
    box-shadow: 0 4px 15px rgba(119, 136, 115, 0.1);
    border: 1px solid {COLOR_PALETTE['light_green']};
    border-top: 4px solid {COLOR_PALETTE['accent_orange']};
    text-align: center;
}}
.card-title {{ font-size: 14px; color: {COLOR_PALETTE['dark_green']}; font-weight: 600; }}
.card-value {{ font-size: 28px; font-weight: 700; color: {COLOR_PALETTE['accent_orange']}; }}
.section {{
    font-size: 22px;
    font-weight: 700;
    color: {COLOR_PALETTE['dark_green']};
    margin: 25px 0 10px;
    border-right: 5px solid {COLOR_PALETTE['accent_orange']};
    padding-right: 15px;
}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Smart_Environmental_Dataset.csv")
        geo = pd.read_csv("combined_protected_areas.geojson")
        geo["geometry"] = geo["geom"].apply(lambda x: wkb.loads(bytes.fromhex(x)))
        gdf = gpd.GeoDataFrame(geo, geometry="geometry", crs="EPSG:4326")
        gdf["lat"] = gdf.geometry.centroid.y
        gdf["lon"] = gdf.geometry.centroid.x
        clean = lambda x: x.replace("محمية", "").strip()
        df["link"] = df["Protected_Area"].apply(clean)
        gdf["link"] = gdf["protected_area"].apply(clean)
        return df, gdf
    except:
        return pd.DataFrame(), None

df, gdf = load_data()


risk_map = {"High": "عالية", "Medium": "متوسطة", "Low": "منخفضة"}

with st.expander("🔍 نطاق التحليل الاستراتيجي (الفلاتر)", expanded=True):
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        with c1:
            areas = st.multiselect("اختر المحميات", df["Protected_Area"].unique(), default=df["Protected_Area"].unique())
        with c2:
            risks = st.multiselect("مستوى المخاطر", df["Risk_Level"].unique(), default=df["Risk_Level"].unique(), 
                                   format_func=lambda x: risk_map.get(x, x))
        with c3:
            years = st.slider("الفترة الزمنية", int(df["Year"].min()), int(df["Year"].max()), (int(df["Year"].min()), int(df["Year"].max())))

        filtered = df[
            (df["Protected_Area"].isin(areas)) &
            (df["Risk_Level"].isin(risks)) &
            (df["Year"].between(years[0], years[1]))
        ].copy()
    else:
        st.stop()


total_fines = filtered["Fine_Amount"].sum()
affected_area = filtered["Area_m2"].sum()
high_risk_ratio = (filtered["Risk_Level"] == "High").mean() if len(filtered) > 0 else 0
violations_count = len(filtered)
impact_score = round((0.35 * np.log1p(total_fines) + 0.35 * np.log1p(affected_area) + 0.3 * high_risk_ratio * 100), 1)

c1, c2, c3, c4, c5 = st.columns(5)
def card(col, title, value):
    col.markdown(f"""<div class="card"><div class="card-title">{title}</div><div class="card-value">{value}</div></div>""", unsafe_allow_html=True)

card(c1, "إجمالي الغرامات", f"{total_fines:,.0f} ر.س")
card(c2, "المساحة المتأثرة", f"{affected_area:,.0f} م²")
card(c3, "نسبة المخاطر العالية", f"{high_risk_ratio*100:.1f}%")
card(c4, "عدد المخالفات", f"{violations_count}")
card(c5, "درجة التأثير", impact_score)


st.markdown('<div class="section">🗺️ التحليل المكاني الذكي للمخالفات</div>', unsafe_allow_html=True)
if gdf is not None:
    map_df = filtered.merge(gdf[["link", "lat", "lon"]], on="link")
    m = folium.Map(location=[24, 45], zoom_start=5, tiles="CartoDB positron")
    cluster = MarkerCluster().add_to(m)
    for _, r in map_df.iterrows():
        marker_color = COLOR_PALETTE['accent_orange'] if r['Risk_Level'] == 'High' else COLOR_PALETTE['dark_green']
        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=6 + (r["Area_m2"] / (map_df["Area_m2"].max() + 1)) * 12,
            color=marker_color, fill=True, fill_color=marker_color, fill_opacity=0.7,
            tooltip=f"<b>محمية: {r['Protected_Area']}</b><br>الغرامة: {r['Fine_Amount']:,.0f} ر.س"
        ).add_to(cluster)
    HeatMap(map_df[["lat", "lon", "Fine_Amount"]].values.tolist(), radius=18, blur=12).add_to(m)
    st_folium(m, height=480, width="100%")

st.markdown('<div class="section">📊 التحليل الإحصائي المتقدم</div>', unsafe_allow_html=True)
r1, r2 = st.columns(2)

with r1:
    trend = filtered.groupby("Year")["Fine_Amount"].sum().reset_index()
    fig_trend = px.line(trend, x="Year", y="Fine_Amount", title="الاتجاه الزمني للغرامات",
                        labels={"Year": "السنة", "Fine_Amount": ""},
                        color_discrete_sequence=[COLOR_PALETTE['accent_orange']])
    fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Cairo", xaxis=dict(automargin=True), yaxis=dict(automargin=True))
    st.plotly_chart(fig_trend, use_container_width=True)

with r2:
    risk_dist = filtered.groupby("Risk_Level")["Fine_Amount"].sum().reset_index()
    risk_dist["Risk_Name"] = risk_dist["Risk_Level"].map(risk_map)
    fig_risk = px.pie(risk_dist, names="Risk_Name", values="Fine_Amount", title="توزيع التأثير حسب مستوى المخاطر",
                      color="Risk_Name",
                      color_discrete_map={
                          "عالية": COLOR_PALETTE['accent_orange'], 
                          "متوسطة": COLOR_PALETTE['mid_green'], 
                          "منخفضة": COLOR_PALETTE['light_green']
                      })
    fig_risk.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_family="Cairo")
    st.plotly_chart(fig_risk, use_container_width=True)

st.markdown("---")
c_wide, c_side = st.columns([1.6, 1])

with c_wide:
    pareto = filtered.groupby("Violation_Type")["Fine_Amount"].sum().sort_values(ascending=True).reset_index()
    fig1 = px.bar(pareto, y="Violation_Type", x="Fine_Amount", orientation='h',
                  title="تحليل أنواع المخالفات (تأثير مالي)",
                  labels={"Violation_Type": "", "Fine_Amount": "إجمالي الغرامات (ر.س)"},
                  color_discrete_sequence=[COLOR_PALETTE['dark_green']])
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Cairo", margin=dict(l=220), yaxis=dict(automargin=True))
    st.plotly_chart(fig1, use_container_width=True)

with c_side:
    fig2 = px.scatter(filtered, x="Distance_To_Urban_km", y="Fine_Amount",
                      size="Area_m2", color="Risk_Level",
                      title="المخاطر مقابل القرب من العمران",
                      labels={"Distance_To_Urban_km": "المسافة (كم)", "Fine_Amount": "الغرامة", "Risk_Level": "المخاطر"},
                      color_discrete_map={"High": COLOR_PALETTE['accent_orange'], "Medium": COLOR_PALETTE['mid_green'], "Low": COLOR_PALETTE['light_green']})
    fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Cairo", xaxis=dict(automargin=True), yaxis=dict(automargin=True))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
eff = filtered.groupby("Protected_Area").agg(total_fines=("Fine_Amount", "sum"), total_area=("Area_m2", "sum")).reset_index()
eff["efficiency"] = eff["total_fines"] / eff["total_area"].replace(0, 1)
fig3 = px.bar(eff.sort_values("efficiency", ascending=False), x="Protected_Area", y="efficiency",
              title="كفاءة الرقابة (ريال لكل متر مربع)",
              labels={"Protected_Area": "المحمية", "efficiency": "معدل الغرامة/م²"},
              color_discrete_sequence=[COLOR_PALETTE['mid_green']])
fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_family="Cairo", xaxis=dict(tickangle=45, automargin=True))
st.plotly_chart(fig3, use_container_width=True)


if not eff.empty:
    top_fine = eff.sort_values("total_fines", ascending=False).iloc[0]["Protected_Area"]
    top_density = eff.sort_values("efficiency", ascending=False).iloc[0]["Protected_Area"]

    st.markdown(f"""
    <div style="background-color: {COLOR_PALETTE['white']}; padding: 25px; border-radius: 12px; border: 1px solid {COLOR_PALETTE['light_green']}; border-right: 8px solid {COLOR_PALETTE['accent_orange']}; shadow: 0 4px 10px rgba(0,0,0,0.05);">
        <h4 style="color: {COLOR_PALETTE['accent_orange']}; margin-top: 0; font-size: 20px;">📌 مخرجات ذكية لدعم القرار الاستراتيجي:</h4>
        <ul style="color: {COLOR_PALETTE['dark_green']}; font-weight: 600; line-height: 1.8; font-size: 16px;">
            <li>المحمية الأعلى تسجيلاً للغرامات: <b style="color:{COLOR_PALETTE['accent_orange']}">{top_fine}</b></li>
            <li>المحمية الأعلى كثافة في المخالفات بالنسبة للمساحة: <b>{top_density}</b></li>
            <li>تحليل البيانات يشير إلى ضرورة تكثيف الدوريات الرقابية في النطاقات القريبة من المراكز الحضرية.</li>
            <li>خرائط التركز الحراري توضح المناطق ذات الأولوية القصوى للتدخل البيئي بناءً على حجم الضرر المالي والمساحي.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)