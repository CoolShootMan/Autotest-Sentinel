"""Standalone script: launch fresh Chrome with wrong QR y4m, scan at scanner URL.
Prints SUCCESS when 'QR code is for a different event' appears.
Called by execute_not_recognized_scan action.
"""
import os, sys
from playwright.sync_api import sync_playwright

# Generate wrong QR y4m (QR from a DIFFERENT event)
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "test_case", "UI")
sys.path.insert(0, UI_DIR)
from conftest import _generate_scanner_y4m

WRONG_QR = "9329611"
y4m_path = "/tmp/pear_data/Ticket_WrongQR.y4m"
_generate_scanner_y4m(y4m_path, qr_text=WRONG_QR)

SCANNER_URL = "https://s.pear.us/7DCjTz"

print(f"DEBUG: Starting NotRecognized scan, y4m={y4m_path}, url={SCANNER_URL}")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            f"--use-file-for-fake-video-capture={y4m_path}",
            "--window-size=600,1100",
            "--no-sandbox",
        ],
    )
    context = browser.new_context(permissions=["camera", "microphone"])
    page = context.new_page()
    page.goto(SCANNER_URL, wait_until="networkidle")
    try:
        page.get_by_text("QR code is for a different event").first.wait_for(state="visible", timeout=20000)
        print("SUCCESS: saw 'QR code is for a different event'")
    except Exception as e:
        print(f"FAIL: {e}")
        page.screenshot(path="/tmp/pear_data/not_recognized_fail.png")
        sys.exit(1)
    finally:
        browser.close()
