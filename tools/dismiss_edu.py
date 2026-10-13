"""
Dismiss Katana "EDU" (in-app onboarding) popups before the UI suite runs.

Invoked by test_case/UI/main.py as step 3 of the pipeline. If the accounts are
left with an onboarding layer on screen, the first UI cases die with confusing
"element not found" / "intercepts pointer events" errors, so this step is
treated as a preflight gate.

The resale onboarding tour (the layer that breaks the very first UI case)
-------------------------------------------------------------------------------
It is a THREE-step tour reached by enabling resale on a post:
    [post editor] Commerce -> "Allow approved co-sellers to resell" ON
    -> the "Customize product settings" drawer opens BY ITSELF
    (equivalently: Events -> <event> -> Post tab -> Selling sub-tab -> Customize)

    1. "Set resale earnings"    -> [Start Customizing]  (+ "Do not show this again")
    2. "Choose a resale model"  -> [Done]
    3. "Set per-product values" -> [Done]

Only after step 3 is "Batch set commission for all products" clickable -- exactly
the element testT1742 could not find.

Why the previous versions silently failed (CI runs #4 / #5)
-------------------------------------------------------------------------------
  * It never navigated to the drawer: the "Customize" click was commented out and
    the `tab "Selling"` it looked for does not exist on the storefront (its bottom
    bar is Upcoming Events / MyForm / Past Events / Verify).
  * It matched buttons with `locator("button").filter(has_text=...)` while the tour
    controls are `<p>` / `<span>` inside a `<button>`; MUI layers stack, so `.first`
    resolved to a copy another aria-hidden layer covered.
  * It never enabled resale, so accounts with no event post (+998, +997) never saw
    the tour at all. The switch is `input[name=allowPromotersResell]` with
    `opacity: 0`, and the visible "Off"/"On" label lives INSIDE the MUI Switch --
    so its accessible name is literally "Off" and
    `get_by_role("checkbox", name="allowPromotersResell")` can never match.
  * It "ticked" the opt-out box by clicking the visible TEXT. In the
    "Set resale earnings" dialog that text is an inert sibling `<p>`, so nothing
    was ticked while the code happily reported success -- and the tour came back
    on the next run.
  * Every failure was swallowed by `except Exception: pass`, and `main()` had no
    return value at all (returncode always 0), so main.py's abort branch never ran.

The blocker that hid all of the above
-------------------------------------
  `get_by_role(...)` **skips `aria-hidden` subtrees**. Whenever a MUI modal is
  open, the entire editor behind it is marked `aria-hidden="true"`, so role-based
  lookups return 0 matches on a page whose screenshot looks perfectly normal and
  whose `innerText` even contains the "Select" label:

      get_by_role("button", name="Select", exact=True).count()  ->  0   # modal up
      get_by_role("button", name="Select", exact=True).count()  ->  1   # modal gone

  The modal here is "We found an unsaved version of this post ... [Discard]",
  raised asynchronously ~2-3s after `/post/create` loads (the recovery snapshot
  is fetched after the first render). So the earlier version's single check at
  +2s raced it and lost -> `_add_first_product` timed out -> no product -> no
  resale switch -> no tour, reported as a bland `product=no`.

Do NOT pass a regex containing "/" to get_by_role(name=...)
----------------------------------------------------------
  Playwright's **Python** binding serialises `name=<compiled pattern>` into its
  own selector string, escaping the slashes, and then its selector parser rejects
  its own output:

      page.get_by_role("button", name=re.compile(r"Add \\d+/\\d+ product"))
      -> InvalidSelectorError: Error while parsing selector
         `button[name=/Add \\d+/\\d+ product/]` - unexpected symbol "\\" at position 21

  A locator written that way can NEVER match -- not a flake, not a timing issue,
  broken everywhere and forever. The JS binding passes a real RegExp object and is
  unaffected, so this only ever bites the Python run. Measured with the project
  interpreter:

      get_by_role("button", name=re.compile(r"Add \\d+"))        -> OK   count=1
      get_by_role("button", name=re.compile(r"Add \\d+/\\d+"))     -> FAIL InvalidSelectorError
      locator("div").filter(has_text=re.compile(r"a/b"))         -> OK   count=1
      locator("button", has_text="product(s)")                   -> OK   count=1

  So: keep regexes on the Python side, and use a plain-string `:has-text` /
  `filter(has_text=...)` for anything that might contain a slash.

What this version does differently
----------------------------------
  * `_click_topmost_any` clicks the element that actually *receives the pointer*
    at its centre (document.elementFromPoint), not the first DOM match -- stacked
    or aria-hidden MUI layers can no longer shadow the click;
  * the unsaved-draft dialog is **polled for** (not checked once) and dismissed in
    a loop before anything else touches the editor; the editor is also left
    cleanly on the way out so the dialog does not arm itself for the next run;
  * `_add_first_product` uses CSS/`hasText` locators (immune to aria-hidden) and
    **verifies its post-condition** -- the resale switch being on screen -- instead
    of trusting that the click did not throw;
  * every failing click reports WHY (`[EDU-WARN] ... <ExceptionType>: <first line>`)
    and `DISMISS_EDU_DEBUG=1` drops a screenshot + page text into `data/_edu_debug/`
    -- a headless preflight that fails silently is worse than one that fails loudly;
  * `_set_opt_out` resolves the opt-out checkbox to its real `<input>` (label-or-
    sibling), clicks it, and **reads `input.checked` back** before believing it;
  * the tick happens BEFORE the advance button, because ticking is what persists;
  * resale is enabled explicitly (`input[name=allowPromotersResell]`, verified),
    which is also what triggers the tour on accounts without event posts;
  * `/account` ("Manage multiple accounts" -> Got it) is handled;
  * the post-selling walk stops at the first event whose drawer opens: the tour is
    per account, and walking all 15 events cost ~5 extra minutes of CI time
    (DISMISS_EDU_FULL_SWEEP=1 restores the full walk);
  * `/events` is skipped entirely for the co-seller account (+998), whose role has
    no such route (HTTP 404);
  * every step is verified and reported; nothing is silently swallowed.

Exit codes
----------
  0  accounts are logged in and every visited page ended popup-free
  2  a cookie file is missing (i.e. step 2, get_all_cookies.py, did not run)
  3  an account's session/page could not be opened (dead session -> the suite
     would produce a full round of bogus "element not found" failures)
  Leftover EDU layers / unverified opt-outs are reported as `[EDU-LEFT]` and
  counted in the summary. They do NOT fail the run by default (aborting would also
  throw away the whole pytest run); set DISMISS_EDU_STRICT=1 to make them exit 4.

Cookie filenames and URLs are resolved dynamically from the BASE_URL environment
variable, and the cookie files are written back after the tour is finished so
the (server-side) "do not show again" choice is kept for the pytest run.
"""
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

