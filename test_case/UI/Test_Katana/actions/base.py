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
        params = v if isinstance(v, dict) else {}
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
        logger.info(">>> Auto-handling modals after page load")
        try:
            # Wait for page to fully render before detecting modals
            page.wait_for_timeout(1000)
            auto_handle_modals(page, {"timeout": 3000, "ignore_if_not_found": True})
        except Exception as e:
            # Failure in bullet layer processing does not affect the main process
            logger.debug(f"Auto modal handling skipped or failed: {e}")

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
    target_frame = v.get("frame") or v.get("frame_locator")
    target_role = v.get("role")
    target_index = v.get("index", 0)

    logger.info(f"Filling field '{target_name or target_locator}' with value '{target_value}' (frame: {target_frame})")
    fill_timeout = v.get("timeout", 10000)

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
                page.get_by_label(target_name, exact=False),
                page.get_by_placeholder(target_name, exact=False),
                page.locator(f"input[name*='{target_name}'], textarea[name*='{target_name}']")
            ]
            target_id = v.get("index", 0)
            filled = False
            for c in candidates:
                if c.nth(target_id).is_visible(timeout=2000):    # 加超时：原来无超时可能等 30s
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

def smart_add_cookies(page: Page, v: dict):
    """Inject cookies from a Playwright storage-state file into the current context.
    Caller is responsible for navigating to the partner URL after this call.
    """
    import json
    state_path = v.get("storage_state") or os.path.join(
        BASE_DIR, "test_case", "UI", "Test_Katana", "cookie_release.json"
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
    """Clear all cookies from the current context to switch to guest."""
    page.context.clear_cookies()
    logger.info("Cleared all cookies to switch back to guest context")

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

def _smart_click_core(page: Page, v: dict):
    """
    核心点击逻辑（不含 Page-level Search 和 AI 自愈）。
    smart_click 和 smart_click_scan 共用此核心函数。
    """
    # 优化：is_visible 加 5s 超时（原来无超时，可能等 30s）
    try:
        if page.get_by_text("Something went wrong!", exact=True).is_visible(timeout=5000):
            logger.error("Application Crashed!")
            raise Exception("Application Crashed")
    except: pass

    # Wait for loading overlays/backdrops to disappear before clicking anything
    # 优化：timeout 从 8s 降至 2s；用 detach 状态检测（不阻塞主流程）
    try:
        backdrop = page.locator(".MuiBackdrop-root, [class*='Backdrop'], .loading-overlay").first
        backdrop.wait_for(state="detached", timeout=2000)  # 2s 超时，避免卡住
    except: pass

    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    target_index = v.get("index", 0)
    target_test_id = v.get("test_id")
    force = v.get("force", False)
    optional = v.get("optional", False)
    skip_if_disabled = v.get("skip_if_disabled", False)
    skip_if_checked = v.get("skip_if_checked", False)

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
                candidate = page.get_by_text(target_name, exact=target_exact).nth(target_index)
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

    # Save / Publish: 优先 Playwright 快速定位，失败后再走 JS fallback
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

    # ---- 通用定位策略 1-4 ----
    # Restore standard scoping: if there is an active modal, restrict all searches to it by default.
    root = active_modal if active_modal else page

    # 1. Test ID
    if target_test_id:
        try:
            el = root.get_by_test_id(target_test_id).nth(target_index)
            if el.is_visible(timeout=5000):
                el.click(force=force)
                return
        except: pass

    # 2. Standard locator
    # 优化：直接 click()，不先 is_visible（Playwright click 内部自带检查）
    if target_locator:
        try:
            if target_locator.startswith("/") or target_locator.startswith("xpath="):
                xpath_locator = target_locator if target_locator.startswith("xpath=") else f"xpath={target_locator}"
                el = page.locator(xpath_locator).nth(target_index)
            else:
                # 修复: 自定义 CSS locator 退回使用全局 page.locator() 进行查找。
                # 由于这些 locator 通常是从 body/html 开始的完整特征路径，将它们约束在 active_modal 之下会导致层叠错误 (如 dialog 内部再找一个 dialog）。
                el = page.locator(target_locator).nth(target_index)

            if target_name:
                el = el.get_by_text(target_name, exact=target_exact)
            el.click(force=force, timeout=5000)  # 直接点击，不先 is_visible
            logger.info(f"Clicked via locator: {target_name or target_locator}")
            return
        except Exception as e:
            if optional:
                logger.info(f"Optional click: locator attempt failed for index {target_index}, skipping. ({e})")
                return
            logger.debug(f"Locator attempt failed: {e}")

    # 3. Aria-label fallback（按钮很少有 aria-label，timeout 极短，避免白等）
    if target_name:
        try:
            el = root.locator(f'button[aria-label="{target_name}"], [aria-label*="{target_name}"]').nth(target_index)
            el.click(force=force, timeout=3000)  # 直接点击
            logger.info(f"Clicked via aria-label fallback: {target_name}")
            return
        except: pass

    # 4. Role / text fallback
    # 优化：移除 scroll_into_view_if_needed（会阻塞且浪费时间）
    # - Playwright click() 内部自带滚动，不需要显式 scroll
    # - 直接 click()，失败再 force
    try:
        if target_role:
            el = root.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
        elif target_name:
            el = root.get_by_text(target_name, exact=target_exact).nth(target_index)
        if el:
            # 先尝试正常点击（Playwright click 内部自带 scroll + 可见性检查）
            try:
                el.click(timeout=5000)  # 5s 超时，不 force
                logger.info(f"Clicked '{target_name}'")
                if target_role == 'option':
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
                return
            except Exception as click_e:
                logger.debug(f"Normal click failed ({click_e}), trying force...")

            # 点击失败，尝试 force（跳过所有检查）
            try:
                el.click(force=True, timeout=3000)
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

    raise Exception(f"smart_click: element not found: {target_name or target_locator}")


def smart_click(page: Page, v: dict):
    """
    快速点击 — 仅使用传统 Playwright 定位策略。

    参数：
        fallback_scan: bool, 默认为 False。
            - False: 精准定位失败后直接抛出异常，不触发 Page-level Search。
                      **适用于 95% 的普通用例，获得最优性能。**
            - True:  精准定位失败后，触发 Page-level Search + AI 自愈兜底。
                      **适用于弹窗嵌套、多层遮罩等传统定位困难的场景。**

    YAML 用法示例：
        # 普通点击（快速）
        click_save: { name: 'Save' }

        # 困难场景（带 Page-level Search，耗时但更稳定）
        click_save: { name: 'Save', fallback_scan: true }

        # 困难场景（显式名称，语义更清晰）
        R_click_save_hard: { name: 'Save', fallback_scan: true }
    """
    try:
        _smart_click_core(page, v)
        return  # 核心定位成功，直接返回
    except Exception as primary_error:
        if not v.get("fallback_scan", False):
            # fallback_scan=False（默认）：精准定位失败 → 直接抛异常，不拖泥带水
            logger.debug(f"smart_click (fast): {primary_error}")
            raise primary_error

        # fallback_scan=True：进入 Page-level Search + AI 兜底链路
        _smart_click_with_fallback(page, v, primary_error)


def _smart_click_with_fallback(page: Page, v, primary_error):
    """
    完整兜底点击 — 包含 Page-level Search 和 AI 自愈。
    仅在 fallback_scan=True 时由 smart_click 调用。
    """
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    optional = v.get("optional", False)

    logger.info(f"smart_click (fallback_scan=True): Page-level Search triggered for '{target_name or target_role}'")

    # ---- 5. Page-level Search: 全页面按钮枚举 ----
    # 优化：is_visible 超时从 2000ms 降至 500ms，减少等待时间
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
                        # 优化：无超时，快速判断可见性 (避免每个隐藏元素阻塞 500ms)
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
                        if btn.is_visible(timeout=1000):           # 优化：加 1s 超时（原来无超时等 30s）
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
        if close_btn.is_visible(timeout=3000):            # 加超时：原来无超时可能等 30s
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
            if el.is_visible(timeout=3000):                   # 加超时：原来无超时可能等 30s
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
                if toast.is_visible(timeout=1000):        # 加超时：原来无超时可能等 30s/个
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
        if target_elem.is_visible(timeout=3000):           # 加超时：原来无超时可能等 30s
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
                    
                # 在每个 frame 中尝试填写
                fields_to_fill = [
                    ("cardnumber", card_number),
                    ("exp-date", expiry),
                    ("cvc", cvc),
                ]
                
                for name, value in fields_to_fill:
                    if value:
                        try:
                            # 使用 focus + type 方法，而不是 fill
                            el = frame.locator(f'input[name="{name}"]')
                            if el.count() > 0:
                                el.click(timeout=3000)
                                el.fill(value, timeout=timeout_ms)
                                logger.info(f"fill_stripe_iframe: filled {name} in frame")
                                filled_count += 1
                        except Exception as e:
                            pass  # 静默失败，尝试下一个 frame
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
        # 截图以便调试
        page.screenshot(path="stripe_iframe_debug.png")

    # 填写主页面字段
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

    # 填写 card name 和 zipcode（这些通常在主页面，不在 iframe 里）
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








def smart_click_optional(page: Page, v: dict):
    """
    可选点击 — 元素不存在时静默跳过，不报错。
    专用于处理"可能出现也可能不出现"的弹框/提示。

    YAML 用法：
        R_click_done: { role: 'button', name: 'Done' }

    与 smart_click + optional: true 的区别：
    - smart_click 的 optional 只在 target_locator 路径生效
    - smart_click_optional 在所有定位策略上都支持 optional 跳过
    """
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
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

    # Find visible modal/tooltip scopes (从后往前遍历，最新的弹框优先)
    # 支持: dialog, modal, tooltip, popover 等浮动层
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
        """在指定范围内查找并点击元素"""
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

    # 搜索策略：先弹框（从后往前，新的弹框优先），再 page 级别
    # 这样做是因为弹框通常包含用户正在操作的元素

    # 1. 先在所有可见弹框中尝试（从后往前，最新的弹框优先）
    for modal in reversed(visible_modals):
        if _find_and_click_in_scope(modal, f"modal[{visible_modals.index(modal)}]:"):
            return

    # 2. 最后在 page 级别尝试（处理没有弹框的情况）
    if _find_and_click_in_scope(page, "page:"):
        return

    # Element not found — silent skip
    logger.info(f"smart_click_optional: element not found '{target_name or target_locator}', skipping.")


def smart_click_retry(page: Page, v: dict):
    """
    带重试的稳定点击 — 元素一定存在但点击不稳定时使用。

    与 smart_click_optional 的区别：
    - smart_click_optional: 找不到元素就跳过（用于可能不存在的元素）
    - smart_click_retry: 元素一定存在，失败时自动重试（用于稳定存在的元素）

    YAML 用法：
        smart_click_retry_publish: { role: 'button', name: 'Publish', retry: 3, delay: 500 }

    新增参数：
    - retry: 重试次数，默认 3
    - delay: 重试间隔(ms)，默认 500
    """
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    target_index = v.get("index", 0)
    target_test_id = v.get("test_id")
    force = v.get("force", False)
    timeout = v.get("timeout", 5000)
    retry_count = v.get("retry", 3)
    delay_ms = v.get("delay", 500)

    # Find visible modal/tooltip scopes (从后往前遍历，最新的弹框优先)
    # 支持: dialog, modal, tooltip, popover 等浮动层
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
        """在指定范围内查找元素"""
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
        """遍历所有可见弹框 + page 查找元素"""
        # 1. 先在所有可见弹框中尝试（从后往前，最新的弹框优先）
        for modal in reversed(visible_modals):
            el = _find_element_in_scope(modal)
            if el is not None:
                return el
        # 2. 最后在 page 级别尝试
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

            # 等待元素动画完成后再点击
            page.wait_for_timeout(200)

            # 点击（Playwright 的 click 本身会等待元素可点击）
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
                if modal_locator.is_visible(timeout=1000):
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
            return
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
    else:
        logger.warning("⚠ No buttons were clicked in modal")
        if not ignore_if_not_found:
            page.screenshot(path="modal_button_not_found.png")
            raise AssertionError("No clickable buttons found in modal")


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
    max_iterations = v.get("max_iterations", 3)

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
            ]
        },
        # Notification toasts
        {
            "modal_identifiers": [
                {"class": "MuiSnackbar-root"},
                {"class": "toast"},
                {"role": "alert"},
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
                handle_modal(page, {
                    **modal_config,
                    "timeout": timeout,
                    "ignore_if_not_found": True,
                    "wait_before_click": 1000
                })
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
            page.wait_for_timeout(500)
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

        # Navigate to URL if provided
        url = v.get("url")
        if url:
            timeout = v.get("timeout", 30000)
            logger.info(f"Session '{session_name}' navigating to: {url}")
            new_page.goto(url, timeout=timeout)
            logger.info(f"✓ Session '{session_name}' loaded")

        # Store session
        page._sessions[session_name] = {
            "page": new_page,
            "context": new_context,
            "parent_session": page._active_session,
            "url": new_page.url
        }

        # Set as active session
        page._active_session = session_name
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

    if not hasattr(page, "_sessions") or session_name not in page._sessions:
        raise ValueError(f"Session '{session_name}' not found. Available sessions: {list(page._sessions.keys()) if hasattr(page, '_sessions') else []}")

    # Set as active session
    page._active_session = session_name
    session = page._sessions[session_name]

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

    if not hasattr(page, "_sessions") or session_name not in page._sessions:
        logger.warning(f"Session '{session_name}' not found")
        return

    session = page._sessions[session_name]

    try:
        # Close the page and context
        session["context"].close()
        del page._sessions[session_name]

        # If we closed the active session, switch to parent or default
        if page._active_session == session_name:
            parent_session = session.get("parent_session")
            page._active_session = parent_session if parent_session else None

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
        cookie_file: Path to cookie JSON file

    Raises:
        FileNotFoundError: If cookie file doesn't exist
        ValueError: If cookie file format is invalid
    """
    import json
    import os

    if not os.path.exists(cookie_file):
        raise FileNotFoundError(f"Cookie file not found: {cookie_file}")

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

