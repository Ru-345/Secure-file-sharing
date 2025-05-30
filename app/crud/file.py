# app/crud/file.py

from app.database import files_collection
from datetime import datetime

async def save_file_metadata(filename, owner_id, file_size):
    new_file = {
        "filename": filename,
        "owner_id": owner_id,
        "file_size": file_size,
        "upload_time": datetime.utcnow()
    }
    result = await files_collection.insert_one(new_file)
    return result.inserted_id
