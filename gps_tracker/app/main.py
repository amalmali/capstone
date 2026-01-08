from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from shapely.geometry import Point, Polygon

from .database import Base, engine, SessionLocal
from .models import Location

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GPS Tracker API")

# Example polygon (replace with real-world coordinates)
POLYGON_COORDS = [
    (34.001, -118.100), 
    (34.010, -118.090),
    (34.015, -118.110), 
    (34.001, -118.100)
]
polygon = Polygon(POLYGON_COORDS)

class GPSData(BaseModel):
    latitude: float
    longitude: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/gps/")
async def receive_gps(data: GPSData, db: Session = Depends(get_db)):
    point = Point(data.longitude, data.latitude)
    inside = polygon.contains(point)
    location = Location(lat=data.latitude, lon=data.longitude, inside_polygon=inside)
    db.add(location)
    db.commit()
    db.refresh(location)
    return {"id": location.id, "inside_polygon": inside}