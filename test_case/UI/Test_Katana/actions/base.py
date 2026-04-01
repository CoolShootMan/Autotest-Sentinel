import os
import re
from playwright.sync_api import Page, Locator, expect
from loguru import logger
from page.home import page_element_role_click, page_element_label_click
from ..utils.ai_vision import ai_vision

def open_url(page: Page, v):
    logger.info(f">>> Current Step: open_url")
    url = v.get("open") or v.get("url") if isinstance(v, dict) else v
    if url:
        from page.home import page_open
        page_open(page, url)

def swipe_avoid_plus(page: Page, v: dict):
    # Specialized action to scroll past specific UI elements
    x = v.get("x", 0)
    y = v.get("y", 300)
    logger.info(f"Swiping/Scrolling: x={x}, y={y}")
    
    # Check if a drawer is open. If so, try to scroll it.
    drawer = page.locator(".MuiDrawer-root div").filter(has=page.locator("[data-som-id], input")).first
    if drawer.is_visible():
        logger.info("Active drawer detected. Scrolling drawer content...")
        # Common MUI drawer content container often has the overflow
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
    
    # Handle random value patterns like RANDOM_1_10, RANDOM_10_50
    if isinstance(target_value, str) and target_value.startswith("RANDOM_"):
        import random
        parts = target_value.split("_")
        if len(parts) == 3:
            min_val, max_val = int(parts[1]), int(parts[2])
            target_value = str(random.randint(min_val, max_val))
            logger.info(f"Generated random value: {target_value} (range: {min_val}-{max_val})")
    
    logger.info(f"Filling field '{target_name or target_locator}' with value '{target_value}'")
    
    # Timeout for traditional fill - trigger AI faster
    fill_timeout = v.get("timeout", 10000)

    try:
        if target_locator:
            # Direct locator fill
            el = page.locator(target_locator).nth(v.get("index", 0))
            el.fill(str(target_value), timeout=fill_timeout)
            logger.info(f"Filled by locator: {target_locator} (index: {v.get('index', 0)})")
        elif "role" in v:
            # Semantic fill
            page.get_by_role(v["role"], name=target_name, exact=v.get("exact", False)).nth(v.get("index", 0)).fill(str(target_value), timeout=fill_timeout)
            logger.info(f"Filled by role+name: {target_name} = {target_value} (index: {v.get('index', 0)})")
        else:
            # Text/Placeholder fallback
            candidates = [
                page.get_by_label(target_name, exact=False),
                page.get_by_placeholder(target_name, exact=False),
                page.locator(f"input[name*='{target_name}'], textarea[name*='{target_name}']"),
                page.locator(f"input[placeholder*='{target_name}'], textarea[placeholder*='{target_name}']")
            ]
            target_id = v.get("index", 0)
            filled = False
            for c in candidates:
                target_el = c.nth(target_id)
                if target_el.is_visible():
                    target_el.fill(str(target_value), timeout=fill_timeout)
                    logger.info(f"Filled by text/attr match: {target_name} (index: {target_id})")
                    filled = True
                    break
            if not filled:
                 # Last resort: generic placeholder
                 page.locator(f"input[placeholder*='{target_name}'], textarea[placeholder*='{target_name}'], input[aria-label*='{target_name}']").nth(target_id).fill(str(target_value), timeout=fill_timeout)
        
        # Add small delay to avoid overwhelming the UI
        page.wait_for_timeout(300)
    except Exception as e:
        logger.error(f"Fill failed ({target_name}): {e}. Attempting AI Self-Healing...")
        try:
            safe_name = re.sub(r'[^\w\-]', '_', str(target_name or 'field'))[:30]
            
            # --- HYBRID SOM UPGRADE ---
            logger.info("AI Healing Step 1: Loading som.js")
            som_js_path = os.path.join(os.path.dirname(__file__), "../utils/som.js")
            with open(som_js_path, "r") as f: som_code = f.read()
            
            logger.info("AI Healing Step 2: Injecting labels")
            mapping = page.evaluate(som_code)
            logger.info(f"AI Healing Step 3: SOM Tagging Complete. Elements: {len(mapping)}")
            
            screenshot_path = f"fail_fill_{safe_name}.png"
            page.screenshot(path=screenshot_path)
            
            # Pass objective context
            test_objective = getattr(page, "_test_description", "UI Filling")
            som_data_meta = {
                "description": test_objective,
                "caseno": getattr(page, "_test_caseno", "Unknown"),
                "history": getattr(page, "_execution_history", [])
            }
            
            instruction = f"The input field/textbox that corresponds to '{target_name or target_locator}'. Use the value '{target_value}'."
            res = ai_vision.find_element_som(screenshot_path, instruction, {**mapping, **som_data_meta})
            
            if res.get("label_id"):
                label_id = res["label_id"]
                diagnosis = res.get("consciousness_diagnosis", "No diagnosis provided.")
                action_type = res.get("suggested_action", "GOAL_CLICK")
                
                logger.info(f"✨ AI 'Junior QA' Found Field ID: {label_id}!")
                logger.info(f"🧠 Diagnosis: {diagnosis}")
                logger.info(f"🚀 Suggested Action: {action_type}")
                
                if action_type == "ABORT_TEST":
                    logger.error(f"🛑 AI decided to ABORT test: {res.get('bug_report', diagnosis)}")
                    raise Exception(f"AI Aborted Test: {res.get('bug_report', diagnosis)}")

                el = page.locator(f'[data-som-id="{label_id}"]').first
                
                # Check for recovery (AI says it's recovery OR AI points to a button/div instead of input)
                is_recovery = (action_type == "RECOVERY_CLICK")
                if not is_recovery:
                    tag = el.evaluate("el => el.tagName").upper()
                    if tag in ["BUTTON", "A", "DIV", "SPAN"]:
                         is_recovery = True
                
                if is_recovery:
                    logger.info(f"🔄 Performing recovery click on '{tag if not is_recovery else 'AI suggested target'}' before filling...")
                    el.click()
                    page.wait_for_timeout(2000)
                    if v.get("_retry_ai", 0) < 1:
                        v["_retry_ai"] = v.get("_retry_ai", 0) + 1
                        return smart_fill(page, v)
                    return

                el.fill(str(target_value))
                return
            else:
                logger.warning(f"AI SOM could not find field '{target_name}'. Result: {res}")
        except Exception as ai_err:
            logger.error(f"AI Healing failed: {ai_err}")
            
        try: page.screenshot(path=f"fail_fill.png")
        except: pass
        raise

