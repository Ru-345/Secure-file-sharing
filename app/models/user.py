from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database import Base

import enum

Base = declarative_base()

class UserRole(enum.Enum):
    client = "client"
    ops = "ops"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    # role = Column(Enum(UserRole), default=UserRole.client)
    files = relationship("File", back_populates="owner")
    role = Column(String)  # "client" or "ops"
