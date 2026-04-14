import re as _re
from playwright.sync_api import Page
from loguru import logger
from .base import smart_click

def click_module_edit_button(page: Page, v: dict):
    module_name = v.get("module_name")
    logger.info(f"Clicking edit button for module: {module_name}")
    # Use double-locator pattern: Find the container that has both the module name and buttons
    # Then click the second button (usually the 'More/Edit' icon)
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button")).last
    container.scroll_into_view_if_needed()
    btn = container.get_by_role("button").nth(1)
    btn.wait_for(state="visible", timeout=10000)
    btn.click(timeout=15000)
    page.wait_for_timeout(1000) # Wait for potential UI transitions

def click_module_paragraph(page: Page, v: dict):
    # Click on module paragraph using smart logic
    smart_click(page, {"role": "paragraph", "name": v.get("text"), "timeout": 10000, **v})

def click_add_new_product(page: Page, v: dict):
    # Click "Add new" button within specific module header
    module_name = v.get("module_name")
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    container.get_by_role("button", name="Add new").click(timeout=15000)

def click_module_add_new(page: Page, v: dict):
    # Click the "Add new" button specifically for the named module
    # Uses refined double-locator pattern:
    module_name = v.get("module_name")
    logger.info(f"Clicking 'Add new' for module: {module_name}")
    
    # 1. Find the deepest div that contains the module title AND an 'Add new' button
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    
    # 2. Click the button within that container
    container.get_by_role("button", name="Add new").click(timeout=10000)

def click_module_post_view_event_cta(page: Page, v: dict):
    post_title = v.get("post_title")
    module_name = v.get("module_name")
    logger.info(f"Clicking view event cta for module: {module_name} and post title: {post_title}")
    container = page.locator("div", has_text=module_name).filter(has_text=post_title).last
    container.get_by_role("button", name="View event").first.click(timeout=10000)

def click_module_collapse(page: Page, v: dict):
    """Collapse a module by clicking its arrow-up icon."""
    module_name = v.get("module_name")
    logger.info(f"Collapsing module: {module_name}")
    # Locate the definitive module header container
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    container.get_by_test_id("arrow-up-icon").first.click(timeout=10000)

def click_module_expand(page: Page, v: dict):
    """Expand a module by clicking its toggle icon.
    The test-id does not change to arrow-down, so we click the same arrow-up-icon.
    """
    module_name = v.get("module_name")
    logger.info(f"Expanding module: {module_name}")
    container = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    container.get_by_test_id("arrow-up-icon").first.click(timeout=10000)

def verify_module_collapsed(page: Page, v: dict):
    """Verifies that a module's body is collapsed by checking its overall container height shrinks."""
    module_name = v.get("module_name")
    logger.info(f"Verifying module '{module_name}' is collapsed by measuring height...")
    # Find the top-level outer wrapper containing this module header.
    # Usually it's the parent of the header container.
    header = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    
    import time
    start_time = time.time()
    # Poll for height to shrink (e.g. < 150px means body is folded, just header left)
    while time.time() - start_time < 5.0:
        box = header.locator("..").bounding_box()
        if box and box['height'] < 150:
            logger.info(f"Module '{module_name}' is successfully collapsed (Visual Height: {box['height']:.1f}px)")
            return
        time.sleep(0.5)
    raise AssertionError(f"Module '{module_name}' did not collapse. Current Height: {box['height']:.1f}px")

def verify_module_expanded(page: Page, v: dict):
    """Verifies that a module's body is expanded by checking its overall container height grows."""
    module_name = v.get("module_name")
    logger.info(f"Verifying module '{module_name}' is expanded by measuring height...")
    header = page.locator("div").filter(has=page.get_by_text(module_name, exact=True)).filter(has=page.get_by_role("button", name="Add new")).last
    
    import time
    start_time = time.time()
    # Poll for height to grow (e.g. > 150px means body is unfolded)
    while time.time() - start_time < 5.0:
        box = header.locator("..").bounding_box()
        if box and box['height'] > 150:
            logger.info(f"Module '{module_name}' is successfully expanded (Visual Height: {box['height']:.1f}px)")
            return
        time.sleep(0.5)
    raise AssertionError(f"Module '{module_name}' did not expand. Current Height: {box['height']:.1f}px")
