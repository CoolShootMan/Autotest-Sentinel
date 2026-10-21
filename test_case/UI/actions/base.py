import os
import re
import subprocess
import sys
from typing import cast

from playwright.sync_api import Page, Locator, expect
from loguru import logger

# Calculate project base directory dynamically (search up for .git or test_case)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(BASE_DIR, "test_case")) and BASE_DIR != os.path.dirname(BASE_DIR):
    BASE_DIR = os.path.dirname(BASE_DIR)
logger.info(f"ACTIONS_BASE_DIR: {BASE_DIR}")
from page.home import page_element_role_click, page_element_label_click, page_open

# Shared locator constants (single source of truth in test_case/UI/locators.py)
sys.path.insert(0, os.path.join(BASE_DIR, "test_case", "UI"))
try:
    from locators import LOCATORS as _LOCATORS
except Exception:
    _LOCATORS = {}

def _resolve_locator(s):
    """Replace {{@key}} placeholders with values from locators.py."""
    if not isinstance(s, str) or "{{@" not in s:
        return s
    for _k, _v in _LOCATORS.items():
        s = s.replace("{{@%s}}" % _k, str(_v))
    return s

# Only import AI vision modules when explicitly enabled (avoids ~20s startup delay)
# Set ENABLE_AI_VISION=true in .env or shell to enable
if os.getenv("ENABLE_AI_VISION", "").lower() in ("1", "true", "yes"):
    from ..utils.ai_vision import ai_vision
else:
    ai_vision = None
    logger.debug("AI vision disabled (set ENABLE_AI_VISION=1 to enable)")

# Cross-test-case global variable store (survives across cases in the same pytest
# process; a step opts in with `save_as` + `global: true`). See global_state.py.
from .global_state import GLOBAL_VARS as _GLOBAL_VARS, set_global as _set_global


def _merged_context_vars(page):
    """Build the full {{var}} lookup table for a page.

    Precedence: page._workflow_context (local, this case/session) overrides the
    cross-case GLOBAL_VARS store.  Falls back to an empty dict when neither exists.
    """
    _wc = getattr(page, "_workflow_context", None) or {}
    # workflow_context wins over global on key collision
    return {**_GLOBAL_VARS, **_wc}


def _fill_vars(page, s):
    """Substitute {{var}} placeholders (from the workflow/global context) inside a string.

    Mirrors the resolution already performed by ``_smart_click_core`` and ``execute_js`` so that
    native actions such as ``open_url`` / ``verify_text_visible`` / ``verify_value`` / ``smart_fill``
    can also consume variables saved earlier via ``execute_js`` ``save_as`` (or published with
    ``global: true``).  No-op when ``s`` is not a string or contains no ``{{...}}`` placeholder, so
    it is safe to call unconditionally on every string argument.
    """
    if not isinstance(s, str) or "{{" not in s:
        return s
    _ctx = _merged_context_vars(page)
    for _k, _val in _ctx.items():
        if _k:
            s = s.replace("{{%s}}" % _k, str(_val))
    return s


def open_url(page: Page, v):
    logger.info(f">>> Current Step: open_url, v={v}, type={type(v)}")
    url = v.get("open") or v.get("url") if isinstance(v, dict) else v
    url = _fill_vars(page, url)
    if url:
        # {{var}} backfill: a URL is often built from a value saved by an earlier step
        # (e.g. the public post URL read off the event "Post" tab) -> navigate natively
        # instead of falling back to `location.href = '{{post_url}}'` JS.
        url = _fill_placeholders(url, page)
        params = v if isinstance(v, dict) else {}
        logger.info(f">>> open_url params keys: {list(params.keys())}")
        # --- Context-level configuration (must be set before page navigation) ---
        ctx = page.context

        geolocation = params.get("geolocation")
        if geolocation:
            import json
            if isinstance(geolocation, str):
                geolocation = json.loads(geolocation)
            logger.info(f"Setting geolocation: {geolocation}")
            ctx.set_geolocation(geolocation)

        timezone_id = params.get("timezone_id")
        if timezone_id:
            # timezone_id is a context creation param, simulate via JS injection
            logger.info(f"Injecting timezone override: {timezone_id}")
            page.add_init_script(f"""
                // Override Date timezone
                const _origTimezone = Intl.DateTimeFormat;
                window.Intl.DateTimeFormat = function(...args) {{
                    if (args.length === 0) args.push(undefined, {{ timeZone: '{timezone_id}' }});
                    else if (args.length === 1) args.push({{ timeZone: '{timezone_id}' }});
                    else if (args[1] && typeof args[1] === 'object') args[1].timeZone = '{timezone_id}';
                    return new _origTimezone(...args);
                }};
                window.Intl.DateTimeFormat.prototype = _origTimezone.prototype;
                window.Intl.DateTimeFormat.supportedLocalesOf = _origTimezone.supportedLocalesOf;
            """)

        locale = params.get("locale")
        if locale:
            # locale is a context creation param, simulate via JS injection
            logger.info(f"Injecting locale override: {locale}")
            page.add_init_script(f"""
                // Override navigator.language and navigator.languages
                Object.defineProperty(navigator, 'language', {{ get: () => '{locale}', configurable: true }});
                Object.defineProperty(navigator, 'languages', {{ get: () => ['{locale}'], configurable: true }});
            """)

        permissions = params.get("permissions")
        if permissions:
            logger.info(f"Granting permissions: {permissions}")
            ctx.grant_permissions(permissions)

        # Check if cookie_file is provided - inject cookies BEFORE opening page
        cookie_file = params.get("cookie_file")
        if cookie_file:
            logger.info(f">>> Injecting cookies BEFORE opening page: {cookie_file}")
            try:
                _inject_cookies_to_context(page, cookie_file)
                logger.info("✓ Cookies injected successfully, opening page with authenticated session")
            except Exception as e:
                logger.warning(f"⚠ Cookie injection failed: {e}. Continuing with unauthenticated session.")

        from page.home import page_open
        page_open(page, url)

        # Automatically handle pop-ups that appear after page loading
        auto_handle_modals_enabled = params.get("auto_handle_modals", True)
        if auto_handle_modals_enabled:
            logger.info(">>> Auto-handling modals after page load")
            try:
                # Wait dynamically for page network activity to settle (max 8s)
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                # Tiny buffer for JS to render the modal after network resolves
                page.wait_for_timeout(1000)
                auto_handle_modals(page, {"timeout": 3000, "ignore_if_not_found": True})
            except Exception as e:
                # Failure in bullet layer processing does not affect the main process
                logger.debug(f"Auto modal handling skipped or failed: {e}")
        else:
            logger.info(">>> Auto-handling modals is disabled")

def open_until_ready(page: Page, v: dict):
    """
    Open a URL and wait until the expected content is really rendered, re-opening
    the URL until it is.

    Storefront pages can briefly serve a client-side 404 ("This page could not be
    found") right after a post is published or its URL alias is re-bound, so a
    plain `open` a few seconds after publishing lands on the 404 shell. Retrying
    here removes that race instead of relying on a fixed sleep.

    YAML usage (the step key MUST be exactly `open_until_ready`: any other name
    starting with "open" is dispatched to open_url by prefix and the retry is
    silently lost):
        open_until_ready:
            url: "{BASE_URL}/autotestshop/post/test1234"
            ready: 'text="General Admission"'   # selector that only exists on the real page
            retries: 6                          # optional, default 3（降低默认重试，失败用例更快失败、缩短单用例耗时）
            timeout: 8000                       # optional, per-attempt wait for `ready`
            retry_delay: 3000                   # optional, wait between attempts
            settle: 1000                        # optional, wait after `ready` is found
    """
    url = v.get("url") or v.get("open")
    ready = v.get("ready") or v.get("ready_selector")
    retries = int(v.get("retries", 3))
    timeout = int(v.get("timeout", 8000))
    retry_delay = int(v.get("retry_delay", 3000))
    settle = int(v.get("settle", 1000))
    not_found_marker = str(v.get("not_found_text", "could not be found")).lower()

    if not url:
        raise AssertionError("open_until_ready: 'url' is required")
    if not ready:
        raise AssertionError("open_until_ready: 'ready' is required")

    last_body = ""
    for attempt in range(1, retries + 1):
        try:
            # Modal handling is deferred to the successful attempt: it costs up to
            # ~9s and is pointless while the page is still the 404 shell.
            open_url(page, {"open": url, "auto_handle_modals": False})
            page.wait_for_selector(ready, timeout=timeout)

            if v.get("auto_handle_modals", True):
                try:
                    auto_handle_modals(page, {"timeout": 3000, "ignore_if_not_found": True})
                except Exception as e:
                    logger.debug(f"open_until_ready: modal handling skipped: {e}")

            page.wait_for_timeout(settle)
            logger.info(f"open_until_ready: '{ready}' rendered on attempt {attempt}/{retries} - {url}")
            return
        except Exception as e:
            try:
                last_body = (page.inner_text("body") or "").strip()[:200].replace("\n", " | ")
            except Exception:
                last_body = "<body unreadable>"
            state = "404 shell" if not_found_marker in last_body.lower() else "content not ready"
            logger.warning(
                f"open_until_ready: attempt {attempt}/{retries} -> {state} - {url} - {str(e)[:120]}"
            )
            if attempt < retries:
                page.wait_for_timeout(retry_delay)

    try:
        page.screenshot(path="fail_open_until_ready.png")
    except Exception:
        pass
    raise AssertionError(
        f"open_until_ready: '{ready}' never rendered after {retries} attempts - {url}. "
        f"Last page body: {last_body}"
    )

def swipe_avoid_plus(page: Page, v: dict):
    x = v.get("x", 0)
    y = v.get("y", 300)
    logger.info(f"Swiping/Scrolling: x={x}, y={y}")
    drawer = page.locator(".MuiDrawer-root div").filter(has=page.locator("[data-som-id], input")).first
    if drawer.is_visible():
        logger.info("Active drawer detected. Scrolling drawer content...")
        drawer.evaluate(f"el => el.scrollBy({x}, {y})")
    else:
        page.mouse.wheel(x, y)
    page.wait_for_timeout(1000)

def smart_swipe(page: Page, v: dict):
    swipe_avoid_plus(page, v)

def smart_sleep(page: Page, v):
    ms = (v.get("sleep") or v.get("ms") or 1000) if isinstance(v, dict) else v
    page.wait_for_timeout(float(ms))

def smart_press(page: Page, v):
    key = (v.get("press") or v.get("key")) if isinstance(v, dict) else v
    if key:
        page.keyboard.press(key)

def smart_screenshot(page: Page, v: dict):
    name = v.get("name", "screenshot")
    page.screenshot(path=f"{name}.png")

def wait_for_selector(page: Page, v: dict):
    selector = v.get("selector") or v.get("locator")
    timeout = v.get("timeout", 30000)
    scroll = v.get("scroll", False)
    if selector:
        el = page.locator(selector).first
        if scroll:
            # First try scroll_into_view_if_needed
            try:
                el.scroll_into_view_if_needed(timeout=5000)
                page.wait_for_timeout(500)
                return
            except Exception as e:
                logger.warning(f"scroll_into_view_if_needed failed: {e}, trying iterative scroll...")
            
            # Fallback: iterative scrolling until element appears
            import time
            start = time.time()
            scroll_distance = 400
            while time.time() - start < timeout / 1000:
                if el.is_visible(timeout=500):
                    logger.info(f"wait_for_selector: element appeared after scrolling")
                    return
                # Use our robust page_scroll to scroll down
                page.evaluate(f"""
                    (delta) => {{
                        const elemBelowMouse = document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2);
                        if (elemBelowMouse) {{
                            let current = elemBelowMouse;
                            while (current && current !== document.body) {{
                                const style = window.getComputedStyle(current);
                                if ((style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                                    current.scrollHeight > current.clientHeight) {{
                                    current.scrollBy({{ top: delta, behavior: 'instant' }});
                                    return;
                                }}
                                current = current.parentElement;
                            }}
                        }}
                        window.scrollBy({{ top: delta, behavior: 'instant' }});
                    }}
                """, scroll_distance)
                page.wait_for_timeout(300)
            
            # Final check
            if el.is_visible(timeout=500):
                return
            
            page.screenshot(path=f"fail_wait_selector_{selector[:30]}.png")
            raise Exception(f"wait_for_selector: element '{selector}' not found after scrolling")
        else:
            page.wait_for_selector(selector, timeout=timeout)

def wait_for_url(page: Page, v: dict):
    url = v.get("url") or v.get("verify_navigation")
    timeout = v.get("timeout", 30000)
    if url:
        # {{var}} backfill so a dynamic expected URL (e.g. "{{post_url}}") can be asserted
        url = _fill_placeholders(url, page)
        if isinstance(url, str) and "*" in url:
            url = re.compile(url.replace("*", ".*"))
        page.wait_for_url(url, timeout=timeout)

def save_html(page: Page, v: dict):
    name = v.get("name", "page")
    with open(f"{name}.html", "w", encoding="utf-8") as f:
        f.write(page.content())

def smart_if(page: Page, v: dict):
    condition = v.get("condition", {})
    then_steps = v.get("then", {})
    else_steps = v.get("else", {})
    
    locator_str = condition.get("locator")
    locator_str = _resolve_locator(locator_str)
    role = condition.get("role")
    name = condition.get("name")
    text = condition.get("text")
    state = condition.get("state", "visible")
    timeout = condition.get("timeout", 5000)
    
    logger.info(f"Evaluating if condition: {condition}")
    
    is_true = False
    try:
        if locator_str:
            if locator_str.startswith("/") or locator_str.startswith("xpath="):
                xpath_locator = locator_str if locator_str.startswith("xpath=") else f"xpath={locator_str}"
                el = page.locator(xpath_locator).first
            else:
                el = page.locator(locator_str).first
        elif role:
            el = page.get_by_role(role, name=name).first
        elif text:
            el = page.get_by_text(text, exact=condition.get("exact", False)).first
        else:
            raise ValueError("Condition must specify locator, role, or text")
            
        if state == "visible":
            el.wait_for(state="visible", timeout=timeout)
            is_true = True
        elif state == "hidden":
            el.wait_for(state="hidden", timeout=timeout)
            is_true = True
    except Exception as e:
        logger.info(f"Condition evaluated to False: {e}")
        is_true = False
        
    from . import get_action
    
    steps_to_run = then_steps if is_true else else_steps
    
    if steps_to_run:
        for k, step_v in steps_to_run.items():
            logger.info(f"  >>> If-block executing step: {k}")
            action = get_action(k)
            if action:
                action(page, step_v)
                # (2026-10-15 fix, T5649) defensive: only the MAIN fixture page gets
                # `_execution_history` initialized (test_ui.py:67). Pages created by
                # create_session (guest/partner namespaces) don't have it, and the old
                # getattr(...) without default raised AttributeError on every if-block
                # executed inside a session namespace. Mirrors the safe pattern at L1049.
                _hist = getattr(page, "_execution_history", None)
                if _hist is not None:
                    _hist.append((k, step_v))
            else:
                logger.error(f"  >>> If-block: Action '{k}' not found.")
                raise Exception(f"Action '{k}' not found in if block.")

def smart_fill(page: Page, v: dict):  
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_value = v.get("value", "")
    target_value = _fill_vars(page, target_value)
    target_locator = v.get("locator")
    target_locator = _resolve_locator(target_locator)
    target_frame = v.get("frame") or v.get("frame_locator")
    target_role = v.get("role")
    target_index = v.get("index", 0)

    logger.info(f"Filling field '{target_name or target_locator}' with value '{target_value}' (frame: {target_frame})")
    fill_timeout = v.get("timeout", 10000)
    # `optional: true` — silently skip when the field is absent/unfillable. Counterpart of
    # `smart_click_optional` for inputs: needed for dialogs/overlays that may or may not appear
    # (e.g. the "Access code required" box a guest only sees when the seller enabled
    # Payment Restriction; see venue_map_fee_breakdown_guest_purchase.yaml).
    optional = v.get("optional", False)

    try:
        # Handle iframe context if frame is specified
        if target_frame:
            fl = page.frame_locator(target_frame)
            if target_locator:
                fl.locator(target_locator).first.fill(str(target_value), timeout=fill_timeout)
            elif target_role:
                fl.get_by_role(target_role, name=target_name, exact=v.get("exact", False)).fill(str(target_value), timeout=fill_timeout)
            else:
                fl.locator(f"textbox[name*='{target_name}']").first.fill(str(target_value), timeout=fill_timeout)
        elif target_locator:
            el = page.locator(target_locator).first
            el.fill(str(target_value), timeout=fill_timeout)
        elif "role" in v:
            page.get_by_role(v["role"], name=target_name, exact=v.get("exact", False)).nth(target_index).fill(str(target_value), timeout=fill_timeout)
        else:
            candidates = [
                page.get_by_label(cast(str, target_name), exact=False),
                page.get_by_placeholder(cast(str, target_name), exact=False),
                page.locator(f"input[name*='{target_name}'], textarea[name*='{target_name}']")
            ]
            target_id = v.get("index", 0)
            filled = False
            for c in candidates:
                if c.nth(target_id).is_visible(timeout=2000):    # Added timeout: original had no timeout, could wait 30s
                    c.nth(target_id).fill(str(target_value), timeout=fill_timeout)
                    filled = True
                    break
            if not filled:
                 page.locator(f"input[placeholder*='{target_name}'], input[aria-label*='{target_name}']").nth(target_id).fill(str(target_value), timeout=fill_timeout)
        page.wait_for_timeout(300)
    except Exception as e:
        if optional:
            logger.info(f"smart_fill (optional): '{target_name or target_locator}' not fillable, skipping ({e})")
            return None
        logger.error(f"Fill failed: {e}. AI Healing not fully implemented for Pure Vision fill yet.")
        raise

def _center_in_view(el):
    """Scroll an element to the middle of its scroll container.

    `scroll_into_view_if_needed()` only guarantees an intersection, so on forms with a
    sticky footer (e.g. the event edit form's Delete/Save bar) the element can end up
    sitting *behind* that footer: measured on testT5390, the start-date input landed at
    y=686 in a 720px-tall viewport, so `click(force=True)` hit the footer instead of the
    field, focus stayed on <body> and every keystroke was silently dropped. Centering
    first makes the click land on the element itself.
    """
    try:
        el.evaluate("e => e.scrollIntoView({block: 'center', inline: 'nearest'})")
        el.page.wait_for_timeout(200)
    except Exception as e:
        logger.debug(f"_center_in_view skipped: {e}")


def fill_numeric(page: Page, v: dict):
    target_locator = v.get("locator")
    target_locator = _resolve_locator(target_locator)
    target_value = str(v.get("value", ""))
    target_placeholder = v.get("placeholder", "Quantity")
    target_name = v.get("name") or v.get("label") or "Inventory"
    index = v.get("index", 0)
    logger.info(f"fill_numeric: forcing value '{target_value}'")

    if target_locator:
        el = page.locator(target_locator).nth(index)
    else:
        el = page.get_by_placeholder(target_placeholder, exact=False).nth(index)

    el.wait_for(state="visible", timeout=v.get("timeout", 10000))
    el.scroll_into_view_if_needed()
    _center_in_view(el)

    max_retries = 3
    for attempt in range(max_retries):
        el.click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(target_value, delay=100)
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        if str(el.input_value()) == target_value:
            return
    raise Exception(f"fill_numeric failed")

def fill_type(page: Page, v: dict):
    """Fill by real keyboard typing — for masked/segmented inputs (e.g. MUI DateField,
    placeholder 'MMMM DD, YYYY') where locator.fill() is swallowed by the input mask
    and silently degrades to today's date.

    Sequence (same as fill_numeric, but WITHOUT the equality verification, because
    masked fields normalize the display value, e.g. typed '12/30/2026' reads back
    as 'Dec 30, 2026').

    YAML:
        fill_type_date: { locator: "input[placeholder='MMMM DD, YYYY']", index: 0, value: '12/30/2026' }
        fill_type_time: { locator: "input[placeholder='hh:mm aa']", index: 0, value: '12:45 am' }
    """
    target_locator = v.get("locator")
    target_value = str(v.get("value", ""))
    index = v.get("index", 0)
    if target_locator:
        el = page.locator(target_locator).nth(index)
    else:
        el = page.get_by_placeholder(str(v.get("placeholder", "")), exact=False).nth(index)
    el.wait_for(state="visible", timeout=v.get("timeout", 10000))
    el.scroll_into_view_if_needed()
    _center_in_view(el)
    el.click(force=True)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(target_value, delay=v.get("delay", 80))
    if v.get("enter", True):
        page.keyboard.press("Enter")
    page.wait_for_timeout(300)

def smart_check(page: Page, v: dict):
    target_name = v.get("name") or v.get("text") or v.get("label")
    target_locator = v.get("locator")
    target_locator = _resolve_locator(target_locator)
    checked = v.get("checked", True)
    target_role = v.get("role")
    target_index = v.get("index", 0)
    no_modal_scope = v.get("no_modal_scope", False)
    optional = v.get("optional", False)
    container = v.get("container")
    logger.info(f"Checking '{target_name or target_locator}' to {checked}"
                + (f" (scoped to container '{container}')" if container else ""))

    def _get_el(root):
        if container:
            # Scope the search to the innermost element containing the container text,
            # mirroring click_container_button's container resolution.
            root = root.locator("div", has_text=container).last
        if target_locator:
            return root.locator(target_locator).nth(target_index)
        elif target_role:
            return root.get_by_role(target_role, name=target_name).nth(target_index)
        else:
            return root.get_by_label(target_name).nth(target_index)

    def _mui_fallback(el):
        """Force-click the parent wrapper for React controlled inputs."""
        logger.warning("Falling back to MUI force-click on parent wrapper...")
        is_currently_checked = el.evaluate("node => node.checked")
        if bool(is_currently_checked) != bool(checked):
            el.locator("..").click(force=True)
            page.wait_for_timeout(500)

    # --- Strategy 1: Page-level first (most common case, no modal restriction) ---
    try:
        el = _get_el(page)
        el.set_checked(checked, timeout=3000)
        logger.info(f"Checked '{target_name or target_locator}' via page-level.")
        return
    except Exception as e:
        if "Clicking the checkbox did not change its state" in str(e) or "intercepts pointer events" in str(e) or "Timeout" in type(e).__name__:
            try:
                _mui_fallback(_get_el(page))
                return
            except Exception as fe:
                logger.warning(f"MUI fallback also failed: {fe}")
        # On Timeout or Strict-mode: fall through to modal-scoped attempt
        logger.debug(f"Page-level check failed ({type(e).__name__}), trying modal scope...")

    # --- Strategy 2: Modal-scoped (only when page-level times out & not suppressed) ---
    if no_modal_scope:
        if optional:
            logger.info(f"Optional check: element '{target_name or target_locator}' not found (no_modal_scope=True), skipping.")
            return
        logger.error(f"Check failed at page-level and no_modal_scope=True, giving up.")
        raise Exception(f"smart_check: element '{target_name or target_locator}' not found on page.")

    try:
        modals = page.locator("[role='dialog'], [role='alertdialog'], .MuiDialog-root, .MuiModal-root").all()
        active_modal = next((m for m in reversed(modals) if m.is_visible()), None)
        if active_modal:
            logger.debug("Trying within active modal scope...")
            el = _get_el(active_modal)
            el.set_checked(checked, timeout=5000)
            logger.info(f"Checked '{target_name or target_locator}' via modal scope.")
            return
        else:
            # No modal found and page-level also failed
            if optional:
                logger.info(f"Optional check: element '{target_name or target_locator}' not found on page or modal, skipping.")
                return
    except Exception as e2:
        if "Clicking the checkbox did not change its state" in str(e2) or "intercepts pointer events" in str(e2) or "Timeout" in type(e2).__name__:
            try:
                _mui_fallback(_get_el(active_modal))
                return
            except Exception as fe2:
                logger.error(f"MUI modal fallback also failed: {fe2}")
        if optional:
            logger.info(f"Optional check: modal-scoped attempt also failed for '{target_name or target_locator}', skipping. ({e2})")
            return
        logger.error(f"Modal-scoped check also failed: {e2}")
        raise


def _visible_overlay_count(page):
    sels = "[role='dialog'], [role='alertdialog'], .MuiDialog-root, .MuiModal-root, .MuiDrawer-root"
    try:
        return sum(1 for e in page.locator(sels).all() if e.is_visible())
    except Exception:
        return 0


def _active_container(page):
    """Return the topmost visible modal/drawer, or the page if none is visible."""
    sels = "[role='dialog'], [role='alertdialog'], .MuiDialog-root, .MuiModal-root, .MuiDrawer-root"
    try:
        visible = [e for e in page.locator(sels).all() if e.is_visible()]
        return visible[-1] if visible else page
    except Exception:
        return page


