from playwright.sync_api import Page
from loguru import logger
from .base import smart_click

def click_module_edit_button(page: Page, v: dict):
    module_name = v.get("module_name")
    # T3556 recording shows target is a div with title and "Add new", then 2nd button (index 1)
    smart_click(page, {
        "locator": f'div:has-text("^{module_name}Add new$")',
        "role": "button",
        "index": 1,
        "name": f"Edit button for {module_name}",
        "timeout": 15000,
        **v
    })

def click_module_paragraph(page: Page, v: dict):
    # Click on module paragraph using smart logic
    smart_click(page, {"role": "paragraph", "name": v.get("text"), "timeout": 10000, **v})

def click_add_new_product(page: Page, v: dict):
    # Click "Add new" button within specific module header
    module_name = v.get("module_name")
    smart_click(page, {
        "locator": f'div:has-text("^{module_name}Add new$")',
        "role": "button",
        "name": "Add new button",
        "index": 1, # Usually the add/edit buttons are here
        "timeout": 15000,
        **v
    })

def click_module_add_new(page: Page, v: dict):
    # Click the "Add new" button specifically for the named module
    module_name = v.get("module_name")
    smart_click(page, {
        "role": "button", 
        "name": "Add new", 
        "locator": f'div:has-text("{module_name}")', 
        "timeout": 10000, 
        **v
    })
