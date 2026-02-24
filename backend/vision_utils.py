import os
import base64
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "meta-llama/llama-3.2-11b-vision-instruct"

def encode_image(image_path: str) -> str:
    """Encode image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def determine_focus_areas(user_request: str, category: str) -> dict:
    """
    Use LLM to determine what aspects of the image to analyze based on user request and category.
    
    Args:
        user_request: The user's prompt/idea
        category: The selected category (e.g., "Realistic Photo", "Logo/Text Design")
    
    Returns:
        Dictionary with focus areas and reasoning
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.warning("OPENROUTER_API_KEY not found, using default focus areas")
        return {
            "success": True,
            "focus_areas": ["composition", "lighting", "colors", "mood"],
            "reasoning": "Default focus areas (API key missing)"
        }
    
    try:
        analysis_prompt = f"""You are an expert AI assistant analyzing how a reference image should be studied for image generation.

User's Category: {category}
User's Request: {user_request}

Your task: Determine the 3-5 MOST IMPORTANT aspects of the reference image to analyze based on what the user wants to achieve.

Available focus areas:
- subject_details: Facial features, hairstyle, skin tone, body type, clothing, poses, expressions, distinctive characteristics
- composition: Layout, framing, rule of thirds, balance, focal points, spatial arrangement
- lighting: Quality, direction, intensity, shadows, highlights, time of day, mood lighting
- colors: Color palette, harmony, saturation, temperature, dominant hues, color relationships
- mood: Atmosphere, emotional tone, vibe, feeling, ambiance
- environment: Setting, background, location details, architectural elements, natural elements
- style: Artistic style, rendering technique, aesthetic, visual treatment, artistic approach
- texture: Surface details, material quality, tactile appearance, pattern details
- perspective: Camera angle, viewpoint, depth, focal length, vanishing points

THINK CAREFULLY about what the user is trying to achieve:

1. If they want to RECREATE a person/character in different scenarios → MUST include subject_details
2. If they want to USE the image's colors/palette → MUST include colors
3. If they want to MATCH the lighting/atmosphere → MUST include lighting + mood
4. If they want to MIMIC the artistic style → MUST include style
5. If they want to REFERENCE the environment/setting → MUST include environment
6. If they want to COPY composition/framing → MUST include composition + perspective

Respond ONLY with JSON (no extra text):
{{
  "focus_areas": ["area1", "area2", "area3"],
  "reasoning": "brief explanation of why these specific aspects matter for THIS request"
}}

EXAMPLES of smart analysis:

Request: "this person in a green suit and black shorts"
→ {{"focus_areas": ["subject_details", "lighting", "colors", "style"], "reasoning": "Need subject identity, plus lighting/colors for natural realism"}}

Request: "use this sunset's color palette for a portrait"
→ {{"focus_areas": ["colors", "lighting", "mood"], "reasoning": "Extracting color scheme and atmospheric qualities"}}

Request: "match the architectural style of this building for a different structure"
→ {{"focus_areas": ["style", "composition", "perspective", "texture"], "reasoning": "Capturing architectural aesthetic and structural elements"}}

Request: "create a logo with this image's aesthetic"
→ {{"focus_areas": ["style", "colors", "composition"], "reasoning": "Extracting visual style and color scheme for branding"}}

Request: "recreate this lighting setup for product photography"
→ {{"focus_areas": ["lighting", "perspective", "mood"], "reasoning": "Analyzing light direction, camera angle, and atmospheric tone"}}

Now analyze the user's actual request and choose focus areas accordingly."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [{"role": "user", "content": analysis_prompt}],
            "temperature": 0.4  # Slightly higher for creative reasoning
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"OpenRouter API Error: {response.text}")
            # Smart fallback: generic but comprehensive
            return {
                "success": True,
                "focus_areas": ["composition", "lighting", "colors", "mood"],
                "reasoning": "Default comprehensive focus areas (API error)"
            }
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        # Extract JSON from response
        import json
        import re
        
        def clean_json_string(s):
            """Clean JSON string from markdown code blocks and potential control characters"""
            # Remove markdown code blocks if present
            s = re.sub(r'```json\s*', '', s)
            s = re.sub(r'```', '', s)
            # Remove any leading/trailing whitespace
            s = s.strip()
            return s

        try:
            # First try: clean the content directly
            cleaned_content = clean_json_string(content)
            # Try to see if the whole thing is JSON
            result = json.loads(cleaned_content)
        except json.JSONDecodeError:
            # Second try: find JSON-like object within the text
            try:
                # Look for { ... } structure, allowing for newlines (DOTALL) using non-greedy match
                # We start looking from the first { to the last }
                start_idx = content.find('{')
                end_idx = content.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx+1]
                    # Clean control characters that might break JSON (newlines are okay in newer Python, but control chars aren't)
                    # We'll rely on strict=False for standard json if needed, but let's just try parsing
                    result = json.loads(json_str, strict=False)
                else:
                    raise ValueError("No JSON object found")
            except Exception as e:
                logger.warning(f"Failed to parse LLM response: {str(e)} | Content snippet: {content[:100]}...")
                # Fallback to defaults
                return {
                    "success": True,
                    "focus_areas": ["composition", "lighting", "colors"],
                    "reasoning": "Default focus areas (LLM parsing error)"
                }

        # If we got here, we have a result. Validate it has the key we need.
        if "focus_areas" not in result:
             result["focus_areas"] = ["composition", "lighting", "colors"]

        result["success"] = True
        logger.info(f"✅ Smart focus areas: {result['focus_areas']} | Reason: {result.get('reasoning', 'N/A')}")
        return result
            
    except Exception as e:
        logger.error(f"Error determining focus areas: {str(e)}")
        return {
            "success": True,
            "focus_areas": ["composition", "lighting", "colors", "mood"],
            "reasoning": f"Default comprehensive areas (error: {str(e)})"
        }


def analyze_image_with_openrouter(image_path: str, user_context: str = "", focus_areas: list = None) -> dict:
    """
    Analyze image using OpenRouter Vision Model (Llama 3.2)
    image_path: Absolute or relative path to the local image file
    user_context: User's request/idea for context
    focus_areas: List of aspects to focus on (e.g., ["lighting", "colors", "mood"])
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found")
        return {"success": False, "error": "OpenRouter API key missing"}

    try:
        # Ensure path is absolute for reading
        if not os.path.isabs(image_path):
            # Assuming image_path is relative to backend root or is the relative URL path
            # If it's the relative URL /uploads/..., we need to resolve it
            if image_path.startswith("/uploads/"):
                # Remove /uploads/ and prepend actual uploads dir
                clean_path = image_path.replace("/uploads/", "", 1)
                # Assuming uploads dir is "uploads" in CWD
                real_path = Path("uploads") / clean_path
            else:
                real_path = Path(image_path)
        else:
            real_path = Path(image_path)

        if not real_path.exists():
             return {"success": False, "error": f"File not found: {real_path}"}
            
        base64_image = encode_image(str(real_path))
        
        # Build context-aware vision prompt
        if focus_areas and len(focus_areas) > 0:
            focus_str = ", ".join(focus_areas)
            vision_prompt = f"""Analyze this reference image for AI image generation, focusing specifically on: {focus_str}.

Provide detailed analysis of these aspects:
"""
            for area in focus_areas:
                if area == "composition":
                    vision_prompt += "\n- Composition: Layout, balance, rule of thirds, focal points"
                elif area == "lighting":
                    vision_prompt += "\n- Lighting: Quality, direction, intensity, time of day indicators"
                elif area == "colors":
                    vision_prompt += "\n- Colors: Palette, harmony, saturation, temperature, dominant colors"
                elif area == "mood":
                    vision_prompt += "\n- Mood: Atmosphere, emotional tone, vibe"
                elif area == "subject_details":
                    vision_prompt += """\n- Subject Details: 
  * Facial features (face shape, eyes, nose, mouth, jawline)
  * Hairstyle and hair color
  * Skin tone and texture
  * Distinctive characteristics (facial hair, accessories, unique features)
  * Body type and posture
  * Current clothing/outfit (for reference, even if user wants to change it)
  * Expression and demeanor"""
                elif area == "environment":
                    vision_prompt += "\n- Environment: Setting, background, location details"
                elif area == "style":
                    vision_prompt += "\n- Style: Artistic style, rendering technique, aesthetic"
                elif area == "texture":
                    vision_prompt += "\n- Texture: Surface details, material quality"
                elif area == "perspective":
                    vision_prompt += "\n- Perspective: Camera angle, depth, focal point, viewpoint"
            
            vision_prompt += f"\n\nUser Context: {user_context}\n\nProvide a concise but comprehensive analysis focused on these aspects for image generation reference."
        else:
            # Fallback to generic prompt if no focus areas
            vision_prompt = f"""Analyze this reference image for AI image generation. Provide:
1. Visual Description: Composition, subjects, colors, lighting
2. Style Analysis: Art style, aesthetic, mood, techniques
3. Color Palette: Dominant colors and scheme
4. Technical Details: Lighting, perspective, depth, texture
5. Prompt Elements: Key elements for image generation

{f"User Context: {user_context}" if user_context else ""}

Format as structured analysis for image generation reference."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Genfy"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": vision_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            logger.error(f"OpenRouter API Error: {response.text}")
            return {"success": False, "error": f"API Error: {response.status_code} - {response.text}"}
            
        data = response.json()
        
        if "choices" not in data or len(data["choices"]) == 0:
             return {"success": False, "error": "No response from model"}
             
        analysis = data["choices"][0]["message"]["content"]
        
        return {
            "success": True,
            "analysis": analysis,
            "model": MODEL_NAME,
            "focus_areas": focus_areas or []
        }

    except Exception as e:
        logger.error(f"Vision analysis error: {str(e)}")
        return {"success": False, "error": str(e)}