def _dismiss_top_overlay(page):
    """Dismiss the topmost visible modal/drawer by its Cancel/Close/Got it button, else Escape."""
    sels = "[role='dialog'], [role='alertdialog'], .MuiDialog-root, .MuiModal-root, .MuiDrawer-root"
    try:
        visible = [e for e in page.locator(sels).all() if e.is_visible()]
        top = visible[-1] if visible else None
        if not top:
            return
        for b in top.locator("button").all():
            try:
                txt = (b.inner_text() or "").strip().lower()
            except Exception:
                continue
            if txt in ("cancel", "close", "got it", "done", "x"):
                b.click(force=True, timeout=2000)
                return
        page.keyboard.press("Escape")
    except Exception as e:
        logger.warning(f"uncheck_all: could not dismiss overlay ({e})")


def uncheck_all(page: Page, v: dict):
    """
    Reusable reset helper: uncheck EVERY visible checkbox/switch inside a scope.

    Default scope = the topmost visible modal/drawer (e.g. the Event settings drawer);
    pass `scope` to anchor to a specific container locator. Pass `exclude` (list of input
    `name` values) to skip known dialog-driven toggles whose "off" state needs a confirm
    dialog (e.g. isTaxEnabled, whose on/off is better driven by the calling flow).

    Only clicks boxes that are currently checked, so plain toggles are safely reset.
    A real click fires React onChange; a MUI parent force-click is used as fallback. If a
    toggle opens a dialog/drawer as a side effect, it is auto-dismissed so the panel stays
    clean for the next step. Returns the number of boxes clicked.

    Params:
        scope (str, optional): container locator to search within.
        exclude (list, optional): input `name` values to skip.
        optional (bool): if True, no-op (return 0) when no checkboxes are found.
    """
    scope_locator = v.get("scope")
    exclude = set(v.get("exclude") or [])
    optional = v.get("optional", False)

    container = page.locator(_resolve_locator(scope_locator)) if scope_locator else _active_container(page)
    try:
        boxes = container.locator("input[type='checkbox']").all()
    except Exception as e:
        if optional:
            logger.info(f"uncheck_all: no checkboxes found (optional), skipping. ({e})")
            return 0
        raise

    unchecked = 0
    for box in boxes:
        try:
            if not box.is_visible():
                continue
            name = box.get_attribute("name") or ""
            if name in exclude:
                continue
            if not box.is_checked():
                continue
            before = _visible_overlay_count(page)
            try:
                box.click(force=True, timeout=2000)
            except Exception:
                box.locator("xpath=..").click(force=True, timeout=2000)
            # dismiss any dialog/drawer the toggle click may have opened (rate/address etc.)
            after = _visible_overlay_count(page)
            for _ in range(max(0, after - before)):
                _dismiss_top_overlay(page)
            unchecked += 1
        except Exception as e:
            logger.warning(f"uncheck_all: skipped a checkbox (name={name or '?'}) ({e})")
    logger.info(f"uncheck_all: clicked {unchecked} checkbox(es) to uncheck "
                f"(scope={scope_locator or 'active modal/drawer'}, exclude={exclude})")
    return unchecked


def smart_add_cookies(page: Page, v: dict):
    """Inject cookies from a Playwright storage-state file into the current context.
    Caller is responsible for navigating to the partner URL after this call.
    """
    import json
    state_path = v.get("storage_state") or os.path.join(
        BASE_DIR, "test_case", "UI", "cookie_release.json"
    )
    if not os.path.exists(state_path):
        raise FileNotFoundError(f"Cookie storage state file not found: {state_path}")
    state = json.load(open(state_path, encoding="utf-8"))
    cookies = state.get("cookies", [])
    if not cookies:
        raise ValueError(f"No cookies found in storage state: {state_path}")
    page.context.add_cookies(cookies)
    logger.info(f"Added {len(cookies)} partner cookies from {state_path}")

def clear_cookies(page: Page, v: dict):
    """Clear all cookies/storage from the current context to switch to guest.
    Optionally inject minimal non-auth guest cookies (vanity_url, visitor_id,
    consent/analytics) so Pear SPA tenant routing still works after the switch.
    Also clears localStorage/sessionStorage because Pear keeps auth tokens there too.
    """
    import json
    page.context.clear_cookies()
    logger.info("Cleared all cookies to switch back to guest context")

    # Pear stores partner auth tokens in localStorage/sessionStorage as well as cookies.
    # Navigating to about:blank first lets us clear storage for all origins safely.
    try:
        page.goto("about:blank", wait_until="domcontentloaded", timeout=5000)
        page.evaluate("() => { try { localStorage.clear(); } catch(e) {} try { sessionStorage.clear(); } catch(e) {} }")
        logger.info("Cleared localStorage and sessionStorage for guest switch")
    except Exception as e:
        logger.warning(f"Clearing storage for guest switch failed: {e}")

    if v.get("inject_guest"):
        state_path = v.get("storage_state") or os.path.join(
            BASE_DIR, "test_case", "UI", "cookie_release.json"
        )
        try:
            state = json.load(open(state_path, encoding="utf-8"))
            non_auth_names = {
                # tenant routing — required so SPA recognizes /autotestshop
                "release_katana_vanity_url",
                "staging_katana_vanity_url",
                "prod_katana_vanity_url",
                # first-party visitor id
                "release_katana_visitor_id",
                "staging_katana_visitor_id",
                "prod_katana_visitor_id",
                # GDPR consent state — harmless
                "katana_cookie_consent",
                # analytics — harmless, NOT identifying
                "_ga",
                "_ga_RV17GL444M",
                "_rdt_uuid",
            }
            guest_cookies = [
                c for c in state.get("cookies", [])
                if c.get("name") in non_auth_names
            ]
            if guest_cookies:
                page.context.add_cookies(guest_cookies)
                logger.info(
                    f"INJECT_GUEST: added {len(guest_cookies)} non-auth cookies "
                    f"from {state_path} (vanity_url + visitor_id)"
                )
            else:
                logger.warning("INJECT_GUEST: no non-auth cookies found in storage state")
        except Exception as e:
            logger.warning(f"INJECT_GUEST failed: {e}")

def smart_upload(page: Page, v: dict):
    if "file_path" in v:
        file_path = v.get("file_path")
        if isinstance(file_path, list):
            file_path = [p if os.path.isabs(p) else os.path.join(BASE_DIR, p) for p in file_path]
        else:
            if not os.path.isabs(file_path):
                file_path = os.path.join(BASE_DIR, file_path)
        target_index = v.get("index", 0)
        with page.expect_file_chooser(timeout=5000) as fc_info:
            if "locator" in v:
                page.locator(v["locator"]).nth(target_index).click()
            else:
                page.get_by_text(cast(str, v.get("text")), exact=True).nth(target_index).click()
        fc = fc_info.value
        fc.set_files(cast("list[str]", file_path if isinstance(file_path, list) else [file_path]))

def _smart_click_core(page: Page, v: dict):
    """
    Core click logic (without Page-level Search and AI self-healing).
    Shared by smart_click and smart_click_scan.

    When quick=True, skips crash check and backdrop wait — use for fast clicks on confirmed stable pages.
    """
    quick = v.get("quick", False)

    if not quick:
        # Optimization: add 5s timeout to is_visible (original had no timeout, could wait 30s)
        try:
            if page.get_by_text("Something went wrong!", exact=True).is_visible(timeout=5000):
                logger.error("Application Crashed!")
                raise Exception("Application Crashed")
        except: pass

        # Wait for loading overlays/backdrops to disappear before clicking anything
        # Optimization: timeout reduced from 8s to 2s; use detached state (non-blocking)
        try:
            backdrop = page.locator(".MuiBackdrop-root, [class*='Backdrop'], .loading-overlay").first
            backdrop.wait_for(state="detached", timeout=2000)  # 2s timeout to avoid stalling
        except: pass

    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_locator = _resolve_locator(target_locator)
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    target_index = v.get("index", 0)
    target_test_id = v.get("test_id")
    force = v.get("force", False)
    optional = v.get("optional", False)
    skip_if_disabled = v.get("skip_if_disabled", False)
    skip_if_checked = v.get("skip_if_checked", False)
    # position: 在命中元素内部按偏移点击（Playwright 的 position 语义，{x, y}）。
    # 用于「必须点到元素自身、而不是盖在它上面的子元素」的场景 —— 例如 RTE 里的
    # CTA 装饰器：内部 button 铺满整块（四周只有圆角留白），点按钮中心会触发按钮
    # 自身行为、装饰器不会被选中，随后带 Edit/Delete 的工具条就不出现；
    # 点装饰器圆角处的留白才能选中它。默认 None = 维持原点中心点击，行为不变。
    target_position = v.get("position")

    # Template {{var}} placeholders from the workflow context (populated by execute_js save_as),
    # so a click can target a value discovered earlier, e.g. name: "{{ticket_axs}}".
    # Falls back to the cross-case global store (see global_state.py).
    _ctx = _merged_context_vars(page)
    if _ctx:
        def _fill(s):
            if not isinstance(s, str):
                return s
            for _k, _val in _ctx.items():
                if _k:
                    s = s.replace("{{%s}}" % _k, str(_val))
            return s
        target_name = _fill(target_name)
        target_locator = _fill(target_locator)
        target_role = _fill(target_role)

    if not target_name and not target_locator and not target_role and not target_test_id:
        return

    # skip_if_checked
    if skip_if_checked and target_locator:
        try:
            el = page.locator(target_locator).nth(target_index)
            is_checked = el.is_checked(timeout=3000)
            if is_checked:
                logger.info(f"skip_if_checked: '{target_locator}' is already ON, skipping toggle click.")
                return
        except Exception as e:
            logger.debug(f"skip_if_checked check error (proceeding normally): {e}")

    logger.info(f"Click started for target: {target_name or target_locator or target_role}")

    # skip_if_disabled
    if skip_if_disabled:
        try:
            if target_role and target_name:
                candidate = page.get_by_role(target_role, name=target_name).nth(target_index)
            elif target_locator:
                candidate = page.locator(target_locator).nth(target_index)
            else:
                candidate = page.get_by_text(cast(str, target_name), exact=target_exact).nth(target_index)
            if candidate.is_disabled(timeout=3000):
                logger.info(f"skip_if_disabled: '{target_name or target_locator}' is disabled, skipping step.")
                return
        except Exception as e:
            logger.debug(f"skip_if_disabled check error (proceeding normally): {e}")

    # Scoping: find visible modals
    # Use is_visible() without timeout to avoid blocking on hidden modals
    raw_modals = page.locator("div[role='dialog'], .MuiDialog-root, .MuiModal-root").all()
    visible_modals = []
    for m in raw_modals[:10]:
        try:
            if m.is_visible():
                visible_modals.append(m)
        except: pass
    active_modal = visible_modals[-1] if visible_modals else None

    # Save / Publish: try Playwright fast locate first, fall back to JS if failed
    if target_name in ("Save", "Publish"):
        playwright_failed_for_special = False

        if active_modal:
            try:
                el = active_modal.get_by_role("button", name=target_name).nth(target_index)
                el.scroll_into_view_if_needed(timeout=3000)
                page.wait_for_timeout(300)
                el.click(force=True)
                logger.info(f"smart_click: '{target_name}' clicked via Playwright (modal-scoped)")
                page.wait_for_timeout(1000)
                return
            except Exception:
                playwright_failed_for_special = True

        if not playwright_failed_for_special and not active_modal:
            try:
                el = page.get_by_role("button", name=target_name).nth(target_index)
                el.scroll_into_view_if_needed(timeout=3000)
                page.wait_for_timeout(300)
                el.click(force=True)
                logger.info(f"smart_click: '{target_name}' clicked via Playwright (page-level)")
                page.wait_for_timeout(1000)
                return
            except Exception:
                playwright_failed_for_special = True

        js_click_code = """
            () => {
                const dialogs = Array.from(document.querySelectorAll('[role="dialog"], .MuiDialog-root, [class*="MuiDialog"]'));
                let targetContainer = null;
                for (const d of dialogs) {
                    const style = window.getComputedStyle(d);
                    if (style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0) {
                        targetContainer = d;
                    }
                }
                const searchIn = targetContainer || document.body;
                const btns = Array.from(searchIn.querySelectorAll('button'));
                for (const btn of btns) {
                    if (btn.textContent.trim() === arguments[0] && !btn.disabled && btn.offsetParent !== null) {
                        btn.click(); return 'ok';
                    }
                }
                const allBtns = Array.from(document.querySelectorAll('button'));
                for (const btn of allBtns) {
                    if (btn.textContent.trim() === arguments[0] && !btn.disabled && btn.offsetParent !== null) {
                        btn.click(); return 'page';
                    }
                }
                return null;
            }
        """
        try:
            clicked = page.evaluate(js_click_code, target_name)
            if clicked:
                logger.info(f"{target_name} clicked via JS fallback ({clicked})")
                page.wait_for_timeout(1000)
                return
        except Exception as e:
            logger.debug(f"JS {target_name} fallback error: {e}")

    # ---- General location strategies 1-4 ----
    # Restore standard scoping: if there is an active modal, restrict all searches to it by default.
    root = active_modal if active_modal else page

    # 1. Test ID
    if target_test_id:
        try:
            el = root.get_by_test_id(target_test_id).nth(target_index)
            if el.is_visible(timeout=5000):
                el.click(force=force, position=target_position)
                return
        except: pass

    # 2. Standard locator
    # Optimization: call click() directly without is_visible first (Playwright click has built-in checks)
    if target_locator:
        try:
            if target_locator.startswith("/") or target_locator.startswith("xpath="):
                xpath_locator = target_locator if target_locator.startswith("xpath=") else f"xpath={target_locator}"
                el = page.locator(xpath_locator).nth(target_index)
            else:
                # Fix: custom CSS locators fall back to global page.locator().
                # These locators typically start from body/html, scoping them under active_modal
                # causes nesting errors (e.g. finding a dialog inside a dialog).
                el = page.locator(target_locator).nth(target_index)

            if target_name:
                el = el.get_by_text(target_name, exact=target_exact)
            el.click(force=force, timeout=5000, position=target_position)  # Click directly, no is_visible check first
            logger.info(f"Clicked via locator: {target_name or target_locator}")
            return
        except Exception as e:
            if optional:
                logger.info(f"Optional click: locator attempt failed for index {target_index}, skipping. ({e})")
                return
            logger.debug(f"Locator attempt failed: {e}")

    # 3. Aria-label fallback (buttons rarely have aria-label, very short timeout to avoid stalling)
    if target_name:
        try:
            el = root.locator(f'button[aria-label="{target_name}"], [aria-label*="{target_name}"]').nth(target_index)
            el.click(force=force, timeout=3000, position=target_position)  # Click directly
            logger.info(f"Clicked via aria-label fallback: {target_name}")
            return
        except: pass

    # 4. Role / text fallback
    # Optimization: removed scroll_into_view_if_needed (blocks and wastes time)
    # - Playwright click() has built-in scrolling, no explicit scroll needed
    # - Click directly, fall back to force on failure
    try:
        if target_role:
            el = root.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
        elif target_name:
            el = root.get_by_text(target_name, exact=target_exact).nth(target_index)
        if el:
            # Try normal click first (Playwright click has built-in scroll + visibility check)
            try:
                el.click(timeout=5000, position=target_position)  # 5s timeout, no force
                logger.info(f"Clicked '{target_name}'")
                if target_role == 'option':
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
                return
            except Exception as click_e:
                logger.debug(f"Normal click failed ({click_e}), trying force...")

            # Click failed, try force (bypass all checks)
            try:
                el.click(force=True, timeout=3000, position=target_position)
                logger.info(f"Force-clicked '{target_name}'")
                if target_role == 'option':
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
                return
            except Exception as force_e:
                logger.debug(f"Force click failed, trying JS: {force_e}")
                try:
                    page.evaluate("(el) => el.click()", el.element_handle())
                    logger.info(f"JS-clicked '{target_name}'")
                    return
                except Exception as js_e:
                    logger.debug(f"JS click also failed: {js_e}")
                    raise
    except Exception as e:
            logger.debug(f"Standard click failed: {e}")

    # 5. Page-wide retry for portal-rendered floating layers (menuitem / option).
    #    These items live in menus appended to <body>, so they are NOT reliably "inside" the
    #    newest visible dialog: active_modal = visible_modals[-1], and when several dialogs are
    #    visible it can resolve to a dialog that does NOT contain the target -> every strategy
    #    above fails even though the item is plainly on the page.
    #    CI evidence (2026-09-20, same run / same code): the Form click in T4859 passed while the
    #    **same step** in T4860 got trapped in dialog#2 with "element not found" - pure DOM-order
    #    jitter. This retry only fires after every earlier strategy has failed, so it is
    #    **purely additive** and has zero impact on currently passing cases.
    if root is not page and target_role in ("menuitem", "option") and target_name:
        try:
            _el = page.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
            try:
                _el.click(timeout=5000, position=target_position)
            except Exception:
                _el.click(force=True, timeout=3000, position=target_position)
            logger.info(f"Clicked '{target_name}' via page-wide retry ({target_role} not in active modal scope)")
            if target_role == "option":
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
            return
        except Exception as e:
            logger.debug(f"Page-wide retry failed for {target_role} '{target_name}': {e}")

    if optional:
        logger.info(f"Optional click: element '{target_name or target_locator}' not found after all standard strategies, skipping.")
        return
    raise Exception(f"smart_click: element not found: {target_name or target_locator}")


def smart_click(page: Page, v: dict):
    """
    Fast click — uses traditional Playwright location strategies only.

    Parameters:
        fallback_scan: bool, default False.
            - False: throw exception directly on locate failure, no Page-level Search triggered.
                      **Suitable for 95% of normal test cases, best performance.**
            - True:  trigger Page-level Search + AI self-healing on locate failure.
                      **For nested dialogs, multi-layer overlays, and hard-to-locate elements.**

    YAML usage examples:
        # Normal click (fast)
        click_save: { name: 'Save' }

        # Difficult scenario (with Page-level Search, slower but more stable)
        click_save: { name: 'Save', fallback_scan: true }

        # Difficult scenario (explicit name, clearer semantics)
        R_click_save_hard: { name: 'Save', fallback_scan: true }
    """
    try:
        _smart_click_core(page, v)
        return  # Core locate succeeded, return immediately
    except Exception as primary_error:
        if not v.get("fallback_scan", False):
            # fallback_scan=False (default): locate failed → raise immediately, no extra steps
            logger.debug(f"smart_click (fast): {primary_error}")
            raise primary_error

        # fallback_scan=True: enter Page-level Search + AI fallback chain
        _smart_click_with_fallback(page, v, primary_error)


def _smart_click_with_fallback(page: Page, v, primary_error):
    """
    Full fallback click — includes Page-level Search and AI self-healing.
    Only called by smart_click when fallback_scan=True.
    """
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    optional = v.get("optional", False)

    logger.info(f"smart_click (fallback_scan=True): Page-level Search triggered for '{target_name or target_role}'")

    # ---- 5. Page-level Search: enumerate all buttons on the page ----
    # Optimization: is_visible timeout reduced from 2000ms to 500ms to reduce wait time
    if target_role == 'button' or target_name in {"Get Tickets", "Selling", "Customize products", "Batch set commission rates"}:
        try:
            if target_name:
                if target_role:
                    all_matches = page.get_by_role(target_role, name=target_name, exact=target_exact).all()
                else:
                    all_matches = page.get_by_text(target_name, exact=target_exact).all()
                logger.debug(f"Page-level search for '{target_name}': {len(all_matches)} total elements")
                for idx, candidate in enumerate(all_matches):
                    try:
                        # Optimization: no timeout, fast visibility check (avoids 500ms wait per hidden element)
                        is_vis = candidate.is_visible()
                        if is_vis:
                            logger.info(f"Page-level found '{target_name}' #{idx}, clicking with force")
                            candidate.click(force=True)
                            return
                    except Exception as inner_e:
                        logger.debug(f"  candidate #{idx} failed: {inner_e}")
                        try:
                            page.evaluate("(el) => el.click()", candidate.element_handle())
                            logger.info(f"Page-level JS-click '{target_name}' #{idx}")
                            return
                        except: pass
        except Exception as e:
            logger.debug(f"Page-level fallback error: {e}")

    # ---- 6. AI Self-Healing Fallback ----
    if optional:
        logger.info(f"Optional click: element '{target_name}' not found after all attempts, skipping.")
        return

    # Global Kill-switch check
    if v.get("disable_ai", False) or os.environ.get("AI_DISABLED") == "True":
        logger.warning(f"AI Healing is DISABLED for '{target_name}'. Raising original error.")
        if target_role == 'button' or target_name == 'Add' or target_name == 'Add new':
            try:
                logger.debug("Traditional/Modal search failed. Trying global search for last visible button...")
                all_btns = page.get_by_role("button", name=target_name, exact=target_exact).all()
                for btn in reversed(all_btns):
                    try:
                        if btn.is_visible(timeout=1000):           # Optimization: add 1s timeout (previously no timeout, would wait 30s)
                            try:
                                btn.scroll_into_view_if_needed(timeout=3000)
                            except: pass
                            btn.click(force=True)
                            logger.info(f"Global fallback SUCCESS for '{target_name}'")
                            return
                        else:
                            try:
                                page.evaluate("(el) => el.click()", btn.element_handle())
                                logger.info(f"Global fallback SUCCESS (JS) for '{target_name}'")
                                return
                            except: pass
                    except: pass
            except: pass
        raise Exception(f"Element not found: {target_name}")

    if ai_vision is None:
        logger.warning("AI vision disabled. Skipping AI healing (set ENABLE_AI_VISION=1 to enable).")
        raise Exception(f"Element not found (AI healing disabled): {target_name}")

    logger.error("Traditional methods failed. Triggering AI Pure Vision Healing...")
    try:
        page_history = getattr(page, "_execution_history", [])
        instruction = f"Click the element: '{target_name}'"
        safe_name = re.sub(r'[^\w\-]', '_', str(target_name or 'target'))[:30]
        screenshot_path = f"ai_vision_{safe_name}.png"
        page.screenshot(path=screenshot_path)

        res = ai_vision.find_element_pure_vision(screenshot_path, instruction, page_history)

        if res.get("found") and res.get("coordinates"):
            coords = res["coordinates"]
            x, y = coords["x"], coords["y"]
            initial_url = page.url

            def perform_click(cx, cy, label):
                logger.debug(f"Performing {label} at {cx}, {cy}")
                page.mouse.click(cx, cy)
                page.wait_for_timeout(1500)

            perform_click(x, y, "AI Primary Click")

            # --- SELF-PATCHING LOGIC ---
            suggested = res.get("suggested_locator")
            yaml_path = getattr(page, "_yaml_path", None)
            case_id = getattr(page, "_test_caseno", None)

            if suggested and yaml_path and case_id:
                try:
                    from ..utils.yaml_patcher import patch_yaml_step
                    patch_yaml_step(yaml_path, case_id, target_name, suggested)
                except Exception as py_ex:
                    logger.warning(f"Self-Patching failed: {py_ex}")

            if res.get("suggested_action") == "GOAL_CLICK" and page.url == initial_url:
                logger.warning("Starting Jitter Retries...")
                for jx, jy in [(2,2), (-2,-2), (3,0), (0,3)]:
                    if page.url != initial_url: break
                    perform_click(x + jx, y + jy, "Jitter")

            if res.get("suggested_action") == "RECOVERY_CLICK" or page.url != initial_url:
                if v.get("_retry_ai", 0) < 2:
                    v["_retry_ai"] = v.get("_retry_ai", 0) + 1
                    return smart_click(page, v)
            return
        else:
            logger.error(f"AI SOM could not locate the element. Logic ends here.")
    except Exception as ai_err:
        logger.error(f"AI Healing Error: {ai_err}")

    if v.get("_retry_ai", 0) > 0:
        return
    raise Exception(f"Failed to click '{target_name}' after all attempts including AI.")

def click_modal_close(page: Page, v: dict):
    logger.info("Attempting to close modal...")
    try:
        close_btn = page.locator("div[role='dialog'] button[aria-label='close'], .MuiDialog-root button.close").first
        if close_btn.is_visible(timeout=3000):            # Added timeout: previously no timeout could wait 30s
            close_btn.click()
        else:
            page.keyboard.press("Escape")
    except Exception as e:
        logger.warning(f"Failed to close modal: {e}")

