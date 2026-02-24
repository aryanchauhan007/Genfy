"""
LLM Utils Module
Handles LLM client initialization, management, and API operations
Includes high-level suggestion and prompt generation functions
Web-framework agnostic - No UI dependencies
"""

import os
import re
import json
import random
import logging
from typing import Optional, Dict, List, Any
from mistralai import Mistral
from anthropic import Anthropic
from dotenv import load_dotenv
from config import NANO_BANANA_SYSTEM_PROMPT, CATEGORIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class LLMError(Exception):
    """Base exception for LLM-related errors"""
    pass

class LLMConnectionError(LLMError):
    """Raised when LLM client initialization fails"""
    pass

class LLMAPIError(LLMError):
    """Raised when LLM API call fails"""
    pass

# ============================================================================
# CLIENT INITIALIZATION
# ============================================================================

def initialize_mistral_client() -> Optional[Mistral]:
    """
    Initialize Mistral AI client from environment variables
    
    Returns:
        Mistral client instance or None if initialization fails
        
    Raises:
        LLMConnectionError: If API key is missing or connection fails
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        error_msg = "Mistral API key not found in .env file"
        logger.error(error_msg)
        raise LLMConnectionError(error_msg)
    
    try:
        client = Mistral(api_key=api_key)
        logger.info("Connected to Mistral AI")
        return client
    except Exception as e:
        error_msg = f"Failed to connect to Mistral: {str(e)[:80]}"
        logger.error(error_msg)
        raise LLMConnectionError(error_msg)

def initialize_anthropic_client() -> Optional[Anthropic]:
    """
    Initialize Anthropic Claude client from environment variables
    
    Returns:
        Anthropic client instance or None if initialization fails
        
    Raises:
        LLMConnectionError: If API key is missing or connection fails
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        error_msg = "Anthropic API key not found in .env file"
        logger.error(error_msg)
        raise LLMConnectionError(error_msg)
    
    try:
        client = Anthropic(api_key=api_key)
        logger.info("Connected to Claude AI")
        return client
    except Exception as e:
        error_msg = f"Failed to connect to Claude: {str(e)[:80]}"
        logger.error(error_msg)
        raise LLMConnectionError(error_msg)

def get_llm_client(llm_name: str):
    """
    Get or create LLM client based on selected LLM
    
    Args:
        llm_name: Name of the LLM ("Mistral" or "Claude")
        
    Returns:
        LLM client instance
        
    Raises:
        LLMConnectionError: If LLM name is unknown or connection fails
    """
    if llm_name == "Mistral":
        return initialize_mistral_client()
    elif llm_name == "Claude":
        return initialize_anthropic_client()
    else:
        error_msg = f"Unknown LLM: {llm_name}"
        logger.error(error_msg)
        raise LLMConnectionError(error_msg)

# ============================================================================
# LLM API CALLS
# ============================================================================

def call_mistral(
    client,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 250
) -> Optional[str]:
    """
    Call Mistral API
    
    Args:
        client: Mistral client instance
        system_prompt: System instruction
        user_prompt: User query
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text or None if call fails
        
    Raises:
        LLMAPIError: If API call fails
    """
    try:
        message = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return message.choices[0].message.content
    except Exception as e:
        error_msg = f"Mistral API Error: {str(e)[:150]}"
        logger.error(error_msg)
        raise LLMAPIError(error_msg)

def call_claude(
    client,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 250
) -> Optional[str]:
    """
    Call Anthropic Claude API
    
    Args:
        client: Anthropic client instance
        system_prompt: System instruction
        user_prompt: User query
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text or None if call fails
        
    Raises:
        LLMAPIError: If API call fails
    """
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text
    except Exception as e:
        error_msg = f"Claude API Error: {str(e)[:150]}"
        logger.error(error_msg)
        raise LLMAPIError(error_msg)

