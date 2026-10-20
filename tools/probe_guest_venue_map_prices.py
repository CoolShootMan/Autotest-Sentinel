#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""READ-ONLY probe: what does the venue_map PUBLIC POST actually expose right now,
and what price do the "Select tickets" map tables carry for EACH product?

Answers the guest-case question:
    the case takes the FIRST non-Sold-out public card as the venue-map product
    (ticket_venue_map + my_revenve), then asserts the map drawer prices a table == my_revenve.
    If card #1 is a different product / price tier than the map tables, that assertion fails.

Uses the SAME click mechanism as the framework's `dispatch_click` action (full mouse event
sequence, [MEASURED] one bare `click` event is ignored by the map widget).

Usage: ./venv/bin/python tools/probe_guest_venue_map_prices.py
"""
from playwright.sync_api import sync_playwright

POST = "https://release.pear.us/autotestshop/post/event-for-ui-auto-venue-map"
EVENTS = ["pointerdown", "mousedown", "pointerup", "mouseup", "click"]
INIT = {"pointerId": 1, "isPrimary": True, "button": 0, "buttons": 1}
# The real run emulates iPhone 14 Pro Max (has_touch=True) — reproduce that exactly,
# because a touch-enabled context changes how the map widget handles pointer events.
DEVICE = "iPhone 14 Pro Max"


def _q(s):
    if "'" not in s:
        return f"'{s}'"
    if '"' not in s:
        return f'"{s}"'
    return "concat(" + ', "\'", '.join(f"'{p}'" for p in s.split("'")) + ")"


with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    # NO storage_state -> anonymous = the guest session the case creates
    ctx = b.new_context(**p.devices[DEVICE],
                        locale="en-US", timezone_id="America/New_York")
    pg = ctx.new_page()
    pg.goto(POST, timeout=45000)
    pg.wait_for_timeout(6000)
    print("url:", pg.url)

    cards = pg.locator("xpath=//div[@role='button'][.//p[contains(@class,'price')]]")
    names = []
    print(f"\n=== public product cards: {cards.count()} ===")
    for i in range(cards.count()):
        c = cards.nth(i)
        ps = c.locator("xpath=.//p")
        texts = [ps.nth(j).inner_text(timeout=1500).strip() for j in range(ps.count())]
        sold = "Sold out" in (c.inner_text(timeout=2000) or "")
        print(f"  [{i}] sold_out={sold}  <p>s={texts}")
        if texts:
            names.append(texts[0])

    # what the case's extractors pick
    name_xp = ("xpath=(//div[@role='button'][.//p[contains(@class, 'price')]]"
               "[not(contains(., 'Sold out'))]//p)[1]")
    price_xp = ("xpath=(//div[@role='button'][.//p[contains(@class, 'price')]]"
                "[not(contains(., 'Sold out'))]//p[contains(@class, 'price')])[1]")
    print(f"\ncase extractor name  = {pg.locator(name_xp).first.inner_text().strip()!r}")
    print(f"case extractor price = {pg.locator(price_xp).first.inner_text().strip()!r}")

    for nm in names:
        print(f"\n=========== product {nm!r} ===========")
        pg.goto(POST, timeout=45000)
        pg.wait_for_timeout(5000)
        try:
            pg.locator(f"xpath=//*[normalize-space(.)={_q(nm)}]").first.click(timeout=15000)
        except Exception as e:
            print("  open failed:", str(e)[:110]); continue
        pg.wait_for_timeout(5000)
        dr = pg.locator(".MuiDrawer-root:has-text('Select tickets')")
        if not (dr.count() and dr.first.is_visible()):
            print("  no Select tickets drawer"); continue
        print("  before:", repr(dr.first.inner_text(timeout=6000).replace("\n", " | ")[:200]))
        try:
            el = pg.locator("rect[data-id]").nth(0)
            el.wait_for(state="attached", timeout=10000)
            for ev in EVENTS:
                el.dispatch_event(ev, INIT)
            pg.wait_for_timeout(2500)
            print("  after rect[0]:", repr(dr.first.inner_text(timeout=6000).replace("\n", " | ")[:260]))
        except Exception as e:
            print("  rect click failed:", str(e)[:110])
        try:
            el = pg.locator("circle[data-id]").nth(0)
            for ev in EVENTS:
                el.dispatch_event(ev, INIT)
            pg.wait_for_timeout(2500)
            print("  after circle[0]:", repr(dr.first.inner_text(timeout=6000).replace("\n", " | ")[:260]))
        except Exception as e:
            print("  circle click failed:", str(e)[:110])

    b.close()