def verify_text_visible(page: Page, v: dict):
    raw_text = v.get("text")
    timeout = v.get("timeout", 10000)
    not_visible = v.get("assert_not_visible", False)

    # --- {{var}} backfill (workflow context + cross-case globals) ---
    # Expected texts may reference variables saved by earlier steps (e.g.
    # "${{retails_price_venue_map}}"). Resolve them natively so dynamic-text checks
    # never need execute_js. No-op when the string contains no placeholder.
    # `text` may ALSO be a LIST of acceptable copies — the assertion passes when ANY of
    # them is visible (mirrors the list support of `verify_row_value`). Handy when one
    # assertion has more than one valid wording across UI variants, e.g. the order
    # confirmation heading renders either "Thank you for your payment." or
    # "Your order is confirmed" depending on the build.
    text_options = None
    if isinstance(raw_text, (list, tuple)):
        text_options = [_fill_placeholders(str(t), page) for t in raw_text]
        text = None
    else:
        text = _fill_placeholders(raw_text, page)
    v = dict(v)
    if v.get("locator"):
        v["locator"] = _fill_placeholders(_resolve_locator(v["locator"]), page)
    if isinstance(v.get("scope"), dict):
        _scope = dict(v["scope"])
        if _scope.get("locator"):
            _scope["locator"] = _fill_placeholders(_resolve_locator(_scope["locator"]), page)
        if _scope.get("text"):
            _scope["text"] = _fill_placeholders(_scope["text"], page)
        v["scope"] = _scope

    # --- Optional scope container ---
    # When `scope` is provided, the target text must live INSIDE the scope container
    # instead of anywhere on the page. Supported scope shapes:
    #   scope: { text: "container text" }    -> container found by accessible text
    #   scope: { locator: "css=xpath" }      -> container found by selector
    # When `scope` is absent, behavior is byte-identical to before this fix.
    # (Fixes the silent global-search bug discovered 2026-09-02 in T1742.)
    scope_locator = None
    scope_label = None
    scope_cfg = v.get("scope")
    if scope_cfg:
        try:
            if scope_cfg.get("locator"):
                scope_locator = page.locator(scope_cfg["locator"]).first
                scope_label = scope_cfg["locator"]
            elif scope_cfg.get("text"):
                scope_locator = page.get_by_text(
                    scope_cfg["text"], exact=scope_cfg.get("exact", False)
                ).first
                scope_label = scope_cfg["text"]
            else:
                raise AssertionError(
                    f"verify: invalid scope {scope_cfg}; need 'text' or 'locator'"
                )
            scope_locator.wait_for(state="visible", timeout=timeout)
        except AssertionError:
            raise
        except Exception:
            page.screenshot(path=f"fail_scope_{str(scope_label)[:10]}.png")
            raise AssertionError(f"Scope container '{scope_label}' not found.")

    search_root = scope_locator if scope_locator is not None else page

    if not_visible:
        if text_options:
            # "none of the alternatives may be visible"
            for t in text_options:
                try:
                    search_root.get_by_text(t, exact=v.get("exact", False)).first.wait_for(
                        state="hidden", timeout=timeout
                    )
                except Exception:
                    page.screenshot(path=f"fail_not_visible_{t[:10]}.png")
                    raise AssertionError(f"Text '{t}' is visible but should not be.")
            logger.info(f"Confirmed none of the alternative texts is visible: {text_options}")
            return
        logger.info(f"Verifying text is NOT visible: {text or v.get('locator')}")
        if v.get("locator"):
            # locator + scope: resolve the locator INSIDE the scope container.
            el = (
                scope_locator.locator(v["locator"]).first
                if scope_locator is not None
                else page.locator(v["locator"]).first
            )
            if text:
                el = el.get_by_text(text, exact=v.get("exact", False))
        elif text:
            # (2026-10-15 fix, T5649) .filter(visible=True): the DOM-first text match can be a
            # HIDDEN duplicate (sticky buy-bar / SSR copy) — without the filter, a hidden
            # .first makes assert_not_visible false-PASS while another copy is still visible.
            el = search_root.get_by_text(text, exact=v.get("exact", False)).filter(visible=True).first
        else:
            raise AssertionError("verify: no text or locator provided")
        try:
            el.wait_for(state="hidden", timeout=timeout)
            logger.info(f"Confirmed element is not visible: {text or v.get('locator')}")
        except:
            if el.is_visible(timeout=3000):                   # Added timeout: previously no timeout could wait 30s
                page.screenshot(path=f"fail_not_visible_{str(text or v.get('locator'))[:10]}.png")
                raise AssertionError(f"Element '{text or v.get('locator')}' is still visible but should not be.")
        return

    if text_options:
        # Any-of match with ONE shared deadline (so 2 alternatives do not double the wait).
        import time as _time
        deadline = _time.time() + timeout / 1000.0
        while True:
            for t in text_options:
                try:
                    if search_root.get_by_text(t, exact=v.get("exact", False)).first.is_visible():
                        logger.info(f"Text '{t}' is visible (one of {len(text_options)} accepted copies).")
                        return
                except Exception:
                    pass
            if _time.time() >= deadline:
                break
            page.wait_for_timeout(400)
        page.screenshot(path=f"fail_verify_{str(text_options[0])[:10]}.png")
        raise AssertionError(
            f"None of the accepted texts is visible within {timeout}ms: {text_options}"
        )

    logger.info(f"Verifying text visibility: {text}")
    try:
        # (2026-10-15 fix, T5649) Do NOT blindly pick .first: on mobile layouts the DOM-first
        # text match can be a HIDDEN duplicate (e.g. sticky buy-bar / SSR copy), which made
        # verify_text_visible time out ("Text not found") even though a visible copy existed
        # (T5649 guest price "$114.90"). filter(visible=True) keeps .first semantics but only
        # among VISIBLE matches. Requires playwright >= 1.51 (local 1.60, CI pin 1.58 — both OK).
        search_root.get_by_text(cast(str, text), exact=v.get("exact", False)).filter(visible=True).first.wait_for(state="visible", timeout=timeout)
        logger.info(f"Text '{text}' is visible.")
    except Exception as e:
        page.screenshot(path=f"fail_verify_{str(text)[:10]}.png")
        raise AssertionError(f"Text '{text}' not found.")

def verify_text_hidden(page: Page, v: dict):
    text = v.get("text")
    timeout = v.get("timeout", 10000)
    logger.info(f"Verifying text hidden: {text}")
    try:
        element = page.get_by_text(cast(str, text), exact=v.get("exact", False)).first
        
        # Evaluate visibility with JS. MUI uses height=0 and overflow=hidden for collapse.
        # Playwright's native hidden state sometimes thinks an element is visible if its own bounding rect is > 0, 
        # even if an ancestor is 0-height and hidden overflow.
        is_hidden_js = """(el) => {
            if (!el) return true;
            let current = el;
            while (current && current !== document.body) {
                const style = window.getComputedStyle(current);
                if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) < 0.05) return true;
                
                // Deal with MUI and standard accessibility clipping techniques
                if (style.clip === 'rect(0px, 0px, 0px, 0px)') return true;
                if (style.clipPath && style.clipPath !== 'none' && style.clipPath.includes('(0')) return true;
                
                const rect = current.getBoundingClientRect();
                // If a container essentially has no dimensions and hides its overflow...
                if ((rect.height <= 2 || rect.width <= 2) && 
                    (style.overflow === 'hidden' || style.overflowY === 'hidden' || style.overflowX === 'hidden')) {
                    return true;
                }
                current = current.parentElement;
            }
            const rect = el.getBoundingClientRect();
            // If the element itself is technically rendered but scaled to 0 or squashed
            if (rect.width <= 2 || rect.height <= 2) return true;
            return false;
        }"""
        
        import time
        start_time = time.time()
        while time.time() - start_time < timeout / 1000.0:
            # First check native playwright hidden
            if element.is_hidden():
                logger.info(f"Text '{text}' is hidden natively.")
                return
            # Then check our robust visual JS check
            if element.evaluate(is_hidden_js):
                logger.info(f"Text '{text}' is successfully hidden (visually via JS).")
                return
            time.sleep(0.5)
            
        raise AssertionError(f"Timeout {timeout}ms exceeded. Text '{text}' remained visible.")
    except Exception as e:
        page.screenshot(path=f"fail_verify_hidden_{str(text)[:10]}.png")
        raise AssertionError(f"Text '{text}' is still visible! Exception: {str(e)}")

def smart_wait(page: Page, v: dict):
    """
    Wait for an element to appear (become visible).
    Supports: role, name, locator, text.
    Usage in YAML:
        wait_customize_back: { role: 'button', name: 'Customize products', timeout: 15000, disable_ai: true }
    """
    timeout = v.get("timeout", 5000)
    role = v.get("role")
    name = v.get("name")
    locator = v.get("locator")
    text = v.get("text")
    logger.info(f"smart_wait: waiting for element (role={role}, name={name}, locator={locator}, text={text}, timeout={timeout})")

    try:
        if locator:
            el = page.locator(locator)
        elif role and name:
            el = page.get_by_role(role, name=name)
        elif role:
            el = page.get_by_role(role)
        elif text:
            el = page.get_by_text(text, exact=False)
        else:
            logger.warning(f"smart_wait: no locator/role/name/text specified, skipping")
            return

        el.first.wait_for(state="visible", timeout=timeout)
        logger.info(f"smart_wait: element appeared successfully")
    except Exception as e:
        logger.warning(f"smart_wait: element did not appear within {timeout}ms: {e}")
        try:
            page.screenshot(path=f"fail_wait_{str(v)[:30]}.png")
        except:
            pass

def reload_page(page: Page, v: dict):
    page.reload()
    page.wait_for_timeout(v.get("sleep_after", 3000))

def page_scroll(page: Page, v: dict):
    """
    Page scroll that auto-detects the real scrollable container.
    Uses multiple strategies in order:
    1. JS scroll on detected scrollable container
    2. mouse.wheel()
    3. keyboard PageDown
    4. keyboard ArrowDown
    """
    y = v.get("y", 500)
    delay = v.get("delay", 1000)
    steps = v.get("steps", 1)

    logger.info(f"page_scroll: scrolling by {y}px x{steps} steps")

    viewport = page.viewport_size or {"width": 1280, "height": 720}
    center_x = viewport["width"] // 2
    center_y = viewport["height"] // 2

    for i in range(steps):
        page.mouse.move(center_x, center_y)
        page.wait_for_timeout(100)

        scroll_method = "unknown"

        # Strategy 1: JS scroll on detected container
        scroll_result = page.evaluate("""
            () => {
                const allScrollable = [];
                document.querySelectorAll('div, section, article, main, ul').forEach(el => {
                    const style = window.getComputedStyle(el);
                    if ((style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                        el.scrollHeight > el.clientHeight + 5) {
                        const rect = el.getBoundingClientRect();
                        if (rect.height > 0 && rect.top < window.innerHeight) {
                            allScrollable.push({ el, scrollable: el.scrollHeight - rect.height, className: el.className.split(' ')[0] });
                        }
                    }
                });

                if (allScrollable.length > 0) {
                    allScrollable.sort((a, b) => b.scrollable - a.scrollable);
                    allScrollable[0].el.scrollBy({ top: window.innerHeight * 0.8, behavior: 'instant' });
                    return 'JS:' + allScrollable[0].className;
                }
                return 'JS_fail';
            }
        """)

        if 'JS_fail' not in scroll_result:
            scroll_method = scroll_result
            logger.info(f"page_scroll: step {i+1}/{steps} {scroll_method}")
            # JS scroll succeeded, but also try mouse.wheel + keyboard for MUI pages
            page.mouse.wheel(0, y)
            page.keyboard.press("PageDown")
        else:
            # Strategy 2: Try to find element under cursor and scroll it
            elem_result = page.evaluate("""
                () => {
                    const centerX = window.innerWidth / 2;
                    const centerY = window.innerHeight / 2;
                    let elem = document.elementFromPoint(centerX, centerY);
                    while (elem && elem !== document.body) {
                        if (elem.scrollHeight > elem.clientHeight) {
                            elem.scrollBy({ top: window.innerHeight * 0.8, behavior: 'instant' });
                            return 'elem_scroll:' + elem.className.split(' ')[0];
                        }
                        elem = elem.parentElement;
                    }
                    return 'elem_fail';
                }
            """)

            if 'elem_fail' not in elem_result:
                scroll_method = elem_result
                logger.info(f"page_scroll: step {i+1}/{steps} {scroll_method}")
            else:
                # Strategy 3: Try to scroll any scrollable element found
                any_scroll = page.evaluate("""
                    () => {
                        const scrollable = document.querySelector('[style*="overflow"]');
                        if (scrollable) {
                            scrollable.scrollTop += 500;
                            return 'any_scroll:' + scrollable.className.split(' ')[0];
                        }
                        // Try body
                        if (document.body && document.body.scrollHeight > document.body.clientHeight) {
                            document.body.scrollTop += 500;
                            return 'body_scroll';
                        }
                        return 'scroll_fail';
                    }
                """)
                
                if 'scroll_fail' not in any_scroll:
                    scroll_method = any_scroll
                    logger.info(f"page_scroll: step {i+1}/{steps} {scroll_method}")
                else:
                    # Strategy 4: mouse.wheel()
                    page.mouse.wheel(0, y)
                    page.wait_for_timeout(200)
                    scroll_method = "mouse_wheel"
                    logger.info(f"page_scroll: step {i+1}/{steps} {scroll_method}")
                    
                    # Strategy 5: keyboard PageDown as last resort
                    page.keyboard.press("PageDown")
                    page.wait_for_timeout(200)
                    page.keyboard.press("PageDown")
                    logger.info(f"page_scroll: step {i+1}/{steps} keyboard PageDown x2")

        # Log scroll position after all strategies
        scroll_pos = page.evaluate("""
            () => {
                const main = document.querySelector('main, [role="main"], #__next, .main-content');
                if (main) return 'main.scrollY=' + main.scrollTop + '/' + main.scrollHeight;
                return 'window.scrollY=' + window.scrollY + '/' + document.body.scrollHeight;
            }
        """)
        logger.info(f"page_scroll: position after step: {scroll_pos}")

        page.wait_for_timeout(delay // steps if steps > 0 else delay)

    logger.info("page_scroll: done")


def scroll_tab_content(page: Page, v: dict):
    """
    Scroll the content area inside a tab (Posts tab, Products tab, etc).
    Finds the scrollable container within the active tab content area.
    """
    y = v.get("y", 500)
    delay = v.get("delay", 1000)
    
    logger.info(f"scroll_tab_content: scrolling content by {y}px")
    
    result = page.evaluate(f"""
        (scrollAmount) => {{
            // Strategy 1: Find tab content container - look for the container after the Posts tab button
            // Common patterns in tabbed UIs
            const tabButton = Array.from(document.querySelectorAll('[role="tab"]')).find(t => t.textContent.includes('Posts'));
            if (tabButton) {{
                // Find the panel associated with this tab (usually the next sibling or element with aria-labelledby)
                let container = tabButton.nextElementSibling;
                while (container) {{
                    if (container.scrollHeight > container.clientHeight) {{
                        container.scrollTop += scrollAmount;
                        return 'scrolled tab panel: ' + container.className;
                    }}
                    container = container.nextElementSibling;
                }}
                
                // Alternative: find container by aria-labelledby
                const panelId = tabButton.getAttribute('aria-controls');
                if (panelId) {{
                    const panel = document.getElementById(panelId);
                    if (panel && panel.scrollHeight > panel.clientHeight) {{
                        panel.scrollTop += scrollAmount;
                        return 'scrolled by aria-controls: ' + panelId;
                    }}
                }}
            }}
            
            // Strategy 2: Find any visible scrollable container in the main content area
            const main = document.querySelector('[role="main"]') || document.querySelector('main') || document.querySelector('#root > div > div');
            if (main && main.scrollHeight > main.clientHeight) {{
                main.scrollTop += scrollAmount;
                return 'scrolled main: ' + main.className;
            }}
            
            // Strategy 3: Window scroll
            window.scrollBy(0, scrollAmount);
            return 'window scroll';
        }}
    """, y)
    
    logger.info(f"scroll_tab_content result: {result}")
    page.wait_for_timeout(delay)

def go_back(page: Page, v: dict):
    """Go back in browser history (equivalent to clicking browser back button)."""
    page.go_back()
    page.wait_for_timeout(v.get("sleep_after", 3000))
    logger.info("Navigated back in browser history")

def test_invalid_qr(page: Page, v):
    from playwright.sync_api import sync_playwright
    url = v if isinstance(v, str) else v.get("open", "https://s.pear.us/iyR93K")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream", "--use-file-for-fake-video-capture=data/error_QR.y4m"])
        context = browser.new_context(permissions=["camera", "microphone"])
        new_page = context.new_page()
        new_page.goto(url)
        try:
            new_page.get_by_text("Code Not Recognized").first.wait_for(state="visible", timeout=15000)
            logger.info("Verified 'Code Not Recognized'")
        finally:
            browser.close()

def execute_not_recognized_scan(page: Page, v):
    """
    Verify 'QR code is for a different event' by overwriting the fake camera y4m
    with a wrong QR code and navigating to the scanner page in the existing browser.
    Restores the correct y4m afterwards.
    """
    import shutil
    sys.path.insert(0, os.path.join(BASE_DIR, "test_case", "UI"))
    from conftest import _generate_scanner_y4m

    correct_y4m = "/tmp/pear_data/Ticket_Small.y4m"
    backup_y4m = "/tmp/pear_data/Ticket_Small_backup.y4m"
    scanner_url = "https://s.pear.us/7DCjTz"

    # Backup correct y4m and generate wrong QR
    shutil.copy(correct_y4m, backup_y4m)
    _generate_scanner_y4m(correct_y4m, qr_text="9329611")
    logger.info(">>> Overwrote camera y4m with wrong QR (9329611)")

    try:
        # Navigate to scanner page
        page.goto(scanner_url, wait_until="networkidle")
        page.wait_for_timeout(12000)
        page.get_by_text("QR code is for a different event").first.wait_for(
            state="visible", timeout=20000
        )
        logger.info(">>> Verified: 'QR code is for a different event' displayed")
    finally:
        # Restore correct y4m
        shutil.copy(backup_y4m, correct_y4m)
        logger.info(">>> Restored correct camera y4m")


def run_workflow_script(page: Page, v):
    """
    Generic workflow script runner for api/ui_workflow/*.py scripts.
    Allows QA to write Python API/script workflows callable from YAML.

    YAML usage:
        run_workflow_script: { script: "create_test_post.py", args: { title: "Test" } }

    Script conventions:
        - Recommended: use Playwright APIRequestContext (automatically carries browser cookies + JS auth header)
        - Legacy approach: subprocess + requests (requires manual token handling, deprecated)
    """
    import json

    script_name = v.get("script")
    if not script_name:
        raise ValueError("run_workflow_script: 'script' parameter is required, format: { script: 'filename.py' }")

    if not script_name.endswith(".py"):
        script_name += ".py"

    script_path = os.path.join(BASE_DIR, "test_case", "UI", "ui_workflow", script_name)

    if not os.path.exists(script_path):
        raise FileNotFoundError(f"run_workflow_script: script not found: {script_path}")

    # New approach: use Playwright APIRequestContext (automatically shares browser cookies + JS auth header)
    # Note: requires the script to support --api-context mode; subprocess legacy logic is kept here for compatibility
    args = v.get("args", {})
    args_json = json.dumps(args)

    logger.info(f">>> Running workflow script: {script_name} | args: {args}")

    result = subprocess.run(
        [sys.executable, script_path, args_json],
        capture_output=True,
        text=True,
        cwd=BASE_DIR
    )

    logger.info(f"[workflow stdout]\n{result.stdout}")
    if result.stderr:
        logger.warning(f"[workflow stderr]\n{result.stderr}")

    if result.returncode != 0:
        logger.error(f"Workflow script '{script_name}' failed with exit code {result.returncode}")
        raise AssertionError(
            f"Workflow script '{script_name}' failed (exit code {result.returncode}).\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )

    logger.info(f"[run_workflow_script] completed successfully.")


def duplicate_post(page: Page, v):
    """
    Duplicate Post — calls duplicate_post.py as a subprocess (standalone requests, independent of browser JS context).

    Flow:
        1. duplicate_post.py loads cookies from cookie_release.json
        2. Extracts old JWT, calls GET /auth/refreshToken to obtain a new JWT
        3. Uses new JWT to call GET /posts/curator/duplicate/verify/{id} (verify)
        4. Uses new JWT to call GET /posts/curator/duplicate/{id} (execute, creates draft)
        5. Draft post id is written to .duplicate_result.json
        6. base.py reads the result and stores it in page._workflow_context

    YAML usage:
        duplicate_post: { post_id: "xxx", capture_key: "cloned_post_id" }
    """
    import subprocess, json as jsonmod

    post_id = v.get("post_id")
    capture_key = v.get("capture_key", "cloned_post_id")

    if not post_id:
        raise ValueError("duplicate_post: 'post_id' parameter is required")

    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "ui_workflow", "duplicate_post.py"
    )
    result_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "ui_workflow", ".duplicate_result.json"
    )

    logger.info(f"[duplicate_post] Running script for post_id={post_id}")

    result = subprocess.run(
        [sys.executable, script_path, jsonmod.dumps({"post_id": post_id})],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(script_path),
        timeout=30,
    )

    if result.stdout:
        logger.info(f"[duplicate_post] stdout: {result.stdout[:300]}")
    if result.stderr:
        logger.warning(f"[duplicate_post] stderr: {result.stderr[:300]}")

    if result.returncode != 0:
        raise AssertionError(f"[duplicate_post] script failed (exit {result.returncode}): {result.stderr[:200]}")

    # Read result file
    if os.path.exists(result_file):
        with open(result_file, "r", encoding="utf-8") as f:
            data = jsonmod.load(f)
        new_post_id = data.get("new_post_id") or data.get("id")
        logger.info(f"[duplicate_post] Done: {post_id} -> {new_post_id}")
    else:
        new_post_id = None
        logger.warning(f"[duplicate_post] Result file not found: {result_file}")

    # Store in context
    if not hasattr(page, "_workflow_context"):
        setattr(page, "_workflow_context", {})
    getattr(page, "_workflow_context")[capture_key] = new_post_id
    logger.info(f"[duplicate_post] Stored {capture_key} = {new_post_id} in workflow context")

def verify_value(page: Page, v: dict):
    """Assert an <input> value (Playwright-native input_value(), no JS).

    YAML usage:
        verify_value_price: { locator: "input[name='variants.0.ticketPrice']", value: "100.00" }
        verify_value_dynamic: { locator: "input[name='variants.0.price']", value: "{{retails_price}}", tolerance: 0.01 }
        verify_value_phone: { locator: "input[name='contact.phoneNumber']", regex: "(\\d\\D*){10}" }

    Supported params:
      - locator / name : target input (CSS/xpath locator, or input[name=...] via `name`)
      - value          : expected value; {{var}} placeholders are backfilled from the
                         workflow context first (e.g. "{{my_revenue_venue_map}}")
      - regex          : instead of an exact `value`, assert the input value MATCHES this
                         regex ({{var}} backfilled). Handy for auto-formatted fields whose
                         exact rendering varies (e.g. a phone field -> "at least 10 digits").
      - tolerance      : optional numeric tolerance (e.g. 0.01) so a full-precision
                         stored value ("114.7727") still matches a 2-dp expectation ("114.77")
      - timeout        : ms to wait for the input to become visible (default 10000)
    """
    target_name = _fill_placeholders(v.get("name"), page)
    target_locator = _resolve_locator(v.get("locator"))
    target_locator = _fill_placeholders(target_locator, page)
    expected_value = _fill_placeholders(str(v.get("value")), page)
    regex = v.get("regex")
    tolerance = v.get("tolerance")
    timeout = v.get("timeout", 10000)
    logger.info(f"Verifying value of '{target_name or target_locator}' matches '{regex or expected_value}'")
    if target_locator:
        el = page.locator(target_locator).first
    else:
        el = page.locator(f'input[name="{target_name}"], [name="{target_name}"]').first
    el.wait_for(state="visible", timeout=timeout)
    actual_value = str(el.input_value())
    if regex:
        pat = _fill_placeholders(str(regex), page)
        if re.search(pat, actual_value):
            logger.info(f"Value '{actual_value}' matches regex {pat!r}")
            return
        raise AssertionError(f"verify_value: '{actual_value}' does not match {pat!r}")
    if actual_value != expected_value:
        try:
            if float(actual_value) == float(expected_value): return
        except: pass
        if tolerance is not None:
            try:
                if abs(float(actual_value) - float(expected_value)) <= float(tolerance):
                    logger.info(f"Value '{actual_value}' is within tolerance {tolerance} of '{expected_value}'")
                    return
            except: pass
        raise AssertionError(f"Expected value '{expected_value}', but found '{actual_value}'")

def verify_value_near(page: Page, v: dict):
    # Restoring simplified version of verify_value_near for compatibility
    near_text = v.get("near_text")
    expected_value = str(v.get("expected") or v.get("value"))
    logger.info(f"Verifying value near text '{near_text}', expected: '{expected_value}'")
    # Search for an input near the exact text match
    el = page.get_by_text(cast(str, near_text), exact=False).locator("xpath=../..//input").first
    el.wait_for(state="visible", timeout=5000)
    actual_value = str(el.input_value())
    if actual_value != expected_value:
        raise AssertionError(f"Near text '{near_text}': Expected '{expected_value}', got '{actual_value}'")


# XPath fragments used by verify_enabled to locate a row's control from its label.
# [WHY TWO] "the element that IS the control" and "an element that CONTAINS the control" are
# different predicates, and conflating them silently selects the control's WRAPPER: for
#     <span><input type="checkbox" disabled></span>
# the predicate `input[@type='checkbox']` is true of the wrapper <span> (it has that child) and
# FALSE of the <input> itself, so `//*[input[...]]` returned the useless span — on which
# is_disabled() is always False (caught by the self-test on 2026-10-16).
_CONTROL_SELF = ("self::input[@type='checkbox'] or self::input[@type='radio'] "
                 "or @role='checkbox' or @role='switch'")
