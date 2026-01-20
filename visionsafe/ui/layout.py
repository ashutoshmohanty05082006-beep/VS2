"""
Layout helpers: Dashboard layout utilities.
Reusable layout patterns for consistent UI.
"""

import streamlit as st
from .theme import COLORS


def page_header(title: str, subtitle: str = None, icon: str = "🛡️"):
    """
    Display a professional page header.
    
    Args:
        title: Page title
        subtitle: Optional subtitle
        icon: Emoji icon
    """
    st.markdown(f"""
    <div style="padding: 20px 0; border-bottom: 2px solid {COLORS['border_gray']};">
        <h1 style="margin: 0; color: {COLORS['text_dark']};">
            {icon} {title}
        </h1>
        {'<p style="margin: 8px 0 0 0; color: ' + COLORS['text_light'] + ';">' + subtitle + '</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")


def divider():
    """Display a horizontal divider."""
    st.markdown(f"""
    <hr style="border: none; border-top: 1px solid {COLORS['border_gray']}; margin: 20px 0;">
    """, unsafe_allow_html=True)


def section_header(title: str, icon: str = "📌"):
    """
    Display a section header within a page.
    
    Args:
        title: Section title
        icon: Emoji icon
    """
    st.markdown(f"""
    <h3 style="color: {COLORS['text_dark']}; border-bottom: 2px solid {COLORS['primary_green']}; padding-bottom: 8px;">
        {icon} {title}
    </h3>
    """, unsafe_allow_html=True)


def filter_panel(title: str = "Filters"):
    """
    Create a filter panel in sidebar.
    
    Returns:
        Expander for filter widgets
    """
    with st.sidebar:
        return st.expander(f"🔍 {title}", expanded=False)


def footer():
    """Display application footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #999; font-size: 12px; padding: 20px 0;">
        <p>VisionSafe AI • Workplace Safety Monitoring • Powered by YOLO</p>
    </div>
    """, unsafe_allow_html=True)
