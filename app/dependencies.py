from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.models.user import User
from app.database import SessionLocal
from app.auth.jwt import decode_token
# from app.main import SessionLocal
from app.utils.security import SECRET_KEY, ALGORITHM  # adjust import as per your project
from app.auth.jwt import get_current_user
from app.routes.auth import verify_token


# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Current user dependency (from token)
# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
    
#     user = db.query(User).filter(User.email == email).first()
#     if user is None:
#         raise credentials_exception
#     return user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = ...  # fetch user from DB based on user_data
    return user

def require_ops(current_user: User = Depends(get_current_user)):
    if current_user.role != "ops":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires ops role"
        )
    return current_user

def require_client(current_user=Depends(get_current_user)):
    if current_user.get("role") != "client":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only client users allowed")
    return current_user