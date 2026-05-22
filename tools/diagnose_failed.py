#!/usr/bin/env python3
"""
diagnose_failed.py — Failed Test Case Diagnosis Report Tool

Replays failed test cases from Allure reports with real browser execution,
captures screenshots + DOM snapshots at each step, probes failure causes,
and generates a detailed HTML diagnosis report.

Usage:
    # Diagnose all failed cases from the latest Allure run
    python tools/diagnose_failed.py

    # Specify a particular Allure run directory
    python tools/diagnose_failed.py --allure-dir 20260521_144342

    # Diagnose a single specific case
    python tools/diagnose_failed.py --case testT1928

    # Watch the replay in a real browser window
    python tools/diagnose_failed.py --case testT1928 --headed

    # Specify environment
    python tools/diagnose_failed.py --env release
"""

import ast
import argparse
import base64
import datetime
import glob
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
ALLURE_RESULTS_DIR = PROJECT_ROOT / "allure-results"
REPORT_OUTPUT_DIR = PROJECT_ROOT / "report"
COOKIE_DIR = PROJECT_ROOT / "test_case" / "UI" / "Test_Katana"

# Ensure project root is on sys.path so we can import test_case.* modules
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Mock heavy AI modules — diagnosis tool never uses ai_vision or RAG
# Without this, importing base.py triggers SentenceTransformer + faiss loading (~20s)
# ---------------------------------------------------------------------------
from unittest.mock import MagicMock
_mock_ai_vision = MagicMock()
_mock_rag_kb = MagicMock()
sys.modules.setdefault("test_case.UI.Test_Katana.utils.ai_vision", _mock_ai_vision)
sys.modules.setdefault("test_case.UI.Test_Katana.utils.rag_knowledge", _mock_rag_kb)

# ---------------------------------------------------------------------------
# JS: Extract visible interactive elements from page (from ui_snapshot.py)
# ---------------------------------------------------------------------------
JS_EXTRACT = """
() => {
    const SELECTORS = [
        'button', 'a', '[role="menuitem"]', '[role="tab"]', '[role="option"]',
        'input', 'select', '[role="combobox"]', '[role="dialog"]',
        '[data-testid]', '[role="button"]', '[role="link"]',
    ];
    const results = [];
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
                testid:     el.getAttribute('data-testid') || '',
                type:       el.getAttribute('type') || '',
                placeholder: el.getAttribute('placeholder') || '',
                text:       (el.innerText || '').trim().substring(0, 100),
                cls:        (el.getAttribute('class') || '').split(' ').filter(c => c).slice(0, 5).join(' '),
                href:       el.getAttribute('href') || '',
            };
            const key = entry.testid || entry.role + '|' + (entry.ariaLabel || entry.text || '');
            if (key) results.push({ key: key, ...entry });
        });
    });
    return results;
}
"""

# JS: Extract page content summary
JS_PAGE_SUMMARY = """
() => {
    return {
        title: document.title,
        url: window.location.href,
        bodyText: document.body.innerText.substring(0, 2000),
    };
}
"""


# ===========================================================================
# Phase 1: Extract failed cases from Allure results
# ===========================================================================

def find_latest_allure_dir() -> Optional[str]:
    """Find the most recent allure-results subdirectory."""
    if not ALLURE_RESULTS_DIR.exists():
        return None
    subdirs = [d for d in ALLURE_RESULTS_DIR.iterdir() if d.is_dir()]
    if not subdirs:
        return None
    subdirs.sort(key=lambda d: d.name, reverse=True)
    return str(subdirs[0])


def extract_failed_cases(allure_dir: str, filter_case: Optional[str] = None) -> List[Dict]:
    """
    Parse *-result.json files, extract failed/broken test cases.

    Returns list of dicts:
    {
        "name": "testT1928",
        "status": "failed",
        "error_message": "...",
        "error_trace": "...",
        "yaml_path": "...",
        "case_data": {...},  # full YAML test case dict
        "steps_order": ["step1", "step2", ...],
    }
    """
    results = []
    result_files = glob.glob(os.path.join(allure_dir, "*-result.json"))

    for f in result_files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue

        status = d.get("status", "").lower()
        if status not in ("failed", "broken"):
            continue

        name = d.get("name", "")
        if filter_case and name != filter_case:
            continue

        status_details = d.get("statusDetails") or {}
        error_message = status_details.get("message", "")
        error_trace = status_details.get("trace", "")

        # Parse parameters[0].value to get YAML test case data
        case_data = {}
        yaml_path = ""
        params = d.get("parameters", [])
        if params:
            raw_value = params[0].get("value", "")
            try:
                parsed = ast.literal_eval(raw_value)
                if isinstance(parsed, dict) and len(parsed) == 1:
                    case_key = list(parsed.keys())[0]
                    case_data = parsed[case_key]
                    yaml_path = case_data.get("__yaml_path__", "")
            except Exception:
                pass

        # Extract step order from test_step
        steps_order = list(case_data.get("test_step", {}).keys())

        results.append({
            "name": name,
            "status": status,
            "error_message": error_message,
            "error_trace": error_trace,
            "yaml_path": yaml_path,
            "case_data": case_data,
            "steps_order": steps_order,
        })

    return results


# ===========================================================================
# Phase 2: Browser replay engine
# ===========================================================================

def resolve_base_url(env: str) -> str:
    """Get BASE_URL from env_config.yaml."""
    config_path = PROJECT_ROOT / "config" / "env_config.yaml"
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg.get("envs", {}).get(env, {}).get("base", "https://release.pear.us")
    except Exception:
        return {"release": "https://release.pear.us", "staging": "https://staging.pear.us", "prod": "https://pear.us"}.get(env, "https://release.pear.us")


def inject_cookies(context, cookie_file: str) -> bool:
    """Inject cookies into browser context. Returns True on success."""
    # Resolve cookie file path
    if not os.path.isabs(cookie_file):
        cookie_file = str(PROJECT_ROOT / cookie_file)
    if not os.path.exists(cookie_file):
        print(f"    [DIAG] Cookie file NOT FOUND: {cookie_file}")
        return False

    with open(cookie_file, "r") as f:
        cookie_data = json.load(f)

    _log_cookie_diagnosis(cookie_file, cookie_data)

    if isinstance(cookie_data, list):
        cookies = cookie_data
    elif isinstance(cookie_data, dict) and "cookies" in cookie_data:
        cookies = cookie_data["cookies"]
    else:
        print(f"    [DIAG] Unrecognized cookie format")
        return False

    try:
        context.add_cookies(cookies)
        print(f"    [DIAG] add_cookies() succeeded ({len(cookies)} cookies)")
        return True
    except Exception as e:
        print(f"    [DIAG] add_cookies() FAILED: {e}")
        return False


