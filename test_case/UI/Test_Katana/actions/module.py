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
    container.get_by_role("button").nth(1).click(timeout=15000)

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
