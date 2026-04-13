import cv2
import numpy as np
import os
import glob

def image_to_y4m(image_path, output_path, duration_sec=5, fps=30):
    """
    Converts a single image into a Y4M video file.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read {image_path}")
        return False

    # Standardize to 1280x720 (16:9) to match base requirements
    # or keep it square 1080x1080? Let's use 1080x1080 for high-res QR
    height, width = 1080, 1080
    img = cv2.resize(img, (width, height))

    # Convert BGR to YUV420P
    yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)
    
    # Y4M Header
    header = f"YUV4MPEG2 W{width} H{height} F{fps}:1 Ip A0:0 C420mpeg2\n".encode()
    
    with open(output_path, 'wb') as f:
        f.write(header)
        num_frames = duration_sec * fps
        frame_tag = b"FRAME\n"
        for _ in range(num_frames):
            f.write(frame_tag)
            f.write(yuv.tobytes())
    
    print(f"Created: {output_path} (Size: {os.path.getsize(output_path)/1024/1024:.2f}MB)")
    return True

def batch_convert(img_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Support png, jpeg, jpg
    extensions = ["*.png", "*.jpg", "*.jpeg"]
    images = []
    for ext in extensions:
        images.extend(glob.glob(os.path.join(img_dir, ext)))
    
    images.sort() # Ensure QR_1.png -> Ticket_1.y4m
    
    for i, img_path in enumerate(images):
        # Naming: Ticket_1.y4m, Ticket_2.y4m ...
        idx = i + 1
        output_name = f"Ticket_{idx}.y4m"
        output_path = os.path.join(output_dir, output_name)
        image_to_y4m(img_path, output_path)

if __name__ == "__main__":
    img_dir = r"Autotest-monster\data\prod_env_QR"
    output_dir = r"Autotest-monster\data"
    batch_convert(img_dir, output_dir)