def find_cookie_file_in_steps(case_data: dict) -> Optional[str]:
    """Scan test_step values to find a cookie_file reference."""
    test_step = case_data.get("test_step", {})
    pre_condition = case_data.get("pre_condition", {})
    for step_val in list(test_step.values()) + list(pre_condition.get("test_step", {}).values()):
        if isinstance(step_val, dict) and "cookie_file" in step_val:
            return step_val["cookie_file"]
    return None


def resolve_env_from_cookie(cookie_file: str) -> str:
    """Reverse-map cookie filename to environment name."""
    if "staging" in cookie_file:
        return "staging"
    elif "prod" in cookie_file:
        return "prod"
    return "release"


def resolve_cookie_file(cookie_file_raw: str, env: str) -> str:
    """Replace {ENV} placeholder and resolve to absolute path."""
    resolved = cookie_file_raw.replace("{ENV}", env)
    if not os.path.isabs(resolved):
        resolved = str(PROJECT_ROOT / resolved)
    return resolved


def _log_cookie_diagnosis(cookie_file: str, cookie_data: Any):
    """Print detailed cookie diagnostics for debugging."""
    print(f"    [DIAG] Cookie file: {cookie_file}")
    print(f"    [DIAG] File exists: {os.path.exists(cookie_file)}")
    if isinstance(cookie_data, list):
        print(f"    [DIAG] Format: list of {len(cookie_data)} cookies")
        for i, c in enumerate(cookie_data[:3]):
            domain = c.get('domain', 'N/A')
            name = c.get('name', 'N/A')[:20]
            print(f"    [DIAG]   Cookie[{i}]: domain={domain}, name={name}...")
    elif isinstance(cookie_data, dict):
        print(f"    [DIAG] Format: dict with keys {list(cookie_data.keys())}")
        if "cookies" in cookie_data:
            print(f"    [DIAG]   Nested cookies count: {len(cookie_data['cookies'])}")
    else:
        print(f"    [DIAG] Format: unexpected {type(cookie_data)}")


def capture_dom_snapshot(page) -> List[Dict]:
    """Capture DOM snapshot using JS_EXTRACT."""
    try:
        return page.evaluate(JS_EXTRACT)
    except Exception:
        return []


def capture_screenshot_b64(page) -> Optional[str]:
    """Capture screenshot as base64 string."""
    try:
        buf = page.screenshot(type="png", full_page=False)
        return base64.b64encode(buf).decode("utf-8")
    except Exception:
        return None


def capture_page_summary(page) -> Dict:
    """Capture page title, URL, and body text."""
    try:
        return page.evaluate(JS_PAGE_SUMMARY)
    except Exception:
        return {}


def auto_dismiss_modals(page):
    """Try to auto-dismiss common popups/modals."""
    try:
        # Close EDU modal if present
        close_btn = page.locator("button[aria-label='Close'], button[aria-label='Got it'], button[aria-label='close dialog'], button[aria-label='Close dialog']").first
        if close_btn.is_visible(timeout=2000):
            close_btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass


