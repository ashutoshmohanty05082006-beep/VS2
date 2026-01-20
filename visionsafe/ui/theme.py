"""
Theme configuration: CSS styling and color scheme.
Professional light theme for VisionSafe.
"""


def load_theme() -> None:
    """Load custom CSS theme for the application."""
    import streamlit as st
    
    st.markdown("""
        <style>
            /* Main Background */
            .stApp {
                background-color: #FFFFFF;
            }
            
            /* Sidebar */
            section[data-testid="stSidebar"] {
                background-color: #F0F2F6;
            }
            
            /* Text Colors */
            h1, h2, h3, h4, h5, h6, p, span, div {
                color: #31333F !important;
            }
            
            /* Metric Cards */
            div[data-testid="stMetricValue"] {
                color: #00C853 !important;
            }
            div[data-testid="stMetricLabel"] {
                color: #707070 !important;
            }
            
            /* Hide Footer & Menu */
            #MainMenu {visibility: visible;}
            footer {visibility: hidden;}
            header[data-testid="stHeader"] { 
                background-color: rgba(0,0,0,0); 
            }
            
            /* Alert Boxes */
            .stAlert {
                background-color: #E8F5E9;
                color: #1B5E20;
                border: 1px solid #C8E6C9;
            }
        </style>
    """, unsafe_allow_html=True)


# Color constants
COLORS = {
    'primary_green': '#00C853',      # Success/Safe
    'warning_orange': '#FF9800',      # Unsafe
    'danger_red': '#F44336',          # Critical/Fired
    'info_blue': '#2196F3',           # Info
    'light_gray': '#F9FAFB',          # Card backgrounds
    'border_gray': '#E0E0E0',         # Borders
    'text_dark': '#31333F',           # Primary text
    'text_light': '#707070'           # Secondary text
}
