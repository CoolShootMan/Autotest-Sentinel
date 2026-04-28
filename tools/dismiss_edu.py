"""
关闭三个账号在各页面可能出现的 EDU 弹窗。
依赖已存在的 cookie 文件，通过 storage_state 登录，无需密码。
用法：python tools/dismiss_edu.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).parent.parent
COOKIE_DIR = PROJECT_ROOT / "test_case" / "UI" / "Test_Katana"

ACCOUNTS = [
    {
        "name": "main (+999)",
        "cookie_file": "cookie_release.json",
        "home_url": "https://release.pear.us/autotestshop",
    },
    {
        "name": "co-seller (+998)",
        "cookie_file": "cookie_release_co_seller.json",
        "home_url": "https://release.pear.us/autotest-coseller",
    },
    {
        "name": "partner co-seller (+997)",
        "cookie_file": "cookie_partner_coseller_release.json",
        "home_url": "https://release.pear.us/partnercoseller997",
    },
]


def dismiss_edu_popups(page: "Page", retries: int = 5) -> None:
    """点掉页面上所有可能出现的 EDU 弹窗按钮（Next / Got it / Try it now）。"""
    for _ in range(retries):
        clicked = False
        for text in ("Next", "Got it"):
            try:
                page.locator("button").filter(has_text=text).click(timeout=1500)
                clicked = True
            except Exception:
                pass
        if not clicked:
            break
    try:
        page.get_by_role("button", name="Try it now").click(timeout=1500)
    except Exception:
        pass


def handle_selling_customize(page: "Page") -> None:
    """Selling tab → Customize products 页面的 EDU 处理流程。"""
    try:
        page.get_by_role("tab", name="Selling", exact=True).click(timeout=5000)
        page.wait_for_timeout(1000)
        dismiss_edu_popups(page)
    except Exception:
        pass

    try:
        page.get_by_role("button", name="Customize products").click(timeout=5000)
        page.wait_for_timeout(1500)
        dismiss_edu_popups(page)
    except Exception:
        pass

    try:
        page.get_by_role("checkbox").check(timeout=3000)
    except Exception:
        pass

    try:
        page.get_by_role("button", name="Start Customizing").click(timeout=5000)
        page.wait_for_timeout(1000)
        dismiss_edu_popups(page)
    except Exception:
        pass

    for _ in range(3):
        try:
            page.locator("button").filter(has_text="Done").click(timeout=3000)
            page.wait_for_timeout(500)
        except Exception:
            break

    try:
        page.get_by_role("button", name="Save").click(timeout=5000)
    except Exception:
        pass

    try:
        page.get_by_role("button", name="Close").click(timeout=5000)
    except Exception:
        pass


def handle_customers(page: "Page") -> None:
    """Customers → Followers 页面 EDU 处理。"""
    try:
        page.goto("https://release.pear.us/customers", timeout=60000)
        page.wait_for_timeout(2000)
        dismiss_edu_popups(page)
    except Exception:
        pass

    try:
        page.get_by_role("tab", name="Followers").click(timeout=5000)
        page.wait_for_timeout(1000)
        dismiss_edu_popups(page)
    except Exception:
        pass

    try:
        page.get_by_role("button", name="Close").click(timeout=3000)
    except Exception:
        pass


def dismiss_for_account(playwright, account: dict):
    name = account["name"]
    cookie_path = COOKIE_DIR / account["cookie_file"]
    home_url = account["home_url"]

    if not cookie_path.exists():
        print(f"[{name}] Cookie 文件不存在，跳过: {cookie_path}")
        return

    print(f"\n[{name}] 加载 cookie，开始处理 EDU...")

    browser = playwright.chromium.launch(headless=False)
    # 通过 storage_state 加载已登录状态，而非 add_init_script
    context = browser.new_context(storage_state=str(cookie_path))
    page = context.new_page()

    # ── ① shop 主页 EDU ──
    page.goto(home_url, timeout=60000)
    page.wait_for_timeout(2000)
    dismiss_edu_popups(page)

    # ── ② 进入Post编辑页，触发该页 EDU ──
    try:
        page.get_by_role("button", name="Image of Product Test event").first.click(timeout=5000)
        page.wait_for_timeout(1500)
        dismiss_edu_popups(page)
    except Exception:
        pass

    # ── ③ Selling tab → Customize products ──
    handle_selling_customize(page)

    # ── ④ Customers → Followers ──
    handle_customers(page)

    # ── ⑤ 回到 storefront 收尾 ──
    page.goto(home_url, timeout=60000)
    page.wait_for_timeout(2000)
    dismiss_edu_popups(page)

    # ── 保存已处理 EDU 后的 cookie ──
    context.storage_state(path=str(cookie_path))
    print(f"[{name}] EDU 处理完毕，cookie 已更新 -> {cookie_path}")

    page.close()
    context.close()
    browser.close()


def main():
    print("=== 开始关闭 EDU 弹窗 ===")
    with sync_playwright() as pw:
        for account in ACCOUNTS:
            dismiss_for_account(pw, account)
    print("\n=== 全部完成 ===")


if __name__ == "__main__":
    main()
