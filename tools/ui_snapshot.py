"""
ui_snapshot.py - DOM snapshot + diff detector

Phase 1: monitor static URLs (no click navigation).
Cookie injection supported for authenticated pages.

Usage:
    # Save baseline snapshot (main account, release env)
    python tools/ui_snapshot.py snapshot --env release --account main --label baseline

    # Save current snapshot
    python tools/ui_snapshot.py snapshot --env release --account main --label current

    # Diff two snapshots
    python tools/ui_snapshot.py diff --env release --base baseline --target current

    # One-shot: snapshot + diff + affected YAML
    python tools/ui_snapshot.py check --env release --account main --label current --base baseline
"""

import typing
import json
import os
import sys
import argparse
import datetime
import re

# Type aliases (Python 3.9 compatible)
Dict = typing.Dict
List = typing.List
Optional = typing.Optional

# ---------------------------------------------------------------------------
# Config: URLs to monitor (extracted from YAML open: statements)
# Phase 1: only static URLs (no click navigation needed)
#
# 2026-09-18 核对（实测每条路由是否 404）：
#   - 移除 `{BASE_URL}/dashboard`、`{BASE_URL}/shop` —— 线上已是
#     "This page could not be found"（404），只会把 404 页的链接灌进索引。
#   - 新增 `explore` / `customers` / `account` / `storefront-modules` —— 实测存在且内容充实。
#   - 点击才能到达的页面（Post settings、各种弹窗）**不在这里**，见 `tools/kb_capture_flow.py`。
# ---------------------------------------------------------------------------
MONITORED_URLS = [
    "{BASE_URL}/events",
    "{BASE_URL}/autotestshop",
    "{BASE_URL}/explore",
    "{BASE_URL}/catalog",
    "{BASE_URL}/customers",
    "{BASE_URL}/account",
    "{BASE_URL}/storefront-modules",
    "{BASE_URL}/post/create",
    "{BASE_URL}/events/create",
    "{BASE_URL}/events/settings",
    "{BASE_URL}/collabs",
]

# 可选：每页一个"内容已出现"的锚点。**测不到也不致命**（新代码里是 try/except），
# 主等待策略是 _build_pw_script 里的 settle()（轮询元素数直到稳定）。
# 注意：本套页面上**没有** `<main>` / `role=main`，旧的 role=main 锚点是空转的，已删除。
WAIT_SELECTORS = {}

SNAPSHOT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "ui_snapshots"
)


# ---------------------------------------------------------------------------
# JS snippet to extract visible interactive elements from a page
# ---------------------------------------------------------------------------
JS_EXTRACT = """
() => {
    const SELECTORS = [
        'button',
        'a',
        '[role="menuitem"]',
        '[role="tab"]',
        'input',
        'select',
        '[role="combobox"]',
        '[data-testid]',
    ];
    const results = [];
    // 可见性判据**必须与 Playwright 对齐**（有实际尺寸 + 未被 visibility/display 隐藏）。
    // ⚠️ 曾经这里还有 `opacity === 0` 与 `!el.offsetParent` 两条 —— 会把 MUI 的开关
    //    整个过滤掉：MUI `<Switch>` 把原生 `<input type="checkbox">` 置为 opacity:0
    //    （真正的可见部分是外层 track/thumb 的 span），但 Playwright 仍能定位/点击它，
    //    YAML 也是靠 `input[name="contactEmail"]` 这类选择器操作的。
    //    ⇒ 旧判据让知识库丢掉最关键的设置开关（2026-09-18 实测发现）。
    const isVisible = (el) => {
        const style = getComputedStyle(el);
        if (style.display === 'none') return false;
        if (style.visibility === 'hidden') return false;
        const r = el.getBoundingClientRect();
        if (r.width <= 0 || r.height <= 0) return false;
        return true;
    };
    SELECTORS.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            if (!isVisible(el)) return;
            const entry = {
                tag:        el.tagName ? el.tagName.toLowerCase() : '',
                role:       el.getAttribute('role') || '',
                ariaLabel:  el.getAttribute('aria-label') || '',
                name:       (el.getAttribute('aria-label') || el.innerText || '').trim().substring(0, 80),
                testid:     el.getAttribute('data-testid') || '',
                type:       el.getAttribute('type') || '',
                placeholder: el.getAttribute('placeholder') || '',
                // HTML `name` 属性：本套 App 的表单控件主要靠它定位
                // （input[name="contactEmail"] 等）。不采集就查不回来。
                nameAttr:   el.getAttribute('name') || '',
                text:       (el.innerText || '').trim().substring(0, 80),
            };
            // Stable key for diffing
            const key = entry.testid || entry.role + '|' + (entry.name || entry.text || '');
            if (key) results.push({ key: key, ...entry });
        });
    });
    return results;
}
"""