load_dotenv(Path(__file__).parent.parent / ".env")

PROJECT_ROOT = Path(__file__).parent.parent
COOKIE_DIR = PROJECT_ROOT / "test_case" / "UI"

# Read from BASE_URL environment variable, default to release environment
ENV_BASE = os.environ.get("BASE_URL", "https://release.pear.us")

# Reverse-map domain to environment name for cookie file naming
_ENV_MAP = {
    "https://staging.pear.us": "staging",
    "https://release.pear.us": "release",
    "https://pear.us": "prod",
}
ACCOUNT_ENV = _ENV_MAP.get(ENV_BASE, "release")

# `has_events` gates the post-selling sweep. Measured 2026-09-23:
#   +999 -> /events has 14 rows
#   +998 -> /events answers HTTP 404 ("This page could not be found."), the
#           co-seller role has no such route at all -- navigating there is not
#           just wasted, it is meaningless
#   +997 -> /events EXISTS but is empty (rowCount 0)
ACCOUNTS = [
    {
        "name": "main (+999)",
        "cookie_file": f"cookie_{ACCOUNT_ENV}.json",
        "home_url": f"{ENV_BASE}/autotestshop",
        "has_events": True,
    },
    {
        "name": "co-seller (+998)",
        "cookie_file": f"cookie_{ACCOUNT_ENV}_co_seller.json",
        "home_url": f"{ENV_BASE}/autotest-coseller",
        "has_events": False,
    },
    {
        "name": "partner co-seller (+997)",
        "cookie_file": f"cookie_{ACCOUNT_ENV}_partner_coseller.json",
        "home_url": f"{ENV_BASE}/partnercoseller997",
        "has_events": True,
    },
]

# Onboarding text markers. Used to decide "is an onboarding layer on screen?",
# which gates every click so we never press a real product button by accident.
EDU_MARKERS = (
    "Set resale earnings",
    "Choose a resale model",
    "Set per-product values",
    "Do not show this again",
    "Do not show me this again",
    "You've added products",
    "Manage multiple accounts",
    "We found an unsaved version",
    "Your shop is ready",
    "You've verified your phone number",
)

# "Do not show this again" / "Do not show me this again" -- ticking one of these
# is what makes the tour permanent for the account. It MUST be verified, because
# a click that lands on the (inert) label text instead of the checkbox silently
# does nothing and the tour re-arms on the next run.
OPT_OUT_LABELS = ("Do not show this again", "Do not show me this again")

# Button that advances / closes the /account "Manage multiple accounts" EDU.
ACCOUNT_EDU_BUTTONS = ("Got it",)

# The unsaved-draft recovery dialog offers Discard / Continue. The preflight
# always discards so the next run starts from a clean editor.
DISCARD_BUTTONS = ("Discard",)


# Buttons that only ever advance an onboarding layer, in the order they appear
# across the tour. "Start Customizing" is the only one with a real side effect
# (it opens the customizing flow) and is required by the tour itself.
TOUR_ADVANCE_BUTTONS = ("Start Customizing", "Done", "Got it", "Next")
POPUP_ADVANCE_BUTTONS = (
    "Try it now",
    "I'll do it later",
    "No, take me to my shop",
    "Got it",
    "Next",
    "Done",
)
# NOTE: "Save" deliberately absent. It used to be in this list, and every entry
# is pressed by exact text with no EDU gating -- in the post editor / resale
# drawer that risks committing whatever is on screen just to clear a popup.

# Maximum number of event rows walked per account (the Events table is
# paginated client-side; the UI suite only uses the first page).
MAX_EVENT_ROWS = 30

_EDU_PICK_JS = """
(texts) => {
  document.querySelectorAll('[data-edu-pick]').forEach(e => e.removeAttribute('data-edu-pick'));
  const wanted = new Set(texts);
  const groups = new Map();
  let n = 0;
  document.querySelectorAll('*').forEach(el => {
    if (el.children.length) return;
    const t = (el.textContent || '').trim();
    if (!wanted.has(t)) return;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    if (!groups.has(t)) groups.set(t, []);
    groups.get(t).push(el);
    n++;
  });
  for (const t of texts) {
    for (const el of groups.get(t) || []) {
      const r = el.getBoundingClientRect();
      const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      if (!hit) continue;
      // The pointer can land on the element itself, on a child of it, or on an
      // ancestor that wraps it (e.g. the real <button> around a <span> label).
      if (hit === el || el.contains(hit)) { el.setAttribute('data-edu-pick', '1'); return t; }
      if (hit.contains(el)) { hit.setAttribute('data-edu-pick', '1'); return t; }
    }
  }
  return null;
}
"""

_CLEAR_PICK_JS = "() => document.querySelectorAll('[data-edu-pick]').forEach(e => e.removeAttribute('data-edu-pick'))"

