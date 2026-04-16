import time
from pathlib import Path

from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://release.pear.us/login", timeout=90000)
    
    page.get_by_role("textbox", name="Email").fill("yuxiao.zhu.ext+998@1m.app")
    page.get_by_role("textbox", name="Input your password").fill("Happy123")
    page.get_by_role("button", name="Log in", exact=True).click()
    # Wait for the URL to change, indicating a successful login and navigation.
    page.wait_for_url(lambda url: "/login" not in url, timeout=60000)

    # Now that login is complete, save the storage state.
    # 构建跨平台路径（支持 Mac、Windows、Linux）
    project_root = Path(__file__).parent.parent
    cookie_path = project_root / "test_case" / "UI" / "Test_Katana" / "cookie_release_co_seller.json"

    cookies = context.storage_state(path=str(cookie_path))
    print(cookies)
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)