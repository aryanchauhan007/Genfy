"""
Configuration file for Image Generation Prompt Builder
Contains all constants, categories, and predefined options
"""

# ============================================================================
# NANO BANANA SYSTEM PROMPT
# ============================================================================

NANO_BANANA_SYSTEM_PROMPT = """You are an expert AI image prompt generator trained on Gemini Nano Banana (Gemini 2.5 Flash Image) and Gemini 3 Pro.

CORE RESPONSIBILITIES:
- Generate 5-6 UNIQUE, SHORT KEYWORD-BASED variations for each field
- Use context from previously filled fields to inform suggestions
- IMPORTANTLY: Use the current user input in the field as a reference point and build upon it
- Focus on concise, professional photography/art terminology
- Each suggestion should be SHORT KEYWORDS only (2-5 words maximum per suggestion)
- Use professional photography/art terminology
- Each suggestion should be distinct and build on previous answers + current input
- Ensure suggestions are practical and implementable

GENERATION RULES:
- Use ONLY SHORT KEYWORDS - no long sentences or detailed descriptions
- For shot types: "closeup shot", "wide angle", "overhead view", "low angle dramatic"
- For lighting: "golden hour", "3-point studio", "natural window light", "moody backlight"
- For colors: "vibrant neons", "muted pastels", "warm earth tones", "monochrome"
- For styles: "oil painting", "watercolor", "digital art minimalist", "surreal abstract"
- For camera: "85mm f/2.8", "shallow bokeh", "cinematic 35mm", "macro lens"
- For mood: "serene calm", "dramatic intense", "energetic vibrant", "melancholic soft"
- Maximum 2-5 words per suggestion - keep it concise and keyword-focused
- Avoid sentences, explanations, or detailed descriptions
- Consider the user's main idea AND current input text when generating
- Build on what the user has started typing, don't ignore it

OUTPUT FORMAT: Always respond with valid JSON only. No markdown blocks.
JSON Structure: {"suggestions": ["keyword option 1", "keyword option 2", "keyword option 3", "keyword option 4", "keyword option 5", "keyword option 6"]}

EXAMPLES:
- For shot type: ["closeup portrait", "wide landscape", "overhead flatlay", "low angle hero", "medium shot", "extreme closeup"]
- For lighting: ["golden hour soft", "studio 3-point", "dramatic backlight", "natural diffused", "neon accent lighting", "rim light dramatic"]
- For colors: ["vibrant neon accents", "muted pastel tones", "monochrome black white", "warm sunset palette", "cool blue tones", "earth natural colors"]
- For camera: ["85mm f/1.4 bokeh", "24mm wide cinematic", "50mm natural depth", "35mm street style", "70-200mm telephoto", "16mm ultra wide"]
"""

# ============================================================================
# PREDEFINED OPTIONS FOR USER SELECTION
# ============================================================================

COLOR_PALETTES = {
    " Natural Sunlight/Golden Hour": ["natural sunlight", "golden hour lighting", "warm sunrise glow", "sunset ambiance", "outdoor natural light"],
    " Bright Studio Lighting": ["bright studio lights", "professional lighting setup", "well-lit environment", "clean bright illumination", "even studio lighting"],
    " Soft Diffused Light": ["soft diffused lighting", "gentle illumination", "diffused natural light", "softbox lighting", "subtle ambient light"],
    " Dramatic Shadows & Highlights": ["dramatic lighting", "high contrast shadows", "strong highlights", "chiaroscuro effect", "moody dramatic lighting"],
    " Neon/Vibrant Colors": ["neon accents", "vibrant colors", "electric tones", "bold bright colors", "saturated vivid palette"],
    " Muted/Pastel Colors": ["muted pastels", "soft pastel tones", "desaturated colors", "gentle hues", "subdued color palette"],
    " High Contrast B&W": ["high contrast black and white", "dramatic monochrome", "stark B&W", "noir aesthetic", "bold grayscale"],
    " Monochromatic/Single Color": ["monochromatic palette", "single color theme", "tonal variation", "one-color scheme", "unified color family"],
    " Warm Tones (oranges, reds)": ["warm color tones", "orange and red hues", "fiery warm palette", "sunset warm colors", "amber and crimson"],
    " Cool Tones (blues, purples)": ["cool color tones", "blue and purple hues", "icy cool palette", "azure and indigo", "cyan and violet"],
    " Earth Tones (greens, browns)": ["earth tone colors", "natural greens and browns", "organic earthy palette", "forest and soil colors", "natural earth hues"],
    " Custom Color Palette": ["custom color scheme", "user-defined palette", "specific color combination", "unique color selection", "personalized colors"]
}