def replay_case(case_info: dict, base_url: str, headed: bool) -> Dict:
    """
    Replay a single failed test case in the browser.

    Returns diagnostic result dict with all collected data.
    """
    from playwright.sync_api import sync_playwright

    case_name = case_info["name"]
    case_data = case_info["case_data"]
    test_step = case_data.get("test_step", {})
    pre_condition = case_data.get("pre_condition", {})
    steps_order = case_info["steps_order"]

    # Build step records list
    step_records = []
    failed_step_name = None
    failed_step_error = ""
    failure_found = False
    probing_results = []

    print(f"\n{'='*60}")
    print(f"  DIAGNOSING: {case_name}")
    print(f"  YAML: {case_info['yaml_path']}")
    print(f"  Steps: {len(steps_order)}")
    print(f"{'='*60}")

    # Determine environment and base URL before launching browser
    cookie_file_raw = find_cookie_file_in_steps(case_data)
    if cookie_file_raw:
        env = resolve_env_from_cookie(cookie_file_raw)
        actual_base_url = resolve_base_url(env)
        cookie_file = resolve_cookie_file(cookie_file_raw, env)
    else:
        # Fallback: infer from base_url (same logic as conftest.py _ENV_MAP)
        env_map = {
            "https://staging.pear.us": "staging",
            "https://release.pear.us": "release",
            "https://pear.us": "prod",
        }
        env = env_map.get(base_url, "release")
        actual_base_url = base_url
        # Try default cookie file (same as conftest.py)
        cookie_file = str(COOKIE_DIR / f"cookie_{env}.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed, args=["--start-maximized"])

        # Use storage_state if cookie file exists (same mechanism as conftest.py)
        context_args = {"viewport": {"width": 1440, "height": 900}}
        if os.path.exists(cookie_file):
            context_args["storage_state"] = cookie_file
            print(f"  [COOKIES] Using storage_state: {cookie_file}")
        else:
            print(f"  [COOKIES] No cookie file found at: {cookie_file}")

        context = browser.new_context(**context_args)
        page = context.new_page()
        page.set_default_timeout(15000)

        # Also import smart_sleep so we can handle it natively
        def do_smart_sleep(page, v):
            """Handle sleep_step natively."""
            if isinstance(v, dict):
                ms = v.get("sleep_step", v.get("ms", 1000))
            else:
                ms = int(v) if isinstance(v, (int, float)) else 1000
            ms = max(200, min(ms, 5000))  # Cap at 5s for diagnostics
            page.wait_for_timeout(ms)

        # Pre-condition steps — run them just like normal test steps
        pre_steps = pre_condition.get("test_step", {})
        if pre_steps:
            print(f"  [PRE-CONDITION] Running {len(pre_steps)} pre-steps...")
            pre_step_num = 0
            for pk, pv in pre_steps.items():
                pre_step_num += 1
                try:
                    if pk.startswith("sleep"):
                        do_smart_sleep(page, pv)
                    else:
                        print(f"    [PRE {pre_step_num}/{len(pre_steps)}] {pk} ... ", end="", flush=True)
                        _execute_step(page, pk, pv, actual_base_url)
                        print("OK")
                except Exception as e:
                    print(f"FAILED - {e[:80]}")
                    print(f"    [PRE-CONDITION] Step '{pk}' failed (non-blocking)")
                    # If open fails, stop pre-condition (nothing else will work)
                    if pk.startswith("open"):
                        break

        # --- Core step replay ---
        for idx, step_name in enumerate(steps_order):
            step_value = test_step[step_name]
            step_num = idx + 1

            # Determine expected action type
            action_type = _classify_step(step_name, step_value)
            print(f"  [{step_num}/{len(steps_order)}] {step_name} ({action_type}) ... ", end="", flush=True)

            # --- BEFORE: screenshot + DOM ---
            before_screenshot = capture_screenshot_b64(page)
            before_dom = capture_dom_snapshot(page)
            before_summary = capture_page_summary(page)

            # --- Execute step ---
            error_msg = ""
            after_screenshot = None
            after_dom = None

            try:
                _execute_step(page, step_name, step_value, actual_base_url)

                # Success
                after_screenshot = capture_screenshot_b64(page)
                after_dom = capture_dom_snapshot(page)
                print("PASSED")

                step_records.append({
                    "step_num": step_num,
                    "step_name": step_name,
                    "action_type": action_type,
                    "step_value": step_value,
                    "status": "passed",
                    "before_screenshot": before_screenshot,
                    "after_screenshot": after_screenshot,
                    "before_dom": before_dom,
                    "after_dom": after_dom,
                    "before_summary": before_summary,
                    "error": "",
                })

            except Exception as e:
                error_msg = str(e)
                after_screenshot = capture_screenshot_b64(page)
                after_dom = capture_dom_snapshot(page)
                after_summary = capture_page_summary(page)

                # Optional steps: treat failure as skipped, don't stop replay
                is_optional = "optional" in step_name.lower()
                if is_optional:
                    print(f"SKIPPED (optional) - {error_msg[:60]}")
                    step_records.append({
                        "step_num": step_num,
                        "step_name": step_name,
                        "action_type": action_type,
                        "step_value": step_value,
                        "status": "skipped",
                        "before_screenshot": before_screenshot,
                        "after_screenshot": after_screenshot,
                        "before_dom": before_dom,
                        "after_dom": after_dom,
                        "before_summary": before_summary,
                        "error": f"Optional step not found: {error_msg[:120]}",
                    })
                    continue

                print(f"FAILED - {error_msg[:80]}")

                if not failure_found:
                    failure_found = True
                    failed_step_name = step_name
                    failed_step_error = error_msg

                    # --- Phase 3: Multi-strategy probing ---
                    print(f"  [PROBING] Running diagnosis on failed step...")
                    probing_results = probe_failure(page, step_name, step_value, error_msg)

                step_records.append({
                    "step_num": step_num,
                    "step_name": step_name,
                    "action_type": action_type,
                    "step_value": step_value,
                    "status": "failed",
                    "before_screenshot": before_screenshot,
                    "after_screenshot": after_screenshot,
                    "before_dom": before_dom,
                    "after_dom": after_dom,
                    "before_summary": before_summary,
                    "error": error_msg,
                    "probing": probing_results if failure_found and step_name == failed_step_name else [],
                })

                # Stop replay after first failure (subsequent steps would be meaningless)
                print(f"  [STOP] Replay stopped at first failure.")
                break

        # Assertion phase check
        if not failure_found:
            expect_result = case_data.get("expect_result", {})
            assertions = expect_result.get("assertions", [])
            if assertions:
                print(f"\n  [ASSERTION] Checking {len(assertions)} assertion(s)...")
                assertion_screenshot = capture_screenshot_b64(page)
                assertion_dom = capture_dom_snapshot(page)

                for a_idx, assertion in enumerate(assertions):
                    a_type = assertion.get("assertion_type", "")
                    print(f"    Assertion {a_idx+1}: {a_type} ... ", end="", flush=True)
                    try:
                        _execute_assertion(page, assertion, actual_base_url)
                        print("PASSED")
                    except Exception as a_err:
                        print(f"FAILED - {a_err}")
                        if not failure_found:
                            failure_found = True
                            failed_step_name = f"assertion_{a_idx+1}"
                            failed_step_error = str(a_err)

                            # Screenshot after assertion failure
                            assert_fail_screenshot = capture_screenshot_b64(page)
                            assert_fail_dom = capture_dom_snapshot(page)

                            probing_results = probe_assertion_failure(page, assertion, a_err, assertion_dom)

                            step_records.append({
                                "step_num": len(steps_order) + a_idx + 1,
                                "step_name": f"assertion_{a_idx+1}",
                                "action_type": f"assertion: {a_type}",
                                "step_value": assertion,
                                "status": "failed",
                                "before_screenshot": assertion_screenshot,
                                "after_screenshot": assert_fail_screenshot,
                                "before_dom": assertion_dom,
                                "after_dom": assert_fail_dom,
                                "before_summary": capture_page_summary(page),
                                "error": str(a_err),
                                "probing": probing_results,
                            })
                        break

        browser.close()

    return {
        "case_name": case_name,
        "yaml_path": case_info["yaml_path"],
        "allure_error": case_info["error_message"],
        "allure_trace": case_info["error_trace"],
        "failed_step": failed_step_name,
        "failed_step_error": failed_step_error,
        "step_records": step_records,
        "total_steps": len(steps_order),
        "steps_passed": sum(1 for s in step_records if s["status"] == "passed"),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _classify_step(step_name: str, step_value: Any) -> str:
    """Classify step type for display."""
    sn = step_name.lower()
    if sn.startswith("open") or sn.startswith("open_"):
        return "open"
    if sn.startswith("sleep"):
        return "sleep"
    if sn.startswith("r_click") or sn.startswith("click") or sn.startswith("l_click"):
        return "click"
    if sn.startswith("fill"):
        return "fill"
    if sn.startswith("check") or sn.startswith("uncheck"):
        return "check"
    if sn.startswith("verify"):
        return "verify"
    if sn.startswith("scroll") or sn.startswith("swipe") or sn.startswith("page_scroll"):
        return "scroll"
    if sn.startswith("wait"):
        return "wait"
    if sn.startswith("press"):
        return "keypress"
    if sn.startswith("go_back"):
        return "navigation"
    if sn.startswith("reload"):
        return "reload"
    if sn.startswith("upload"):
        return "upload"
    if sn.startswith("smart_if"):
        return "conditional"
    if sn.startswith("save_html"):
        return "save_html"
    if sn.startswith("execute_js"):
        return "js"
    if sn.startswith("handle_modal"):
        return "modal"
    if sn.startswith("session_"):
        return "session"
    if sn.startswith("smart_click_optional"):
        return "click_optional"
    if sn.startswith("smart_click_retry"):
        return "click_retry"
    if isinstance(step_value, (int, float)):
        return "sleep"
    return "other"


def _execute_step(page, step_name: str, step_value: Any, base_url: str):
    """Execute a single test step using simplified Playwright logic."""
    sn = step_name.lower()

    # --- Sleep steps ---
    if sn.startswith("sleep") or isinstance(step_value, (int, float)):
        ms = step_value if isinstance(step_value, (int, float)) else step_value.get("sleep_step", 1000) if isinstance(step_value, dict) else 1000
        ms = max(200, min(int(ms), 5000))
        page.wait_for_timeout(ms)
        return

    # --- Open URL ---
    if sn.startswith("open"):
        url = step_value.get("open") or step_value.get("url") if isinstance(step_value, dict) else step_value
        if not url:
            return
        url = str(url).replace("{BASE_URL}", base_url)

        # Handle cookie_file
        if isinstance(step_value, dict) and "cookie_file" in step_value:
            cookie_file = step_value["cookie_file"]
            if not os.path.isabs(cookie_file):
                cookie_file = str(PROJECT_ROOT / cookie_file)
            if os.path.exists(cookie_file):
                with open(cookie_file, "r") as f:
                    cookie_data = json.load(f)
                cookies = cookie_data if isinstance(cookie_data, list) else cookie_data.get("cookies", [])
                page.context.add_cookies(cookies)

        page.goto(url, wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        auto_dismiss_modals(page)
        return

    # --- Check/Uncheck ---
    if sn.startswith("check") or sn.startswith("uncheck"):
        should_check = sn.startswith("check")
        loc_str = step_value.get("locator", "") if isinstance(step_value, dict) else ""
        if loc_str:
            el = page.locator(loc_str).first
            if should_check:
                el.check(timeout=5000)
            else:
                el.uncheck(timeout=5000)
            return

    # --- Fill ---
    if sn.startswith("fill"):
        loc_str = step_value.get("locator", "") if isinstance(step_value, dict) else ""
        fill_val = step_value.get("value", "") if isinstance(step_value, dict) else ""
        if loc_str and fill_val is not None:
            el = page.locator(loc_str).first
            el.fill(str(fill_val), timeout=5000)
            return

    # --- Click steps (the most complex) ---
    if (sn.startswith("r_click") or sn.startswith("click") or sn.startswith("l_click")
            or sn.startswith("smart_click_optional") or sn.startswith("smart_click_retry")):
        _execute_click_step(page, step_name, step_value)
        return

    # --- Verify text visible ---
    if sn.startswith("verify_text_visible") or sn == "verify_product_visible":
        text = step_value.get("text", "") if isinstance(step_value, dict) else ""
        if text:
            page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=10000)
        return

    # --- Verify text hidden ---
    if sn.startswith("verify_hidden"):
        text = step_value.get("text", "") if isinstance(step_value, dict) else ""
        if text:
            page.get_by_text(text, exact=False).first.wait_for(state="hidden", timeout=5000)
        return

    # --- Verify value ---
    if sn.startswith("verify_value"):
        loc_str = step_value.get("locator", "") if isinstance(step_value, dict) else ""
        expected = step_value.get("value", "") if isinstance(step_value, dict) else ""
        if loc_str:
            el = page.locator(loc_str).first
            actual = el.input_value(timeout=5000)
            if str(actual) != str(expected):
                raise AssertionError(f"Value mismatch: expected '{expected}', got '{actual}'")
        return

    # --- Wait for URL ---
    if sn.startswith("wait_for_url") or sn.startswith("verify_navigation"):
        url_or_pattern = step_value.get("url", "") if isinstance(step_value, dict) else ""
        if url_or_pattern:
            url_or_pattern = str(url_or_pattern).replace("{BASE_URL}", base_url)
            page.wait_for_url(url_or_pattern, timeout=10000)
        return

    # --- Wait for selector ---
    if sn.startswith("wait_for_selector"):
        sel = step_value.get("selector", "") if isinstance(step_value, dict) else ""
        if sel:
            page.wait_for_selector(sel, state="visible", timeout=10000)
        return

    # --- Wait toast ---
    if sn.startswith("wait_toast"):
        text = step_value.get("text", "") if isinstance(step_value, dict) else ""
        if text:
            page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=10000)
            page.wait_for_timeout(2000)
        return

    # --- Wait (generic) ---
    if sn.startswith("wait_"):
        page.wait_for_timeout(2000)
        return

    # --- Scroll ---
    if sn.startswith("scroll") or sn.startswith("swipe") or sn.startswith("page_scroll"):
        y = step_value.get("y", 0) if isinstance(step_value, dict) else 0
        if y:
            page.mouse.wheel(0, y)
            page.wait_for_timeout(500)
        return

    # --- Press key ---
    if sn.startswith("press"):
        key = step_value.get("key", "") if isinstance(step_value, dict) else ""
        if key:
            page.keyboard.press(key)
        return

    # --- Reload ---
    if sn.startswith("reload"):
        page.reload(wait_until="load", timeout=30000)
        page.wait_for_timeout(2000)
        return

    # --- Go back ---
    if sn.startswith("go_back"):
        page.go_back(wait_until="load", timeout=15000)
        page.wait_for_timeout(1000)
        return

    # --- Upload ---
    if sn.startswith("upload"):
        loc_str = step_value.get("locator", "") if isinstance(step_value, dict) else ""
        file_path = step_value.get("file", "") if isinstance(step_value, dict) else ""
        if loc_str and file_path:
            el = page.locator(loc_str).first
            abs_path = str(PROJECT_ROOT / file_path) if not os.path.isabs(file_path) else file_path
            el.set_input_files(abs_path, timeout=5000)
        return

    # --- Save HTML (skip in diagnostic) ---
    if sn.startswith("save_html"):
        return

    # --- Execute JS ---
    if sn.startswith("execute_js"):
        script = step_value.get("script", "") if isinstance(step_value, dict) else ""
        if script:
            page.evaluate(script)
        return

    # --- Handle modal / auto_handle_modals (skip in diagnostic) ---
    if sn.startswith("handle_modal") or sn.startswith("auto_handle_modals"):
        return

    # --- Conditional (smart_if) ---
    if sn.startswith("smart_if"):
        condition = step_value.get("condition", "") if isinstance(step_value, dict) else ""
        then_steps = step_value.get("then", {}) if isinstance(step_value, dict) else {}
        else_steps = step_value.get("else", {}) if isinstance(step_value, dict) else {}
        # Simplified: just try then steps
        for tk, tv in then_steps.items():
            _execute_step(page, tk, tv, base_url)
        return

    # --- Session actions (skip) ---
    if sn.startswith("session_") or sn.startswith("create_session") or sn.startswith("switch_session") or sn.startswith("close_session"):
        print(f"(session action, skipped)")
        return

    # --- screenshot step (capture but don't save file) ---
    if sn.startswith("screenshot"):
        return

    # --- Unknown step: try project action registry, then click fallback ---
    # Import project's action registry for custom actions (e.g. delete_coseller_if_exists)
    try:
        from test_case.UI.Test_Katana.actions import get_action
        action_fn = get_action(step_name)
        if action_fn:
            action_fn(page, step_value if isinstance(step_value, dict) else {})
            return
    except Exception:
        pass

    if isinstance(step_value, dict) and any(k in step_value for k in ["role", "locator", "text", "name", "test_id"]):
        _execute_click_step(page, step_name, step_value)
        return

    print(f"(unhandled: {step_name})")


def _execute_click_step(page, step_name: str, v: dict):
    """Execute a click step with multiple location strategies."""
    if not isinstance(v, dict):
        return

    target_role = v.get("role")
    target_name = v.get("name") or v.get("text") or v.get("label") or v.get("placeholder")
    target_locator = v.get("locator")
    target_test_id = v.get("test_id")
    target_index = v.get("index", 0)
    force = v.get("force", False)
    optional = v.get("optional", False)
    exact = v.get("exact", False)

    # Skip if no actionable targets
    if not target_name and not target_locator and not target_role and not target_test_id:
        return

    # 1. Test ID
    if target_test_id:
        try:
            el = page.get_by_test_id(target_test_id).nth(target_index)
            if el.is_visible(timeout=3000):
                el.click(force=force)
                return
        except Exception:
            if optional:
                return

    # 2. Locator (CSS or XPath)
    if target_locator:
        try:
            if target_locator.startswith("/") or target_locator.startswith("xpath="):
                xpath_loc = target_locator if target_locator.startswith("xpath=") else f"xpath={target_locator}"
                el = page.locator(xpath_loc).nth(target_index)
            else:
                el = page.locator(target_locator).nth(target_index)

            # If both locator + text/role, try combining
            if target_name:
                try:
                    el = el.get_by_text(target_name, exact=exact)
                except Exception:
                    pass

            el.click(force=force, timeout=5000)
            page.wait_for_timeout(300)
            return
        except Exception as e:
            if optional:
                return

    # 3. Aria-label fallback
    if target_name:
        try:
            el = page.locator(f'[aria-label="{target_name}"], [aria-label*="{target_name}"]').nth(target_index)
            el.click(force=force, timeout=3000)
            page.wait_for_timeout(300)
            return
        except Exception:
            pass

    # 4. Role / text
    try:
        if target_role:
            el = page.get_by_role(role=target_role, name=target_name, exact=exact).nth(target_index)
        elif target_name:
            el = page.get_by_text(target_name, exact=exact).nth(target_index)
        else:
            raise Exception("No locator strategy matched")

        el.click(timeout=5000)
        page.wait_for_timeout(300)
        if target_role == "option":
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
        return
    except Exception:
        try:
            el.click(force=True, timeout=3000)
            page.wait_for_timeout(300)
            return
        except Exception:
            pass

    if optional:
        return

    raise Exception(f"Element not found: role={target_role}, name={target_name}, locator={target_locator}, test_id={target_test_id}")


def _execute_assertion(page, assertion: dict, base_url: str):
    """Execute a single assertion check."""
    a_type = assertion.get("assertion_type", "")

    if a_type == "element_visible_by_text":
        text = assertion.get("text", "")
        if text:
            page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=10000)
            return

    elif a_type == "element_visible":
        role = assertion.get("role")
        name = assertion.get("name")
        if role:
            page.get_by_role(role, name=name).first.wait_for(state="visible", timeout=10000)
            return

    elif a_type == "element_visible_by_locator":
        locator = assertion.get("locator", "")
        if locator:
            page.locator(locator).first.wait_for(state="visible", timeout=10000)
            return

    elif a_type == "element_not_visible":
        role = assertion.get("role")
        name = assertion.get("name")
        locator = assertion.get("locator")
        if locator:
            el = page.locator(locator).first
            if el.is_visible(timeout=3000):
                raise AssertionError(f"Element should NOT be visible: {locator}")
        elif role:
            el = page.get_by_role(role, name=name).first
            if el.is_visible(timeout=3000):
                raise AssertionError(f"Element should NOT be visible: {role} '{name}'")
        return

    elif a_type == "element_checked":
        locator = assertion.get("locator", "")
        index = assertion.get("index", 0)
        if locator:
            is_checked = page.locator(locator).nth(index).is_checked(timeout=5000)
            if not is_checked:
                raise AssertionError(f"Element should be checked: {locator}[{index}]")
        return

    elif a_type == "element_not_checked":
        locator = assertion.get("locator", "")
        if locator:
            is_checked = page.locator(locator).first.is_checked(timeout=3000)
            if is_checked:
                raise AssertionError(f"Element should NOT be checked: {locator}")
        return


