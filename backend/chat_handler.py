"""
Chat handling module for interactive Q&A
Backend business logic - No UI dependencies
Manages chat flow, suggestions, and final prompt generation
"""

import logging
from typing import Dict, List, Any, Optional
from config import CATEGORIES
from llm_utils import generate_suggestions, generate_final_prompt
from database import save_prompt_to_history

logger = logging.getLogger(__name__)

# ============================================================================
# SESSION HELPER FUNCTIONS
# ============================================================================

def ask_next_question(session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get the next question in conversational flow
    
    Args:
        session_data: Dictionary containing session state
        
    Returns:
        Question dictionary or None if no more questions
    """
    selected_category = session_data.get("selected_category")
    if not selected_category:
        return None
    
    cat_data = CATEGORIES.get(selected_category)
    if not cat_data:
        return None
    
    questions = cat_data["questions"]
    conversation_step = session_data.get("conversation_step", 0)
    
    if conversation_step < len(questions):
        return questions[conversation_step]
    
    return None

def get_chat_messages(session_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Get all chat messages from session
    
    Args:
        session_data: Dictionary containing session state
        
    Returns:
        List of message dictionaries with 'role' and 'content'
    """
    return session_data.get("messages", [])

def add_chat_message(
    session_data: Dict[str, Any],
    role: str,
    content: str
) -> None:
    """
    Add a message to the chat history
    
    Args:
        session_data: Dictionary containing session state
        role: Message role ("user" or "assistant")
        content: Message content
    """
    if "messages" not in session_data:
        session_data["messages"] = []
    
    session_data["messages"].append({
        "role": role,
        "content": content
    })

# ============================================================================
# SUGGESTION HANDLING
# ============================================================================

def get_suggestions_for_question(
    client,
    session_data: Dict[str, Any],
    question: Dict[str, Any],
    refresh_count: int = 0
) -> List[str]:
    """
    Get or generate suggestions for a specific question
    
    Args:
        client: LLM client instance
        session_data: Dictionary containing session state
        question: Question dictionary
        refresh_count: Number of times refreshed
        
    Returns:
        List of suggestion strings
    """
    question_id = question["id"]
    cache_key = f"sugg_{question_id}"
    
    # Check cache first (if refresh_count is 0)
    if refresh_count == 0 and cache_key in session_data:
        return session_data[cache_key]
    
    # Generate new suggestions
    conversation_step = session_data.get("conversation_step", 0)
    
    try:
        suggestions = generate_suggestions(
            client,
            session_data,
            question,
            conversation_step,
            current_input="",
            refresh_count=refresh_count
        )
        
        # Cache the suggestions
        session_data[cache_key] = suggestions
        
        return suggestions
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        return []

def handle_suggestion_selection(
    session_data: Dict[str, Any],
    suggestion: str,
    action: str = "toggle"
) -> List[str]:
    """
    Handle suggestion chip selection/deselection
    
    Args:
        session_data: Dictionary containing session state
        suggestion: Suggestion text
        action: "toggle", "add", or "remove"
        
    Returns:
        Updated list of selected suggestions
    """
    if "selected_chips" not in session_data:
        session_data["selected_chips"] = []
    
    selected = session_data["selected_chips"]
    
    if action == "toggle":
        if suggestion in selected:
            selected.remove(suggestion)
        else:
            selected.append(suggestion)
    elif action == "add" and suggestion not in selected:
        selected.append(suggestion)
    elif action == "remove" and suggestion in selected:
        selected.remove(suggestion)
    
    return selected

def clear_selected_suggestions(session_data: Dict[str, Any]) -> None:
    """Clear all selected suggestion chips"""
    session_data["selected_chips"] = []

# ============================================================================
# ANSWER SUBMISSION
# ============================================================================

def submit_answer(
    client,
    session_data: Dict[str, Any],
    answer: str
) -> Dict[str, Any]:
    """
    Submit an answer and move to next question
    
    Args:
        client: LLM client instance
        session_data: Dictionary containing session state
        answer: User's answer (combined selected suggestions or typed answer)
        
    Returns:
        Dictionary with status and next question info:
        {
            "success": bool,
            "next_question": dict or None,
            "is_complete": bool,
            "message": str
        }
    """
    current_q = ask_next_question(session_data)
    
    if not current_q:
        return {
            "success": False,
            "message": "No current question found",
            "is_complete": False
        }
    
    # Save answer
    if "answers_json" not in session_data:
        session_data["answers_json"] = {}
    
    session_data["answers_json"][current_q["id"]] = answer
    
    # Add user message to chat
    add_chat_message(session_data, "user", answer)
    
    # Increment conversation step
    session_data["conversation_step"] = session_data.get("conversation_step", 0) + 1
    
    # Clear selections and cached suggestions
    clear_selected_suggestions(session_data)
    question_cache_key = f"sugg_{current_q['id']}"
    if question_cache_key in session_data:
        del session_data[question_cache_key]
    
    # Check if there are more questions
    next_q = ask_next_question(session_data)
    
    if next_q:
        # More questions remain
        ai_response = f"""Got it! ✔

**Question {session_data['conversation_step'] + 1}:** {next_q['text']}

_{next_q['placeholder']}_"""
        
        add_chat_message(session_data, "assistant", ai_response)
        
        return {
            "success": True,
            "next_question": next_q,
            "is_complete": False,
            "message": "Answer saved, next question ready"
        }
    else:
        # All questions answered - generate final prompt
        return {
            "success": True,
            "next_question": None,
            "is_complete": True,
            "message": "All questions answered",
            "should_generate_prompt": True
        }

def skip_remaining_questions(
    session_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Skip all remaining questions and trigger final prompt generation
    
    Args:
        session_data: Dictionary containing session state
        
    Returns:
        Dictionary with generation status
    """
    # Mark session as skipping to verification/generation
    session_data["conversation_step"] = 999  # Force past all questions
    
    return {
        "success": True,
        "next_question": None,
        "is_complete": True,
        "message": "Skipping to generation",
        "should_generate_prompt": True
    }

# ============================================================================
# FINAL PROMPT GENERATION
# ============================================================================

def generate_and_save_final_prompt(
    client,
    session_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate final prompt and save to database
    
    Args:
        client: LLM client instance
        session_data: Dictionary containing session state
        
    Returns:
        Dictionary with generation status:
        {
            "success": bool,
            "final_prompt": str,
            "error": str (if failed)
        }
    """
    try:
        # Add status message
        add_chat_message(
            session_data,
            "assistant",
            "✅ All questions answered! Generating your professional prompt..."
        )
        
        # ✅ CONTEXT-AWARE VISION ANALYSIS (if files uploaded but not analyzed)
        uploaded_files = session_data.get("uploaded_files", [])
        if uploaded_files:
            # Check if any files need analysis
            unanalyzed_files = [f for f in uploaded_files if not f.get("analyzed", False)]
            
            if unanalyzed_files:
                logger.info(f"🎯 [Chat Mode] Triggering context-aware analysis for {len(unanalyzed_files)} file(s)")
                
                # Import vision utilities
                from vision_utils import determine_focus_areas, analyze_image_with_openrouter
                from pathlib import Path
                from datetime import datetime
                
                # Step 1: Determine what aspects to focus on
                user_idea = session_data.get("user_idea", "")
                category = session_data.get("selected_category", "")
                
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
                        
                        logger.info(f"🔍 [Chat Mode] Analyzing {file_data['name']} with focus: {focus_areas}")
                        
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
        
        # Generate prompt (now with context-aware image analysis if available)
        final_prompt = generate_final_prompt(client, session_data)
        
        if not final_prompt:
            return {
                "success": False,
                "error": "Generated prompt is empty"
            }
        
        # Save to session
        session_data["final_prompt"] = final_prompt
        session_data["current_step"] = "final_prompt"
        
        # Save to database
        # Save to database
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
            },
            user_id=session_data.get("user_id")  # Added user_id
        )
        
        logger.info(f"Final prompt generated and saved at {timestamp}")
        
        return {
            "success": True,
            "final_prompt": final_prompt,
            "timestamp": timestamp
        }
        
    except Exception as e:
        error_msg = f"Error generating final prompt: {str(e)[:150]}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }

