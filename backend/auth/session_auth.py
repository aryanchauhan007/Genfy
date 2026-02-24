from fastapi import HTTPException, status
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def verify_session_owner(session: Dict[str, Any], user_id: str, session_id: str) -> None:
    """
    Verify that the session belongs to the user, or allow claiming if anonymous.
    
    Args:
        session: The session dictionary
        user_id: The authenticated user ID
        session_id: The session ID (for logging)
        
    Raises:
        HTTPException: 403 Forbidden if owned by another user
    """
    current_owner = session.get("user_id")
    
    if current_owner and current_owner != user_id:
        logger.warning(f"❌ Access denied: User {user_id[:8]}... tried to access session {session_id[:8]} owned by {current_owner[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Session belongs to another user"
        )
    
    # If unowned, claim it
    if not current_owner:
        logger.info(f"👤 User {user_id[:8]}... claiming anonymous session {session_id[:8]}...")
        session["user_id"] = user_id