def call_llm(
    client,
    llm_name: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 250
) -> Optional[str]:
    """
    Unified function to call any LLM
    
    Args:
        client: LLM client instance
        llm_name: Name of the LLM ("Mistral" or "Claude")
        system_prompt: System instruction
        user_prompt: User query
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Generated text or None
        
    Raises:
        LLMAPIError: If LLM name is unknown or API call fails
    """
    if not client:
        error_msg = "No LLM client initialized"
        logger.error(error_msg)
        raise LLMAPIError(error_msg)
    
    if llm_name == "Mistral":
        return call_mistral(client, system_prompt, user_prompt, temperature, max_tokens)
    elif llm_name == "Claude":
        return call_claude(client, system_prompt, user_prompt, temperature, max_tokens)
    else:
        error_msg = f"Unknown LLM: {llm_name}"
        logger.error(error_msg)
        raise LLMAPIError(error_msg)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_json_safely(response_text: str) -> Dict[str, Any]:
    """
    Extract JSON from response safely, handling markdown blocks
    
    Args:
        response_text: Raw response text potentially containing JSON
        
    Returns:
        Parsed JSON dictionary or empty dict if parsing fails
    """
    try:
        # Remove markdown code blocks
        response_text = re.sub(r'```[\s\S]*?```', '', response_text)
        response_text = re.sub(r'^```', '', response_text, flags=re.MULTILINE)
        response_text = re.sub(r'```$', '', response_text, flags=re.MULTILINE)
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}")
        return {}

def get_previous_answers_context(session_data: Dict[str, Any], current_q_idx: int) -> str:
    """
    Build context from previously answered questions
    
    Args:
        session_data: Dictionary containing session state (selected_category, answers_json)
        current_q_idx: Index of current question
        
    Returns:
        Formatted string of previous answers
    """
    if current_q_idx == 0:
        return "This is the first question - no previous context available."
    
    previous_answers = []
    category_data = CATEGORIES[session_data.get("selected_category")]
    
    for i in range(current_q_idx):
        q = category_data["questions"][i]
        answer = session_data.get("answers_json", {}).get(q["id"], "")
        if answer:
            previous_answers.append(f"-  {q['text']}: {answer}")
    
    if not previous_answers:
        return "No previous answers filled yet."
    
    return "PREVIOUS CONTEXT:\n" + "\n".join(previous_answers)

# ============================================================================
# HIGH-LEVEL GENERATION FUNCTIONS
# ============================================================================

def generate_suggestions(
    client,
    session_data: Dict[str, Any],
    question: Dict[str, Any],
    q_idx: int,
    current_input: str = "",
    refresh_count: int = 0,
) -> List[str]:
    """
    Generate AI-powered suggestions for a question
    
    Args:
        client: LLM client instance
        session_data: Dictionary containing session state
        question: Question dictionary with 'text', 'suggestion_style', etc.
        q_idx: Question index
        current_input: Current user input (optional)
        refresh_count: Number of times suggestions have been refreshed
        
    Returns:
        List of 5-6 suggestion strings
    """
    if not client:
        logger.warning("Client is None, returning empty suggestions")
        return []
    
    suggestion_style = question.get("suggestion_style", "medium")
    length_guides = {
        "keywords": "1-3 words",
        "medium": "4-7 words",
        "detailed": "8-15 words",
        "narrative": "10-20 words",
    }
    length_instruction = length_guides.get(suggestion_style, "4-7 words")
    
    previous_context = get_previous_answers_context(session_data, q_idx)
    
    current_input_context = ""
    if current_input.strip():
        current_input_context = f"\nCURRENT INPUT: {current_input}\n"
    
    variation_seed = ""
    if refresh_count > 0:
        variation_styles = [
            "creative and bold",
            "professional and refined",
            "experimental and unique",
            "artistic and expressive",
            "minimal and clean",
            "dramatic and intense",
            "subtle and sophisticated",
            "vibrant and energetic",
        ]
        selected_style = variation_styles[refresh_count % len(variation_styles)]
        random_seed = random.randint(1000, 9999)
        variation_seed = f"""
VARIATION #{refresh_count} (Seed: {random_seed}):
- Focus on {selected_style} approaches
- Generate COMPLETELY DIFFERENT suggestions than previous attempts
- Explore alternative perspectives and synonyms
- Be MORE diverse than before
"""
    
    prompt = f"""
PROJECT INFO:
- User Main Idea: {session_data.get('user_idea')}
- Category: {session_data.get('selected_category')}

{previous_context}
{current_input_context}

CURRENT QUESTION: {question['text']}
SUGGESTION LENGTH: {length_instruction}

{variation_seed}

Generate 5-6 UNIQUE suggestions following the length requirement.
Return ONLY valid JSON: {{"suggestions": ["suggestion 1", "suggestion 2", "suggestion 3", "suggestion 4", "suggestion 5", "suggestion 6"]}}
"""
    
    try:
        response_text = call_llm(
            client,
            session_data.get("selected_llm"),
            NANO_BANANA_SYSTEM_PROMPT,
            prompt,
            temperature=0.7 + (0.1 * min(refresh_count, 3)),
            max_tokens=150,
        )
        
        if response_text:
            result = extract_json_safely(response_text)
            suggestions = result.get("suggestions", [])
            if suggestions and len(suggestions) >= 5:
                return suggestions[:6]
            return suggestions if suggestions else []
        
        return []
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)[:100]}")
        return []