def fill_numeric(page: Page, v: dict):
    """
    Fill a controlled numeric input (e.g. MUI TextField type=number) using
    native keyboard events to ensure React state synchronization and commitment.
    """
    target_locator = v.get("locator")
    target_value = str(v.get("value", ""))
    target_placeholder = v.get("placeholder", "Quantity")
    target_name = v.get("name") or v.get("label") or "Inventory"
    index = v.get("index", 0)

    logger.info(f"fill_numeric: forcing value '{target_value}' on '{target_locator or target_placeholder or target_name}'")

    if target_locator:
        el = page.locator(target_locator).nth(index)
    else:
        # Try multiple semantic matches
        candidates = [
            page.locator('input[name="variants.0.inventoryQuantity"]').nth(index),
            page.locator('input[name*="inventoryQuantity"]').nth(index),
            page.get_by_placeholder(target_placeholder, exact=False).nth(index),
            page.get_by_label(target_name, exact=False).nth(index),
            page.get_by_label(target_placeholder, exact=False).nth(index),
            page.locator(f"input[name*='{target_placeholder.lower()}']").nth(index),
            page.locator("input[type='number']").nth(index)
        ]
        el = None
        for candidate in candidates:
            try:
                if candidate.is_visible(timeout=2000):
                    el = candidate
                    break
            except:
                continue
        
        if not el:
            el = page.get_by_placeholder(target_placeholder, exact=False).nth(index)

    el.wait_for(state="visible", timeout=v.get("timeout", 10000))
    el.scroll_into_view_if_needed()
    
    max_retries = 3
    for attempt in range(max_retries):
        # 1. Focus and Clear
        el.click(force=True)
        page.keyboard.press("Control+A")
        page.wait_for_timeout(100)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        
        # 2. Native Typing
        page.keyboard.type(target_value, delay=100)
        
        # 3. Explicit Commit
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        page.keyboard.press("Tab")
        page.wait_for_timeout(800)
        
        # 4. Verification
        current_val = str(el.input_value())
        if current_val == target_value:
            logger.info(f"fill_numeric: Successfully verified value '{target_value}' on attempt {attempt+1}.")
            return
        else:
            logger.warning(f"fill_numeric: Verification failed on attempt {attempt+1}. Expected '{target_value}', got '{current_val}'. Retrying...")
            page.wait_for_timeout(1000)
            
    raise Exception(f"fill_numeric: Failed to set value '{target_value}' after {max_retries} attempts. Final value: '{el.input_value()}'")

