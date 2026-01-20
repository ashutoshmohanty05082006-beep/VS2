"""
VisionSafe AI - Main Entry Point
Professional workplace safety monitoring with AI-powered PPE detection.
"""

import streamlit as st
from visionsafe.ui.theme import load_theme
from visionsafe.pages.live_monitor import live_monitor_page
from visionsafe.pages.analytics import analytics_page
from visionsafe.pages.violations_log import violations_log_page


def main():
    """Main application entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title="VisionSafe AI",
        layout="wide",
        page_icon="🛡️",
        initial_sidebar_state="expanded"
    )
    
    # Load theme
    load_theme()
    
    # Sidebar navigation
    with st.sidebar:
        st.image("assets/logo.png", width=140) if False else None  # Logo if exists
        st.title("VisionSafe AI")
        st.markdown("**Workplace Safety Monitoring**")
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            [
                "📹 Live Monitor",
                "📊 Analytics",
                "📝 Violations Log"
            ],
            label_visibility="collapsed"
        )
    
    # Route to appropriate page
    if page == "📹 Live Monitor":
        live_monitor_page()
    
    elif page == "📊 Analytics":
        analytics_page()
    
    elif page == "📝 Violations Log":
        violations_log_page()


if __name__ == "__main__":
    main()
