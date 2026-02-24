"""
FastAPI Backend for Image Generation Prompt Builder
REST API with session management and LLM integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import backend modules
from database import init_database
# Import routers
from routes import session, chat, history

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

# ✅ Rate Limiter Setup (protects against API abuse)
limiter = Limiter(key_func=get_remote_address)

# Initialize database on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    logger.info("Database initialized")
    yield

# Initialize FastAPI app
app = FastAPI(
    title="Image Generation Prompt Builder API",
    description="AI-powered image prompt generation with LLM support",
    version="1.0.0",
    lifespan=lifespan
)

# ✅ Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware for frontend
# ✅ Security Fix: Only allow specific origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",       # Local development
    "http://localhost:3001",
    "http://localhost:3002",
    "http://10.5.51.146:3000",     # Old Network access
    "http://10.5.51.146:3001",
    "http://10.5.51.146:3002",
    "http://10.5.50.135:3000",     # New Network access
    "http://10.5.50.135:3001",
    "http://10.5.50.135:3002",
    os.getenv("FRONTEND_URL", ""), # Production/custom frontend URL
]

# Filter out empty strings
ALLOWED_ORIGINS = [origin for origin in ALLOWED_ORIGINS if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ Specific origins only (was "*")
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include Routers
# Include Routers
app.include_router(session.router)
app.include_router(chat.router)
app.include_router(history.router)
from routes import auth, files
app.include_router(auth.router)
app.include_router(files.router)

from fastapi.staticfiles import StaticFiles
import os

# Mount static files for uploads
# Ensure uploads directory exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")
    
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Image Generation Prompt Builder API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    # Exclude database, cache, and upload files from triggering reload
    # This prevents the server from restarting when these files change
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_excludes=["*.db", "*.db-*", "uploads/*", "__pycache__/*", "*.pyc"]
    )