# Finds an opt-out checkbox by its visible label and tags the *input*.
#
# The label and the checkbox are only sometimes associated:
#   * "You've added products" popup -> the text IS a <label> that wraps the input
#   * "Set resale earnings" dialog  -> the text is a SIBLING <p> inside
#     <div data-testid="mui-stack"><span class="MuiCheckbox-root"><input/>…</span><p>…</p></div>
# so clicking the text does nothing in the second case. Always resolve to the
# input and click that.
_OPT_OUT_JS = """
(labels) => {
  document.querySelectorAll('[data-opt-pick]').forEach(e => e.removeAttribute('data-opt-pick'));
  const wanted = new Set(labels);
  const found = [];
  document.querySelectorAll('*').forEach(el => {
    if (el.children.length) return;
    const t = (el.textContent || '').trim();
    if (!wanted.has(t)) return;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    found.push({ label: t, el });
  });
  for (const item of found) {
    let inp = item.el.tagName === 'LABEL' ? item.el.querySelector('input[type=checkbox]') : null;
    let scope = item.el.parentElement;
    for (let i = 0; i < 3 && scope && !inp; i++) {
      inp = scope.querySelector('input[type=checkbox]');
      if (!inp) scope = scope.parentElement;
    }
    if (!inp) continue;
    const ir = inp.getBoundingClientRect();
    if (ir.width <= 0 || ir.height <= 0) continue;
    inp.setAttribute('data-opt-pick', '1');
    return { label: item.label, checked: !!inp.checked };
  }
  return null;
}
"""

_READ_OPT_OUT_JS = """
() => {
  const i = document.querySelector('[data-opt-pick="1"]');
  if (!i) return null;
  const svg = i.parentElement ? i.parentElement.querySelector('svg') : null;
  return { checked: !!i.checked, icon: svg ? svg.getAttribute('data-testid') : null };
}
"""

# JS-level click: fires the input's change handler even when an aria-hidden
# backdrop is stacked on top of it (the "stuck backdrop" case observed when a
# MUI popup is open -- elementFromPoint finds the backdrop, not the checkbox).
_FORCE_OPT_OUT_JS = """
() => {
  const i = document.querySelector('[data-opt-pick="1"]');
  if (i) i.click();
  return i ? !!i.checked : null;
}
"""

_CLEAR_OPT_PICK_JS = "() => document.querySelectorAll('[data-opt-pick]').forEach(e => e.removeAttribute('data-opt-pick'))"



# --------------------------------------------------------------------------- #
# Core primitives
# --------------------------------------------------------------------------- #
def _click_topmost_any(page: Page, texts, timeout: int = 4000):
    """Click the topmost pointer-receiving element matching the first usable text.

    Returns the text that was clicked, or None. `texts` is tried in order, so the
    caller controls precedence (e.g. "Start Customizing" before "Done").

    Unlike `locator(...).first.click()`, this respects what the user would really
    hit: `document.elementFromPoint` is consulted at the candidate's centre, so an
    aria-hidden-but-still-drawn MUI layer stacked on top cannot silently absorb
    the click (that is the exact failure mode of the old T1742 run:
    "…<p>Done</p> from <div aria-hidden=\"true\"…> subtree intercepts pointer events").
    """
    try:
        hit = page.evaluate(_EDU_PICK_JS, list(texts))
    except Exception:
        return None
    if not hit:
        return None
    try:
        page.locator("[data-edu-pick='1']").first.click(timeout=timeout)
        return hit
    except Exception:
        return None
    finally:
        try:
            page.evaluate(_CLEAR_PICK_JS)
        except Exception:
            pass


def _click_topmost_text(page: Page, text: str, timeout: int = 4000) -> bool:
    """Convenience wrapper for a single label."""
    return _click_topmost_any(page, (text,), timeout=timeout) is not None


def _edu_layers(page: Page, limit: int = 3) -> list:
    """Return a short description of every visible onboarding text layer."""
    found = []
    for marker in EDU_MARKERS:
        if len(found) >= limit:
            break
        try:
            loc = page.get_by_text(marker, exact=False)
            for i in range(min(loc.count(), 3)):
                node = loc.nth(i)
                try:
                    if node.is_visible():
                        found.append(marker)
                        break
                except Exception:
                    continue
        except Exception:
            continue
    return found


def _set_opt_out(page: Page, labels=OPT_OUT_LABELS) -> dict:
    """Tick an onboarding opt-out checkbox and **verify** it really got checked.

    Ticking it is the whole point of the preflight: it is what makes the tour
    permanent for the account. The old implementation clicked the *visible text*
    and reported "1 tick" while the box stayed empty, because in the
    "Set resale earnings" dialog the text is an inert sibling `<p>` -- so the
    tour came back on the next run (the exact CI symptom being fixed here).

    Escalation, each step verified by reading `input.checked` back:
      1. Playwright click on the tagged `<input>` (it is the topmost hit target);
      2. JS `.click()` on the input -- still works when an aria-hidden backdrop
         from an open MUI popup is covering it;
      3. give up and report `unverified` so the caller can complain loudly.

    Returns {"label": str|None, "ticked": bool, "how": str}.
    """
    report = {"label": None, "ticked": False, "how": "not-found"}
    try:
        found = page.evaluate(_OPT_OUT_JS, list(labels))
    except Exception:
        return report
    if not found:
        return report

    report["label"] = found["label"]
    if found["checked"]:
        report["ticked"] = True
        report["how"] = "already-checked"
        return report

    try:
        page.locator("[data-opt-pick='1']").first.click(timeout=2500)
    except Exception:
        pass
    try:
        state = page.evaluate(_READ_OPT_OUT_JS)
    except Exception:
        state = None
    if state and state.get("checked"):
        report["ticked"] = True
        report["how"] = "click"
        return report

    try:
        if page.evaluate(_FORCE_OPT_OUT_JS):
            report["ticked"] = True
            report["how"] = "js-click"
            return report
    except Exception:
        pass

    report["how"] = "unverified"
    return report


def _tick_dont_show_again(page: Page) -> int:
    """Tick the on-screen opt-out box; returns 1 only when it is VERIFIED checked."""
    report = _set_opt_out(page)
    return 1 if report["ticked"] else 0


