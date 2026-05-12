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
            launch_args = [
                "--use-fake-ui-for-media-stream", 
                "--use-fake-device-for-media-stream", 
                f"--use-file-for-fake-video-capture={y4m_path}",
                "--window-size=600,1100",
                "--start-maximized",
                "--disable-translate",
                "--disable-features=Translate"
            ]
            print(f"DEBUG: Launching with args: {launch_args}")
            browser = p.chromium.launch(headless=False, args=launch_args)
            
            iphone_14 = p.devices['iPhone 14 Pro Max']
            
            context = browser.new_context(
                **iphone_14,
                permissions=["camera", "microphone"],
                ignore_https_errors=True,
            )
            page = context.new_page()
            
            # --- DIAGNOSTIC: Capture all browser console messages ---
            def handle_console(msg):
                print(f"  [BROWSER CONSOLE][{msg.type.upper()}] {msg.text}")
            def handle_page_error(err):
                print(f"  [PAGE ERROR] {err}")
            page.on("console", handle_console)
            page.on("pageerror", handle_page_error)
            
            # --- KEY FIX: Patch getUserMedia to relax 'exact' constraints ---
            page.add_init_script("""
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    const _original = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
                    navigator.mediaDevices.getUserMedia = function(constraints) {
                        if (constraints && constraints.video && typeof constraints.video === 'object') {
                            const v = JSON.parse(JSON.stringify(constraints.video));
                            if (v.facingMode && v.facingMode.exact) {
                                v.facingMode = { ideal: v.facingMode.exact };
                                console.log('[PATCH] Relaxed facingMode from exact to ideal');
                            }
                            if (v.deviceId && v.deviceId.exact) {
                                delete v.deviceId;
                                console.log('[PATCH] Removed deviceId.exact constraint');
                            }
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
                page.screenshot(path="debug_camera_fail.png")
                browser.close()
                return False
                
            print("RESULT: Camera loaded successfully!")
            print("DEBUG: Waiting for 'Code Not Recognized' toast...")
            
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
