#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only environment preflight for the fee_breakdown / taxes UI cases.

Answers, in one shot:
  1. Is the admin account still seeded (does /events show events at all, or does it bounce
     to /explore "Welcome to Pear 1/7")?
  2. Is the venue_map seed event ('event-for-ui-auto-venue-map') present?
  3. Are there TDC / AXS badged events, and do they still have a NON-Sold-out product?

No clicks that change state — open + read only.

Usage: ./venv/bin/python tools/probe_env_state.py
"""
from playwright.sync_api import sync_playwright

BASE = "https://release.pear.us"
STATE = "test_case/UI/cookie_release.json"
VENUE_EVENT = "event-for-ui-auto-venue-map"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(storage_state=STATE,
                        viewport={"width": 600, "height": 1100},
                        locale="en-US", timezone_id="America/New_York")
    pg = ctx.new_page()

    # ---- 1/2. admin events list -------------------------------------------------
    pg.goto(f"{BASE}/events", timeout=30000)
    pg.wait_for_timeout(5000)
    print("url after /events :", pg.url)
    on_explore = "/explore" in pg.url
    print("bounced to /explore:", on_explore)
    if on_explore:
        print("  => ADMIN SIDE IS EMPTY (account rebuilt). Re-run "
              "test_case/API auto script/tests/00_UI Prefill/"
              "test_ui_prefill_data_configuration.py, and do NOT run it concurrently "
              "with this test stream.")
    vm = pg.locator(f"xpath=//*[normalize-space(.)='{VENUE_EVENT}']").count()
    print(f"venue_map seed event '{VENUE_EVENT}' on /events: count={vm}")

    # ---- 3. badge-tagged events + sellable product ------------------------------
    for badge in ("TDC", "AXS"):
        leaf = f"xpath=//*[normalize-space(.)='{badge}' and not(*)]"
        n = pg.locator(leaf).count()
        print(f"\n--- badge {badge}: {n} element(s) on the events list ---")
        if n == 0:
            continue
        for i in range(1, n + 1):
            row = pg.locator(f"xpath=({leaf}/parent::*)[{i}]")
            try:
                txt = row.first.inner_text(timeout=4000).replace("\n", " | ")[:110]
            except Exception as e:
                txt = f"<unreadable: {str(e)[:50]}>"
            print(f"  [{i}] {txt}")
        # open the first one and count sellable products
        try:
            pg.locator(f"xpath=({leaf}/parent::*)[1]").first.click(timeout=15000)
            pg.wait_for_timeout(5000)
            tab = pg.locator("xpath=//button[@role='tab'][.//*[contains(., 'Tickets')]]")
            if tab.count():
                tab.first.click(timeout=10000)
                pg.wait_for_timeout(3500)
            cards = pg.locator("xpath=//div[@data-testid='mui-stack']"
                               "[.//button[@data-testid='enhance-button']]")
            sellable = pg.locator("xpath=//div[@data-testid='mui-stack']"
                                  "[.//button[@data-testid='enhance-button']]"
                                  "[not(contains(., 'Sold out'))]")
            print(f"  product cards={cards.count()}  non-Sold-out={sellable.count()}")
            pg.locator("xpath=//button[@aria-label='Close']").first.click(timeout=10000)
            pg.wait_for_timeout(3000)
        except Exception as e:
            print(f"  <open failed: {str(e)[:90]}>")

    b.close()