# ===========================================================================
# Phase 3: Multi-strategy failure probing
# ===========================================================================

def probe_failure(page, step_name: str, step_value: dict, error_msg: str) -> List[Dict]:
    """
    At the failure step, try multiple strategies to understand why the element was not found.
    Returns list of probe result dicts.
    """
    probes = []

    if not isinstance(step_value, dict):
        return probes

    target_role = step_value.get("role")
    target_name = step_value.get("name") or step_value.get("text") or step_value.get("label") or step_value.get("placeholder")
    target_locator = step_value.get("locator")
    target_test_id = step_value.get("test_id")

    # Probe 1: Find elements containing target text
    if target_name:
        try:
            elements = page.locator("*").filter(has_text=target_name).all()
            matches = []
            for el in elements[:10]:
                try:
                    tag = el.evaluate("e => e.tagName.toLowerCase()")
                    text = el.evaluate("e => (e.innerText || '').trim().substring(0, 100)")
                    role = el.get_attribute("role") or ""
                    aria = el.get_attribute("aria-label") or ""
                    testid = el.get_attribute("data-testid") or ""
                    visible = el.is_visible()
                    matches.append({
                        "tag": tag, "text": text, "role": role,
                        "ariaLabel": aria, "testid": testid, "visible": visible
                    })
                except Exception:
                    pass
            probes.append({
                "probe": f"Elements containing text '{target_name}'",
                "count": len(elements),
                "matches": matches,
            })
        except Exception as e:
            probes.append({"probe": f"Text search for '{target_name}'", "error": str(e)})

    # Probe 2: Find elements by role
    if target_role:
        try:
            elements = page.get_by_role(target_role).all()
            matches = []
            for el in elements[:10]:
                try:
                    text = el.evaluate("e => (e.innerText || '').trim().substring(0, 80)")
                    aria = el.get_attribute("aria-label") or ""
                    testid = el.get_attribute("data-testid") or ""
                    visible = el.is_visible()
                    matches.append({"text": text, "ariaLabel": aria, "testid": testid, "visible": visible})
                except Exception:
                    pass
            probes.append({
                "probe": f"All elements with role='{target_role}'",
                "count": len(elements),
                "matches": matches,
            })
        except Exception as e:
            probes.append({"probe": f"Role search for '{target_role}'", "error": str(e)})

    # Probe 3: Find elements by test_id pattern
    if target_test_id:
        try:
            elements = page.locator(f'[data-testid*="{target_test_id}"]').all()
            matches = []
            for el in elements[:10]:
                try:
                    testid = el.get_attribute("data-testid") or ""
                    text = el.evaluate("e => (e.innerText || '').trim().substring(0, 80)")
                    visible = el.is_visible()
                    matches.append({"testid": testid, "text": text, "visible": visible})
                except Exception:
                    pass
            probes.append({
                "probe": f"Elements with testid containing '{target_test_id}'",
                "count": len(elements),
                "matches": matches,
            })
        except Exception as e:
            probes.append({"probe": f"TestId search for '{target_test_id}'", "error": str(e)})

    # Probe 4: Try locator directly
    if target_locator:
        try:
            count = page.locator(target_locator).count()
            probes.append({
                "probe": f"Locator '{target_locator}' count",
                "count": count,
                "matches": [{"info": f"Found {count} element(s) with this locator"}],
            })
        except Exception as e:
            probes.append({"probe": f"Locator '{target_locator}'", "error": str(e)})

    # Probe 5: Check if any active modal/dialog
    try:
        modals = page.locator("[role='dialog'], .MuiDialog-root, .MuiModal-root, .MuiPopover-root").all()
        visible_modals = []
        for m in modals[:5]:
            try:
                if m.is_visible():
                    modal_text = m.evaluate("e => (e.innerText || '').trim().substring(0, 200)")
                    visible_modals.append({"text": modal_text})
            except Exception:
                pass
        if visible_modals:
            probes.append({
                "probe": "Active modals/dialogs/popovers on page",
                "count": len(visible_modals),
                "matches": visible_modals,
            })
    except Exception:
        pass

    # Probe 6: aria-label search
    if target_name:
        try:
            elements = page.locator(f'[aria-label*="{target_name}"]').all()
            matches = []
            for el in elements[:10]:
                try:
                    tag = el.evaluate("e => e.tagName.toLowerCase()")
                    aria = el.get_attribute("aria-label") or ""
                    text = el.evaluate("e => (e.innerText || '').trim().substring(0, 80)")
                    visible = el.is_visible()
                    matches.append({"tag": tag, "ariaLabel": aria, "text": text, "visible": visible})
                except Exception:
                    pass
            probes.append({
                "probe": f"Elements with aria-label containing '{target_name}'",
                "count": len(elements),
                "matches": matches,
            })
        except Exception:
            pass

    return probes