# ---------------------------------------------------------------------------
# Environment & Cookie helpers
# ---------------------------------------------------------------------------

def _load_env_config() -> dict:
    """Load env_config.yaml and return the full config dict."""
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "config", "env_config.yaml"
    )
    try:
        import yaml
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _load_base_url(env: str) -> str:
    """Get BASE_URL for a given environment from env_config.yaml."""
    cfg = _load_env_config()
    envs = cfg.get("envs", {})
    if env in envs:
        return envs[env].get("base", "")
    # Fallback
    defaults = {"release": "https://release.pear.us", "staging": "https://staging.pear.us", "prod": "https://pear.us"}
    return defaults.get(env, "")


def _resolve_cookie_path(env: str, account: str = "main") -> Optional[str]:
    """Build path to cookie storage_state file. Returns None if not found."""
    cookie_patterns = {
        "release": "cookie_release",
        "staging": "cookie_staging",
        "prod": "cookie_prod",
    }
    prefix = cookie_patterns.get(env, f"cookie_{env}")

    # Account suffix mapping
    account_suffix_map = {
        "main":      "",
        "co_seller": "_co_seller",
        "partner":   "_partner_coseller",
        "demi":      "_demi",
        "yx":        "_yx",
    }
    suffix = account_suffix_map.get(account, f"_{account}")
    filename = prefix + suffix + ".json"

    cookie_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "test_case", "UI", "Test_Katana"
    )
    path = os.path.join(cookie_dir, filename)
    if os.path.exists(path):
        return path
    # Try without account suffix for simple cases
    if account == "main":
        simple = os.path.join(cookie_dir, prefix + ".json")
        if os.path.exists(simple):
            return simple
    return None


# ---------------------------------------------------------------------------
# Snapshot logic (runs in a single Playwright session to maintain cookies)
# ---------------------------------------------------------------------------

def take_snapshot(urls: List[str], env: str, account: str = "main") -> dict:
    """Visit multiple URLs with a SINGLE Playwright session (cookies persist),
    extract elements from each page, return dict {url_template: elements}."""
    base_url = _load_base_url(env)
    cookie_path = _resolve_cookie_path(env, account)

    if cookie_path:
        print(f"  [Cookie] Using: {os.path.basename(cookie_path)}")
    else:
        print(f"  [Cookie] No cookie file found for env={env}, account={account} -- visiting UNAUTHENTICATED")

    resolved_urls = {}
    for url_tpl in urls:
        resolved_urls[url_tpl] = url_tpl.replace("{BASE_URL}", base_url)

    script = _build_pw_script(resolved_urls, cookie_path, WAIT_SELECTORS)

    tmp_py = os.path.join(SNAPSHOT_DIR, "_pw_snapshot_run.py")
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    with open(tmp_py, "w", encoding="utf-8") as f:
        f.write(script)

    import subprocess
    result = subprocess.run(
        [sys.executable, tmp_py],
        capture_output=True,
        text=True,
        timeout=600,
    )
    # stderr contains progress messages, print them
    if result.stderr:
        sys.stderr.write(result.stderr)
        sys.stderr.flush()
    if result.returncode != 0:
        print("  ERROR: " + result.stderr[:500], file=sys.stderr)
        return {}

    try:
        data = json.loads(result.stdout)
        return data
    except json.JSONDecodeError:
        print("  ERROR parsing output: " + result.stdout[:300])
        return {}


