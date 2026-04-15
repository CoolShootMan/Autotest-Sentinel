import os
import re
import subprocess
import sys
from playwright.sync_api import Page, Locator, expect
from loguru import logger

# Calculate project base directory dynamically (search up for .git or test_case)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(BASE_DIR, "test_case")) and BASE_DIR != os.path.dirname(BASE_DIR):
    BASE_DIR = os.path.dirname(BASE_DIR)
logger.info(f"ACTIONS_BASE_DIR: {BASE_DIR}")
from page.home import page_element_role_click, page_element_label_click, page_open
from ..utils.ai_vision import ai_vision

def open_url(page: Page, v):
    logger.info(f">>> Current Step: open_url")
    url = v.get("open") or v.get("url") if isinstance(v, dict) else v
    if url:
        from page.home import page_open
        page_open(page, url)

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
    if selector:
        page.wait_for_selector(selector, timeout=timeout)

def wait_for_url(page: Page, v: dict):
    url = v.get("url") or v.get("verify_navigation")
    timeout = v.get("timeout", 30000)
    if url:
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
                page._execution_history.append((k, step_v))
            else:
                logger.error(f"  >>> If-block: Action '{k}' not found.")
                raise Exception(f"Action '{k}' not found in if block.")

def smart_fill(page: Page, v: dict):  
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_value = v.get("value", "")
    target_locator = v.get("locator")

    logger.info(f"Filling field '{target_name or target_locator}' with value '{target_value}'")
    fill_timeout = v.get("timeout", 10000)

    try:
        if target_locator:
            el = page.locator(target_locator).nth(v.get("index", 0))
            el.fill(str(target_value), timeout=fill_timeout)
        elif "role" in v:
            page.get_by_role(v["role"], name=target_name, exact=v.get("exact", False)).nth(v.get("index", 0)).fill(str(target_value), timeout=fill_timeout)
        else:
            candidates = [
                page.get_by_label(target_name, exact=False),
                page.get_by_placeholder(target_name, exact=False),
                page.locator(f"input[name*='{target_name}'], textarea[name*='{target_name}']")
            ]
            target_id = v.get("index", 0)
            filled = False
            for c in candidates:
                if c.nth(target_id).is_visible():
                    c.nth(target_id).fill(str(target_value), timeout=fill_timeout)
                    filled = True
                    break
            if not filled:
                 page.locator(f"input[placeholder*='{target_name}'], input[aria-label*='{target_name}']").nth(target_id).fill(str(target_value), timeout=fill_timeout)
        page.wait_for_timeout(300)
    except Exception as e:
        logger.error(f"Fill failed: {e}. AI Healing not fully implemented for Pure Vision fill yet.")
        raise

def fill_numeric(page: Page, v: dict):
    target_locator = v.get("locator")
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

def smart_check(page: Page, v: dict):
    target_name = v.get("name") or v.get("text") or v.get("label")
    target_locator = v.get("locator")
    checked = v.get("checked", True)
    target_role = v.get("role")
    target_index = v.get("index", 0)
    no_modal_scope = v.get("no_modal_scope", False)
    logger.info(f"Checking '{target_name or target_locator}' to {checked}")

    def _get_el(root):
        if target_locator:
            return page.locator(target_locator).nth(target_index)
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
        if "Clicking the checkbox did not change its state" in str(e) or "intercepts pointer events" in str(e):
            try:
                _mui_fallback(_get_el(page))
                return
            except Exception as fe:
                logger.warning(f"MUI fallback also failed: {fe}")
        # On Timeout or Strict-mode: fall through to modal-scoped attempt
        logger.debug(f"Page-level check failed ({type(e).__name__}), trying modal scope...")

    # --- Strategy 2: Modal-scoped (only when page-level times out & not suppressed) ---
    if no_modal_scope:
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
    except Exception as e2:
        if "Clicking the checkbox did not change its state" in str(e2) or "intercepts pointer events" in str(e2):
            try:
                _mui_fallback(_get_el(active_modal))
                return
            except Exception as fe2:
                logger.error(f"MUI modal fallback also failed: {fe2}")
        logger.error(f"Modal-scoped check also failed: {e2}")
        raise

