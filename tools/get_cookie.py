import time

from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://release.pear.us/login", timeout=90000)
    page.screenshot(path="login_debug.png")
    print("Screenshot saved to login_debug.png")
    
    # The login page might directly show the email/password fields or require a click.
    try:
        if page.get_by_text("Log in with password").is_visible(timeout=5000):
            page.get_by_text("Log in with password").click()
    except:
        print("Log in with password not found, checking for Email field directly.")

    try:
        if page.get_by_text("Use Phone").is_visible(timeout=5000):
            page.get_by_text("Use Phone").click()
    except:
        pass

    # Fill credentials
    page.get_by_role("textbox", name="Phone number").fill("4083598157")
    page.get_by_role("textbox", name="Input your password").fill("Xuan123456")
    page.get_by_role("button", name="Log in", exact=True).click()
    # Wait for the URL to change, indicating a successful login and navigation.
    page.wait_for_url(lambda url: "/login" not in url, timeout=60000)

    # Now that login is complete, save the storage state.
    cookies = context.storage_state(path="D:\\new test\\Autotest-monster\\test_case\\UI\\Test_Katana\\cookie_release.json")
    print(cookies)
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
