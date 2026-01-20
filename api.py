"""
VisionSafe API Bridge
Standalone FastAPI server that serves stats to frontend dashboards.
Run with: uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import os
import cv2
import shutil
import uuid
import random
import csv
from datetime import datetime
from pathlib import Path

# --- PDF GENERATION IMPORTS ---
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = FastAPI(title="VisionSafe API", version="1.0.0")

# Load YOLO model at startup
try:
    from ultralytics import YOLO
    model = YOLO("models/best.pt")
    print("✅ YOLO model loaded successfully!")
except Exception as e:
    print(f"⚠️ YOLO model failed to load: {e}")
    model = None

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folders Setup
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
EVIDENCE_FOLDER = "evidence_snaps"

for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, EVIDENCE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Serve static files (Snapshots live here!)
app.mount("/evidence", StaticFiles(directory=EVIDENCE_FOLDER), name="evidence")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/stats")
def get_stats():
    if os.path.exists("safety_database.csv"):
        try:
            df = pd.read_csv("safety_database.csv")
            df = df.fillna("")
            
            if df.empty:
                return {"total_violations": 0, "unique_workers": 0, "critical_issue": "None", "status": "ready"}
            
            return {
                "total_violations": len(df),
                "unique_workers": int(df['ID'].nunique()),
                "critical_issue": str(df['Violation'].mode()[0]) if not df.empty else "None",
                "status": "live"
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}
    return {"total_violations": 0, "unique_workers": 0, "critical_issue": "None", "status": "no_data"}

@app.get("/recent")
def get_recent(limit: int = 10):
    if os.path.exists("safety_database.csv"):
        try:
            df = pd.read_csv("safety_database.csv")
            df = df.fillna("-")
            if df.empty: return []
            records = df.tail(limit).to_dict(orient="records")
            return list(reversed(records))
        except Exception as e:
            return []
    return []

# --- NEW ENDPOINT: REPORT & LEADERBOARD STATS ---
@app.get("/report_stats")
def get_report_stats():
    if not os.path.exists("safety_database.csv"):
        return {"leaderboard": [], "recent_confidence": []}

    try:
        df = pd.read_csv("safety_database.csv")
        df = df.fillna("-")

        # 1. LEADERBOARD LOGIC (Sincerity Rating)
        # We calculate "Stars" based on violation frequency.
        # Fewer violations = Higher Rating.
        worker_counts = df['ID'].value_counts().to_dict()
        leaderboard = []
        
        for worker_id, violation_count in worker_counts.items():
            # Base score 5.0, deduct 0.5 per violation, minimum 1.0
            stars = max(1.0, 5.0 - (violation_count * 0.5))
            leaderboard.append({
                "id": worker_id,
                "violations": int(violation_count),
                "stars": stars
            })
        
        # Sort by stars (descending)
        leaderboard = sorted(leaderboard, key=lambda x: x['stars'], reverse=True)
        
        # 2. CONFIDENCE SCORE LOGIC
        # "The more PPE worn = Higher Confidence"
        recent_scans = []
        for _, row in df.tail(10).iterrows(): # Last 10 scans
            violation_str = str(row.get("Violation", ""))
            
            # Count missing items
            missing_items = [x.strip() for x in violation_str.split(",")] if violation_str else []
            missing_count = len(missing_items)
            
            # Assume 5 standard PPE items (Helmet, Vest, Gloves, Goggles, Shoes)
            total_items = 5
            worn_count = max(0, total_items - missing_count)
            
            # Calculate Confidence %
            confidence_score = int((worn_count / total_items) * 100)
            
            # Determine Alert Status
            status_text = "Standard Alert"
            if confidence_score < 50:
                status_text = "Advisory Alert (High Risk)"
            
            recent_scans.append({
                "worker_id": row.get("ID", "Unknown"),
                "time": row.get("Time", "-"),
                "score": confidence_score,
                "status": status_text,
                "missing_count": missing_count
            })

        return {
            "leaderboard": leaderboard[:5], # Top 5 workers
            "recent_confidence": list(reversed(recent_scans)) # Newest first
        }

    except Exception as e:
        print(f"Report Error: {e}")
        return {"leaderboard": [], "recent_confidence": []}

# --- PDF DOWNLOAD ENDPOINT ---
@app.get("/download_report")
def download_report():
    if not os.path.exists("safety_database.csv"):
        return JSONResponse(content={"error": "No database found"}, status_code=404)

    try:
        df = pd.read_csv("safety_database.csv")
        df = df.fillna("-")
        
        pdf_filename = f"Safety_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(PROCESSED_FOLDER, pdf_filename)
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"VisionSafe Compliance Report", styles['Title']))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        data = [["Worker ID", "Violation", "Time"]]
        for _, row in df.iterrows():
            data.append([str(row.get("ID", "-")), str(row.get("Violation", "-")), str(row.get("Time", "-"))])

        table = Table(data, colWidths=[100, 250, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        return FileResponse(pdf_path, filename=pdf_filename, media_type='application/pdf')

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ============================================================================
# 🎞️ VIDEO PROCESSING
# ============================================================================

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    if model is None:
        return JSONResponse(content={"error": "YOLO model not loaded"}, status_code=500)

    try:
        ext = file.filename.split(".")[-1]
        unique_id = str(uuid.uuid4())[:8]
        safe_name = f"video_{unique_id}.{ext}"
        input_path = os.path.join(UPLOAD_FOLDER, safe_name)

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"📥 Received file: {safe_name}")

        output_filename = f"processed_{unique_id}.webm"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)
        
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        new_width = 640
        new_height = int((new_width / orig_w) * orig_h)
        
        fourcc = cv2.VideoWriter_fourcc(*'vp09') 
        out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))
        if not out.isOpened():
             fourcc = cv2.VideoWriter_fourcc(*'vp80')
             out = cv2.VideoWriter(output_path, fourcc, fps, (new_width, new_height))

        frame_count = 0
        last_annotated = None
        
        db_file = "safety_database.csv"
        if not os.path.exists(db_file):
            with open(db_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Violation", "Time", "Evidence"])

        print(f"🎬 Processing {safe_name} (Full PPE Check Active)...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            frame_resized = cv2.resize(frame, (new_width, new_height))

            if frame_count % 5 == 0:
                results = model(frame_resized, verbose=False)
                last_annotated = results[0].plot()

                if frame_count % 30 == 0: 
                    class_indices = results[0].boxes.cls.cpu().numpy()
                    names = results[0].names
                    detected_items = [names[int(c)] for c in class_indices]

                    if 'Person' in detected_items or 'person' in detected_items:
                        required_gear = ["Helmet", "Vest", "Gloves", "Goggles", "Shoes"] 
                        missing_gear = []

                        for gear in required_gear:
                            is_present = any(gear.lower() in d.lower() for d in detected_items)
                            if not is_present:
                                missing_gear.append(gear + " Missing")

                        if missing_gear:
                            violation_text = ", ".join(missing_gear)
                            
                            snapshot_filename = f"violation_{unique_id}_{frame_count}.jpg"
                            snapshot_path = os.path.join(EVIDENCE_FOLDER, snapshot_filename)
                            cv2.imwrite(snapshot_path, last_annotated)

                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            worker_id = f"Worker-{random.randint(100, 999)}"
                            
                            try:
                                with open(db_file, 'a', newline='') as f:
                                    writer = csv.writer(f)
                                    writer.writerow([worker_id, violation_text, timestamp, snapshot_filename])
                                    f.flush() 
                                    print(f"📝 Logged: {violation_text}")
                            except Exception as e:
                                print(f"Write Error: {e}")

            out.write(last_annotated if last_annotated is not None else frame_resized)
            frame_count += 1
            
            if frame_count % 30 == 0:
                print(f"⏳ Processed {frame_count} frames...")

        cap.release()
        out.release()
        print(f"✅ Analysis Complete! File: {output_filename}")

        return {
            "status": "success",
            "filename": output_filename,
            "video_url": f"/video/{output_filename}",
            "url": f"/video/{output_filename}"
        }

    except Exception as e:
        print(f"❌ Processing Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/video/{filename}")
async def serve_video(filename: str):
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(file_path, media_type="video/webm")

@app.post("/clear-database")
def clear_database():
    try:
        if os.path.exists("safety_database.csv"):
            os.remove("safety_database.csv")
        return {"status": "cleared"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)