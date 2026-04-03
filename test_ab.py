import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_manual(y4m_filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    y4m_path = os.path.join(current_dir, "data", y4m_filename)
    url = "https://s.pear.us/iyR93K"
    
    print(f"\n--- Manual Test: {y4m_filename} ---")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=False, args=[
                "--use-fake-ui-for-media-stream", 
                "--use-fake-device-for-media-stream", 
                f"--use-file-for-fake-video-capture={y4m_path}"
            ])
            
            iphone_14 = p.devices['iPhone 14 Pro Max']
            
            context = browser.new_context(
                **iphone_14,
                permissions=["camera", "microphone"]
            )
            page = context.new_page()
            page.goto(url)
            
            time.sleep(5)
            
            if page.get_by_text("Failed to start the camera").is_visible():
                print(f"RESULT: ❌ {y4m_filename} Failed")
            else:
                print(f"RESULT: ✅ {y4m_filename} Success")
            
            browser.close()
        except Exception as e:
            print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_manual("Ticket_C.y4m")
    test_manual("error_prod.y4m")
