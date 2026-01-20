"""
Live Monitor Page: Real-time camera/video processing with live detection.
Main monitoring interface for safety compliance.
"""

import streamlit as st
import cv2
import tempfile
import time
from datetime import datetime

from visionsafe.backend.detection import load_model, run_detection, extract_detections, draw_annotations
from visionsafe.backend.ppe_detection import get_missing_gear
from visionsafe.backend.violations import update_strikes, get_worker_status, is_fired
from visionsafe.backend.evidence import save_snapshot
from visionsafe.backend.database import record_violation, save_violation
from visionsafe.ui.layout import page_header, section_header, divider
from visionsafe.ui.components import status_badge, info_box


def live_monitor_page():
    """Render the live monitor page."""
    
    page_header("Live Safety Monitor", "Real-time PPE compliance detection", "📹")
    
    # Sidebar settings
    with st.sidebar:
        st.subheader("⚙️ Settings")
        conf_threshold = st.slider("AI Confidence", 0.0, 1.0, 0.4, 0.05)
        model_path = st.text_input("Model Path", "models/best.pt")
        source_option = st.selectbox("Input Source", ["Webcam", "Upload Video"])
        
        st.markdown("---")
        max_strikes = st.slider("Max Strikes (Firing Threshold)", 5, 30, 15)
        cooldown = st.slider("Cooldown (seconds)", 1, 30, 5)
        
        st.markdown("---")
        start_btn = st.checkbox("🚀 Start System", value=False)
    
    # Initialize session state
    if 'worker_db' not in st.session_state:
        st.session_state['worker_db'] = {}
    if 'violation_log' not in st.session_state:
        st.session_state['violation_log'] = []
    
    if not start_btn:
        info_box(
            "Ready to Monitor",
            "Enable 'Start System' in the sidebar to begin real-time detection",
            "info"
        )
        return
    
    # Load model
    try:
        model = load_model(model_path)
    except Exception as e:
        st.error(f"❌ Error loading model: {e}")
        return
    
    # Get video source
    cap = None
    
    if source_option == "Webcam":
        cap = cv2.VideoCapture(0)
    else:  # Upload Video
        uploaded_file = st.sidebar.file_uploader("📹 Upload footage", type=['mp4', 'avi', 'mov', 'mkv'])
        
        if not uploaded_file:
            info_box("Upload Required", "Please upload a video file to begin analysis", "info")
            return
        
        if st.sidebar.button("🔄 Reset Video"):
            st.rerun()
        
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
    
    if not cap or not cap.isOpened():
        st.error("❌ Cannot open video source")
        return
    
    # Main monitoring layout
    col_video, col_status = st.columns([0.7, 0.3])
    
    st_frame = col_video.empty()
    
    frame_placeholder = col_video.empty()
    frame_count = [0]  # Use list to modify in nested scope
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                st.warning("⏹️ Video Feed Ended")
                break
            
            # Run detection
            results = run_detection(model, frame, conf=conf_threshold)
            
            # Extract detections
            boxes, classes, track_ids, person_indices, ppe_indices = extract_detections(results)
            
            if boxes is not None and len(person_indices) > 0:
                ppe_boxes = boxes[ppe_indices]
                ppe_classes = classes[ppe_indices]
                
                # Process each person
                for idx in person_indices:
                    pid = track_ids[idx]
                    pbox = boxes[idx]
                    
                    # Get missing gear
                    missing_items = get_missing_gear(pbox, ppe_boxes, ppe_classes)
                    is_safe = len(missing_items) == 0
                    
                    # Initialize worker if new
                    if pid not in st.session_state['worker_db']:
                        st.session_state['worker_db'][pid] = {
                            'strikes': 0,
                            'last_violation': [],
                            'last_strike_time': 0
                        }
                    
                    worker = st.session_state['worker_db'][pid]
                    
                    # Update strikes with cooldown logic
                    new_strike = update_strikes(worker, missing_items, cooldown)
                    
                    if new_strike:
                        # Save evidence
                        evidence_path = save_snapshot(frame, pid)
                        
                        # Record violation
                        violation = record_violation(
                            worker_id=pid,
                            missing_items=missing_items,
                            strikes=worker['strikes'],
                            evidence_path=evidence_path
                        )
                        save_violation(violation)
                        st.session_state['violation_log'].append(violation)
                    
                    # Get status for drawing
                    color, status_label, is_fired_flag = get_worker_status(
                        worker, missing_items, max_strikes
                    )
                    
                    # Draw on frame
                    x1, y1, x2, y2 = map(int, pbox)
                    
                    if is_fired_flag:
                        label = f"ID:{pid} FIRED!"
                    elif not is_safe:
                        label = f"ID:{pid} {missing_items[0]}"
                    else:
                        label = f"ID:{pid} SAFE"
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Display frame
            st_frame.image(frame, channels="BGR", use_container_width=True)
            
            # Update status panel
            with col_status:
                st.subheader("⚠️ Live Alerts")
                
                if st.session_state['violation_log']:
                    recent_violations = st.session_state['violation_log'][-5:]
                    
                    for v in reversed(recent_violations):
                        with st.container():
                            st.write(f"**{v['ID']}**")
                            st.caption(v['Violation'])
                            st.metric("Strikes", v['Strikes'])
                            st.divider()
                else:
                    st.info("No violations yet")
            
            frame_count[0] += 1
    
    finally:
        cap.release()
