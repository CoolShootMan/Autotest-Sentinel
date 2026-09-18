"""路由健康探测：确认候选路径是 404、还是被踢到登录页、还是真的能打开。

**为什么需要**：`MONITORED_URLS` 里的路由会悄悄死掉 —— 返回 404 时页面不报错，
只留下 404 页的两个链接，会被当成"页面控件"静默灌进知识库索引（见
`autotest-kb-refresh` 已知坑 #10）。新增/修改路由后跑一次，确认哪些能用。

用法：
    py -3.9 tools/probe_routes.py                     # 探测内置候选集
    py -3.9 tools/probe_routes.py --paths /a,/b,/c    # 探测指定路径
    py -3.9 tools/probe_routes.py --from-monitored    # 只探测当前 MONITORED_URLS
    py -3.9 tools/probe_routes.py --out data/_routes.json

前置：先跑 `py -3.9 tools/get_all_cookies.py` 拿到 owner 登录态，否则会全被踢到登录页。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).parent
sys.path.insert(0, str(TOOLS))
from ui_snapshot import _load_base_url, _resolve_cookie_path  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

# 内置候选集：覆盖线上常见路由 + 历史上出现过的死路由（回归用）
DEFAULT_CANDIDATES = [
    "/", "/home", "/dashboard", "/shop", "/settings", "/storefront-modules",
    "/catalog", "/account", "/profile", "/analytics", "/orders", "/customers",
    "/events", "/collabs", "/post/create", "/events/create", "/events/settings",
    "/autotestshop/settings", "/autotestshop/storefront", "/autotest-co-seller",
]


def _paths_from_monitored() -> list[str]:
    """从 ui_snapshot.MONITORED_URLS 抽出路径（去掉 BASE_URL 前缀）。"""
    import ui_snapshot  # noqa: PLC0415
    out: list[str] = []
    for tpl in getattr(ui_snapshot, "MONITORED_URLS", []):
        path = tpl.split("}", 1)[-1] if "}" in tpl else tpl
        out.append(path or "/")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="探测候选路由是否存在/是否 404/是否掉登录态")
    ap.add_argument("--env", default="release")
    ap.add_argument("--account", default="main")
    ap.add_argument("--paths", default="", help="逗号分隔的路径列表，如 /a,/b")
    ap.add_argument("--from-monitored", action="store_true", help="只探测当前 MONITORED_URLS")
    ap.add_argument("--out", default="", help="把探测结果写为 JSON")
    args = ap.parse_args()

    if args.from_monitored:
        candidates = _paths_from_monitored()
    elif args.paths:
        candidates = [p.strip() for p in args.paths.split(",") if p.strip()]
    else:
        candidates = DEFAULT_CANDIDATES

    base = _load_base_url(args.env)
    cookie = _resolve_cookie_path(args.env, args.account)

    rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state=cookie) if cookie else browser.new_context()
        page = ctx.new_page()
        page.set_default_timeout(25000)
        for u in candidates:
            rec: dict = {"path": u}
            try:
                page.goto(base + u, wait_until="domcontentloaded", timeout=25000)
                page.wait_for_timeout(4000)
                body = page.inner_text("body") or ""
                rec["title"] = page.title()
                rec["final"] = page.url.replace(base, "")
                rec["is_404"] = "could not be found" in body.lower()
                rec["login_redirect"] = "/login" in page.url
                rec["head"] = body[:120].replace("\n", " | ")
            except Exception as e:  # noqa: BLE001
                rec["error"] = str(e)[:120]
            rows.append(rec)
        browser.close()

    for r in rows:
        if r.get("error"):
            flag = "ERR "
        elif r.get("is_404"):
            flag = "404 "
        elif r.get("login_redirect"):
            flag = "LOG "
        else:
            flag = "OK  "
        print(f'{flag} {r["path"]:28s} {r.get("title", "")[:28]:28s} {r.get("final", "")[:40]}')

    if args.out:
        Path(args.out).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"written -> {args.out}")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