_CONTROL_DESC = (".//input[@type='checkbox'] or .//input[@type='radio'] "
                 "or .//*[@role='checkbox'] or .//*[@role='switch']")


def verify_enabled(page: Page, v: dict):
    """Assert an element is enabled — or DISABLED (Playwright-native, no JS).

    [WHY IT EXISTS] The framework could assert visibility / text / attributes, but not
    actionability state, so every "this control must be disabled" check had to be an
    `execute_js` reading `element.disabled`. `locator.is_disabled()` is the native API and it
    covers BOTH a native `disabled` attribute and `aria-disabled="true"`, so it works for plain
    inputs and for MUI Switch / Checkbox / Radio alike.

    Supported params:
      - locator : directly target the control
      - label   : accessible text of the row (e.g. "Recommend at checkout"); the control is then
                  found by walking UP from the label to the nearest ancestor that holds one, and
                  taking that ancestor's first control — exactly the walk the old JS did.
      - scope   : optional container locator to search the label within (e.g. the open dialog)
      - exact   : exact text match for `label` (default False)
      - enabled : expected state (default True); set false to assert the control is DISABLED
      - control : optional XPath fragment overriding "the element that IS the control"
                  (default: self::input[type=checkbox] / self::input[type=radio] /
                  @role=checkbox / @role=switch)
      - timeout : ms to wait for the control (default 10000)

    YAML usage:
        verify_recommend_at_checkout_disabled:
            label: "Recommend at checkout"
            scope: "xpath=//*[@role='dialog']"
            enabled: false
    """
    enabled = v.get("enabled", True)
    timeout = int(v.get("timeout", 10000))
    exact = bool(v.get("exact", False))
    ctrl_self = v.get("control") or _CONTROL_SELF
    ctrl_desc = v.get("control_desc") or _CONTROL_DESC

    if v.get("locator"):
        ctrl = page.locator(_fill_placeholders(_resolve_locator(v["locator"]), page)).first
        where = v["locator"]
    elif v.get("label"):
        label_text = _fill_placeholders(str(v["label"]), page)
        scope_loc = v.get("scope")
        base = (
            page.locator(_fill_placeholders(_resolve_locator(scope_loc), page)).last
            if scope_loc
            else page
        )
        label_loc = base.get_by_text(label_text, exact=exact).first
        label_loc.wait_for(state="visible", timeout=timeout)
        # nearest ancestor-or-self that CONTAINS a control, then the control itself inside it.
        # `ancestor-or-self::*[...][1]` counts from the NEAREST on a reverse axis, so this is the
        # innermost such ancestor — the same element the old JS climb found.
        ctrl = label_loc.locator(
            f"xpath=ancestor-or-self::*[{ctrl_desc}][1]//*[{ctrl_self}]"
        ).first
        where = f"label {label_text!r} (scope={scope_loc!r})"
    else:
        raise ValueError("verify_enabled: need 'locator' or 'label'")

    ctrl.wait_for(state="attached", timeout=timeout)
    actual_disabled = ctrl.is_disabled()
    if bool(enabled) == (not actual_disabled):
        logger.info(f"verify_enabled: control for {where} is "
                    f"{'enabled' if enabled else 'DISABLED'} as expected")
        return not actual_disabled
    raise AssertionError(
        f"verify_enabled: control for {where} is "
        f"{'DISABLED' if actual_disabled else 'ENABLED'} but the case expects it to be "
        f"{'enabled' if enabled else 'DISABLED'}"
    )


def verify_attribute(page: Page, v: dict):
    """Assert an element's attribute value (Playwright-native get_attribute(), no JS).

    The native replacement for the ad-hoc execute_js "read getAttribute and compare"
    pattern. Reusable across all YAML cases — e.g. verifying an <a href>, an <img src/alt>,
    or an ARIA state (aria-checked). Supports {{var}} backfill on `value` and `regex`.

    Supported params:
      - locator        : target element (CSS/xpath locator)  [required]
      - attribute      : attribute name to read (e.g. "href")  [required]
      - value          : expected exact value; {{var}} placeholders backfilled
      - regex          : instead of exact `value`, assert the attribute MATCHES this regex
                         ({{var}} backfilled)
      - scope          : optional container to search within (same shape as verify_text_visible)
      - index          : element index when locator matches several (default 0)
      - timeout        : ms to wait for the element (default 10000)

    YAML usage:
        verify_learn_more_href:
            locator: "xpath=//*[@role='dialog']//a[normalize-space(.)='Learn more']"
            attribute: "href"
            value: "https://partner.pear.us/post/advanced-event-settings"
    """
    target_locator = _fill_placeholders(_resolve_locator(v.get("locator")), page)
    scope_cfg = v.get("scope")
    attribute = v.get("attribute")
    expected_value = (
        _fill_placeholders(str(v["value"]), page) if v.get("value") is not None else None
    )
    regex = v.get("regex")
    index = v.get("index", 0)
    timeout = v.get("timeout", 10000)

    if not target_locator:
        raise ValueError("verify_attribute: 'locator' is required")
    if not attribute:
        raise ValueError("verify_attribute: 'attribute' is required")

    if scope_cfg:
        try:
            if scope_cfg.get("locator"):
                scope_loc = page.locator(scope_cfg["locator"]).first
            elif scope_cfg.get("text"):
                scope_loc = page.get_by_text(
                    scope_cfg["text"], exact=scope_cfg.get("exact", False)
                ).first
            else:
                raise AssertionError(
                    f"verify_attribute: invalid scope {scope_cfg}; need 'text' or 'locator'"
                )
            scope_loc.wait_for(state="visible", timeout=timeout)
            el = scope_loc.locator(target_locator).nth(index)
        except Exception:
            raise AssertionError(f"verify_attribute: scope container {scope_cfg} not found.")
    else:
        el = page.locator(target_locator).nth(index)

    el.wait_for(state="visible", timeout=timeout)
    actual = el.get_attribute(attribute)
    actual = "" if actual is None else str(actual)
    logger.info(f"verify_attribute: {target_locator}[{attribute}] = {actual!r}")

    if regex:
        pat = _fill_placeholders(str(regex), page)
        if re.search(pat, actual):
            logger.info(f"Attribute '{attribute}'='{actual}' matches regex {pat!r}")
            return
        raise AssertionError(
            f"verify_attribute: '{attribute}'='{actual}' does not match {pat!r}"
        )
    if expected_value is None:
        raise ValueError("verify_attribute: need 'value' or 'regex'")
    if actual != expected_value:
        raise AssertionError(
            f"verify_attribute: expected {attribute}='{expected_value}', but found '{actual}'"
        )
    logger.info(f"verify_attribute OK: {attribute}='{expected_value}'")


def verify_radio_checked(page: Page, v: dict):
    """Assert a radio option's selection state (Playwright-native, no JS).

    Handles both native <input type="radio"> (is_checked) and MUI role="radio"
    controls (aria-checked="true"). Reusable across all YAML cases.

    Supported params:
      - locator        : directly target the radio control (input[type=radio] or
                         role="radio"); takes precedence over `label`
      - label          : accessible text of the radio option; the radio control is found
                         inside the option's container (e.g. "Ticket buyers only")
      - exact          : exact text match for `label` (default true — avoids matching the
                         option's descriptive paragraph, which often contains the same words)
      - group          : optional locator for the radio group / container to scope the label
                         search (e.g. the open drawer)
      - assert_checked : expected selection state (default true); set false to assert the
                         radio is NOT selected
      - timeout        : ms to wait (default 10000)

    YAML usage:
        verify_default_radio_option1:
            label: "Ticket buyers only"
            group: "xpath=//*[@role='dialog'][.//*[contains(normalize-space(.),'Address visibility settings')]]"
    """
    label = v.get("label")
    group_loc = v.get("group")
    exact = v.get("exact", True)
    assert_checked = v.get("assert_checked", True)
    timeout = v.get("timeout", 10000)

    if v.get("locator"):
        radio = page.locator(_fill_placeholders(_resolve_locator(v["locator"]), page)).first
    elif label:
        if group_loc:
            group = page.locator(_fill_placeholders(_resolve_locator(group_loc), page)).first
            group.wait_for(state="visible", timeout=timeout)
            base = group
        else:
            base = page
        option = base.get_by_text(_fill_placeholders(label, page), exact=exact).first
        option.wait_for(state="visible", timeout=timeout)
        # The radio control lives in the SAME option container as the label text, but is
        # typically a SIBLING of the label span (MUI FormControlLabel:
        #   <label> [ <span radio><input type=radio></span> <span label>{text}</span> ]).
        # So walk up to the nearest ancestor that contains a radio, then grab that radio.
        if option.locator("xpath=ancestor::*[.//input[@type='radio']][1]//input[@type='radio']").count() > 0:
            radio = option.locator("xpath=ancestor::*[.//input[@type='radio']][1]//input[@type='radio']").first
        else:
            radio = option.locator("xpath=ancestor::*[.//*[@role='radio']][1]//*[@role='radio']").first
    else:
        raise ValueError("verify_radio_checked: need 'locator' or 'label'")

    radio.wait_for(state="visible", timeout=timeout)

    # Native input -> is_checked(); MUI role=radio -> aria-checked attribute
    tag = (radio.get_attribute("type") or "").lower()
    role = (radio.get_attribute("role") or "").lower()
    if tag == "radio":
        is_checked = radio.is_checked()
    elif role == "radio":
        is_checked = (radio.get_attribute("aria-checked") or "false").lower() == "true"
    else:
        try:
            is_checked = radio.is_checked()
        except Exception:
            is_checked = (radio.get_attribute("aria-checked") or "false").lower() == "true"

    # Compute the state label BEFORE branching: `got` was previously only assigned in
    # the failure branch, so the success-path logger.info below raised
    # UnboundLocalError on the very first PASS of this action.
    got = "checked" if is_checked else "unchecked"
    if is_checked != assert_checked:
        wanted = "checked" if assert_checked else "unchecked"
        raise AssertionError(
            f"verify_radio_checked: radio (label={label!r}, locator={v.get('locator')!r}) "
            f"expected {wanted} but is {got}."
        )
    logger.info(f"verify_radio_checked OK: radio is {got}")


def _money_str(x, nd=2):
    """Format a number as a fixed-decimal string, half-up (114.7727 -> '114.77')."""
    from decimal import Decimal, ROUND_HALF_UP
    quantum = Decimal(1).scaleb(-int(nd))          # nd=2 -> Decimal('0.01')
    return str(Decimal(str(x)).quantize(quantum, rounding=ROUND_HALF_UP))


def _fill_placeholders(s, page):
    """Backfill {{var}} placeholders from the page workflow context, falling back to the
    cross-case global store (same lookup table execute_js / smart_click use).

    Lets non-JS actions (verify_*, extract_value, compute_value) consume variables saved
    by earlier steps. No-op when the value is not a string or has no placeholder.
    """
    if not isinstance(s, str) or "{{" not in s:
        return s
    for _k, _v in _merged_context_vars(page).items():
        if _k:
            s = s.replace("{{%s}}" % _k, str(_v))
    return s


def _save_context_value(page, save_as, value, is_global=False):
    """Store a value in the page workflow context (optionally the cross-case store)."""
    if not save_as:
        return
    if not hasattr(page, "_workflow_context"):
        setattr(page, "_workflow_context", {})
    getattr(page, "_workflow_context")[save_as] = value
    logger.info(f"Saved '{save_as}' = {value!r} in workflow context")
    if is_global:
        _set_global(save_as, value)
        logger.info(f"Also published '{save_as}' to the cross-case global store")


def extract_value(page: Page, v: dict):
    """Read a value from the page and save it to the workflow context — the Playwright-native
    replacement for the common `execute_js` "read a price and save_as" pattern.

    Supported params:
      - locator / name : where to read from (CSS/xpath locator; `name` -> input[name=...])
      - source         : "input" (default, input_value) | "text" (inner_text) |
                         "content" (textContent, no layout whitespace) |
                         "attribute"
      - attribute      : attribute name when source="attribute"
      - strip_whitespace : remove ALL whitespace from the raw text before regex/parse
                         (default false; handy when the target is split across text nodes,
                         e.g. a post URL rendered as "host\\n/post/\\nslug")
      - regex          : custom extraction regex (first capture group, else whole match);
                         default pulls the first number (-123.45) from the raw string
      - numeric        : parse the result as a number (default true)
      - round          : decimals of the saved number string (default 2 -> "114.77")
      - save_as        : workflow-context key, usable as {{save_as}} in later steps
      - global         : also publish to the cross-case store (like execute_js global:true)
      - timeout        : ms to poll until the value is readable (default 10000)
      - index          : element index when the locator matches several (default 0)

    YAML usage:
        extract_value_my_revenue:
            locator: "input[name='variants.0.ticketPrice']"
            save_as: "my_revenue_venue_map"
        extract_value_card_retail:
            locator: "xpath=//p[normalize-space(.)='{{ticket}}']/ancestor::*[contains(.,'incl.')][1]"
            source: text
            save_as: "retail_price"
    """
    import time

    locator = _fill_placeholders(_resolve_locator(v.get("locator")), page)
    name = _fill_placeholders(v.get("name"), page)
    source = v.get("source", "input")
    attribute = v.get("attribute")
    regex = v.get("regex")
    numeric = v.get("numeric", True)
    nd = v.get("round", 2)
    save_as = v.get("save_as")
    timeout = v.get("timeout", 10000)
    index = v.get("index", 0)

    if not locator and not name:
        raise ValueError("extract_value: 'locator' or 'name' is required")

    if locator:
        el = page.locator(locator).nth(index)
    else:
        el = page.locator(f'input[name="{name}"], [name="{name}"]').first

    label = locator or name
    logger.info(f"extract_value: reading '{label}' (source={source}, save_as={save_as})")

    start = time.time()
    last_err = None
    while time.time() - start < timeout / 1000.0:
        try:
            el.wait_for(state="visible", timeout=2000)
            if source == "input":
                raw = el.input_value()
            elif source == "attribute":
                raw = el.get_attribute(attribute) or ""
            elif source in ("content", "textcontent", "text_content"):
                # textContent: layout does not inject whitespace/newlines -> good for URLs
                raw = el.text_content() or ""
            else:
                raw = el.inner_text()
            raw = "" if raw is None else str(raw)
            if v.get("strip_whitespace"):
                raw = re.sub(r"\s+", "", raw)
            if regex:
                m = re.search(regex, raw)
                if not m:
                    raise ValueError(f"regex {regex!r} not found in {raw[:80]!r}")
                out = m.group(1) if m.groups() else m.group(0)
            elif numeric:
                m = re.search(r"-?\d+(?:\.\d+)?", raw.replace(",", ""))
                if not m:
                    raise ValueError(f"no number found in {raw[:80]!r}")
                out = m.group(0)
            else:
                out = raw.strip()
            value = _money_str(float(out), nd) if numeric else out
            _save_context_value(page, save_as, value, v.get("global"))
            return value
        except Exception as e:
            last_err = e
            time.sleep(0.3)
    raise AssertionError(f"extract_value: could not read '{label}' within {timeout}ms: {last_err}")


def compute_value(page: Page, v: dict):
    """Evaluate an arithmetic expression ({{var}} backfilled) and save the result — the
    native replacement for the `execute_js` "define a helper fn + call it" money-math
    pattern (e.g. retail = (my_revenue + 1) / (1 - fee% - tax%)).

    Supported params:
      - expression : arithmetic expression; {{var}} placeholders are backfilled from the
                     workflow context first. Only digits and + - * / ( ) . are allowed,
                     so an unresolved {{var}} fails loudly instead of evaluating junk.
      - save_as    : workflow-context key for the result
      - global     : also publish to the cross-case store
      - round      : decimals of the saved number string (default 2 -> "114.77")

    YAML usage:
        compute_value_retails_price:
            expression: "({{my_revenue_venue_map}} + 1) / (1 - 0.1 - 0.02)"
            save_as: "retails_price_venue_map"
    """
    expression = v.get("expression") or v.get("expr")
    if not expression:
        raise ValueError("compute_value: 'expression' is required")
    expr = _fill_placeholders(str(expression), page)
    if not re.fullmatch(r"[\d\s+\-*/().]+", expr):
        raise ValueError(
            f"compute_value: unsafe or unresolved expression: {expr!r} "
            "(only numbers and + - * / ( ) . are allowed; check the {{var}} names)"
        )
    try:
        result = eval(expr, {"__builtins__": {}}, {})
    except Exception as e:
        raise AssertionError(f"compute_value: cannot evaluate {expr!r}: {e}")
    value = _money_str(float(result), v.get("round", 2))
    logger.info(f"compute_value: {expr} = {value}")
    _save_context_value(page, v.get("save_as"), value, v.get("global"))
    return value


def _xpath_literal(s):
    """Return an XPath 1.0 string literal for `s` (handles quotes safely)."""
    s = str(s)
    if '"' not in s:
        return '"%s"' % s
    if "'" not in s:
        return "'%s'" % s
    # both quote kinds present -> concat()
    return "concat(%s)" % ", '\"', ".join("'%s'" % part for part in s.split('"'))


def _find_row_amount(page, label, scope=None, tail_limit=24, levels=4, signed=True, timeout=10000):
    """Locate the amount of a labelled row with Playwright locators only (no JS).

    [DOM FACT] MUI rows put the label either in a leaf (<p>Total</p>) or in a DIRECT text
    node (<X>Subtotal<span>$64.48</span></X>); the amount then lives in that element or in
    one of its nearest ancestors. This helper matches the label via
    `normalize-space(text())`, climbs up to `levels` ancestors, keeps the stripped tail
    short (<= tail_limit) so it never walks past the row and grabs a foreign amount, and
    parses the first signed "$x.yz" it meets.

    Returns (value, error_message); value is None when nothing was found.
    """
    import time

    lit = _xpath_literal(label)
    start = time.time()
    last_err = None
    while time.time() - start < timeout / 1000.0:
        try:
            if scope:
                cands = page.locator(scope).first.locator(f"xpath=.//*[normalize-space(text())={lit}]")
            else:
                cands = page.locator(f"xpath=//*[normalize-space(text())={lit}]")
            n = cands.count()
            for i in range(n):
                node = cands.nth(i)
                try:
                    if not node.is_visible():
                        continue
                except Exception:
                    continue
                for _lvl in range(int(levels)):
                    try:
                        text = node.inner_text()
                    except Exception:
                        break
                    tail = re.sub(r"\s+", " ", text.replace(label, " ")).strip()
                    if len(tail) <= int(tail_limit):
                        m = re.search(r"(-?)\s*\$\s*([\d,]+(?:\.\d+)?)", tail)
                        if m:
                            val = float(m.group(2).replace(",", ""))
                            return (-val if (signed and m.group(1) == "-") else val), None
                    parent = node.locator("xpath=..")
                    if parent.count() == 0:
                        break
                    node = parent.first
            last_err = f"label matched {n} element(s) but no '$' amount within {levels} ancestor level(s)"
        except Exception as e:
            last_err = e
        time.sleep(0.4)
    return None, last_err


def extract_row_value(page: Page, v: dict):
    """Read the amount of a labelled row (e.g. "Subtotal", "Transaction fees", "Total",
    "Net Earning") and save it — the Playwright-native replacement for the `rowVal(label)`
    JS helper repeated across the fee-breakdown cases (see actions/base.py `_find_row_amount`).

    Supported params:
      - label      : row label text (exact match against the element's own text node)
      - scope      : optional locator restricting the search container (e.g. the Checkout drawer)
                     or the whole page when omitted
      - save_as    : workflow-context key (usable as {{save_as}} later)
      - global     : also publish to the cross-case store
      - round      : decimals of the saved string (default 2 -> "64.48")
      - timeout    : ms to poll for the row (default 10000)
      - levels     : how many ancestors to climb while looking for the amount (default 4)
      - tail_limit : max chars kept after stripping the label (default 24; use 16 for
                     the "Show summary" header amount)
      - signed     : keep a leading '-' (default true, e.g. refunded Net Earning "-5.27")
      - required   : raise when the row is not found (default true; false saves "")

    YAML usage:
        extract_row_value_subtotal:
            label: "Subtotal"
            scope: ".MuiDrawer-root"
            save_as: "subtotal"
    """
    label = _fill_placeholders(v.get("label") or v.get("text"), page)
    if not label:
        raise ValueError("extract_row_value: 'label' is required")
    scope = _fill_placeholders(_resolve_locator(v.get("scope")), page)
    timeout = v.get("timeout", 10000)
    val, err = _find_row_amount(
        page, label, scope,
        tail_limit=v.get("tail_limit", 24),
        levels=v.get("levels", 4),
        signed=v.get("signed", True),
        timeout=timeout,
    )
    if val is None:
        if v.get("required", True):
            raise AssertionError(
                f"extract_row_value: no amount found for row '{label}' within {timeout}ms ({err})"
            )
        value = ""
    else:
        value = _money_str(val, v.get("round", 2))
    _save_context_value(page, v.get("save_as"), value, v.get("global"))
    logger.info(f"extract_row_value: '{label}' = {value}")
    return value


def verify_row_value(page: Page, v: dict):
    """Assert the amount of a labelled row equals `value` (± tolerance) — the native
    replacement for the `rowVal(label) == expected` JS assertions.

    Params: label, scope, value (expected; {{var}} backfilled), tolerance (default 0.01),
            timeout, levels, tail_limit, signed (see extract_row_value),
            absent_when_zero (default false): when true, a MISSING row is accepted when the
            expected value is 0 — this encodes the "[PRICING FACT] a 0 amount hides its row"
            rule natively instead of an `if(tax===0 && !row) ...` JS branch. A row that IS
            present with 0 still passes (and a present non-zero amount still fails), so the
            guard stays meaningful while tolerating a UI that renders zero rows in some
            contexts and hides them in others.
            retry_until_match (default false, added 2026-10-16): keep RE-READING the row until
            the amount actually MATCHES (within tolerance) or `timeout` runs out, instead of
            returning the first amount seen. Needed whenever the value changes ASYNCHRONOUSLY
            after an action — e.g. a partner full refund settles server-side and "Net Earning"
            flips from +fees to -fees while the row stays visible the whole time. Native
            replacement for the old `for(i<50){ v=rowVal(l); if(v!==null && v<0) break; await 500 }`
            polling JS. `retry_interval` (default 0.5s) controls the pause between reads.
            Without this flag the first read wins: `_find_row_amount` returns as soon as it
            sees ANY amount, so an unchanged-but-wrong value fails immediately.

    `value` may also be a LIST of acceptable values — the assertion passes when the row
    matches ANY of them. (e.g. the confirmation header shows either the item total or the
    grand total depending on the ticket provider.)
    """
    import time

    label = _fill_placeholders(v.get("label") or v.get("text"), page)
    if not label:
        raise ValueError("verify_row_value: 'label' is required")
    raw_expected = v.get("value")
    if isinstance(raw_expected, (list, tuple)):
        expected_list = [_fill_placeholders(str(e), page) for e in raw_expected]
    else:
        expected_list = [_fill_placeholders(str(raw_expected), page)]
    expected = " | ".join(expected_list)
    scope = _fill_placeholders(_resolve_locator(v.get("scope")), page)
    timeout = v.get("timeout", 10000)
    tolerance = v.get("tolerance", 0.01)
    levels = v.get("levels", 4)
    tail_limit = v.get("tail_limit", 24)
    signed = v.get("signed", True)
    retry_match = bool(v.get("retry_until_match", False))
    retry_interval = float(v.get("retry_interval", 0.5))
    exp_nums = []
    for e in expected_list:
        m = re.search(r"-?[\d.]+", e.replace(",", ""))
        exp_nums.append(float(m.group(0)) if m else None)

    def _matches(val):
        """True when `val` satisfies the expected value(s) under the current tolerance mode."""
        if tolerance is not None:
            return any(n is not None and abs(val - n) <= float(tolerance) for n in exp_nums)
        return any(_money_str(val) == e.strip() for e in expected_list)

    absent_ok = bool(v.get("absent_when_zero")) and any(
        n is not None and abs(n) <= float(tolerance or 0) for n in exp_nums
    )

    deadline = time.time() + float(timeout) / 1000.0
    last_val, last_err = None, None
    while True:
        # With `retry_until_match` each read gets a SHORT slice of the budget: a single
        # `_find_row_amount` call returns on the first amount it sees, so giving it the whole
        # `timeout` would consume the budget on a still-wrong value and never re-read it.
        if retry_match:
            left_ms = int(max(0.0, deadline - time.time()) * 1000)
            slice_ms = max(400, min(left_ms, 1200))
        else:
            slice_ms = timeout
        val, err = _find_row_amount(
            page, label, scope,
            tail_limit=tail_limit, levels=levels, signed=signed, timeout=slice_ms,
        )
        if val is not None:
            last_val = val
            if _matches(val):
                logger.info(f"verify_row_value: row '{label}' = {val} matches '{expected}'")
                return val
        else:
            last_err = err
            if absent_ok:
                logger.info(f"verify_row_value: row '{label}' absent and expected '{expected}' is 0 -> ok")
                return 0.0
        if not retry_match or time.time() >= deadline:
            break
        if last_val is not None:
            logger.info(f"verify_row_value: row '{label}' = {last_val} != '{expected}' — retrying…")
        time.sleep(retry_interval)

    if last_val is None:
        raise AssertionError(f"verify_row_value: row '{label}' not found within {timeout}ms ({last_err})")
    raise AssertionError(f"verify_row_value: row '{label}' amount {last_val} != expected '{expected}'")