def _build_pw_script(resolved_urls: Dict[str, str], cookie_path: Optional[str],
                     wait_selectors: Optional[Dict[str, str]] = None) -> str:
    """Build a self-contained Playwright script that visits all URLs in one session.

    等待策略（2026-09-18 修）：旧写法是 `wait_until="networkidle"` + `wait_for_selector("body")`，
    对 SPA 太弱 —— `/post/create`、`/events/create`、`/events/settings`、`/collabs` 实测
    只抓到 **2 个元素**（页面已渲染但还没 hydrate 完），把知识库质量拉低了一大截。
    现在改为 `domcontentloaded` + **轮询元素数直到稳定**，并加两道守卫：
      - 落到 `/login` → 跳过（访客 DOM 是垃圾，owner 控件全丢）
      - 正文含 "could not be found" → 404 页面，跳过（别把 404 页的链接灌进索引）
    """
    # ⚠️ 生成的临时脚本必须保持**纯 ASCII**（2026-09-18 修）：子进程按平台默认编码
    #   写/读临时 .py，脚本里一旦混入中文，就会在 "写入 → 被 py 当源码解析" 这条链路上
    #   冒出 `Non-UTF-8 code ... ` 的 SyntaxError（实测踩过，静态快照整步挂掉）。
    #   做法：① 所有数据用 json.dumps(...)（默认 ensure_ascii=True）内嵌；
    #        ② 脚本自带的注释/日志/文档串一律英文 ASCII；
    #        ③ 结果 stdout 也 ensure_ascii=True 转义，父进程再把 \uXXXX 解回来。
    urls_json = json.dumps(resolved_urls)              # ASCII-safe
    waits_json = json.dumps(wait_selectors or {})      # ASCII-safe
    cookie_arg = json.dumps(cookie_path) if cookie_path else "None"  # ASCII-safe
    js_ascii = ascii(JS_EXTRACT)                       # pure-ASCII Python literal of the JS source

    script = f"""
import sys, json, os
from playwright.sync_api import sync_playwright

RESOLVED_URLS = {urls_json}
WAIT_SELECTORS = {waits_json}
COOKIE_PATH = {cookie_arg}

JS_EXTRACT = {js_ascii}


def session_ok(context):
    \"\"\"Login-state check (project rule 1): cookie carries `..._web_auth_token`
    and NOT `..._web_auth_token_guest`. Visitor DOM is garbage (owner-only
    controls vanish), so it is better to write nothing than to pollute the KB.\"\"\"
    names = [c.get("name", "") for c in context.cookies()]
    has_auth = any(n.endswith("_web_auth_token") for n in names)
    has_guest = any(n.endswith("_web_auth_token_guest") for n in names)
    if not has_auth or has_guest:
        return False, f"auth_token={{has_auth}} guest_token={{has_guest}}"
    return True, "ok"


def settle(page):
    \"\"\"Wait until the SPA render is stable: fixed 2s, then poll element count;
    stable = the same non-trivial count twice in a row.\"\"\"
    page.wait_for_timeout(2000)
    prev, stable, waited = -1, 0, 0
    els = []
    while waited < 12000:
        els = page.evaluate(JS_EXTRACT)
        if len(els) == prev and len(els) > 2:
            stable += 1
            if stable >= 2:
                break
        else:
            stable = 0
        prev = len(els)
        page.wait_for_timeout(800)
        waited += 800
    return els


results = {{}}
warnings = []
login_redirects = []
session_checked = False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context_options = {{}}
    if COOKIE_PATH and os.path.exists(COOKIE_PATH):
        context_options["storage_state"] = COOKIE_PATH
    context = browser.new_context(**context_options)
    page = context.new_page()
    page.set_default_timeout(30000)

    for url_tpl, url in RESOLVED_URLS.items():
        print(f"Visiting: {{url}}", file=sys.stderr, flush=True)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            sel = WAIT_SELECTORS.get(url_tpl)
            if sel:
                try:
                    page.wait_for_selector(sel, timeout=8000)
                except Exception:
                    pass

            # Validate login state on first landing; abort the whole run if invalid
            # (never persist a full set of visitor DOM).
            if not session_checked:
                ok, why = session_ok(context)
                print(f"  [session] {{why}}", file=sys.stderr, flush=True)
                if not ok:
                    print(f"  [FATAL] invalid session ({{why}}) -> aborting, snapshot NOT written. "
                          f"Run: py -3.9 tools/get_all_cookies.py", file=sys.stderr, flush=True)
                    sys.exit(3)
                session_checked = True

            if "/login" in page.url:
                warnings.append(f"{{url_tpl}} -> redirected to login, skipped (stale cookie)")
                login_redirects.append(url_tpl)
                print(f"  SKIP: login redirect", file=sys.stderr, flush=True)
                results[url_tpl] = []
                continue
            elements = settle(page)
            body = (page.inner_text("body") or "")[:2000].lower()
            if "could not be found" in body:
                warnings.append(f"{{url_tpl}} -> 404 page (this page could not be found), skipped")
                print(f"  SKIP: 404 page", file=sys.stderr, flush=True)
                results[url_tpl] = []
                continue
            results[url_tpl] = elements
            print(f"  Got {{len(elements)}} elements", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"  ERROR: {{str(e)[:200]}}", file=sys.stderr, flush=True)
            results[url_tpl] = []

    browser.close()

for w in warnings:
    print(f"  [WARN] {{w}}", file=sys.stderr, flush=True)

# Any page redirected to login => this snapshot is untrustworthy, emit nothing.
if login_redirects:
    print(f"  [FATAL] {{len(login_redirects)}} page(s) redirected to login: {{login_redirects}}"
          f" -> snapshot untrustworthy, aborting (refresh cookie first)", file=sys.stderr, flush=True)
    sys.exit(3)

# ensure_ascii=True keeps stdout pure ASCII so the parent can decode it under ANY
# locale encoding; json.loads re-expands the escaped unicode sequences (backslash-u).
print(json.dumps(results), file=sys.stdout, flush=True)
"""
    return script


