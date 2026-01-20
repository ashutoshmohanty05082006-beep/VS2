
# 🎬 Video Upload & Analysis Feature

## Overview

Your backend now has a **video processing endpoint** that:
1. Accepts video uploads from your friend's frontend
2. Runs YOLO on every frame
3. Draws bounding boxes (persons, PPE, violations)
4. Returns the processed video for download

This is a **powerful demo feature** because:
- ✅ Works offline (don't need live camera)
- ✅ Shows worst-case scenarios (pre-recorded problematic videos)
- ✅ Gives audience time to see results without pressure

---

## 🖥️ Backend Setup (Already Done)

Your `api.py` now has these endpoints:

### POST `/upload_video`
Upload a video file and get it processed:
```bash
curl -X POST -F "file=@demo.mp4" http://localhost:8000/upload_video
```

**Response:**
```json
{
  "status": "completed",
  "message": "Processed 150 frames",
  "video_url": "/processed_video/processed_demo.mp4",
  "filename": "processed_demo.mp4"
}
```

### GET `/processed_video/{filename}`
Stream or download the processed video:
```
http://localhost:8000/processed_video/processed_demo.mp4
```

### GET `/processed_videos`
List all processed videos:
```
http://localhost:8000/processed_videos
```

---

## 👩‍💻 Frontend Setup (For Your Friend)

### Option 1: Standalone HTML Page (Easiest)
1. Open the file `upload.html` (we created it)
2. Update line 213 with your public API URL:
```javascript
const API_URL = "https://didactic-space-engine-7vj9rvw54979fx7jq-8000.app.github.dev"; // Your forwarded address
```
3. **Open `upload.html` in a browser** → Done!

### Option 2: Integrate into Existing Dashboard
If she has her own frontend, add this JavaScript:

```html
<!-- Include in her HTML -->
<div id="uploadForm">
    <input type="file" id="videoFile" accept="video/*">
    <button onclick="uploadAndAnalyze()">Upload & Analyze</button>
    <div id="loading" style="display:none;">
        <p>Processing... (may take 20-30 seconds)</p>
    </div>
    <video id="resultVideo" controls style="display:none;"></video>
</div>

<script>
    const API_URL = "https://YOUR_PUBLIC_API_URL"; // Update this!

    async function uploadAndAnalyze() {
        const file = document.getElementById("videoFile").files[0];
        if (!file) {
            alert("Please select a video");
            return;
        }

        document.getElementById("loading").style.display = "block";
        document.getElementById("resultVideo").style.display = "none";

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(`${API_URL}/upload_video`, {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.status === "completed") {
                const videoURL = API_URL + data.video_url;
                document.getElementById("resultVideo").src = videoURL;
                document.getElementById("resultVideo").style.display = "block";
            } else {
                alert("Error: " + data.error);
            }
        } catch (err) {
            alert("Failed to upload: " + err.message);
        } finally {
            document.getElementById("loading").style.display = "none";
        }
    }
</script>
```

---

## ⚠️ Important Notes

### Processing Time
- **On cloud (Codespaces):** ~2-3 seconds per 1 second of video
- A 10-second clip = ~20-30 seconds processing
- **Demo rule:** Use only **5-10 second clips**

### Supported Formats
Any format OpenCV can read:
- MP4, AVI, MOV, MKV, WebM, etc.

### Storage
- Uploaded files go to: `uploads/`
- Processed files go to: `processed/`
- Automatically cleaned up (or manually if needed)

---

## 📋 Checklist Before Demo

**Backend:**
- [ ] API is running on port 8000 (public)
- [ ] `uploads/` folder exists
- [ ] `processed/` folder exists
- [ ] Model is available at `models/best.pt`

**Frontend (Her Part):**
- [ ] `upload.html` is ready (or integrated into her site)
- [ ] API_URL is updated to your public forwarded address
- [ ] No trailing slash in API_URL
- [ ] Tested with short video clip (5-10 seconds)

---

## 🚀 Demo Script

1. **Open `upload.html` in browser**
2. **Select a short demo video** (fire, person without helmet, etc.)
3. **Click "Upload & Analyze"**
4. **Wait 20-30 seconds** while it processes
5. **Show the result video** with bounding boxes drawn on every frame

Judges love this because:
- Shows your model works on real data
- Demonstrates "production-ready" features
- Gives you time to explain what's happening
- Works even if live camera fails

---

## 🔧 Troubleshooting

### "Cannot fetch from API"
- API_URL is wrong
- Port 8000 is not public
- Check browser console (F12) for details

### "Video won't play"
- Try different video format (MP4 usually works best)
- Check video wasn't corrupted during upload
- Try shorter clip (under 10 seconds)

### Processing takes forever
- Video is too long → use shorter clip
- Cloud server is slow → normal
- Check terminal for errors

### CORS Error
- Already fixed in backend
- If still getting errors, clear browser cache

---

## 📝 Example Demo Videos

Create short test videos with:
- Person **missing helmet** (violation ✓)
- Person **fully equipped** (safe ✓)  
- Multiple people in frame
- Partial PPE (edge cases)

---

## ✅ You're Ready!

This feature transforms your demo from "just statistics" to **"here's proof it works in real scenarios"**. 🎬

**Send this guide to your friend** and she can integrate it into her dashboard!