def generate_final_prompt(client, session_data: Dict[str, Any]) -> str:
    """
    Generate final image prompt from all Q&A answers
    
    Args:
        client: LLM client instance
        session_data: Dictionary containing all session data
        
    Returns:
        Generated final prompt string
    """
    if not client:
        logger.warning("Client is None, returning empty prompt")
        return ""
    
    cat_data = CATEGORIES[session_data.get("selected_category")]
    questions = cat_data["questions"]
    
    responses_text = "\n".join(
        [f"-  {q['text']}: {session_data.get('answers_json', {}).get(q['id'], '')}" for q in questions]
    )
    
    visual_settings_text = ""
    if session_data.get("selected_image_purpose"):
        visual_settings_text += f"\n- Image Purpose: {session_data['selected_image_purpose']}"
    if session_data.get("selected_color_palette"):
        visual_settings_text += f"\n- Color Palette: {session_data['selected_color_palette']}"
    if session_data.get("selected_aspect_ratio"):
        visual_settings_text += f"\n- Aspect Ratio: {session_data['selected_aspect_ratio']}"
    if session_data.get("selected_camera_settings"):
        visual_settings_text += f"\n- Camera Settings: {session_data['selected_camera_settings']}"
    
    # ✅ ADD REFERENCE IMAGE ANALYSIS IF AVAILABLE
    reference_analysis_text = ""
    if session_data.get("reference_analysis") and len(session_data["reference_analysis"]) > 0:
        reference_analysis_text = "\n\nREFERENCE IMAGE ANALYSIS:"
        for idx, analysis in enumerate(session_data["reference_analysis"], 1):
            reference_analysis_text += f"\n\n📸 Reference Image {idx}: {analysis['filename']}"
            reference_analysis_text += f"\nFocus Areas: {', '.join(analysis.get('focus_areas', []))}"
            reference_analysis_text += f"\n{analysis['analysis']}"
    
    final_prompt_instruction = f"""
PROJECT DETAILS:
Category: {session_data.get('selected_category')}
User Main Idea: {session_data.get('user_idea')}

VISUAL SETTINGS:{visual_settings_text if visual_settings_text else " None"}
{reference_analysis_text}

USER'S ANSWERS:
{responses_text}

TASK: Generate a professional, detailed image prompt (150-220 words) optimized for image generation.

CRITICAL INSTRUCTIONS:
1. {"⚠️ REFERENCE IMAGE MODE: Use GENERIC descriptive terms for the subject based on what's in the reference image (e.g., 'the subject', 'the main element', 'the item', 'the scene', 'the character', etc.). DO NOT describe specific identifying features, visual details, or unique characteristics - the uploaded reference image will provide those. Focus ONLY on: scenario, context, action, additional elements, environment, lighting, camera angle, mood, composition, and artistic style." if reference_analysis_text else "Use the user's idea and Q&A answers, including detailed subject description"}
2. Synthesize all the information to create a cohesive, vivid prompt
3. Ensure the final prompt is specific and actionable for AI image generation
4. {"Combine the user's original idea with the visual style and subject details from the reference image." if reference_analysis_text else ""}
5. {"IMPORTANT: Include a clear directive in the prompt itself on HOW to use the attached image (e.g., 'Using the attached reference image for character consistency...', 'Adopting the composition of the reference image...', etc.)." if reference_analysis_text else ""}

RESPOND ONLY WITH THE FINAL PROMPT (no preamble, no explanation).
"""
    
    try:
        # Use a proper system prompt for text generation, NOT the suggestions JSON prompt
        prompt_generator_system = "You are an expert AI image prompt engineer. Generate detailed, vivid, professional image prompts optimized for AI image generators like Midjourney, DALL-E, Stable Diffusion, and Gemini."
        
        response_text = call_llm(
            client,
            session_data.get("selected_llm"),
            prompt_generator_system,  # ✅ FIXED: Use proper system prompt  
            final_prompt_instruction,
            temperature=0.75,
            max_tokens=1200,
        )
        return response_text.strip() if response_text else ""
    except Exception as e:
        logger.error(f"Error generating final prompt: {str(e)[:150]}")
        return ""

