import os
import sys
import time
from playwright.sync_api import sync_playwright

def run_isolated_scan():
    # Detect BASE_DIR
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Use forward slashes for safer Chromium argument parsing on Windows
    y4m_path = os.path.join(current_dir, "data", "error_prod.y4m").replace("\\", "/")
    url = "https://s.pear.us/iyR93K"
    
    print(f"DEBUG: Starting isolated scan for 'Code Not Recognized'")
    print(f"Path: {y4m_path}")

    with sync_playwright() as p:
        try:
            # EXACT args from conftest.py which we know works for Ticket_C
            launch_args = [
                "--use-fake-ui-for-media-stream", 
                "--use-fake-device-for-media-stream", 
                f"--use-file-for-fake-video-capture={y4m_path}",
                "--window-size=600,1100",
                "--start-maximized",
                "--disable-translate",
                "--disable-features=Translate"
            ]
            browser = p.chromium.launch(headless=False, args=launch_args)
            
            # Use exact same emulation as the success run
            iphone_14 = p.devices['iPhone 14 Pro Max']
            
            context = browser.new_context(
                **iphone_14,
                permissions=["camera", "microphone"]
            )
            page = context.new_page()
            page.goto(url)
            
            # Identical timeout as success run
            print("DEBUG: Waiting for camera initialization...")
            page.wait_for_timeout(5000)
            
            if page.get_by_text("Failed to start the camera").is_visible():
                print("RESULT: ❌ Failed to start camera")
                browser.close()
                return False
                
            print("RESULT: ✅ Camera loaded successfully!")
            print("DEBUG: Waiting for 'Code Not Recognized' toast...")
            
            # Simple loop for the toast
            success = False
            for i in range(15):
                if page.get_by_text("Code Not Recognized").is_visible():
                    print("SUCCESS: Invalid Code state verified!")
                    success = True
                    break
                time.sleep(2)
                
            page.screenshot(path="final_isolated_state.png")
            browser.close()
            return success
                
        except Exception as e:
            print(f"ERROR: Script crash: {str(e)}")
            return False

if __name__ == "__main__":
    if run_isolated_scan():
        sys.exit(0)
    else:
        sys.exit(1)