def verify_number(page: Page, v: dict):
    """Assert a NUMBER satisfies a relation — the native replacement for the
    `if(!(x > 0)) throw ...` guards (e.g. "a TDC hub ticket must show a POSITIVE Service fee").

    Params:
      - value    : the actual number; {{var}} is backfilled (e.g. "{{service_fee}}")
      - op       : eq | ne | gt | gte | lt | lte (default "gt")
      - expected : comparison target (default 0)
      - tolerance: slack for eq/ne (default 0.01)

    YAML usage:
        verify_number_service_fee: { value: "{{service_fee}}", op: "gt", expected: "0" }
    """
    if "value" not in v:
        raise ValueError("verify_number: 'value' is required")
    actual_raw = _fill_placeholders(str(v.get("value")), page)
    m = re.search(r"-?[\d.]+", actual_raw.replace(",", ""))
    if not m:
        raise AssertionError(f"verify_number: '{actual_raw}' is not a number")
    actual = float(m.group(0))
    exp_raw = _fill_placeholders(str(v.get("expected", 0)), page)
    me = re.search(r"-?[\d.]+", exp_raw.replace(",", ""))
    expected = float(me.group(0)) if me else 0.0
    op = str(v.get("op", "gt")).lower()
    tol = float(v.get("tolerance", 0.01))
    ok = {
        "eq": lambda a, b: abs(a - b) <= tol,
        "ne": lambda a, b: abs(a - b) > tol,
        "gt": lambda a, b: a > b,
        "gte": lambda a, b: a >= b,
        "lt": lambda a, b: a < b,
        "lte": lambda a, b: a <= b,
    }.get(op)
    if ok is None:
        raise ValueError(f"verify_number: unsupported op {op!r} (use eq/ne/gt/gte/lt/lte)")
    if not ok(actual, expected):
        raise AssertionError(f"verify_number: {actual} {op} {expected} is false")
    logger.info(f"verify_number: {actual} {op} {expected} -> ok")
    return actual


def set_value(page: Page, v: dict):
    """Write a literal (or {{var}}-templated) value into the workflow context — the native
    counterpart of "save a constant / build a URL"; no DOM involved.

    Params: value (required; {{var}} is backfilled from the context first), save_as, global.

    YAML usage:
        set_value_post_url:
            value: "https://release.pear.us/autotestshop/post/event-for-ui-auto-venue-map"
            save_as: "post_url"
            global: true
    """
    if "value" not in v:
        raise ValueError("set_value: 'value' is required")
    value = _fill_placeholders(v.get("value"), page)
    _save_context_value(page, v.get("save_as"), value, v.get("global"))
    logger.info(f"set_value: '{v.get('save_as')}' = {value!r}")
    return value


def verify_defined(page: Page, v: dict):
    """Fail fast when context variables the case depends on are missing — the native
    replacement for the `execute_js_ensure_globals` guard JS.

    Params: vars (list, or comma-separated string). Cross-case globals and local workflow
    vars share the same lookup table as {{var}}, so both are accepted.

    YAML usage:
        verify_defined_globals: { vars: [post_url, ticket_venue_map, my_revenve] }
    """
    names = v.get("vars") or v.get("names") or v.get("keys") or []
    if isinstance(names, str):
        names = [n.strip() for n in names.split(",") if n.strip()]
    if not names:
        raise ValueError("verify_defined: 'vars' (list of names) is required")
    ctx = _merged_context_vars(page)
    missing = [n for n in names if ctx.get(n) in (None, "")]
    if missing:
        raise AssertionError(
            f"verify_defined: missing context variables {missing} "
            f"(available: {sorted(k for k in ctx)}) — run the parent case first in the same pytest process"
        )
    logger.info(f"verify_defined: all present -> {names}")
    return "defined: " + ", ".join(names)


def verify_text_regex(page: Page, v: dict):
    """Assert that the page (or a scope container) contains text matching a regex — the
    native replacement for `if(!/re/.test(txt)) throw ...` JS assertions over a region's text.

    Supported params:
      - pattern / regex  : Python regex; {{var}} placeholders are backfilled first, so a
                           dynamic expected value can be injected directly into the pattern
                           (e.g. "Unit\\\\s*:\\\\s*{{seat_unit}}\\\\b")
      - scope / locator  : optional region to search (locator string, or {locator:}/{text:}
                           dict). Defaults to the whole page body.
      - assert_not_match : invert — assert the pattern is NOT present (default false)
      - flags            : optional regex flags string, e.g. "i" (default none)
      - timeout          : ms to poll until it matches/does not match (default 10000)

    YAML usage:
        verify_unit_matches:
            scope: ".MuiDrawer-root:has-text('Checkout')"
            pattern: "Unit\\s*:\\s*{{seat_unit}}\\b"
    """
    import time

    pat = _fill_placeholders(str(v.get("pattern") or v.get("regex")), page)
    if not pat:
        raise ValueError("verify_text_regex: 'pattern' is required")
    flags = re.IGNORECASE if "i" in str(v.get("flags", "")).lower() else 0
    negate = bool(v.get("assert_not_match", False))
    timeout = v.get("timeout", 10000)
    scope_cfg = v.get("scope") or v.get("locator")

    start = time.time()
    last = None
    while True:
        try:
            if isinstance(scope_cfg, dict):
                sl = scope_cfg.get("locator")
                if sl:
                    text = page.locator(_fill_placeholders(_resolve_locator(sl), page)).first.inner_text()
                else:
                    text = page.get_by_text(cast(str, scope_cfg.get("text"))).first.inner_text()
            elif isinstance(scope_cfg, str):
                text = page.locator(_fill_placeholders(_resolve_locator(scope_cfg), page)).first.inner_text()
            else:
                text = page.inner_text("body")
            m = re.search(pat, text, flags)
            if (m is not None) != negate:
                logger.info(f"verify_text_regex: pattern {pat!r} {'absent (expected)' if negate else 'matched: ' + repr(m.group(0))}")
                return m.group(0) if m else ""
            last = f"pattern {pat!r} {'is present but should be absent' if negate else 'not found'}"
        except Exception as e:
            last = e
        if time.time() - start >= timeout / 1000.0:
            break
        time.sleep(0.4)
    raise AssertionError(f"verify_text_regex: {last}")


def verify_all_commission_values(page: Page, v: dict):
    """
    Verifies commission rates for all products in a list or module.
    Expects a list of values or a single value in 'v'.
    """
    expected_values = v.get("values", [])
    if not expected_values and "value" in v:
        expected_values = [v["value"]]

    logger.info(f"Verifying all commission values: {expected_values}")

    # Implementation based on typical Katana commission UI (labels or inputs)
    for i, val in enumerate(expected_values):
        try:
            # Common pattern: Mui input or a text label
            target = page.locator(f"input[value='{val}'], :text-is('{val}%'), :text-is('{val}')").nth(i)
            target.wait_for(state="visible", timeout=5000)
            logger.info(f"Commission value {i} verified: {val}")
        except Exception as e:
            logger.error(f"Failed to find commission value {val} at index {i}: {e}")
            raise AssertionError(f"Could not verify commission value: {val}")


def wait_toast(page: Page, v: dict):
    """
    Wait for a toast / snackbar message to appear, indicating a background operation completed.
    Supports: message (the text to wait for), timeout (ms, default 15000).

    Usage in YAML:
        wait_save_success: { message: "Post products updated", timeout: 15000 }
        wait_publish_success: { message: "Published", timeout: 10000 }
    """
    import time
    message = v.get("message", "")
    timeout = v.get("timeout", 15000)
    optional = v.get("optional", False)
    if optional:
        timeout = 2000  # short poll when toast is optional
    logger.info(f"wait_toast: waiting for '{message}' (timeout={timeout}ms, optional={optional})")

    start = time.time()
    while time.time() - start < timeout / 1000.0:
        # Search in common toast/snackbar container selectors
        toast_locator = page.locator(
            "[class*='Snackbar'], [class*='Toast'], [role='alert'], "
            ".MuiSnackbar-root, [class*='notification'], [class*='message']"
        )
        for toast in toast_locator.all():
            try:
                if toast.is_visible(timeout=1000):        # Added timeout: previously no timeout could wait 30s per item
                    content = toast.inner_text()
                    if message in content:
                        logger.info(f"Toast found: '{content.strip()[:80]}'")
                        page.wait_for_timeout(500)
                        return
            except Exception:
                pass
        time.sleep(0.3)

    if optional:
        logger.info(f"wait_toast optional: toast '{message}' not found, skipping.")
    else:
        logger.warning(f"Toast '{message}' not found within {timeout}ms, continuing anyway...")
        page.screenshot(path=f"warn_toast_{message[:20]}.png")

def drag_element(page: Page, v: dict):
    """
    Drag and drop element using Playwright's mouse or drag_to API

    Supported parameters:
    - source_locator: Source element locator to drag
    - target_locator: Target element locator to drop on
    - source_text: Text to identify source element (automatically targets drag handle icon if found)
    - target_text: Text to identify target element (automatically targets drag handle icon if found)
    - timeout: Timeout in milliseconds for element visibility (default: 10000)
    """
    logger.info(">>> Current Step: drag_element")

    source_locator = v.get("source_locator")
    source_text = v.get("source_text")
    target_locator = v.get("target_locator")
    target_text = v.get("target_text")

    dialog = page.locator("[role='dialog']").first
    in_dialog = dialog.count() > 0 and dialog.is_visible()

    def find_item_and_handle(text):
        """Find the '=' drag handle SVG icon on the same row as the given text.
        
        Strategy: locate the text element to get its Y position, then find ALL
        drag-handle SVGs (identified by their characteristic path d='M9.333…')
        and pick the one whose vertical centre is closest to the text element.
        """
        scope = dialog if in_dialog else page

        # Step 1 – locate the text element (used for Y-coordinate reference)
        t_loc = scope.get_by_text(text, exact=True).first
        if t_loc.count() == 0 or not t_loc.is_visible():
            t_loc = scope.get_by_text(text).first

        t_box = t_loc.bounding_box()
        if not t_box:
            logger.warning(f"Could not get bounding box for text '{text}', returning text element")
            return t_loc

        text_cy = t_box["y"] + t_box["height"] / 2
        logger.info(f"Text '{text}' centre Y = {text_cy:.0f}")

        # Step 2 – collect ALL visible '=' drag-handle SVGs in the scope
        #   The handle SVG contains a <path> whose d attribute starts with 'M9.333'
        handles = scope.locator("svg").filter(has=page.locator("path[d*='M9.333']"))
        handle_count = handles.count()
        logger.info(f"Found {handle_count} drag-handle SVG(s) in scope")

        if handle_count == 0:
            logger.warning("No '=' drag handles found, falling back to text element")
            return t_loc

        # Step 3 – pick the handle whose vertical centre is closest to the text
        best_handle = None
        best_distance = float('inf')

        for i in range(handle_count):
            h = handles.nth(i)
            if not h.is_visible():
                continue
            h_box = h.bounding_box()
            if h_box:
                h_cy = h_box["y"] + h_box["height"] / 2
                distance = abs(h_cy - text_cy)
                logger.debug(f"  handle[{i}] centre Y={h_cy:.0f}, distance={distance:.0f}")
                if distance < best_distance:
                    best_distance = distance
                    best_handle = h

        if best_handle is not None and best_distance < 60:
            h_box = best_handle.bounding_box()
            if h_box is not None:
                logger.info(
                    f"Matched drag handle for '{text}' — "
                    f"handle centre=({h_box['x'] + h_box['width']/2:.0f}, {h_box['y'] + h_box['height']/2:.0f}), "
                    f"y-distance={best_distance:.0f}px"
                )
            return best_handle

        logger.warning(f"No nearby drag handle for '{text}' (best distance={best_distance:.0f}px), falling back to text element")
        return t_loc

    if source_locator:
        source_elem = page.locator(source_locator).first
    elif source_text:
        source_elem = find_item_and_handle(source_text)
    else:
        raise ValueError("drag_element: Either 'source_locator' or 'source_text' must be provided")

    if target_locator:
        target_elem = page.locator(target_locator).first
    elif target_text:
        target_elem = find_item_and_handle(target_text)
    else:
        raise ValueError("drag_element: Either 'target_locator' or 'target_text' must be provided")

    timeout = v.get("timeout", 10000)
    delay = v.get("delay", 0)

    # Wait for elements to be ready
    logger.info("Waiting for source element to be ready...")
    source_elem.wait_for(state="attached", timeout=timeout)
    logger.info("Waiting for target element to be ready...")
    target_elem.wait_for(state="attached", timeout=timeout)

    source_box = source_elem.bounding_box()
    target_box = target_elem.bounding_box()

    if source_box and target_box:
        source_x = source_box["x"] + source_box["width"] / 2
        source_y = source_box["y"] + source_box["height"] / 2
        target_x = target_box["x"] + target_box["width"] / 2
        target_y = target_box["y"] + target_box["height"] / 2

        logger.info(f"Mouse drag handle from ({source_x:.0f}, {source_y:.0f}) to ({target_x:.0f}, {target_y:.0f})")

        page.mouse.move(source_x, source_y)
        page.mouse.down()
        page.wait_for_timeout(400)  # Hold to activate drag handle sensor

        steps = 25
        for i in range(1, steps + 1):
            cur_x = source_x + (target_x - source_x) * i / steps
            cur_y = source_y + (target_y - source_y) * i / steps
            page.mouse.move(cur_x, cur_y)
            page.wait_for_timeout(20)

        page.wait_for_timeout(400)  # Hold before release
        page.mouse.up()
        page.wait_for_timeout(1000)
        logger.info("✓ Drag and drop completed successfully via mouse handle")
    else:
        raise RuntimeError("Could not obtain bounding boxes for drag elements")


def drag_and_drop_by_coordinates(page: Page, v: dict):
    """
    Drag and drop using absolute or relative coordinates

    Supported parameters:
    - source_locator: Source element locator (required)
    - start_x: Starting X coordinate (relative to source element)
    - start_y: Starting Y coordinate (relative to source element)
    - end_x: Ending X coordinate (absolute or relative to source)
    - end_y: Ending Y coordinate (absolute or relative to source)
    - absolute: Use absolute coordinates if true (default: false)
    - steps: Number of intermediate move steps for smooth animation (default: 1)

    Usage examples:

    1. Drag with relative coordinates:
       drag_and_drop_by_coordinates:
           source_locator: ".draggable"
           start_x: 100
           start_y: 100
           end_x: 300
           end_y: 300

    2. Drag with absolute coordinates:
       drag_and_drop_by_coordinates:
           source_locator: ".draggable"
           start_x: 100
           start_y: 100
           end_x: 500
           end_y: 500
           absolute: true

    3. Smooth drag animation:
       drag_and_drop_by_coordinates:
           source_locator: ".card"
           start_x: 50
           start_y: 50
           end_x: 200
           end_y: 200
           steps: 10  # 10 intermediate points for smooth animation
    """
    logger.info(">>> Current Step: drag_and_drop_by_coordinates")

    source_locator_str = v.get("source_locator")
    if not source_locator_str:
        raise ValueError("drag_and_drop_by_coordinates: 'source_locator' is required")

    source_elem = page.locator(source_locator_str).first
    source_elem.wait_for(state="attached", timeout=v.get("timeout", 10000))

    source_box = source_elem.bounding_box()
    start_x = v.get("start_x", 0)
    start_y = v.get("start_y", 0)
    end_x = v.get("end_x", 0)
    end_y = v.get("end_y", 0)
    absolute = v.get("absolute", False)
    steps = v.get("steps", 1)

    # Calculate coordinates
    if absolute:
        # Use absolute screen coordinates
        actual_start_x = start_x
        actual_start_y = start_y
        actual_end_x = end_x
        actual_end_y = end_y
    else:
        # Use relative coordinates from source element
        if source_box is None:
            raise RuntimeError("Could not obtain bounding box for drag source element")
        actual_start_x = source_box["x"] + source_box["width"] / 2 + start_x
        actual_start_y = source_box["y"] + source_box["height"] / 2 + start_y
        actual_end_x = source_box["x"] + source_box["width"] / 2 + end_x
        actual_end_y = source_box["y"] + source_box["height"] / 2 + end_y

    logger.info(f"Dragging from ({actual_start_x:.0f}, {actual_start_y:.0f}) to ({actual_end_x:.0f}, {actual_end_y:.0f}) with {steps} steps")

    try:
        # Move to start position
        page.mouse.move(actual_start_x, actual_start_y)
        page.mouse.down()

        # Perform drag with intermediate steps
        if steps > 1:
            for i in range(1, steps + 1):
                ratio = i / steps
                intermediate_x = actual_start_x + (actual_end_x - actual_start_x) * ratio
                intermediate_y = actual_start_y + (actual_end_y - actual_start_y) * ratio
                page.mouse.move(intermediate_x, intermediate_y)
                page.wait_for_timeout(10)  # Small delay for each step
        else:
            # Direct move
            page.mouse.move(actual_end_x, actual_end_y)

        page.mouse.up()
        logger.info("✓ Drag and drop by coordinates completed successfully")

    except Exception as e:
        logger.error(f"✗ Drag and drop by coordinates failed: {e}")
        raise


def swipe_to_element(page: Page, v: dict):
    """
    Swipe/scroll to make an element visible or move it into view

    Supported parameters:
    - locator: Target element locator (required)
    - text: Text to identify target element (alternative to locator)
    - direction: Swipe direction - 'up', 'down', 'left', 'right' (default: 'down')
    - distance: Swipe distance in pixels (default: 500)
    - speed: Swipe speed multiplier (default: 1.0)
    - timeout: Timeout in milliseconds (default: 5000)

    Usage examples:

    1. Swipe to make element visible:
       swipe_to_element:
           locator: "#my-element"
           direction: "down"
           distance: 300

    2. Swipe by text:
       swipe_to_element:
           text: "Load More"
           direction: "up"

    3. Long swipe:
       swipe_to_element:
           locator: ".footer"
           direction: "down"
           distance: 1000
           speed: 2.0
    """
    logger.info(">>> Current Step: swipe_to_element")

    locator_str = v.get("locator")
    text = v.get("text")
    direction = v.get("direction", "down")
    distance = v.get("distance", 500)
    speed = v.get("speed", 1.0)
    timeout = v.get("timeout", 5000)

    # Get target element
    if locator_str:
        target_elem = page.locator(locator_str).first
    elif text:
        target_elem = page.get_by_text(text).first
    else:
        raise ValueError("swipe_to_element: Either 'locator' or 'text' must be provided")

    # Check if element is already visible
    try:
        if target_elem.is_visible(timeout=3000):           # Added timeout: previously no timeout could wait 30s
            logger.info("Element is already visible")
            return
    except:
        pass

    # Calculate swipe coordinates based on direction
    viewport_size = page.viewport_size
    if viewport_size is None:
        raise ValueError("swipe_to_element requires a fixed viewport (no_viewport must be False)")

    # Center of viewport
    center_x = viewport_size["width"] / 2
    center_y = viewport_size["height"] / 2

    # Start and end coordinates
    start_x, start_y = center_x, center_y
    end_x, end_y = center_x, center_y

    if direction == "up":
        start_y = center_y + distance / 2
        end_y = center_y - distance / 2
    elif direction == "down":
        start_y = center_y - distance / 2
        end_y = center_y + distance / 2
    elif direction == "left":
        start_x = center_x + distance / 2
        end_x = center_x - distance / 2
    elif direction == "right":
        start_x = center_x - distance / 2
        end_x = center_x + distance / 2

    logger.info(f"Swiping {direction} by {distance}px (from {start_x:.0f},{start_y:.0f} to {end_x:.0f},{end_y:.0f})")

    try:
        # Perform swipe
        page.mouse.move(start_x, start_y)
        page.mouse.down()
        page.wait_for_timeout(50)  # Small delay to register the down event
        page.mouse.move(end_x, end_y)
        page.mouse.up()

        # Wait for animation
        page.wait_for_timeout(int(500 / speed))

        # Verify element is now visible
        if not target_elem.is_visible(timeout=timeout):
            logger.warning(f"Element still not visible after swipe. Attempting scrollIntoView...")
            target_elem.scroll_into_view_if_needed()

        logger.info("✓ Swipe completed successfully")

    except Exception as e:
        logger.error(f"✗ Swipe failed: {e}")
        raise


def scroll_to_bottom(page: Page, v: dict):
    """
    Scroll to page bottom or to a specific element containing target text.
    Supports: text (target text to scroll to), iterations (scroll steps, default 10),
              delay (ms between scrolls, default 500).
    """
    import time
    target_text = v.get("text", "")
    iterations = v.get("iterations", 10)
    delay_ms = v.get("delay", 500)

    logger.info(f"scroll_to_bottom: target_text='{target_text}', iterations={iterations}")

    if target_text:
        try:
            el = page.get_by_text(target_text, exact=False).first
            el.scroll_into_view_if_needed(timeout=15000)
            logger.info(f"scroll_to_bottom: scrolled to target text '{target_text}'")
            page.wait_for_timeout(300)
            return
        except Exception as e:
            logger.debug(f"scroll_to_bottom: direct scroll failed ({e}), trying iterative scroll...")

    for i in range(iterations):
        page.mouse.wheel(0, 500)
        page.wait_for_timeout(delay_ms)
        scroll_pos = page.evaluate("window.scrollY + window.innerHeight")
        doc_height = page.evaluate("document.documentElement.scrollHeight")
        if scroll_pos >= doc_height - 100:
            logger.info(f"scroll_to_bottom: reached bottom at iteration {i+1}")
            break


def fill_stripe_iframe(page: Page, v: dict):
    """
    Fill Stripe Elements iframe fields using evaluate() for reliable cross-origin access.
    Supports: card_number, expiry, cvc, card_name, zipcode
    
    Features:
    - Waits for Stripe iframe to load with retry mechanism
    - Retries up to 3 times if fields cannot be filled on first attempt
    """
    card_number = v.get("card_number", "")
    expiry = v.get("expiry", "")
    cvc = v.get("cvc", "")
    card_name = v.get("card_name", "")
    zipcode = v.get("zipcode", "")
    timeout_ms = v.get("timeout", 15000)
    max_retries = v.get("max_retries", 3)

    logger.info(f"fill_stripe_iframe: card={bool(card_number)}, expiry={bool(expiry)}, cvc={bool(cvc)}")

    def wait_for_stripe_frames(timeout=10000):
        """Wait for at least one Stripe iframe to be present."""
        import time
        start = time.time()
        while time.time() - start < timeout / 1000:
            for frame in page.frames:
                if frame.url and "stripe" in frame.url.lower():
                    return True
            time.sleep(0.5)
        return False

    def fill_stripe_fields():
        """Attempt to fill Stripe iframe fields. Returns count of filled fields."""
        filled_count = 0
        
        for frame in page.frames:
            try:
                url = frame.url or ""
                if "stripe" not in url.lower():
                    continue
                    
                # Try to fill fields in each frame
                fields_to_fill = [
                    ("cardnumber", card_number),
                    ("exp-date", expiry),
                    ("cvc", cvc),
                ]
                
                for name, value in fields_to_fill:
                    if value:
                        try:
                            # Use focus + type approach instead of fill
                            el = frame.locator(f'input[name="{name}"]')
                            if el.count() > 0:
                                el.click(timeout=3000)
                                el.fill(value, timeout=timeout_ms)
                                logger.info(f"fill_stripe_iframe: filled {name} in frame")
                                filled_count += 1
                        except Exception as e:
                            pass  # Silent failure, try next frame
            except:
                continue
        
        return filled_count

    # Step 1: Wait for Stripe iframe to load
    logger.info("fill_stripe_iframe: waiting for Stripe iframe to load...")
    if not wait_for_stripe_frames(timeout=10000):
        logger.warning("fill_stripe_iframe: Stripe iframe not found after 10s")

    # Step 2: Try to fill fields with retry mechanism
    filled_count = 0
    for attempt in range(1, max_retries + 1):
        logger.info(f"fill_stripe_iframe: attempt {attempt}/{max_retries}")
        filled_count = fill_stripe_fields()
        
        if filled_count > 0:
            logger.info(f"fill_stripe_iframe: successfully filled {filled_count} fields on attempt {attempt}")
            break
        
        if attempt < max_retries:
            logger.info(f"fill_stripe_iframe: retrying in 1 second...")
            page.wait_for_timeout(1000)
    
    if filled_count == 0:
        logger.warning("fill_stripe_iframe: could not fill Stripe fields after all retries, they may require manual input")
        # Take screenshot for debugging
        page.screenshot(path="stripe_iframe_debug.png")

    # Fill main page fields
    if card_name:
        try:
            page.fill('input[name="cardName"]', card_name)
            logger.info(f"fill_stripe_iframe: filled cardName")
        except Exception as e:
            logger.warning(f"fill_stripe_iframe: failed to fill cardName ({e})")

    if zipcode:
        try:
            page.fill('input[name="billingAddress.zipcode"]', zipcode)
            logger.info(f"fill_stripe_iframe: filled zipcode")
        except Exception as e:
            logger.warning(f"fill_stripe_iframe: failed to fill zipcode ({e})")

    # Fill card name and zipcode (these are usually on the main page, not inside the iframe)
    if card_name:
        try:
            page.fill('input[name="cardName"]', card_name)
            logger.info(f"fill_stripe_iframe: filled cardName")
        except Exception as e:
            logger.warning(f"fill_stripe_iframe: failed to fill cardName ({e})")

    if zipcode:
        try:
            page.fill('input[name="billingAddress.zipcode"]', zipcode)
            logger.info(f"fill_stripe_iframe: filled zipcode")
        except Exception as e:
            logger.warning(f"fill_stripe_iframe: failed to fill zipcode ({e})")








