"""Read-only admin probe: read the CURRENT Address visibility radio state of the
venue_map event (no Apply, no Save)."""
from playwright.sync_api import sync_playwright

BASE = "https://release.pear.us"
STATE = "test_case/UI/cookie_release.json"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(storage_state=STATE, viewport={"width": 600, "height": 1100},
                        locale="en-US", timezone_id="America/New_York")
    pg = ctx.new_page()
    pg.goto(f"{BASE}/events", timeout=30000)
    pg.wait_for_timeout(4000)
    pg.locator("xpath=//*[normalize-space(.)='event-for-ui-auto-venue-map']").first.click(timeout=15000)
    pg.wait_for_timeout(4000)
    pg.locator("xpath=//*[normalize-space(.)='Edit event']").first.click(timeout=15000)
    pg.wait_for_timeout(3000)
    pg.locator("xpath=//*[normalize-space(.)='Reveal address later?']/ancestor::*[.//input[@type='checkbox']][1]//input[@type='checkbox']").first.click(timeout=15000)
    pg.wait_for_timeout(2500)
    for label in ["Ticket buyers only", "Ticket buyers after a set time",
                  "Everyone after a set time", "Keep address hidden"]:
        radio = pg.locator(f"xpath=//*[normalize-space(.)='{label}']/ancestor::*[.//input[@type='radio']][1]//input[@type='radio']").first
        try:
            print(f"{label}: checked={radio.is_checked()}")
        except Exception as e:
            print(f"{label}: ERR {str(e)[:60]}")
    b.close()
