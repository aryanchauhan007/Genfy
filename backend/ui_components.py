"""
UI Components and styling for the Streamlit app
Contains CSS styling and reusable UI functions
"""

import streamlit as st


def apply_custom_css():
    """Apply custom CSS styling to the app"""
    st.markdown("""
<style>
/* ============================================================================
   MATERIAL DESIGN 3 - SMOOTH MICRO-INTERACTIONS
   ============================================================================ */
:root {
    --md-primary: #6366f1;
    --md-secondary: #ec4899;
    --md-surface: #ffffff;
    --md-shadow-1: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    --md-shadow-2: 0 3px 6px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12);
    --md-shadow-3: 0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10);
    --md-shadow-4: 0 15px 25px rgba(0,0,0,0.15), 0 5px 10px rgba(0,0,0,0.05);
    --md-shadow-5: 0 20px 40px rgba(0,0,0,0.2);
}

/* ============================================================================
   SMOOTH MICRO-ANIMATIONS
   ============================================================================ */
@keyframes ripple {
    0% {
        transform: scale(0);
        opacity: 1;
    }
    100% {
        transform: scale(4);
        opacity: 0;
    }
}

@keyframes slideUpFade {
    from {
        opacity: 0;
        transform: translateY(40px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes scaleUp {
    from {
        transform: scale(0.9);
        opacity: 0;
    }
    to {
        transform: scale(1);
        opacity: 1;
    }
}

@keyframes gentleFloat {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-6px);
    }
}

@keyframes cardFlip {
    from {
        transform: rotateY(90deg);
        opacity: 0;
    }
    to {
        transform: rotateY(0deg);
        opacity: 1;
    }
}

@keyframes expandWidth {
    from {
        width: 0%;
    }
    to {
        width: 100%;
    }
}

@keyframes progressPulse {
    0%, 100% {
        transform: scaleY(1);
    }
    50% {
        transform: scaleY(1.2);
    }
}

@keyframes smoothWave {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(100%);
    }
}

@keyframes breathe {
    0%, 100% {
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3);
    }
    50% {
        box-shadow: 0 5px 25px rgba(99, 102, 241, 0.5);
    }
}

@keyframes smoothPulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.03);
    }
}

/* ============================================================================
   CLEAN GRADIENT BACKGROUND
   ============================================================================ */
.main {
    background: linear-gradient(to bottom right, #f8fafc, #e0e7ff, #fce7f3, #f8fafc);
    min-height: 100vh;
}

.block-container {
    padding: 2.5rem 1.5rem !important;
    max-width: 1400px;
    animation: slideUpFade 0.6s ease-out;
}

/* ============================================================================
   ELEGANT TYPOGRAPHY
   ============================================================================ */
h1 {
    font-size: 2.75rem !important;
    font-weight: 800 !important;
    color: #1e293b !important;
    margin-bottom: 0.5rem !important;
    animation: slideUpFade 0.7s ease-out;
    line-height: 1.2;
}

h2 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #334155 !important;
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
    animation: slideUpFade 0.6s ease-out;
    position: relative;
}

h2::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    height: 4px;
    width: 60px;
    background: linear-gradient(to right, #6366f1, #ec4899);
    border-radius: 2px;
    animation: expandWidth 0.8s ease-out;
}

h3 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    animation: slideUpFade 0.5s ease-out;
}

/* ============================================================================
   MATERIAL CARDS/BUTTONS - RIPPLE EFFECT
   ============================================================================ */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 1rem 1.8rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    box-shadow: var(--md-shadow-2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: scaleUp 0.4s ease-out;
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.stButton > button:active::before {
    width: 300px;
    height: 300px;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--md-shadow-4) !important;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: var(--md-shadow-2) !important;
}

/* Primary button - different gradient */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #f43f5e 0%, #fb7185 100%) !important;
}

/* ============================================================================
   CHIP BUTTONS - MINIMAL STYLE
   ============================================================================ */
[data-testid="baseButton-secondary"] {
    background: #f1f5f9 !important;
    color: #475569 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    box-shadow: var(--md-shadow-1) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: scaleUp 0.3s ease-out;
    margin: 4px !important;
}

[data-testid="baseButton-secondary"]:hover {
    background: #6366f1 !important;
    color: white !important;
    border-color: #6366f1 !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--md-shadow-3) !important;
}

/* Selected chip */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    box-shadow: var(--md-shadow-2) !important;
    animation: smoothPulse 2s ease-in-out infinite !important;
}

[data-testid="baseButton-primary"]:hover {
    transform: scale(1.05) !important;
    box-shadow: var(--md-shadow-3) !important;
}

/* ============================================================================
   MATERIAL CARDS FOR CHAT
   ============================================================================ */
.stChatMessage {
    background: white !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
    box-shadow: var(--md-shadow-2) !important;
    animation: cardFlip 0.5s ease-out;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid #f1f5f9;
}

.stChatMessage:hover {
    transform: translateY(-4px) !important;
    box-shadow: var(--md-shadow-4) !important;
}

/* User messages */
.stChatMessage[data-testid*="user"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none;
}

.stChatMessage[data-testid*="user"]:hover {
    box-shadow: 0 15px 30px rgba(99, 102, 241, 0.3) !important;
}

/* AI messages */
.stChatMessage[data-testid*="assistant"] {
    background: white !important;
    color: #334155 !important;
}

/* ============================================================================
   SMOOTH INPUT FIELDS
   ============================================================================ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: white !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 0.85rem 1rem !important;
    color: #1e293b !important;
    font-size: 1rem !important;
    box-shadow: var(--md-shadow-1) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1), var(--md-shadow-2) !important;
    outline: none;
}

.stChatInputContainer {
    background: white !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 16px !important;
    box-shadow: var(--md-shadow-2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stChatInputContainer:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1), var(--md-shadow-3) !important;
}

/* ============================================================================
   SELECT BOXES
   ============================================================================ */
.stSelectbox > div > div {
    background: white !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    color: #334155 !important;
    box-shadow: var(--md-shadow-1) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stSelectbox > div > div:hover {
    border-color: #cbd5e1 !important;
    box-shadow: var(--md-shadow-2) !important;
}

/* ============================================================================
   MATERIAL SIDEBAR
   ============================================================================ */
section[data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: var(--md-shadow-2);
    animation: slideUpFade 0.6s ease-out;
}

section[data-testid="stSidebar"] > div {
    padding: 2rem 1.5rem !important;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #1e293b !important;
}

/* ============================================================================
   ELEVATED METRICS
   ============================================================================ */
.stMetric {
    background: white !important;
    padding: 1.5rem !important;
    border-radius: 16px !important;
    box-shadow: var(--md-shadow-2) !important;
    animation: scaleUp 0.4s ease-out;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid #f1f5f9;
}

.stMetric:hover {
    transform: translateY(-6px) !important;
    box-shadow: var(--md-shadow-4) !important;
    animation: breathe 2s ease-in-out infinite;
}

.stMetric label {
    color: #64748b !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stMetric [data-testid="stMetricValue"] {
    color: #6366f1 !important;
    font-size: 2.25rem !important;
    font-weight: 700 !important;
}

/* ============================================================================
   MATERIAL PROGRESS BAR
   ============================================================================ */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
    border-radius: 8px !important;
    position: relative;
    overflow: hidden;
}

.stProgress > div > div > div::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: smoothWave 2s linear infinite;
}

.stProgress > div > div {
    background: #e2e8f0 !important;
    border-radius: 8px !important;
    height: 8px !important;
    overflow: hidden;
}

/* ============================================================================
   MATERIAL ALERTS
   ============================================================================ */
.stSuccess, .stError, .stWarning, .stInfo {
    background: white !important;
    border-left: 4px solid !important;
    border-radius: 12px !important;
    padding: 1rem 1.5rem !important;
    box-shadow: var(--md-shadow-2) !important;
    animation: slideUpFade 0.4s ease-out;
}

.stSuccess {
    border-left-color: #10b981 !important;
    color: #065f46 !important;
}

.stError {
    border-left-color: #ef4444 !important;
    color: #991b1b !important;
}

.stWarning {
    border-left-color: #f59e0b !important;
    color: #78350f !important;
}

.stInfo {
    border-left-color: #3b82f6 !important;
    color: #1e3a8a !important;
}

/* ============================================================================
   DOWNLOAD BUTTON
   ============================================================================ */
.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.875rem 1.75rem !important;
    font-weight: 600 !important;
    box-shadow: var(--md-shadow-2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: scaleUp 0.4s ease-out;
}

.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--md-shadow-4) !important;
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
}

/* ============================================================================
   DIVIDERS
   ============================================================================ */
hr {
    border: none !important;
    height: 1px !important;
    background: #e2e8f0 !important;
    margin: 2rem 0 !important;
}

/* ============================================================================
   SCROLLBAR
   ============================================================================ */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

/* ============================================================================
   CAPTION
   ============================================================================ */
.stCaption {
    color: #64748b !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
}

/* ============================================================================
   STAGGERED CARDS
   ============================================================================ */
div[data-testid="column"] {
    animation: slideUpFade 0.5s ease-out;
}

div[data-testid="column"]:nth-child(1) { animation-delay: 0.05s; }
div[data-testid="column"]:nth-child(2) { animation-delay: 0.10s; }
div[data-testid="column"]:nth-child(3) { animation-delay: 0.15s; }
div[data-testid="column"]:nth-child(4) { animation-delay: 0.20s; }

/* ============================================================================
   RESPONSIVE
   ============================================================================ */
@media (max-width: 768px) {
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.65rem !important; }
    .stButton > button { padding: 0.875rem 1.5rem !important; }
}

/* ============================================================================
   LARGE CENTERED CATEGORY IMAGES
   ============================================================================ */

/* Center image containers */
[data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin: 20px auto !important;
}

/* Make images large and centered */
[data-testid="stImage"] img {
    width: 220px !important;
    height: 220px !important;
    object-fit: cover !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
    margin: 0 auto !important;
    display: block !important;
    transition: transform 0.3s ease !important;
}

/* Hover effect for images */
[data-testid="stImage"] img:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2) !important;
}

/* Center all column content */
[data-testid="column"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
}

/* Center buttons */
.stButton {
    display: flex !important;
    justify-content: center !important;
}

/* Center captions */
.stCaption {
    text-align: center !important;
}

</style>
""", unsafe_allow_html=True)


def display_progress(session_state):
    """Display progress in sidebar"""
    if session_state.selected_category:
        from config import CATEGORIES
        cat_data = CATEGORIES[session_state.selected_category]
        total_q = len(cat_data["questions"])
        answered = sum(1 for q in cat_data["questions"] 
                      if session_state.answers_json.get(q["id"], "").strip())
        
        progress_pct = answered / total_q
        st.progress(progress_pct, text=f"{answered}/{total_q} answered ({int(progress_pct*100)}%)")