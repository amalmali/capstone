from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PredictionInput(BaseModel):
    
    Protected_Area: str
    Violation_Type: str
    Season: str
    
   
    Area_m2: float
    Distance_To_Road_km: float  
    Distance_To_Urban_km: float 
    Year: int
    Fine_Amount: float

    class Config:
        
        orm_mode = True

class PredictionResponse(BaseModel):
    Risk_Level: str
    Confidence: float 
    Reasons: List[str]

class HistoryRecord(BaseModel):
    id: int
    protected_area: str
    violation_type: str
    risk_level: str
    fine_amount: float
    reasons: str
    date: datetime

    class Config:
        orm_mode = True