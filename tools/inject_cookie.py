#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate a Playwright `browser_run_code_unsafe` snippet that injects a cookie
file and opens a URL, then returns a minimal owner/guest gate result.

Why this exists
---------------
The Playwright MCP server has no filesystem access, so the cookie JSON cannot be
passed as a path -- it must be inlined into the code string.  We therefore let
this *local* script (which does have fs) read the cookie file and write the
ready-to-run snippet to disk; the MCP tool is then invoked with
`filename: tools/_inject_cookie.js`.  The auth token never appears in chat.

Usage
-----
    py -3.9 tools/inject_cookie.py \
        --cookie-file test_case/UI/Test_Katana/cookie_release_co_seller.json \
        --url https://release.pear.us/autotest-coseller

Options
-------
    --out      where to write the snippet (default: tools/_inject_cookie.js)
    --keep     do NOT clearCookies() first (default: clear, i.e. full switch)
    --wait     ms to wait after navigation before probing (default: 6000)
    --vanity   override release_katana_vanity_url cookie value (optional)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def load_cookies(path: pathlib.Path):
    """Accept either a bare list of cookie dicts or a {"cookies": [...]} wrapper."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        for key in ("cookies", "Cookies", "data"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
        raise SystemExit(f"[inject] no cookie list found in {path}")
    if isinstance(raw, list):
        return raw
    raise SystemExit(f"[inject] unsupported cookie payload in {path}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cookie-file", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", default="tools/_inject_cookie.js")
    ap.add_argument("--keep", action="store_true", help="do not clearCookies() first")
    ap.add_argument("--wait", type=int, default=6000)
    ap.add_argument("--vanity", default=None, help="value for release_katana_vanity_url")
    args = ap.parse_args()

    cf = (REPO / args.cookie_file) if not pathlib.Path(args.cookie_file).is_absolute() \
        else pathlib.Path(args.cookie_file)
    if not cf.exists():
        print(f"[inject] cookie file not found: {cf}", file=sys.stderr)
        return 2

    cookies = load_cookies(cf)
    if args.vanity:
        for c in cookies:
            if c.get("name") == "release_katana_vanity_url":
                c["value"] = args.vanity

    # Keep only the fields Playwright's addCookies() understands.
    allowed = {"name", "value", "domain", "path", "expires", "httpOnly", "secure", "sameSite"}
    clean = [{k: v for k, v in c.items() if k in allowed} for c in cookies]
    for c in clean:
        if c.get("sameSite") not in ("Strict", "Lax", "None"):
            c["sameSite"] = "Lax"

    payload = json.dumps(clean, ensure_ascii=False)

    snippet = f"""async (page) => {{
  await page.context(){'.clearCookies();' if not args.keep else ';'}
  await page.context().addCookies({payload});
  await page.goto({json.dumps(args.url)}, {{ waitUntil: 'domcontentloaded', timeout: 60000 }});
  await page.waitForTimeout({args.wait});
  const cookies = (await page.context().cookies()).map(c => c.name);
  let loginCount = 0;
  try {{ loginCount = await page.getByText('Log in', {{ exact: true }}).count(); }} catch (e) {{}}
  const ownerMarkers = ['Copy link', 'Manage event', 'Add footer'];
  const found = {{}};
  for (const m of ownerMarkers) {{
    try {{ found[m] = (await page.getByText(m, {{ exact: true }}).count()) > 0; }} catch (e) {{ found[m] = false; }}
  }}
  return {{
    url: page.url(),
    title: await page.title(),
    hasGuestCookie: cookies.some(n => n.includes('guest')),
    ownerCookie: cookies.some(n => n.endsWith('_web_auth_token')),
    loginVisible: loginCount > 0,
    ownerMarkers: found,
    cookieCount: cookies.length,
  }};
}}
"""

    out = (REPO / args.out) if not pathlib.Path(args.out).is_absolute() else pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(snippet, encoding="utf-8")
    # never echo the payload
    n_auth = sum(1 for c in clean if "auth_token" in c.get("name", ""))
    print(f"[inject] wrote {out.relative_to(REPO)}  cookies={len(clean)} auth_tokens={n_auth} url={args.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
