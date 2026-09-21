#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb_capture_flow.py —— 把「点击才能到达的页面」补录进 DOM 知识库。

## 为什么需要它

`ui_snapshot.py` 只抓 `MONITORED_URLS` 里那 9 个**静态 URL**。但真实的业务控件大量藏在
点击路径后面：Post settings 面板、邮箱弹窗、二级配置页、编辑器内部 —— 这些永远进不了知识库，
于是「新功能的控件」在 KB 里查不到，RAG 自愈也就帮不上忙。

本工具补上这一段：按一份 **flow 描述文件**驱动浏览器走点击路径，每个 stage 抓一次 DOM，
产出与基线快照**同格式**的文件，并可选地即时写入 FAISS 索引。

## 关键：为什么产出的是「快照文件」而不是只写索引

`dom_kb.build_index()` 是**整体重建**（新建 `IndexFlatIP` 后覆盖）⇒ 只 `add_elements()` 的增量
会在下一次 `dom_kb.py build` 时**全部丢失**。而 `dom_kb.build_from_snapshot()` 现在会额外合并
`ui_snapshots/flows__<env>__*.json` ⇒ 流程补录的内容能**跨重建存活**，真正"越攒越多"。

文件名**不含时间戳**（`flows__<env>__<name>.json`，同名覆盖）⇒ 重复采集不会让仓库膨胀。

## 用法

```bash
py -3.9 tools/kb_capture_flow.py --flow data/kb_flows/post_contact_email.json
py -3.9 tools/kb_capture_flow.py --flow ... --dry-run     # 只打印将执行的动作
py -3.9 tools/kb_capture_flow.py --flow ... --no-add      # 只写快照，不写索引
```

## flow 描述文件格式

```json
{
  "name": "post_contact_email",
  "url_template": "{BASE_URL}/post/<post_id>/settings",
  "stages": [
    {"label": "settings_switch_on",
     "url": "{BASE_URL}/post/<post_id>/settings",
     "wait_for": "text=Post settings",
     "actions": []},
    {"label": "email_dialog",
     "actions": [{"click": "button[data-testid=\"manage-button\"]"}, {"wait": 1000}]}
  ]
}
```

- `url_template`：写进 KB 的归属 key。查询时 `--url` 必须**逐字符一致**（含 `{BASE_URL}`）。
  **每个 stage 可以用自己的 `url_template` 覆盖** —— 一个 flow 里跨了不同页面时（配置页 / 弹窗 / 前台页），
  各自归属到各自的 key 才有意义。
- `stages[].url`：给了就导航；不给则沿用上一个 stage 的页面状态（用于"点开弹窗后再抓一次"）。
- `actions`：`{"click": sel}` / `{"wait": ms}` / `{"wait_for": sel}` / `{"goto": url}` / `{"press": key}`。
  `sel` 用 Playwright 选择器语法，`button[data-testid="manage-button"]`、`text=Save`、`role=button[name="Save"]` 都行。
  **单个 action 失败不致命**（只告警）—— 很多控件要前置条件满足才出现，点不到 ≠ 这一页没价值。
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
PROJECT_DIR = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

from ui_snapshot import JS_EXTRACT, SNAPSHOT_DIR, _load_base_url, _resolve_cookie_path  # noqa: E402


def resolve(tpl: str, base_url: str) -> str:
    return tpl.replace("{BASE_URL}", base_url)