def generate_quick_prompt(client, session_data: Dict[str, Any]) -> str:
    """
    Generate prompt quickly from just user idea and visual settings
    (Skip the Q&A process)
    
    Args:
        client: LLM client instance
        session_data: Dictionary containing session state
        
    Returns:
        Generated prompt string
    """
    if not client:
        logger.warning("Client is None, returning empty prompt")
        return ""
    
    # Build visual settings text
    visual_settings_text = ""
    if session_data.get("selected_image_purpose"):
        visual_settings_text += f"\n- Image Purpose: {session_data['selected_image_purpose']}"
    if session_data.get("selected_color_palette"):
        visual_settings_text += f"\n- Color Palette: {session_data['selected_color_palette']}"
    if session_data.get("selected_aspect_ratio"):
        visual_settings_text += f"\n- Aspect Ratio: {session_data['selected_aspect_ratio']}"
    if session_data.get("selected_camera_settings"):
        visual_settings_text += f"\n- Camera Settings: {session_data['selected_camera_settings']}"
    
    # ✅ ADD REFERENCE IMAGE ANALYSIS IF AVAILABLE
    reference_analysis_text = ""
    if session_data.get("reference_analysis") and len(session_data["reference_analysis"]) > 0:
        reference_analysis_text = "\n\nREFERENCE IMAGE ANALYSIS:"
        for idx, analysis in enumerate(session_data["reference_analysis"], 1):
            reference_analysis_text += f"\n\n📸 Reference Image {idx}: {analysis['filename']}"
            reference_analysis_text += f"\nFocus Areas: {', '.join(analysis.get('focus_areas', []))}"
            reference_analysis_text += f"\n{analysis['analysis']}"
    
    quick_prompt_instruction = f"""
PROJECT DETAILS:
Category: {session_data.get('selected_category')}
User Main Idea: {session_data.get('user_idea')}

VISUAL SETTINGS:{visual_settings_text if visual_settings_text else " None"}
{reference_analysis_text}

TASK: 
Generate a professional, detailed image prompt (150-220 words) optimized for image generation.

CRITICAL INSTRUCTIONS:
1. {"⚠️ REFERENCE IMAGE MODE: The user has provided a reference image. INTEGRATE the key visual details from the 'Reference Image Analysis' into the prompt. Describe the subject, style, and mood found in the analysis to ensure the new image resembles the reference. If the analysis identifies a specific person or character, INCLUDE those descriptors." if reference_analysis_text else "Base the prompt on the user's idea and visual settings, including detailed subject description"}
2. Make intelligent assumptions about shot type, composition, and mood based on the category
3. Ensure the final prompt is vivid, specific, and actionable for AI image generation
4. {"Combine the user's original idea with the visual style and subject details from the reference image." if reference_analysis_text else ""}
5. {"IMPORTANT: Include a clear directive in the prompt itself on HOW to use the attached image (e.g., 'Using the attached reference image for character consistency...', 'Adopting the composition of the reference image...', etc.)." if reference_analysis_text else ""}

RESPOND ONLY WITH THE FINAL PROMPT (no preamble, no explanation).
"""
    
    try:
        # Use a proper system prompt for text generation, NOT the suggestions JSON prompt
        prompt_generator_system = "You are an expert AI image prompt engineer. Generate detailed, vivid, professional image prompts optimized for AI image generators like Midjourney, DALL-E, Stable Diffusion, and Gemini."
        
        response_text = call_llm(
            client,
            session_data.get("selected_llm"),
            prompt_generator_system,  # ✅ FIXED: Use proper system prompt
            quick_prompt_instruction,
            temperature=0.75,
            max_tokens=1200,
        )
        
        # DEBUG: Log what the LLM actually returned
        logger.info(f"🤖 LLM Raw Response Length: {len(response_text) if response_text else 0}")
        logger.info(f"🤖 LLM Response Preview: {response_text[:200] if response_text else 'EMPTY'}...")
        logger.info(f"🤖 Response looks like JSON: {response_text.strip().startswith('{') if response_text else False}")
        
        return response_text.strip() if response_text else ""
    except Exception as e:
        logger.error(f"Error generating quick prompt: {str(e)[:150]}")
        return ""

