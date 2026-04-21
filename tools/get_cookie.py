import time
from pathlib import Path

from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://release.pear.us/login", timeout=90000)
    
    # Wait for page to load, take screenshot if login form not visible
    page.wait_for_timeout(2000)
    
    # Try to find and click "Log in with password" button if it exists
    try:
        page.get_by_text("Log in with password").click(timeout=5000)
        page.wait_for_timeout(1000)
    except:
        pass
    
    # Try to find email input field with different locators
    try:
        page.get_by_role("textbox", name="Email").fill("yuxiao.zhu.ext+999@1m.app")
    except:
        # Try placeholder or label
        try:
            page.locator("input[type='email'], input[name='email'], input[placeholder*='email' i]").fill("yuxiao.zhu.ext+999@1m.app")
        except:
            page.screenshot(path="login_error.png")
            raise Exception("Could not find email input field")
    
    try:
        page.get_by_role("textbox", name="Input your password").fill("Happy123")
    except:
        try:
            page.locator("input[type='password']").fill("Happy123")
        except:
            page.screenshot(path="login_error.png")
            raise Exception("Could not find password input field")
    
    page.get_by_role("button", name="Log in", exact=True).click()
    
    # Wait for the URL to change, indicating a successful login and navigation.
    page.wait_for_url(lambda url: "/login" not in url, timeout=60000)

    # Now that login is complete, save the storage state.
    project_root = Path(__file__).parent.parent
    cookie_path = project_root / "test_case" / "UI" / "Test_Katana" / "cookie_release.json"

    cookies = context.storage_state(path=str(cookie_path))
    print(cookies)
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
