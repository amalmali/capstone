from sqlalchemy import create_engine, Column, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#نغير بيانات الداتا بس او نتأكد منها
DATABASE_URL = "postgresql://postgres:postgres@db:5432/geo_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()