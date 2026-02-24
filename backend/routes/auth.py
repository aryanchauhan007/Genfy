from fastapi import APIRouter, HTTPException, Response, Depends, Request
from pydantic import BaseModel, EmailStr
from uuid import uuid4
import hashlib
from database import create_user, get_user_by_email
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address
from auth.dependencies import get_current_user_id

router = APIRouter()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

class UserSignup(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    """Hash password using SHA-256 (Simple implementation for dev)"""
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/api/auth/signup")
@limiter.limit("5/hour")  # ✅ Max 5 signups per hour per IP
async def signup(request: Request, user: UserSignup):
    """Register a new user (Rate limited: 5/hour)"""
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_id = str(uuid4())
    password_hash = hash_password(user.password)
    
    success = create_user(user_id, user.email, password_hash)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user")
        
    return {
        "id": user_id,
        "email": user.email,
        "created_at": datetime.now().isoformat()
    }

@router.post("/api/auth/login")
@limiter.limit("10/minute")  # ✅ Max 10 login attempts per minute
async def login(request: Request, user: UserLogin):
    """Login user (Rate limited: 10/min - prevents brute force)"""
    db_user = get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if db_user["password_hash"] != hash_password(user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
        
    return {
        "user": {
            "id": db_user["id"],
            "email": db_user["email"]
        },
        "session": {
            "access_token": "mock-token-for-local-dev", # For this migration, we rely on client-side state or mocked token
            "token_type": "bearer",
            "expires_in": 3600
        }
    }

@router.post("/api/auth/logout")
async def logout():
    """Logout user"""
    return {"success": True}

@router.get("/api/users/me")
async def get_current_user_profile(
    user_id: str = Depends(get_current_user_id)  # ✅ Auth required
):
    """Get current user profile (resolves 404 error)"""
    from database import get_user_by_id
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "id": user["id"],
        "email": user["email"],
        # Add other profile fields if needed
    }
