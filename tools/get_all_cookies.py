"""
一次性获取三个账号的 cookie，顺序登录后分别保存到对应的 json 文件。
用法：python tools/get_all_cookies.py

Cookie 文件名根据当前环境动态生成（如 cookie_release.json），
确保不同环境不会互相覆盖。
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(Path(__file__).parent.parent / ".env")

PROJECT_ROOT = Path(__file__).parent.parent
COOKIE_DIR = PROJECT_ROOT / "test_case" / "UI" / "Test_Katana"

# 从 BASE_URL 环境变量读取，默认 release 环境
ENV_BASE = os.environ.get("BASE_URL", "https://release.pear.us")

# 根据域名反推环境名，用于 cookie 文件命名
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
    print(f"\n[{name}] 开始登录...")

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(f"{ENV_BASE}/login", timeout=20000)
    page.wait_for_timeout(2000)

    # 如果有"Log in with password"按钮先点一下
    try:
        page.get_by_text("Log in with password").click(timeout=5000)
        page.wait_for_timeout(1000)
    except Exception:
        pass

    # 填写 Email
    try:
        page.get_by_role("textbox", name="Email").fill(account["email"])
    except Exception:
        try:
            page.locator(
                "input[type='email'], input[name='email'], input[placeholder*='email' i]"
            ).fill(account["email"])
        except Exception:
            page.screenshot(path=f"login_error_{name}.png")
            raise RuntimeError(f"[{name}] 找不到 Email 输入框")

    # 填写密码
    try:
        page.get_by_role("textbox", name="Input your password").fill(account["password"])
    except Exception:
        try:
            page.locator("input[type='password']").fill(account["password"])
        except Exception:
            page.screenshot(path=f"login_error_{name}.png")
            raise RuntimeError(f"[{name}] 找不到密码输入框")

    page.get_by_role("button", name="Log in", exact=True).click()
    page.wait_for_url(lambda url: "/login" not in url, timeout=60000)

    cookie_path = COOKIE_DIR / account["cookie_file"]
    context.storage_state(path=str(cookie_path))
    print(f"[{name}] Cookie 已保存 -> {cookie_path}")

    page.close()
    context.close()
    browser.close()


def main():
    print("=== 开始批量获取 Cookie ===")
    with sync_playwright() as pw:
        for account in ACCOUNTS:
            login_and_save(pw, account)
    print("\n=== 全部完成 ===")


if __name__ == "__main__":
    main()