def dismiss_edu_tour(page: Page, buttons=TOUR_ADVANCE_BUTTONS, max_passes: int = 8) -> dict:
    """Finish a multi-step onboarding tour, verifying it is actually gone.

    Every click is gated on "an onboarding layer is on screen" so a real product
    button carrying the same label (e.g. the drawer's own "Save") is never pressed.

    The opt-out box is ticked **before** the advance button on every pass, because
    ticking it is what persists the choice; pressing "Start Customizing" first
    would walk the tour without ever setting it.

    Returns {"clicks": [...], "ticks": n, "resolved": bool,
             "unverified_opt_out": bool}.
    """
    report = {"clicks": [], "ticks": 0, "resolved": False, "unverified_opt_out": False}

    for _ in range(max_passes):
        if not _edu_layers(page):
            report["resolved"] = True
            break

        opt = _set_opt_out(page)
        if opt["ticked"]:
            report["ticks"] += 1
        elif opt["label"]:
            # The box is on screen but reads unchecked -- the tour WILL come back,
            # so this is reported rather than silently swallowed.
            report["unverified_opt_out"] = True

        clicked = _click_topmost_any(page, buttons)
        if clicked:
            report["clicks"].append(clicked)

        page.wait_for_timeout(1200)
        if not clicked:
            # Nothing we recognise to press: give the layer one more moment, then
            # stop to avoid spinning (the caller reports the leftover).
            page.wait_for_timeout(1200)
            report["resolved"] = not _edu_layers(page)
            break
    else:
        report["resolved"] = not _edu_layers(page)

    return report


def dismiss_edu_popups(page: Page, retries: int = 6) -> dict:
    """Dismiss whatever onboarding popup may be covering the current page.

    Keeps the previous semantics (keep pressing the usual onboarding labels until
    nothing responds) but the click mechanism is now tag-agnostic and targets the
    topmost pointer-receiving element, and opt-out boxes are ticked on the way.
    Returns the same report shape as `dismiss_edu_tour`.
    """
    report = {"clicks": [], "ticks": 0, "resolved": False}

    for _ in range(retries):
        report["ticks"] += _tick_dont_show_again(page)
        clicked = _click_topmost_any(page, POPUP_ADVANCE_BUTTONS, timeout=1500)
        if not clicked:
            report["resolved"] = True
            break
        report["clicks"].append(clicked)
        page.wait_for_timeout(700)

    return report


# --------------------------------------------------------------------------- #
# Page-specific flows
# --------------------------------------------------------------------------- #
def _discard_unsaved_draft(page: Page, wait_ms: int = 4000) -> bool:
    """Click Discard if the "we found an unsaved version of this post" dialog is up.

    Entering /post/create while a recovery snapshot exists pops a Discard /
    Continue dialog (observed 2026-09-23). It is the single most damaging blocker
    in this whole flow: it is a MUI **modal**, so the entire editor behind it is
    marked `aria-hidden="true"` -- and Playwright's `get_by_role(...)` **skips
    aria-hidden subtrees entirely**. The editor is fully rendered, a screenshot
    looks perfectly normal, `document.body.innerText` even contains the "Select"
    label, yet every role-based lookup returns 0 matches:

        get_by_role("button", name="Select", exact=True).count()  ->  0   # dialog up
        get_by_role("button", name="Select", exact=True).count()  ->  1   # dialog gone

    That is exactly how the first run of this version reported
    `product=no · resale=NOT enabled` on all three accounts.

    The dialog arrives ASYNCHRONOUSLY (the recovery snapshot is fetched after the
    first render), so polling is required -- a single check 2s after navigation
    races it and loses.

    Returns True when the dialog was found and Discard was clicked.
    """
    while wait_ms > 0:
        try:
            if page.evaluate(
                "() => document.body.innerText.includes('unsaved version')"
            ):
                break
        except Exception:
            return False
        page.wait_for_timeout(400)
        wait_ms -= 400
    else:
        return False
    return _click_topmost_any(page, DISCARD_BUTTONS, timeout=3000) is not None


def _add_first_product(page: Page, timeout: int = 8000) -> bool:
    """Post editor -> Select -> pick a product -> "Add N/20 product(s)".

    Needed because the resale switch only renders once the post has a product
    (`input[name=allowPromotersResell]` is its reliable fingerprint).

    Post-condition is **verified**: success means the resale switch is on screen,
    not merely "the Add button click did not throw". The previous version returned
    True right after the click, so a no-op Add still counted as success.

    Locators are CSS/`hasText` first on purpose: `get_by_role` returns nothing
    while a modal (e.g. the unsaved-draft dialog) has made the editor
    aria-hidden, which is the state this step usually runs in.
    """
    resale_sel = "input[name='allowPromotersResell']"

    def _has_product() -> bool:
        try:
            return page.locator(resale_sel).count() > 0
        except Exception:
            return False

    def _wait_product(ms: int) -> bool:
        while ms > 0:
            if _has_product():
                return True
            page.wait_for_timeout(400)
            ms -= 400
        return _has_product()

    if _has_product():
        return True  # a product is already in this post

    try:
        page.locator("button", has_text="Select").first.click(timeout=timeout)
    except Exception:
        try:
            page.get_by_role("button", name="Select", exact=True).first.click(timeout=timeout)
        except Exception as exc:
            print(f"    [EDU-WARN] could not open the product picker: "
                  f"{type(exc).__name__}: {str(exc).splitlines()[0]}")
            _debug_dump(page, "add_product_no_select")
            return False
    page.wait_for_timeout(1500)

    picked = False
    last_err = None
    for sel in ("[role=dialog] div[aria-label][role='button']",
                "div[aria-label][role='button']"):
        try:
            page.locator(sel).first.click(timeout=3000)
            picked = True
            break
        except Exception as exc:
            last_err = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
            continue
    if not picked:
        print(f"    [EDU-WARN] could not pick a product card: {last_err}")
        _debug_dump(page, "add_product_no_card")
        return False
    page.wait_for_timeout(800)

    # The confirm button reads "Add N/20 product(s)".
    #
    # DO NOT use `get_by_role("button", name=re.compile(r"Add \d+/\d+ product"))`:
    # the Python binding serialises the pattern into Playwright's own selector
    # syntax as `button[name=/Add \d+/\d+ product/]`, and the backslash-escaped
    # `/` makes its parser fail outright --
    #
    #   InvalidSelectorError: Error while parsing selector
    #   `button[name=/Add \d+/\d+ product/]` - unexpected symbol "\" at position 21
    #
    # so the locator can NEVER match, in any environment. (JS Playwright passes a
    # real RegExp object and is unaffected, which is why this only shows up in the
    # Python run.) A plain-string `:has-text` substring match is safe, and the
    # regex stays on the Python side where it belongs.
    add_btn = page.locator("button").filter(has_text="product(s)").first
    last_err = None

    def _selected_count() -> int:
        """How many products the picker thinks are selected (from 'Add N/M')."""
        try:
            m = re.search(r"Add\s+(\d+)/\d+", add_btn.inner_text(timeout=2000))
        except Exception:
            return -1
        return int(m.group(1)) if m else -1

    for _ in range(3):
        try:
            if _selected_count() == 0:
                # A card click silently missed; retry it rather than pressing a
                # 0/20 button and calling the resulting no-op a success.
                page.locator("[role=dialog] div[aria-label][role='button']").first.click(
                    timeout=2000
                )
                page.wait_for_timeout(800)
            add_btn.click(timeout=3000)
            if _wait_product(4000):
                return True
            last_err = "clicked but the resale switch never appeared"
        except Exception as exc:
            # Keep the reason: "element not found" and "… intercepts pointer
            # events" need completely different fixes, and swallowing the text
            # is what made the first CI failure so opaque.
            last_err = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
            page.wait_for_timeout(700)
    print(f"    [EDU-WARN] could not add a product: {last_err}")
    _debug_dump(page, "add_product_no_switch")
    return False


