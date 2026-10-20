"""Read-only probe: guest opens the venue_map post, selects a map seat, clicks
Buy now to open the Checkout drawer, then dumps every CTA button's testid/text so
the checkout locator can be fixed against reality. NEVER clicks Continue/Place order."""
import json
from playwright.sync_api import sync_playwright

POST = "https://release.pear.us/autotestshop/post/event-for-ui-auto-venue-map"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 600, "height": 1100}, locale="en-US",
                        timezone_id="America/New_York")  # guest
    pg = ctx.new_page()
    pg.goto(POST, timeout=30000)
    pg.wait_for_timeout(5000)

    # click the venue-map product card (first product line)
    pg.locator("xpath=//*[normalize-space(.)='General Admission']").first.click(timeout=15000)
    pg.wait_for_timeout(2500)

    # venue map: pick a table then a seat
    pg.locator("rect[data-id]").first.dispatch_event("click")
    pg.wait_for_timeout(1500)
    pg.locator("circle[data-id]").nth(1).dispatch_event("click")
    pg.wait_for_timeout(2500)

    # Buy now -> Checkout drawer
    pg.get_by_role("button", name="Buy now").first.click(timeout=15000)
    pg.wait_for_timeout(3000)

    info = pg.evaluate("""
      () => {
        const nz = e => (e.textContent||'').replace(/\\s+/g,' ').trim();
        const btns = [...document.querySelectorAll('button')].filter(e => e.offsetParent !== null);
        const out = {cta_candidates: []};
        btns.forEach(e => {
          const tid = e.getAttribute('data-testid') || '';
          const t = nz(e);
          if (/continue|checkout|credit|paypal|pay/i.test(t) || /checkout/i.test(tid)) {
            out.cta_candidates.push({testid: tid, text: t.slice(0,60)});
          }
        });
        return out;
      }
    """)
    print(json.dumps(info, indent=2)[:2000])
    b.close()
