import sys
import os
from playwright.sync_api import sync_playwright
import time

def run_invalid_scan():
    # Use sync playwright to avoid loop issues
    with sync_playwright() as p:
        # Load the invalid QR video
        # Load the invalid QR video for testing zooming/scanning
        video_path = r"d:\new test\Autotest-monster\data\error_prod.y4m"
        
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-video-capture={video_path}",
                "--allow-file-access-from-files"
            ]
        )
        
        # Emulate iPhone 12 Pro to match pytest environment (prevents severe CSS scaling/cropping)
        iphone_12 = p.devices['iPhone 12 Pro']
        context = browser.new_context(
            **iphone_12,
            permissions=["camera", "microphone"],
            storage_state=r"d:\new test\Autotest-monster\test_case\UI\Test_Katana\cookie_release.json"
        )
        page = context.new_page()
        
        # Override WebRTC constraints identically to conftest.py
        page.add_init_script("""
            const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
            navigator.mediaDevices.getUserMedia = function(constraints) {
                if (constraints && constraints.video && typeof constraints.video === 'object') {
                    if (constraints.video.facingMode) delete constraints.video.facingMode;
                    if (constraints.video.width) delete constraints.video.width;
                    if (constraints.video.height) delete constraints.video.height;
                    if (constraints.video.aspectRatio) delete constraints.video.aspectRatio;
                    console.log('WebRTC override: Stripped constraints to prevent .y4m cropping');
                }
                return originalGetUserMedia(constraints);
            };
        """)

        print("Navigating to scanner link...")
        page.goto("https://s.pear.us/iyR93K")
        
        try:
            print("Waiting for popup text...")
            page.locator("text=Code Not Recognized").wait_for(state="visible", timeout=30000)
            print("SUCCESS: Code Not Recognized detected.")
            status = "SUCCESS"
        except Exception as e:
            print(f"FAILURE: Timed out waiting for Code Not Recognized with error_prod.y4m. {e}")
            page.screenshot(path="fail_invalid_scan_final.png")
            status = "FAILURE"
        
        browser.close()
        return status

if __name__ == "__main__":
    result = run_invalid_scan()
    print(result)
    if result == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)