# ============================================================================
# SESSION INITIALIZATION
# ============================================================================

def initialize_chat_session(
    category: str,
    user_idea: str,
    selected_llm: str = "Claude",
    visual_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Initialize a new chat session
    
    Args:
        category: Selected category name
        user_idea: User's main idea
        selected_llm: LLM to use
        visual_settings: Optional visual settings dict
        
    Returns:
        Initialized session_data dictionary
    """
    session_data = {
        "selected_category": category,
        "user_idea": user_idea,
        "selected_llm": selected_llm,
        "conversation_step": 0,
        "answers_json": {},
        "messages": [],
        "selected_chips": [],
        "api_key_entered": True,  # Assumed true for web app
    }
    
    # Add visual settings if provided
    if visual_settings:
        session_data.update({
            "selected_color_palette": visual_settings.get("color_palette"),
            "selected_aspect_ratio": visual_settings.get("aspect_ratio"),
            "selected_camera_settings": visual_settings.get("camera_settings"),
            "selected_image_purpose": visual_settings.get("image_purpose"),
        })
    
    # Add first question to messages
    first_q = ask_next_question(session_data)
    if first_q:
        welcome_msg = f"""Great! Let's build your **{category}** prompt.

**Question 1:** {first_q['text']}

_{first_q['placeholder']}_"""
        add_chat_message(session_data, "assistant", welcome_msg)
    
    return session_data
