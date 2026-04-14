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
    logger.info(f"Checking '{target_name or target_locator}' to {checked}")

    target_role = v.get("role")

    try:
        if target_locator:
            el = page.locator(target_locator).nth(v.get("index", 0))
            el.set_checked(checked, timeout=5000)
        elif target_role:
            page.get_by_role(target_role, name=target_name).nth(v.get("index", 0)).set_checked(checked, timeout=5000)
        else:
            page.get_by_label(target_name).nth(v.get("index", 0)).set_checked(checked, timeout=5000)
    except Exception as e:
        logger.error(f"Check failed: {e}")
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
    force = v.get("force", False) # Default to False for better event triggering
    
    # Validation
    if not target_name and not target_locator and not target_role:
        return

    logger.info(f"Click started for target: {target_name or target_locator or target_role}")

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
        # Standard locator attempt
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
    except Exception as e:
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