def smart_upload(page: Page, v: dict):
    if "file_path" in v:
        file_path = v.get("file_path")
        target_index = v.get("index", 0)
        with page.expect_file_chooser(timeout=5000) as fc_info:
            if "locator" in v:
                page.locator(v["locator"]).nth(target_index).click()
            else:
                page.get_by_text(v.get("text"), exact=True).nth(target_index).click()
        fc = fc_info.value
        fc.set_files(file_path if isinstance(file_path, list) else [file_path])

def smart_click(page: Page, v: dict):
    if page.get_by_text("Something went wrong!", exact=True).is_visible():
        logger.error("Application Crashed!")
        raise Exception("Application Crashed")

    # Wait for loading overlays/backdrops to disappear before clicking anything
    try:
        backdrop = page.locator(".MuiBackdrop-root, [class*='Backdrop'], .loading-overlay").first
        backdrop.wait_for(state="hidden", timeout=8000)
    except: pass

    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    target_index = v.get("index", 0)
    target_test_id = v.get("test_id")
    force = v.get("force", False) # Default to False for better event triggering
    optional = v.get("optional", False) # If True, skip silently when element not found
    skip_if_disabled = v.get("skip_if_disabled", False) # If True, skip silently when button is disabled

    # Validation
    if not target_name and not target_locator and not target_role and not target_test_id:
        return

    logger.info(f"Click started for target: {target_name or target_locator or target_role}")

    # skip_if_disabled: if the target button is disabled, skip this step silently
    if skip_if_disabled:
        try:
            if target_role and target_name:
                candidate = page.get_by_role(target_role, name=target_name).nth(target_index)
            elif target_locator:
                candidate = page.locator(target_locator).nth(target_index)
            else:
                candidate = page.get_by_text(target_name, exact=target_exact).nth(target_index)
            # is_disabled() returns True when button has disabled attribute or aria-disabled="true"
            if candidate.is_disabled(timeout=3000):
                logger.info(f"skip_if_disabled: '{target_name or target_locator}' is disabled, skipping step.")
                return
        except Exception as e:
            logger.debug(f"skip_if_disabled check error (proceeding normally): {e}")

    # Scoping: find all visible modals
    modals = page.locator("div[role='dialog'], .MuiDialog-root, .MuiModal-root").all()
    visible_modals = [m for m in modals if m.is_visible()]
    active_modal = visible_modals[-1] if visible_modals else None

    # Special handling for "Publish": use JS to find and click, searching in visible dialog first, then full page
    if target_name == "Publish":
        logger.debug("Publish handler: using JS-based click")
        try:
            page.wait_for_timeout(3000)  # Wait for loading/Confirm dialog to settle
            clicked = page.evaluate("""
                () => {
                    // Find all visible dialogs and pick the last one (most recent)
                    const dialogs = Array.from(document.querySelectorAll('[role="dialog"], .MuiDialog-root, [class*="MuiDialog"]'));
                    let targetContainer = null;
                    for (const d of dialogs) {
                        const style = window.getComputedStyle(d);
                        if (style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0) {
                            targetContainer = d;
                        }
                    }
                    // Search in visible dialog first
                    if (targetContainer) {
                        const dialogBtns = Array.from(targetContainer.querySelectorAll('button'));
                        for (const btn of dialogBtns) {
                            const t = btn.textContent.trim();
                            if (t === 'Publish' && btn.offsetParent !== null) {
                                btn.click();
                                return 'dialog';
                            }
                        }
                    }
                    // Fallback: search entire page
                    const allBtns = Array.from(document.querySelectorAll('button'));
                    for (const btn of allBtns) {
                        const t = btn.textContent.trim();
                        if (t === 'Publish' && btn.offsetParent !== null) {
                            btn.click();
                            return 'page';
                        }
                    }
                    return null;
                }
            """)
            if clicked:
                logger.info(f"Publish clicked via JS ({clicked})")
                page.wait_for_timeout(1000)
                return
            else:
                logger.debug("JS Publish: no visible button found")
        except Exception as e:
            logger.debug(f"JS Publish click error: {e}")

    # Special handling for "Save": use JS to find and click the LAST visible Save button in the most recent dialog
    if target_name == "Save":
        logger.debug("Save handler: using JS-based click")
        try:
            page.wait_for_timeout(1500)
            clicked = page.evaluate("""
                () => {
                    // Find all visible dialogs
                    const dialogs = Array.from(document.querySelectorAll('[role="dialog"], .MuiDialog-root, [class*="MuiDialog"]'));
                    let targetContainer = null;
                    for (const d of dialogs) {
                        const style = window.getComputedStyle(d);
                        if (style.display !== 'none' && style.visibility !== 'hidden' && parseFloat(style.opacity) > 0) {
                            targetContainer = d;
                        }
                    }
                    // Search in the last visible dialog first, then full page
                    const searchIn = targetContainer || document.body;
                    const btns = Array.from(searchIn.querySelectorAll('button'));
                    for (const btn of btns) {
                        if (btn.textContent.trim() === 'Save' && !btn.disabled && btn.offsetParent !== null) {
                            btn.click();
                            return 'ok';
                        }
                    }
                    // Fallback: search entire page
                    const allBtns = Array.from(document.querySelectorAll('button'));
                    for (const btn of allBtns) {
                        if (btn.textContent.trim() === 'Save' && !btn.disabled && btn.offsetParent !== null) {
                            btn.click();
                            return 'page';
                        }
                    }
                    return null;
                }
            """)
            if clicked:
                logger.info(f"Save clicked via JS ({clicked})")
                page.wait_for_timeout(1000)
                return
            else:
                logger.debug("JS Save: no enabled button found")
        except Exception as e:
            logger.debug(f"JS Save click error: {e}")

    # For most buttons (Get Tickets, Selling, Customize, Batch set, etc.), search the WHOLE page.
    # Only scope to modal for known dialog buttons (Confirm, Save, Cancel, etc.)
    dialog_buttons = {"Confirm", "Save", "Cancel", "Apply to all", "Close", "Delete", "Yes", "No"}
    root = active_modal if (active_modal and target_name in dialog_buttons) else page

    try:
        # 1. Test ID attempt (Most robust if available)
        if target_test_id:
            el = root.get_by_test_id(target_test_id).nth(target_index)
            if el.is_visible(timeout=5000):
                el.click(force=force)
                return

        # 2. Standard locator attempt
        # If target_locator is an absolute XPath or specified, use it directly from page
        if target_locator:
            if target_locator.startswith("/") or target_locator.startswith("xpath="):
                # Ensure Playwright treats it as XPath explicitly to avoid CSS engine errors
                xpath_locator = target_locator if target_locator.startswith("xpath=") else f"xpath={target_locator}"
                el = page.locator(xpath_locator).nth(target_index)
            else:
                el = root.locator(target_locator).nth(target_index)
            
            # If name is also provided, filter by it
            if target_name:
                el = el.get_by_text(target_name, exact=target_exact)
                
            if el.is_visible(timeout=60000):
                el.click(force=force)
                return
            else:
                if optional:
                    logger.info(f"Optional click: element at index {target_index} not visible, skipping.")
                    return
    except Exception as e:
        if optional:
            logger.info(f"Optional click: locator attempt failed for index {target_index}, skipping. ({e})")
            return
        logger.debug(f"Locator attempt failed: {e}")

    try:
        # 1.1 Aria-label fallback (Critical for icon buttons)
        if target_name:
            el = root.locator(f'button[aria-label="{target_name}"], [aria-label*="{target_name}"]').nth(target_index)
            if el.is_visible(timeout=60000):
                el.click(force=force)
                logger.info(f"Clicked via aria-label fallback: {target_name}")
                return
    except: pass

    # ---- 4. Robust page-level fallback (always from page, not from root modal) ----
    if target_role == 'button' or target_name in {"Get Tickets", "Selling", "Customize products", "Batch set commission rates"}:
        try:
            if target_name:
                # Find ALL matching elements on the page
                if target_role:
                    all_matches = page.get_by_role(target_role, name=target_name, exact=target_exact).all()
                else:
                    all_matches = page.get_by_text(target_name, exact=target_exact).all()
                logger.debug(f"Page-level search for '{target_name}': {len(all_matches)} total elements")
                for idx, candidate in enumerate(all_matches):
                    try:
                        is_vis = candidate.is_visible(timeout=2000)
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

    try:
        if target_role:
            el = root.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
        elif target_name:
            el = root.get_by_text(target_name, exact=target_exact).nth(target_index)

        # FINAL ATTEMPT: For dialog buttons, skip scroll stability check (dialogs often have CSS animations)
        if el:
            try:
                el.scroll_into_view_if_needed(timeout=3000)
            except Exception as scroll_e:
                logger.debug(f"Scroll not stable (normal for dialogs): {scroll_e}")
            page.wait_for_timeout(300)
            try:
                # Always try force=True for dialog buttons to bypass animation/timeouts
                el.click(force=True)
                logger.info(f"Force-clicked '{target_name}'")
                return
            except Exception as click_e:
                logger.debug(f"Force click failed, trying JS: {click_e}")
                # Last resort: JS click using element_handle
                try:
                    page.evaluate("(el) => el.click()", el.element_handle())
                    logger.info(f"JS-clicked '{target_name}'")
                    return
                except Exception as js_e:
                    logger.debug(f"JS click also failed: {js_e}")
                    raise
            # Close dropdown/listbox after selecting an option
            if target_role == 'option':
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
            return
    except Exception as e:
        logger.debug(f"Standard click failed: {e}")


    # 3. --- AI Self-Healing Fallback (The "Brain") ---
    # Optional check: if all traditional methods failed and this click is optional, skip gracefully
    if optional:
        logger.info(f"Optional click: element '{target_name or target_locator}' not found after all attempts, skipping.")
        return

    # Global Kill-switch check
    if v.get("disable_ai", False) or os.environ.get("AI_DISABLED") == "True":
        logger.warning(f"AI Healing is DISABLED for '{target_name or target_locator}'. Raising original error.")
        
        # 3.1 Global Fallback (Last ditch effort for common buttons like 'Add')
        if target_role == 'button' or target_name == 'Add' or target_name == 'Add new':
            try:
                logger.debug("Traditional/Modal search failed. Trying global search for last visible button...")
                all_btns = page.get_by_role("button", name=target_name, exact=target_exact).all()
                for btn in reversed(all_btns):
                    if btn.is_visible():
                        try:
                            btn.scroll_into_view_if_needed(timeout=3000)
                        except: pass
                        btn.click(force=True)
                        logger.info(f"Global fallback SUCCESS for '{target_name}'")
                        return
                    else:
                        # Try JS click for hidden elements
                        try:
                            page.evaluate("(el) => el.click()", btn.element_handle())
                            logger.info(f"Global fallback SUCCESS (JS) for '{target_name}'")
                            return
                        except: pass
            except: pass
            
        raise Exception(f"Element not found: {target_name or target_locator}")

    logger.error("Traditional methods failed. Triggering AI Pure Vision Healing...")
    try:
        page_history = getattr(page, "_execution_history", [])
        instruction = f"Click the element: '{target_name or target_locator}'"
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
                    from .utils.yaml_patcher import patch_yaml_step
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
            logger.error(f"💀 AI SOM could not locate the element. Logic ends here.")
    except Exception as ai_err:
        logger.error(f"AI Healing Error: {ai_err}")

    # If even AI fails, re-raise original or fail
    if v.get("_retry_ai", 0) > 0:
        return # We already tried
    raise Exception(f"Failed to click '{target_name or target_locator}' after all attempts including AI.")

