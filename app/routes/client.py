# app/routes/client.py

from fastapi import APIRouter, Depends
from app.utils.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/dashboard")
def client_dashboard(current_user: User = Depends(get_current_user)):
    return {"msg": f"Welcome, {current_user.email}!", "role": current_user.role.value}

@router.get("/files")
def list_files():
    return {"message": "List files endpoint (to be implemented)"}
