import os
from pathlib import Path

def trim_y4m(input_path, output_path, num_frames=60):
    """
    Trims a large Y4M file by keeping only the first num_frames.
    Each frame starts with 'FRAME\n'.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    print(f"Trimming {input_path} -> {output_path} (Keeping {num_frames} frames)...")
    
    with open(input_path, 'rb') as f_in:
        # 1. Read and write the header (ends with 0x0A)
        header = b""
        while True:
            byte = f_in.read(1)
            if not byte: break
            header += byte
            if byte == b'\n':
                break
        
        if not header:
            print("Error: Could not find Y4M header.")
            return

        with open(output_path, 'wb') as f_out:
            f_out.write(header)
            
            # 2. Read and write frames
            frames_written = 0
            while frames_written < num_frames:
                # Look for 'FRAME\n'
                tag = f_in.read(6)
                if not tag or tag != b"FRAME\n":
                    # If we don't find the tag where expected, but it's a large file, 
                    # we might be at EOF or middle of sync. Y4M frames are usually fixed size.
                    # For safety, if it's not 'FRAME\n', we stop.
                    break
                
                f_out.write(tag)
                
                # Calculate frame size from header if possible, or just read until next FRAME
                # Based on W1080 H1080 C420 -> Frame size = 1080*1080*1.5 = 1749600 bytes
                frame_data_size = 1749600 
                data = f_in.read(frame_data_size)
                if not data: break
                f_out.write(data)
                
                frames_written += 1
                if frames_written % 10 == 0:
                    print(f"Processed {frames_written} frames...")

    print(f"Success! Created {output_path} ({os.path.getsize(output_path) / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    project_root = Path(__file__).parent

    input_file = project_root / "data" / "Ticket_C.y4m"
    output_file = project_root / "data" / "Ticket_Small.y4m"
    trim_y4m(str(input_file), str(output_file), num_frames=60)
