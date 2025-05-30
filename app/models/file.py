from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .user import Base  # Import Base from user model or your models package

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    upload_date = Column(DateTime, default=datetime.utcnow)
    upload_time = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    owner = relationship("User", back_populates="files")
