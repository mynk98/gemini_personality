#!/usr/bin/env python3
import cv2
import os
import sys
import datetime

# Constants
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(BASE_DIR, 'personality/camera')
EVOLUTION_LOG = os.path.join(BASE_DIR, 'personality/evolution.txt')

def capture_user():
    # 1. Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.", file=sys.stderr)
        return False

    # Wait for the camera to adjust to light
    print("Adjusting camera...", file=sys.stderr)
    for i in range(30):
        cap.read()

    # 2. Capture frame
    ret, frame = cap.read()
    
    if ret:
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Save image
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_photo_{timestamp}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        cv2.imwrite(filepath, frame)
        print(f"Photo captured and saved to: {filepath}")
        
        # Link as 'user_photo.png' for consistent reference
        link_path = os.path.join(OUTPUT_DIR, "user_photo.png")
        if os.path.exists(link_path):
            os.remove(link_path)
        
        # Copy file as fallback for link (more robust)
        import shutil
        shutil.copy2(filepath, link_path)
        
        # 3. Update memory log
        with open(EVOLUTION_LOG, 'a') as f:
            f.write(f"{datetime.datetime.now().isoformat()}: [EVOLUTION] Memory Update: Successfully captured and saved an image of the user at {filepath}.\n")
        
        cap.release()
        return True
    else:
        print("Error: Could not capture photo.", file=sys.stderr)
        cap.release()
        return False

if __name__ == "__main__":
    if capture_user():
        sys.exit(0)
    else:
        sys.exit(1)