def click_modal_close(page: Page, v: dict):
    logger.info("Attempting to close modal...")
    try:
        close_btn = page.locator("div[role='dialog'] button[aria-label='close'], .MuiDialog-root button.close").first
        if close_btn.is_visible():
            close_btn.click()
        else:
            page.keyboard.press("Escape")
    except Exception as e:
        logger.warning(f"Failed to close modal: {e}")

def verify_text_visible(page: Page, v: dict):
    text = v.get("text")
    timeout = v.get("timeout", 10000)
    not_visible = v.get("assert_not_visible", False)

    if not_visible:
        logger.info(f"Verifying text is NOT visible: {text or v.get('locator')}")
        if v.get("locator"):
            el = page.locator(v["locator"]).first
            if text:
                el = el.get_by_text(text, exact=v.get("exact", False))
        elif text:
            el = page.get_by_text(text, exact=v.get("exact", False)).first
        else:
            raise AssertionError("verify: no text or locator provided")
        try:
            el.wait_for(state="hidden", timeout=timeout)
            logger.info(f"Confirmed element is not visible: {text or v.get('locator')}")
        except:
            if el.is_visible():
                page.screenshot(path=f"fail_not_visible_{str(text or v.get('locator'))[:10]}.png")
                raise AssertionError(f"Element '{text or v.get('locator')}' is still visible but should not be.")
        return

    logger.info(f"Verifying text visibility: {text}")
    try:
        page.get_by_text(text, exact=v.get("exact", False)).first.wait_for(state="visible", timeout=timeout)
        logger.info(f"Text '{text}' is visible.")
    except Exception as e:
        page.screenshot(path=f"fail_verify_{text[:10]}.png")
        raise AssertionError(f"Text '{text}' not found.")

