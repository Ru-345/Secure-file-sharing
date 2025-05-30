from fastapi import FastAPI
from app.routes import auth, client, ops, files, ui  # Your route modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import Base  # Your User model Base
from app.database import  create_tables, engine
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


DATABASE_URL = "sqlite:///./test.db"  # SQLite DB URL

# Setup SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create FastAPI app with metadata
app = FastAPI(
    title="Secure File Sharing API",
    description="REST API for a secure file-sharing system with client and ops users.",
    version="1.0.0"
)
app.include_router(files.router)

templates = Jinja2Templates(directory="app/templates")

# Create tables at startup event
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include your routers with prefixes and tags
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ops.router, prefix="/ops", tags=["ops"])
app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(files.router, prefix="/files", tags=["files"])
app.include_router(files.router)
app.include_router(ui.router)  # UI routes (login/upload pages)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Secure File Sharing API"}
