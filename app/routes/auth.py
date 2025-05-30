from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.models.user import User, UserRole
from app.utils.security import hash_password, verify_password, create_access_token
from passlib.context import CryptContext
from jose import JWTError, jwt
# from app.main import SessionLocal
# app/routes/auth.py

from app.database import SessionLocal  # ✅ instead of from app.main

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"
router = APIRouter()

# Pydantic models for input/output
class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Signup route (client only)
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(data.password)
    new_user = User(email=data.email, hashed_password=hashed_pwd, role=UserRole.client)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created successfully. Please verify your email."}

# Login route
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    return {"access_token": access_token}

def authenticate_user(username: str, password: str, db: Session = SessionLocal()):
    user = db.query(User).filter(User.email == username).first()
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None