"""
Page Handler Functions
Backend business logic for different pages/views
No UI dependencies - Returns data for API endpoints
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import CATEGORIES, COLOR_PALETTES, ASPECT_RATIOS, CAMERA_SETTINGS, IMAGE_PURPOSE
from database import (
    get_prompt_history,
    get_prompt_details,
    delete_prompt_from_history,
    clear_all_history
)
from llm_utils import generate_quick_prompt, refine_prompt

logger = logging.getLogger(__name__)

# ============================================================================
# CATEGORY PAGE
# ============================================================================

def get_categories_data() -> List[Dict[str, Any]]:
    """
    Get all categories with their metadata
    
    Returns:
        List of category dictionaries with name, emoji, description, image_path
    """
    categories = []
    
    for cat_name, cat_data in CATEGORIES.items():
        categories.append({
            "name": cat_name,
            "key": cat_data.get("key"),
            "emoji": cat_data.get("emoji"),
            "description": cat_data.get("description"),
            "image_path": cat_data.get("image_path"),
            "color": cat_data.get("color"),
            "question_count": len(cat_data.get("questions", []))
        })
    
    return categories

def select_category(category_name: str) -> Dict[str, Any]:
    """
    Select a category and return its data
    
    Args:
        category_name: Name of the category to select
        
    Returns:
        Dictionary with category info and questions
    """
    if category_name not in CATEGORIES:
        return {
            "success": False,
            "error": f"Category '{category_name}' not found"
        }
    
    cat_data = CATEGORIES[category_name]
    
    return {
        "success": True,
        "category": category_name,
        "data": cat_data,
        "questions": cat_data.get("questions", [])
    }

# ============================================================================
# VISUAL SETTINGS PAGE
# ============================================================================

def get_visual_settings_options() -> Dict[str, Any]:
    """
    Get all available visual settings options
    
    Returns:
        Dictionary with color palettes, aspect ratios, camera settings, image purposes
    """
    return {
        "color_palettes": {name: details for name, details in COLOR_PALETTES.items()},
        "aspect_ratios": {name: details for name, details in ASPECT_RATIOS.items()},
        "camera_settings": {name: details for name, details in CAMERA_SETTINGS.items()},
        "image_purposes": {name: details for name, details in IMAGE_PURPOSE.items()}
    }

def save_visual_settings(session_data: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save visual settings to session
    
    Args:
        session_data: Session state dictionary
        settings: Dictionary with visual settings
        
    Returns:
        Updated session data
    """
    session_data["selected_color_palette"] = settings.get("color_palette")
    session_data["selected_aspect_ratio"] = settings.get("aspect_ratio")
    session_data["selected_camera_settings"] = settings.get("camera_settings")
    session_data["selected_image_purpose"] = settings.get("image_purpose")
    
    # Save details to answers_json
    if "answers_json" not in session_data:
        session_data["answers_json"] = {}
    
    if settings.get("color_palette"):
        session_data["answers_json"]["visual_color_palette"] = settings["color_palette"]
        session_data["answers_json"]["visual_color_details"] = ", ".join(
            COLOR_PALETTES.get(settings["color_palette"], [])
        )
    
    if settings.get("aspect_ratio"):
        session_data["answers_json"]["visual_aspect_ratio"] = settings["aspect_ratio"]
        session_data["answers_json"]["visual_aspect_details"] = ASPECT_RATIOS.get(
            settings["aspect_ratio"], ""
        )
    
    if settings.get("camera_settings"):
        session_data["answers_json"]["visual_camera_settings"] = settings["camera_settings"]
        session_data["answers_json"]["visual_camera_details"] = CAMERA_SETTINGS.get(
            settings["camera_settings"], ""
        )
    
    if settings.get("image_purpose"):
        session_data["answers_json"]["visual_image_purpose"] = settings["image_purpose"]
        session_data["answers_json"]["visual_image_purpose_details"] = IMAGE_PURPOSE.get(
            settings["image_purpose"], ""
        )
    
    return session_data

