import cv2
import os
import glob

def extract_frames(video_folder="data/raw_videos", output_folder="data/images", fps_to_save=1):
    """
    Extracts 1 frame per second from all videos in the folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Find all mp4, avi, mov files
    video_files = glob.glob(os.path.join(video_folder, "*.*"))
    
    for video_path in video_files:
        print(f"Processing {video_path}...")
        cap = cv2.VideoCapture(video_path)
        video_fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Calculate hop size (e.g., if video is 30fps, we need 1 frame every 30 frames)
        hop = round(video_fps / fps_to_save)
        current_frame = 0
        
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            if current_frame % hop == 0:
                # Create a unique name: video_name_frame_0.jpg
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                out_name = os.path.join(output_folder, f"{base_name}_frame_{current_frame}.jpg")
                cv2.imwrite(out_name, frame)
                
            current_frame += 1
            
        cap.release()
    print("✅ Done! Check your data/images folder.")

if __name__ == "__main__":
    # Make sure you created 'data/raw_videos' and uploaded videos there first!
    extract_frames()