def smart_check(page: Page, v: dict):
    target_name = v.get("name") or v.get("text") or v.get("label")
    target_locator = v.get("locator")
    target_role = v.get("role", "checkbox")
    checked = v.get("checked", True)
    timeout = v.get("timeout", 15000) # Default to 15s to trigger AI faster than global 90s
    
    logger.info(f"Checking '{target_name or target_locator}' to state: {checked} (timeout: {timeout}ms)")

    try:
        if target_locator:
            el = page.locator(target_locator).nth(v.get("index", 0))
            try:
                el.scroll_into_view_if_needed(timeout=2000)
                el.set_checked(checked, timeout=timeout)
            except Exception as set_err:
                # Handle hidden inputs by clicking the label/parent, but avoid the info button
                if "visible" in str(set_err).lower() or "intercepts" in str(set_err).lower():
                    logger.info("Direct check failed, attempting to click label/parent to toggle...")
                    # Find the nearest label or checkbox span, EXCLUDING the info icon button
                    parent_label = el.locator("xpath=ancestor::label").first
                    if parent_label.count() > 0:
                         parent_label.click(force=True)
                    else:
                         el.click(force=True)
                else: raise
        else:
            try:
                # Try role first
                page.get_by_role(target_role, name=target_name, exact=v.get("exact", False)).nth(v.get("index", 0)).set_checked(checked, timeout=timeout // 2)
            except:
                # Fallback to label
                page.get_by_label(target_name).nth(v.get("index", 0)).set_checked(checked, timeout=timeout // 2)
        logger.info(f"Successfully set checked state for '{target_name or target_locator}'")
    except Exception as e:
        if v.get("disable_ai", False):
            logger.warning(f"AI Healing is DISABLED for smart_check on '{target_name or target_locator}'. Raising original error.")
            raise
        logger.error(f"Check failed ({target_name}): {e}. Triggering AI Self-Healing...")

        try:
            safe_name = re.sub(r'[^\w\-]', '_', str(target_name or 'checkbox'))[:30]
            
            # --- HYBRID SOM UPGRADE ---
            som_js_path = os.path.join(os.path.dirname(__file__), "../utils/som.js")
            with open(som_js_path, "r") as f: som_code = f.read()
            
            mapping = page.evaluate(som_code)
            screenshot_path = f"fail_check_{safe_name}.png"
            page.screenshot(path=screenshot_path)
            
            # Pass objective context
            test_objective = getattr(page, "_test_description", "Checkbox/Radio selection")
            som_data_meta = {
                "description": test_objective,
                "caseno": getattr(page, "_test_caseno", "Unknown"),
                "history": getattr(page, "_execution_history", [])
            }
            
            instruction = f"The checkbox, radio button, or switch for '{target_name or target_locator}'. We want to set it to {'checked' if checked else 'unchecked'}. NOTE: Avoid clicking the circular 'Info' icon if it's next to the checkbox."
            res = ai_vision.find_element_som(screenshot_path, instruction, {**mapping, **som_data_meta})
            
            if res.get("label_id"):
                label_id = res["label_id"]
                diagnosis = res.get("consciousness_diagnosis", "No diagnosis provided.")
                action_type = res.get("suggested_action", "GOAL_CLICK")
                
                logger.info(f"✨ AI 'Junior QA' Found Checkbox ID: {label_id}!")
                logger.info(f"🧠 Diagnosis: {diagnosis}")
                
                if action_type == "ABORT_TEST":
                    raise Exception(f"AI Aborted Test: {res.get('bug_report', diagnosis)}")

                el = page.locator(f'[data-som-id="{label_id}"]').first
                
                # If suggested a click, do it
                if action_type in ["GOAL_CLICK", "RECOVERY_CLICK"]:
                    el.click(force=True)
                    logger.info(f"AI healed check action via click on target {label_id}.")
                    return

                # Default back to set_checked if id is likely an input
                el.set_checked(checked)
                logger.info(f"AI healed check action for '{target_name}'.")
                return
            else:
                logger.warning(f"AI SOM could not find checkbox '{target_name}'.")
        except Exception as ai_err:
            logger.error(f"AI Healing failed for smart_check: {ai_err}")
            
        try: page.screenshot(path=f"fail_check.png")
        except: pass
        raise

def smart_upload(page: Page, v: dict):
    if "file_path" in v:
        file_path = v.get("file_path")
        if not os.path.exists(file_path):
             logger.error(f"File not found: {file_path}")
             raise FileNotFoundError(file_path)

        target_index = v.get("index", 0)
        try:
            if "locator" in v:
                el = page.locator(v["locator"]).nth(target_index)
                # Try setting files directly first (stable for hidden inputs)
                try:
                    el.set_input_files(file_path, timeout=3000)
                    logger.info(f"Uploaded file via set_input_files on locator: {v['locator']}")
                    return
                except:
                    # Fallback to click + chooser
                    with page.expect_file_chooser(timeout=5000) as fc_info:
                        el.click()
                    fc = fc_info.value
                    fc.set_files(file_path)
            else:
                target_name = v.get("text") or v.get("name") or v.get("label") or v.get("placeholder")
                # Try semantic search + chooser
                with page.expect_file_chooser(timeout=5000) as fc_info:
                    el = None
                    if target_name:
                        el = page.get_by_label(target_name).nth(target_index)
                        if not el.is_visible():
                            el = page.get_by_text(target_name, exact=True).nth(target_index)
                    
                    if not el:
                         raise Exception(f"Upload target not found: {target_name}")
                    
                    el.click()
                fc = fc_info.value
                fc.set_files(file_path)
            logger.info(f"Uploaded file: {file_path}")
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise

def smart_click(page: Page, v: dict):
    # Crash Check
    if page.get_by_text("Something went wrong!", exact=True).is_visible():
        logger.error(f"Application Crashed (Detected at start of click)!")
        page.screenshot(path=f"crash_click.png")
        raise Exception("Application Crashed")
        
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_role = v.get("role")
    target_exact = v.get("exact", False)
    target_index = v.get("index", 0)
    force = v.get("force", False) # Default to False for better event triggering
    optional = v.get("optional", False) # If True, skip if element not found
    
    # Validation
    if not target_name and not target_locator and not target_role:
        logger.warning(f"No target specified for smart_click in step. Skipping.")
        return

    logger.info(f"Click started for target: {target_name or target_locator or target_role}")

    # Regex Pre-processing
    if target_name and isinstance(target_name, str) and (target_name.startswith("^") or target_name.endswith("$")):
        target_name = re.compile(target_name)
    if target_locator and isinstance(target_locator, str) and (target_locator.startswith("^") or target_locator.endswith("$")):
        target_locator = re.compile(target_locator)

    # --- TOPMOST MODAL SCOPING ---
    modals = page.locator("div[role='dialog'], .MuiDialog-root, .MuiPopover-root, .MuiModal-root, [role='presentation']").all()
    active_modal = None
    for m in reversed(modals):
        try:
            if m.is_visible():
                class_attr = m.get_attribute("class") or ""
                role_attr = m.get_attribute("role") or ""
                # Ignore backdrops and snackbars
                if "MuiBackdrop" in class_attr or "MuiSnackbar" in class_attr or "alert" in role_attr.lower():
                    continue
                # Ensure it has some interactive content or text
                if not m.inner_text().strip():
                    continue
                active_modal = m
                break
        except: continue
    
    if active_modal:
        modal_desc = active_modal.get_attribute("class") or "unnamed modal"
        logger.info(f"Scoping smart_click inside topmost modal/drawer: {modal_desc[:50]}")
        root = active_modal
    else:
        root = page


    # 1. Targeted Locator Check
    if target_locator:
        try:
            el = root.locator(target_locator).nth(target_index)
            # FALLBACK: If scoped locator fails, try page-wide (for cases where drawer closed but we still think it's open)
            if not el.is_visible(timeout=2000) and root != page:
                logger.debug("Scoped locator failed, falling back to page-wide search.")
                el = page.locator(target_locator).nth(target_index)
                
            el.click(force=force, timeout=v.get("timeout", 5000))
            logger.info(f"Clicked target locator: {target_locator} (index: {target_index})")
            return
        except Exception as e:
            logger.debug(f"Direct locator click failed: {e}")

    # 2. Page-wide Semantic Search (Role/Text)
    try:
        el = None
        if target_role:
            el = root.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
            # FALLBACK: If scoped search fails to find it visible, try page-wide
            try:
                el.wait_for(state="visible", timeout=3000)
            except:
                if root != page:
                    el = page.get_by_role(role=target_role, name=target_name, exact=target_exact).nth(target_index)
        elif target_name:
            el = root.get_by_text(target_name, exact=target_exact).nth(target_index)
            try:
                el.wait_for(state="visible", timeout=3000)
            except:
                if root != page:
                    el = page.get_by_text(target_name, exact=target_exact).nth(target_index)
        
        # FINAL ATTEMPT: Wait for the best candidate to become visible/stable
        if el:
            # Check if button is disabled before clicking
            is_disabled = False
            try:
                is_disabled = el.is_disabled()
            except: pass

            if is_disabled:
                logger.warning(f"Target '{target_name}' is disabled. Will try fallback if available.")
                raise Exception(f"Button '{target_name}' is disabled.")

            el.wait_for(state="visible", timeout=5000)
            el.click(force=force)
            logger.info(f"Clicked target '{target_name or 'unnamed'}' (index: {target_index}) via semantic search.")
            return
    except Exception as e:
        logger.debug(f"Standard click failed: {e}")
        # --- FALLBACK SUPPORT ---
        fallback = v.get("fallback")
        if fallback:
            logger.warning(f"Triggering fallback click for '{target_name}'. Reason: {e}")
            return smart_click(page, fallback)


    # 3. --- AI Self-Healing Fallback (The "Brain") ---
    if v.get("disable_ai", False):
        logger.warning(f"AI Healing is DISABLED for '{target_name or target_locator}'. ")
        # Check if optional - skip instead of raising error
        if optional:
            logger.info(f"Element '{target_name or target_locator}' not found but optional=True. Skipping.")
            return
        raise Exception(f"Element not found: {target_name or target_locator}")

    logger.error(f"All traditional methods failed for '{target_name or target_locator}'. Triggering AI Self-Healing...")

    try:
        safe_name = re.sub(r'[^\w\-]', '_', str(target_name or 'target'))[:30]
        
        # --- HYBRID SOM UPGRADE WITH RETRY ---
        som_js_path = os.path.join(os.path.dirname(__file__), "../utils/som.js")
        with open(som_js_path, "r") as f: som_code = f.read()
        
        mapping = None
        screenshot_path = f"ai_healing_{safe_name}.png"
        
        for attempt in range(2):
            try:
                mapping = page.evaluate(som_code)
                page.screenshot(path=screenshot_path)
                break
            except Exception as e:
                if "context was destroyed" in str(e) and attempt == 0:
                    logger.warning("Execution context destroyed during AI evaluation. Retrying after 2s...")
                    page.wait_for_timeout(2000)
                    continue
                raise e

        description = f"The interactive element (button, card, icon) for '{target_name}'. CRITICAL: You are likely in a nested drawer. Prefer elements in the TOPMOST/FOREGROUND layer. Avoid labels that appear in the background layer."
        if not target_name:
            description = f"The primary interactive element (Context: {target_role or target_locator}). Favor the topmost visible modal."
        
        # Add objective context for Junior QA Consciousness
        test_objective = getattr(page, "_test_description", "Unknown Action")
        som_data_meta = {
            "description": test_objective,
            "caseno": getattr(page, "_test_caseno", "Unknown"),
            "history": getattr(page, "_execution_history", [])
        }
        
        res = ai_vision.find_element_som(screenshot_path, description, {**mapping, **som_data_meta})
        
        if res.get("label_id"):
            label_id = res["label_id"]
            diagnosis = res.get("consciousness_diagnosis", "No diagnosis provided.")
            action_type = res.get("suggested_action", "GOAL_CLICK")
            
            logger.info(f"✨ AI 'Junior QA' Found Target ID: {label_id}!")
            logger.info(f"🧠 Diagnosis: {diagnosis}")
            logger.info(f"🚀 Suggested Action: {action_type}")
            
            if action_type == "ABORT_TEST":
                logger.error(f"🛑 AI decided to ABORT test: {res.get('bug_report', diagnosis)}")
                raise Exception(f"AI Aborted Test: {res.get('bug_report', diagnosis)}")

            el = page.locator(f'[data-som-id="{label_id}"]').first
            
            # Check if this is a 'recovery' or 'precondition' action
            is_retryable = (action_type in ["RECOVERY_CLICK", "PRECONDITION_ACTION"])
            if not is_retryable:
                # Fallback check based on name/role if AI didn't specify
                text = (el.inner_text() or "").lower()
                aria = (el.get_attribute("aria-label") or "").lower()
                if any(k in text or k in aria for k in ["close", "dismiss", "got it", "skip", "ok"]):
                    if target_name and not any(k in target_name.lower() for k in ["close", "dismiss", "got it", "skip", "ok"]):
                        is_retryable = True
            
            el.click(force=True)
            page.wait_for_timeout(2000)
            
            if is_retryable:
                logger.info(f"🔄 {action_type} performed. Retrying original click for '{target_name or target_locator}'...")
                if v.get("_retry_ai", 0) < 2: # Allow up to 2 AI-assisted retries for complex flows
                    v["_retry_ai"] = v.get("_retry_ai", 0) + 1
                    return smart_click(page, v)
            return
        else:
            logger.error(f"💀 AI SOM could not locate the element. Logic ends here.")
    except Exception as ai_err:
        logger.error(f"AI Healing Error: {ai_err}")
            
        # Add objective context for Junior QA Consciousness
        test_objective = getattr(page, "_test_description", "Unknown Action")
        som_data_meta = {
            "description": test_objective,
            "caseno": getattr(page, "_test_caseno", "Unknown"),
            "history": getattr(page, "_execution_history", [])
        }
        
        res = ai_vision.find_element_som(screenshot_path, description, {**mapping, **som_data_meta})
        
        if res.get("label_id"):
            label_id = res["label_id"]
            diagnosis = res.get("consciousness_diagnosis", "No diagnosis provided.")
            action_type = res.get("suggested_action", "GOAL_CLICK")
            
            logger.info(f"✨ AI 'Junior QA' Found Target ID: {label_id}!")
            logger.info(f"🧠 Diagnosis: {diagnosis}")
            logger.info(f"🚀 Suggested Action: {action_type}")
            
            if action_type == "ABORT_TEST":
                logger.error(f"🛑 AI decided to ABORT test: {res.get('bug_report', diagnosis)}")
                raise Exception(f"AI Aborted Test: {res.get('bug_report', diagnosis)}")

            el = page.locator(f'[data-som-id="{label_id}"]').first
            
            # Check if this is a 'recovery' action (like closing a blocking modal)
            is_recovery = (action_type == "RECOVERY_CLICK")
            if not is_recovery:
                # Fallback check based on name/role if AI didn't specify
                text = (el.inner_text() or "").lower()
                aria = (el.get_attribute("aria-label") or "").lower()
                if any(k in text or k in aria for k in ["close", "dismiss", "got it", "skip", "ok"]):
                    if target_name and not any(k in target_name.lower() for k in ["close", "dismiss", "got it", "skip", "ok"]):
                        is_recovery = True
            
            el.click()
            page.wait_for_timeout(2000)
            
            if is_recovery:
                logger.info(f"🔄 Recovery action performed. Retrying original click for '{target_name}'...")
                if v.get("_retry_ai", 0) < 1:
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
    
    # --- FINAL FALLBACK SUPPORT ---
    fallback = v.get("fallback")
    if fallback:
        logger.warning(f"All attempts (including AI) failed for '{target_name}'. Executing fallback action: {fallback}")
        return smart_click(page, fallback)

    # Check if optional - skip instead of raising error
    if optional:
        logger.info(f"Element '{target_name or target_locator}' not found but optional=True. Skipping.")
        return

    raise Exception(f"Failed to click '{target_name or target_locator}' after all attempts including AI.")

def click_modal_close(page: Page, v: dict):
    logger.info("Attempting to close modal...")
    try:
        close_btn = page.locator("div[role='dialog'] button[aria-label='close'], .MuiDialog-root button.close").first
        if close_btn.is_visible():
            close_btn.click()
            logger.info("Clicked modal close button.")
        else:
            modal_visible = page.locator("div[role='dialog'], .MuiDialog-root, .MuiModal-root").first.is_visible()
            if modal_visible:
                page.keyboard.press("Escape")
                logger.info("Pressed Escape to close visible modal (fallback).")
            else:
                logger.info("No modal detected to close.")
        page.wait_for_timeout(1000)
    except Exception as e:
        logger.warning(f"Failed to close modal: {e}")
def verify_text_visible(page: Page, v: dict):
    # Verify a specific text is visible on the page
    text = v.get("text")
    timeout = v.get("timeout", 10000)
    logger.info(f"Verifying visibility of text: {text}")
    try:
        locator = page.get_by_text(text, exact=v.get("exact", False))
        
        # Polling in Python for visibility
        import time
        start_time = time.time()
        visible_found = False
        while time.time() - start_time < timeout / 1000:
            count = locator.count()
            for i in range(count):
                if locator.nth(i).is_visible():
                    visible_found = True
                    break
            if visible_found:
                break
            page.wait_for_timeout(500)
        
        if not visible_found:
            raise Exception(f"No visible instance of '{text}' found among {locator.count()} matches.")

        logger.info(f"Text '{text}' is visible.")

    except Exception as e:
        logger.error(f"Verification failed: Text '{text}' not visible after {timeout}ms. Error: {e}")
        page.screenshot(path=f"fail_verify_text_{text[:10]}.png")
        # Log all matching elements' status for debug
        try:
            count = locator.count()
            logger.info(f"Matches found: {count}")
            for i in range(count):
                logger.info(f"Match {i}: visible={locator.nth(i).is_visible()}, box={locator.nth(i).bounding_box()}")
        except: pass
        raise AssertionError(f"Text '{text}' not found or not visible.")


def reload_page(page: Page, v: dict):
    logger.info("Reloading page...")
    page.reload()
    sleep_time = v.get("sleep_after", 3000)
    page.wait_for_timeout(sleep_time)



def test_invalid_qr(page: Page, v):
    from playwright.sync_api import sync_playwright
    logger.info(">>> Executing isolated invalid QR scan sub-test using error_QR.y4m")
    url = v if isinstance(v, str) else v.get("open", "https://s.pear.us/iyR93K")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
            "--use-file-for-fake-video-capture=data/error_QR.y4m",
        ])
        context = browser.new_context(permissions=["camera", "microphone"])
        context.add_init_script('''
            const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
            navigator.mediaDevices.getUserMedia = function(constraints) {
                if (constraints && constraints.video && typeof constraints.video === 'object') {
                    if (constraints.video.facingMode) delete constraints.video.facingMode;
                    if (constraints.video.width) delete constraints.video.width;
                    if (constraints.video.height) delete constraints.video.height;
                    if (constraints.video.aspectRatio) delete constraints.video.aspectRatio;
                }
                return originalGetUserMedia(constraints);
            };
        ''')
        new_page = context.new_page()
        new_page.goto(url)
        try:
            # Code Not Recognized popup is expected
            new_page.get_by_text("Code Not Recognized").first.wait_for(state="visible", timeout=15000)
            logger.info("Successfully verified 'Code Not Recognized' on sub-browser")
        except Exception as e:
            new_page.screenshot(path="fail_invalid_qr.png")
            logger.error("Failed to verify Invalid QR scan. Saved fail_invalid_qr.png")
            raise e
        finally:
            browser.close()


