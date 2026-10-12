"""Probe 3: full flow - toggle tax ON, fill rate=2, click Save, observe dialogs.

NOTE: clicking Save persists the 2% tax on the autotest event (same as the real
test case intends). Idempotent on re-run.
"""
import json
from playwright.sync_api import sync_playwright

BASE = "https://release.pear.us"
COOKIE = "test_case/UI/cookie_release.json"
EVENT_NAME = "event-for-ui-auto-venue-map"


def dump_dialogs(page, tag):
    dlg = page.evaluate(
        """() => [...document.querySelectorAll('[role=dialog]')].map(d => ({
              text: (d.innerText||'').replace(/\\s+/g,' ').slice(0,500),
              buttons: [...d.querySelectorAll('button')].map(b => (b.textContent||'').trim()).filter(Boolean),
            }))"""
    )
    print(f"--- dialogs ({tag}):", json.dumps(dlg, ensure_ascii=False, indent=1))


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
        print("event url:", page.url)

        # open Settings with retry + polling for the drawer
        opened = False
        for attempt in range(3):
            page.locator("//*[normalize-space(.)='Settings']").first.click()
            for _ in range(10):
                page.wait_for_timeout(500)
                if page.locator("input[name='isTaxEnabled']").count() > 0:
                    opened = True
                    break
            if opened:
                break
            print(f"Settings drawer not open (attempt {attempt + 1})")
        if not opened:
            print("FAILED to open settings drawer; body head:",
                  page.evaluate("() => (document.body.innerText||'').replace(/\\s+/g,' ').slice(0,300)"))
            browser.close()
            return
        page.wait_for_timeout(1000)

        # 1. toggle the switch on (force click visible switch root)
        sw = page.locator(".MuiSwitch-root:has(input[name='isTaxEnabled'])").first
        sw.click(force=True, timeout=10000)
        page.wait_for_timeout(1500)
        state = page.evaluate(
            """() => {
              const t = document.querySelector('input[name=\"isTaxEnabled\"]');
              const r = document.querySelector('input[name=\"customTaxRate\"]');
              return { checked: t ? t.checked : null, rate: r ? r.value : null, rateVisible: r ? r.getBoundingClientRect().width>0 : false };
            }"""
        )
        print("after toggle:", json.dumps(state))

        # 2. fill the rate
        page.locator("input[name='customTaxRate']").first.fill("2")
        page.wait_for_timeout(800)
        state = page.evaluate(
            """() => {
              const t = document.querySelector('input[name=\"isTaxEnabled\"]');
              const r = document.querySelector('input[name=\"customTaxRate\"]');
              return { checked: t ? t.checked : null, rate: r ? r.value : null };
            }"""
        )
        print("after fill:", json.dumps(state))

        # 3. click Save (inside the drawer)
        save_clicked = False
        for loc in ["//button[normalize-space(.)='Save']", "button:has-text('Save')"]:
            try:
                page.locator(loc).first.click(force=True, timeout=5000)
                save_clicked = True
                break
            except Exception as e:
                print("save try failed:", loc, str(e)[:120])
        print("save clicked:", save_clicked)
        page.wait_for_timeout(2500)
        dump_dialogs(page, "after Save #1")

        # 4. click 'Got it' if present
        got = page.locator("button:has-text('Got it')").first
        if got.count() > 0:
            got.click(force=True)
            page.wait_for_timeout(2000)
            dump_dialogs(page, "after Got it")
            # drawer still open? does it need another Save?
            drawer_open = page.evaluate(
                """() => [...document.querySelectorAll('.MuiDrawer-root')].some(d => /Event settings/i.test(d.innerText||'') && d.getBoundingClientRect().width>0)"""
            )
            print("settings drawer still open after Got it:", drawer_open)
            if drawer_open:
                page.locator("//button[normalize-space(.)='Save']").first.click(force=True)
                page.wait_for_timeout(2500)
                dump_dialogs(page, "after Save #2")
                got2 = page.locator("button:has-text('Got it')").first
                if got2.count() > 0:
                    got2.click(force=True)
                    page.wait_for_timeout(2000)
                    dump_dialogs(page, "after Got it #2")

        # 5. verify persisted: reopen Settings and read state
        page.wait_for_timeout(2000)
        page.locator("//*[normalize-space(.)='Settings']").first.click()
        page.wait_for_timeout(3000)
        state = page.evaluate(
            """() => {
              const t = document.querySelector('input[name=\"isTaxEnabled\"]');
              const r = document.querySelector('input[name=\"customTaxRate\"]');
              return { checked: t ? t.checked : null, rate: r ? r.value : null };
            }"""
        )
        print("REOPENED settings state:", json.dumps(state))
        browser.close()


if __name__ == "__main__":
    main()
