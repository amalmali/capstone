from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class EnvironmentalPrediction(Base):
    __tablename__ = "environmental_predictions"

    id = Column(Integer, primary_key=True, index=True)
    
   
    protected_area = Column(String, index=True)
    violation_type = Column(String)
    season = Column(String)
    year = Column(Integer)
    area_m2 = Column(Float)
    
    
    distance_to_road_km = Column(Float)
    distance_to_urban_km = Column(Float)
    
    fine_amount = Column(Float)
    
   
    risk_level = Column(String) 
    reasons = Column(String)    
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)