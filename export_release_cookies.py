#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
导出 release.pear.us 的登录态为 Playwright storage state，供 UI 自动化用例使用。

用法（在你本机、有显示器的终端里执行）：
    cd /Users/yuhong/Documents/Pear-automation-test
    ./venv/bin/python export_release_cookies.py

脚本会打开一个浏览器窗口，请在登录页手动完成登录（手机号 + 验证码）。
登录成功后脚本自动把 storage state 写到：
    test_case/UI/Test_Katana/cookie_release.json
（该文件名由 BASE_URL 决定：release -> cookie_release.json，staging -> cookie_staging.json）

写完后即可运行用例：
    ./venv/bin/python runner.py testT5649
"""
import os
import json

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE_URL", "https://release.pear.us")
OUT = os.path.join("test_case", "UI", "Test_Katana", "cookie_release.json")


def main():
    with sync_playwright() as p:
        # headless=False 才能让你在登录页手动输入
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(BASE + "/events", wait_until="load")
        print(f"请在弹出的浏览器窗口中登录 {BASE} ...")
        print("(登录成功、页面离开 /login 后，本脚本会自动继续)")
        try:
            # 登录后 URL 不再包含 /login 即视为成功
            page.wait_for_url(lambda u: "/login" not in u, timeout=180000)
        except Exception:
            print("等待登录超时（180s），仍尝试保存当前 storage state。")
        state = context.storage_state()
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        print(f"已保存 storage state 到 {OUT}  (cookies 数量: {len(state.get('cookies', []))})")
        browser.close()


if __name__ == "__main__":
    main()