def probe_assertion_failure(page, assertion: dict, error_msg: str, dom_snapshot: list) -> List[Dict]:
    """Probe assertion failures (locator/text not found)."""
    probes = []
    a_type = assertion.get("assertion_type", "")

    if a_type == "element_visible_by_text":
        target_text = assertion.get("text", "")
        # Search for similar text in DOM
        similar = [e for e in dom_snapshot if target_text.lower() in e.get("text", "").lower() or target_text in e.get("text", "")]
        probes.append({
            "probe": f"DOM elements matching '{target_text}'",
            "count": len(similar),
            "matches": similar[:10],
        })
        # Also search for partial matches
        words = target_text.split()[:3]  # first 3 words
        partial = [e for e in dom_snapshot if any(w.lower() in e.get("text", "").lower() for w in words if len(w) > 2)]
        if partial and not similar:
            probes.append({
                "probe": f"Partial text matches (first 3 words of '{target_text}')",
                "count": len(partial),
                "matches": partial[:10],
            })

    elif a_type == "element_visible_by_locator":
        locator = assertion.get("locator", "")
        try:
            count = page.locator(locator).count()
            probes.append({
                "probe": f"Locator '{locator}' element count",
                "count": count,
                "matches": [{"info": f"Found {count} element(s)"}],
            })
        except Exception as e:
            probes.append({"probe": f"Locator '{locator}'", "error": str(e)})

    elif a_type == "element_visible":
        role = assertion.get("role")
        name = assertion.get("name")
        if role:
            try:
                elements = page.get_by_role(role, name=name).all()
                probes.append({
                    "probe": f"Elements with role='{role}' name='{name}'",
                    "count": len(elements),
                    "matches": [{"info": f"Found {len(elements)} element(s)"}],
                })
            except Exception as e:
                probes.append({"probe": f"Role='{role}' name='{name}'", "error": str(e)})

    return probes


