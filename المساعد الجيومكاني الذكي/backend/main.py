from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse # أضفنا هذا لاستدعاء الشات
import pandas as pd
import joblib
import secrets
import os
import numpy as np

from database import get_db, engine
from models import Base, EnvironmentalPrediction
from schemas import PredictionInput 


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Environmental Risk API - النسخة المحدثة 2026")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "Risk_model_pipeline.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "ml", "Risk_label_encoder.pkl")

if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
else:
    print("⚠️ خطأ: ملفات المودل غير موجودة.")


@app.get("/llm/chat", response_class=HTMLResponse)
async def get_chat_page():
    
    file_path = os.path.join(BASE_DIR, "templates", "chat.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return HTMLResponse(content=content, headers={"X-Frame-Options": "ALLOWALL"})
    return HTMLResponse(content="<h1>ملف chat.html غير موجود في مجلد templates</h1>", status_code=404)


USERNAME = "ibtesam"
PASSWORD = "1234"

@app.post("/login")
async def login(data: dict):
    username = data.get("username")
    password = data.get("password")
    if secrets.compare_digest(username, USERNAME) and secrets.compare_digest(password, PASSWORD):
        return {"message": "Login successful", "status": "success"}
    raise HTTPException(status_code=401, detail="اسم المستخدم أو كلمة المرور غير صحيحة")


@app.post("/predict")
def predict_risk(data: PredictionInput, db: Session = Depends(get_db)):
    try:
        input_data = data.dict()
        input_df = pd.DataFrame([input_data])

        prediction = model.predict(input_df)
        risk_level = label_encoder.inverse_transform(prediction)[0]
        
        probabilities = model.predict_proba(input_df)
        confidence = np.max(probabilities) * 100

        reasons_list = []
        if risk_level == "High":
            if data.Fine_Amount > 100000: reasons_list.append("قيمة الغرامة مرتفعة جداً")
            if data.Distance_To_Road_km > 20: reasons_list.append("الموقع بعيد جداً عن الطرق")
        elif risk_level == "Medium":
            if data.Area_m2 > 1000: reasons_list.append("المساحة المتضررة واسعة")
        else:
            reasons_list.append("تأثير محدود")

        reasons_str = " | ".join(reasons_list)

        record = EnvironmentalPrediction(
            protected_area=data.Protected_Area,
            violation_type=data.Violation_Type,
            season=data.Season,
            area_m2=data.Area_m2,
            distance_to_road_km=data.Distance_To_Road_km,
            distance_to_urban_km=data.Distance_To_Urban_km,
            year=data.Year,
            fine_amount=data.Fine_Amount,
            risk_level=risk_level,
            reasons=reasons_str
        )
        db.add(record)
        db.commit()
        
        return {
            "Risk_Level": risk_level,
            "Confidence": confidence,
            "Reasons": reasons_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    records = db.query(EnvironmentalPrediction).order_by(EnvironmentalPrediction.created_at.desc()).limit(20).all()
    return [
        {
            "id": r.id,
            "protected_area": r.protected_area,
            "violation_type": r.violation_type,
            "area_m2": r.area_m2,
            "fine_amount": r.fine_amount,
            "risk_level": r.risk_level,
            "reasons": r.reasons,
            "date": r.created_at
        } for r in records
    ]