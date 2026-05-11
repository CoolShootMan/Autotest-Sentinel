"""
Fetch cookies for three accounts in sequence, logging in one by one and saving to individual JSON files.
Usage: python tools/get_all_cookies.py

Cookie filenames are generated dynamically based on the current environment (e.g. cookie_release.json),
ensuring different environments never overwrite each other's cookie files.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(Path(__file__).parent.parent / ".env")

PROJECT_ROOT = Path(__file__).parent.parent
COOKIE_DIR = PROJECT_ROOT / "test_case" / "UI" / "Test_Katana"

# Read from BASE_URL environment variable, default to release environment
ENV_BASE = os.environ.get("BASE_URL", "https://release.pear.us")

# Reverse-map domain to environment name for cookie file naming
_ENV_MAP = {
    "https://staging.pear.us": "staging",
    "https://release.pear.us": "release",
    "https://pear.us": "prod",
}
CURRENT_ENV = _ENV_MAP.get(ENV_BASE, "release")

ACCOUNTS = [
    {
        "name": "main (+999)",
        "email": "yuxiao.zhu.ext+999@1m.app",
        "password": "Happy123",
        "cookie_file": f"cookie_{CURRENT_ENV}.json",
    },
    {
        "name": "co-seller (+998)",
        "email": "yuxiao.zhu.ext+998@1m.app",
        "password": "Happy123",
        "cookie_file": f"cookie_{CURRENT_ENV}_co_seller.json",
    },
    {
        "name": "partner co-seller (+997)",
        "email": "yuxiao.zhu.ext+997@1m.app",
        "password": "Happy123",
        "cookie_file": f"cookie_{CURRENT_ENV}_partner_coseller.json",
    },
]


def login_and_save(playwright, account: dict):
    name = account["name"]
    print(f"\n[{name}] Starting login...")

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(f"{ENV_BASE}/login", timeout=20000)
    page.wait_for_timeout(2000)

    # Click "Log in with password" button if it exists
    try:
        page.get_by_text("Log in with password").click(timeout=5000)
        page.wait_for_timeout(1000)
    except Exception:
        pass

    # Fill Email
    try:
        page.get_by_role("textbox", name="Email").fill(account["email"])
    except Exception:
        try:
            page.locator(
                "input[type='email'], input[name='email'], input[placeholder*='email' i]"
            ).fill(account["email"])
        except Exception:
            page.screenshot(path=f"login_error_{name}.png")
            raise RuntimeError(f"[{name}] Email input field not found")

    # Fill Password
    try:
        page.get_by_role("textbox", name="Input your password").fill(account["password"])
    except Exception:
        try:
            page.locator("input[type='password']").fill(account["password"])
        except Exception:
            page.screenshot(path=f"login_error_{name}.png")
            raise RuntimeError(f"[{name}] Password input field not found")

    page.get_by_role("button", name="Log in", exact=True).click()
    page.wait_for_url(lambda url: "/login" not in url, timeout=60000)

    cookie_path = COOKIE_DIR / account["cookie_file"]
    context.storage_state(path=str(cookie_path))
    print(f"[{name}] Cookie saved -> {cookie_path}")

    page.close()
    context.close()
    browser.close()


def main():
    print("=== Starting bulk cookie collection ===")
    with sync_playwright() as pw:
        for account in ACCOUNTS:
            login_and_save(pw, account)
    print("\n=== All accounts completed ===")


if __name__ == "__main__":
    main()