def dispatch_click(page: Page, v: dict):
    """Click an element by dispatching DOM events directly on it (Playwright's
    `locator.dispatch_event`) — for widgets whose hit-testing makes a real click impossible.

    [WHY IT EXISTS] A real `locator.click()` needs Playwright's hit-target check to pass, i.e.
    the element must be the top-most element at the click point. SVG/canvas widgets often break
    that: the interactive node is covered by a sibling, or a transparent hit area has
    `pointer-events: none`. Example (verified on release 2026-10-13, venue-map "Select tickets"
    drawer): the table `circle[data-id]` is covered, and its `rect[data-id]` twin is
    `pointer-events: none` — a real click times out or is swallowed, while dispatching the
    event sequence on the circle selects the table ("1 table selected / Total: $100.00").

    Supported params:
      - locator / name : target element (CSS/xpath locator, or `name` -> input[name=...])
      - index          : element index when the locator matches several (default 0)
      - events         : event names to dispatch in order (default the full mouse sequence
                         ["pointerdown", "mousedown", "pointerup", "mouseup", "click"])
      - event_init     : eventInit passed to every dispatched event; the default carries the
                         pointer/mouse payload of a real interaction
                         ({"pointerId": 1, "isPrimary": True, "button": 0, "buttons": 1}).
                         [MEASURED] the venue-map table map ignores the sequence WITHOUT it.
      - timeout        : ms to wait for the element to be ATTACHED (default 10000; no hit-test)
      - expect         : optional condition checked AFTER dispatching; the dispatch is REPEATED
                         until it holds (added 2026-10-16). Shape:
                             expect:
                                 scope: "<container locator>"     # default: whole page
                                 text: "1 item selected"          # substring that must be present
                                 pattern: "Total:\\s*\\$\\d"       # OR a regex over the scope text
                                 timeout: 4000                    # per-attempt poll budget
                         This turns a SILENT no-op into a self-healing step. Motivating case
                         (venue-map table map, 2026-10-16): the drawer can open, and the
                         `rect[data-id]` nodes be attached, BEFORE the SVG map finishes laying
                         out — dispatching on a not-yet-laid-out node is accepted by Playwright
                         yet IGNORED by the widget, so the cart silently stays empty and the
                         NEXT assertion fails far away with a misleading "price not found".
                         With `expect` the click is retried until the drawer really shows it.
      - retries        : extra attempts when `expect` is set (default 3; ignored without expect)
      - retry_delay    : ms between attempts (default 1000)

    YAML usage:
        dispatch_click_select_seat: { locator: "circle[data-id]", index: 0 }
        dispatch_click_map_hint:
            locator: "rect[data-id]"
            index: 0
            expect: { scope: ".MuiDrawer-root:has-text('Select tickets')", text: "1 item selected" }
    """
    import time

    events = v.get("events") or ["pointerdown", "mousedown", "pointerup", "mouseup", "click"]
    init = v.get("event_init") or {"pointerId": 1, "isPrimary": True, "button": 0, "buttons": 1}
    index = v.get("index", 0)
    timeout = v.get("timeout", 10000)
    expect = v.get("expect") or {}
    retries = int(v.get("retries", 3 if expect else 0))
    retry_delay = float(v.get("retry_delay", 1000)) / 1000.0
    expect_timeout = int(expect.get("timeout", 4000)) if expect else 0
    locator = _fill_placeholders(_resolve_locator(v.get("locator")), page)
    name = _fill_placeholders(v.get("name"), page)
    if not locator and not name:
        raise ValueError("dispatch_click: 'locator' or 'name' is required")

    def _target():
        # Re-resolve every attempt: the widget re-renders its nodes as the map lays out.
        if locator:
            return page.locator(locator).nth(index)
        return page.locator(f'input[name="{name}"], [name="{name}"]').nth(index)

    def _expect_ok():
        """(ok, message) — poll the expectation for up to expect_timeout."""
        if not expect:
            return True, "no expectation"
        scope_sel = _fill_placeholders(_resolve_locator(expect.get("scope")), page)
        want_text = _fill_placeholders(expect.get("text"), page)
        want_pat = _fill_placeholders(expect.get("pattern"), page)
        start = time.time()
        last = "no text/pattern declared"
        while True:
            try:
                scope = page.locator(scope_sel).first if scope_sel else None
                if want_text:
                    if scope is not None:
                        hit = scope.locator(f"xpath=.//*[contains(normalize-space(.), {_xpath_literal(want_text)})]")
                    else:
                        hit = page.locator(f"xpath=//*[contains(normalize-space(.), {_xpath_literal(want_text)})]")
                    if hit.count() > 0:
                        return True, f"text {want_text!r} present"
                    last = f"text {want_text!r} absent"
                elif want_pat:
                    body = (scope or page).inner_text()
                    if re.search(want_pat, body):
                        return True, f"pattern {want_pat!r} matched"
                    last = f"pattern {want_pat!r} not matched"
            except Exception as e:
                last = f"expect probe error: {e}"
            if time.time() - start >= expect_timeout / 1000.0:
                return False, last
            time.sleep(0.4)

    last_msg = ""
    for attempt in range(retries + 1):
        try:
            el = _target()
            el.wait_for(state="attached", timeout=timeout)
            for ev in events:
                el.dispatch_event(ev, init)
        except Exception as e:
            # The target may legitimately not be there yet (e.g. the drawer that contains the
            # map is still opening). With retries configured that is just a failed attempt —
            # without this, the very first wait would abort the whole step.
            last_msg = f"{type(e).__name__}: {str(e)[:160]}"
            logger.warning(f"dispatch_click: attempt {attempt + 1}/{retries + 1} could not be sent "
                           f"({last_msg})" + (" — retrying" if attempt < retries else ""))
            if attempt < retries:
                time.sleep(retry_delay)
                continue
            raise
        ok, msg = _expect_ok()
        if ok:
            logger.info(f"dispatch_click: dispatched {list(events)} on {locator or name} "
                        f"(index={index}, attempt {attempt + 1}) -> {msg}")
            return f"dispatched {list(events)}"
        last_msg = msg
        logger.warning(f"dispatch_click: expectation NOT met after attempt {attempt + 1}/{retries + 1} "
                       f"({msg})" + (" — retrying" if attempt < retries else ""))
        if attempt < retries:
            time.sleep(retry_delay)
    raise AssertionError(
        f"dispatch_click: expectation not met after {retries + 1} attempt(s) on "
        f"{locator or name} (index={index}): {last_msg}")


# ---------------------------------------------------------------------------------------------
# Network capture — the native replacement for "monkey-patch a JS global and read it later".
# ---------------------------------------------------------------------------------------------
def _net_bucket(page: Page, name: str) -> list:
    if not hasattr(page, "_net_captures"):
        setattr(page, "_net_captures", {})
    return getattr(page, "_net_captures").setdefault(name, [])


def _query_params(url: str) -> dict:
    """Parse a URL's query string into a flat dict (repeated keys -> list)."""
    from urllib.parse import urlparse, parse_qs
    try:
        qs = parse_qs(urlparse(url).query, keep_blank_values=True)
    except Exception:
        return {}
    out = {}
    for k, vals in qs.items():
        out[k] = vals[0] if len(vals) == 1 else vals
    return out


def _net_values_equal(expected: str, actual) -> bool:
    """Lenient value compare: exact string, or numerically equal within 1e-6.

    Trackers commonly serialize the same money amount differently ("11.98" vs
    "11.980000000000001"), so a strict string compare would be brittle.
    """
    if actual is None:
        return False
    if str(actual) == str(expected):
        return True
    try:
        return abs(float(actual) - float(expected)) < 1e-6
    except (TypeError, ValueError):
        return False


def start_network_capture(page: Page, v: dict):
    """Start recording the page's network requests into a named bucket.

    [WHY IT EXISTS] Verifying that a tracking pixel / analytics beacon fired used to require an
    `execute_js` that monkey-patched the global (`window.fbq = ...`) and read back a JS array.
    The framework had NO network observability at all, so there was no native alternative.
    Recording real requests is both native and strictly stronger: it observes what actually LEFT
    the browser, including events fired from code the test never touched, and it works for any
    tracker (Meta Pixel, Google Analytics, TikTok, ...) with no per-vendor JS.

    The handler is attached to the Page once; each bucket keeps its own url filter, so several
    capture buckets can run at the same time (e.g. "pixel" + "analytics").

    Supported params:
      - name         : bucket name (default "default")
      - url_contains : only record requests whose URL contains this substring (optional —
                       strongly recommended, otherwise every request on the page is buffered)
      - clear        : empty the bucket before starting (default True)

    YAML usage:
        start_network_capture_pixel: { name: "pixel", url_contains: "facebook.com" }
    """
    name = v.get("name", "default")
    url_contains = v.get("url_contains")

    if not hasattr(page, "_net_capture_specs"):
        setattr(page, "_net_capture_specs", {})

        def _on_request(req, _page=page):
            try:
                url = req.url
                for bucket, spec in getattr(_page, "_net_capture_specs", {}).items():
                    filt = spec.get("url_contains")
                    if filt and filt not in url:
                        continue
                    getattr(_page, "_net_captures").setdefault(bucket, []).append({
                        "url": url,
                        "method": req.method,
                        "resource_type": req.resource_type,
                        "params": _query_params(url),
                    })
            except Exception:
                pass

        page.on("request", _on_request)

    getattr(page, "_net_capture_specs")[name] = {"url_contains": url_contains}
    if v.get("clear", True):
        setattr(page, "_net_captures", {**getattr(page, "_net_captures", {})})
        getattr(page, "_net_captures")[name] = []
    logger.info(f"start_network_capture: bucket '{name}' recording "
                f"(url_contains={url_contains!r})")
    return f"capturing into '{name}'"


def verify_network_capture(page: Page, v: dict):
    """Assert that a captured request happened — the native pixel / analytics / API-call check.

    Supported params:
      - name          : bucket name (default "default")
      - url_contains  : additional substring the request URL must contain
      - params        : dict of query-param -> expected value; every pair must match. Values are
                        compared exactly, or numerically when both are numbers (see
                        _net_values_equal).
      - regex         : regex that must match somewhere in the FULL request URL. Use this when a
                        tracker's parameter ENCODING is not worth depending on (Meta sends
                        `cd[value]=11.98` on some builds and `cd%5Bvalue%5D=11.98` on others, but
                        the bare `11.98` is present either way).
      - min_count     : how many matching requests are required (default 1)
      - timeout       : ms to keep re-checking, so a beacon fired asynchronously is not missed
                        (default 5000)
      - save_as / global : publish the matching URLs (newline-joined) as a variable

    On failure the error lists what WAS captured, which makes a wrong expectation obvious.

    YAML usage:
        verify_pixel_addtocart:
            name: "pixel"
            url_contains: "facebook.com/tr"
            params: { ev: "AddToCart" }
            regex: "11\\.98"
            timeout: 10000
    """
    import time

    name = v.get("name", "default")
    url_contains = v.get("url_contains")
    params = v.get("params") or {}
    regex = v.get("regex")
    min_count = int(v.get("min_count", 1))
    timeout = int(v.get("timeout", 5000))
    if regex:
        regex = _fill_placeholders(str(regex), page)
    deadline = time.time() + timeout / 1000.0

    def _matches(entry):
        url = entry.get("url", "")
        if url_contains and url_contains not in url:
            return False
        for k, expected in params.items():
            exp = _fill_placeholders(str(expected), page)
            if not _net_values_equal(exp, entry.get("params", {}).get(k)):
                return False
        if regex and not re.search(regex, url):
            return False
        return True

    last_pool = []
    while True:
        pool = list(getattr(page, "_net_captures", {}).get(name, []))
        last_pool = pool
        hits = [e["url"] for e in pool if _matches(e)]
        if len(hits) >= min_count:
            logger.info(f"verify_network_capture: {len(hits)} matching request(s) in bucket "
                        f"'{name}': {hits[:3]}")
            if v.get("save_as"):
                _save_context_value(page, v["save_as"], "\n".join(hits), bool(v.get("global")))
            return hits[:min_count]
        if time.time() >= deadline:
            break
        time.sleep(0.3)

    sample = "\n    ".join(u for u in (e.get("url", "") for e in last_pool[-8:])) or "(nothing captured)"
    raise AssertionError(
        f"verify_network_capture: no request in bucket '{name}' matched "
        f"url_contains={url_contains!r} params={params!r} regex={regex!r} within {timeout}ms "
        f"(captured {len(last_pool)} request(s)); last captured:\n    {sample}")


def hover(page: Page, v: dict):
    """Hover an element with Playwright's native `locator.hover()`.

    [WHY IT EXISTS] The framework had NO hover action, so any widget that reveals a SUBMENU on
    hover had to be driven with an `execute_js` that dispatched synthetic
    `mouseenter`/`mouseover` events. Motivating case (RTE "Insert" dropdown,
    Post_content.yaml): the dropdown's "Event" item opens the "Insert all merch" submenu only
    on hover, so a click would activate it instead of revealing the submenu.

    Supported params:
      - locator        : element locator (CSS/xpath)
      - role / name     : alternative addressing via `get_by_role` / `get_by_text`
      - exact          : exact text match for `name` (default False)
      - index          : element index when the locator matches several (default 0)
      - timeout        : ms to wait for the element + for the hover (default 10000)
      - force          : bypass Playwright's actionability checks (default False)
      - expect         : optional condition checked AFTER hovering; the hover is REPEATED until
                         it holds — same shape as `dispatch_click.expect`:
                             expect:
                                 scope: "<container locator>"   # default: whole page
                                 text: "Insert all merch"       # substring that must appear
                                 pattern: "Insert all merch"    # OR a regex over the scope text
                                 timeout: 4000
                                 retries: 3                     # extra attempts
                                 retry_delay: 800               # ms between attempts
                         Turns "the submenu did not open" from a confusing downstream failure
                         into a self-healing step.

    YAML usage:
        hover_insert_event_item: { role: "menuitem", name: "Event", exact: true }
        hover_insert_event_item:
            role: "menuitem"
            name: "Event"
            exact: true
            expect: { text: "Insert all merch" }
    """
    import time

    locator = _fill_placeholders(_resolve_locator(v.get("locator")), page)
    role = v.get("role")
    name = _fill_placeholders(v.get("name") or v.get("text"), page)
    exact = bool(v.get("exact", False))
    index = v.get("index", 0)
    timeout = int(v.get("timeout", 10000))
    force = bool(v.get("force", False))
    expect = v.get("expect") or {}
    retries = int(expect.get("retries", 3)) if expect else 0
    retry_delay = float(expect.get("retry_delay", 800)) / 1000.0
    expect_timeout = int(expect.get("timeout", 4000)) if expect else 0

    if not locator and not role and not name:
        raise ValueError("hover: one of 'locator', 'role' or 'name' is required")

    def _target():
        if locator:
            return page.locator(locator).nth(index)
        if role:
            return page.get_by_role(role, name=name, exact=exact).nth(index)
        return page.get_by_text(name, exact=exact).nth(index)

    def _expect_ok():
        """(ok, message) — poll the expectation for up to expect_timeout."""
        if not expect:
            return True, "no expectation"
        scope_sel = _fill_placeholders(_resolve_locator(expect.get("scope")), page)
        want_text = _fill_placeholders(expect.get("text"), page)
        want_pat = _fill_placeholders(expect.get("pattern"), page)
        start = time.time()
        last = "no text/pattern declared"
        while True:
            try:
                scope = page.locator(scope_sel).first if scope_sel else None
                if want_text:
                    if scope is not None:
                        hit = scope.locator(f"xpath=.//*[contains(normalize-space(.), {_xpath_literal(want_text)})]")
                    else:
                        hit = page.locator(f"xpath=//*[contains(normalize-space(.), {_xpath_literal(want_text)})]")
                    if hit.count() > 0:
                        return True, f"text {want_text!r} present"
                    last = f"text {want_text!r} absent"
                elif want_pat:
                    body = (scope or page).inner_text()
                    if re.search(want_pat, body):
                        return True, f"pattern {want_pat!r} matched"
                    last = f"pattern {want_pat!r} not matched"
            except Exception as e:
                last = f"expect probe error: {e}"
            if time.time() - start >= expect_timeout / 1000.0:
                return False, last
            time.sleep(0.4)

    last_msg = ""
    for attempt in range(retries + 1):
        try:
            el = _target()
            el.wait_for(state="visible", timeout=timeout)
            el.scroll_into_view_if_needed()
            el.hover(timeout=timeout, force=force)
        except Exception as e:
            last_msg = f"{type(e).__name__}: {str(e)[:160]}"
            logger.warning(f"hover: attempt {attempt + 1}/{retries + 1} failed to hover "
                           f"{locator or role or name} ({last_msg})"
                           + (" — retrying" if attempt < retries else ""))
            if attempt < retries:
                time.sleep(retry_delay)
                continue
            raise
        ok, msg = _expect_ok()
        if ok:
            logger.info(f"hover: hovered {locator or role or name} (index={index}, "
                        f"attempt {attempt + 1}) -> {msg}")
            return f"hovered {locator or role or name}"
        last_msg = msg
        logger.warning(f"hover: expectation NOT met after attempt {attempt + 1}/{retries + 1} "
                       f"({msg})" + (" — retrying" if attempt < retries else ""))
        if attempt < retries:
            time.sleep(retry_delay)
    raise AssertionError(
        f"hover: expectation not met after {retries + 1} attempt(s) on "
        f"{locator or role or name} (index={index}): {last_msg}")


def click_open_new_tab(page: Page, v: dict):
    """Click an element that opens a NEW BROWSER TAB, then assert where that tab lands.

    [WHY IT EXISTS] This framework had no popup / new-tab handling at all. `smart_click` +
    `wait_for_url` only work when the link navigates the CURRENT page; when the target is
    `target="_blank"` (or calls `window.open`) the current page never changes, so `wait_for_url`
    times out. The old workaround was an `execute_js` that rewrote `target` to `_self` and
    monkey-patched `window.open` to force a same-tab jump — exactly the JS we no longer allow.
    This action instead uses Playwright's native `context.expect_page()`, which IS the supported
    way to catch a popup, so the same coverage is kept with zero JS.

    Motivating case (verified on release 2026-10-16, tdc_fee_breakdown_guest_purchase_ui.yaml):
    the order confirmation page's "View Tickets" link opens https://mpvsb.tickets.com/ in a new
    tab.

    Supported params:
      - locator / name   : target element (locator, or `name` -> input/[name=...])
      - index            : element index when the locator matches several (default 0)
      - url              : glob (`*` allowed) the NEW TAB's URL must match, like `wait_for_url`.
                           Optional, but usually the whole point of the step.
      - timeout          : ms budget for BOTH catching the popup and matching its URL (default 30000)
      - click_timeout    : ms budget for waiting for the element + clicking it
                           (default min(timeout, 15000))
      - close            : close the new tab afterwards (default True — the suite continues on the
                           original page)
      - save_as / global : optionally publish the resolved new-tab URL as a variable

    YAML usage:
        session_guest__click_open_new_tab_view_tickets:
            locator: "xpath=(//*[self::a or self::button or @role='button'][contains(normalize-space(.), 'View Tickets')])[1]"
            url: "*mpvsb.tickets.com*"
            timeout: 30000
    """
    import time
    from fnmatch import fnmatch

    locator = _fill_placeholders(_resolve_locator(v.get("locator")), page)
    name = _fill_placeholders(v.get("name"), page)
    if not locator and not name:
        raise ValueError("click_open_new_tab: 'locator' or 'name' is required")
    index = v.get("index", 0)
    timeout = int(v.get("timeout", 30000))
    click_timeout = int(v.get("click_timeout", min(timeout, 15000)))
    url = v.get("url") or v.get("expected_url")
    if url is not None:
        url = _fill_placeholders(url, page)
    close_after = bool(v.get("close", True))

    target = (
        page.locator(locator).nth(index)
        if locator
        else page.locator(f'input[name="{name}"], [name="{name}"]').nth(index)
    )
    target.wait_for(state="visible", timeout=click_timeout)

    logger.info(f"click_open_new_tab: clicking {locator or name} (index={index}); "
                f"expecting a new tab matching {url!r}")
    with page.context.expect_page(timeout=click_timeout) as page_info:
        target.click(timeout=click_timeout)
    new_page = page_info.value
    try:
        new_page.wait_for_load_state("domcontentloaded", timeout=timeout)
    except Exception as e:
        logger.warning(f"click_open_new_tab: new tab load state not reached within {timeout}ms: {e}")

    if url:
        deadline = time.time() + timeout / 1000.0
        while True:
            got = new_page.url or ""
            if fnmatch(got, url):
                logger.info(f"click_open_new_tab: new tab landed on {got!r} (matches {url!r})")
                break
            if time.time() >= deadline:
                raise AssertionError(
                    f"click_open_new_tab: new tab URL {got!r} did not match {url!r} within {timeout}ms")
            new_page.wait_for_timeout(300)
    else:
        got = new_page.url or ""
        logger.info(f"click_open_new_tab: new tab opened at {got!r} (no url pattern asserted)")

    if v.get("save_as"):
        _save_context_value(page, v["save_as"], got, bool(v.get("global")))

    if close_after:
        try:
            new_page.close()
        except Exception as e:
            logger.warning(f"click_open_new_tab: could not close the new tab: {e}")
    return got


def smart_click_optional(page: Page, v: dict):
    """
    Optional click — silently skips if the element does not exist, no error raised.
    Designed for modals/tooltips that may or may not appear.

    YAML usage:
        R_click_done: { role: 'button', name: 'Done' }

    Difference from smart_click + optional: true:
    - smart_click's optional only applies on the target_locator path
    - smart_click_optional supports optional skipping on ALL location strategies
    """
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_locator = _resolve_locator(target_locator)
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    target_index = v.get("index", 0)
    target_test_id = v.get("test_id")
    force = v.get("force", False)
    timeout = v.get("timeout", 5000)

    def _try_click(el, desc):
        try:
            el.click(force=force, timeout=timeout)
            logger.info(f"smart_click_optional: clicked '{desc}'")
            return True
        except Exception as e:
            logger.debug(f"smart_click_optional: click failed for '{desc}' ({e})")
            return False

    # Find visible modal/tooltip scopes (iterate in reverse, prioritise newest modal)
    # Supports: dialog, modal, tooltip, popover and other floating layers
    modal_selector = "div[role='dialog'], .MuiDialog-root, .MuiModal-root, .MuiTooltip-popper, .MuiPopper-root, [role='tooltip'], [role='popover'], .MuiAutocomplete-popper, .MuiMenu-paper"
    raw_modals = page.locator(modal_selector).all()
    visible_modals = []
    for m in raw_modals[:10]:
        try:
            if m.is_visible():
                visible_modals.append(m)
        except:
            pass

    def _find_and_click_in_scope(scope, desc_prefix=""):
        """Find and click element within the given scope"""
        desc = f"{desc_prefix}{target_role}:{target_name}" if target_role and target_name else (target_name or target_locator or f"test_id={target_test_id}")

        # 1. Test ID
        if target_test_id:
            try:
                el = scope.get_by_test_id(target_test_id).nth(target_index)
                if _try_click(el, f"test_id={target_test_id}"):
                    return True
            except:
                pass

        # 2. Locator
        if target_locator:
            try:
                if target_locator.startswith("/") or target_locator.startswith("xpath="):
                    xpath_locator = target_locator if target_locator.startswith("xpath=") else f"xpath={target_locator}"
                    el = page.locator(xpath_locator).nth(target_index)
                else:
                    el = page.locator(target_locator).nth(target_index)
                if target_name:
                    el = el.get_by_text(target_name, exact=target_exact)
                if _try_click(el, target_locator):
                    return True
            except Exception as e:
                logger.debug(f"smart_click_optional: locator failed ({e})")

        # 3. Role + name (most common)
        if target_role and target_name:
            try:
                el = scope.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
                if _try_click(el, f"{target_role}:{target_name}"):
                    return True
            except:
                pass

        # 4. Text only
        if target_name and not target_role:
            try:
                el = scope.get_by_text(target_name, exact=target_exact).nth(target_index)
                if _try_click(el, f"text={target_name}"):
                    return True
            except:
                pass

        return False

    # Search strategy: try modals first (newest first), then page level
    # Rationale: modals typically contain the element the user is currently interacting with

    # 1. Try all visible modals first (newest modal first, reverse order)
    for modal in reversed(visible_modals):
        if _find_and_click_in_scope(modal, f"modal[{visible_modals.index(modal)}]:"):
            return

    # 2. Finally try at page level (handles cases with no modal)
    if _find_and_click_in_scope(page, "page:"):
        return

    # Element not found — silent skip
    logger.info(f"smart_click_optional: element not found '{target_name or target_locator}', skipping.")


