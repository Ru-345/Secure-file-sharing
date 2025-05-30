import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
SECRET_KEY = "your_very_secret_key"  # Use a secure, random key for production
ALGORITHM = "HS256"
UPLOAD_DIR = "app/uploads"  # Add this if you're using upload paths too

# Make sure the folder exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
