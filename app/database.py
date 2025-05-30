# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from app.models.user import Base
from sqlalchemy.ext.declarative import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"  # Or your MongoDB Atlas URI
client = AsyncIOMotorClient(MONGO_URL)

db = client["secure_file_sharing"]
users_collection = db["users"]
files_collection = db["files"]
audit_logs_collection = db["audit_logs"]

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_tables():
    from app.models import user, file  # Import models here to register them
    Base.metadata.create_all(bind=engine)