def run_capture(flow: dict, env: str, account: str, dry_run: bool = False):
    """驱动浏览器走 flow，返回 {url_template: [elements], stage_labels: [...]}"""
    base_url = _load_base_url(env)
    if not base_url:
        raise SystemExit(f"[FAIL] env_config.yaml 里找不到 env={env} 的 base url")

    cookie_path = _resolve_cookie_path(env, account)
    if cookie_path:
        print(f"  [Cookie] {os.path.basename(cookie_path)}")
    else:
        print(f"  [WARN] 没找到 env={env} account={account} 的 cookie 文件 → 会以访客视角抓，"
              f"owner 专属控件抓不到。先跑 py -3.9 tools/get_all_cookies.py")

    url_template = flow.get("url_template") or "{BASE_URL}"
    stages = flow.get("stages") or []

    if dry_run:
        print(f"  base_url     : {base_url}")
        print(f"  url_template : {url_template}")
        for i, st in enumerate(stages, 1):
            print(f"  [{i}] {st.get('label', '?')}  url={st.get('url', '(inherit)')}  "
                  f"wait_for={st.get('wait_for', '-')}  actions={st.get('actions', [])}")
        return None, None

    from playwright.sync_api import sync_playwright

    by_template = {}
    labels = []
    action_warnings = []
    login_warned = False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        opts = {}
        if cookie_path and os.path.exists(cookie_path):
            opts["storage_state"] = cookie_path
        context = browser.new_context(**opts)
        page = context.new_page()
        page.set_default_timeout(30000)

        def session_ok():
            """项目铁律 1：有 `..._web_auth_token` 且无 `..._web_auth_token_guest` 才算登录态。"""
            names = [c.get("name", "") for c in context.cookies()]
            has_auth = any(n.endswith("_web_auth_token") for n in names)
            has_guest = any(n.endswith("_web_auth_token_guest") for n in names)
            return (has_auth and not has_guest), f"auth_token={has_auth} guest_token={has_guest}"

        for i, st in enumerate(stages, 1):
            label = st.get("label") or f"stage{i}"
            if st.get("url"):
                target = resolve(st["url"], base_url)
                print(f"  [{i}] goto {target}", file=sys.stderr, flush=True)
                page.goto(target, wait_until="domcontentloaded", timeout=30000)
            if st.get("wait_for"):
                try:
                    page.wait_for_selector(st["wait_for"], timeout=15000)
                except Exception as e:
                    print(f"      wait_for 超时: {str(e)[:120]}", file=sys.stderr, flush=True)

            for act in st.get("actions", []):
                # 单步失败不致命：至少把当前 stage 已到位的 DOM 抓到（很多控件只在
                # 开关为 On 等前置下才出现，点不到 ≠ 这一页没有价值）。
                try:
                    if "click" in act:
                        print(f"      click {act['click']}", file=sys.stderr, flush=True)
                        page.click(act["click"], timeout=15000)
                        page.wait_for_timeout(400)
                    elif "wait" in act:
                        page.wait_for_timeout(int(act["wait"]))
                    elif "wait_for" in act:
                        page.wait_for_selector(act["wait_for"], timeout=15000)
                    elif "goto" in act:
                        page.goto(resolve(act["goto"], base_url), wait_until="domcontentloaded", timeout=30000)
                    elif "press" in act:
                        page.keyboard.press(act["press"])
                except Exception as e:
                    msg = f"{label}: action {act} 失败 -> {str(e)[:160]}"
                    print(f"      [WARN] {msg}", file=sys.stderr, flush=True)
                    action_warnings.append(msg)

            # 访客视角告警：拿到 /login 的话 DOM 是垃圾（owner 控件全丢）
            cur = page.url
            if "/login" in cur and not login_warned:
                print(f"  [WARN] 落到登录页 ({cur}) → cookie 失效，抓到的将是访客 DOM，别入库！",
                      file=sys.stderr, flush=True)
                login_warned = True

            # 首次落地即校验登录态（不只是看 URL，还要看 cookie 判据）
            if not login_warned:
                ok, why = session_ok()
                if not ok:
                    print(f"  [FATAL] 登录态无效（{why}）→ 中止，不入库。"
                          f"先跑: py -3.9 tools/get_all_cookies.py", file=sys.stderr, flush=True)
                    raise SystemExit(3)

            els = page.evaluate(JS_EXTRACT)
            tpl = st.get("url_template") or url_template

            # 404 守卫：别把 404 页的那两个链接当成"页面控件"灌进索引
            try:
                body = (page.inner_text("body") or "")[:2000].lower()
            except Exception:
                body = ""
            if "could not be found" in body:
                msg = f"{label}: 是 404 页面（this page could not be found），已跳过"
                print(f"  [WARN] {msg}", file=sys.stderr, flush=True)
                action_warnings.append(msg)
                labels.append({"label": label, "url": cur, "url_template": tpl, "elements": 0, "skipped": "404"})
                continue

            print(f"      {label}: {len(els)} elements  ({cur})", file=sys.stderr, flush=True)
            by_template.setdefault(tpl, []).extend(els)
            labels.append({"label": label, "url": cur, "url_template": tpl, "elements": len(els)})

        browser.close()

    if login_warned:
        raise SystemExit("[FAIL] cookie 失效导致访客视角，已放弃入库（先刷新 cookie）")

    for w in action_warnings:
        print(f"  [WARN] {w}")

    # 同一 stage 间会有大量重复元素（同一个页面不同状态），交给 build/add 的签名去重
    return by_template, labels