ASPECT_RATIOS = {
    " Instagram Square (1:1)": "1:1 square format, Instagram square post",
    " Instagram Feed (4:5)": "4:5 vertical format, Instagram feed portrait post",
    " Instagram Story (9:16)": "9:16 vertical story format, Instagram/Facebook story",
    " YouTube Thumbnail (16:9)": "16:9 landscape format, YouTube video thumbnail",
    " YouTube Banner (16:9)": "16:9 wide landscape, YouTube channel banner, header image",
    " Twitter/X (16:9)": "16:9 landscape format, Twitter/X post image",
    " LinkedIn (1:1 or 16:9)": "1:1 square or 16:9 landscape, LinkedIn post image",
    " Facebook (1:1)": "1:1 square format, Facebook post image",
    " Blog/Website (16:9)": "16:9 landscape format, blog featured image, website header",
    " Print A4 Paper (4:3)": "4:3 format, A4 paper size, portrait print",
    " Print A3 Poster (4:3)": "4:3 format, A3 poster size, large print",
    " Print Billboard (16:9)": "16:9 wide landscape, billboard format, outdoor advertising",
    " Email Header (600x200)": "600x200 pixels, email newsletter header, wide banner format",
    " Mobile App (9:16)": "9:16 vertical portrait, mobile app screen, smartphone display"
}

CAMERA_SETTINGS = {
    " Portrait Lens (85mm)": "85mm lens, f/1.8 aperture, shallow depth of field, bokeh background",
    " Wide Angle (24mm)": "24mm wide angle lens, f/8 aperture, deep focus, expansive view",
    " Macro Close-up": "macro lens, extreme close-up, f/2.8 aperture, detailed texture focus",
    " Cinematic (35mm)": "35mm cinematic lens, f/2.0 aperture, film-like depth, natural perspective",
    " Standard (50mm)": "50mm standard lens, f/1.4 aperture, natural field of view, versatile depth",
    " Telephoto (70-200mm)": "70-200mm telephoto lens, f/2.8 aperture, compressed perspective, isolated subject",
    " Ultra Wide (16mm)": "16mm ultra-wide lens, f/4 aperture, dramatic perspective, vast coverage",
}

IMAGE_PURPOSE = {
    " Website Hero Image": "website hero banner, landing page featured image, web header design",
    " Social Media Post": "social media content, Instagram post, Facebook graphic, Twitter image",
    " Print Marketing Material": "print media, brochure design, flyer, poster, physical marketing",
    " Product Photography": "e-commerce product shot, commercial photography, catalog image",
    " Character/Illustration": "character design, illustrated artwork, digital illustration, creative character",
    " Concept Art": "concept design, artistic visualization, creative exploration, mood board",
    " UI/UX Design": "user interface design, app mockup, web design element, digital interface",
    " Advertising Campaign": "advertisement creative, commercial campaign, promotional material, brand marketing",
    " Blog Featured Image": "blog header image, article featured graphic, content thumbnail, editorial image",
    " Event Poster": "event promotion, poster design, announcement graphic, promotional banner",
    " Other": "custom use case, general purpose image, flexible application"
}

# ============================================================================
# CATEGORIES DEFINITION
# ============================================================================