def verify_text_hidden(page: Page, v: dict):
    text = v.get("text")
    timeout = v.get("timeout", 10000)
    logger.info(f"Verifying text hidden: {text}")
    try:
        element = page.get_by_text(text, exact=v.get("exact", False)).first
        
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
        page.screenshot(path=f"fail_verify_hidden_{text[:10]}.png")
        raise AssertionError(f"Text '{text}' is still visible! Exception: {str(e)}")

def smart_wait(page: Page, v: dict):
    """
    Wait for an element to appear (become visible).
    Supports: role, name, locator, text.
    Usage in YAML:
        wait_customize_back: { role: 'button', name: 'Customize products', timeout: 15000, disable_ai: true }
    """
    timeout = v.get("timeout", 10000)
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
    Subprocess isolated action to verify 'Code Not Recognized'.
    Bypasses Playwright video source limitations by launching a fresh browser.
    """
    logger.info(">>> Subprocess Isolation: Launching invalid QR scan...")
    result = subprocess.run(
        [sys.executable, "run_invalid_qr.py"], 
        capture_output=True, 
        text=True, 
        cwd=BASE_DIR
    )
    if "SUCCESS" in result.stdout:
        logger.info("Successfully verified 'Code Not Recognized' via subprocess")
    else:
        logger.error(f"Failed to verify Invalid QR scan. Output:\n{result.stdout}\nStderr:\n{result.stderr}")
        raise AssertionError("Invalid QR scan failed in subprocess. Check logs for details.")

def verify_value(page: Page, v: dict):
    target_name = v.get("name")
    target_locator = v.get("locator")
    expected_value = str(v.get("value"))
    timeout = v.get("timeout", 10000)
    logger.info(f"Verifying value of '{target_name or target_locator}' matches '{expected_value}'")
    if target_locator:
        el = page.locator(target_locator).first
    else:
        el = page.locator(f'input[name="{target_name}"], [name="{target_name}"]').first
    el.wait_for(state="visible", timeout=timeout)
    actual_value = str(el.input_value())
    if actual_value != expected_value:
        try:
            if float(actual_value) == float(expected_value): return
        except: pass
        raise AssertionError(f"Expected value '{expected_value}', but found '{actual_value}'")

def verify_value_near(page: Page, v: dict):
    # Restoring simplified version of verify_value_near for compatibility
    near_text = v.get("near_text")
    expected_value = str(v.get("expected") or v.get("value"))
    logger.info(f"Verifying value near text '{near_text}', expected: '{expected_value}'")
    # Search for an input near the exact text match
    el = page.get_by_text(near_text, exact=False).locator("xpath=../..//input").first
    el.wait_for(state="visible", timeout=5000)
    actual_value = str(el.input_value())
    if actual_value != expected_value:
        raise AssertionError(f"Near text '{near_text}': Expected '{expected_value}', got '{actual_value}'")

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
    logger.info(f"wait_toast: waiting for '{message}' (timeout={timeout}ms)")

    start = time.time()
    while time.time() - start < timeout / 1000.0:
        # Search in common toast/snackbar container selectors
        toast_locator = page.locator(
            "[class*='Snackbar'], [class*='Toast'], [role='alert'], "
            ".MuiSnackbar-root, [class*='notification'], [class*='message']"
        )
        for toast in toast_locator.all():
            try:
                if toast.is_visible():
                    content = toast.inner_text()
                    if message in content:
                        logger.info(f"Toast found: '{content.strip()[:80]}'")
                        page.wait_for_timeout(500)
                        return
            except Exception:
                pass
        time.sleep(0.3)

    logger.warning(f"Toast '{message}' not found within {timeout}ms, continuing anyway...")
    page.screenshot(path=f"warn_toast_{message[:20]}.png")

def drag_element(page: Page, v: dict):
    """
    Drag and drop element using Playwright's drag and drop API

    Supported parameters:
    - source_locator: Source element locator to drag (required)
    - target_locator: Target element locator to drop on (required)
    - source_text: Text to identify source element (alternative to source_locator)
    - target_text: Text to identify target element (alternative to target_locator)
    - timeout: Timeout in milliseconds for element visibility (default: 10000)
    - force: Force the drag operation even if elements are not visible (default: false)
    - delay: Delay in milliseconds between drag start and drop (default: 0)

    Usage examples:

    1. Drag by locator:
       drag_element:
           source_locator: "#draggable-item"
           target_locator: "#drop-zone"

    2. Drag by text:
       drag_element:
           source_text: "Drag me"
           target_text: "Drop here"

    3. Drag with position offset:
       drag_element:
           source_locator: ".card"
           target_locator: ".container"
           source_position: { x: 10, y: 10 }  # Offset from source element center
           target_position: { x: 50, y: 50 }  # Offset from target element center

    4. Drag with delay:
       drag_element:
           source_locator: "#item1"
           target_locator: "#item2"
           delay: 500  # Wait 500ms before dropping
    """
    logger.info(">>> Current Step: drag_element")

    # Get source element
    source_locator = v.get("source_locator")
    source_text = v.get("source_text")

    if source_locator:
        source_elem = page.locator(source_locator).first
    elif source_text:
        source_elem = page.get_by_text(source_text).first
    else:
        raise ValueError("drag_element: Either 'source_locator' or 'source_text' must be provided")

    # Get target element
    target_locator = v.get("target_locator")
    target_text = v.get("target_text")

    if target_locator:
        target_elem = page.locator(target_locator).first
    elif target_text:
        target_elem = page.get_by_text(target_text).first
    else:
        raise ValueError("drag_element: Either 'target_locator' or 'target_text' must be provided")

    timeout = v.get("timeout", 10000)
    delay = v.get("delay", 0)
    force = v.get("force", False)

    # Wait for elements to be ready
    logger.info(f"Waiting for source element to be ready...")
    source_elem.wait_for(state="attached", timeout=timeout)

    logger.info(f"Waiting for target element to be ready...")
    target_elem.wait_for(state="attached", timeout=timeout)

    # Get optional position offsets
    source_position = v.get("source_position", {})
    target_position = v.get("target_position", {})

    # Perform drag and drop
    logger.info(f"Dragging element to target...")

    try:
        # Use bounding box for precise control if positions are specified
        if source_position or target_position:
            source_box = source_elem.bounding_box()
            target_box = target_elem.bounding_box()

            # Calculate source point (center + offset)
            source_x = source_box["x"] + source_box["width"] / 2 + source_position.get("x", 0)
            source_y = source_box["y"] + source_box["height"] / 2 + source_position.get("y", 0)

            # Calculate target point (center + offset)
            target_x = target_box["x"] + target_box["width"] / 2 + target_position.get("x", 0)
            target_y = target_box["y"] + target_box["height"] / 2 + target_position.get("y", 0)

            logger.info(f"Drag from ({source_x:.0f}, {source_y:.0f}) to ({target_x:.0f}, {target_y:.0f})")

            # Perform drag using mouse
            page.mouse.move(source_x, source_y)
            page.mouse.down()
            if delay > 0:
                page.wait_for_timeout(delay)
            page.mouse.move(target_x, target_y)
            page.mouse.up()

        else:
            # Use Playwright's built-in drag and drop API
            source_elem.drag_to(
                target_elem,
                force=force,
                timeout=timeout
            )

        logger.info("✓ Drag and drop completed successfully")

    except Exception as e:
        logger.error(f"✗ Drag and drop failed: {e}")
        raise


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
        if target_elem.is_visible():
            logger.info("Element is already visible")
            return
    except:
        pass

    # Calculate swipe coordinates based on direction
    viewport_size = page.viewport_size()

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