def _enable_resale(page: Page, timeout: int = 4000) -> dict:
    """Turn ON "Allow approved co-sellers to resell" and verify it is on.

    The control is `<input type="checkbox" name="allowPromotersResell">` with
    `opacity: 0` inside a MUI Switch, and the visible "Off"/"On" text lives INSIDE
    the switch -- so the input's accessible name is literally "Off". That is why
    the previous `get_by_role("checkbox", name="allowPromotersResell")` could never
    match and the step was silently skipped, leaving +998 / +997 without the resale
    onboarding (which only fires once resale is enabled).

    Enabling it also auto-opens the "Customize product settings" drawer showing the
    "Set resale earnings" tour, so the caller must dismiss that straight after.

    Returns {"found": bool, "enabled": bool, "how": str}.
    """
    report = {"found": False, "enabled": False, "how": "not-found"}
    sel = "input[name='allowPromotersResell']"

    def _drawer_open() -> bool:
        try:
            return bool(page.evaluate(
                "() => document.body.innerText.includes('Customize product settings')"
            ))
        except Exception:
            return False

    try:
        if not page.locator(sel).count():
            return report
        report["found"] = True
    except Exception:
        return report

    if _drawer_open():
        report["enabled"] = True
        report["how"] = "drawer-already-open"
        return report

    try:
        if page.locator(sel).first.is_checked():
            report["enabled"] = True
            report["how"] = "already-on"
            return report
    except Exception:
        pass

    try:
        page.locator(sel).first.click(timeout=timeout)
    except Exception:
        pass
    page.wait_for_timeout(1200)
    # Either the input reads checked, or the drawer side effect proves it worked
    # (the form re-renders underneath the drawer, so `checked` alone is not enough).
    try:
        if page.locator(sel).first.is_checked() or _drawer_open():
            report["enabled"] = True
            report["how"] = "click"
            return report
    except Exception:
        if _drawer_open():
            report["enabled"] = True
            report["how"] = "click+drawer"
            return report

    # An aria-hidden backdrop from an open MUI popup can shadow the switch.
    try:
        if page.evaluate(
            """() => { const i = document.querySelector("input[name='allowPromotersResell']");
                       if (i) i.click(); return i ? i.checked : false; }"""
        ) or _drawer_open():
            report["enabled"] = True
            report["how"] = "js-click"
    except Exception:
        pass
    return report


def _close_topmost_edu_popup(page: Page) -> bool:
    """Close the popup that owns the topmost EDU layer (X inside it).

    Gated on an onboarding layer actually being on screen: `[data-testid=CloseIcon]`
    also matches the **post editor's own X**, and clicking that would close the
    editor mid-flow and make the resale switch unreachable. No EDU layer -> no
    click.
    """
    if not _edu_layers(page):
        return False
    try:
        icons = page.locator("[data-testid='CloseIcon']")
        for i in range(min(icons.count(), 4)):
            node = icons.nth(i)
            try:
                box = node.bounding_box()
                if not box or box["width"] <= 0:
                    continue
                node.click(timeout=2000)
                page.wait_for_timeout(600)
                return True
            except Exception:
                continue
    except Exception:
        pass
    return False


# --------------------------------------------------------------------------- #
# Failure self-evidence
# --------------------------------------------------------------------------- #
# A preflight that fails silently in CI is worse than one that fails loudly: the
# run is headless, nobody sees the page, and the log only says `product=no`.
# With DISMISS_EDU_DEBUG=1 every failure leaves a screenshot + the page text in
# data/_edu_debug/ so the next person can see what the browser was actually
# looking at. Nothing is written unless the flag is set.
_DEBUG_DIR = PROJECT_ROOT / "data" / "_edu_debug"


def _debug_dump(page: Page, tag: str) -> None:
    """Save a screenshot and the page text for `tag` (only with DISMISS_EDU_DEBUG=1)."""
    if os.environ.get("DISMISS_EDU_DEBUG", "").strip().lower() not in ("1", "true", "yes", "on"):
        return
    try:
        _DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(_DEBUG_DIR / f"{tag}.png"))
        head = ""
        try:
            head = page.evaluate(
                "() => `url=${location.href}\\nviewport=${innerWidth}x${innerHeight}"
                " dpr=${devicePixelRatio}\\n`"
            )
        except Exception:
            pass
        (_DEBUG_DIR / f"{tag}.txt").write_text(
            head + page.inner_text("body"), encoding="utf-8"
        )
        print(f"    [EDU-DEBUG] dumped data/_edu_debug/{tag}.png")
    except Exception:
        pass


