"""
Defines the visual design system, custom CSS styles, and theme settings.
Injects CSS for a premium dark cyber-theme, glassmorphic cards, custom typography,
vibrant neon gradients, and interactive hover effects.
"""

import streamlit as st

def set_page_theme():
    """Initializes Streamlit page configurations with title and layout."""
    st.set_page_config(
        page_title="CyberVision - Cyber Threat Intelligence Dashboard",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded"
    )

def inject_custom_css():
    """Injects high-fidelity custom CSS into Streamlit for premium aesthetics."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Outfit:wght@400;600;800&display=swap');
    
    /* Typography & Core Styling */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Premium Glassmorphic Cards */
    .metric-card {
        background: rgba(17, 25, 40, 0.65);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.085);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 20px;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 242, 254, 0.4);
        box-shadow: 0 12px 40px 0 rgba(0, 242, 254, 0.15);
    }
    
    /* Neon Status Indicators */
    .indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .indicator-green {
        background-color: #00ff87;
        box-shadow: 0 0 10px #00ff87;
    }
    .indicator-red {
        background-color: #ff0055;
        box-shadow: 0 0 10px #ff0055;
    }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #090e17;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Custom buttons style */
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.2);
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4);
        color: white;
    }
    
    /* Metric label and values */
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #8c9ba5;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        color: #ffffff;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
    }
    
    /* General App Wrapper styling */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Style the widgets and baseweb elements for dark mode consistency */
    div[data-baseweb="select"] > div {
        background-color: #0e1420 !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] * {
        color: #ffffff !important;
    }
    input {
        background-color: #0e1420 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Theme Palette configuration for Plotly Charts
COLOR_PALETTE = {
    "background": "#0b0f19",
    "card": "#111928",
    "primary": "#00f2fe",
    "secondary": "#4facfe",
    "accent": "#7f00ff",
    "neon_green": "#00ff87",
    "neon_pink": "#ff0055",
    "neon_yellow": "#ffdd00",
    "text": "#ffffff",
    "muted": "#8c9ba5",
    "grid": "rgba(255, 255, 255, 0.05)",
}

PLOTLY_THEME_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": COLOR_PALETTE["text"], "family": "Inter, sans-serif"},
    "xaxis": {
        "gridcolor": COLOR_PALETTE["grid"],
        "linecolor": COLOR_PALETTE["grid"],
        "zerolinecolor": COLOR_PALETTE["grid"],
        "tickfont": {"color": COLOR_PALETTE["muted"]}
    },
    "yaxis": {
        "gridcolor": COLOR_PALETTE["grid"],
        "linecolor": COLOR_PALETTE["grid"],
        "zerolinecolor": COLOR_PALETTE["grid"],
        "tickfont": {"color": COLOR_PALETTE["muted"]}
    },
    "legend": {"font": {"color": COLOR_PALETTE["muted"]}},
}
