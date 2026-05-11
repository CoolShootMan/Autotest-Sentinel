import os
import sys
import time
from playwright.sync_api import sync_playwright

def run_isolated_scan_c():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    y4m_path = os.path.join(current_dir, "data", "Ticket_C.y4m").replace("\\", "/")
    url = "https://s.pear.us/iyR93K"
    
    print(f"DEBUG: Starting isolated scan for Ticket_C")
    print(f"Path: {y4m_path}")

    with sync_playwright() as p:
        try:
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
            iphone_14 = p.devices['iPhone 14 Pro Max']
            context = browser.new_context(**iphone_14, permissions=["camera", "microphone"], ignore_https_errors=True)
            page = context.new_page()
            
            page.add_init_script("""
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    const _original = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
                    navigator.mediaDevices.getUserMedia = function(constraints) {
                        if (constraints && constraints.video && typeof constraints.video === 'object') {
                            const v = JSON.parse(JSON.stringify(constraints.video));
                            if (v.facingMode && v.facingMode.exact) { v.facingMode = { ideal: v.facingMode.exact }; }
                            if (v.deviceId && v.deviceId.exact) { delete v.deviceId; }
                            // Key fix: remove the 16:9 resolution constraint imposed by the web frontend
                            // Prevents Chromium from cropping or stretching 1080x1080 Ticket_C images to fit 1280x720
                            if (v.width) delete v.width;
                            if (v.height) delete v.height;
                            constraints = { ...constraints, video: v };
                        }
                        return _original(constraints);
                    };
                }
            """)

            page.goto(url, wait_until="domcontentloaded")
            
            print("DEBUG: Waiting for camera initialization...")
            page.wait_for_timeout(8000)
            
            if page.get_by_text("Failed to start the camera").is_visible():
                print("RESULT: Failed to start camera")
                browser.close()
                return False
                
            print("RESULT: Camera loaded successfully!")
            print("DEBUG: Waiting for ANY toast...")
            
            for i in range(15):
                visible_text = page.locator("body").inner_text()
                # print(f"DEBUG {i}: Body text snippet -> {visible_text[:100].replace(chr(10), ' ')}")
                
                # Check for ANY common toast keywords
                if "Code" in visible_text or "Verified" in visible_text or "Redeemed" in visible_text or "Not Recognized" in visible_text or "Error" in visible_text or "success" in visible_text.lower():
                    toast = page.locator("div[role='alert'], .toast, .MuiAlert-message, :text('Code'), :text('Verified')").all_inner_texts()
                    if not toast:
                         toast = [t for t in visible_text.split('\n') if "Code" in t or "Verified" in t]
                    print(f"SUCCESS: Found potential toast(s): {toast}")
                    page.screenshot(path="final_isolated_state_c.png")
                    browser.close()
                    return True
                time.sleep(2)
                
            print("FAILED: No known toast appeared after 30s.")
            print("FINAL PAGE TEXT DUMP:")
            print(page.locator("body").inner_text())
            page.screenshot(path="final_isolated_state_c_timeout.png")
            browser.close()
            return False
                
        except Exception as e:
            print(f"ERROR: Script crash: {str(e)}")
            return False

if __name__ == "__main__":
    if run_isolated_scan_c():
        sys.exit(0)
    else:
        sys.exit(1)
