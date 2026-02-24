"""
Page Handler Functions
Backend business logic for different pages/views
No UI dependencies - Returns data for API endpoints
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import CATEGORY_DEFAULT_SETTINGS, CATEGORIES, COLOR_PALETTES, ASPECT_RATIOS, CAMERA_SETTINGS, IMAGE_PURPOSE
from database import (
    get_prompt_history,
    get_prompt_details,
    delete_prompt_from_history,
    clear_all_history_for_user,
    save_prompt_to_history
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

def select_category(category: str) -> Dict[str, Any]:
    """Select a category and get its questions"""
    if category not in CATEGORIES:
        return {"success": False, "error": f"Category '{category}' not found"}
    
    cat_data = CATEGORIES[category]
    questions = cat_data.get("questions", [])
    
    logger.info(f"✅ Selected category: {category} with {len(questions)} questions")
    
    # ✅ Get Default Visual Settings
    defaults = CATEGORY_DEFAULT_SETTINGS.get(category, {})

    return {
        "success": True,
        "category": category,
        "questions": [q["id"] for q in questions],
        "question_details": questions,
        "default_settings": defaults
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
    # Update session settings
    if "color_palette" in settings and settings["color_palette"]:
        session_data["selected_color_palette"] = settings["color_palette"]
    
    if "aspect_ratio" in settings and settings["aspect_ratio"]:
        session_data["selected_aspect_ratio"] = settings["aspect_ratio"]
    
    if "camera_settings" in settings and settings["camera_settings"]:
        session_data["selected_camera_settings"] = settings["camera_settings"]
    
    if "image_purpose" in settings and settings["image_purpose"]:
        session_data["selected_image_purpose"] = settings["image_purpose"]
    
    # ✅ Initialize answers_json if not exists
    if "answers_json" not in session_data:
        session_data["answers_json"] = {}
    
    # ✅ Save visual settings to answers_json
    if settings.get("color_palette"):
        session_data["answers_json"]["visual_color_palette"] = settings["color_palette"]
        color_details = COLOR_PALETTES.get(settings["color_palette"], [])
        if isinstance(color_details, list):
            session_data["answers_json"]["visual_color_details"] = ", ".join(color_details)
        else:
            session_data["answers_json"]["visual_color_details"] = str(color_details)
    
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
    
    logger.info(f"✅ Visual settings saved to session")
    
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
    category = session_data.get("selected_category", "")
    
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
        # ✅ Initialize answers_json if not exists
        if "answers_json" not in session_data or not session_data["answers_json"]:
            session_data["answers_json"] = {}
        
        # ✅ Map user_idea to the correct field based on category
        category_field_mapping = {
            "Realistic Photo": "subject",
            "Stylized Art": "subject",
            "Logo/Text Design": "text",
            "Product Shot": "product",
            "Minimalist": "focus",
            "Sequential Art": "scene",
            "Conceptual/Abstract": "concept"
        }
        
        primary_field = category_field_mapping.get(category, "subject")
        session_data["answers_json"][primary_field] = user_idea
        
        logger.info(f"✅ Mapped user_idea to field '{primary_field}': {user_idea[:50]}")
        
        # ✅ CONTEXT-AWARE VISION ANALYSIS (if files uploaded but not analyzed)
        uploaded_files = session_data.get("uploaded_files", [])
        logger.info(f"📁 Checking for uploaded files... Found: {len(uploaded_files)}")
        
        if uploaded_files:
            # Check if any files need analysis
            unanalyzed_files = [f for f in uploaded_files if not f.get("analyzed", False)]
            logger.info(f"🔍 Unanalyzed files: {len(unanalyzed_files)} out of {len(uploaded_files)}")
            
            if unanalyzed_files:
                logger.info(f"🎯 Triggering context-aware analysis for {len(unanalyzed_files)} file(s)")
                logger.info(f"📋 User idea: {user_idea}")
                logger.info(f"📋 Category: {category}")
                
                # Import vision utilities
                from vision_utils import determine_focus_areas, analyze_image_with_openrouter
                from pathlib import Path
                
                # Step 1: Determine what aspects to focus on
                focus_result = determine_focus_areas(user_idea, category)
                focus_areas = focus_result.get("focus_areas", [])
                
                logger.info(f"📋 Focus areas: {focus_areas} - {focus_result.get('reasoning', '')}")
                
                # Step 2: Analyze each unanalyzed file with focused prompt
                if "reference_analysis" not in session_data:
                    session_data["reference_analysis"] = []
                
                for file_data in unanalyzed_files:
                    if file_data.get("type", "").startswith("image/"):
                        file_url = file_data["url"]
                        
                        # Construct path
                        relative_path = file_url.lstrip("/")
                        absolute_path = Path.cwd() / relative_path
                        
                        logger.info(f"🔍 Analyzing {file_data['name']} with focus: {focus_areas}")
                        
                        analysis_result = analyze_image_with_openrouter(
                            str(absolute_path),
                            user_context=user_idea,
                            focus_areas=focus_areas
                        )
                        
                        if analysis_result.get("success"):
                            file_data["vision_analysis"] = analysis_result["analysis"]
                            file_data["analyzed_by"] = analysis_result["model"]
                            file_data["focus_areas"] = focus_areas
                            file_data["analyzed"] = True
                            
                            session_data["reference_analysis"].append({
                                "filename": file_data["name"],
                                "analysis": analysis_result["analysis"],
                                "focus_areas": focus_areas,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            logger.info(f"✅ Analysis complete for {file_data['name']}")
                        else:
                            logger.warning(f"⚠️ Analysis failed for {file_data['name']}: {analysis_result.get('error')}")
                            file_data["analysis_error"] = analysis_result.get("error")
        
        # Generate the prompt (now with context-aware image analysis if available)
        final_prompt = generate_quick_prompt(client, session_data)
        
        if not final_prompt or final_prompt.strip() == "":
            return {
                "success": False,
                "error": "Generated prompt is empty"
            }
        
        # Save to session
        session_data["final_prompt"] = final_prompt
        session_data["current_step"] = "final_prompt"

        # ✅ Apply default visual settings if not set
        defaults = CATEGORY_DEFAULT_SETTINGS.get(category, {})
        
        current_palette = session_data.get("selected_color_palette")
        current_aspect = session_data.get("selected_aspect_ratio")
        current_camera = session_data.get("selected_camera_settings")
        current_purpose = session_data.get("selected_image_purpose")

        # Auto-fill defaults if missing
        final_palette = current_palette if current_palette else defaults.get("color_palette")
        final_aspect = current_aspect if current_aspect else defaults.get("aspect_ratio")
        final_camera = current_camera if current_camera else defaults.get("camera_settings")
        final_purpose = current_purpose if current_purpose else defaults.get("image_purpose")

        # Update session with defaults for consistency
        if not current_palette and final_palette: session_data["selected_color_palette"] = final_palette
        if not current_aspect and final_aspect: session_data["selected_aspect_ratio"] = final_aspect
        if not current_camera and final_camera: session_data["selected_camera_settings"] = final_camera
        if not current_purpose and final_purpose: session_data["selected_image_purpose"] = final_purpose
        
        # ✅ Save to database with complete answers_json
        timestamp = save_prompt_to_history(
            category=category,
            user_idea=user_idea,
            llm_used=session_data.get("selected_llm"),
            answers_json=session_data.get("answers_json", {}),
            final_prompt=final_prompt,
            visual_settings={
                "color_palette": final_palette,
                "aspect_ratio": final_aspect,
                "camera_settings": final_camera,
                "image_purpose": final_purpose
            },
            user_id=session_data.get("user_id")  # ✅ Pass user_id as positional arg
        )
        
        logger.info(f"✅ Quick prompt generated and saved: {final_prompt[:50]}...")
        
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
        "answers": session_data.get("answers_json", {}),
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

def get_history_list(limit: int = 50, user_id: str = None) -> Dict[str, Any]:
    """
    Get prompt generation history
    
    Args:
        limit: Maximum number of records to retrieve
        user_id: Optional user ID to filter by
        
    Returns:
        Dictionary with history records
    """
    try:
        history = get_prompt_history(limit=limit, user_id=user_id)
        
        # Convert to list of dicts
        history_list = []
        for record in history:
            # record is now a dictionary
            prompt_id = record["id"]
            timestamp = record["timestamp"]
            category = record["category"]
            user_idea = record["user_idea"]
            llm_used = record["llm_used"]
            final_prompt = record["final_prompt"]
            generated_image_url = record["generated_image_url"]
            # files_json = record.get("files_json", []) # Available if needed
            
            # Truncate idea for preview
            idea_preview = user_idea[:100] + "..." if len(user_idea) > 100 else user_idea
            
            history_list.append({
                "id": prompt_id,
                "timestamp": timestamp,
                "category": category,
                "user_idea": user_idea,
                "idea_preview": idea_preview,
                "llm_used": llm_used,
                "final_prompt": final_prompt,
                "generated_image_url": generated_image_url
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

def get_history_details(prompt_id: int, user_id: str = None) -> Dict[str, Any]:
    """
    Get detailed information for a specific prompt
    
    Args:
        prompt_id: ID of the prompt
        user_id: REQUIRED - User who owns this prompt
        
    Returns:
        Dictionary with full prompt details
    """
    if not user_id:
        return {"success": False, "error": "user_id is required"}
        
    try:
        details = get_prompt_details(prompt_id, user_id)
        
        if not details:
            return {
                "success": False,
                "error": "Prompt not found"
            }
        
        # Unpack the tuple (Supabase returns parsed JSON already)
        # Updated to include files_json (10 items)
        (prompt_id, timestamp, category, user_idea, llm_used, 
         answers_json, final_prompt, visual_settings, generated_image_url, files_json) = details
        
        # Supabase returns dicts directly, no need to parse
        answers = answers_json if isinstance(answers_json, dict) else {}
        visual = visual_settings if isinstance(visual_settings, dict) else {}
        files = files_json if isinstance(files_json, list) else []
        
        return {
            "success": True,
            "id": prompt_id,
            "timestamp": timestamp,
            "category": category,
            "user_idea": user_idea,
            "llm_used": llm_used,
            "answers": answers,
            "visual_settings": visual,
            "final_prompt": final_prompt,
            "generated_image_url": generated_image_url,
            "files": files
        }
        
    except Exception as e:
        error_msg = f"Error retrieving prompt details: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def delete_history_item(prompt_id: int, user_id: str = None) -> Dict[str, Any]:
    """
    Delete a prompt from history
    
    Args:
        prompt_id: ID of the prompt to delete
        user_id: REQUIRED - User who owns this prompt
        
    Returns:
        Dictionary with deletion status
    """
    if not user_id:
        return {"success": False, "error": "user_id is required"}
        
    try:
        success = delete_prompt_from_history(prompt_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": "Prompt deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": "Prompt not found or access denied"
            }
            
    except Exception as e:
        error_msg = f"Error deleting prompt: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

def clear_history(user_id: str = None) -> Dict[str, Any]:
    """
    Clear all prompt history for a user
    
    Args:
        user_id: REQUIRED - User who owns the history
        
    Returns:
        Dictionary with clear status
    """
    if not user_id:
        return {"success": False, "error": "user_id is required"}
        
    try:
        success = clear_all_history_for_user(user_id)
        
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