# ---------------------------------------------------------------------------
# Snapshot file I/O
# ---------------------------------------------------------------------------

def save_snapshot(label: str, env: str, data: dict) -> str:
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{label}__{env}__{timestamp}.json"
    filepath = os.path.join(SNAPSHOT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("  Snapshot saved: " + filepath)
    return filepath


def load_latest_snapshot(label: str, env: str):
    # type: (str, str) -> Optional[tuple]
    if not os.path.exists(SNAPSHOT_DIR):
        return None
    prefix = label + "__" + env + "__"
    files = [f for f in os.listdir(SNAPSHOT_DIR) if f.startswith(prefix) and f.endswith(".json")]
    if not files:
        return None
    latest = sorted(files)[-1]
    filepath = os.path.join(SNAPSHOT_DIR, latest)
    with open(filepath, encoding="utf-8") as f:
        return (filepath, json.load(f))


# ---------------------------------------------------------------------------
# Diff logic
# ---------------------------------------------------------------------------

def normalize_elements(elements):
    # type: (List[dict]) -> Dict[str, dict]
    result = {}
    for el in elements:
        key = el.get("key", "")
        if key:
            result[key] = el
    return result


def diff_snapshots(base_data: dict, target_data: dict) -> dict:
    base_by_url = base_data.get("urls", {})
    target_by_url = target_data.get("urls", {})

    all_urls = set(list(base_by_url.keys()) + list(target_by_url.keys()))
    report = {
        "by_url": {},
        "summary": {"added": 0, "removed": 0, "changed": 0},
    }

    for url in sorted(all_urls):
        base_els = normalize_elements(base_by_url.get(url, []))
        target_els = normalize_elements(target_by_url.get(url, []))

        added = [target_els[k] for k in target_els if k not in base_els]
        removed = [base_els[k] for k in base_els if k not in target_els]

        changed = []
        for k in base_els:
            if k in target_els:
                base_el = base_els[k]
                target_el = target_els[k]
                diffs = {}
                for field in ["name", "text", "role", "testid", "placeholder", "ariaLabel"]:
                    if base_el.get(field) != target_el.get(field):
                        diffs[field] = {
                            "old": base_el.get(field),
                            "new": target_el.get(field),
                        }
                if diffs:
                    changed.append({"key": k, "changes": diffs})

        if added or removed or changed:
            report["by_url"][url] = {
                "added": added[:10],
                "removed": removed[:10],
                "changed": changed[:10],
                "added_count": len(added),
                "removed_count": len(removed),
                "changed_count": len(changed),
            }
            report["summary"]["added"] += len(added)
            report["summary"]["removed"] += len(removed)
            report["summary"]["changed"] += len(changed)

    return report


def find_affected_yaml(step_key: str, workspace: str = ".") -> List[str]:
    """Search YAML files that reference a given key (element name/text/testid)."""
    import subprocess
    result = subprocess.run(
        ["grep", "-rl", step_key, os.path.join(workspace, "test_case")],
        capture_output=True,
        text=True,
    )
    files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
    return files


def print_report(report: dict) -> None:
    print("\n===== UI Snapshot Diff Report =====")
    summary = report["summary"]
    print(
        f"  Added: {summary['added']}  "
        f"Removed: {summary['removed']}  "
        f"Changed: {summary['changed']}"
    )
    print()

    for url, info in report["by_url"].items():
        print(f"  URL: {url}")
        if info["removed"]:
            print(f"    REMOVED ({info['removed_count']}):")
            for el in info["removed"][:5]:
                name_or_text = el.get("name") or el.get("text") or ""
                print(f"      - {(el.get('role') or el.get('tag') or '')}: {name_or_text}")
        if info["added"]:
            print(f"    ADDED ({info['added_count']}):")
            for el in info["added"][:5]:
                name_or_text = el.get("name") or el.get("text") or ""
                print(f"      + {(el.get('role') or el.get('tag') or '')}: {name_or_text}")
        if info["changed"]:
            print(f"    CHANGED ({info['changed_count']}):")
            for el in info["changed"][:5]:
                changes_desc = ", ".join(
                    f"{k}: {v['old']} -> {v['new']}"
                    for k, v in el["changes"].items()
                )
                print(f"      ~ {el['key']}: {changes_desc}")
        print()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_snapshot(args):
    env = args.env
    account = args.account
    label = args.label
    base_url = _load_base_url(env)
    cookie_path = _resolve_cookie_path(env, account)

    print(f"[snapshot] env={env}, account={account}, base_url={base_url}")
    if cookie_path:
        print(f"[snapshot] cookie={os.path.basename(cookie_path)}")

    urls_to_check = args.urls if args.urls else MONITORED_URLS

    data = take_snapshot(urls_to_check, env, account)

    if not data:
        print("No data captured, aborting save.")
        return

    snapshot_data = {
        "urls": data,
        "env": env,
        "account": account,
        "base_url": base_url,
        "cookie": os.path.basename(cookie_path) if cookie_path else None,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    save_snapshot(label, env, snapshot_data)


def cmd_diff(args):
    base = load_latest_snapshot(args.base, args.env)
    target = load_latest_snapshot(args.target, args.env)
    if not base:
        print(f"No snapshot found for label '{args.base}' / env '{args.env}'")
        return
    if not target:
        print(f"No snapshot found for label '{args.target}' / env '{args.env}'")
        return

    print(f"Diffing:\n  base:   {base[0]}\n  target: {target[0]}")
    report = diff_snapshots(base[1], target[1])
    print_report(report)

    # Save report
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    report_path = os.path.join(
        SNAPSHOT_DIR,
        f"diff__{args.base}__{args.target}__{args.env}.json",
    )
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nReport saved: {report_path}")


def cmd_check(args):
    """One-shot: snapshot(current) + diff + list affected YAML."""
    env = args.env
    account = args.account
    base_url = _load_base_url(env)
    cookie_path = _resolve_cookie_path(env, account)

    print(f"[check] env={env}, account={account}, base={args.base}")

    # 1) Load base snapshot
    base = load_latest_snapshot(args.base, env)
    if not base:
        print(
            f"No base snapshot '{args.base}' found. "
            f"Please run: snapshot --label {args.base} --env {env} --account {account} first."
        )
        return

    # 2) Take current snapshot
    data = take_snapshot(MONITORED_URLS, env, account)
    if not data:
        print("No data captured.")
        return

    snapshot_data = {
        "urls": data,
        "env": env,
        "account": account,
        "base_url": base_url,
        "cookie": os.path.basename(cookie_path) if cookie_path else None,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    target_path = save_snapshot(args.label, env, snapshot_data)

    # 3) Diff
    target = (target_path, snapshot_data)
    print(f"\nDiffing:\n  base:   {base[0]}\n  target: {target[0]}")
    report = diff_snapshots(base[1], target[1])
    print_report(report)

    # 4) Find affected YAML files
    print("\n===== Affected YAML files =====")
    found_any = False
    for url, info in report.get("by_url", {}).items():
        for el in info.get("removed", []):
            key = el.get("name") or el.get("text") or el.get("testid") or ""
            if key:
                files = find_affected_yaml(key)
                if files:
                    found_any = True
                    print(f"  '{key}' REMOVED -> may affect: {files}")
        for el in info.get("changed", []):
            for field, val in el.get("changes", {}).items():
                old_val = val.get("old") or ""
                if old_val and isinstance(old_val, str) and len(old_val) > 2:
                    files = find_affected_yaml(old_val)
                    if files:
                        found_any = True
                        print(f"  '{old_val}' CHANGED -> may affect: {files}")
    if not found_any:
        print("  No affected YAML files found.")


def main():
    # Parse in two stages: first parent args, then subcommand args
    # This allows --env/--account to appear before OR after the subcommand
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--env", default="release")
    parent_parser.add_argument("--account", default="main")

    parser = argparse.ArgumentParser(description="UI DOM Snapshot + Diff Tool")
    sub = parser.add_subparsers(dest="command", required=True)

    p_snap = sub.add_parser("snapshot", help="Take DOM snapshot of monitored URLs",
                            parents=[parent_parser])
    p_snap.add_argument("--label", required=True)
    p_snap.add_argument("--urls", nargs="*", help="Specific URLs to snapshot")

    p_diff = sub.add_parser("diff", help="Diff two snapshots",
                            parents=[parent_parser])
    p_diff.add_argument("--base", required=True)
    p_diff.add_argument("--target", required=True)

    p_check = sub.add_parser("check", help="Snapshot + diff + find affected YAML",
                             parents=[parent_parser])
    p_check.add_argument("--label", required=True)
    p_check.add_argument("--base", required=True)

    args = parser.parse_args()
    cmd_fn = {"snapshot": cmd_snapshot, "diff": cmd_diff, "check": cmd_check}[args.command]
    cmd_fn(args)


if __name__ == "__main__":
    main()