def smart_click_retry(page: Page, v: dict):
    """
    Stable click with retry — use when the element is guaranteed to exist but clicks are flaky.

    Difference from smart_click_optional:
    - smart_click_optional: skips if element not found (for elements that may not exist)
    - smart_click_retry: element is guaranteed present, auto-retries on failure (for reliably present elements)

    YAML usage:
        smart_click_retry_publish: { role: 'button', name: 'Publish', retry: 3, delay: 500 }

    Additional parameters:
    - retry: number of retry attempts, default 3
    - delay: delay between retries (ms), default 500
    """
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_locator = _resolve_locator(target_locator)
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    target_index = v.get("index", 0)
    target_test_id = v.get("test_id")
    force = v.get("force", False)
    timeout = v.get("timeout", 5000)
    retry_count = v.get("retry", 3)
    delay_ms = v.get("delay", 500)

    # Find visible modal/tooltip scopes (iterate in reverse, prioritise newest modal)
    # Supports: dialog, modal, tooltip, popover and other floating layers
    modal_selector = "div[role='dialog'], .MuiDialog-root, .MuiModal-root, .MuiTooltip-popper, .MuiPopper-root, [role='tooltip'], [role='popover'], .MuiAutocomplete-popper, .MuiMenu-paper"
    raw_modals = page.locator(modal_selector).all()
    visible_modals = []
    for m in raw_modals[:10]:
        try:
            if m.is_visible():
                visible_modals.append(m)
        except:
            pass

    def _find_element_in_scope(scope):
        """Find element within the given scope"""
        # 1. Test ID
        if target_test_id:
            try:
                el = scope.get_by_test_id(target_test_id).nth(target_index)
                if el.is_visible(timeout=timeout):
                    return el
            except:
                pass

        # 2. Locator
        if target_locator:
            try:
                if target_locator.startswith("/") or target_locator.startswith("xpath="):
                    xpath_locator = target_locator if target_locator.startswith("xpath=") else f"xpath={target_locator}"
                    el = page.locator(xpath_locator).nth(target_index)
                else:
                    el = page.locator(target_locator).nth(target_index)
                if target_name:
                    el = el.get_by_text(target_name, exact=target_exact)
                if el.is_visible(timeout=timeout):
                    return el
            except:
                pass

        # 3. Role + name (most common)
        if target_role and target_name:
            try:
                el = scope.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
                if el.is_visible(timeout=timeout):
                    return el
            except:
                pass

        # 4. Text only
        if target_name and not target_role:
            try:
                el = scope.get_by_text(target_name, exact=target_exact).nth(target_index)
                if el.is_visible(timeout=timeout):
                    return el
            except:
                pass

        return None

    def _find_element():
        """Search all visible modals + page for the element"""
        # 1. Try all visible modals first (newest modal first, reverse order)
        for modal in reversed(visible_modals):
            el = _find_element_in_scope(modal)
            if el is not None:
                return el
        # 2. Finally try at page level
        return _find_element_in_scope(page)

    desc = f"{target_role}:{target_name}" if target_role and target_name else (target_name or target_locator or f"test_id={target_test_id}")

    for attempt in range(1, retry_count + 1):
        try:
            el = _find_element()
            if el is None:
                if attempt < retry_count:
                    logger.debug(f"smart_click_retry: attempt {attempt}/{retry_count} - element not visible, waiting {delay_ms}ms...")
                    page.wait_for_timeout(delay_ms)
                    continue
                else:
                    logger.warning(f"smart_click_retry: element '{desc}' not found after {retry_count} attempts")
                    raise Exception(f"Element not found: {desc}")

            # Wait for element animation to complete before clicking
            page.wait_for_timeout(200)

            # Click (Playwright's click already waits for the element to be clickable)
            el.click(force=force, timeout=timeout)
            logger.info(f"smart_click_retry: successfully clicked '{desc}' (attempt {attempt}/{retry_count})")
            return

        except Exception as e:
            if attempt < retry_count:
                logger.debug(f"smart_click_retry: attempt {attempt}/{retry_count} failed for '{desc}': {e}, retrying...")
                page.wait_for_timeout(delay_ms)
            else:
                logger.error(f"smart_click_retry: all {retry_count} attempts failed for '{desc}': {e}")
                raise


def select_event_with_sellable_product(page: Page, v: dict):
    """Open the first badge-tagged event (on the events list) that still has a SELLABLE product.

    WHY (2026-10-16): the events list can carry SEVERAL events with the same provider badge, and
    the first one may have every product "Sold out" (measured on release: the TDC badge is on both
    "Parking - League Championship Series TDC" — 3/3 sold out — and "League Championship Series
    TDC" — 28 sellable). The old seed hard-picked the first badge event (`extract_value` on
    `//*[normalize-space(.)='TDC' and not(*)]/parent::*//p`) and then clicked it by name, so it died
    with `extract_value: could not read 'xpath=//div[@data-testid='mui-stack']
    [...][not(contains(., 'Sold out'))]'` the moment that event sold out.

    This action walks the badge events in list order: open one, look for a sellable product card,
    and when the event has none, close it with the header X (`button[aria-label='Close']`, the
    top-left close icon `data-testid='komi-header-icon-btn'`) to return to the events list and try
    the NEXT badge event. It leaves the page ON the chosen event with `open_tab` selected, and
    publishes the chosen event's NAME.

    Params:
      - badge        : badge text matched as a LEAF element, e.g. "TDC" / "AXS" (required)
      - product_cards: locator of a SELLABLE product card; default = the standard
                       mui-stack + enhance-button card whose text does NOT contain "Sold out"
      - open_tab     : optional tab to click after entering the event ("Tickets & Merch")
      - close        : header close (X) locator; default `xpath=//button[@aria-label='Close']`
      - list_url     : optional URL ({{var}}-backfilled) to (re)load between attempts
      - max_events   : how many badge events to try (default 4)
      - settle       : ms to let the event page / the list render (default 3000)
      - save_as      : workflow-context key receiving the chosen event NAME
      - global       : also publish to the cross-case store
      - required     : raise when no badge event has a sellable product (default true)
      - timeout      : ms budget for entering the event page (default 15000)

    YAML usage:
        select_event_with_sellable_product_tdc:
            badge: "TDC"
            open_tab: "Tickets & Merch"
            save_as: "event_tdc"
            global: true
    """
    import time as _time

    badge = _fill_placeholders(v.get("badge") or v.get("tag"), page)
    if not badge:
        raise ValueError("select_event_with_sellable_product: 'badge' is required")
    card_locator = _fill_placeholders(
        _resolve_locator(v.get("product_cards"))
        or "xpath=//div[@data-testid='mui-stack'][.//button[@data-testid='enhance-button']]"
           "[not(contains(., 'Sold out'))]",
        page,
    )
    open_tab = _fill_placeholders(v.get("open_tab") or v.get("tab"), page)
    close_locator = _fill_placeholders(
        _resolve_locator(v.get("close")) or "xpath=//button[@aria-label='Close']", page
    )
    list_url = _fill_placeholders(v.get("list_url"), page)
    max_events = int(v.get("max_events", 4))
    timeout = v.get("timeout", 15000)
    settle = v.get("settle", 3000)
    save_as = v.get("save_as")
    is_global = bool(v.get("global", False))
    required = bool(v.get("required", True))

    badge_leaf = f"//*[normalize-space(.)={_xpath_literal(badge)} and not(*)]"

    def _badge_row(index):
        return page.locator(f"xpath=({badge_leaf}/parent::*)[{index}]")

    # Make sure the badge list is rendered before we start walking it.
    deadline = _time.time() + timeout / 1000.0
    while _badge_row(1).count() == 0 and _time.time() < deadline:
        page.wait_for_timeout(500)
    if _badge_row(1).count() == 0:
        if list_url:
            page.goto(list_url, wait_until="domcontentloaded")
            page.wait_for_timeout(settle)
            deadline = _time.time() + timeout / 1000.0
            while _badge_row(1).count() == 0 and _time.time() < deadline:
                page.wait_for_timeout(500)

    tried = []
    for index in range(1, max_events + 1):
        row = _badge_row(index)
        if row.count() == 0:
            break

        name = ""
        try:
            name = (row.first.locator("xpath=.//p").first.inner_text() or "").strip()
        except Exception:
            pass
        logger.info(
            f"select_event_with_sellable_product: trying {badge} event #{index}"
            f"{' ' + repr(name) if name else ''}"
        )

        # Enter the event. The card name <p> is what the existing cases click successfully;
        # fall back to the row itself, then to a force-click.
        target = row.first.locator("xpath=.//p").first
        if target.count() == 0:
            target = row.first
        try:
            target.click(timeout=8000)
        except Exception:
            target.click(force=True, timeout=5000)

        try:
            page.wait_for_url(re.compile(r"/events/[^/]+/view"), timeout=timeout)
        except Exception:
            pass
        page.wait_for_timeout(settle)

        if open_tab:
            try:
                page.get_by_role("tab", name=open_tab).first.click(timeout=8000)
            except Exception as e:
                logger.debug(f"select_event_with_sellable_product: tab '{open_tab}' not clicked: {e}")
            page.wait_for_timeout(2500)

        sellable = page.locator(card_locator).count()
        if sellable > 0:
            logger.info(
                f"select_event_with_sellable_product: {badge} event #{index}"
                f"{' ' + repr(name) if name else ''} has {sellable} sellable product(s) -> selected"
            )
            if save_as:
                _save_context_value(page, save_as, name, is_global)
            return

        # Every product of this event is sold out -> close it (header X) and try the next one.
        logger.info(
            f"select_event_with_sellable_product: {badge} event #{index}"
            f"{' ' + repr(name) if name else ''} has NO sellable product (all 'Sold out') -> "
            f"closing it and looking for the next {badge} event"
        )
        tried.append(name or f"#{index}")
        try:
            page.locator(close_locator).first.click(timeout=8000)
        except Exception:
            page.locator(close_locator).first.click(force=True, timeout=5000)
        if list_url:
            page.goto(list_url, wait_until="domcontentloaded")
        page.wait_for_timeout(settle)
        # wait for the list to render again so the next badge row can be resolved
        deadline = _time.time() + timeout / 1000.0
        while _badge_row(index + 1).count() == 0 and _time.time() < deadline:
            page.wait_for_timeout(500)

    msg = (
        f"select_event_with_sellable_product: no {badge} event with a sellable product found "
        f"among the first {max_events} badge event(s) (tried: {tried})"
    )
    if required:
        page.screenshot(path=f"fail_select_{badge}_event.png")
        raise RuntimeError(msg)
    logger.warning(msg)
    if save_as:
        _save_context_value(page, save_as, "", is_global)


def handle_modal(page: Page, v: dict):
    """
    Handle various types of modals, dialogs, and popups by clicking buttons within them.
    Supports multiple modal identification methods and button selection strategies.

    Supported parameters:
    - modal_identifiers: List of modal identification methods (tried in order)
      - selector: CSS/XPath selector
      - role: ARIA role (dialog, alertdialog, etc.)
      - text: Text content within modal
      - class: CSS class name
      - test_id: data-testid attribute
    - button_selectors: List of button selection methods (tried in order)
      - selector: CSS/XPath selector
      - role: ARIA role (button)
      - text: Button text
      - test_id: data-testid attribute
      - index: Button index (if multiple)
    - timeout: Timeout in milliseconds for modal detection (default: 5000)
    - wait_before_click: Delay before clicking button (default: 1000)
    - close_all: Close all matching modals (default: false)
    - max_attempts: Maximum number of attempts to find modal (default: 3)
    - ignore_if_not_found: Don't fail if modal not found (default: false)

    Usage examples:

    1. Simple modal with text button:
       handle_modal:
           modal_identifiers:
               - role: "dialog"
           button_selectors:
               - text: "Got it"

    2. Multiple modal types and buttons:
       handle_modal:
           modal_identifiers:
               - class: "MuiDialog-root"
               - role: "alertdialog"
               - selector: "[role='dialog']"
           button_selectors:
               - text: "Accept"
               - text: "Agree"
               - role: "button", name: "Close"

    3. Modal with test_id:
       handle_modal:
           modal_identifiers:
               - test_id: "cookie-banner"
           button_selectors:
               - test_id: "accept-button"

    4. Close all matching modals:
       handle_modal:
           modal_identifiers:
               - class: "notification-toast"
           button_selectors:
               - selector: ".close-button"
           close_all: true

    5. Ignore if modal not found:
       handle_modal:
           modal_identifiers:
               - class: "promo-banner"
           button_selectors:
               - text: "Close"
           ignore_if_not_found: true
    """
    logger.info(">>> Current Step: handle_modal")

    modal_identifiers = v.get("modal_identifiers", [])
    button_selectors = v.get("button_selectors", [])
    timeout = v.get("timeout", 5000)
    wait_before_click = v.get("wait_before_click", 1000)
    close_all = v.get("close_all", False)
    max_attempts = v.get("max_attempts", 4)
    ignore_if_not_found = v.get("ignore_if_not_found", False)

    if not modal_identifiers:
        raise ValueError("handle_modal: 'modal_identifiers' must be provided")
    if not button_selectors:
        raise ValueError("handle_modal: 'button_selectors' must be provided")

    logger.info(f"Looking for modal with {len(modal_identifiers)} identification methods")
    logger.info(f"Button selectors to try: {len(button_selectors)}")

    modal_found = False
    modal_locator = None

    # Try each modal identifier
    for attempt in range(max_attempts):
        logger.info(f"Modal detection attempt {attempt + 1}/{max_attempts}")

        for modal_id in modal_identifiers:
            try:
                # Build modal locator based on identifier type
                if "selector" in modal_id:
                    modal_locator = page.locator(modal_id["selector"]).first
                elif "role" in modal_id:
                    role = modal_id["role"]
                    name = modal_id.get("name")
                    if name:
                        modal_locator = page.get_by_role(role, name=name).first
                    else:
                        modal_locator = page.get_by_role(role).first
                elif "text" in modal_id:
                    modal_locator = page.get_by_text(modal_id["text"], exact=False).first
                elif "class" in modal_id:
                    modal_locator = page.locator(f".{modal_id['class']}").first
                elif "test_id" in modal_id:
                    modal_locator = page.locator(f"[data-testid='{modal_id['test_id']}']").first
                else:
                    logger.warning(f"Unknown modal identifier type: {modal_id}")
                    continue

                # Check if modal is visible
                visibility_timeout = v.get("visibility_timeout", 100)
                if modal_locator.is_visible(timeout=visibility_timeout):
                    logger.info(f"✓ Modal found using: {modal_id}")
                    modal_found = True
                    break
                else:
                    logger.debug(f"Modal not visible using: {modal_id}")

            except Exception as e:
                logger.debug(f"Error checking modal with {modal_id}: {e}")
                continue

        if modal_found:
            break

        # Wait before retry
        if attempt < max_attempts - 1:
            page.wait_for_timeout(500)

    if not modal_found:
        if ignore_if_not_found:
            logger.info("Modal not found, but ignoring as per configuration")
            return False
        else:
            logger.error(f"Modal not found after {max_attempts} attempts")
            page.screenshot(path="modal_not_found.png")
            raise AssertionError("Modal not found")

    # Click buttons in modal
    buttons_clicked = 0
    if close_all:
        # Close all matching buttons
        logger.info("Closing all matching buttons in modal")
        for button_id in button_selectors:
            try:
                button = find_button_in_modal(page, modal_locator, button_id)
                if button and button.is_visible():
                    button.click()
                    buttons_clicked += 1
                    page.wait_for_timeout(wait_before_click)
            except Exception as e:
                logger.debug(f"Error clicking button {button_id}: {e}")
    else:
        # Click first matching button
        logger.info("Clicking first matching button in modal")
        for button_id in button_selectors:
            try:
                button = find_button_in_modal(page, modal_locator, button_id)
                if button and button.is_visible():
                    logger.info(f"Clicking button: {button_id}")
                    page.wait_for_timeout(wait_before_click)
                    button.click(timeout=1000)
                    buttons_clicked += 1
                    break
            except Exception as e:
                logger.debug(f"Error clicking button {button_id}: {e}")
                continue

    if buttons_clicked > 0:
        logger.info(f"✓ Modal handled successfully, clicked {buttons_clicked} button(s)")
        return True
    else:
        logger.warning("⚠ No buttons were clicked in modal")
        if not ignore_if_not_found:
            page.screenshot(path="modal_button_not_found.png")
            raise AssertionError("No clickable buttons found in modal")
        return False


def find_button_in_modal(page: Page, modal_locator, button_id):
    """
    Helper function to find a button within a modal using various selection methods
    """
    try:
        if "selector" in button_id:
            return modal_locator.locator(button_id["selector"]).last
        elif "role" in button_id:
            role = button_id["role"]
            name = button_id.get("name")
            index = button_id.get("index", -1)
            if name:
                return modal_locator.get_by_role(role, name=name, exact=button_id.get("exact", False)).nth(index)
            else:
                return modal_locator.get_by_role(role).nth(index)
        elif "text" in button_id:
            text = button_id["text"]
            exact = button_id.get("exact", False)
            index = button_id.get("index", 0)
            return modal_locator.get_by_text(text, exact=exact).nth(index)
        elif "test_id" in button_id:
            return modal_locator.locator(f"[data-testid='{button_id['test_id']}']").last
        else:
            logger.warning(f"Unknown button selector type: {button_id}")
            return None
    except Exception as e:
        logger.debug(f"Error finding button with {button_id}: {e}")
        return None


def auto_handle_modals(page: Page, v: dict):
    """
    Automatically detect and handle common modals that appear after page navigation.
    This is a convenience wrapper for handle_modal with pre-configured common modal patterns.

    Supported parameters:
    - timeout: Timeout in milliseconds (default: 3000)
    - wait_before_click: Delay before clicking (default: 300)
    - ignore_if_not_found: Always succeed even if no modal found (default: true)
    - max_iterations: Maximum times to iterate through modal patterns (default: 5)
                         Use this to handle multi-step modals (e.g., tours with multiple steps)

    Usage examples:

    1. Auto-handle after page load:
       auto_handle_modals:
           timeout: 3000

    2. Handle multi-step modals (tours):
       auto_handle_modals:
           timeout: 5000
           max_iterations: 10  # Handle up to 10 modal steps

    Common modals detected:
    - Cookie consent banners
    - Welcome/guide tours (multi-step)
    - Notification toasts
    - Update prompts
    - Announcement banners
    """
    logger.info(">>> Current Step: auto_handle_modals")

    timeout = v.get("timeout", 3000)
    ignore_if_not_found = v.get("ignore_if_not_found", True)
    max_iterations = v.get("max_iterations", 5)

    # Early exit: skip if no modal/popup elements present on page
    # MuiPopover-paper: visible only when a popover/modal is open
    # MuiBackdrop-root: visible only when a backdrop overlay exists
    has_popover = page.locator(".MuiPopover-paper").count() > 0
    has_backdrop = page.locator(".MuiBackdrop-root").count() > 0
    if not has_popover and not has_backdrop:
        logger.info("No modal/popup elements found (MuiPopover-paper / MuiBackdrop-root), skipping auto_handle_modals")
        return

    # Common modal patterns
    common_modals = [
        # Cookie banners
        {
            "modal_identifiers": [
                {"class": "cookie-banner"},
                {"text": "Customize Your Cookie Choices"},
                {"selector": "div[aria-describedby='cm__desc']"},
            ],
            "button_selectors": [
                {"text": "Accept all"},
                {"text": "Agree"},
                {"text": "Got it"},
                {"role": "button", "name": "Accept all"},
                {"test_id": "accept-cookies"},
                {"selector": "div[aria-describedby='cm__desc'] button[data-role='all']"},
            ]
        },
        # Welcome/guide tours (multi-step modals)
        {
            "modal_identifiers": [
                {"role": "presentation", "name": "Customize your shop"},
                {"role": "presentation", "name": "Add new module"},
                {"role": "presentation", "name": "Preview your shop"},
                {"role": "presentation", "name": "Introduce content tabs"},
                {"role": "presentation", "name": "Rearrange modules"},
                {"role": "presentation", "name": "You've added products — great start!"},
                {"class": "MuiPopover-paper"},
                {"selector": "div[role='presentation'] .MuiPopover-paper"},
            ],
            "button_selectors": [
                {"role": "button", "name": "Next"},
                {"role": "button","name": "Skip"},
                {"role": "button","name": "Got it"},
                {"role": "button","name": "Close"},
                {"role": "button","name": "Finish"},
                {"test_id": "button"},
                {"selector": "div[role='presentation'] button[data-track-location='Dialog']"},
                {"selector": "div[role='presentation'] button[aria-label='Close']"},
            ]
        },
        # Notification toasts
        {
            "modal_identifiers": [
                {"class": "MuiSnackbar-root"},
                {"class": "toast"},
                {"role": "alert"},
                {"role": "presentation", "name": "Continue creating"},
                {"selector": "div[data-track-location='Dialog']"},
            ],
            "button_selectors": [
                {"selector": ".close-button"},
                {"selector": "[aria-label='Close']"},
                {"role": "button", "name": "Close"},
                {"selector": "div[data-track-location='Dialog'] button[data-track-location='Dialog']"},
            ]
        },
    ]

    total_handled = 0
    iteration = 0

    # Loop to handle multi-step modals (e.g., tours with multiple "Next" buttons)
    while iteration < max_iterations:
        iteration += 1
        logger.info(f">>> Modal handling iteration {iteration}/{max_iterations}")

        handled_this_round = 0
        modal_found_this_round = False

        for modal_config in common_modals:
            try:
                # Try to find and handle the modal
                handled = handle_modal(page, {
                    **modal_config,
                    "timeout": timeout,
                    "ignore_if_not_found": True,
                    "wait_before_click": 1000,
                    "max_attempts": 2,
                    "visibility_timeout": 100
                })
                if handled:
                    handled_this_round += 1
                    modal_found_this_round = True
                    logger.info(f"✓ Modal handled in iteration {iteration}")

            except Exception as e:
                # Continue to next modal pattern
                logger.debug(f"Modal pattern failed in iteration {iteration}: {e}")
                continue

        if handled_this_round > 0:
            total_handled += handled_this_round
            # Wait a bit for next modal to appear (multi-step scenarios)
            page.wait_for_timeout(1000)
        else:
            # No modals found/handled in this iteration, stop looping
            logger.info(f"No modals found in iteration {iteration}, stopping auto-handle")
            break

    if total_handled > 0:
        logger.info(f"✓ Auto-handled {total_handled} modal step(s) across {iteration} iteration(s)")
    else:
        logger.info("No modals detected to handle")


