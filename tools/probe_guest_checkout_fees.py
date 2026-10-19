#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""READ-ONLY probe: dump the guest CHECKOUT drawer text + what `_find_row_amount` reads
for the "Transaction fees" row, with signed=True vs signed=False.

Motivation: the guest case publishes `transaction-fees` globally and the partner case asserts
`Net Earning == -(transaction-fees)`. A real run produced `expected '7.77'` (POSITIVE), i.e.
the extracted fee came out NEGATIVE. This probe shows the raw drawer text to explain why.

Guest session (no storage_state). Stops at the Checkout drawer — no order is placed.

Usage: ./venv/bin/python tools/probe_guest_checkout_fees.py
"""
import sys, os, re
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "test_case", "UI"))
from test_case.UI.actions import base as B  # noqa: E402

POST = "https://release.pear.us/autotestshop/post/event-for-ui-auto-venue-map"
EVENTS = ["pointerdown", "mousedown", "pointerup", "mouseup", "click"]
INIT = {"pointerId": 1, "isPrimary": True, "button": 0, "buttons": 1}


def _q(s):
    if "'" not in s:
        return f"'{s}'"
    if '"' not in s:
        return f'"{s}"'
    return "concat(" + ', "\'", '.join(f"'{p}'" for p in s.split("'")) + ")"


with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(**p.devices["iPhone 14 Pro Max"],
                        locale="en-US", timezone_id="America/New_York")
    pg = ctx.new_page()
    pg.goto(POST, timeout=45000)
    pg.wait_for_timeout(6000)

    price_xp = ("xpath=(//div[@role='button'][.//p[contains(@class,'price')]]"
                "[not(contains(., 'Sold out'))]//p[contains(@class,'price')])[1]")
    for attempt in range(3):
        if pg.locator(price_xp).count():
            break
        print(f"  (post not rendered yet, attempt {attempt + 1}: {pg.url}) — reloading")
        pg.goto(POST, timeout=45000)
        pg.wait_for_timeout(8000)
    if not pg.locator(price_xp).count():
        print("ABORT: public post never rendered product cards. url =", pg.url)
        print("page text head:", repr(pg.inner_text("body")[:400]))
        b.close()
        raise SystemExit(2)

    name = pg.locator("xpath=(//div[@role='button'][.//p[contains(@class,'price')]]"
                      "[not(contains(., 'Sold out'))]//p)[1]").first.inner_text().strip()
    print(f"product = {name!r}")
    cards = pg.locator("xpath=//div[@role='button'][.//p[contains(@class,'price')]]")
    for i in range(cards.count()):
        try:
            print(f"  card[{i}]: {cards.nth(i).inner_text(timeout=2000)!r}")
        except Exception:
            pass
    print("  => 'incl. fees' present on the post =",
          "incl" in pg.inner_text("body").lower())
    pg.locator(f"xpath=//*[normalize-space(.)={_q(name)}]").first.click(timeout=15000)
    pg.wait_for_timeout(5000)

    el = pg.locator("rect[data-id]").nth(0)
    el.wait_for(state="attached", timeout=15000)
    for ev in EVENTS:
        el.dispatch_event(ev, INIT)
    pg.wait_for_timeout(2500)
    dr = pg.locator(".MuiDrawer-root:has-text('Select tickets')")
    print("map drawer:", repr(dr.first.inner_text().replace("\n", " | ")[:220]))

    for how in (lambda: pg.get_by_role("button", name="Buy now").first,
                lambda: pg.locator("xpath=//button[normalize-space(.)='Buy now']").first,
                lambda: pg.get_by_text("Buy now", exact=True).first):
        try:
            how().click(timeout=8000)
            print("  Buy now clicked")
            break
        except Exception as e:
            print(f"  Buy now attempt failed: {str(e)[:80]}")
    pg.wait_for_timeout(7000)
    cd = pg.locator(".MuiDrawer-root:has-text('Checkout')")

    def dump(tag):
        print(f"\n=== CHECKOUT drawer raw text [{tag}] ===")
        t = cd.first.inner_text()
        for line in t.split("\n"):
            if line.strip():
                print(f"  |{line.strip()}|")

    dump("collapsed")
    print("\n=== _find_row_amount (COLLAPSED) ===")
    for lab in ("Transaction fees", "Total", "Subtotal", "Taxes"):
        for signed in (True, False):
            v, err = B._find_row_amount(pg, lab, ".MuiDrawer-root:has-text('Checkout')",
                                        tail_limit=24, levels=4, signed=signed, timeout=3000)
            print(f"  {lab!r:18} signed={signed!s:5} -> {v}   err={err}")

    # expand the breakdown exactly like the case does (step 10/11)
    print("\n--- clicking the 'Total' row to expand the breakdown ---")
    try:
        pg.locator("xpath=//*[normalize-space(.)='Total']").first.click(timeout=10000)
    except Exception as e:
        print("  expand click failed:", str(e)[:100])
    pg.wait_for_timeout(2500)
    dump("expanded")

    print("\n=== _find_row_amount (EXPANDED) ===")
    for lab in ("Transaction fees", "Total", "Subtotal", "Taxes"):
        for signed in (True, False):
            v, err = B._find_row_amount(pg, lab, ".MuiDrawer-root:has-text('Checkout')",
                                        tail_limit=24, levels=4, signed=signed, timeout=3000)
            print(f"  {lab!r:18} signed={signed!s:5} -> {v}   err={err}")

    # raw tail inspection around each label, to see where a '-' could come from
    for lab in ("Transaction fees", "Total", "Subtotal"):
        print(f"\n=== ancestor tails around {lab!r} (expanded) ===")
        cands = cd.first.locator(f"xpath=.//*[normalize-space(text())={_q(lab)}]")
        n = cands.count()
        print("  label matches:", n)
        for i in range(n):
            node = cands.nth(i)
            for lvl in range(4):
                try:
                    t = re.sub(r"\s+", " ", node.inner_text().replace(lab, " ")).strip()
                    print(f"    [{i}] lvl{lvl} len={len(t)} tail={t[:100]!r}")
                except Exception as e:
                    print(f"    [{i}] lvl{lvl} <err {str(e)[:40]}>")
                    break
                try:
                    node = node.locator("xpath=..").first
                except Exception:
                    break
    b.close()