# ===========================================================================
# Phase 4: HTML Report Generation
# ===========================================================================

def generate_html_report(diagnosis_results: List[Dict], env: str, allure_dir: str) -> str:
    """Generate a standalone HTML diagnosis report. Returns the file path."""
    REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = str(REPORT_OUTPUT_DIR / f"Error_Test_Case_Diagnosis_Report_{timestamp}.html")

    # Build HTML
    html_parts = [_HTML_HEAD]
    html_parts.append(_render_summary(diagnosis_results, env, allure_dir))

    for result in diagnosis_results:
        html_parts.append(_render_case(result))

    html_parts.append(_HTML_FOOTER)
    html_content = "\n".join(html_parts)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return report_path


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;"))


def _render_summary(results: List[Dict], env: str, allure_dir: str) -> str:
    """Render the summary dashboard section."""
    total = len(results)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = ""
    for i, r in enumerate(results):
        status_icon = "&#10060;" if r["failed_step"] else "&#9989;"
        case_id = f"case_{i}"
        rows += f"""
        <tr>
            <td><a href="#{case_id}" style="color:#4a90d9;text-decoration:none;font-weight:600">{_esc(r['case_name'])}</a></td>
            <td>{status_icon}</td>
            <td>{_esc(r['failed_step'] or 'N/A')}</td>
            <td>{_esc((r['failed_step_error'] or '')[:80])}</td>
            <td>{r['steps_passed']}/{r['total_steps']}</td>
            <td>{_esc(r['yaml_path'].split('/')[-1] if r['yaml_path'] else 'N/A')}</td>
        </tr>"""

    return f"""
    <div class="summary-section">
        <h2>Summary Dashboard</h2>
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{total}</div>
                <div class="stat-label">Failed Cases Diagnosed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for r in results if r['failed_step'])}</div>
                <div class="stat-label">Failure Reproduced</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(1 for r in results if not r['failed_step'])}</div>
                <div class="stat-label">Passed on Replay (Flaky?)</div>
            </div>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Case</th><th>Status</th><th>Failed Step</th><th>Error</th><th>Progress</th><th>YAML</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        <div class="meta-info">
            Environment: <strong>{_esc(env)}</strong> &nbsp;|&nbsp;
            Allure Run: <strong>{_esc(allure_dir)}</strong> &nbsp;|&nbsp;
            Generated: <strong>{ts}</strong>
        </div>
    </div>"""


