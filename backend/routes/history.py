from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging

from page_handlers import (
    get_history_list,
    get_history_details,
    delete_history_item,
    clear_history
)
from auth.dependencies import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/sessions/history")
async def get_session_history(
    user_id: str = Depends(get_current_user_id),  # ✅ Auth required
    limit: int = 50
):
    """Get prompt generation history for authenticated user only"""
    try:
        # ✅ Always pass user_id to get only their history
        result = get_history_list(limit=limit, user_id=user_id)
        if result.get("success"):
            history_data = []
            for item in result.get("history", []):
                history_data.append({
                    "id": str(item["id"]),
                    "session_id": str(item["id"]),
                    "prompt_text": item["final_prompt"],
                    "category": item["category"],
                    "created_at": item["timestamp"],
                    "model_used": item["llm_used"] or "Unknown",
                    "word_count": len(item["final_prompt"].split()) if item["final_prompt"] else 0,
                })
            return {"success": True, "history": history_data}
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        logger.error(f"❌ Error in get_session_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/sessions/history/{prompt_id}")
async def get_history_item(
    prompt_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """Get details for a specific history item"""
    try:
        result = get_history_details(prompt_id, user_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/sessions/history/{prompt_id}")
async def delete_history_endpoint(
    prompt_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a history item"""
    try:
        result = delete_history_item(prompt_id, user_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/sessions/history/clear")
async def clear_all_history_endpoint(
    user_id: str = Depends(get_current_user_id)
):
    """Clear all history"""
    try:
        result = clear_history(user_id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to clear"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy routes
@router.get("/api/history")
async def get_history_legacy(
    user_id: str = Depends(get_current_user_id),
    limit: int = 50
):
    return await get_session_history(user_id, limit)

@router.get("/api/history/{prompt_id}")
async def get_history_item_legacy(
    prompt_id: int,
    user_id: str = Depends(get_current_user_id)
):
    return await get_history_item(prompt_id, user_id)

@router.delete("/api/history/{prompt_id}")
async def delete_history_legacy(
    prompt_id: int,
    user_id: str = Depends(get_current_user_id)
):
    return await delete_history_endpoint(prompt_id, user_id)

@router.delete("/api/history")
async def clear_all_history_legacy(
    user_id: str = Depends(get_current_user_id)
):
    return await clear_all_history_endpoint(user_id)
