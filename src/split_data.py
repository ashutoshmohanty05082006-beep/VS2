import os
import shutil
import random

# Define paths
# Matches your folder structure from the screenshot
images_dir = "data/images"
labels_dir = "data/labels"
data_dir = "data"

def split_dataset(val_split=0.2):
    # Create the destination structure
    dirs = ['train/images', 'train/labels', 'val/images', 'val/labels']
    for d in dirs:
        os.makedirs(os.path.join(data_dir, d), exist_ok=True)

    # Get list of labeled files from the LABELS folder
    # We trust the label folder: if a text file exists, we look for its matching image
    label_files = [f for f in os.listdir(labels_dir) if f.endswith('.txt') and f != "classes.txt"]
    file_stems = [os.path.splitext(f)[0] for f in label_files]
    
    # Shuffle and split
    random.shuffle(file_stems)
    split_idx = int(len(file_stems) * (1 - val_split))
    train_files = file_stems[:split_idx]
    val_files = file_stems[split_idx:]

    print(f"Total labeled items found: {len(file_stems)}")
    print(f"Training: {len(train_files)} | Validation: {len(val_files)}")

    # Helper function to move files
    def move_files(file_list, destination_type):
        for stem in file_list:
            # 1. Move Image (Try different extensions)
            image_found = False
            for ext in ['.jpg', '.png', '.jpeg', '.mp4']: # Added mp4 just in case, though unlikely for training
                src_img = os.path.join(images_dir, stem + ext)
                if os.path.exists(src_img):
                    dst_img = os.path.join(data_dir, destination_type, 'images', stem + ext)
                    shutil.copy(src_img, dst_img)
                    image_found = True
                    break
            
            if not image_found:
                print(f"⚠️ Warning: Image for label '{stem}' not found.")

            # 2. Move Label
            src_lbl = os.path.join(labels_dir, stem + '.txt')
            dst_lbl = os.path.join(data_dir, destination_type, 'labels', stem + '.txt')
            shutil.copy(src_lbl, dst_lbl)

    print("Moving training files...")
    move_files(train_files, 'train')
    
    print("Moving validation files...")
    move_files(val_files, 'val')
    
    print("✅ Success! Your data is organized.")

if __name__ == "__main__":
    split_dataset()