def save_flow_snapshot(name: str, env: str, base_url: str, by_template: dict, labels: list) -> str:
    """写 ui_snapshots/flows__<env>__<name>.json（同名覆盖，无时间戳 → 不会膨胀仓库）。"""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    path = os.path.join(SNAPSHOT_DIR, f"flows__{env}__{name}.json")
    payload = {
        "base_url": base_url,
        "flow": name,
        "captured_at": datetime.datetime.now().isoformat(),
        "stages": labels,
        "urls": by_template,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"  快照已写入: {path}")
    return path


def main():
    ap = argparse.ArgumentParser(description="把点击路径补录进 DOM 知识库")
    ap.add_argument("--flow", required=True, help="flow 描述 JSON 文件")
    ap.add_argument("--env", default="release")
    ap.add_argument("--account", default="main",
                    help="main(owner) / co_seller / partner / demi / yx")
    ap.add_argument("--dry-run", action="store_true", help="只打印将执行的动作")
    ap.add_argument("--no-add", action="store_true", help="只写快照，不即时写入 FAISS 索引")
    args = ap.parse_args()

    with open(args.flow, encoding="utf-8") as f:
        flow = json.load(f)

    name = flow.get("name") or Path(args.flow).stem
    print(f"== flow: {name} (env={args.env}, account={args.account}) ==")

    urls, labels = run_capture(flow, args.env, args.account, dry_run=args.dry_run)
    if args.dry_run:
        return
    if urls is None or labels is None:
        raise SystemExit("[FAIL] run_capture 未返回抓取结果（非 dry-run 却为空）")

    base_url = _load_base_url(args.env)
    total = sum(len(v) for v in urls.values())
    if not total:
        raise SystemExit("[FAIL] 没抓到任何元素，未写入")

    snapshot_path = save_flow_snapshot(name, args.env, base_url, urls, labels)
    print(f"  抓取合计 {total} 个元素，分布在 {len(urls)} 个 url_template：")
    for tpl, els in urls.items():
        print(f"    {tpl}  ({len(els)})")

    if not args.no_add:
        import dom_kb
        all_ok = True
        for tpl, els in urls.items():
            all_ok = dom_kb.add_elements(els, url_template=tpl) and all_ok
        try:
            import pickle
            after = len(pickle.load(open(os.path.join(PROJECT_DIR, "dom_kb", "meta.pkl"), "rb"))["elements"])
        except Exception:
            after = "?"
        print(f"  add_elements -> {all_ok}；索引现有 {after} 个元素")

    print(f"  完成。快照: {snapshot_path}")
    print("  提示：这些内容会在下次 dom_kb.py build 时被自动合并（flows__* 快照），不会丢。")


if __name__ == "__main__":
    main()