def _leave_editor_without_saving(page: Page) -> int:
    """Close the post editor and discard any "unsaved changes" prompt.

    The editor's X is an **icon button** (`aria-label="Close"`, no text node), so
    the old text-only `_click_topmost_text(page, "Close")` was a silent no-op: the
    editor stayed open, the abandoned edit became a recovery snapshot, and the
    next run got the "We found an unsaved version of this post" dialog that blinds
    every role-based locator. Clearing it here is what keeps the preflight
    idempotent -- run it twice and the second run must report 0 drafts.

    Returns the number of discard prompts that were confirmed.
    """
    discarded = 0

    # A recovery dialog may already be up (e.g. the editor was reopened).
    if _discard_unsaved_draft(page, wait_ms=1200):
        discarded += 1
        page.wait_for_timeout(600)

    for sel in ("button[aria-label='Close']", "[data-testid='CloseIcon']"):
        try:
            page.locator(sel).first.click(timeout=2000)
            break
        except Exception:
            continue
    page.wait_for_timeout(1000)

    # The X is usually followed by a "Discard this post?" confirm.
    for _ in range(3):
        if _click_topmost_any(page, DISCARD_BUTTONS, timeout=2000) is not None:
            discarded += 1
            page.wait_for_timeout(600)
        else:
            break
    return discarded


def handle_create_post_edu(page: Page, base_url: str) -> dict:
    """Trigger and finish the post-creation onboarding flows.

    Flow measured live 2026-09-23 (same for +999 / +998 / +997):
      1. /post/create -> (optional) "unsaved version of this post" -> Discard
      2. Select -> pick a product -> "Add 1/20 product(s)"
      3. popup "You've added products - great start!" -> tick "Do not show me
         this again" -> close
      4. enable "Allow approved co-sellers to resell" -> the "Customize product
         settings" drawer opens BY ITSELF with the 3-step resale tour
         ("Set resale earnings" -> "Choose a resale model" -> "Set per-product values")
      5. tick "Do not show this again" (VERIFIED) -> Start Customizing -> Done -> Done
      6. Cancel the drawer, then leave the editor without saving

    Returns a report dict; `tour.unverified_opt_out` / `opt_out` tell the caller
    whether the account's "don't show again" flag was really persisted.
    """
    report = {
        "added_product": False,
        # Split on purpose: `entry` must be 0 on a healthy run. A non-zero entry
        # count means the PREVIOUS run left a recovery snapshot behind, i.e. the
        # preflight is feeding itself and never converges. `exit` is the normal
        # "Discard this post?" confirm raised when the editor is closed.
        "drafts_discarded": 0,
        "drafts_on_entry": 0,
        "drafts_on_exit": 0,
        "popup_opt_out": False,
        "opt_out_seen": False,
        "resale": None,
        "tour": None,
    }

    # Close any blocking modal first ("Your shop is ready" etc.)
    _click_topmost_text(page, "Close", timeout=1500)

    if not _open(page, f"{base_url}/post/create"):
        return report

    # A recovery dialog makes the whole editor aria-hidden, which blinds every
    # role-based lookup -- so it MUST go before anything else. It can be raised
    # more than once (leaving the editor without saving arms the next visit), so
    # clear it in a loop.
    for _ in range(3):
        if _discard_unsaved_draft(page):
            report["drafts_discarded"] += 1
            report["drafts_on_entry"] += 1
        else:
            break
    dismiss_edu_popups(page)

    # "Creating a post for one of your events?" -> always No (accounts with events
    # would otherwise be redirected into the event-post flow).
    _click_topmost_text(page, "No", timeout=1500)
    page.wait_for_timeout(300)

    # Step through the post creation wizard.
    for btn_name in ("Next", "Next", "Start Creating"):
        if _click_topmost_text(page, btn_name, timeout=2000):
            page.wait_for_timeout(400)
            dismiss_edu_popups(page)

    # -- 3. product, then the "You've added products" popup ----------------
    _debug_dump(page, "before_add_product")
    report["added_product"] = _add_first_product(page)
    if report["added_product"]:
        page.wait_for_timeout(1500)
        # `dismiss_edu_popups` ticks the opt-out BEFORE pressing the advance
        # button, so its ticks must be propagated: otherwise the popup is closed
        # with the box already ticked while the report still says "not verified"
        # (and the summary would print a misleading `opt_out=n/a`).
        if dismiss_edu_popups(page)["ticks"]:
            report["popup_opt_out"] = True
    opt = _set_opt_out(page)
    if opt["ticked"]:
        report["popup_opt_out"] = True
    elif opt["label"]:
        report["opt_out_seen"] = True
        print(f"    [EDU-WARN] opt-out checkbox not verified ({opt['how']})")
    _close_topmost_edu_popup(page)
    page.wait_for_timeout(600)

    # -- 4/5. enable resale -> the tour appears in the auto-opened drawer ---
    resale = _enable_resale(page)
    report["resale"] = resale
    if resale["enabled"]:
        page.wait_for_timeout(1800)
        if _edu_layers(page):
            tour = dismiss_edu_tour(page)
            report["tour"] = tour
            if tour["ticks"]:
                report["popup_opt_out"] = True
            if tour["unverified_opt_out"] and not tour["ticks"]:
                print("    [EDU-WARN] resale tour opt-out checkbox not verified")

    # -- 6. leave without saving ------------------------------------------
    _close_drawer(page, prefer_cancel=True)
    page.wait_for_timeout(500)
    exit_drafts = _leave_editor_without_saving(page)
    report["drafts_discarded"] += exit_drafts
    report["drafts_on_exit"] += exit_drafts
    return report


