"""
Analytics Page: Charts, metrics, and dashboard for safety analytics.
"""

import streamlit as st
import pandas as pd

from visionsafe.backend.database import load_database, get_statistics, get_violations_by_type, get_violations_by_hour
from visionsafe.ui.layout import page_header, section_header, divider
from visionsafe.ui.components import kpi_card, metric_row, info_box
from visionsafe.ui.theme import COLORS


def analytics_page():
    """Render the analytics page."""
    
    page_header("Site Safety Analytics", "Real-time compliance metrics and trends", "📊")
    
    df = load_database()
    
    if df.empty:
        info_box(
            "No Data Yet",
            "Run the Live Monitor to collect safety compliance data",
            "info"
        )
        return
    
    # Get statistics
    stats = get_statistics()
    
    # --- KPI METRICS ROW ---
    section_header("📈 Key Metrics", "📊")
    
    metrics = [
        {
            'title': 'Total Violations',
            'value': stats['total_violations'],
            'icon': '🚨',
            'color': COLORS['danger_red']
        },
        {
            'title': 'Unique Workers',
            'value': stats['unique_workers'],
            'icon': '👷',
            'color': COLORS['info_blue']
        },
        {
            'title': 'Critical Issue',
            'value': stats['most_common_violation'][:20] if len(stats['most_common_violation']) > 1 else 'N/A',
            'icon': '⚠️',
            'color': COLORS['warning_orange']
        }
    ]
    
    metric_row(metrics)
    
    divider()
    
    # --- VIOLATION CHARTS ---
    section_header("📉 Violation Analysis", "📉")
    
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.subheader("Violations by Type")
        violations_by_type = get_violations_by_type()
        
        if violations_by_type:
            violation_df = pd.DataFrame(
                list(violations_by_type.items()),
                columns=['Violation Type', 'Count']
            ).sort_values('Count', ascending=False)
            
            st.bar_chart(
                violation_df.set_index('Violation Type'),
                color=COLORS['primary_green']
            )
        else:
            st.info("No violation data available")
    
    with col2:
        st.subheader("Activity Timeline")
        violations_by_hour = get_violations_by_hour()
        
        if violations_by_hour:
            hour_df = pd.DataFrame(
                list(violations_by_hour.items()),
                columns=['Hour', 'Count']
            ).sort_values('Hour')
            hour_df['Hour'] = hour_df['Hour'].astype(str) + ":00"
            
            st.area_chart(
                hour_df.set_index('Hour'),
                color=COLORS['danger_red']
            )
        else:
            st.info("No hourly data available")
    
    divider()
    
    # --- WORKER VIOLATIONS TABLE ---
    section_header("Worker Violation Records", "👷")
    
    worker_summary = df.groupby('ID').agg({
        'Violation': 'count',
        'Strikes': 'max'
    }).rename(columns={'Violation': 'Total Incidents'}).sort_values('Strikes', ascending=False)
    
    st.dataframe(worker_summary, use_container_width=True)
    
    divider()
    
    # --- RECENT VIOLATIONS ---
    section_header("Recent Incidents", "🔔")
    
    recent = df.tail(10)[['Time', 'ID', 'Violation', 'Strikes']]
    st.dataframe(recent, use_container_width=True, hide_index=True)