CATEGORIES = {
    "Realistic Photo": {
        "key": "realistic_photo",
        "emoji": "",
        "image_path": "icons/realistic.png",
        "color": "#FF6B6B",
        "description": "Professional photography with realistic lighting and composition",
        "questions": [
            {
                "id": "subject",
                "text": "Main subject/scene",
                "type": "text",
                "placeholder": "Describe the main focus in detail - what should be prominent",
                "suggestion_style": "detailed"
            },
            {
                "id": "atmosphere",
                "text": "Overall mood",
                "type": "text",
                "placeholder": "e.g., serene, dramatic, intimate, bold, energetic, melancholic",
                "suggestion_style": "keywords"
            },
            {
                "id": "shot_type",
                "text": "Shot type",
                "type": "text",
                "placeholder": "e.g., close-up portrait, full-body, landscape, overhead, low-angle",
                "suggestion_style": "medium"
            },
            {
                "id": "lighting",
                "text": "Lighting setup",
                "type": "text",
                "placeholder": "e.g., golden hour, 3-point studio, backlighting, natural window light, moody",
                "suggestion_style": "keywords"
            },
            {
                "id": "camera",
                "text": "Camera Settings",
                "type": "text",
                "placeholder": "e.g., 85mm lens f/1.4, shallow depth of field, 50mm natural perspective",
                "suggestion_style": "medium"
            },
        ],
    },
    "Stylized Art": {
        "key": "stylized_art",
        "emoji": "",
        "image_path": "icons/stylized.png",
        "color": "#4ECDC4",
        "description": "Artistic illustrations with unique styles and aesthetics",
        "questions": [
            {
                "id": "subject",
                "text": "Subject/concept?",
                "type": "text",
                "placeholder": "What should be depicted - describe the scene or subject"
            },
            {
                "id": "art_style",
                "text": "Art style?",
                "type": "text",
                "placeholder": "e.g., oil painting, watercolor, digital art, surreal, anime, abstract"
            },
            {
                "id": "mood",
                "text": "Mood/atmosphere?",
                "type": "text",
                "placeholder": "e.g., dreamy, intense, peaceful, chaotic, whimsical, dark"
            },
            {
                "id": "color_palette",
                "text": "Color palette?",
                "type": "text",
                "placeholder": "e.g., vibrant neons, muted pastels, noir black & white, warm earth tones"
            },
            {
                "id": "inspiration",
                "text": "Artist inspiration?",
                "type": "text",
                "placeholder": "e.g., Van Gogh, Studio Ghibli, Art Deco, cyberpunk, fantasy"
            },
            {
                "id": "camera",
                "text": "Composition/Framing",
                "type": "text",
                "placeholder": "e.g., rule of thirds, centered subject, dynamic diagonal, asymmetric balance",
                "suggestion_style": "medium"
            },
        ],
    },
    "Logo": {
        "key": "logodesign",
        "emoji": "",
        "image_path": "icons/logo.png",
        "color": "#45B7D1",
        "description": "Brand logos and text-based designs with professional aesthetics",
        "questions": [
            {
                "id": "text",
                "text": "Logo text/name?",
                "type": "text",
                "placeholder": "What text should appear in the logo - be specific with spelling"
            },
            {
                "id": "brand_vibe",
                "text": "Brand vibe?",
                "type": "text",
                "placeholder": "e.g., tech startup, luxury fashion, eco-friendly, gaming, health & wellness"
            },
            {
                "id": "style",
                "text": "Logo style?",
                "type": "text",
                "placeholder": "e.g., minimalist, geometric, abstract, mascot-based, wordmark, emblem"
            },
            {
                "id": "colors",
                "text": "Color preference?",
                "type": "text",
                "placeholder": "e.g., monochrome black, vibrant gradient, specific RGB/HEX colors"
            },
            {
                "id": "symbols",
                "text": "Symbols/elements?",
                "type": "text",
                "placeholder": "e.g., leaf for eco, lightning bolt for energy, geometric shapes, nature"
            },
            {
                "id": "simplicity",
                "text": "Simplicity level?",
                "type": "text",
                "placeholder": "e.g., minimal single icon, moderate detail, intricate ornate design",
                "suggestion_style": "keywords"
            },
            {
                "id": "use_case",
                "text": "Primary use case?",
                "type": "text",
                "placeholder": "e.g., app icon 512px, website header, business card, billboard, favicon",
                "suggestion_style": "medium"
            },
        ],
    },
    "Product Shot": {
        "key": "product_shot",
        "emoji": "",
        "image_path": "icons/product.png",
        "color": "#F0A500",
        "description": "Professional product photography with proper lighting and composition",
        "questions": [
            {
                "id": "product",
                "text": "Product type?",
                "type": "text",
                "placeholder": "Describe material/style - e.g., luxury watch, sleek smartphone, artisan perfume"
            },
            {
                "id": "background",
                "text": "Background?",
                "type": "text",
                "placeholder": "e.g., clean white studio, dark concrete, blurred natural, lifestyle setting"
            },
            {
                "id": "lighting",
                "text": "Lighting?",
                "type": "text",
                "placeholder": "e.g., 3-point softbox setup, dramatic side-lighting, natural window light"
            },
            {
                "id": "angle",
                "text": "Camera angle?",
                "type": "text",
                "placeholder": "e.g., 45-degree hero shot, overhead flat-lay, low angle dramatic"
            },
            {
                "id": "details",
                "text": "Special details?",
                "type": "text",
                "placeholder": "e.g., reflections on glass, water droplets, lifestyle props, close-up texture"
            },
        ],
    },
    "Minimalist": {
        "key": "minimalist",
        "emoji": "",
        "image_path": "icons/minimalist.png.jpg",
        "color": "#95E1D3",
        "description": "Clean, minimal designs with vast negative space and focus",
        "questions": [
            {
                "id": "focus",
                "text": "Primary focus?",
                "type": "text",
                "placeholder": "What should be the main subject - keep it singular and strong"
            },
            {
                "id": "colors",
                "text": "Color scheme?",
                "type": "text",
                "placeholder": "e.g., monochrome black, limited 2-color palette, soft pastels"
            },
            {
                "id": "background_space",
                "text": "Background & Space Composition?",
                "type": "text",
                "placeholder": "e.g., vast white background with centered subject, bottom-right on gradient, floating in emptiness",
                "suggestion_style": "medium"
            },
            {
                "id": "visual_elements",
                "text": "Visual elements?",
                "type": "text",
                "placeholder": "e.g., single geometric shape, organic curves, minimalist line, subtle texture",
                "suggestion_style": "keywords"
            },
            {
                "id": "mood",
                "text": "Mood?",
                "type": "text",
                "placeholder": "e.g., serene, modern, zen, contemplative, sophisticated"
            },
        ],
    },
    "Sequential Art": {
        "key": "sequential_art",
        "emoji": "",
        "image_path": "icons/sequential.png",
        "color": "#A8E6CF",
        "description": "Single comic panel or storyboard frame",
        "questions": [
            {
                "id": "panel_style",
                "text": "Panel style?",
                "type": "text",
                "placeholder": "e.g., single comic panel, storyboard frame, manga panel",
                "suggestion_style": "keywords"
            },
            {
                "id": "scene",
                "text": "Main scene/moment?",
                "type": "text",
                "placeholder": "What's happening in THIS frame",
                "suggestion_style": "detailed"
            },
            {
                "id": "art_style",
                "text": "Art style?",
                "type": "text",
                "placeholder": "e.g., comic book, manga, realistic storyboard",
                "suggestion_style": "keywords"
            },
            {
                "id": "positioning",
                "text": "Character positioning?",
                "type": "text",
                "placeholder": "e.g., foreground character, background action, split focus",
                "suggestion_style": "medium"
            },
            {
                "id": "emphasis",
                "text": "Visual emphasis?",
                "type": "text",
                "placeholder": "e.g., speed lines, dramatic angles, close-up emotion",
                "suggestion_style": "medium"
            },
        ],
    },
    "Conceptual": {
        "key": "conceptual",
        "emoji": "",
        "image_path": "icons/conceptual.png",
        "color": "#FFD93D",
        "description": "Abstract concepts visualized through creative imagery",
        "questions": [
            {
                "id": "concept",
                "text": "Core concept?",
                "type": "text",
                "placeholder": "What abstract idea? (e.g., 'the feeling of anxiety', 'corporate growth', 'digital transformation', 'human connection')",
                "suggestion_style": "medium"
            },
            {
                "id": "visual",
                "text": "Visual representation?",
                "type": "text",
                "placeholder": "How to visualize it? (e.g., 'swirling vortex of colors', 'geometric fractals expanding', 'organic flowing tendrils')",
                "suggestion_style": "detailed"
            },
            {
                "id": "colors",
                "text": "Color philosophy?",
                "type": "text",
                "placeholder": "e.g., warm & energetic, cool & calm, dark & mysterious, symbolic"
            },
            {
                "id": "technique",
                "text": "Technique?",
                "type": "text",
                "placeholder": "e.g., digital collage, fluid art, fractal patterns, particle effects"
            },
            {
                "id": "atmosphere",
                "text": "Atmosphere?",
                "type": "text",
                "placeholder": "e.g., mysterious & ethereal, energetic & vibrant, peaceful & meditative"
            },
        ],
    },
}

