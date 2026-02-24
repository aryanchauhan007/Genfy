from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from typing import List, Dict, Any
from pathlib import Path
import logging
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

# Import local utilities
from file_storage import save_upload_file, delete_file, UPLOAD_DIR
from vision_utils import analyze_image_with_openrouter
from memory_store import get_session # Using shared memory store for session data

router = APIRouter()
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/api/session/{session_id}/upload")
@limiter.limit("20/minute")  # ✅ Max 20 file uploads per minute
async def upload_file(request: Request, session_id: str, file: UploadFile = File(...)):
    """
    Upload a file to local storage (Rate limited: 20/min)
    Analysis will be triggered during prompt generation for context-awareness.
    """
    logger.info(f"📤 UPLOAD ENDPOINT CALLED - Session: {session_id}, File: {file.filename}")
    
    session = get_session(session_id)
    if not session:
        logger.error(f"❌ Session {session_id} not found!")
        raise HTTPException(status_code=404, detail="Session not found")
    
    logger.info(f"✅ Session found, current uploaded_files count: {len(session.get('uploaded_files', []))}")
        
    try:
        # 1. Save file locally
        logger.info(f"💾 Saving file to disk...")
        file_url = save_upload_file(file, session_id)
        logger.info(f"✅ File saved at: {file_url}")
        
        # 2. Add to session (metadata only, no analysis yet)
        if "uploaded_files" not in session:
            logger.info(f"📋 Initializing uploaded_files list in session")
            session["uploaded_files"] = []
            
        file_data = {
            "name": file.filename,
            "url": file_url,
            "uploaded_at": datetime.now().isoformat(),
            "type": file.content_type,
            "analyzed": False  # Flag to track if analysis has been done
        }
        
        session["uploaded_files"].append(file_data)
        logger.info(f"✅ File metadata added to session. Total files: {len(session['uploaded_files'])}")
        logger.info(f"📄 File data: {file_data}")
        
        return {
            "success": True,
            "url": file_url,
            "filename": file.filename,
            "message": "File uploaded successfully. Analysis will occur during prompt generation."
        }
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/session/{session_id}/files")
async def get_files(session_id: str):
    """Get all files for a session"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return {
        "success": True,
        "files": session.get("uploaded_files", [])
    }

@router.delete("/api/session/{session_id}/files/{file_index}")
async def delete_file_endpoint(session_id: str, file_index: int):
    """Delete a file by index"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    files = session.get("uploaded_files", [])
    if file_index < 0 or file_index >= len(files):
        raise HTTPException(status_code=404, detail="File index out of range")
        
    file_to_delete = files[file_index]
    file_url = file_to_delete["url"]
    
    # Delete from disk
    # We pass the URL path (e.g. /uploads/...) to delete_file
    delete_file(file_url)
    
    # Remove from session
    files.pop(file_index)
    session["uploaded_files"] = files
    
    # Remove from reference_analysis if present
    if "reference_analysis" in session:
        session["reference_analysis"] = [
            ref for ref in session["reference_analysis"] 
            if ref["filename"] != file_to_delete["name"]
        ]
        
    return {"success": True, "message": "File deleted"}

@router.get("/api/session/{session_id}/reference-context")
async def get_reference_context(session_id: str):
    """Get formatted reference analysis for prompt generation"""
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    references = session.get("reference_analysis", [])
    
    combined = ""
    if references:
        combined = "\n\n=== REFERENCE IMAGES ===\n\n"
        for idx, ref in enumerate(references, 1):
            combined += f"Reference {idx} ({ref['filename']}):\n"
            combined += f"{ref['analysis']}\n\n"
            
    return {
        "success": True,
        "references": references,
        "combined_context": combined
    }
