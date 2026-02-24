"""
Authentication and Authorization Dependencies for FastAPI
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Extract and validate user_id from request
    
    For now, expects user_id in Authorization header: "Bearer {user_id}"
    TODO: Replace with JWT token validation
    
    Args:
        authorization: Authorization header value
        
    Returns:
        user_id string
        
    Raises:
        HTTPException: If authorization invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        # Simple Bearer token parsing
        # Format: "Bearer user_id"
        scheme, credentials = authorization.split()
        
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        user_id = credentials
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID"
            )
        
        logger.info(f"✅ Authenticated user: {user_id[:8]}...")
        return user_id
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

async def get_current_user(
    user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Get full user object from user_id
    
    Args:
        user_id: User ID from authentication
        
    Returns:
        User dictionary
    """
    from database import get_user_by_id
    
    user = get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
