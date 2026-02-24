"""
FastAPI Backend for Image Generation Prompt Builder
REST API with session management and LLM integration
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import backend modules
from database import init_database
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
    refine_prompt_handler,
    get_history_list,
    get_history_details,
    delete_history_item,
    clear_history
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Image Generation Prompt Builder API",
    description="AI-powered image prompt generation with LLM support",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    logger.info("Database initialized")

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

# In-memory session storage (use Redis in production)
sessions: Dict[str, Dict[str, Any]] = {}

def get_session(session_id: str) -> Dict[str, Any]:
    """Get or create a session"""
    if session_id not in sessions:
        sessions[session_id] = {
            "current_step": "category",
            "user_idea": "",
            "selected_category": None,
            "selected_llm": "Claude",
            "answers_json": {},
            "messages": [],
            "conversation_step": 0,
            "selected_chips": [],
            "api_key_entered": True,
            "created_at": datetime.now().isoformat()
        }
    return sessions[session_id]

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SessionCreate(BaseModel):
    llm_provider: Optional[str] = "Claude"
    user_id: Optional[str] = None

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
    action: str = "toggle"  # "toggle", "add", or "remove"

class AnswerSubmit(BaseModel):
    answer: str

class PromptRefine(BaseModel):
    refinement_instruction: str

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Image Generation Prompt Builder API",
        "version": "1.0.0"
    }

# === SESSION ENDPOINTS ===

@app.post("/api/session/create")
async def create_session(data: SessionCreate):
    """Create a new session"""
    session_id = str(uuid.uuid4())
    session = get_session(session_id)
    session["selected_llm"] = data.llm_provider
    session["user_id"] = data.user_id # Save user_id to session
    
    return {
        "session_id": session_id,
        "llm_provider": data.llm_provider
    }

@app.get("/api/session/{session_id}")
async def get_session_data(session_id: str):
    """Get current session state"""
    session = get_session(session_id)
    return session

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"success": True, "message": "Session deleted"}
    raise HTTPException(status_code=404, detail="Session not found")

# === LLM ENDPOINTS ===

@app.get("/api/llms/available")
async def get_llms():
    """Get list of available LLMs"""
    available = get_available_llms()
    return {"llms": available}

class LLMUpdate(BaseModel):
    llm_provider: str

@app.post("/api/session/{session_id}/llm")
async def update_session_llm(session_id: str, data: LLMUpdate):
    """Update session LLM provider"""
    session = get_session(session_id)
    session["selected_llm"] = data.llm_provider
    return {"success": True, "llm_provider": data.llm_provider}

# === CATEGORY ENDPOINTS ===

@app.get("/api/categories")
async def get_categories():
    """Get all available categories"""
    categories = get_categories_data()
    return {"categories": categories}

@app.post("/api/categories/select/{session_id}")
async def select_category_endpoint(session_id: str, data: CategorySelect):
    """Select a category and save user idea"""
    session = get_session(session_id)
    
    result = select_category(data.category)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # ✅ Update session with category AND user_idea
    session["selected_category"] = data.category
    session["user_idea"] = data.user_idea  # ✅ This must be saved!
    session["current_step"] = "visual_settings"
    
    # ✅ Apply Default Settings to Session
    defaults = result.get("default_settings", {})
    if defaults:
        if defaults.get("color_palette"): session["selected_color_palette"] = defaults["color_palette"]
        if defaults.get("aspect_ratio"): session["selected_aspect_ratio"] = defaults["aspect_ratio"]
        if defaults.get("camera_settings"): session["selected_camera_settings"] = defaults["camera_settings"]
        if defaults.get("image_purpose"): session["selected_image_purpose"] = defaults["image_purpose"]
        logger.info(f"✅ Applied defaults for {data.category}: {defaults}")

    logger.info(f"✅ Session updated - Category: {data.category}, User Idea: {data.user_idea[:50]}")

    return {
        "success": True,
        "category": data.category,
        "questions": result["questions"]
    }

# === VISUAL SETTINGS ENDPOINTS ===

@app.get("/api/visual-settings/options")
async def get_visual_options():
    """Get all visual settings options"""
    options = get_visual_settings_options()
    return options

@app.post("/api/visual-settings/save/{session_id}")
async def save_settings(session_id: str, settings: VisualSettings):
    """Save visual settings"""
    session = get_session(session_id)
    
    settings_dict = settings.dict()
    save_visual_settings(session, settings_dict)
    
    return {
        "success": True,
        "settings": settings_dict
    }

@app.post("/api/visual-settings/generate-quick/{session_id}")
async def generate_quick(session_id: str):
    """Generate prompt quickly without Q&A"""
    session = get_session(session_id)
    
    try:
        client = get_llm_client(session["selected_llm"])
        result = generate_quick_prompt_handler(client, session)
        
        if result["success"]:
            session["current_step"] = "final_prompt"
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === CHAT ENDPOINTS ===

@app.post("/api/chat/start/{session_id}")
async def start_chat(session_id: str, data: ChatStart):
    """Start chat mode (advanced Q&A)"""
    session = get_session(session_id)
    
    # Save visual settings if provided
    if data.visual_settings:
        save_visual_settings(session, data.visual_settings.dict())
    
    # Initialize chat
    chat_session = initialize_chat_session(
        category=data.category,
        user_idea=data.user_idea,
        selected_llm=session["selected_llm"],
        visual_settings=data.visual_settings.dict() if data.visual_settings else None
    )
    
    # Update session
    session.update(chat_session)
    session["current_step"] = "chat"
    
    return {
        "success": True,
        "messages": session["messages"],
        "first_question": ask_next_question(session)
    }

@app.get("/api/chat/messages/{session_id}")
async def get_messages(session_id: str):
    """Get chat messages"""
    session = get_session(session_id)
    return {"messages": session.get("messages", [])}

@app.get("/api/chat/current-question/{session_id}")
async def get_current_question(session_id: str):
    """Get current question"""
    session = get_session(session_id)
    question = ask_next_question(session)
    
    if not question:
        return {"question": None, "is_complete": True}
    
    return {
        "question": question,
        "is_complete": False,
        "conversation_step": session.get("conversation_step", 0)
    }

# === SUGGESTION ENDPOINTS ===

@app.get("/api/suggestions/{session_id}")
async def get_suggestions(session_id: str, refresh: int = 0):
    """Get suggestions for current question"""
    session = get_session(session_id)
    
    current_q = ask_next_question(session)
    if not current_q:
        return {"suggestions": []}
    
    try:
        client = get_llm_client(session["selected_llm"])
        suggestions = get_suggestions_for_question(
            client,
            session,
            current_q,
            refresh_count=refresh
        )
        
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suggestions/toggle/{session_id}")
async def toggle_suggestion(session_id: str, data: SuggestionToggle):
    """Toggle suggestion selection"""
    session = get_session(session_id)
    
    selected = handle_suggestion_selection(
        session,
        data.suggestion,
        action=data.action
    )
    
    return {
        "success": True,
        "selected_suggestions": selected
    }

@app.get("/api/suggestions/selected/{session_id}")
async def get_selected_suggestions(session_id: str):
    """Get currently selected suggestions"""
    session = get_session(session_id)
    return {"selected": session.get("selected_chips", [])}

@app.delete("/api/suggestions/clear/{session_id}")
async def clear_suggestions(session_id: str):
    """Clear all selected suggestions"""
    session = get_session(session_id)
    session["selected_chips"] = []
    return {"success": True}

# === ANSWER ENDPOINTS ===

@app.post("/api/answer/submit/{session_id}")
async def submit_user_answer(session_id: str, data: AnswerSubmit):
    """Submit answer and move to next question"""
    session = get_session(session_id)
    
    try:
        client = get_llm_client(session["selected_llm"])
        result = submit_answer(client, session, data.answer)
        
        # If all questions answered, generate final prompt
        if result.get("should_generate_prompt"):
            prompt_result = generate_and_save_final_prompt(client, session)
            session["current_step"] = "final_prompt"
            return {
                **result,
                **prompt_result
            }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === PROMPT ENDPOINTS ===

@app.get("/api/prompt/final/{session_id}")
async def get_final_prompt(session_id: str):
    """Get final generated prompt"""
    session = get_session(session_id)
    prompt_data = get_final_prompt_data(session)
    return prompt_data

@app.post("/api/prompt/refine/{session_id}")
async def refine_prompt_endpoint(session_id: str, data: PromptRefine):
    """Refine the final prompt"""
    session = get_session(session_id)
    
    try:
        client = get_llm_client(session["selected_llm"])
        result = refine_prompt_handler(client, session, data.refinement_instruction)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HISTORY ENDPOINTS (UPDATED FOR FRONTEND COMPATIBILITY)
# ============================================================================

@app.post("/api/chat/skip/{session_id}")
async def skip_questions(session_id: str):
    """Skip remaining questions and generate prompt"""
    session = get_session(session_id)
    
    # Skip questions
    result = skip_remaining_questions(session)

    # Generate prompt immediately
    if result.get("should_generate_prompt"):
        try:
            client = get_llm_client(session.get("selected_llm", "Claude"))
            prompt_result = generate_and_save_final_prompt(client, session)
            session["current_step"] = "final_prompt"
            return {
                **result,
                **prompt_result
            }
        except Exception as e:
            logger.error(f"Error generating prompt during skip: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return result

@app.get("/api/sessions/history")
async def get_session_history(limit: int = 50, user_id: Optional[str] = None):
    """Get prompt generation history"""
    try:
        result = get_history_list(limit=limit, user_id=user_id)
        
        logger.info(f"📜 Fetching history, got {len(result.get('history', []))} items")
        
        # Transform the data to match frontend expectations
        if result.get("success"):
            history_data = []
            for item in result.get("history", []):
                history_data.append({
                    "id": str(item["id"]),
                    "session_id": str(item["id"]),
                    "prompt_text": item["final_prompt"],  # ✅ Map final_prompt to prompt_text
                    "category": item["category"],
                    "created_at": item["timestamp"],  # ✅ Map timestamp to created_at
                    "model_used": item["llm_used"] or "Unknown",
                    "word_count": len(item["final_prompt"].split()) if item["final_prompt"] else 0,
                })
            
            logger.info(f"✅ Returning {len(history_data)} history items")
            
            return {
                "success": True,
                "history": history_data
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
    except Exception as e:
        logger.error(f"❌ Error in get_session_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/history/{prompt_id}")
async def get_history_item(prompt_id: int):
    """Get details for a specific history item"""
    try:
        result = get_history_details(prompt_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
        return result
    except Exception as e:
        logger.error(f"❌ Error in get_history_item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/history/{prompt_id}")
async def delete_history_endpoint(prompt_id: int):
    """Delete a history item"""
    try:
        result = delete_history_item(prompt_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
        return result
    except Exception as e:
        logger.error(f"❌ Error in delete_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/history/clear")
async def clear_all_history_endpoint():
    """Clear all history"""
    try:
        result = clear_history()
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to clear"))
        return result
    except Exception as e:
        logger.error(f"❌ Error in clear_all_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === LEGACY HISTORY ENDPOINTS (for backward compatibility) ===

@app.get("/api/history")
async def get_history_legacy(limit: int = 50):
    """Legacy endpoint - redirects to new endpoint"""
    return await get_session_history(limit)

@app.get("/api/history/{prompt_id}")
async def get_history_item_legacy(prompt_id: int):
    """Legacy endpoint - redirects to new endpoint"""
    return await get_history_item(prompt_id)

@app.delete("/api/history/{prompt_id}")
async def delete_history_legacy(prompt_id: int):
    """Legacy endpoint - redirects to new endpoint"""
    return await delete_history_endpoint(prompt_id)

@app.delete("/api/history")
async def clear_all_history_legacy():
    """Legacy endpoint - redirects to new endpoint"""
    return await clear_all_history_endpoint()


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