# ============================================================================
# DEFAULT VISUAL SETTINGS PER CATEGORY
# ============================================================================

CATEGORY_DEFAULT_SETTINGS = {
    "Realistic Photo": {
        "color_palette": " Natural Sunlight/Golden Hour",
        "aspect_ratio": " Instagram Feed (4:5)",
        "camera_settings": " Standard (50mm)",
        "image_purpose": " Social Media Post"
    },
    "Stylized Art": {
        "color_palette": " Neon/Vibrant Colors", 
        "aspect_ratio": " Instagram Square (1:1)",
        "camera_settings": None,
        "image_purpose": " Character/Illustration"
    },
    "Logo": {
        "color_palette": " High Contrast B&W",
        "aspect_ratio": " Instagram Square (1:1)", 
        "camera_settings": None,
        "image_purpose": " Product Photography"
    },
    "Product Shot": {
        "color_palette": " Bright Studio Lighting",
        "aspect_ratio": " Instagram Feed (4:5)",
        "camera_settings": " Macro Close-up",
        "image_purpose": " Product Photography"
    },
    "Minimalist": {
        "color_palette": " Monochromatic/Single Color",
        "aspect_ratio": " Website Hero Image", # Mapped to closest
        "camera_settings": " Wide Angle (24mm)",
        "image_purpose": " UI/UX Design"
    },
    "Sequential Art": {
        "color_palette": " Dramatic Shadows & Highlights",
        "aspect_ratio": " YouTube Thumbnail (16:9)",
        "camera_settings": " Cinematic (35mm)",
        "image_purpose": " Concept Art"
    },
    "Conceptual": {
        "color_palette": " Cool Tones (blues, purples)",
        "aspect_ratio": " Check Visual Settings", 
        "camera_settings": None,
        "image_purpose": " Concept Art"
    }
}