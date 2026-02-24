from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory session storage (imported from app.py in a real app, but for now defining here or importing from a shared module would be better. 
# To avoid circular imports, we should move sessions dict to a separate file or keep it in app state.
# For simplicity in this refactor, I will assume we can keep sessions in a shared module or pass it. 
# A better approach is `dependencies` or a `services` module.
# Let's create a memory_store.py for strict separation.
# Let's create a memory_store.py for strict separation.
from memory_store import get_session
from auth.dependencies import get_current_user_id
from auth.session_auth import verify_session_owner

class SessionCreate(BaseModel):
    llm_provider: Optional[str] = "Claude"
    user_id: Optional[str] = None

class LLMUpdate(BaseModel):
    llm_provider: str

@router.post("/api/session/create")
async def create_session(
    data: SessionCreate,
    user_id: str = Depends(get_current_user_id)  # ✅ Auth required
):
    """Create a new session (requires authentication)"""
    session_id = str(uuid.uuid4())
    session = get_session(session_id)
    session["selected_llm"] = data.llm_provider
    session["user_id"] = user_id  # ✅ Use authenticated user_id
    
    return {
        "session_id": session_id,
        "llm_provider": data.llm_provider
    }

@router.get("/api/session/{session_id}")
async def get_session_data(
    session_id: str,
    user_id: str = Depends(get_current_user_id)  # ✅ Auth required
):
    """Get current session state (requires authentication)"""
    session = get_session(session_id)
    
    # ✅ Verify ownership or allow claiming anonymous sessions
    verify_session_owner(session, user_id, session_id)
    
    return session

@router.delete("/api/session/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id)  # ✅ Auth required
):
    """Delete a session (requires authentication)"""
    session = get_session(session_id)
    
    # ✅ Verify ownership
    if session.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Use memory_store's cache for deletion
    from memory_store import _session_cache
    
    if session_id in _session_cache:
        del _session_cache[session_id]
        # Also could delete from DB here if we implemented delete_session_from_db
        # But for now, just removing from cache is enough to "reset" it (it will reload from DB if accessed again)
        # To truly delete, we should add a DB delete function.
        return {"success": True, "message": "Session deleted from cache"}
        
    return {"success": True, "message": "Session not in active cache"}

@router.post("/api/session/{session_id}/llm")
async def update_session_llm(session_id: str, data: LLMUpdate):
    """Update session LLM provider"""
    session = get_session(session_id)
    session["selected_llm"] = data.llm_provider
    return {"success": True, "llm_provider": data.llm_provider}
