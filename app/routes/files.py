from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from app.dependencies import get_db, get_current_user
from app.models.user import User
from sqlalchemy import Column, Integer, String
from app.models.user import Base
from app.dependencies import require_ops, require_client
from app.config import UPLOAD_DIR  # wherever you define your upload folder path
from app.crud.file import save_file_metadata
import shutil
import os


router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileModel(Base):
    __tablename__ = "files"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    filename = Column(String)
    path = Column(String)
    owner_id = Column(Integer)


@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Permission check: owner or ops user
    if db_file.owner_id != current_user.id and current_user.role != "ops":
        raise HTTPException(status_code=403, detail="Not authorized to access this file")

    file_path = os.path.join(UPLOAD_DIR, db_file.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(path=file_path, filename=db_file.filename, media_type="application/octet-stream")


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Define path to save the file
    file_location = f"uploads/{file.filename}"
    
    # Save file to disk
    with open(file_location, "wb+") as f:
        f.write(await file.read())
    
    # Get the size of the saved file in bytes
    file_size = os.path.getsize(file_location)
    await save_file_metadata(file.filename, current_user["id"], file_size)

    return {"message": "File uploaded successfully"}
    
    # Create new FileModel instance with metadata
    new_file = FileModel(
        filename=file.filename,
        owner_id=current_user.id,
        file_size=file_size
    )
    
    # Add and commit to DB
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    # Return relevant info to client
    return {
        "filename": new_file.filename,
        "size": new_file.file_size,
        "uploaded_at": new_file.upload_time
    }

@router.get("/download/{file_id}", operation_id="download_file_by_id")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Permission check: owner or ops user
    if db_file.owner_id != current_user.id and current_user.role != "ops":
        raise HTTPException(status_code=403, detail="Not authorized to access this file")

    file_path = db_file.path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(path=file_path, filename=db_file.filename, media_type="application/octet-stream")

@router.get("/files/all", dependencies=[Depends(require_ops)])
def list_all_files(db: Session = Depends(get_db)):
    files = db.query(FileModel).all()
    return files
pass

@router.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if db_file.owner_id != current_user.id and current_user.role != "ops":
        raise HTTPException(status_code=403, detail="Not authorized")

    os.remove(os.path.join(UPLOAD_DIR, db_file.filename))
    db.delete(db_file)
    db.commit()
    return {"msg": "File deleted"}
