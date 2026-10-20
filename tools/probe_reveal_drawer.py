"""Read-only probe #2: verify the FIXED scope locator and every assertion target
inside the Address visibility settings sheet. Never clicks Apply/Save."""
from playwright.sync_api import sync_playwright

BASE = "https://release.pear.us"
STATE = "test_case/UI/cookie_release.json"
SCOPE = "xpath=//*[contains(@class,'MuiDrawer-paper')][.//*[contains(normalize-space(.),'Address visibility settings')]]"

CHECKS = [
    ("scope", SCOPE),
    ("title", SCOPE + "//*[normalize-space(.)='Address visibility settings']"),
    ("desc", SCOPE + "//*[contains(normalize-space(.),'Control when the event location is shown')]"),
    ("learn_more_href", SCOPE + "//a[normalize-space(.)='Learn more']"),
    ("opt1_label", SCOPE + "//*[normalize-space(.)='Ticket buyers only']"),
    ("opt2_label", SCOPE + "//*[normalize-space(.)='Ticket buyers after a set time']"),
    ("opt3_label", SCOPE + "//*[normalize-space(.)='Everyone after a set time']"),
    ("opt4_label", SCOPE + "//*[normalize-space(.)='Keep address hidden']"),
    ("apply_btn", SCOPE + "//button[normalize-space(.)='Apply']"),
]

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

    for name, loc in CHECKS:
        try:
            n = pg.locator(loc).count()
            vis = pg.locator(loc).first.is_visible() if n else False
            print(f"OK  {name}: count={n} visible={vis}")
        except Exception as e:
            print(f"FAIL {name}: {str(e)[:100]}")

    href = pg.locator(SCOPE + "//a[normalize-space(.)='Learn more']").first.get_attribute("href")
    print("learn_more href =", href)

    # radio default state (option1 checked, others not)
    for label, want in [("Ticket buyers only", True), ("Ticket buyers after a set time", False),
                        ("Everyone after a set time", False), ("Keep address hidden", False)]:
        radio = pg.locator(f"xpath=//*[normalize-space(.)='{label}']/ancestor::*[.//input[@type='radio']][1]//input[@type='radio']").first
        print(f"radio '{label}' checked={radio.is_checked()} (want {want})")
    b.close()