def generate_quick_prompt_handler(
    client,
    session_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate prompt quickly without Q&A
    
    Args:
        client: LLM client instance
        session_data: Session state dictionary
        
    Returns:
        Dictionary with generation result
    """
    user_idea = session_data.get("user_idea", "").strip()
    
    if not user_idea:
        return {
            "success": False,
            "error": "Please describe your image idea before continuing"
        }
    
    if not client:
        return {
            "success": False,
            "error": "LLM client not initialized"
        }
    
    try:
        final_prompt = generate_quick_prompt(client, session_data)
        
        if not final_prompt or final_prompt.strip() == "":
            return {
                "success": False,
                "error": "Generated prompt is empty"
            }
        
        # Save to session
        session_data["final_prompt"] = final_prompt
        session_data["current_step"] = "final_prompt"
        
        # Save to database
        from database import save_prompt_to_history
        timestamp = save_prompt_to_history(
            category=session_data.get("selected_category"),
            user_idea=session_data.get("user_idea"),
            llm_used=session_data.get("selected_llm"),
            answers_json=session_data.get("answers_json", {}),
            final_prompt=final_prompt,
            visual_settings={
                "color_palette": session_data.get("selected_color_palette"),
                "aspect_ratio": session_data.get("selected_aspect_ratio"),
                "camera_settings": session_data.get("selected_camera_settings"),
                "image_purpose": session_data.get("selected_image_purpose")
            }
        )
        
        return {
            "success": True,
            "final_prompt": final_prompt,
            "timestamp": timestamp
        }
        
    except Exception as e:
        error_msg = f"Error generating quick prompt: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

# ============================================================================
# FINAL PROMPT PAGE
# ============================================================================

def get_final_prompt_data(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get final prompt and metadata for display
    
    Args:
        session_data: Session state dictionary
        
    Returns:
        Dictionary with prompt and metadata
    """
    return {
        "final_prompt": session_data.get("final_prompt", ""),
        "category": session_data.get("selected_category"),
        "llm_used": session_data.get("selected_llm"),
        "user_idea": session_data.get("user_idea"),
        "visual_settings": {
            "color_palette": session_data.get("selected_color_palette"),
            "aspect_ratio": session_data.get("selected_aspect_ratio"),
            "camera_settings": session_data.get("selected_camera_settings"),
            "image_purpose": session_data.get("selected_image_purpose")
        },
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# ============================================================================
# REFINEMENT PAGE
# ============================================================================

def refine_prompt_handler(
    client,
    session_data: Dict[str, Any],
    refinement_instruction: str
) -> Dict[str, Any]:
    """
    Refine the final prompt based on user feedback
    
    Args:
        client: LLM client instance
        session_data: Session state dictionary
        refinement_instruction: User's refinement request
        
    Returns:
        Dictionary with refined prompt or error
    """
    if not refinement_instruction or not refinement_instruction.strip():
        return {
            "success": False,
            "error": "Please enter what you want to change"
        }
    
    try:
        refined_prompt = refine_prompt(client, session_data, refinement_instruction)
        
        if not refined_prompt or refined_prompt.strip() == "":
            return {
                "success": False,
                "error": "Refined prompt is empty"
            }
        
        # Update session
        session_data["final_prompt"] = refined_prompt
        
        return {
            "success": True,
            "refined_prompt": refined_prompt
        }
        
    except Exception as e:
        error_msg = f"Error refining prompt: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

# ============================================================================
# HISTORY PAGE
# ============================================================================

def get_history_list(limit: int = 50) -> Dict[str, Any]:
    """
    Get prompt generation history
    
    Args:
        limit: Maximum number of records to retrieve
        
    Returns:
        Dictionary with history records
    """
    try:
        history = get_prompt_history(limit=limit)
        
        # Convert to list of dicts
        history_list = []
        for record in history:
            prompt_id, timestamp, category, user_idea, llm_used, final_prompt = record
            
            # Truncate idea for preview
            idea_preview = user_idea[:100] + "..." if len(user_idea) > 100 else user_idea
            
            history_list.append({
                "id": prompt_id,
                "timestamp": timestamp,
                "category": category,
                "user_idea": user_idea,
                "idea_preview": idea_preview,
                "llm_used": llm_used,
                "final_prompt": final_prompt
            })
        
        return {
            "success": True,
            "total": len(history_list),
            "history": history_list
        }
        
    except Exception as e:
        error_msg = f"Error retrieving history: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def get_history_details(prompt_id: int) -> Dict[str, Any]:
    """
    Get detailed information for a specific prompt
    
    Args:
        prompt_id: ID of the prompt
        
    Returns:
        Dictionary with full prompt details
    """
    try:
        details = get_prompt_details(prompt_id)
        
        if not details:
            return {
                "success": False,
                "error": "Prompt not found"
            }
        
        # Unpack the tuple
        (prompt_id, timestamp, category, user_idea, llm_used, 
         answers_json, final_prompt, visual_settings) = details
        
        # Parse JSON strings
        try:
            answers = json.loads(answers_json) if answers_json else {}
            visual = json.loads(visual_settings) if visual_settings else {}
        except:
            answers = {}
            visual = {}
        
        return {
            "success": True,
            "id": prompt_id,
            "timestamp": timestamp,
            "category": category,
            "user_idea": user_idea,
            "llm_used": llm_used,
            "answers": answers,
            "visual_settings": visual,
            "final_prompt": final_prompt
        }
        
    except Exception as e:
        error_msg = f"Error retrieving prompt details: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def delete_history_item(prompt_id: int) -> Dict[str, Any]:
    """
    Delete a prompt from history
    
    Args:
        prompt_id: ID of the prompt to delete
        
    Returns:
        Dictionary with deletion status
    """
    try:
        success = delete_prompt_from_history(prompt_id)
        
        if success:
            return {
                "success": True,
                "message": "Prompt deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": "Prompt not found"
            }
            
    except Exception as e:
        error_msg = f"Error deleting prompt: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def clear_history() -> Dict[str, Any]:
    """
    Clear all prompt history
    
    Returns:
        Dictionary with clear status
    """
    try:
        success = clear_all_history()
        
        if success:
            return {
                "success": True,
                "message": "History cleared successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to clear history"
            }
            
    except Exception as e:
        error_msg = f"Error clearing history: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