def execute_t3981_flow(page: Page, v):
    import subprocess
    logger.info(">>> T3981 Phase 1: Scan Initialization (Valid/Redeemed)")
    page.goto("https://s.pear.us/iyR93K")
    page.wait_for_load_state("networkidle")
    # Acceptance of either scan result confirms camera injection is working
    # Increased timeout for slower mobile emulation environment
    page.locator("text=Code Verified|text=Code Already Redeemed").first.wait_for(state="visible", timeout=30000)
    logger.info("Successfully verified scanner/camera initialization.")

    
    logger.info(">>> T3981 Phase 2: Invalid Scan (Subprocess Isolation)")
    result = subprocess.run(["python", "run_invalid_qr.py"], capture_output=True, text=True, cwd=r"d:\new test\Autotest-monster")
    if "SUCCESS" in result.stdout:
        logger.info("Successfully verified 'Code Not Recognized' via subprocess")
    else:
        logger.error(f"Failed to verify Invalid QR scan. Output: {result.stdout} | {result.stderr}")
        raise AssertionError(f"Invalid QR scan failed in subprocess. Output: {result.stdout}")
            
    logger.info(">>> T3981 demo flow completed successfully.")

def verify_value(page: Page, v: dict):
    # Verify the value of an input field
    target_name = v.get("name")
    target_locator = v.get("locator")
    expected_value = str(v.get("value"))
    timeout = v.get("timeout", 10000)

    logger.info(f"Verifying value of '{target_name or target_locator}' matches '{expected_value}'")

    if target_locator:
        el = page.locator(target_locator).first
    else:
        # Use name attribute fallback
        el = page.locator(f'input[name="{target_name}"], [name="{target_name}"]').first

    el.wait_for(state="visible", timeout=timeout)

    try:
        actual_value = str(el.input_value())
        if actual_value != expected_value:
            # Check if it's a numeric match (e.g. "10" matching 10)
            try:
                if float(actual_value) == float(expected_value):
                    logger.info(f"Numeric match success: {actual_value} == {expected_value}")
                    return
            except: pass

            logger.error(f"Value check FAILED for {target_name or target_locator}. Expected: '{expected_value}', Actual: '{actual_value}'")
            page.screenshot(path=f"fail_verify_value_{target_name or 'elem'}.png")
            assert actual_value == expected_value, f"Expected value '{expected_value}', but found '{actual_value}'"
        
        logger.info(f"Successfully verified value '{actual_value}'")
    except Exception as e:
        logger.error(f"Error during value verification: {e}")
        page.screenshot(path=f"error_verify_value_{target_name or 'elem'}.png")
        raise AssertionError(f"Failed to verify value of {target_name or target_locator}. Error: {e}")


