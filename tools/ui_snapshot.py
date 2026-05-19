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
# ---------------------------------------------------------------------------
MONITORED_URLS = [
    "{BASE_URL}/events",
    "{BASE_URL}/autotestshop",
    "{BASE_URL}/catalog",
    "{BASE_URL}/dashboard",
    "{BASE_URL}/post/create",
    "{BASE_URL}/events/create",
    "{BASE_URL}/events/settings",
    "{BASE_URL}/collabs",
    "{BASE_URL}/shop",
]

WAIT_SELECTORS = {
    "{BASE_URL}/events":          "role=main",
    "{BASE_URL}/autotestshop":     "role=main",
    "{BASE_URL}/catalog":          "role=main",
    "{BASE_URL}/dashboard":        "role=main",
    "{BASE_URL}/post/create":      "role=main",
    "{BASE_URL}/events/create":    "role=main",
    "{BASE_URL}/events/settings": "role=main",
    "{BASE_URL}/collabs":         "role=main",
    "{BASE_URL}/shop":            "role=main",
}

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
    // Check if element is visible (not hidden by display/visibility/opacity)
    const isVisible = (el) => {
        if (!el.offsetParent && el.tagName !== 'BODY') return false;
        const style = getComputedStyle(el);
        if (style.display === 'none') return false;
        if (style.visibility === 'hidden') return false;
        if (parseFloat(style.opacity) === 0) return false;
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
            return yaml.safe_load(f) or {}
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

    script = _build_pw_script(resolved_urls, cookie_path)

    tmp_py = os.path.join(SNAPSHOT_DIR, "_pw_snapshot_run.py")
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    with open(tmp_py, "w", encoding="utf-8") as f:
        f.write(script)

    import subprocess
    result = subprocess.run(
        [sys.executable, tmp_py],
        capture_output=True,
        text=True,
        timeout=300,
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


def _build_pw_script(resolved_urls: Dict[str, str], cookie_path: Optional[str]) -> str:
    """Build a self-contained Playwright script that visits all URLs in one session."""
    urls_json = json.dumps(resolved_urls, ensure_ascii=False)
    cookie_arg = repr(cookie_path)  # Windows-safe: repr() escapes backslashes correctly

    script = f"""
import sys, json, os
from playwright.sync_api import sync_playwright

RESOLVED_URLS = {urls_json}
COOKIE_PATH = {cookie_arg}

JS_EXTRACT = {JS_EXTRACT!r}

results = {{}}

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
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_selector("body", timeout=10000)
            elements = page.evaluate(JS_EXTRACT)
            results[url_tpl] = elements
            print(f"  Got {{len(elements)}} elements", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"  ERROR: {{str(e)[:200]}}", file=sys.stderr, flush=True)
            results[url_tpl] = []

    browser.close()

print(json.dumps(results, ensure_ascii=False), file=sys.stdout, flush=True)
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