def _render_case(result: Dict) -> str:
    """Render a single case diagnosis section."""
    i = hash(result["case_name"]) % 10000
    case_id = f"case_{i}"

    # Error section
    error_section = ""
    if result["allure_error"]:
        error_section = f"""
        <div class="error-box">
            <div class="error-title">Allure Error Message</div>
            <pre>{_esc(result['allure_error'])}</pre>
        </div>"""

    # Step-by-step replay
    steps_html = ""
    for sr in result["step_records"]:
        steps_html += _render_step_record(sr)

    # If no failure found during replay
    if not result["failed_step"] and not any(s["status"] == "failed" for s in result["step_records"]):
        steps_html += f"""
        <div class="flaky-notice">
            All steps passed during replay. This may be a flaky test or a timing issue.
            The original Allure error was: <code>{_esc(result['allure_error'][:200])}</code>
        </div>"""

    return f"""
    <div class="case-section" id="{case_id}">
        <h2>Case: {_esc(result['case_name'])}</h2>
        <div class="case-meta">
            YAML: <code>{_esc(result['yaml_path'])}</code><br>
            Timestamp: {_esc(result['timestamp'])}
        </div>
        {error_section}
        <h3>Step-by-Step Replay</h3>
        <div class="steps-container">{steps_html}</div>
    </div>"""


def _render_step_record(sr: Dict) -> str:
    """Render a single step record."""
    status_class = {"passed": "step-passed", "skipped": "step-skipped"}.get(sr["status"], "step-failed")
    status_badge = {"passed": '<span class="badge badge-pass">PASSED</span>', "skipped": '<span class="badge badge-skip">SKIPPED</span>'}.get(sr["status"], '<span class="badge badge-fail">FAILED</span>')

    # Step header
    header = f"""
    <div class="step-record {status_class}">
        <div class="step-header">
            <span class="step-num">#{sr['step_num']}</span>
            <span class="step-name">{_esc(sr['step_name'])}</span>
            <span class="step-type">{_esc(sr['action_type'])}</span>
            {status_badge}
        </div>"""

    # Step value display
    step_val_str = _esc(str(sr.get("step_value", "")))
    if len(step_val_str) > 200:
        step_val_str = step_val_str[:200] + "..."

    content = f"""
        <div class="step-value"><strong>Config:</strong> <code>{step_val_str}</code></div>"""

    # Before screenshot
    if sr.get("before_screenshot"):
        content += f"""
        <details>
            <summary>Screenshot (Before Step)</summary>
            <img src="data:image/png;base64,{sr['before_screenshot']}" class="screenshot" loading="lazy">
        </details>"""

    # After screenshot
    if sr.get("after_screenshot"):
        content += f"""
        <details>
            <summary>Screenshot (After Step) {"- FAILURE" if sr["status"] == "failed" else ""}</summary>
            <img src="data:image/png;base64,{sr['after_screenshot']}" class="screenshot failure-screenshot" loading="lazy">
        </details>"""

    # DOM snapshot
    if sr.get("before_dom"):
        content += _render_dom_table(sr["before_dom"], "DOM Snapshot (Before Step)")

    # Error message
    if sr.get("error"):
        content += f"""
        <div class="error-msg"><strong>Error:</strong> <code>{_esc(sr['error'])}</code></div>"""

    # Probing results
    if sr.get("probing"):
        content += _render_probing(sr["probing"])

    content += "</div>"
    return header + content


def _render_dom_table(dom: List[Dict], title: str) -> str:
    """Render DOM snapshot as a collapsible table."""
    if not dom:
        return ""

    rows = ""
    for i, el in enumerate(dom[:50]):  # limit to 50 elements
        rows += f"""
        <tr>
            <td>{i+1}</td>
            <td><code>{_esc(el.get('tag', ''))}</code></td>
            <td>{_esc(el.get('role', ''))}</td>
            <td>{_esc(el.get('text', '')[:60])}</td>
            <td>{_esc(el.get('ariaLabel', ''))}</td>
            <td>{_esc(el.get('testid', ''))}</td>
        </tr>"""

    total = len(dom)
    truncated_note = f" (showing 50 of {total})" if total > 50 else ""

    return f"""
    <details>
        <summary>{_esc(title)} ({total} elements){truncated_note}</summary>
        <div class="dom-table-wrapper">
            <table class="data-table dom-table">
                <thead><tr><th>#</th><th>Tag</th><th>Role</th><th>Text</th><th>aria-label</th><th>data-testid</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </details>"""


def _render_probing(probes: List[Dict]) -> str:
    """Render probing results."""
    html = '<div class="probing-section"><div class="probing-title">Diagnosis Probes</div>'

    for probe in probes:
        probe_name = _esc(probe.get("probe", "Unknown probe"))
        count = probe.get("count", 0)

        if probe.get("error"):
            html += f"""
            <div class="probe-item">
                <span class="probe-name">{probe_name}</span>
                <span class="probe-error">Error: {_esc(probe['error'])}</span>
            </div>"""
        else:
            matches = probe.get("matches", [])
            html += f"""
            <div class="probe-item">
                <span class="probe-name">{probe_name}</span>
                <span class="probe-count">{count} found</span>
                <details>
                    <summary>View matches</summary>
                    <table class="data-table probe-table">
                        <thead><tr><th>#</th><th>Tag</th><th>Text</th><th>Role</th><th>aria-label</th><th>data-testid</th><th>Visible</th></tr></thead>
                        <tbody>"""

            for mi, m in enumerate(matches[:20]):
                html += f"""
                        <tr>
                            <td>{mi+1}</td>
                            <td><code>{_esc(m.get('tag', m.get('info', '')))}</code></td>
                            <td>{_esc(m.get('text', ''))[:60]}</td>
                            <td>{_esc(m.get('role', ''))}</td>
                            <td>{_esc(m.get('ariaLabel', ''))}</td>
                            <td>{_esc(m.get('testid', ''))}</td>
                            <td>{'&#9989;' if m.get('visible') else '&#10060;'}</td>
                        </tr>"""

            html += """
                    </tbody></table>
                </details>
            </div>"""

    html += "</div>"
    return html