def create_session(page: Page, v: dict):
    """
    Create a named session (browser context) that can be referenced later.
    Sessions are completely isolated and support all testing operations.

    Supported parameters:
    - name: Session name (required) - used to reference this session
    - url: URL to open in the new session (optional)
    - cookie_file: Path to cookie JSON file to inject (optional)
    - cookies: List of cookie dictionaries to inject (optional)
    - storage_state: Path to storage state JSON file (optional)
    - timeout: Timeout for page load in milliseconds (default: 30000)

    Usage examples:

    1. Create a named session:
       test_step:
           session_user_b:
               open_incognito: "https://example.com"
               cookie_file: "cookies/user_b.json"
               R_click_profile: { role: 'button', name: 'Profile' }

    2. Reference existing session:
       test_step:
           session_user_b:
               R_click_settings: { role: 'button', name: 'Settings' }

    3. Nested sessions:
       test_step:
           session_admin:
               open_incognito: "https://example.com/admin"
               session_sub_admin:
                   open_incognito: "https://example.com/settings"
                   R_click_settings: { role: 'button', name: 'Settings' }
    """
    session_name = v.get("name")
    if not session_name:
        raise ValueError("create_session: 'name' parameter is required")

    logger.info(f">>> Creating session: {session_name}")

    # Get browser from current page
    context = page.context
    browser = context.browser

    if not browser:
        raise RuntimeError("Cannot access browser from current page")

    try:
        # Initialize session storage if not exists
        if not hasattr(page, "_sessions"):
            setattr(page, "_sessions", {})
        if not hasattr(page, "_active_session"):
            setattr(page, "_active_session", None)
        if not hasattr(page, "_session_stack"):
            setattr(page, "_session_stack", [])

        # Create new browser context for the session
        new_context_args = {
            "viewport": context.pages[0].viewport_size if context.pages else {"width": 1280, "height": 720},
            "locale": "en-US",
            "timezone_id": "America/New_York",
        }

        # Load storage state if provided
        storage_state = v.get("storage_state")
        if storage_state and os.path.exists(storage_state):
            import json
            logger.info(f"Loading storage state from: {storage_state}")
            with open(storage_state, "r") as f:
                new_context_args["storage_state"] = json.load(f)

        # Create the new context
        new_context = browser.new_context(**new_context_args)
        logger.info(f"✓ Created browser context for session: {session_name}")

        # Load cookies if provided
        cookie_file = v.get("cookie_file")
        if cookie_file and os.path.exists(cookie_file):
            import json
            logger.info(f"Loading cookies from: {cookie_file}")
            with open(cookie_file, "r") as f:
                cookie_data = json.load(f)
                if isinstance(cookie_data, list):
                    new_context.add_cookies(cookie_data)
                elif isinstance(cookie_data, dict) and "cookies" in cookie_data:
                    new_context.add_cookies(cookie_data["cookies"])
            logger.info(f"✓ Loaded cookies for session: {session_name}")

        # Add custom cookies if provided
        cookies = v.get("cookies", [])
        if cookies and not cookie_file:
            logger.info(f"Adding {len(cookies)} custom cookies to session: {session_name}")
            new_context.add_cookies(cookies)

        # Create page in the new context
        new_page = new_context.new_page()

        # Share workflow context with the new session so templated vars
        # (saved via execute_js save_as in the parent session) are available here.
        _wfc = getattr(page, "_workflow_context", None)
        if _wfc is not None:
            setattr(new_page, "_workflow_context", dict(_wfc))

        # Navigate to URL if provided
        url = v.get("url")
        if url:
            timeout = v.get("timeout", 30000)
            logger.info(f"Session '{session_name}' navigating to: {url}")
            new_page.goto(url, timeout=timeout)
            logger.info(f"✓ Session '{session_name}' loaded")

        # Store session
        getattr(page, "_sessions")[session_name] = {
            "page": new_page,
            "context": new_context,
            "parent_session": getattr(page, "_active_session", None),
            "url": new_page.url
        }

        # Set as active session
        setattr(page, "_active_session", session_name)
        logger.info(f">>> Active session set to: {session_name}")

        # Return for potential chaining
        return new_page

    except Exception as e:
        logger.error(f"✗ Failed to create session '{session_name}': {e}")
        raise


def switch_session(page: Page, v: dict):
    """
    Switch to a previously created session.

    Supported parameters:
    - name: Session name to switch to (required)

    Usage:
       test_step:
           switch_to_user_b:
               switch_session: { name: "user_b" }
           R_click_button: { role: 'button', name: 'Continue' }
    """
    session_name = v.get("name")
    if not session_name:
        raise ValueError("switch_session: 'name' parameter is required")

    if not hasattr(page, "_sessions") or session_name not in getattr(page, "_sessions"):
        raise ValueError(f"Session '{session_name}' not found. Available sessions: {list(getattr(page, '_sessions').keys()) if hasattr(page, '_sessions') else []}")

    # Set as active session
    setattr(page, "_active_session", session_name)
    session = getattr(page, "_sessions")[session_name]

    logger.info(f">>> Switched to session: {session_name}")
    logger.info(f">>> Session URL: {session['url']}")

    return session["page"]


def close_session(page: Page, v: dict):
    """
    Close a session and clean up its resources.

    Supported parameters:
    - name: Session name to close (required, or "current" for active session)

    Usage:
       test_step:
           close_user_b:
               close_session: { name: "user_b" }
    """
    session_name = v.get("name")

    if not session_name or session_name == "current":
        session_name = getattr(page, "_active_session", None)

    if not session_name:
        raise ValueError("No active session to close")

    if not hasattr(page, "_sessions") or session_name not in getattr(page, "_sessions"):
        logger.warning(f"Session '{session_name}' not found")
        return

    session = getattr(page, "_sessions")[session_name]

    try:
        # Close the page and context
        session["context"].close()
        del getattr(page, "_sessions")[session_name]

        # If we closed the active session, switch to parent or default
        if getattr(page, "_active_session", None) == session_name:
            parent_session = session.get("parent_session")
            setattr(page, "_active_session", parent_session if parent_session else None)

        logger.info(f"✓ Closed session: {session_name}")

    except Exception as e:
        logger.error(f"✗ Failed to close session '{session_name}': {e}")
        raise

def _inject_cookies_to_context(page: Page, cookie_file: str):
    """
    Internal helper: Inject cookies to browser context BEFORE opening page.
    This is more efficient than injecting after page load (no reload needed).

    Args:
        page: Playwright page object
        cookie_file: Path to cookie JSON file (supports relative paths from project root)

    Raises:
        FileNotFoundError: If cookie file doesn't exist
        ValueError: If cookie file format is invalid
    """
    import json
    import os

    # Resolve relative paths against project root (BASE_DIR)
    if not os.path.isabs(cookie_file) and not os.path.exists(cookie_file):
        resolved_path = os.path.join(BASE_DIR, cookie_file)
        if os.path.exists(resolved_path):
            cookie_file = resolved_path
            logger.info(f"Resolved cookie file path: {cookie_file}")

    if not os.path.exists(cookie_file):
        raise FileNotFoundError(f"Cookie file not found: {cookie_file} (resolved from CWD: {os.getcwd()})")

    # Get current browser context
    context = page.context

    logger.info(f"Loading cookies from: {cookie_file}")
    with open(cookie_file, "r") as f:
        cookie_data = json.load(f)

    # Handle different JSON formats
    if isinstance(cookie_data, list):
        # Direct list of cookies
        cookies_to_add = cookie_data
    elif isinstance(cookie_data, dict):
        # Playwright storage state format
        if "cookies" in cookie_data:
            cookies_to_add = cookie_data["cookies"]
        else:
            raise ValueError(f"Unexpected cookie file format (missing 'cookies' key): {cookie_file}")
    else:
        raise ValueError(f"Invalid cookie file format: {cookie_file}")

    # Add cookies to context
    context.add_cookies(cookies_to_add)
    logger.info(f"✓ Loaded {len(cookies_to_add)} cookies to context (ready for authenticated page load)")


def execute_js(page: Page, v):
    """
    Execute JavaScript in the browser page context.

    YAML usage:
        # 1. Inline script
        execute_js: { script: "document.title" }

        # 2. Script with arguments
        execute_js:
            script: "(selector) => document.querySelector(selector).innerText"
            args: "h1"

        # 3. Multiple arguments
        execute_js:
            script: "(a, b) => a + b"
            args: [1, 2]

        # 4. External JS file
        execute_js: { file: "scripts/scroll_to_top.js" }

        # 5. Assert return value
        execute_js:
            script: "() => document.querySelectorAll('.item').length"
            assert_equals: 5

        # 6. Save return value to workflow context
        execute_js:
            script: "() => document.querySelector('.price').textContent"
            save_as: "price_text"
    """
    import json as json_mod

    script = v.get("script")
    file = v.get("file")
    args = v.get("args")
    assert_equals = v.get("assert_equals")
    assert_contains = v.get("assert_contains")
    save_as = v.get("save_as")
    timeout = v.get("timeout", 10000)

    if not script and not file:
        raise ValueError("execute_js: 'script' or 'file' is required")

    if file:
        file_path = file if os.path.isabs(file) else os.path.join(BASE_DIR, file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"execute_js: file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            script = f.read()
        logger.info(f"execute_js: loaded script from {file_path}")

    # Ensure script is a callable expression
    # If script doesn't look like a function, wrap it in an IIFE
    stripped = script.strip()
    if not stripped.startswith("(") and not stripped.startswith("function"):
        # It's a raw expression, wrap it
        script = f"() => ({stripped})"

    # Template {{var}} placeholders from the workflow context (populated by save_as).
    # This makes variables saved by an earlier execute_js step usable in later steps,
    # including inside a different session (create_session copies _workflow_context).
    # Falls back to the cross-case global store (see global_state.py).
    _ctx = _merged_context_vars(page)
    if _ctx:
        def _tmpl(s):
            if not isinstance(s, str):
                return s
            for _k, _v in _ctx.items():
                if _k:
                    s = s.replace("{{%s}}" % _k, str(_v))
            return s
        script = _tmpl(script)
        if isinstance(args, list):
            args = [_tmpl(a) if isinstance(a, str) else a for a in args]

    logger.info(f"execute_js: executing script (length={len(script)})")

    result = page.evaluate(script, args)

    logger.info(f"execute_js: result = {result}")

    # Assertions
    if assert_equals is not None:
        if result != assert_equals:
            raise AssertionError(f"execute_js: expected {assert_equals!r}, got {result!r}")
        logger.info(f"execute_js: assert_equals passed ({result})")

    if assert_contains is not None:
        if assert_contains not in str(result):
            raise AssertionError(f"execute_js: expected result to contain {assert_contains!r}, got {result!r}")
        logger.info(f"execute_js: assert_contains passed")

    # Save to workflow context
    if save_as:
        if not hasattr(page, "_workflow_context"):
            setattr(page, "_workflow_context", {})
        getattr(page, "_workflow_context")[save_as] = result
        logger.info(f"execute_js: saved result as '{save_as}' = {result!r}")
        # Cross-case global store: a step can publish a value that other test cases
        # (and any session) can read via {{var}} when running in the same pytest process.
        if v.get("global"):
            _set_global(save_as, result)
            logger.info(f"execute_js: also published '{save_as}' to the cross-case global store")

    return result


def verify_no_sibling_text(page: Page, v: dict):
    """
    Verify that an element's siblings do NOT contain the specified text,
    OR directly verify that a text is NOT visible anywhere on the page/scope.

    Supported parameters:
    - locator: Element locator to anchor on (optional if 'text' is provided alone)
    - index: Element index, supports negative values like -1 for last (default: -1)
    - text: The text that should NOT exist (required)
    - container: Scope container text — search within this container's element (optional)
    - timeout: Timeout in milliseconds (default: 5000)

    Usage in YAML:
        # Pattern 1: Verify siblings of a specific element do NOT contain text
        verify_no_sibling_add_new:
            locator: '[data-testid="base-more-horiz-icon-cta"]'
            index: -1
            text: 'Add new'

        # Pattern 2: Directly verify text is NOT visible within a scope (recommended for absent elements)
        verify_no_cta_checkbox:
            text: 'Choose call-to-action type'
            container: 'test_general_products'
    """
    locator_str = v.get("locator")
    text = v.get("text", "Add new")
    target_index = v.get("index", -1)
    container_text = v.get("container")
    timeout = v.get("timeout", 5000)

    if not text:
        raise ValueError("verify_no_sibling_text: 'text' parameter is required")

    # Pattern 2: No locator, just search for text absence within a scope
    if not locator_str and container_text:
        logger.info(f"Verifying text '{text}' is NOT visible within container: {container_text}")
        scope = page.locator("div", has_text=container_text).last
        matches = scope.locator(f":text-is('{text}'), button:has-text('{text}'), [data-testid]:has-text('{text}')")
        for i in range(min(matches.count(), 10)):
            if matches.nth(i).is_visible():
                page.screenshot(path=f"fail_visible_{text[:10]}.png")
                raise AssertionError(
                    f"Text '{text}' was found and is VISIBLE within '{container_text}', "
                    f"but it should NOT exist."
                )
        logger.info(f"Confirmed: text '{text}' is NOT visible within '{container_text}'")
        return

    # Pattern 1: Original sibling-check logic
    if not locator_str:
        raise ValueError("verify_no_sibling_text: either 'locator' or 'container' parameter is required")

    logger.info(f"Verifying no sibling with text '{text}' for element: {locator_str}[{target_index}]")

    el = page.locator(locator_str).nth(target_index)
    el.wait_for(state="visible", timeout=timeout)

    parent = el.locator("xpath=..")
    sibling_with_text = parent.locator(f":text-is('{text}')").or_(
        parent.locator(f"button:has-text('{text}')")
    ).or_(
        parent.locator(f"[data-testid]:has-text('{text}')")
    )

    count = sibling_with_text.count()
    if count > 0:
        for i in range(count):
            if sibling_with_text.nth(i).is_visible():
                page.screenshot(path=f"fail_sibling_{text[:10]}.png")
                raise AssertionError(
                    f"Found sibling element with text '{text}' near '{locator_str}[{target_index}]', "
                    f"but it should NOT exist."
                )

    logger.info(f"Confirmed: no sibling with text '{text}' found near '{locator_str}[{target_index}]'")


def delete_coseller_if_exists(page: Page, v: dict):
    """
    Complete flow to delete co-seller (if exists).
    
    This is a compound action that encapsulates 4 steps:
    1. Check if co-seller data exists in the list
    2. Click More button (three dots)
    3. Click Delete menu option
    4. Confirm delete in dialog
    5. Verify delete success toast
    
    If no co-seller data exists, the entire flow is skipped silently without error.
    
    YAML usage:
        delete_coseller_if_exists: { timeout: 10000 }
    
    Parameters:
    - timeout: Overall timeout in ms, default 10000ms
    - toast_timeout: Timeout for waiting toast message, default 8000ms
    """
    timeout = v.get("timeout", 10000)
    toast_timeout = v.get("toast_timeout", 8000)
    
    logger.info("delete_coseller_if_exists: checking if co-seller exists...")
    
    # Step 0 (Pre-check): Verify co-seller data exists in the list
    # Look for co-seller entries - if none exist, skip the entire flow
    has_coseller_data = page.evaluate("""
        () => {
            // Look for indicators that co-seller data exists:
            // 1. Check for the last MoreHorizIcon button (co-seller row's button)
            // 2. Check if there's text indicating co-seller count > 0
            
            const moreBtns = document.querySelectorAll('button');
            let moreHorizBtns = 0;
            for (const btn of moreBtns) {
                if (btn.querySelector('svg[data-testid="MoreHorizIcon"]')) {
                    moreHorizBtns++;
                }
            }
            
            // Also check for co-seller specific elements
            const pageText = document.body.innerText;
            const hasCoSellerSection = /Co-sellers?\\s*\\(\\d+\\)/.test(pageText);
            
            // If there's only 1 MoreHorizIcon (Post-level), no co-seller exists
            if (moreHorizBtns <= 1) {
                return false;
            }
            
            // If Co-sellers section shows (0), no co-seller exists
            if (/Co-sellers?\\s*\\(0\\)/.test(pageText)) {
                return false;
            }
            
            return true;
        }
    """)
    
    if not has_coseller_data:
        logger.info("delete_coseller_if_exists: no co-seller data found, skipping entire delete flow")
        return
    
    # Step 1: Find the co-seller row's More button (the LAST one on page)
    # Page has 3 More buttons: Post-level (top), Action button, co-seller row (last)
    try:
        all_more_buttons = page.locator("button:has(svg[data-testid='MoreHorizIcon'])")
        count = all_more_buttons.count()
        logger.info(f"delete_coseller_if_exists: found {count} More buttons on page")
        
        # Use the LAST More button - that's the co-seller row's button
        more_button = all_more_buttons.last
        more_button.wait_for(state="visible", timeout=timeout)
        logger.info("delete_coseller_if_exists: co-seller found (last More button), proceeding with delete flow")
    except Exception:
        logger.info("delete_coseller_if_exists: no co-seller found (More button not present), skipping")
        return
    
    # Step 2: Click More button
    try:
        more_button.click()
        logger.info("delete_coseller_if_exists: clicked More button")
        page.wait_for_timeout(1000)
    except Exception as e:
        logger.warning(f"delete_coseller_if_exists: failed to click More button: {e}")
        return
    
    # Step 3: Click Delete option in menu
    try:
        delete_option = page.get_by_text("Delete", exact=True)
        delete_option.wait_for(state="visible", timeout=timeout)
        delete_option.click()
        logger.info("delete_coseller_if_exists: clicked Delete option")
        page.wait_for_timeout(1500)
    except Exception as e:
        logger.warning(f"delete_coseller_if_exists: failed to click Delete option: {e}")
        return
    
    # Step 4: Confirm delete in dialog
    # From co-seller row's More menu -> Delete, the dialog title is always "Delete the selected posts"
    try:
        dialog = page.locator("div[role='dialog']").filter(has_text="Delete the selected posts")
        dialog.wait_for(state="visible", timeout=timeout)
        logger.info("delete_coseller_if_exists: confirmation dialog appeared")

        # Pre-check: If dialog shows "No items selected" or "You haven't selected any items",
        # the co-seller post is already deleted - skip the delete flow
        dialog_text = dialog.inner_text()
        if "no item" in dialog_text.lower() or "haven't selected" in dialog_text.lower() or "not selected" in dialog_text.lower():
            logger.info("delete_coseller_if_exists: dialog shows no items selected, co-seller already deleted - skipping")
            # Close the dialog (click Cancel or press Escape)
            try:
                cancel_btn = dialog.get_by_role("button", name="Cancel")
                if cancel_btn.is_visible():
                    cancel_btn.click()
                else:
                    page.keyboard.press("Escape")
            except:
                page.keyboard.press("Escape")
            return

        # Click the Delete button (not Cancel) inside the dialog
        confirm_button = dialog.get_by_role("button", name="Delete")
        confirm_button.wait_for(state="visible", timeout=timeout)
        confirm_button.click()
        logger.info("delete_coseller_if_exists: clicked Confirm Delete button")
        page.wait_for_timeout(3000)
    except Exception as e:
        logger.warning(f"delete_coseller_if_exists: failed to confirm delete: {e}")
        return
    
    # Step 5: Verify delete success toast
    try:
        toast_text = "post deleted resell successfully."
        toast = page.get_by_text(toast_text, exact=False)
        toast.wait_for(state="visible", timeout=toast_timeout)
        logger.info(f"delete_coseller_if_exists: verified success toast '{toast_text}'")
    except Exception as e:
        logger.warning(f"delete_coseller_if_exists: toast verification failed: {e}")
        # Don't fail if toast doesn't appear, the delete might still be successful


def ensure_auto_archive(page: Page, v: dict):
    """
    Idempotently enable/disable the 'Auto-archive completed event posts' switch at
    {BASE_URL}/events/settings. The switch is a MUI Switch whose real <input> is
    visually hidden, so we force-click it to open the confirm dialog, then click
    Apply. This guarantees the final toggle state regardless of the starting state,
    which matters because T4559/T4853/T5105 share this global merchant setting.

    YAML usage:
        ensure_auto_archive: { enabled: true }      # turn ON
        ensure_auto_archive: { enabled: false }     # turn OFF
    """
    target = bool(v.get("enabled", True))
    switch = page.locator('input[name="autoArchive"]')
    try:
        current = switch.is_checked(timeout=3000)
    except Exception:
        current = None
    if current == target:
        logger.info(f"ensure_auto_archive: already {'enabled' if target else 'disabled'}, no action")
        return

    # Force-click the hidden MUI switch input to open the confirm dialog
    switch.click(force=True, timeout=5000)
    page.wait_for_timeout(1200)

    # Click Apply inside the dialog
    apply_btn = page.locator("[role='dialog']").get_by_role("button", name="Apply").first
    try:
        apply_btn.click(timeout=5000)
    except Exception:
        page.get_by_role("button", name="Apply").first.click(timeout=5000)
    page.wait_for_timeout(1500)

    logger.info(f"ensure_auto_archive: set to {'enabled' if target else 'disabled'}")



def smart_seat_click(page: Page, v: dict):
    """
    Select seats in the venue-map dialog until the "N table selected" counter reaches
    `target`, then assert it.

    Seat-map reality (T2515, verified 2026-10-13):
    - selection only registers for a REAL mouse click at a seat center (Playwright
      locator.click refuses because the seat's own <circle> dot intercepts the rect;
      force and JS clicks don't register);
    - zoom must fully settle before rect coordinates are read, or the saved points are
      stale (YAML sleep_step keys collapse under PyYAML, so timing lives in here);
    - after each successful selection the map re-renders and every previously computed
      coordinate goes stale, so we re-verify elementFromPoint self-hit BEFORE each
      click, and re-collect candidates each round. Clicking a covered/old point
      cancels a selected seat instead of selecting the target one.
    The whole zoom -> collect -> verify -> click loop is self-contained and idempotent
    per dialog session (calling it again re-zooms and only targets seats not in
    window.__picked).

    YAML usage:
        smart_seat_click_1: { target: 5 }   # select 5 fresh seats
        smart_seat_click_2: { target: 6 }   # after drawer reopen, add a 6th
        # [2026-10-13] KAT-12263 FIXED: $80/$100 inside seats are clickable again.
        # Back to the original $80 seat; counter text is now "N items selected"
        # (frontend wording change shipped with the fix).
        smart_seat_click_1: { target: 1, stroke: "#E9803D" }
    """
    target = int(v.get("target", 0))
    if target <= 0:
        raise ValueError("smart_seat_click: 'target' (>0) is required")
    zoom_times = int(v.get("zoom", 4))
    stroke_filter = v.get("stroke") or ""

    # --- zoom in (default 4x; T4955 $50 seats need 2x, see docstring) ---
    # Click the zoom button inside a VISIBLE dialog only: the buy-ticket flow renders
    # two duplicate "Select tickets" dialogs and querySelector picks the hidden one,
    # making the zoom a no-op (T4955 on 12061, 2026-10-13).
    for _ in range(zoom_times):
        page.evaluate("""() => {
            const ds = [...document.querySelectorAll('[role="dialog"]')].filter(d => { const s = getComputedStyle(d); return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity) > 0; });
            for (const d of ds) { const z = d.querySelector('[aria-label="Zoom in"]'); if (z) { z.click(); break; } }
        }""")
        page.wait_for_timeout(900)
    page.wait_for_timeout(3000)

    def count():
        # [2026-10-13] frontend now shows "N items selected" (was "N tables selected"
        # before the KAT-12263 fix was deployed). Match both wordings.
        m = re.search(r"(\d+) (tables?|items?) selected", page.locator('[role="dialog"]:visible').first.inner_text())
        return int(m.group(1)) if m else 0

    def collect():
        raw = page.evaluate("""(strokeFilter) => {
            window.__picked = window.__picked || [];
            const dialogs = [...document.querySelectorAll('[role="dialog"]')].filter(d => { const s = getComputedStyle(d); return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity) > 0; });
            const rects = [], avail = new Set();
            const circleSel = strokeFilter
                ? 'circle[data-id][stroke="' + strokeFilter + '"]'
                : 'circle[data-id]:not([stroke="transparent"])';
            for (const d of dialogs) {
                rects.push(...d.querySelectorAll('rect[data-id]'));
                [...d.querySelectorAll(circleSel)].forEach(c => avail.add(c.getAttribute('data-id')));
            }
            const out = [];
            for (const r of rects) {
                const id = r.getAttribute('data-id');
                if (window.__picked.includes(id)) continue;
                if (!avail.has(id)) continue;
                const rb = r.getBoundingClientRect();
                if (rb.width < 60) continue;
                const cx = Math.round(rb.x + rb.width / 2), cy = Math.round(rb.y + rb.height / 2);
                const hit = document.elementFromPoint(cx, cy);
                if (hit && hit.getAttribute('data-id') === id) out.push(id + ',' + cx + ',' + cy);
            }
            return out.join(';');
        }""", stroke_filter)
        out = []
        for chunk in str(raw).split(";"):
            chunk = chunk.strip()
            if not chunk:
                continue
            parts = [p.strip() for p in chunk.split(",")]
            if len(parts) == 3:
                out.append((parts[0], float(parts[1]), float(parts[2])))
        return out

    def self_hit(cid, cx, cy):
        return page.evaluate(
            "([id, x, y]) => { const el = document.elementFromPoint(x, y); return !!(el && el.getAttribute('data-id') === id); }",
            [cid, cx, cy],
        )

    rounds = 0
    while True:
        n = count()
        if n >= target:
            logger.info(f"smart_seat_click: reached target {target} with {n} selected")
            return
        cands = collect()
        if not cands:
            raise AssertionError(f"smart_seat_click: no self-hit candidates (count {n})")
        progress = False
        for cid, cx, cy in cands:
            if not self_hit(cid, cx, cy):
                continue  # stale coordinate after a re-render; skip
            page.mouse.click(cx, cy)
            page.wait_for_timeout(1800)
            n2 = count()
            logger.info(f"smart_seat_click: clicked seat {cid[:8]} ({cx},{cy}) -> {n2}")
            if n2 >= target:
                return
            if n2 > n:
                page.evaluate("window.__picked = window.__picked || []; if (!window.__picked.includes(%r)) window.__picked.push(%r);" % (cid, cid))
                progress = True
                break
            # n2 <= n: either a no-op or a cancellation; try the next candidate
        rounds += 1
        if rounds >= 20 and not progress:
            raise AssertionError(f"smart_seat_click: stuck at {count()} tables, target {target}")
    final = count()
    if final < target:
        raise AssertionError(f"smart_seat_click: reached {final} tables, target {target}")
    logger.info(f"smart_seat_click: done, {final} tables selected")
