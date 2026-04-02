import os
import re
from playwright.sync_api import Page, Locator, expect
from loguru import logger
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

    try:
        if target_locator:
            el = page.locator(target_locator).nth(v.get("index", 0))
            el.set_checked(checked, timeout=5000)
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
        fc.set_files(file_path)

def smart_click(page: Page, v: dict):
    if page.get_by_text("Something went wrong!", exact=True).is_visible():
        logger.error("Application Crashed!")
        raise Exception("Application Crashed")
        
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    target_index = v.get("index", 0)
    force = v.get("force", False)
    
    if "x" in v and "y" in v and not target_name and not target_locator and not target_role:
        logger.info(f"Click started for coordinates: ({v['x']}, {v['y']})")
        page.mouse.click(v["x"], v["y"])
        page.wait_for_timeout(1000)
        return

    if not target_name and not target_locator and not target_role:
        return

    logger.info(f"Click started for target: {target_name or target_locator or target_role}")

    # Scoping
    modals = page.locator("div[role='dialog'], .MuiDialog-root, .MuiModal-root").all()
    active_modal = None
    for m in reversed(modals):
        if m.is_visible():
            active_modal = m
            break
    root = active_modal if active_modal else page

    # 1. Traditional
    try:
        el = root.locator(target_locator).get_by_text(target_name, exact=target_exact).nth(target_index)
        el.click(force=force, timeout=10000)
        return
    except: pass

    try:
        if target_role:
            el = root.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
        elif target_name:
            el = root.get_by_text(target_name, exact=target_exact).nth(target_index)
        
        if el and el.is_visible(timeout=5000):
            el.click(force=force)
            return
    except: pass

    # 1.1 Global Fallback (In case modal scoping is confused)
    try:
        if target_role == 'button' or target_name == 'Add':
            logger.debug("Modal-scoped search failed. Trying global search for last visible button...")
            all_btns = page.get_by_role("button", name=target_name, exact=target_exact).all()
            for btn in reversed(all_btns):
                if btn.is_visible():
                    btn.click(force=force)
                    return
    except: pass

    # 1.5. Grace Period (Wait for modal animations)
    page.wait_for_timeout(3000)

    # 2. AI Pure Vision Fallback
    import os
    if v.get("disable_ai", False) or os.environ.get("AI_DISABLED") == "True":
        raise Exception(f"Element not found: {target_name or target_locator or target_role}")

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
            raise Exception("AI failed visually.")
    except Exception as e:
        logger.error(f"AI Healing Failed: {e}")
        raise e

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
    logger.info(f"Verifying text visibility: {text}")
    try:
        page.get_by_text(text, exact=v.get("exact", False)).first.wait_for(state="visible", timeout=timeout)
        logger.info(f"Text '{text}' is visible.")
    except Exception as e:
        page.screenshot(path=f"fail_verify_{text[:10]}.png")
        raise AssertionError(f"Text '{text}' not found.")

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

def execute_t3981_flow(page: Page, v):
    def scan_result_locator():
        return page.locator("text=Code Verified").or_(page.locator("text=Code Already Redeemed")).or_(page.locator("text=Redeemed")).first

    page.goto("https://s.pear.us/iyR93K")
    scan_result_locator().wait_for(state="visible", timeout=30000)
    page.get_by_role("button", name="Scan next ticket").click()
    page.wait_for_timeout(3000)
    scan_result_locator().wait_for(state="visible", timeout=30000)