def handle_post_selling_edu(page: Page, base_url: str) -> dict:
    """Finish the post-selling onboarding tour on every event the suite touches.

    Path per event:  Events -> <event> -> Post tab -> Selling sub-tab -> Customize
    The tour ("Set resale earnings" -> "Choose a resale model" -> "Set per-product
    values") only exists inside that drawer, which the old implementation never
    reached.

    The tour is **per account** (server-side, no localStorage key): once the
    drawer has been opened and dealt with, no other event can still be carrying
    it. So the sweep stops at the first row whose drawer actually opened --
    opening a drawer costs ~20s a row (five short-timeout clicks that mostly
    fail on events without a post), and a 15-event walk added ~5 minutes of pure
    CI time for nothing. Set DISMISS_EDU_FULL_SWEEP=1 to force the old full walk.

    Returns {"events_visited": n, "tours_finished": n, "leftovers": [...]}.
    """
    full_sweep = os.environ.get("DISMISS_EDU_FULL_SWEEP", "").strip().lower() in (
        "1", "true", "yes", "on",
    )
    report = {"events_visited": 0, "tours_finished": 0, "leftovers": []}

    try:
        page.goto(f"{base_url}/events", timeout=60000)
    except Exception:
        report["leftovers"].append("events page unreachable")
        return report
    page.wait_for_timeout(3000)
    dismiss_edu_popups(page)

    rows = page.locator(".MuiTableRow-root")
    try:
        total = min(rows.count(), MAX_EVENT_ROWS + 1)  # +1 for the header row
    except Exception:
        return report

    for i in range(1, total):
        try:
            title = (rows.nth(i).locator("td").first.inner_text() or "").strip()
        except Exception:
            continue
        if not title:
            continue

        # Enumerate by table position: event titles are dynamic (they carry test
        # data), so the row index is more stable than any literal name.
        try:
            rows.nth(i).locator("td").first.click(timeout=6000)
        except Exception:
            continue
        page.wait_for_timeout(2500)
        report["events_visited"] += 1

        decisive = False
        try:
            if _open_post_selling_drawer(page):
                # The drawer opened: this is the only place the tour lives, and
                # it can only be armed once per account -> this row settles it.
                decisive = True
                if _edu_layers(page):
                    result = dismiss_edu_tour(page)
                    if result["resolved"]:
                        report["tours_finished"] += 1
                        print(f"    [{title}] resale tour finished "
                              f"(clicks: {' > '.join(result['clicks'])}; opt-out ticks: {result['ticks']})")
                    else:
                        report["leftovers"].append(
                            f"{title}: tour not finished (clicked {result['clicks']})"
                        )
                else:
                    print(f"    [{title}] post-selling drawer opened, no onboarding layer")
                _close_drawer(page)
        except Exception as exc:  # never let one event abort the whole sweep
            report["leftovers"].append(f"{title}: {type(exc).__name__}: {exc}")

        if decisive and not full_sweep:
            break

        # Back to the list for the next row
        try:
            page.goto(f"{base_url}/events", timeout=60000)
            page.wait_for_timeout(2000)
        except Exception:
            break

    return report


def _open_post_selling_drawer(page: Page) -> bool:
    """Post tab -> Selling sub-tab -> Customize; True when the drawer is open.

    Short timeouts on purpose: most events have no post at all, so this has to
    fail fast instead of burning 30s on every row.
    """
    try:
        page.get_by_role("tab", name="Post", exact=True).click(timeout=3500)
        page.wait_for_timeout(1500)
        page.get_by_role("tab", name="Selling", exact=True).click(timeout=2500)
        page.wait_for_timeout(1500)
        page.get_by_role("button", name="Customize", exact=True).click(timeout=3000)
        page.wait_for_timeout(2500)
        return True
    except Exception:
        return False


def _close_drawer(page: Page, prefer_cancel: bool = False) -> None:
    """Leave a drawer without saving anything.

    `prefer_cancel=True` for the resale drawer: Cancel is explicit about not
    persisting, whereas the X may silently keep what was edited.
    """
    close_icon = lambda: page.locator("[data-testid='CloseIcon']").first.click(timeout=2500)
    cancel = lambda: page.get_by_role("button", name="Cancel", exact=True).first.click(timeout=2000)
    attempts = (cancel, close_icon) if prefer_cancel else (close_icon, cancel)
    for attempt in attempts + (lambda: page.keyboard.press("Escape"),):
        try:
            attempt()
            page.wait_for_timeout(800)
            return
        except Exception:
            continue


def handle_customers(page: Page) -> None:
    """Customers -> Followers page EDU handling."""
    try:
        page.goto(f"{ENV_BASE}/customers", timeout=60000)
        page.wait_for_timeout(2500)
    except Exception:
        return
    dismiss_edu_popups(page)

    try:
        page.get_by_role("tab", name="Followers").click(timeout=5000)
        page.wait_for_timeout(1500)
        dismiss_edu_popups(page)
    except Exception:
        pass

    _click_topmost_text(page, "Close", timeout=3000)


def handle_account_edu(page: Page, base_url: str) -> bool:
    """`/account` -> "Manage multiple accounts" EDU -> "Got it".

    Measured 2026-09-23 on +998: a popover anchored to the "Switch" button with
    title "Manage multiple accounts" and a single "Got it" action. It is one-shot
    per account (it does not come back after being dismissed).
    """
    if not _open(page, f"{base_url}/account"):
        return False
    page.wait_for_timeout(2000)
    dismiss_edu_popups(page)
    if _click_topmost_any(page, ACCOUNT_EDU_BUTTONS, timeout=3000) is not None:
        page.wait_for_timeout(800)
        return True
    return False


