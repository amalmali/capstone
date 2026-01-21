import joblib
import pandas as pd
import numpy as np
from arabic_reshaper import reshape
from bidi.algorithm import get_display


def fix_text(text):
    return get_display(reshape(text))


try:
    model = joblib.load("ml/Risk_model_pipeline.pkl")
    le = joblib.load("ml/Risk_label_encoder.pkl")
    print("✅ تم تحميل النموذج بنجاح.\n")
except FileNotFoundError:
    print("❌ خطأ: لم يتم العثور على ملفات النموذج في مجلد ml/")
    exit()

sample_input = {
    "Protected_Area": "روضة التنهات",
    "Violation_Type": "رمي نفايات",
    "Season": "Winter",
    "Area_m2": 2500,
    "Distance_To_Road_km": 1.5,
    "Distance_To_Urban_km": 10.2,
    "Year": 2025,
    "Fine_Amount": 5000
}