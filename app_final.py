import streamlit as st
import cv2
import pandas as pd
from ultralytics import YOLO
import time
from datetime import datetime
import tempfile
import os
from fpdf import FPDF

# --- SETUP EVIDENCE FOLDER ---
if not os.path.exists("evidence_snaps"):
    os.makedirs("evidence_snaps")

# --- PAGE CONFIG ---
st.set_page_config(page_title="VisionSafe AI", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

# --- CUSTOM CSS (CLEAN LIGHT THEME) ---
st.markdown("""
    <style>
        /* 1. Main Background */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* 2. Sidebar Background */
        section[data-testid="stSidebar"] {
            background-color: #F0F2F6;
        }
        
        /* 3. Text Colors (Must be DARK now!) */
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: #31333F !important;
        }
        
        /* 4. Metric Cards */
        div[data-testid="stMetricValue"] {
            color: #00C853 !important; /* VisionSafe Green */
        }
        div[data-testid="stMetricLabel"] {
            color: #707070 !important; /* Lighter Grey for labels */
        }
        
        /* 5. Tidy Up UI */
        #MainMenu {visibility: visible;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
        
        /* 6. Custom Alert Boxes */
        .stAlert {
            background-color: #E8F5E9; /* Very light green background for alerts */
            color: #1B5E20; /* Dark green text */
            border: 1px solid #C8E6C9;
        }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURATION ---
MAX_STRIKES = 15  # Strictness (Lower = Stricter)
COOLDOWN_SECONDS = 5 # Anti-Spam Timer

# --- STATE MANAGEMENT ---
if 'worker_db' not in st.session_state:
    st.session_state['worker_db'] = {} 
if 'violation_log' not in st.session_state:
    st.session_state['violation_log'] = []

# --- SIDEBAR NAVIGATION ---
# Load Custom Logo if it exists, otherwise skip
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=150)

st.sidebar.title("VisionSafe")
page = st.sidebar.radio("Menu", ["📹 Live Monitor", "📊 Analytics", "📝 Violations Log"])
st.sidebar.markdown("---")

# --- HELPER FUNCTIONS ---
def get_missing_gear(person_box, ppe_boxes, ppe_classes):
    x1, y1, x2, y2 = person_box
    detected_gear = set()

    for box, cls_id in zip(ppe_boxes, ppe_classes):
        bx1, by1, bx2, by2 = box
        center_x = (bx1 + bx2) / 2
        center_y = (by1 + by2) / 2
        
        if x1 < center_x < x2 and y1 < center_y < y2:
            if cls_id == 1: detected_gear.add('Helmet')
            elif cls_id == 2: detected_gear.add('Welding Helmet')
            elif cls_id == 3: detected_gear.add('Goggles')
            elif cls_id == 4: detected_gear.add('Vest')
            elif cls_id == 5: detected_gear.add('Gloves')
            elif cls_id == 6: detected_gear.add('Shoes')

    missing = []
    if 'Vest' not in detected_gear: missing.append('Vest')
    if 'Gloves' not in detected_gear: missing.append('Gloves')
    if 'Shoes' not in detected_gear: missing.append('Shoes')
    
    has_head_protection = ('Helmet' in detected_gear) or \
                          ('Welding Helmet' in detected_gear) or \
                          ('Goggles' in detected_gear)
    
    if not has_head_protection:
        missing.append('Headgear')

    return missing

@st.cache_resource
def load_model(path):
    return YOLO(path)

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # 1. Add Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="VisionSafe Compliance Report", ln=True, align='C')
    pdf.ln(10) # Add a break
    
    # 2. Add Timestamp of Report
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    
    # 3. Simple Table Layout
    pdf.set_font("Arial", size=10)
    
    # Header
    pdf.set_font("Arial", style="B", size=10)
    col_width = 45 # Width of each column
    headers = ["Time", "ID", "Violation", "Strikes"]
    
    for head in headers:
        pdf.cell(col_width, 10, head, border=1)
    pdf.ln()
    
    # Rows
    pdf.set_font("Arial", size=10)
    for index, row in df.iterrows():
        # Truncate text to avoid breaking the PDF layout
        time_txt = str(row['Time'])[:19]
        id_txt = str(row['ID'])
        vio_txt = str(row['Violation'])[:20] 
        strike_txt = str(row['Strikes'])
        
        # We only print these 4 columns
        pdf.cell(col_width, 10, time_txt, border=1)
        pdf.cell(col_width, 10, id_txt, border=1)
        pdf.cell(col_width, 10, vio_txt, border=1)
        pdf.cell(col_width, 10, strike_txt, border=1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ==========================================
# PAGE 1: LIVE MONITOR (With Turbo Mode)
# ==========================================
if page == "📹 Live Monitor":
    st.title("📹 Live Safety Monitor")
    
    # Settings in Sidebar
    conf_slide = st.sidebar.slider("AI Confidence", 0.0, 1.0, 0.4, 0.05)
    model_path = st.sidebar.text_input("Model Path", "models/best.pt")
    source_option = st.sidebar.selectbox("Input Source", ["Upload Video", "Webcam"])
    
    start_btn = st.sidebar.checkbox("🚀 Start System", value=False)
    
    if start_btn:
        try:
            model = load_model(model_path)
        except Exception as e:
            st.error(f"Error loading model: {e}")
            st.stop()
            
        cap = None
        tfile = None
        
        # --- SOURCE LOGIC ---
        if source_option == "Webcam":
            cap = cv2.VideoCapture(0)
            
        elif source_option == "Upload Video":
            uploaded_file = st.sidebar.file_uploader("Upload footage", type=['mp4', 'avi', 'mov'])
            if uploaded_file:
                # Reset button logic
                if st.sidebar.button("🔄 Reset Video"):
                    st.rerun()
                    
                # Save to temp file safely
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(uploaded_file.read())
                tfile.close() # Close file so OpenCV can open it
                
                cap = cv2.VideoCapture(tfile.name)
            else:
                st.info("⚠️ Please upload a video file to begin analysis.")
                st.stop()
        
        # --- PROCESSING LOOP ---
        col1, col2 = st.columns([0.7, 0.3])
        st_frame = col1.empty()
        st_log = col2.empty()
        
        if cap:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: 
                    st.warning("Video Feed Ended.")
                    break
                
                # ⚡ TURBO MODE ENABLED ⚡
                # Resizing frame to 640px width ensures high FPS on cloud
                orig_h, orig_w = frame.shape[:2]
                new_w = 640
                new_h = int((new_w / orig_w) * orig_h)
                frame = cv2.resize(frame, (new_w, new_h))

                # YOLO Tracking
                results = model.track(frame, persist=True, conf=conf_slide, verbose=False)
                
                if results[0].boxes.id is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy()
                    classes = results[0].boxes.cls.cpu().numpy()
                    track_ids = results[0].boxes.id.int().cpu().numpy()

                    person_indices = [i for i, cls in enumerate(classes) if cls == 0]
                    ppe_indices = [i for i, cls in enumerate(classes) if cls != 0]
                    
                    ppe_boxes = boxes[ppe_indices]
                    ppe_classes = classes[ppe_indices]

                    for idx in person_indices:
                        pid = track_ids[idx]
                        pbox = boxes[idx]
                        
                        missing_items = get_missing_gear(pbox, ppe_boxes, ppe_classes)
                        is_safe = len(missing_items) == 0
                        current_violation_signature = sorted(missing_items)

                        # --- DATABASE LOGIC ---
                        if pid not in st.session_state['worker_db']:
                            st.session_state['worker_db'][pid] = {
                                'strikes': 0, 'last_violation': [], 'last_strike_time': 0
                            }
                        
                        worker = st.session_state['worker_db'][pid]
                        current_time = time.time()
                        
                        # 1. Unsafe? 2. New Fault? 3. Cooldown Over?
                        is_new_fault = (current_violation_signature != worker['last_violation'])
                        is_cooldown_over = (current_time - worker['last_strike_time']) > COOLDOWN_SECONDS

                        if not is_safe and is_new_fault and is_cooldown_over:
                            worker['strikes'] += 1
                            worker['last_violation'] = current_violation_signature
                            worker['last_strike_time'] = current_time

                            # 📸 SNAPSHOT
                            timestamp_str = datetime.now().strftime("%H-%M-%S")
                            snap_filename = f"evidence_snaps/Worker{pid}_{timestamp_str}.jpg"
                            cv2.imwrite(snap_filename, frame)

                            violation_record = {
                                "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "ID": f"Worker-{pid}",
                                "Violation": ", ".join(missing_items),
                                "Strikes": worker['strikes'],
                                "Evidence": snap_filename
                            }
                            
                            st.session_state['violation_log'].append(violation_record)
                            
                            # CSV SAVE
                            df_new = pd.DataFrame([violation_record])
                            if os.path.isfile("safety_database.csv"):
                                df_existing = pd.read_csv("safety_database.csv")
                                df_final = pd.concat([df_existing, df_new], ignore_index=True).tail(500)
                                df_final.to_csv("safety_database.csv", index=False)
                            else:
                                df_new.to_csv("safety_database.csv", index=False)
                        
                        if is_safe:
                            worker['last_violation'] = []

                        # --- DRAWING ---
                        x1, y1, x2, y2 = map(int, pbox)
                        if worker['strikes'] >= MAX_STRIKES:
                            color = (0, 0, 255) # RED
                            label = f"ID:{pid} FIRED!"
                        elif not is_safe:
                            color = (0, 165, 255) # ORANGE
                            label = f"ID:{pid} {missing_items[0]}"
                        else:
                            color = (0, 255, 0) # GREEN
                            label = f"ID:{pid} SAFE"

                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                st_frame.image(frame, channels="BGR", use_container_width=True)
                
                # Live Status Panel
                with col2:
                    st.subheader("⚠️ Live Alerts")
                    if st.session_state['violation_log']:
                        df_log = pd.DataFrame(st.session_state['violation_log'])
                        st.dataframe(df_log.tail(5)[['Time', 'ID', 'Violation']], hide_index=True)
            
            cap.release()
            if tfile:
                os.remove(tfile.name)

# ==========================================
# PAGE 2: ANALYTICS
# ==========================================
elif page == "📊 Analytics":
    st.title("📊 Site Safety Analytics")
    
    if os.path.isfile("safety_database.csv"):
        df = pd.read_csv("safety_database.csv")
        
        col1, col2, col3 = st.columns(3)
        total_violations = len(df)
        col1.metric("Total Violations (Today)", total_violations, delta="Live Data")
        active_workers = df['ID'].nunique()
        col2.metric("Unique Violators", active_workers, delta="-2 from yesterday", delta_color="inverse")
        
        if not df.empty:
            top_violation = df['Violation'].mode()[0]
        else:
            top_violation = "None"
        col3.metric("Critical Issue", top_violation, delta="Needs Attention", delta_color="off")
        
        st.markdown("---")
        
        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            st.subheader("📈 Violations by Category")
            all_violations = []
            for v in df['Violation']:
                if isinstance(v, str):
                    all_violations.extend(v.split(", "))
            if all_violations:
                v_counts = pd.Series(all_violations).value_counts()
                st.bar_chart(v_counts, color="#00C853")
            else:
                st.info("No violation types recorded yet.")
            
        with c2:
            st.subheader("🕒 Activity Timeline")
            df['Hour'] = pd.to_datetime(df['Time']).dt.hour
            hourly_counts = df['Hour'].value_counts().sort_index()
            st.area_chart(hourly_counts, color="#FF5252")
    else:
        st.info("ℹ️ No data collected yet. Go to 'Live Monitor' and run a test!")

# ==========================================
# PAGE 3: FULL LOGS
# ==========================================
elif page == "📝 Violations Log":
    st.title("📝 Detailed Compliance Log")
    
    if os.path.isfile("safety_database.csv"):
        df = pd.read_csv("safety_database.csv")
        tab1, tab2 = st.tabs(["📄 Data Table", "📸 Evidence Locker"])
        
        with tab1:
            st.dataframe(df, use_container_width=True, height=400)
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, "safety_log.csv", "text/csv")
            with col2:
                if st.button("📄 Generate PDF Report"):
                    try:
                        pdf_bytes = create_pdf(df)
                        st.download_button("⬇️ Download PDF", pdf_bytes, "VisionSafe_Report.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"Error: {e}")

            with st.expander("🗑️ Clear Database"):
                if st.button("Delete All Records"):
                    if os.path.exists("safety_database.csv"):
                        os.remove("safety_database.csv")
                    if os.path.exists("evidence_snaps"):
                        for file in os.listdir("evidence_snaps"):
                            os.remove(os.path.join("evidence_snaps", file))
                    st.session_state['worker_db'] = {}
                    st.session_state['violation_log'] = []
                    st.success("Database & Evidence Wiped.")
                    st.rerun()

        with tab2:
            st.subheader("🔍 Forensic Evidence Viewer")
            if 'Evidence' in df.columns:
                evidence_df = df[df['Evidence'].notna()]
                if not evidence_df.empty:
                    evidence_options = [f"{row['Time']} | {row['ID']} | {row['Violation']}" for index, row in evidence_df.iterrows()]
                    selected_option = st.selectbox("Select an Incident to Review:", evidence_options)
                    if selected_option:
                        selected_index = evidence_options.index(selected_option)
                        selected_row = evidence_df.iloc[selected_index]
                        image_path = selected_row['Evidence']
                        
                        c1, c2 = st.columns([0.6, 0.4])
                        with c1:
                            if os.path.exists(image_path):
                                st.image(image_path, caption=f"Evidence: {selected_row['ID']}", use_container_width=True)
                            else:
                                st.error(f"⚠️ Image file missing: {image_path}")
                        with c2:
                            st.info(f"**Timestamp:** {selected_row['Time']}")
                            st.error(f"**Violation:** {selected_row['Violation']}")
                            st.warning(f"**Strike Count:** {selected_row['Strikes']}")
                            if os.path.exists(image_path):
                                with open(image_path, "rb") as file:
                                    st.download_button(label="💾 Download Proof", data=file, file_name=os.path.basename(image_path), mime="image/jpeg")
                else:
                    st.info("No snapshots recorded yet.")
            else:
                st.warning("Evidence column not found in database.")
    else:
        st.write("No records found.")