def refine_prompt(client, session_data: Dict[str, Any], refinement_instruction: str) -> str:
    """
    Refine an existing prompt based on user feedback
    
    Args:
        client: LLM client instance
        session_data: Dictionary containing session state with 'final_prompt'
        refinement_instruction: User's refinement request
        
    Returns:
        Refined prompt string
    """
    if not client:
        logger.warning("Client is None, returning empty prompt")
        return ""
    
    current_prompt = session_data.get("final_prompt", "")
    reference_analysis = session_data.get("reference_analysis")
    
    # Format reference analysis if it exists
    reference_analysis_text = ""
    if reference_analysis:
        reference_analysis_text = f"REFERENCE IMAGE ANALYSIS:\n{json.dumps(reference_analysis, indent=2)}\n"

    refinement_prompt = f"""
CURRENT PROMPT:
{current_prompt}

{reference_analysis_text}

USER REFINEMENT REQUEST:
{refinement_instruction}

TASK:
Modify the prompt according to the user's request while maintaining professional quality.
Keep it 150-220 words optimized for image generation.

CRITICAL INSTRUCTIONS:
1. Maintain the core subject and style unless explicitly asked to change.
2. {"⚠️ REFERENCE IMAGE MODE: Ensure the prompt continues to reflect the key visual details from the Reference Image Analysis. If the user asks to change something specific, do so, but keep the rest consistent with the image." if reference_analysis else "Ensure the prompt remains vivid and descriptive."}
3. {"IMPORTANT: The prompt MUST retain the clear directive on HOW to use the attached image (e.g., 'Using the attached reference image...'). DO NOT REMOVE THIS INSTRUCTION unless the user explicitly asks to stop using the reference image." if reference_analysis else ""}

RESPOND ONLY WITH THE REFINED PROMPT.
"""
    
    try:
        response_text = call_llm(
            client,
            session_data.get("selected_llm"),
            NANO_BANANA_SYSTEM_PROMPT,
            refinement_prompt,
            temperature=0.75,
            max_tokens=1200
        )
        return response_text.strip() if response_text else ""
    except Exception as e:
        logger.error(f"Error refining prompt: {str(e)[:150]}")
        return ""

# ============================================================================
# API KEY VALIDATION
# ============================================================================

def validate_api_keys() -> Dict[str, bool]:
    """
    Validate that required API keys are set
    
    Returns:
        Dictionary with availability status for each LLM
    """
    mistral_key = os.getenv("MISTRAL_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    return {
        "mistral_available": bool(mistral_key),
        "anthropic_available": bool(anthropic_key),
        "either_available": bool(mistral_key or anthropic_key),
        "both_available": bool(mistral_key and anthropic_key),
    }

def get_available_llms() -> List[str]:
    """
    Get list of available LLMs based on API keys
    
    Returns:
        List of available LLM names
    """
    validation = validate_api_keys()
    available = []
    
    if validation["mistral_available"]:
        available.append("Mistral")
    if validation["anthropic_available"]:
        available.append("Claude")
    
    return available if available else ["Mistral"]

def get_default_llm() -> str:
    """
    Get the default LLM based on availability
    
    Returns:
        Default LLM name
    """
    available = get_available_llms()
    return available if available else "Mistral"
