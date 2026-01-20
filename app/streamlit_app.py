import streamlit as st
import pandas as pd
import cv2
import numpy as np
import tempfile
import os
from src.detector import SafetyMonitor

st.set_page_config(page_title="PPE Safety Monitor", layout="wide")
st.title("🛡️ PPE Safety Compliance Monitor")

st.sidebar.header("Upload Video")
uploaded_file = st.sidebar.file_uploader("Upload video for PPE analysis", type=["mp4", "avi", "mov", "mkv"])

# Model selection
model_options = {
    "YOLOv8 Nano (Fast)": "yolov8n.pt",
    "YOLOv8 Small": "yolov8s.pt",
    "YOLOv8 Medium": "yolov8m.pt",
    "Custom PPE Model": "runs/detect/train/weights/best.pt"  # If trained
}
selected_model = st.sidebar.selectbox("Select Model", list(model_options.keys()))

if uploaded_file is not None:
    # Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_file.read())
        video_path = tmp_file.name

    st.video(video_path)

    # Initialize detector
    try:
        detector = SafetyMonitor(model_path=model_options[selected_model])

        # Process video
        with st.spinner("Processing video for PPE compliance..."):
            compliance_data = detector.process_video(video_path)

        # Clean up temp file
        os.unlink(video_path)

        if compliance_data:
            # Convert to DataFrame for display
            df_compliance = pd.DataFrame(compliance_data)

            st.subheader("📊 Compliance Summary")

            # Overall statistics
            total_frames = df_compliance['frame'].max() + 1 if 'frame' in df_compliance.columns else 1
            total_violations = len(df_compliance[df_compliance['status'] == 'Violation'])
            total_safe = len(df_compliance[df_compliance['status'] == 'Safe'])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Persons Detected", len(df_compliance))
            with col2:
                st.metric("Safe Compliance", total_safe)
            with col3:
                st.metric("Violations Found", total_violations)

            # Detailed results
            st.subheader("📋 Detailed Compliance Report")
            st.dataframe(df_compliance)

            # Violation breakdown
            if total_violations > 0:
                st.subheader("🚨 Violation Details")
                violations_df = df_compliance[df_compliance['status'] == 'Violation']
                violation_counts = {}
                for violations in violations_df['violations']:
                    for v in violations:
                        violation_counts[v] = violation_counts.get(v, 0) + 1

                st.bar_chart(pd.DataFrame.from_dict(violation_counts, orient='index', columns=['Count']))

            # Export option
            if st.button("Export Compliance Report"):
                csv = df_compliance.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="ppe_compliance_report.csv",
                    mime="text/csv"
                )

        else:
            st.warning("No persons detected in the video. Please check the model and video quality.")

    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        st.info("Make sure you have the required dependencies installed: pip install -r requirements.txt")

else:
    st.info("👆 Upload a video file in the sidebar to start PPE compliance analysis.")

    st.subheader("📖 How to Use")
    st.markdown("""
    1. **Upload Video**: Select a video file containing people wearing or not wearing PPE
    2. **Choose Model**: Select a YOLO model (Nano for speed, Medium for accuracy)
    3. **Process**: The system will detect persons and check for required PPE items
    4. **Review Results**: View compliance summary and detailed violation reports

    **Required PPE Items Checked:**
    - Helmet/Hardhat
    - Goggles/Glasses
    - Mask
    - Gloves
    - Shoes/Boots

    **Note**: For best results, train a custom model on PPE data from Roboflow Universe.
    """)

    st.subheader("🎯 Training Your Own Model")
    st.markdown("""
    To improve accuracy for your specific environment:

    1. Go to [Roboflow Universe](https://universe.roboflow.com/) and search for "PPE detection"
    2. Download a dataset with classes: person, helmet, goggles, mask, gloves, shoes
    3. Extract frames from your lab videos and label them
    4. Train using: `yolo train data=ppe_dataset.yaml model=yolov8n.pt epochs=100`
    5. Use the trained weights in the model selection above
    """)
