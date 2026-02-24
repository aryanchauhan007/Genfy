from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional, List
from pydantic import BaseModel
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

from memory_store import get_session
from auth.dependencies import get_current_user_id
from auth.session_auth import verify_session_owner
from llm_utils import get_llm_client, get_available_llms
from chat_handler import (
    initialize_chat_session,
    ask_next_question,
    get_suggestions_for_question,
    handle_suggestion_selection,
    submit_answer,
    generate_and_save_final_prompt,
    skip_remaining_questions
)
from page_handlers import (
    get_categories_data,
    select_category,
    get_visual_settings_options,
    save_visual_settings,
    generate_quick_prompt_handler,
    get_final_prompt_data,
    refine_prompt_handler
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Models
class CategorySelect(BaseModel):
    category: str
    user_idea: str

class VisualSettings(BaseModel):
    color_palette: Optional[str] = None
    aspect_ratio: Optional[str] = None
    camera_settings: Optional[str] = None
    image_purpose: Optional[str] = None

class ChatStart(BaseModel):
    category: str
    user_idea: str
    visual_settings: Optional[VisualSettings] = None

class SuggestionRefresh(BaseModel):
    refresh_count: int = 0

class SuggestionToggle(BaseModel):
    suggestion: str
    action: str = "toggle"

class AnswerSubmit(BaseModel):
    answer: str

class PromptRefine(BaseModel):
    refinement_instruction: str

# Endpoints

@router.get("/api/llms/available")
async def get_llms():
    """Get list of available LLMs"""
    available = get_available_llms()
    return {"llms": available}

@router.get("/api/categories")
async def get_categories():
    """Get all available categories"""
    categories = get_categories_data()
    return {"categories": categories}

@router.post("/api/categories/select/{session_id}")
async def select_category_endpoint(
    session_id: str, 
    data: CategorySelect,
    user_id: str = Depends(get_current_user_id)  # ✅ Auth required
):
    """Select a category and save user idea"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    
    result = select_category(data.category)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    session["selected_category"] = data.category
    session["user_idea"] = data.user_idea
    session["current_step"] = "visual_settings"
    
    defaults = result.get("default_settings", {})
    if defaults:
        if defaults.get("color_palette"): session["selected_color_palette"] = defaults["color_palette"]
        if defaults.get("aspect_ratio"): session["selected_aspect_ratio"] = defaults["aspect_ratio"]
        if defaults.get("camera_settings"): session["selected_camera_settings"] = defaults["camera_settings"]
        if defaults.get("image_purpose"): session["selected_image_purpose"] = defaults["image_purpose"]

    return {
        "success": True,
        "category": data.category,
        "questions": result["questions"]
    }

@router.get("/api/visual-settings/options")
async def get_visual_options():
    """Get all visual settings options"""
    options = get_visual_settings_options()
    return options

@router.post("/api/visual-settings/save/{session_id}")
async def save_settings(
    session_id: str, 
    settings: VisualSettings,
    user_id: str = Depends(get_current_user_id)  # ✅ Auth required
):
    """Save visual settings"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
        
    settings_dict = settings.dict()
    save_visual_settings(session, settings_dict)
    return {"success": True, "settings": settings_dict}

@router.post("/api/visual-settings/generate-quick/{session_id}")
@limiter.limit("10/minute")  # ✅ Max 10 prompts per minute
async def generate_quick(
    request: Request, 
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Generate prompt quickly without Q&A (Rate limited: 10/min)"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    try:
        client = get_llm_client(session["selected_llm"])
        result = generate_quick_prompt_handler(client, session)
        if result["success"]:
            session["current_step"] = "final_prompt"
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat/start/{session_id}")
async def start_chat(
    session_id: str, 
    data: ChatStart,
    user_id: str = Depends(get_current_user_id)  # ✅ Auth required
):
    """Start chat mode (advanced Q&A)"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
        
    if data.visual_settings:
        save_visual_settings(session, data.visual_settings.dict())
    
    chat_session = initialize_chat_session(
        category=data.category,
        user_idea=data.user_idea,
        selected_llm=session["selected_llm"],
        visual_settings=data.visual_settings.dict() if data.visual_settings else None
    )
    session.update(chat_session)
    session["current_step"] = "chat"
    
    return {
        "success": True,
        "messages": session["messages"],
        "first_question": ask_next_question(session)
    }

@router.get("/api/chat/messages/{session_id}")
async def get_messages(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get chat messages"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    return {"messages": session.get("messages", [])}

@router.get("/api/chat/current-question/{session_id}")
async def get_current_question(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get current question"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    question = ask_next_question(session)
    if not question:
        return {"question": None, "is_complete": True}
    return {
        "question": question,
        "is_complete": False,
        "conversation_step": session.get("conversation_step", 0)
    }

@router.post("/api/chat/skip/{session_id}")
async def skip_questions(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Skip remaining questions and generate prompt"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    result = skip_remaining_questions(session)

    if result.get("should_generate_prompt"):
        try:
            client = get_llm_client(session.get("selected_llm", "Claude"))
            prompt_result = generate_and_save_final_prompt(client, session)
            session["current_step"] = "final_prompt"
            return {**result, **prompt_result}
        except Exception as e:
            logger.error(f"Error generating prompt during skip: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    return result

@router.get("/api/suggestions/{session_id}")
async def get_suggestions(
    session_id: str, 
    refresh: int = 0,
    user_id: str = Depends(get_current_user_id)
):
    """Get suggestions for current question"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    current_q = ask_next_question(session)
    if not current_q:
        return {"suggestions": []}
    try:
        client = get_llm_client(session["selected_llm"])
        suggestions = get_suggestions_for_question(client, session, current_q, refresh_count=refresh)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/suggestions/toggle/{session_id}")
async def toggle_suggestion(
    session_id: str, 
    data: SuggestionToggle,
    user_id: str = Depends(get_current_user_id)
):
    """Toggle suggestion selection"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    selected = handle_suggestion_selection(session, data.suggestion, action=data.action)
    return {"success": True, "selected_suggestions": selected}

@router.get("/api/suggestions/selected/{session_id}")
async def get_selected_suggestions(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get currently selected suggestions"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    return {"selected": session.get("selected_chips", [])}

@router.delete("/api/suggestions/clear/{session_id}")
async def clear_suggestions(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Clear all selected suggestions"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    session["selected_chips"] = []
    return {"success": True}

@router.post("/api/answer/submit/{session_id}")
async def submit_user_answer(
    session_id: str, 
    data: AnswerSubmit,
    user_id: str = Depends(get_current_user_id)
):
    """Submit answer and move to next question"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    try:
        client = get_llm_client(session["selected_llm"])
        result = submit_answer(client, session, data.answer)
        if result.get("should_generate_prompt"):
            prompt_result = generate_and_save_final_prompt(client, session)
            session["current_step"] = "final_prompt"
            return {**result, **prompt_result}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/prompt/final/{session_id}")
async def get_final_prompt(
    session_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get final generated prompt"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    prompt_data = get_final_prompt_data(session)
    
    # DEBUG: Log what we're returning
    logger.info(f"📤 Returning final_prompt API response:")
    logger.info(f"   - final_prompt length: {len(prompt_data.get('final_prompt', ''))}")
    logger.info(f"   - final_prompt preview: {prompt_data.get('final_prompt', '')[:100]}...")
    logger.info(f"   - All keys: {list(prompt_data.keys())}")
    
    return prompt_data

@router.post("/api/prompt/refine/{session_id}")
@limiter.limit("5/minute")  # ✅ Max 5 refinements per minute
async def refine_prompt_endpoint(
    request: Request, 
    session_id: str, 
    data: PromptRefine,
    user_id: str = Depends(get_current_user_id)
):
    """Refine the final prompt (Rate limited: 5/min)"""
    session = get_session(session_id)
    verify_session_owner(session, user_id, session_id)
    try:
        client = get_llm_client(session["selected_llm"])
        result = refine_prompt_handler(client, session, data.refinement_instruction)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
