import os
import shutil
from pathlib import Path
from fastapi import UploadFile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")

def init_storage():
    """Initialize upload directory"""
    if not UPLOAD_DIR.exists():
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created upload directory: {UPLOAD_DIR.absolute()}")

def save_upload_file(file: UploadFile, session_id: str) -> str:
    """
    Save uploaded file to local storage
    Returns: relative URL path to file
    """
    init_storage()
    
    # Create session-specific directory
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        session_dir.mkdir(parents=True, exist_ok=True)
        
    # Generate safe filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = session_dir / safe_filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return relative path for static serving
        # We will serve 'uploads' directory at /uploads
        return f"/uploads/{session_id}/{safe_filename}"
        
    except Exception as e:
        logger.error(f"Error saving file {file.filename}: {e}")
        raise e

def delete_file(file_url: str) -> bool:
    """
    Delete file from local storage
    file_url expected format: /uploads/{session_id}/{filename}
    """
    try:
        # Strip leading /uploads/ to get relative path
        if file_url.startswith("/uploads/"):
            rel_path = file_url.replace("/uploads/", "", 1)
        else:
            rel_path = file_url.lstrip("/")
            
        file_path = UPLOAD_DIR / rel_path
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting file {file_url}: {e}")
        return False