# ---------------------------------------------------------------------------
# HTML Template Parts
# ---------------------------------------------------------------------------
_HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Error Test Case Diagnosis Report</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #1a1a2e; line-height: 1.6; }
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
h1 { text-align: center; padding: 30px 0 10px; color: #1a1a2e; font-size: 28px; }
h1 .icon { font-size: 32px; }
h2 { color: #2d3436; margin: 30px 0 15px; padding-bottom: 8px; border-bottom: 2px solid #dfe6e9; font-size: 22px; }
h3 { color: #636e72; margin: 20px 0 10px; font-size: 18px; }
.summary-section { background: #fff; border-radius: 12px; padding: 25px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.summary-stats { display: flex; gap: 20px; margin-bottom: 20px; }
.stat-card { flex: 1; text-align: center; padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; }
.stat-card .stat-number { font-size: 36px; font-weight: 700; }
.stat-card .stat-label { font-size: 13px; opacity: 0.9; margin-top: 5px; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 10px 0; }
.data-table th { background: #2d3436; color: #fff; padding: 10px 12px; text-align: left; font-weight: 600; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #eee; }
.data-table tr:hover { background: #f8f9fa; }
.meta-info { margin-top: 15px; color: #636e72; font-size: 13px; }
.case-section { background: #fff; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.case-meta { color: #636e72; font-size: 13px; margin-bottom: 15px; }
.case-meta code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.error-box { background: #fff5f5; border: 1px solid #ffcccc; border-radius: 8px; padding: 15px; margin: 15px 0; }
.error-title { font-weight: 700; color: #d63031; margin-bottom: 8px; }
.error-box pre { font-size: 12px; white-space: pre-wrap; word-break: break-all; color: #d63031; }
.step-record { border: 1px solid #dfe6e9; border-radius: 8px; margin: 10px 0; overflow: hidden; }
.step-header { display: flex; align-items: center; gap: 10px; padding: 12px 15px; background: #f8f9fa; }
.step-passed .step-header { background: #e8f8f0; }
.step-failed .step-header { background: #ffeaea; }
.step-skipped .step-header { background: #f0f0f0; }
.step-num { font-weight: 700; color: #636e72; min-width: 30px; }
.step-name { font-weight: 600; font-family: 'Consolas', monospace; }
.step-type { font-size: 11px; background: #dfe6e9; padding: 2px 8px; border-radius: 10px; color: #636e72; }
.badge { font-size: 11px; padding: 3px 10px; border-radius: 10px; font-weight: 600; }
.badge-pass { background: #00b894; color: #fff; }
.badge-fail { background: #d63031; color: #fff; }
.badge-skip { background: #b2bec3; color: #fff; }
.step-value { padding: 10px 15px; font-size: 12px; border-top: 1px solid #eee; }
.step-value code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; word-break: break-all; }
.error-msg { padding: 10px 15px; background: #fff5f5; font-size: 12px; border-top: 1px solid #ffcccc; }
.error-msg code { color: #d63031; }
.screenshot { max-width: 100%; height: auto; border: 1px solid #dfe6e9; border-radius: 6px; margin: 8px 0; cursor: zoom-in; }
.failure-screenshot { border-color: #ff7675; }
details { margin: 8px 15px; }
details summary { cursor: pointer; font-size: 13px; color: #4a90d9; padding: 4px 0; user-select: none; }
details summary:hover { text-decoration: underline; }
.dom-table-wrapper { max-height: 400px; overflow-y: auto; border: 1px solid #eee; border-radius: 6px; }
.probing-section { margin: 10px 15px; border: 1px solid #fdcb6e; border-radius: 8px; background: #fffde7; }
.probing-title { font-weight: 700; color: #e17055; padding: 10px 15px; border-bottom: 1px solid #fdcb6e; }
.probe-item { padding: 8px 15px; border-bottom: 1px solid #fef3c7; font-size: 13px; }
.probe-item:last-child { border-bottom: none; }
.probe-name { font-weight: 600; }
.probe-count { color: #0984e3; margin-left: 8px; }
.probe-error { color: #d63031; margin-left: 8px; font-size: 12px; }
.flaky-notice { padding: 15px; background: #fff9c4; border: 1px solid #f9a825; border-radius: 8px; margin: 15px 0; font-size: 14px; }
</style>
</head>
<body>
<div class="container">
<h1><span class="icon">&#128269;</span> Error Test Case Diagnosis Report</h1>
"""

_HTML_FOOTER = """
</div>
</body>
</html>"""


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Diagnose failed test cases from Allure reports by replaying them in a real browser."
    )
    parser.add_argument("--allure-dir", type=str, default=None,
                        help="Specific Allure results subdirectory name (e.g. 20260521_144342)")
    parser.add_argument("--case", type=str, default=None,
                        help="Diagnose a specific test case by name (e.g. testT1928)")
    parser.add_argument("--env", type=str, default="release",
                        help="Environment: release, staging, prod (default: release)")
    parser.add_argument("--headed", action="store_true",
                        help="Show browser window during replay")
    args = parser.parse_args()

    # Resolve allure directory
    if args.allure_dir:
        allure_dir = str(ALLURE_RESULTS_DIR / args.allure_dir)
        if not os.path.isdir(allure_dir):
            print(f"ERROR: Allure directory not found: {allure_dir}")
            sys.exit(1)
    else:
        allure_dir = find_latest_allure_dir()
        if not allure_dir:
            print("ERROR: No Allure results found. Run tests first.")
            sys.exit(1)

    print(f"Allure results directory: {allure_dir}")
    print(f"Environment: {args.env}")

    # Phase 1: Extract failed cases
    print("\n--- Phase 1: Extracting failed cases from Allure ---")
    failed_cases = extract_failed_cases(allure_dir, filter_case=args.case)

    if not failed_cases:
        if args.case:
            print(f"No failed results found for case '{args.case}' in this run.")
        else:
            print("No failed/broken test cases found in this Allure run.")
        sys.exit(0)

    print(f"Found {len(failed_cases)} failed/broken case(s):")
    for c in failed_cases:
        print(f"  - {c['name']}: {c['error_message'][:80]}")

    # Phase 2+3: Replay each case and probe failures
    base_url = resolve_base_url(args.env)
    print(f"\n--- Phase 2: Browser Replay (BASE_URL: {base_url}) ---")

    diagnosis_results = []
    for case_info in failed_cases:
        try:
            result = replay_case(case_info, base_url, args.headed)
            diagnosis_results.append(result)
        except Exception as e:
            print(f"  [FATAL] Diagnosis failed for {case_info['name']}: {e}")
            diagnosis_results.append({
                "case_name": case_info["name"],
                "yaml_path": case_info["yaml_path"],
                "allure_error": case_info["error_message"],
                "allure_trace": case_info["error_trace"],
                "failed_step": None,
                "failed_step_error": f"Diagnosis engine error: {e}",
                "step_records": [],
                "total_steps": len(case_info.get("steps_order", [])),
                "steps_passed": 0,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

    # Phase 4: Generate HTML report
    print(f"\n--- Phase 4: Generating HTML Report ---")
    report_path = generate_html_report(diagnosis_results, args.env, os.path.basename(allure_dir))
    print(f"Report generated: {report_path}")

    # Summary
    reproduced = sum(1 for r in diagnosis_results if r["failed_step"])
    flaky = len(diagnosis_results) - reproduced
    print(f"\n{'='*60}")
    print(f"  Diagnosis Complete!")
    print(f"  Total cases: {len(diagnosis_results)}")
    print(f"  Failure reproduced: {reproduced}")
    print(f"  Passed on replay (possibly flaky): {flaky}")
    print(f"  Report: {report_path}")
    print(f"{'='*60}")

    return report_path


if __name__ == "__main__":
    main()