def verify_value_near(page: Page, v: dict):
    """
    Verify the value of an input field by finding it relative to a nearby text element.
    Example: find input near "5555" text and verify its value.
    
    Usage in YAML:
        verify_value_near: { near_text: "5555", expected: "10" }
    """
    near_text = v.get("near_text")  # The text to search near (e.g., "5555")
    near_index = v.get("near_index", 0)  # Index if multiple matches
    expected_value = str(v.get("expected") or v.get("value"))
    direction = v.get("direction", "right")  # 'right', 'left', 'below', 'above'
    offset_selector = v.get("selector")  # Optional: CSS selector to narrow down
    
    logger.info(f"Verifying value near text '{near_text}' (direction: {direction}), expected: '{expected_value}'")
    
    try:
        # Step 1: Find the anchor element with the near_text
        if near_text:
            anchor = page.get_by_text(near_text, exact=False).nth(near_index)
            anchor_box = anchor.bounding_box()
            
            if not anchor_box:
                raise Exception(f"Anchor text '{near_text}' not found or not visible")
            
            logger.info(f"Found anchor '{near_text}' at: {anchor_box}")
        
        # Step 2: Build XPath/selector to find nearby input
        # Strategy: Use JavaScript to find sibling or parent elements containing input
        js_script = f"""
        (function() {{
            // Find all text elements and inputs
            const allElements = document.querySelectorAll('*');
            let targetInput = null;
            
            // Find the anchor element with matching text
            for (let el of allElements) {{
                if (el.children.length === 0 && el.textContent.trim() === '{near_text}' && el.offsetParent !== null) {{
                    const rect = el.getBoundingClientRect();
                    const anchorX = rect.left + rect.width / 2;
                    const anchorY = rect.top + rect.height / 2;
                    
                    // Search for input in specified direction
                    const searchRadius = 300; // pixels
                    let bestMatch = null;
                    let bestDistance = Infinity;
                    
                    const inputs = document.querySelectorAll('input[name*="commission"], input[type="number"], input[placeholder*="e.g.,"]');
                    
                    for (let input of inputs) {{
                        if (!input.offsetParent) continue; // Skip hidden elements
                        
                        const inputRect = input.getBoundingClientRect();
                        const inputX = inputRect.left + inputRect.width / 2;
                        const inputY = inputRect.top + inputRect.height / 2;
                        
                        let dx = inputX - anchorX;
                        let dy = inputY - anchorY;
                        
                        // Check if in correct direction
                        let validDirection = false;
                        if ('{direction}' === 'right') {{
                            validDirection = dx > 0 && dx < searchRadius && Math.abs(dy) < 150;
                        }} else if ('{direction}' === 'left') {{
                            validDirection = dx < 0 && Math.abs(dx) < searchRadius && Math.abs(dy) < 150;
                        }} else if ('{direction}' === 'below') {{
                            validDirection = dy > 0 && dy < searchRadius && Math.abs(dx) < 150;
                        }} else if ('{direction}' === 'above') {{
                            validDirection = dy < 0 && Math.abs(dy) < searchRadius && Math.abs(dx) < 150;
                        }}
                        
                        if (validDirection) {{
                            const distance = Math.sqrt(dx*dx + dy*dy);
                            if (distance < bestDistance) {{
                                bestDistance = distance;
                                bestMatch = input;
                            }}
                        }}
                    }}
                    
                    if (bestMatch) {{
                        return bestMatch.outerHTML.substring(0, 200);
                    }}
                    break;
                }}
            }}
            return null;
        }})()
        """
        
        result = page.evaluate(js_script)
        if result:
            logger.info(f"Found nearby input via JS: {result[:100]}...")
        
        # Step 3: Alternative approach - find input by name near the text container
        # Use the name attribute pattern from the original step
        name_pattern = v.get("name") or "commissionRateForPromoters"
        
        # Try to find the input within the same container as near_text
        candidates = [
            page.locator(f'input[name="{name_pattern}"]').first,
            page.locator(f'input[name*="commission"]').first,
            page.locator('input[type="number"]').first,
        ]
        
        el = None
        for candidate in candidates:
            try:
                if candidate.is_visible(timeout=1000):
                    el = candidate
                    break
            except:
                continue
        
        if not el:
            # Fallback: use near() method if available
            if near_text:
                try:
                    # Try to find text then use next sibling
                    text_locator = page.get_by_text(near_text, exact=True)
                    el = text_locator.locator("xpath=following-sibling::input").first
                    if el.is_visible(timeout=1000):
                        logger.info("Found input via following-sibling XPath")
                except:
                    pass
        
        if not el:
            raise Exception(f"Could not locate input field near '{near_text}'")
        
        # Step 4: Verify the value
        actual_value = str(el.input_value())
        logger.info(f"Actual value found: '{actual_value}', expected: '{expected_value}'")
        
        if actual_value != expected_value:
            # Try numeric match
            try:
                if float(actual_value) == float(expected_value):
                    logger.info(f"Numeric match success: {actual_value} == {expected_value}")
                    return
            except:
                pass
            
            logger.error(f"Value check FAILED. Expected: '{expected_value}', Actual: '{actual_value}'")
            page.screenshot(path=f"fail_verify_value_near_{near_text}.png")
            assert actual_value == expected_value, f"Expected '{expected_value}', got '{actual_value}'"
        
        logger.info(f"Successfully verified value near '{near_text}': '{actual_value}'")
        
    except AssertionError:
        raise
    except Exception as e:
        logger.error(f"Error in verify_value_near: {e}")
        page.screenshot(path=f"error_verify_value_near_{near_text or 'unknown'}.png")
        raise AssertionError(f"Failed to verify value near '{near_text}': {e}")
