"""
一次性获取三个账号的 cookie，顺序登录后分别保存到对应的 json 文件。
用法：python tools/get_all_cookies.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).parent.parent
COOKIE_DIR = PROJECT_ROOT / "test_case" / "UI" / "Test_Katana"

ACCOUNTS = [
    {
        "name": "main (+999)",
        "email": "yuxiao.zhu.ext+999@1m.app",
        "password": "Happy123",
        "cookie_file": "cookie_release.json",
    },
    {
        "name": "co-seller (+998)",
        "email": "yuxiao.zhu.ext+998@1m.app",
        "password": "Happy123",
        "cookie_file": "cookie_release_co_seller.json",
    },
    {
        "name": "partner co-seller (+997)",
        "email": "yuxiao.zhu.ext+997@1m.app",
        "password": "Happy123",
        "cookie_file": "cookie_partner_coseller_release.json",
    },
]


def login_and_save(playwright, account: dict):
    name = account["name"]
    print(f"\n[{name}] 开始登录...")

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://release.pear.us/login", timeout=90000)
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
