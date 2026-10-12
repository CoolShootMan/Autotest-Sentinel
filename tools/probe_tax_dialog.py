"""Probe: what actually happens when clicking 'Charge tax on tickets' in event Settings.

No Save is clicked -> nothing persists. Read-only observation of DOM behavior.
"""
import json
import sys
from playwright.sync_api import sync_playwright

BASE = "https://release.pear.us"
COOKIE = "test_case/UI/cookie_release.json"
EVENT_NAME = "event-for-ui-auto-venue-map"


def dump_inputs(page, tag):
    print(f"\n----- inputs ({tag}) -----")
    info = page.evaluate(
        """() => {
          const vis = el => { const r = el.getBoundingClientRect(); return r.width>0 && r.height>0; };
          return [...document.querySelectorAll('input')].filter(vis).map(i => ({
            name: i.name || '', type: i.type || '', value: i.value || '',
            placeholder: i.placeholder || '', checked: i.checked, disabled: i.disabled,
          }));
        }"""
    )
    for i in info:
        print("  ", json.dumps(i, ensure_ascii=False))
    print(f"----- dialogs ({tag}) -----")
    dlg = page.evaluate(
        """() => [...document.querySelectorAll('[role=dialog]')].map(d => ({
              cls: d.className.slice(0,80),
              text: (d.innerText||'').replace(/\\s+/g,' ').slice(0,300),
            }))"""
    )
    for d in dlg:
        print("  ", json.dumps(d, ensure_ascii=False))


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
        print("after /events url:", page.url)

        # find the event card by name
        cnt = page.locator(f"//*[normalize-space(.)='{EVENT_NAME}']").count()
        print(f"locator count for '{EVENT_NAME}':", cnt)
        names = page.evaluate(
            """(n) => {
              const nz = e => (e.textContent||'').replace(/\\s+/g,' ').trim();
              return [...document.querySelectorAll('p')].filter(p => nz(p)===n).map(p => nz(p));
            }""",
            EVENT_NAME,
        )
        print("exact-name <p> matches:", names)
        page.locator(f"//p[normalize-space(.)='{EVENT_NAME}']").first.click()
        page.wait_for_timeout(5000)
        print("after click event url:", page.url)

        # open Settings
        page.locator("//*[normalize-space(.)='Settings']").first.click()
        page.wait_for_timeout(3000)
        print("after Settings url:", page.url)
        dump_inputs(page, "settings open")

        # state of isTaxEnabled before click
        before = page.evaluate(
            """() => { const i=document.querySelector('input[name=\"isTaxEnabled\"]'); return i? i.checked : null; }"""
        )
        print("\nisTaxEnabled.checked BEFORE:", before)

        # click the 'Charge tax on tickets' text
        page.locator("//*[normalize-space(.)='Charge tax on tickets']").first.click()
        page.wait_for_timeout(2500)
        after = page.evaluate(
            """() => { const i=document.querySelector('input[name=\"isTaxEnabled\"]'); return i? i.checked : null; }"""
        )
        print("isTaxEnabled.checked AFTER click:", after)
        dump_inputs(page, "after click charge tax")

        # drawer text around 'tax'
        drawer_txt = page.evaluate(
            """() => {
              const d = [...document.querySelectorAll('.MuiDrawer-root')].find(x => /tax/i.test(x.innerText||''));
              return d ? (d.innerText||'').replace(/\\s+/g,' ').slice(0, 1200) : '(no drawer with tax text)';
            }"""
        )
        print("\nDrawer text (tax area):\n", drawer_txt)
        browser.close()


if __name__ == "__main__":
    sys.exit(main())
