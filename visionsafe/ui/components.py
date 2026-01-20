"""
UI Components: Reusable Streamlit widgets and cards.
Professional dashboard components for data presentation.
"""

import streamlit as st
from .theme import COLORS


def kpi_card(title: str, value, icon: str = "📊", color: str = None, delta: str = None):
    """
    Display a KPI card with title, value, and icon.
    
    Args:
        title: Card title
        value: Main value to display
        icon: Emoji icon
        color: Hex color for value
        delta: Optional delta text
    """
    if color is None:
        color = COLORS['primary_green']
    
    delta_html = f"<small>{delta}</small>" if delta else ""
    
    st.markdown(f"""
    <div style="
        background: {COLORS['light_gray']};
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid {color};">
        <h4 style="color: {COLORS['text_light']}; margin: 0 0 10px 0;">{icon} {title}</h4>
        <h2 style="color: {color}; margin: 0;">{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str, label: str = None):
    """
    Display a status badge.
    
    Args:
        status: One of 'safe', 'unsafe', 'fired'
        label: Optional custom label
    """
    status_config = {
        'safe': {'color': COLORS['primary_green'], 'emoji': '✅', 'label': 'SAFE'},
        'unsafe': {'color': COLORS['warning_orange'], 'emoji': '⚠️', 'label': 'UNSAFE'},
        'fired': {'color': COLORS['danger_red'], 'emoji': '🚨', 'label': 'FIRED'}
    }
    
    config = status_config.get(status, status_config['safe'])
    display_label = label or config['label']
    
    st.markdown(f"""
    <span style="
        background: {config['color']}20;
        color: {config['color']};
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;">
        {config['emoji']} {display_label}
    </span>
    """, unsafe_allow_html=True)


def info_box(title: str, content: str, box_type: str = "info"):
    """
    Display an information box.
    
    Args:
        title: Box title
        content: Box content
        box_type: One of 'info', 'warning', 'error', 'success'
    """
    box_config = {
        'info': {'color': COLORS['info_blue'], 'icon': 'ℹ️'},
        'warning': {'color': COLORS['warning_orange'], 'icon': '⚠️'},
        'error': {'color': COLORS['danger_red'], 'icon': '❌'},
        'success': {'color': COLORS['primary_green'], 'icon': '✅'}
    }
    
    config = box_config.get(box_type, box_config['info'])
    
    st.markdown(f"""
    <div style="
        background: {config['color']}10;
        border-left: 4px solid {config['color']};
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;">
        <h4 style="color: {config['color']}; margin: 0 0 8px 0;">
            {config['icon']} {title}
        </h4>
        <p style="margin: 0; color: {COLORS['text_dark']};">{content}</p>
    </div>
    """, unsafe_allow_html=True)


def metric_row(metrics: list):
    """
    Display metrics in a row.
    
    Args:
        metrics: List of dicts with 'title', 'value', 'icon' keys
    """
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
            kpi_card(
                title=metric.get('title', ''),
                value=metric.get('value', '0'),
                icon=metric.get('icon', '📊'),
                color=metric.get('color')
            )


def stat_card(label: str, value, delta: str = None, delta_color: str = "normal"):
    """
    Display a simple stat card (wrapper around st.metric for consistency).
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta text
        delta_color: 'normal', 'inverse', or 'off'
    """
    st.metric(label, value, delta=delta, delta_color=delta_color)
