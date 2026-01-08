from sqlalchemy import Column, Integer, Float, Boolean
from .database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    inside_polygon = Column(Boolean, default=False)