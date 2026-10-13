"""Probe 2: toggle isTaxEnabled ON (proper switch click) and observe what appears.

No Save is clicked -> nothing persists.
"""
import json
from playwright.sync_api import sync_playwright

BASE = "https://release.pear.us"
COOKIE = "test_case/UI/cookie_release.json"
EVENT_NAME = "event-for-ui-auto-venue-map"


def dump(page, tag):
    print(f"\n----- {tag} -----")
    info = page.evaluate(
        """() => {
          const vis = el => { const r = el.getBoundingClientRect(); return r.width>0 && r.height>0; };
          return [...document.querySelectorAll('input, textarea')].filter(vis).map(i => ({
            tag: i.tagName.toLowerCase(), name: i.name || '', type: i.type || '',
            value: i.value || '', placeholder: i.placeholder || '', checked: i.checked,
          }));
        }"""
    )
    for i in info:
        print("  ", json.dumps(i, ensure_ascii=False))
    dlg = page.evaluate(
        """() => [...document.querySelectorAll('[role=dialog]')].map(d => (d.innerText||'').replace(/\\s+/g,' ').slice(0,300))"""
    )
    print("   dialogs:", json.dumps(dlg, ensure_ascii=False))


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            storage_state=COOKIE,
            viewport={"width": 430, "height": 932},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        )
        page = ctx.new_page()
        page.goto(f"{BASE}/events", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        page.locator(f"//p[normalize-space(.)='{EVENT_NAME}']").first.click()
        page.wait_for_timeout(5000)
        page.locator("//*[normalize-space(.)='Settings']").first.click()
        page.wait_for_timeout(3000)

        before = page.evaluate("() => document.querySelector('input[name=\"isTaxEnabled\"]').checked")
        print("isTaxEnabled BEFORE:", before)

        # click the visible switch root (user-like), fallback to the hidden input
        sw = page.locator(".MuiSwitch-root:has(input[name='isTaxEnabled'])").first
        if sw.count() == 0:
            sw = page.locator("input[name='isTaxEnabled']").first
        sw.click(force=True)
        page.wait_for_timeout(2500)

        after = page.evaluate("() => document.querySelector('input[name=\"isTaxEnabled\"]').checked")
        print("isTaxEnabled AFTER switch click:", after)
        dump(page, "after toggle ON")

        txt = page.evaluate(
            """() => {
              const d = [...document.querySelectorAll('.MuiDrawer-root')].find(x => /tax/i.test(x.innerText||''));
              return d ? (d.innerText||'').replace(/\\s+/g,' ').slice(0, 1500) : '(no drawer)';
            }"""
        )
        print("\nDrawer text after toggle:\n", txt)
        browser.close()


if __name__ == "__main__":
    main()
