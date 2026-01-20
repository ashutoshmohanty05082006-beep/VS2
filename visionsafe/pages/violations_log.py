"""
Violations Log Page: Detailed logs, evidence viewer, and exports.
"""

import streamlit as st
import pandas as pd
import os

from visionsafe.backend.database import load_database, export_csv, clear_database
from visionsafe.backend.evidence import clear_evidence_dir, get_evidence_files
from visionsafe.backend.pdf_report import create_pdf_report
from visionsafe.ui.layout import page_header, section_header, divider
from visionsafe.ui.components import info_box, status_badge
from visionsafe.ui.theme import COLORS


def violations_log_page():
    """Render the violations log page."""
    
    page_header("Compliance Log", "Detailed incident records and evidence", "📝")
    
    df = load_database()
    
    if df.empty:
        info_box(
            "No Records",
            "No violations have been recorded yet",
            "info"
        )
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📄 Data Table", "📸 Evidence Gallery", "⚙️ Admin"])
    
    # TAB 1: Data Table
    with tab1:
        section_header("Violation Records", "📋")
        
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        st.markdown("---")
        
        # Export buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="safety_compliance_log.csv",
                mime="text/csv"
            )
        
        with col2:
            try:
                pdf_bytes = create_pdf_report(df)
                if pdf_bytes:
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_bytes,
                        file_name="VisionSafe_Report.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"PDF generation error: {e}")
        
        with col3:
            st.info("📊 Generating analytics...")
    
    # TAB 2: Evidence Gallery
    with tab2:
        section_header("Evidence Gallery", "🔍")
        
        # Filter for rows with evidence
        if 'Evidence' in df.columns:
            evidence_df = df[df['Evidence'].notna() & (df['Evidence'] != '')]
            
            if not evidence_df.empty:
                # Create selectbox options
                evidence_options = [
                    f"{row['Time']} | {row['ID']} | {row['Violation']}"
                    for _, row in evidence_df.iterrows()
                ]
                
                selected_option = st.selectbox(
                    "Select an Incident to Review:",
                    evidence_options
                )
                
                if selected_option:
                    selected_index = evidence_options.index(selected_option)
                    selected_row = evidence_df.iloc[selected_index]
                    image_path = selected_row['Evidence']
                    
                    # Display layout
                    col_img, col_info = st.columns([0.6, 0.4])
                    
                    with col_img:
                        if os.path.exists(image_path):
                            st.image(
                                image_path,
                                caption=f"Evidence: {selected_row['ID']}",
                                use_container_width=True
                            )
                        else:
                            st.error(f"⚠️ Image not found: {image_path}")
                    
                    with col_info:
                        st.markdown("### Incident Details")
                        
                        st.metric("Timestamp", selected_row['Time'])
                        
                        status_badge('unsafe')
                        st.markdown(f"**Violation:** {selected_row['Violation']}")
                        
                        st.metric("Strike Count", int(selected_row['Strikes']))
                        
                        # Download button for individual image
                        if os.path.exists(image_path):
                            with open(image_path, "rb") as f:
                                st.download_button(
                                    label="💾 Download Evidence",
                                    data=f.read(),
                                    file_name=os.path.basename(image_path),
                                    mime="image/jpeg"
                                )
            else:
                info_box("No Evidence", "No snapshots recorded yet", "info")
        else:
            st.warning("Evidence column not found in database")
    
    # TAB 3: Admin Panel
    with tab3:
        section_header("Administration", "⚙️")
        
        st.subheader("Database Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Records", len(df))
            st.metric("Unique Workers", df['ID'].nunique())
        
        with col2:
            st.metric("Evidence Files", len(get_evidence_files()))
            st.info("System is operational")
        
        st.markdown("---")
        
        st.subheader("⚠️ Danger Zone")
        
        if st.checkbox("🗑️ Show Clear Database Options"):
            st.warning("This action cannot be undone!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Delete All Records"):
                    try:
                        clear_database()
                        clear_evidence_dir()
                        st.session_state['worker_db'] = {}
                        st.session_state['violation_log'] = []
                        st.success("✅ Database and evidence wiped successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing database: {e}")
            
            with col2:
                if st.button("Clear Evidence Only"):
                    try:
                        clear_evidence_dir()
                        st.success("✅ Evidence folder cleared")
                    except Exception as e:
                        st.error(f"Error clearing evidence: {e}")
