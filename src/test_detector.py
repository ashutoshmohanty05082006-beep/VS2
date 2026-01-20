from ultralytics import YOLO
import cv2
import os

# 1. Load your trained model
model_path = 'models/best.pt'
if not os.path.exists(model_path):
    print(f"❌ Error: Model not found at {model_path}")
    exit()

print(f"✅ Loading model from {model_path}...")
model = YOLO(model_path)

# 2. Open a test video (or use webcam with source=0)
# DO THIS: Drag a video into your 'data' folder and change the name below
video_path = 'data/test_video.mp4' 

if not os.path.exists(video_path):
    # If no video, let's try a single image just to test
    print(f"⚠️ Video {video_path} not found. Trying to predict on a sample image...")
    results = model.predict(source="data/val/images", save=True, conf=0.5)
    print(f"✅ Prediction done! Check the 'runs/detect' folder.")
    exit()

# 3. Run inference on the video
cap = cv2.VideoCapture(video_path)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Save the output video
output_path = 'output_video.mp4'
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

print("🚀 Processing video... Press 'q' to stop early.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Run YOLO on the frame
    results = model(frame, conf=0.4) # conf=0.4 means "only show if 40% sure"

    # Plot the results on the frame
    annotated_frame = results[0].plot()

    # Write to output file
    out.write(annotated_frame)

cap.release()
out.release()
print(f"✅ Done! Output saved to {output_path}")