# --------------------------------------------------------------------------- #
# Per-account driver
# --------------------------------------------------------------------------- #
def dismiss_for_account(playwright, account: dict) -> dict:
    name = account["name"]
    cookie_path = COOKIE_DIR / account["cookie_file"]
    home_url = account["home_url"]

    result = {
        "name": name,
        "ok": False,
        "cookie_missing": False,
        "leftovers": [],
        "tours_finished": 0,
        "events_visited": 0,
        # Diagnostics for the summary: the whole point of this preflight is the
        # "do not show this again" flag, so its verified state is reported.
        "opt_out_verified": False,
        "resale_enabled": False,
        "products_added": 0,
        "account_edu_dismissed": False,
    }

    if not cookie_path.exists():
        # Distinct from a dead session: this means step 2 (get_all_cookies.py) did
        # not produce the file at all, so CI should look there first.
        result["cookie_missing"] = True
        print(f"[{name}] Cookie file not found, skipping: {cookie_path}")
        return result

    print(f"\n[{name}] Loading cookie, starting EDU dismissal...")

    # CI (GitHub-hosted runner) has no display, so it must stay headless; locally
    # keep the browser visible so the flow can be watched.
    headless_ci = os.environ.get("CI", "").lower() == "true"
    browser = playwright.chromium.launch(headless=headless_ci)
    context = browser.new_context(storage_state=str(cookie_path))
    page = context.new_page()

    try:
        # -- 0. Session sanity check: a dead cookie makes every later step a no-op
        if not _open(page, home_url):
            result["leftovers"].append(f"home page unreachable: {home_url}")
            return result
        if "/login" in page.url:
            result["leftovers"].append("session expired (redirected to /login)")
            return result

        # -- 1. Shop home page EDU
        dismiss_edu_popups(page)
        page.wait_for_timeout(500)
        dismiss_edu_popups(page)

        # -- 2. Post creation wizard EDU (universal across all accounts).
        #       Also enables resale, which is the only way to reach the resale
        #       onboarding on accounts that have no event posts.
        created = handle_create_post_edu(page, ENV_BASE)
        resale = created.get("resale") or {}
        tour = created.get("tour") or {}
        opt_out_seen = bool(created.get("opt_out_seen") or tour.get("unverified_opt_out"))
        result["opt_out_verified"] = bool(
            created.get("popup_opt_out") and not tour.get("unverified_opt_out")
        )
        if opt_out_seen and not result["opt_out_verified"]:
            # The box was on screen but never verified checked -> the tour WILL be
            # back on the next run. Reported, not swallowed.
            result["leftovers"].append(
                "post-create: 'do not show this again' present but could not be verified"
            )
        if created.get("added_product"):
            result["products_added"] += 1
        if resale.get("enabled"):
            result["resale_enabled"] = True
        if tour:
            result["tours_finished"] += 1 if tour.get("resolved") else 0
            if not tour.get("resolved"):
                result["leftovers"].append(
                    f"resale tour not finished (clicked {tour.get('clicks')})"
                )
            if tour.get("unverified_opt_out") and not tour.get("ticks"):
                result["leftovers"].append(
                    "resale tour: 'do not show this again' could not be verified"
                )
        if result["opt_out_verified"]:
            opt_state = "verified"
        elif opt_out_seen:
            opt_state = "NOT verified"   # a box was on screen but would not tick
        else:
            opt_state = "n/a"            # nothing shown -> nothing to tick
        print(
            f"    post-create: product={'yes' if created.get('added_product') else 'no'} · "
            f"resale={'on by ' + resale['how'] if resale.get('enabled') else 'NOT enabled'} · "
            f"tour={'finished' if tour.get('resolved') else ('skipped' if not tour else 'UNFINISHED')} · "
            f"opt-out={opt_state} · "
            f"drafts={created.get('drafts_discarded', 0)}"
            f"(entry={created.get('drafts_on_entry', 0)}, exit={created.get('drafts_on_exit', 0)})"
        )

        # -- 3. Post-selling tour inside the event post drawer.
        #       Skipped for the co-seller account: it has no /events route at all
        #       (HTTP 404 "This page could not be found.").
        if account.get("has_events", True):
            selling = handle_post_selling_edu(page, ENV_BASE)
            result["events_visited"] = selling["events_visited"]
            result["tours_finished"] += selling["tours_finished"]
            result["leftovers"].extend(selling["leftovers"])
        else:
            print(f"    [{name}] no /events route for this role -- skipping the event sweep")

        # -- 4. Customers -> Followers
        handle_customers(page)

        # -- 5. Account page EDU ("Manage multiple accounts" -> Got it)
        if handle_account_edu(page, ENV_BASE):
            result["account_edu_dismissed"] = True
            print("    /account: 'Manage multiple accounts' dismissed")

        # -- 6. Back to the storefront to settle
        if _open(page, home_url):
            dismiss_edu_popups(page)
            page.wait_for_timeout(500)
            dismiss_edu_popups(page)

        result["ok"] = True
        # Persist the state (cookies + the "do not show again" choice the app
        # stored) so the pytest run starts from the same place.
        context.storage_state(path=str(cookie_path))
        print(f"[{name}] EDU dismissal complete, cookie updated -> {cookie_path}")
    finally:
        try:
            page.close()
        except Exception:
            pass
        try:
            context.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass

    return result


def _open(page: Page, url: str, retries: int = 2) -> bool:
    """goto with retries -- the app throws net::ERR_TOO_MANY_REDIRECTS on a cold
    navigation often enough that a single attempt is not a reliable probe."""
    for _ in range(retries):
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            return True
        except Exception:
            page.wait_for_timeout(1000)
    return False


def main() -> int:
    print("=== Starting EDU popup dismissal ===")
    strict = os.environ.get("DISMISS_EDU_STRICT", "").strip().lower() in ("1", "true", "yes", "on")

    results = []
    only = os.environ.get("DISMISS_EDU_ONLY", "").strip().lower()
    accounts = [a for a in ACCOUNTS if only in a["name"].lower()] if only else ACCOUNTS
    with sync_playwright() as pw:
        for account in accounts:
            results.append(dismiss_for_account(pw, account))

    print("\n=== EDU dismissal summary ===")
    hard_failure = False
    cookie_missing = False
    leftovers = 0
    for r in results:
        state = "OK" if r["ok"] else "FAILED"
        print(
            f"  [{r['name']}] {state} · events={r['events_visited']} · "
            f"tours_finished={r['tours_finished']} · "
            f"resale={'on' if r.get('resale_enabled') else 'off'} · "
            f"opt_out={'verified' if r.get('opt_out_verified') else 'n/a'} · "
            f"leftovers={len(r['leftovers'])}"
        )
        for item in r["leftovers"]:
            leftovers += 1
            print(f"    [EDU-LEFT] {item}")
        if r.get("cookie_missing"):
            cookie_missing = True
        if not r["ok"]:
            hard_failure = True

    if cookie_missing:
        print("=== EDU dismissal aborted: a cookie file is missing (check step 2, get_all_cookies.py) ===")
        return 2
    if hard_failure:
        print("=== EDU dismissal aborted: an account session/page could not be opened ===")
        return 3
    if leftovers and strict:
        print(f"=== EDU dismissal strict mode: {leftovers} unresolved onboarding layer(s) ===")
        return 4
    if leftovers:
        print(
            f"=== EDU dismissal finished with {leftovers} unresolved onboarding layer(s) "
            f"(non-fatal; set DISMISS_EDU_STRICT=1 to fail instead) ==="
        )
        return 0
    print("=== All accounts processed, no onboarding layer left ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
