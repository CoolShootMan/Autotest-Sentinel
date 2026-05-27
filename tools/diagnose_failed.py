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
import difflib
import glob
import json
import os
import re
import subprocess
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
REPORT_OUTPUT_DIR = PROJECT_ROOT / "Error_Test_Case_Diagnosis_Report"
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
# Gemini AI + DOM Knowledge Base (lazy-loaded for Probe 9)
# ---------------------------------------------------------------------------
_gemini_model = None
_gemini_api_keys = []  # all available keys for fallback
_gemini_current_key_idx = 0
_gemini_model_idx = 0  # current model in fallback chain
_dom_kb_loaded = False

# Model fallback chain: preferred → fallback → lite
# Each model has independent quota; if all keys for current model fail,
# downgrade to next model.
_GEMINI_MODEL_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


def _load_gemini(force_model: str = None):
    """Lazy-load Gemini model using keys from backend/.env.

    Supports model fallback chain + multiple API key rotation:
    1. Try preferred model (gemini-2.5-flash) with key[0]
    2. On quota error → rotate to next key for same model
    3. All keys exhausted for current model → downgrade to next model
    """
    global _gemini_model, _gemini_api_keys, _gemini_current_key_idx, _gemini_model_idx
    if _gemini_model is not None and force_model is None:
        return _gemini_model
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv as _ld
        # Load keys from backend/.env
        _backend_env = os.path.join(PROJECT_ROOT, "backend", ".env")
        if os.path.exists(_backend_env):
            _ld(_backend_env, override=True)
        keys_str = os.getenv("GEMINI_API_KEYS", "")
        if not keys_str:
            return None
        keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if not keys:
            return None
        _gemini_api_keys = keys
        _gemini_current_key_idx = 0
        model_name = force_model or _GEMINI_MODEL_CHAIN[_gemini_model_idx]
        genai.configure(api_key=keys[0])
        _gemini_model = genai.GenerativeModel(model_name)
        return _gemini_model
    except Exception:
        return None


def _rotate_gemini_key():
    """Rotate to next API key for the current model.
    Returns True if rotated, False if all keys for current model exhausted.
    """
    global _gemini_model, _gemini_current_key_idx
    if len(_gemini_api_keys) <= 1:
        return False
    _gemini_current_key_idx = (_gemini_current_key_idx + 1) % len(_gemini_api_keys)
    # If we've cycled back to key 0, all keys exhausted for this model
    if _gemini_current_key_idx == 0:
        return False
    try:
        import google.generativeai as genai
        model_name = _GEMINI_MODEL_CHAIN[_gemini_model_idx]
        genai.configure(api_key=_gemini_api_keys[_gemini_current_key_idx])
        _gemini_model = genai.GenerativeModel(model_name)
        return True
    except Exception:
        return False


def _downgrade_gemini_model():
    """Downgrade to next model in the fallback chain.
    Returns True if downgraded, False if already at the last model.
    """
    global _gemini_model, _gemini_model_idx, _gemini_current_key_idx
    if _gemini_model_idx >= len(_GEMINI_MODEL_CHAIN) - 1:
        return False
    _gemini_model_idx += 1
    _gemini_current_key_idx = 0
    try:
        import google.generativeai as genai
        model_name = _GEMINI_MODEL_CHAIN[_gemini_model_idx]
        genai.configure(api_key=_gemini_api_keys[0])
        _gemini_model = genai.GenerativeModel(model_name)
        return True
    except Exception:
        return False


def _query_dom_kb(step_value: dict, url_hint: str = "", top_k: int = 5):
    """Query DOM knowledge base for similar elements. Lazy-loads dependencies."""
    global _dom_kb_loaded
    if not _dom_kb_loaded:
        try:
            tools_dir = os.path.join(PROJECT_ROOT, "tools")
            if tools_dir not in sys.path:
                sys.path.insert(0, tools_dir)
            from dom_kb import query_for_failed_step, add_elements
            import tools.dom_kb as _dk
            _query_dom_kb._fn = _dk.query_for_failed_step
            _query_dom_kb._add_fn = _dk.add_elements
        except Exception:
            _query_dom_kb._fn = None
            _query_dom_kb._add_fn = None
        _dom_kb_loaded = True
    fn = getattr(_query_dom_kb, "_fn", None)
    if fn:
        return fn(step_value, url_hint=url_hint, top_k=top_k)
    return []


def _add_dom_to_kb(dom_elements: list, url_hint: str = ""):
    """Add DOM elements to knowledge base incrementally. Silent on failure."""
    global _dom_kb_loaded
    if not _dom_kb_loaded:
        # Trigger lazy-load
        _query_dom_kb({})
    add_fn = getattr(_query_dom_kb, "_add_fn", None)
    if add_fn:
        try:
            add_fn(dom_elements, url_template=url_hint)
        except Exception:
            pass  # Silent: KB update is best-effort


def probe_ai_rag_suggestion(step_value: dict, url_hint: str = "",
                            dom_snapshot: list = None, error_msg: str = "") -> Optional[dict]:
    """Probe 9: AI RAG Suggestion.

    1. Query DOM KB for top-K similar elements via vector search
    2. Send candidates + context to Gemini
    3. Gemini picks the best match and generates a YAML locator fix
    4. Returns a probe dict with heuristic_suggestion, or None if unavailable
    """
    # Query DOM KB
    candidates = _query_dom_kb(step_value, url_hint=url_hint, top_k=5)
    if not candidates:
        return None

    # Filter out low-quality candidates before sending to Gemini
    def _is_quality_candidate(c):
        el = c["element"]
        score = c.get("score", 0)
        text = el.get("text", "")
        role = el.get("role", "")
        # Skip container elements
        if role in ("dialog", "alertdialog", "presentation", "none"):
            return False
        # Skip elements with garbage text (e.g. "Short answer name=")
        if "name=" in text and len(text) < 30:
            return False
        # Skip very low score
        if score < 0.35:
            return False
        # Skip elements whose text is just a concatenation of labels (common in form dialogs)
        if text.count(" ") > 8 and any(x in text.lower() for x in ("short", "long", "email", "phone", "paragraph")):
            return False
        return True

    filtered_candidates = [c for c in candidates if _is_quality_candidate(c)]
    if not filtered_candidates:
        return None

    # Build candidate descriptions for the prompt
    candidate_descs = []
    for i, c in enumerate(filtered_candidates):
        el = c["element"]
        score = c["score"]
        candidate_descs.append(
            f"  [{i+1}] score={score:.3f} | page={c.get('url_template','')} | "
            f"tag={el.get('tag','')} role={el.get('role','')} "
            f"testid={el.get('testid','')} ariaLabel={el.get('ariaLabel','')} "
            f"text={el.get('text','')} name={el.get('name','')}"
        )

    # Build the original step description
    if isinstance(step_value, dict):
        orig_desc = ", ".join(f"{k}={v}" for k, v in step_value.items() if v)
    else:
        orig_desc = str(step_value)

    prompt = f"""You are a QA automation expert. A UI test step FAILED because the element locator is outdated.

FAILED STEP LOCATOR:
  {orig_desc}

ERROR MESSAGE:
  {error_msg[:300] if error_msg else 'N/A'}

The DOM Knowledge Base found these similar elements on the CURRENT page:

{chr(10).join(candidate_descs)}

Your task: Pick the BEST matching element and generate a YAML locator fix.

CRITICAL RULES:
1. Pick the element that is SEMANTICALLY the same as the original (text may have changed slightly)
2. Prefer: test_id > role+name > role+ariaLabel > locator
3. If the element changed (e.g. button text changed from "Edit post" to "Edit content"), that's expected — pick the replacement
4. The "text" field in the candidates above is the element's innerText. DO NOT use it as the "name" field unless it is a SHORT, meaningful label (1-5 words). NEVER suggest values like "Short answer name=" or concatenated form labels.
5. If a candidate has role="combobox" or role="textbox", it is likely a form INPUT field, NOT a button or link. Do NOT pick input fields unless the original step was also an input field.
6. If no good match exists, return {{"reason": "brief explanation of why no match found"}}
7. Return ONLY a valid JSON object with the new locator fields, e.g. {{"role": "button", "name": "Edit content"}}
8. EVIDENCE-BASED name change: Only suggest a new "name" value if the candidate's text/aria-label EXPLICITLY provides it. If the candidate's name matches or is consistent with the original step's name, keep the ORIGINAL name. Do NOT invent or guess a name. Example: original step has name="Choose date", candidate has aria-label="Choose date" → keep name="Choose date", only change role if needed.

Respond with JSON only, no markdown:."""

    model = _load_gemini()
    if model is None:
        return None

    # Retry strategy: rotate keys first, then downgrade model
    last_error = None
    while True:
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
            result = json.loads(raw)

            # Check if AI gave a reason instead of a fix
            if "reason" in result and len(result) == 1:
                return {
                    "probe": "AI RAG Analysis (no match found)",
                    "count": 0,
                    "matches": [],
                    "ai_reason": result["reason"],
                    "score": 0.0,
                }

            # Build the suggestion
            suggested_fix = {}
            for k in ("test_id", "role", "name", "text", "label", "placeholder", "locator"):
                if k in result and result[k]:
                    suggested_fix[k] = result[k]

            if not suggested_fix:
                return None

            # Get the matched element from filtered candidates for display
            best_match = filtered_candidates[0]["element"] if filtered_candidates else {}
            return {
                "probe": "AI RAG Suggestion (Gemini + DOM Knowledge Base)",
                "count": 1,
                "matches": [best_match],
                "heuristic_suggestion": suggested_fix,
                "score": 0.85,
                "ai_candidates": candidate_descs,
            }
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            if "quota" in err_str or "429" in err_str or "resource_exhausted" in err_str:
                # 1. Try next key for current model
                if _rotate_gemini_key():
                    model = _gemini_model
                    continue
                # 2. All keys exhausted → downgrade model
                if _downgrade_gemini_model():
                    model = _gemini_model
                    continue
                # 3. All models exhausted
                break
            break  # non-quota error, don't retry

    return {
        "probe": "AI RAG Suggestion",
        "error": str(last_error),
    }

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
        start_time = d.get("start", 0)

        results.append({
            "name": name,
            "status": status,
            "error_message": error_message,
            "error_trace": error_trace,
            "yaml_path": yaml_path,
            "case_data": case_data,
            "steps_order": steps_order,
            "start": start_time,
        })

    # Read yaml files to get the original order of test cases
    yaml_order_map = {}
    yaml_first_start = {}
    for r in results:
        ypath = r.get("yaml_path")
        st = r.get("start", 0)
        if ypath:
            if ypath not in yaml_first_start or st < yaml_first_start[ypath]:
                yaml_first_start[ypath] = st
            if ypath not in yaml_order_map:
                abs_ypath = ypath if os.path.isabs(ypath) else str(PROJECT_ROOT / ypath)
                try:
                    with open(abs_ypath, "r", encoding="utf-8") as yf:
                        ydata = yaml.safe_load(yf)
                        if isinstance(ydata, dict):
                            yaml_order_map[ypath] = list(ydata.keys())
                except Exception:
                    pass

    def _case_order(x):
        ypath = x.get("yaml_path")
        name = x.get("name")
        idx = yaml_order_map.get(ypath, []).index(name) if ypath in yaml_order_map and name in yaml_order_map[ypath] else 9999
        return (yaml_first_start.get(ypath, 0), idx)

    # Sort results by execution start time of YAML file, then by actual YAML definition order
    results.sort(key=_case_order)

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


def _capture_post_state(page) -> Dict:
    """Lightweight post-step state snapshot for anomaly detection.

    Captures only the minimal signals needed to detect state drift:
    URL, title, modal presence, and rough DOM element count.
    Each query is designed to be fast (< 50ms) so it doesn't
    materially slow down the replay loop.
    """
    state = {"url": "", "title": "", "has_modal": False, "modal_count": 0, "dom_element_count": 0}
    try:
        state["url"] = page.url
    except Exception:
        pass
    try:
        state["title"] = page.title()
    except Exception:
        pass
    try:
        modal_sel = '[role="dialog"], .MuiDialog-root, .MuiModal-root, .MuiPopover-root'
        state["modal_count"] = page.locator(modal_sel).count()
        state["has_modal"] = state["modal_count"] > 0
    except Exception:
        pass
    try:
        state["dom_element_count"] = page.locator("body *").count()
    except Exception:
        pass
    return state


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
    last_warning_step = None   # (step_num, step_name, warning_text) of last ambiguous click
    first_anomaly_step_num = None  # Step number where first state anomaly was detected

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
        is_guest = case_data.get("guest", False)
        if is_guest:
            print("  [COOKIES] 'guest: true' detected. Running without cookies.")
        elif os.path.exists(cookie_file):
            context_args["storage_state"] = cookie_file
            print(f"  [COOKIES] Using storage_state: {cookie_file}")
        else:
            print(f"  [COOKIES] No cookie file found at: {cookie_file}")

        context = browser.new_context(**context_args)
        page = context.new_page()
        page.set_default_timeout(15000)

        # -------------------------------------------------------------
        # NEW: Network Request Monitoring
        # -------------------------------------------------------------
        failed_requests = []
        def handle_response(response):
            if response.status >= 500 or (response.status >= 400 and response.request.resource_type in ["fetch", "xhr"]):
                failed_requests.append({
                    "url": response.url,
                    "status": response.status,
                    "method": response.request.method,
                })
        
        def handle_request_failed(request):
            if request.resource_type in ["fetch", "xhr", "document"]:
                failed_requests.append({
                    "url": request.url,
                    "status": 0,
                    "method": request.method,
                    "error": request.failure.strip() if request.failure else "failed",
                })
                
        page.on("response", handle_response)
        page.on("requestfailed", handle_request_failed)
        # -------------------------------------------------------------

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
        previous_step_warning = None
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
                step_warn = _execute_step(page, step_name, step_value, actual_base_url)

                # Success
                after_screenshot = capture_screenshot_b64(page)
                after_dom = capture_dom_snapshot(page)
                # Incrementally add current page DOM to knowledge base
                _add_dom_to_kb(after_dom, url_hint=actual_base_url)
                print("PASSED")
                if step_warn:
                    previous_step_warning = step_warn
                    last_warning_step = (step_num, step_name, step_warn)
                    print(f"  [AMBIGUITY WARNING] Step #{step_num} '{step_name}': {step_warn}")
                elif action_type == "click":
                    # Only clear if this was a clean, unambiguous click
                    previous_step_warning = None

                step_records.append({
                    "step_num": step_num,
                    "step_name": step_name,
                    "action_type": action_type,
                    "step_value": step_value,
                    "status": "passed",
                    "warning": step_warn or "",
                    "before_screenshot": before_screenshot,
                    "after_screenshot": after_screenshot,
                    "before_dom": before_dom,
                    "after_dom": after_dom,
                    "before_summary": before_summary,
                    "post_state": _capture_post_state(page),
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
                        "warning": "",
                        "before_screenshot": before_screenshot,
                        "after_screenshot": after_screenshot,
                        "before_dom": before_dom,
                        "after_dom": after_dom,
                        "before_summary": before_summary,
                        "post_state": _capture_post_state(page),
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
                    probing_results = probe_failure(page, step_name, step_value, error_msg, after_dom)

                    # --- ROOT CAUSE PREDICTION ---
                    # Case 1: Previous click had an ambiguous match (warning was set)
                    root_cause_parts = []
                    if previous_step_warning and last_warning_step:
                        root_cause_parts.append(
                            f"Step #{last_warning_step[0]} '{last_warning_step[1]}' had an ambiguous locator match: "
                            f"{last_warning_step[2]}  →  This click may have landed on the wrong element."
                        )

                    # Case 2: Active modal/popover is blocking the target element
                    modal_probe = next((p for p in probing_results if "modal" in p.get("probe", "").lower() and p.get("count", 0) > 0), None)
                    if modal_probe:
                        modal_texts = "; ".join(m.get("text", "")[:60] for m in modal_probe.get("matches", []) if m.get("text"))
                        root_cause_parts.append(
                            f"A modal/dialog/popover is currently blocking the page "
                            f"({modal_probe['count']} found: {modal_texts or 'no text'}). "
                            f"A prior step may have accidentally triggered it."
                        )

                    # Case 3: Post-state retrospection — find first state anomaly
                    anomalies = _detect_state_anomalies(step_records, step_num)
                    if anomalies:
                        first = anomalies[0]
                        first_anomaly_step_num = first["step_num"]
                        root_cause_parts.append(
                            f"State anomaly detected at Step #{first['step_num']} "
                            f"'{first['step_name']}': {first['detail']}. "
                            f"This step caused an unexpected page state change that likely led to the current failure."
                        )

                    # Case 4: UI Change Detection — target text/aria-label exists but role changed
                    # This catches UI redesigns where an element's role was changed
                    # (e.g. textbox -> button, link -> button, etc.)
                    # Extract target info from step_value (same logic as _execute_step)
                    _target_role = step_value.get("role") if isinstance(step_value, dict) else None
                    _target_name = None
                    if isinstance(step_value, dict):
                        _target_name = step_value.get("name") or step_value.get("text") or step_value.get("label") or step_value.get("placeholder")
                    if _target_role and _target_name:
                        # Find aria-label probe that matched the target name
                        aria_probe = next((p for p in probing_results if "aria-label" in p.get("probe", "") and p.get("count", 0) > 0), None)
                        role_probe = next((p for p in probing_results if f"role='{_target_role}'" in p.get("probe", "")), None)
                        if aria_probe and role_probe:
                            # aria-label found something, but role search found 0 or different elements
                            role_count = role_probe.get("count", 0)
                            aria_matches = aria_probe.get("matches", [])
                            if role_count == 0 and aria_matches:
                                # The text exists but the expected role doesn't
                                actual_tags = list(set(m.get("tag", "") for m in aria_matches if m.get("tag")))
                                actual_roles = list(set(m.get("role", "") for m in aria_matches if m.get("role")))
                                if actual_tags or actual_roles:
                                    tag_hint = f" (actual tag: {', '.join(actual_tags)})" if actual_tags else ""
                                    role_hint = f" (actual role: {', '.join(actual_roles)})" if actual_roles else ""
                                    root_cause_parts.append(
                                        f"UI element '{_target_name}' exists but its role has changed: "
                                        f"expected role='{_target_role}' not found, "
                                        f"but element with matching aria-label was found as {tag_hint or role_hint}. "
                                        f"The page may have been redesigned — update the locator to use the new role or a CSS locator."
                                    )
                                    # --- Inject heuristic_suggestion from Case 4 findings ---
                                    best_match = aria_matches[0]
                                    suggested_fix = {}
                                    if actual_roles:
                                        suggested_fix["role"] = actual_roles[0]
                                    elif actual_tags:
                                        suggested_fix["tag"] = actual_tags[0]
                                    suggested_fix["name"] = _target_name
                                    probing_results.append({
                                        "probe": "UI Change Detection (role mismatch)",
                                        "count": len(aria_matches),
                                        "matches": aria_matches,
                                        "heuristic_suggestion": suggested_fix,
                                        "score": 0.95,
                                        "reason": f"Element '{_target_name}' found with role='{actual_roles[0] if actual_roles else 'unknown'}', expected role='{_target_role}'",
                                    })

                    if root_cause_parts:
                        error_msg += "\n\n[ROOT CAUSE PREDICTION]: " + "  |  ".join(root_cause_parts) + "\nPrevious step may have caused an unexpected page state change."
                        failed_step_error = error_msg

                step_records.append({
                    "step_num": step_num,
                    "step_name": step_name,
                    "action_type": action_type,
                    "step_value": step_value,
                    "status": "failed",
                    "warning": "",
                    "before_screenshot": before_screenshot,
                    "after_screenshot": after_screenshot,
                    "before_dom": before_dom,
                    "after_dom": after_dom,
                    "before_summary": before_summary,
                    "post_state": _capture_post_state(page),
                    "error": error_msg,
                    "probing": probing_results if failure_found and step_name == failed_step_name else [],
                    "anomaly_step_num": first_anomaly_step_num,
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
        "failed_requests": failed_requests,
        "total_steps": len(steps_order),
        "steps_passed": sum(1 for s in step_records if s["status"] == "passed"),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "anomaly_step_nums": [a["step_num"] for a in anomalies] if failure_found and anomalies else [],
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
        return _execute_click_step(page, step_name, step_value)

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
        return _execute_click_step(page, step_name, step_value)

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

    warning = None  # Track ambiguous matches across ALL strategies

    # Skip if no actionable targets
    if not target_name and not target_locator and not target_role and not target_test_id:
        return

    # 1. Test ID
    if target_test_id:
        try:
            el = page.get_by_test_id(target_test_id).nth(target_index)
            if el.is_visible(timeout=3000):
                el.click(force=force)
                return warning
        except Exception:
            if optional:
                return

    # 2. Locator (CSS or XPath)
    if target_locator:
        try:
            if target_locator.startswith("/") or target_locator.startswith("xpath="):
                xpath_loc = target_locator if target_locator.startswith("xpath=") else f"xpath={target_locator}"
                loc_base = page.locator(xpath_loc)
            else:
                loc_base = page.locator(target_locator)

            # If both locator + text/role, try combining
            if target_name:
                try:
                    loc_base = loc_base.get_by_text(target_name, exact=exact)
                except Exception:
                    pass

            # Ambiguity check for locator strategy
            try:
                loc_base.first.wait_for(state="attached", timeout=5000)
                count = loc_base.count()
                if count > 1 and target_name:
                    warning = f"Ambiguous locator+name matched {count} elements (locator='{target_locator}', name='{target_name}')."
            except Exception:
                pass

            el = loc_base.nth(target_index)
            el.click(force=force, timeout=5000)
            page.wait_for_timeout(300)
            return warning
        except Exception as e:
            if optional:
                return

    # 3. Aria-label fallback
    if target_name:
        try:
            loc_base = page.locator(f'[aria-label="{target_name}"], [aria-label*="{target_name}"]')
            # Ambiguity check for aria-label strategy
            try:
                loc_base.first.wait_for(state="attached", timeout=3000)
                count = loc_base.count()
                if count > 1:
                    warning = f"Ambiguous aria-label matched {count} elements for name='{target_name}' (substring match on aria-label)."
            except Exception:
                pass

            el = loc_base.nth(target_index)
            el.click(force=force, timeout=3000)
            page.wait_for_timeout(300)
            return warning
        except Exception:
            pass

    # 4. Role / text
    try:
        if target_role:
            el_base = page.get_by_role(role=target_role, name=target_name, exact=exact)
        elif target_name:
            el_base = page.get_by_text(target_name, exact=exact)
        else:
            raise Exception("No locator strategy matched")

        try:
            el_base.first.wait_for(state="attached", timeout=5000)
            count = el_base.count()
            if count > 1:
                warning = f"Ambiguous locator matched {count} elements (e.g. role={target_role}, name='{target_name}')."
        except Exception:
            pass

        el = el_base.nth(target_index)
        el.click(timeout=5000)
        page.wait_for_timeout(300)
        if target_role == "option":
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
        return warning
    except Exception:
        try:
            el.click(force=True, timeout=3000)
            page.wait_for_timeout(300)
            return warning
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


def _detect_state_anomalies(step_records: List[Dict], failed_step_num: int) -> List[Dict]:
    """Retrospect step post-states to find the first state anomaly.

    Scans step_records[0 .. failed_step_num-1] looking for signals that
    indicate a step caused an unexpected page state change. Returns a
    list of anomaly dicts sorted by step_num (earliest first).

    Anomaly types:
      A — Unexpected URL change on a non-navigation step
      B — Modal appeared after a step and persisted through subsequent steps
      C — Page DOM element count dropped > 50% (major restructure/navigate)
    """
    from urllib.parse import urlparse

    anomalies = []

    # Action types that are passive (don't actively change page state).
    # URL/modal changes during these steps are side effects of prior actions,
    # not caused by the current step itself.
    PASSIVE_ACTIONS = {"sleep", "screenshot", "assert", "assertion"}

    for i in range(len(step_records)):
        sr = step_records[i]
        post = sr.get("post_state")
        if not post or not post.get("url"):
            continue

        step_num = sr["step_num"]
        action_type = sr.get("action_type", "")

        # Skip anomaly detection for passive actions entirely.
        # Sleep/screenshot/assert don't cause state changes; any URL/modal
        # shift during these steps is a delayed effect of prior steps.
        if action_type in PASSIVE_ACTIONS:
            continue

        # --- Anomaly A: Unexpected URL change ---
        # Compare with previous step's post_state URL
        if i > 0:
            prev_post = step_records[i - 1].get("post_state")
            if prev_post and prev_post.get("url"):
                prev_url = prev_post["url"]
                curr_url = post["url"]

                if curr_url != prev_url:
                    # Ignore hash/fragment-only changes
                    prev_path = urlparse(prev_url).path
                    curr_path = urlparse(curr_url).path
                    if prev_path != curr_path:
                        # Only flag if this step isn't supposed to navigate
                        nav_types = {"open", "navigation", "reload", "modal"}
                        if action_type not in nav_types:
                            anomalies.append({
                                "step_num": step_num,
                                "step_name": sr["step_name"],
                                "anomaly_type": "unexpected_navigation",
                                "detail": (
                                    f"URL changed from {prev_path} to {curr_path} "
                                    f"after a '{action_type}' action (expected no navigation)"
                                ),
                                "prev_url": prev_url,
                                "curr_url": curr_url,
                            })

        # --- Anomaly C: DOM element count dropped > 50% ---
        if i > 0:
            prev_post = step_records[i - 1].get("post_state")
            if prev_post and prev_post.get("dom_element_count") > 20:
                prev_count = prev_post["dom_element_count"]
                curr_count = post.get("dom_element_count", 0)
                if curr_count > 0 and (prev_count - curr_count) / prev_count > 0.5:
                    anomalies.append({
                        "step_num": step_num,
                        "step_name": sr["step_name"],
                        "anomaly_type": "dom_restructure",
                        "detail": (
                            f"Page element count dropped {prev_count} -> {curr_count} "
                            f"({round((prev_count - curr_count) / prev_count * 100)}% decrease), "
                            f"indicating a major page restructure"
                        ),
                    })

    # --- Anomaly B: Modal appeared and persisted ---
    # Find the first step where has_modal became True
    modal_appeared_step = None
    for i in range(len(step_records)):
        post = step_records[i].get("post_state")
        if not post:
            continue
        if post.get("has_modal"):
            # Check if this is the first appearance
            if i == 0 or not step_records[i - 1].get("post_state", {}).get("has_modal"):
                modal_appeared_step = step_records[i]
                break

    # If a modal appeared and persisted to the failed step, it's suspicious
    if modal_appeared_step:
        # Skip if the step that first showed the modal is a passive action
        # (the modal was actually triggered by a prior step, not this one)
        if modal_appeared_step.get("action_type", "") not in PASSIVE_ACTIONS:
            # Check that the modal persisted through at least one subsequent step
            modal_idx = None
            for idx, sr in enumerate(step_records):
                if sr["step_num"] == modal_appeared_step["step_num"]:
                    modal_idx = idx
                    break
            if modal_idx is not None:
                persisted = False
                for j in range(modal_idx + 1, len(step_records)):
                    later_post = step_records[j].get("post_state")
                    if later_post and not later_post.get("has_modal"):
                        break  # Modal was dismissed, not a problem
                    if j == len(step_records) - 1 or step_records[j]["step_num"] >= failed_step_num:
                        persisted = True
                        break
                if persisted and modal_appeared_step.get("action_type") != "modal":
                    # Don't double-report if it's already caught by Anomaly A or existing modal probe
                    already_reported = any(
                        a["step_num"] == modal_appeared_step["step_num"]
                        for a in anomalies
                    )
                    if not already_reported:
                        modal_count = modal_appeared_step.get("post_state", {}).get("modal_count", 1)
                        anomalies.append({
                            "step_num": modal_appeared_step["step_num"],
                            "step_name": modal_appeared_step["step_name"],
                            "anomaly_type": "modal_persisted",
                            "detail": (
                                f"A modal/dialog appeared ({modal_count} found) and persisted "
                                f"through subsequent steps without being dismissed"
                            ),
                        })

    # Sort by step_num ascending (earliest anomaly first)
    anomalies.sort(key=lambda a: a["step_num"])
    return anomalies


# ===========================================================================
# Phase 3: Multi-strategy failure probing
# ===========================================================================

def probe_failure(page, step_name: str, step_value: dict, error_msg: str, dom_snapshot: list = None) -> List[Dict]:
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
            for el in elements[:15]:
                try:
                    tag = el.evaluate("e => e.tagName.toLowerCase()")
                    text = el.evaluate("e => (e.innerText || '').trim().substring(0, 100)")
                    role = el.get_attribute("role") or ""
                    aria = el.get_attribute("aria-label") or ""
                    testid = el.get_attribute("data-testid") or ""
                    visible = el.is_visible()
                    # Compute precision score: shorter text + has role/testid = more precise element
                    text_len = len(text)
                    precision = text_len if text_len > 0 else 9999
                    matches.append({
                        "tag": tag, "text": text, "role": role,
                        "ariaLabel": aria, "testid": testid, "visible": visible,
                        "_precision": precision,
                    })
                except Exception:
                    pass
            # Sort by precision: shortest text first (most specific element)
            # Elements with role or testid get a boost (more likely to be interactive)
            for m in matches:
                if m.get("role"):
                    m["_precision"] -= 500
                if m.get("testid"):
                    m["_precision"] -= 300
                if m.get("ariaLabel"):
                    m["_precision"] -= 200
            matches.sort(key=lambda x: x["_precision"])
            probes.append({
                "probe": f"Elements containing text '{target_name}'",
                "count": len(elements),
                "matches": matches[:10],
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

    # Probe 7: Heuristic Similarity Matching (NEW)
    if dom_snapshot:
        try:
            best_match = None
            best_score = 0.0
            
            for el in dom_snapshot:
                score = 0.0
                if target_role and el.get("role") == target_role:
                    score += 0.3
                if target_test_id and target_test_id in el.get("testid", ""):
                    score += 0.25
                text_to_match = el.get("text", "") or el.get("ariaLabel", "") or el.get("placeholder", "")
                if target_name and text_to_match:
                    sim = difflib.SequenceMatcher(None, str(target_name).lower(), text_to_match.lower()).ratio()
                    score += 0.45 * sim
                
                if score > best_score:
                    best_score = score
                    best_match = el
            
            # Lower threshold: 0.25 for low-confidence, 0.4 for confident
            if best_match and best_score >= 0.25:
                # Format a suggested fix
                suggested_fix = {}
                if best_match.get("testid"):
                    suggested_fix["test_id"] = best_match["testid"]
                elif best_match.get("role"):
                    suggested_fix["role"] = best_match["role"]
                    # Prefer ariaLabel over text (innerText can be very long with newlines)
                    if best_match.get("ariaLabel"):
                        suggested_fix["name"] = best_match["ariaLabel"]
                    elif best_match.get("text"):
                        # Clean up innerText: collapse whitespace, limit length
                        clean_text = " ".join(best_match["text"].split())[:60]
                        suggested_fix["name"] = clean_text
                else:
                    # Fallback to locator
                    if best_match.get("text"):
                        clean_text = " ".join(best_match["text"].split())[:60]
                        suggested_fix["text"] = clean_text

                if suggested_fix:
                    confidence = "high" if best_score >= 0.4 else "medium"
                    probes.append({
                        "probe": f"Heuristic Similarity Suggestion ({confidence} confidence)",
                        "count": 1,
                        "matches": [best_match],
                        "heuristic_suggestion": suggested_fix,
                        "score": best_score,
                    })
                else:
                    # Found a structural match but no usable attributes — warn instead of silence
                    probes.append({
                        "probe": "Heuristic Similarity (match found, insufficient attributes for suggestion)",
                        "count": 1,
                        "matches": [best_match],
                        "score": best_score,
                        "warning": "Element found but has no role/testid/ariaLabel/text — cannot auto-generate locator. Manual inspection required.",
                    })
            elif best_match and best_score > 0 and target_name:
                # Best match exists but score is very low — still provide a hint
                probes.append({
                    "probe": "Heuristic Similarity (low match, no suggestion)",
                    "count": 1,
                    "matches": [best_match],
                    "score": best_score,
                    "warning": f"Best match score {best_score:.2f} is too low for a confident suggestion. Check DOM manually.",
                })
        except Exception as e:
            probes.append({"probe": "Heuristic Similarity Suggestion", "error": str(e)})

    # Probe 8: Fallback suggestion from Probe 1 text matches
    # If no heuristic suggestion was generated above, but Probe 1 found visible
    # elements containing the target text, generate a direct suggestion from those.
    has_heuristic = any("heuristic_suggestion" in p for p in probes)
    if not has_heuristic and target_name:
        text_probe = next((p for p in probes if "containing" in p.get("probe", "") and "target" in p.get("probe", "").lower() and p.get("count", 0) > 0), None)
        # Also try matching the Probe 1 format: "Elements containing 'xxx'"
        if not text_probe:
            text_probe = next(
                (p for p in probes if p.get("probe", "").startswith("Elements containing") and p.get("count", 0) > 0),
                None
            )
        if text_probe:
            # Probe 1 already sorts by precision (shortest text first).
            # Pick the first visible, non-container match.
            _CONTAINER_TAGS = {"html", "body", "main"}
            visible_matches = [
                m for m in text_probe.get("matches", [])
                if m.get("visible") and m.get("tag", "").lower() not in _CONTAINER_TAGS
            ]
            if visible_matches:
                best = visible_matches[0]
                suggested_fix = {}
                # Build the best possible locator from available attributes
                if best.get("testid"):
                    suggested_fix["test_id"] = best["testid"]
                if best.get("role"):
                    suggested_fix["role"] = best["role"]
                # For name: prefer ariaLabel > short clean text
                if best.get("ariaLabel"):
                    suggested_fix["name"] = best["ariaLabel"]
                elif best.get("text"):
                    clean_text = " ".join(best["text"].split())
                    if len(clean_text) <= 80:
                        suggested_fix["name"] = clean_text
                if suggested_fix:
                    probes.append({
                        "probe": "Fallback Suggestion (from visible text match)",
                        "count": 1,
                        "matches": [best],
                        "heuristic_suggestion": suggested_fix,
                        "score": 0.3,
                    })

    # Probe 9: AI RAG Suggestion (Gemini + DOM Knowledge Base)
    # Uses vector search + LLM to find the best replacement locator.
    # Kept separate from rule-based probes (7/8) which are preserved for comparison.
    ai_probe = probe_ai_rag_suggestion(
        step_value=step_value,
        url_hint="",  # TODO: pass URL from step context if available
        dom_snapshot=dom_snapshot,
        error_msg=error_msg,
    )
    if ai_probe:
        probes.append(ai_probe)

    return probes
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

def generate_html_report(diagnosis_results: List[Dict], env: str, allure_dir: str, start_time: datetime.datetime = None, end_time: datetime.datetime = None) -> str:
    """Generate a standalone HTML diagnosis report. Returns the file path."""
    REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = str(REPORT_OUTPUT_DIR / f"Error_Test_Case_Diagnosis_Report_{timestamp}.html")

    # Build HTML
    html_parts = [_HTML_HEAD]
    html_parts.append(_render_summary(diagnosis_results, env, allure_dir, start_time, end_time))

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


def _render_summary(results: List[Dict], env: str, allure_dir: str, start_time: datetime.datetime = None, end_time: datetime.datetime = None) -> str:
    """Render the summary dashboard section."""
    total = len(results)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build time range display like Allure: "13:48:54 - 14:12:02 (23m 08s)"
    time_range_html = ""
    if start_time and end_time:
        duration = end_time - start_time
        total_seconds = int(duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        duration_str = f"{minutes}m {seconds:02d}s" if minutes > 0 else f"{seconds}s"
        start_str = start_time.strftime("%H:%M:%S")
        end_str = end_time.strftime("%H:%M:%S")
        date_str = start_time.strftime("%Y/%m/%d")
        time_range_html = f"""
        <div style="font-size:15px;color:#555;margin-bottom:15px;">
            <span style="font-weight:bold;color:#333;">{date_str}</span>
            <span style="color:#888;">{start_str} - {end_str} ({duration_str})</span>
        </div>"""

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
        {time_range_html}
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

    # Network Failures
    network_section = ""
    if result.get("failed_requests"):
        rows = ""
        for req in result["failed_requests"]:
            status = req.get("status")
            badge_cls = "badge-fail" if status >= 500 else "badge-warn"
            badge = f'<span class="badge {badge_cls}">{status}</span>' if status else f'<span class="badge badge-fail">FAILED</span>'
            rows += f"<tr><td>{badge}</td><td>{_esc(req.get('method', ''))}</td><td>{_esc(req.get('url', ''))}</td><td>{_esc(req.get('error', ''))}</td></tr>"
        
        network_section = f"""
        <div class="network-box">
            <div class="network-title">&#9888; Network Request Failures Detected</div>
            <table class="data-table">
                <thead><tr><th>Status</th><th>Method</th><th>URL</th><th>Error</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
            <p style="font-size: 12px; margin-top: 5px; color: #666;">These backend or network errors might be the root cause of the UI failure.</p>
        </div>
        """

    # Step-by-step replay
    anomaly_steps = set(result.get("anomaly_step_nums", []))
    steps_html = ""
    for sr in result["step_records"]:
        steps_html += _render_step_record(sr, anomaly_steps)

    # If no failure found during replay
    if not result["failed_step"] and not any(s["status"] == "failed" for s in result["step_records"]):
        steps_html += f"""
        <div class="flaky-notice">
            All steps passed during replay. This may be a flaky test or a timing issue.
            The original Allure error was: <code>{_esc(result['allure_error'][:200])}</code>
        </div>"""

    # --- Fix Suggestions (from heuristic probe) ---
    suggestions_html = ""
    fix_suggestions = []
    if result.get("failed_step"):
        for sr in result.get("step_records", []):
            if sr.get("step_name") == result["failed_step"]:
                # Collect ALL heuristic suggestions (rule-based + AI), show all
                all_suggestions = []
                for p in sr.get("probing", []):
                    if "heuristic_suggestion" in p:
                        all_suggestions.append({
                            "step_name": sr["step_name"],
                            "suggestion": p["heuristic_suggestion"],
                            "probe": p.get("probe", ""),
                            "score": p.get("score", 0),
                            "reason": p.get("reason", ""),
                            "ai_candidates": p.get("ai_candidates", []),
                        })
                # Sort by score descending, but keep ALL suggestions
                if all_suggestions:
                    all_suggestions.sort(key=lambda x: x.get("score", 0), reverse=True)
                    fix_suggestions.extend(all_suggestions)
    if fix_suggestions:
        sugg_cards = ""
        for fix in fix_suggestions:
            sugg = fix["suggestion"]
            score = fix.get("score", 0)
            # Confidence badge color
            if score >= 0.7:
                conf_color = "#2e7d32"
                conf_label = "High"
            elif score >= 0.4:
                conf_color = "#e65100"
                conf_label = "Medium"
            else:
                conf_color = "#6a1b9a"
                conf_label = "Low"

            yaml_preview = "<br>".join(
                f"<code style='background:#f5f5f5;padding:2px 6px;border-radius:3px;'>{_esc(k)}</code>: {_esc(str(v))}"
                for k, v in sugg.items()
            )
            # Build original vs suggested comparison
            orig_step_value = None
            for sr2 in result.get("step_records", []):
                if sr2.get("step_name") == fix["step_name"]:
                    orig_step_value = sr2.get("step_value")
                    break
            orig_preview = ""
            if isinstance(orig_step_value, dict):
                orig_lines = []
                for k in ("role", "name", "text", "label", "test_id", "locator"):
                    if k in orig_step_value:
                        orig_lines.append(
                            f"<code style='background:#ffebee;padding:2px 6px;border-radius:3px;text-decoration:line-through;'>{_esc(k)}</code>: {_esc(str(orig_step_value[k]))}"
                        )
                if orig_lines:
                    orig_preview = (
                        "<div style='margin:8px 0 4px;font-size:12px;color:#888;'>Original (in YAML):</div>"
                        + "<br>".join(orig_lines)
                    )

            reason_html = ""
            if fix.get("reason"):
                reason_html = f"<div style='margin-top:6px;font-size:12px;color:#666;font-style:italic;'>{_esc(fix['reason'])}</div>"

            # Style differently for AI vs rule-based suggestions
            is_ai = "AI RAG" in fix.get("probe", "")
            if is_ai:
                card_bg = "#e3f2fd"
                card_border = "#90caf9"
                title_icon = "&#x1F916;"
                source_badge = '<span style="background:#1565c0;color:#fff;font-size:10px;padding:2px 6px;border-radius:10px;margin-left:6px;">Gemini + RAG</span>'
                # Collapsible RAG candidates detail
                ai_candidates_html = ""
                if fix.get("ai_candidates"):
                    cand_items = "<br>".join(f"<div style='font-size:11px;color:#555;padding:2px 0;border-bottom:1px solid #e0e0e0;'>{_esc(c)}</div>" for c in fix["ai_candidates"])
                    _uid = id(fix)  # unique id for toggle
                    ai_candidates_html = f"""
                    <div style="margin-top:8px;">
                        <button onclick="var d=document.getElementById('rag-candidates-{_uid}');d.style.display=d.style.display==='none'?'block':'none';this.innerHTML=d.style.display==='none'?'&#9660; View all RAG candidates ({len(fix['ai_candidates'])})':'&#9650; Hide RAG candidates';" style="background:#bbdefb;color:#1565c0;border:1px solid #90caf9;border-radius:4px;padding:3px 10px;cursor:pointer;font-size:11px;">&#9660; View all RAG candidates ({len(fix['ai_candidates'])})</button>
                        <div id="rag-candidates-{_uid}" style="display:none;margin-top:6px;padding:8px;background:#fff;border:1px solid #e0e0e0;border-radius:4px;max-height:200px;overflow-y:auto;">
                            {cand_items}
                        </div>
                    </div>"""
            else:
                card_bg = "#f1f8e9"
                card_border = "#a5d6a7"
                title_icon = "&#x1F4A1;"
                source_badge = ""
                ai_candidates_html = ""

            sugg_cards += f"""
            <div class="suggestion-card" style="margin-bottom:12px;padding:14px;background:{card_bg};border:1px solid {card_border};border-radius:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <div style="font-weight:bold;color:#1565c0;">{title_icon} Suggested Fix for Step '{_esc(fix['step_name'])}'{source_badge}</div>
                    <span style="background:{conf_color};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:bold;">{conf_label} Confidence ({score:.0%})</span>
                </div>
                {orig_preview}
                <div style='margin:8px 0 4px;font-size:12px;color:#888;'>Suggested change:</div>
                <div style="font-size:13px;color:#444;line-height:1.8;">{yaml_preview}</div>
                {reason_html}
                {ai_candidates_html}
            </div>"""
        suggestions_html = f"""
        <div style="margin: 15px 0;">
            <div style="font-weight:bold;color:#2e7d32;font-size:14px;margin-bottom:8px;">&#x1F4A1; Auto-Fix Suggestions</div>
            {sugg_cards}
        </div>"""

    return f"""
    <div class="case-section" id="{case_id}">
        <h2>Case: {_esc(result['case_name'])}</h2>
        <div class="case-meta">
            YAML: <code>{_esc(result['yaml_path'])}</code><br>
            Timestamp: {_esc(result['timestamp'])}
        </div>
        {suggestions_html}
        {network_section}
        {error_section}
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 20px 0 10px;">
            <h3 style="margin: 0;">Step-by-Step Replay</h3>
            <button onclick="const content = this.parentElement.nextElementSibling; if (content.style.display === 'none') {{ content.style.display = 'block'; this.innerHTML = 'Collapse &#x25B2;'; }} else {{ content.style.display = 'none'; this.innerHTML = 'Expand &#x25BC;'; }}" style="background: #e3f2fd; color: #1e88e5; border: 1px solid #90caf9; border-radius: 4px; padding: 6px 12px; cursor: pointer; font-size: 13px; font-weight: bold; transition: background 0.2s;">Collapse &#x25B2;</button>
        </div>
        <div class="steps-container" style="display:block;">{steps_html}</div>
    </div>"""


def _render_step_record(sr: Dict, anomaly_steps: set = None) -> str:
    """Render a single step record."""
    if anomaly_steps is None:
        anomaly_steps = set()

    has_warning = bool(sr.get("warning"))
    is_anomaly = sr["step_num"] in anomaly_steps and sr["status"] == "passed"
    status_class = {"passed": "step-passed", "skipped": "step-skipped"}.get(sr["status"], "step-failed")
    if has_warning and sr["status"] == "passed":
        status_class = "step-warning"  # amber highlight for ambiguous-click steps
    if is_anomaly:
        status_class = "step-anomaly"  # amber highlight for state anomaly steps

    status_badge_map = {
        "passed": '<span class="badge badge-pass">PASSED</span>',
        "skipped": '<span class="badge badge-skip">SKIPPED</span>',
    }
    status_badge = status_badge_map.get(sr["status"], '<span class="badge badge-fail">FAILED</span>')
    if has_warning and sr["status"] == "passed":
        status_badge = '<span class="badge badge-pass">PASSED</span> <span class="badge badge-warn">⚠️ AMBIGUOUS</span>'
    if is_anomaly:
        status_badge = '<span class="badge badge-pass">PASSED</span> <span class="badge badge-anomaly">⚠️ STATE ANOMALY</span>'

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

    # Ambiguous locator warning box (for PASSED steps that had multiple matches)
    if has_warning:
        content += f"""
        <div style="background:#fff8e1; border:2px solid #ffc107; border-radius:8px; padding:10px 14px; margin:8px 15px;">
            <strong style="color:#e65100; font-size:13px;">⚠️ AMBIGUOUS LOCATOR WARNING</strong><br>
            <span style="color:#664d03; font-size:12px;">{_esc(sr['warning'])}</span>
        </div>"""

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

    # State anomaly info box (for PASSED steps flagged by retrospection)
    if is_anomaly and sr.get("post_state"):
        ps = sr["post_state"]
        anomaly_detail = ""
        if ps.get("url"):
            anomaly_detail += f"<strong>URL:</strong> <code>{_esc(ps['url'])}</code><br>"
        if ps.get("has_modal"):
            anomaly_detail += f"<strong>Modal detected:</strong> {ps['modal_count']} dialog(s) present<br>"
        if ps.get("dom_element_count"):
            anomaly_detail += f"<strong>DOM elements:</strong> {ps['dom_element_count']}"
        content += f"""
        <div style="background:#fff8e1; border:2px solid #ffc107; border-radius:8px; padding:10px 14px; margin:8px 15px;">
            <strong style="color:#e65100; font-size:13px;">⚠️ STATE ANOMALY DETECTED</strong><br>
            <span style="color:#664d03; font-size:12px;">This step caused an unexpected page state change that likely led to the failure.</span><br>
            <div style="margin-top:6px; font-size:12px; color:#555;">{anomaly_detail}</div>
        </div>"""

    # Post-state snapshot (collapsible, for every step that has it)
    if sr.get("post_state"):
        ps = sr["post_state"]
        state_lines = []
        if ps.get("url"):
            state_lines.append(f"URL: {ps['url']}")
        if ps.get("title"):
            state_lines.append(f"Title: {ps['title']}")
        state_lines.append(f"Modal: {'Yes (' + str(ps['modal_count']) + ')' if ps.get('has_modal') else 'No'}")
        if ps.get("dom_element_count"):
            state_lines.append(f"DOM elements: {ps['dom_element_count']}")
        state_text = "<br>".join(_esc(l) for l in state_lines)
        content += f"""
        <details style="margin:4px 15px;">
            <summary style="font-size:12px; color:#888; cursor:pointer;">Page State (After Step)</summary>
            <div style="background:#fafafa; border:1px solid #eee; border-radius:6px; padding:8px 12px; margin-top:4px; font-size:12px; color:#666; font-family:monospace;">{state_text}</div>
        </details>"""

    # DOM snapshot
    if sr.get("before_dom"):
        content += _render_dom_table(sr["before_dom"], "DOM Snapshot (Before Step)")

    # Error message
    if sr.get("error"):
        error_text = sr['error']
        root_cause_html = ""
        if "[ROOT CAUSE PREDICTION]" in error_text:
            parts = error_text.split("[ROOT CAUSE PREDICTION]:", 1)
            error_text = parts[0].strip()
            if len(parts) > 1:
                prediction_text = parts[1].strip()
                root_cause_html = f"""
        <div style="background:#fff3cd; border:2px solid #ffc107; border-radius:8px; padding:12px 16px; margin:8px 0;">
            <strong style="color:#856404; font-size:14px;">⚠️ ROOT CAUSE PREDICTION</strong><br>
            <span style="color:#664d03; font-size:13px; white-space:pre-wrap;">{_esc(prediction_text)}</span>
        </div>"""
        content += f"""
        <div class="error-msg"><strong>Error:</strong> <code>{_esc(error_text)}</code></div>{root_cause_html}"""

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
        elif probe.get("ai_reason"):
            html += f"""
            <div class="probe-item" style="border:1px solid #e3f2fd;border-radius:8px;padding:10px 14px;">
                <span class="probe-name">&#129302; {probe_name}</span>
                <div style="font-size:12px;color:#1565c0;margin-top:6px;"><strong>AI Analysis:</strong> {_esc(probe['ai_reason'])}</div>
            </div>"""
        elif "heuristic_suggestion" in probe:
            sugg = probe["heuristic_suggestion"]
            sugg_yaml = yaml.dump(sugg, default_flow_style=False).strip()
            score = round(probe.get("score", 0.0) * 100)
            m = probe["matches"][0] if probe["matches"] else {}

            # Different styling for AI RAG suggestions vs rule-based ones
            is_ai = "AI RAG" in probe_name
            card_icon = "&#129302;" if is_ai else "&#128161;"  # robot vs lightbulb
            card_border = "#1976d2" if is_ai else "#e9ecef"
            card_bg = "#e3f2fd" if is_ai else "#f8f9fa"
            badge = '<span style="background:#1565c0;color:#fff;font-size:10px;padding:2px 6px;border-radius:10px;margin-left:8px;">Gemini + RAG</span>' if is_ai else ""

            # Build AI candidates detail (collapsible)
            ai_detail = ""
            if is_ai and probe.get("ai_candidates"):
                cand_lines = "".join(f"<li style='margin:2px 0;font-size:11px;'>{_esc(c)}</li>" for c in probe["ai_candidates"])
                ai_detail = f"""
                <details style="margin-top:8px;">
                    <summary style="font-size:11px;color:#1565c0;cursor:pointer;">View all RAG candidates ({len(probe['ai_candidates'])})</summary>
                    <ul style="background:#fff;border:1px solid #e3f2fd;border-radius:4px;padding:8px;margin-top:4px;">{cand_lines}</ul>
                </details>"""

            html += f"""
            <div class="probe-item suggestion-card" style="border:2px solid {card_border};border-radius:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                    <span class="probe-name">{card_icon} {probe_name} (Confidence: {score}%){badge}</span>
                </div>
                <div style="font-size: 12px; margin-bottom: 10px; color: #555;">
                    Found a highly similar element on the page:<br>
                    <strong>Tag:</strong> <code>{_esc(m.get('tag',''))}</code>,
                    <strong>Role:</strong> <code>{_esc(m.get('role',''))}</code>,
                    <strong>Text:</strong> <code>{_esc(m.get('text',''))}</code>,
                    <strong>TestID:</strong> <code>{_esc(m.get('testid',''))}</code>
                </div>
                <div style="display:flex; gap: 15px;">
                    <div style="flex:1;">
                        <div style="font-size:11px; font-weight:bold; color:#666; margin-bottom:4px;">Suggested YAML Fix:</div>
                        <pre style="background:{card_bg}; padding:10px; border-radius:6px; border:1px solid {card_border}; font-size:12px; margin:0;">{_esc(sugg_yaml)}</pre>
                    </div>
                </div>
                {ai_detail}
            </div>"""
        else:
            matches = probe.get("matches", [])
            warning_msg = probe.get("warning", "")
            warning_html = ""
            if warning_msg:
                warning_html = f'<div style="margin-top:6px;padding:6px 10px;background:#fff3e0;border-left:3px solid #ff9800;border-radius:4px;font-size:12px;color:#e65100;">&#9888; {_esc(warning_msg)}</div>'
            html += f"""
            <div class="probe-item">
                <span class="probe-name">{probe_name}</span>
                <span class="probe-count">{count} found</span>
                {warning_html}
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
.data-table td { padding: 8px 12px; border-bottom: 1px solid #eee; word-break: break-word; overflow-wrap: anywhere; }
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
.step-warning .step-header { background: #fff8e1; border-left: 4px solid #ffc107; }
.step-anomaly .step-header { background: #fff8e1; border-left: 4px solid #ffc107; }
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
.network-box { background: #fff4e5; border: 1px solid #ffe0b2; border-radius: 8px; padding: 15px; margin: 15px 0; }
.network-title { font-weight: 700; color: #e65100; margin-bottom: 8px; }
.badge-warn { background: #f39c12; color: #fff; }
.badge-anomaly { background: #f39c12; color: #fff; }
.suggestion-card { background: #e3f2fd !important; border: 1px solid #90caf9 !important; border-radius: 8px; padding: 15px !important; margin-top: 10px; }
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
    parser.add_argument("--fix-only", action="store_true",
                        help="Skip replay; load saved suggestions from latest report and apply fixes interactively")
    parser.add_argument("--fix-json", type=str, default=None,
                        help="Path to a specific fix_suggestions.json file (used with --fix-only)")
    args = parser.parse_args()

    # --fix-only mode: load saved suggestions and run interactive fix (no replay)
    if args.fix_only:
        json_path = args.fix_json
        if not json_path:
            # Find the latest fix_suggestions.json
            json_files = sorted(REPORT_OUTPUT_DIR.glob("fix_suggestions_*.json"), reverse=True)
            if not json_files:
                print("ERROR: No fix_suggestions JSON found. Run diagnosis first to generate suggestions.")
                sys.exit(1)
            json_path = str(json_files[0])
            print(f"Using latest fix suggestions: {json_path}")
        else:
            json_path = str(PROJECT_ROOT / json_path)

        if not os.path.exists(json_path):
            print(f"ERROR: Fix suggestions file not found: {json_path}")
            sys.exit(1)

        with open(json_path, "r", encoding="utf-8") as f:
            fix_suggestions = json.load(f)

        if not fix_suggestions:
            print("No fix suggestions found in the JSON file.")
            sys.exit(0)

        _run_interactive_fix(fix_suggestions)
        return

    # Track start time for report duration
    start_time = datetime.datetime.now()

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
    failed_yamls = set()
    for case_info in failed_cases:
        ypath = case_info.get("yaml_path", "")
        if ypath in failed_yamls:
            print(f"  [SKIP] Skipping {case_info['name']} due to Cascade Failure (a prior case in {ypath} failed).")
            diagnosis_results.append({
                "case_name": case_info["name"],
                "yaml_path": ypath,
                "allure_error": case_info["error_message"],
                "allure_trace": case_info["error_trace"],
                "failed_step": "cascade_failure",
                "failed_step_error": "Skipped due to Cascade Failure from a prior test in the same YAML.",
                "step_records": [],
                "total_steps": len(case_info.get("steps_order", [])),
                "steps_passed": 0,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            continue

        try:
            result = replay_case(case_info, base_url, args.headed)
            diagnosis_results.append(result)
            if result.get("failed_step") and not result.get("failed_step_error", "").startswith("Diagnosis engine error"):
                failed_yamls.add(ypath)
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
            failed_yamls.add(ypath)

    # Phase 4: Generate HTML report
    print(f"\n--- Phase 4: Generating HTML Report ---")
    end_time = datetime.datetime.now()
    report_path = generate_html_report(diagnosis_results, args.env, os.path.basename(allure_dir), start_time, end_time)
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

    # Interactive Fix
    # Collect all heuristic suggestions (rule-based + AI)
    fix_suggestions = []
    for r in diagnosis_results:
        if r.get("failed_step"):
            for sr in r.get("step_records", []):
                if sr.get("step_name") == r["failed_step"]:
                    for p in sr.get("probing", []):
                        if "heuristic_suggestion" in p:
                            fix_suggestions.append({
                                "yaml_path": r["yaml_path"],
                                "case_name": r["case_name"],
                                "step_name": sr["step_name"],
                                "suggestion": p["heuristic_suggestion"],
                                "probe": p.get("probe", ""),
                                "score": p.get("score", 0),
                            })

    # Save fix suggestions to JSON for later --fix-only use
    if fix_suggestions:
        fix_suggestions.sort(key=lambda x: x.get("score", 0), reverse=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = REPORT_OUTPUT_DIR / f"fix_suggestions_{ts}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(fix_suggestions, f, indent=2, ensure_ascii=False)
        print(f"Fix suggestions saved: {json_path}")

    _run_interactive_fix(fix_suggestions)

    return report_path


def _run_interactive_fix(fix_suggestions: list):
    """Run the interactive fix loop from a list of fix suggestion dicts."""
    if not fix_suggestions:
        return

    # Sort by score descending for terminal display
    fix_suggestions.sort(key=lambda x: x.get("score", 0), reverse=True)
    print(f"\n{'='*60}")
    print(f"  \033[92mHeuristic Auto-Fix Available ({len(fix_suggestions)} suggestions)\033[0m")
    print(f"{'='*60}")
    for idx, fix in enumerate(fix_suggestions):
        is_ai = "AI RAG" in fix.get("probe", "")
        source_tag = "\033[94m[AI RAG]\033[0m" if is_ai else "\033[92m[Rule]\033[0m"
        print(f"\n  {source_tag} #{idx+1} (confidence: {fix.get('score', 0):.0%}) — {fix.get('probe', '')}")
        print(f"  Case: {fix['case_name']} | Step: {fix['step_name']}")
        print(f"  YAML: {fix['yaml_path']}")
        print(f"  Suggested Locator Update:\n{yaml.dump(fix['suggestion'], default_flow_style=False).strip()}")

        ans = input("\n  Apply this fix? [y/N/skip]: ").strip().lower()
        if ans == 'y':
            ok = _apply_yaml_fix(fix)
            if ok:
                print("  \033[92mFix applied successfully!\033[0m")
            else:
                print("  \033[91mFix failed. Please check the error above.\033[0m")

    return report_path


def _apply_yaml_fix(fix: dict) -> bool:
    """Directly patch a single step in a YAML file."""
    yaml_path = PROJECT_ROOT / fix["yaml_path"]
    case_name = fix["case_name"]
    step_name = fix["step_name"]
    suggestion = fix["suggestion"]

    if not yaml_path.exists():
        print(f"  [ERROR] File not found: {yaml_path}")
        return False

    try:
        with open(yaml_path, encoding="utf-8") as f:
            text = f.read()
        lines = text.splitlines(keepends=True)

        # Find the case block, then the step line
        in_case = False
        case_indent = None
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            # Detect case start
            if stripped.startswith(case_name + ":"):
                in_case = True
                case_indent = indent
                continue

            # Detect case end (next top-level key at same or lower indent)
            if in_case and indent <= case_indent and stripped and not stripped.startswith("#"):
                in_case = False
                continue

            if in_case and stripped.startswith(step_name + ":"):
                # Found the step line — parse old step, apply suggestion
                old_step_str = stripped[len(step_name)+1:].strip()
                # Try to parse as inline dict
                is_inline = bool(old_step_str)
                try:
                    old_step = yaml.safe_load(old_step_str) if old_step_str else {}
                    if not isinstance(old_step, dict):
                        old_step = {}
                except Exception:
                    old_step = {}

                # Build new step
                new_step = dict(old_step)
                for k, v in suggestion.items():
                    if v is None:
                        new_step.pop(k, None)
                    else:
                        new_step[k] = v

                # Serialize back to inline YAML
                parts = []
                for k in ("role", "name", "locator", "test_id", "placeholder",
                          "aria-label", "label", "index", "exact", "optional",
                          "value", "checked", "timeout", "frame"):
                    if k in new_step:
                        v = new_step[k]
                        if isinstance(v, str):
                            parts.append(f"{k}: '{v}'")
                        elif isinstance(v, bool):
                            parts.append(f"{k}: {str(v).capitalize()}")
                        else:
                            parts.append(f"{k}: {v}")
                for k, v in new_step.items():
                    if k not in ("role", "name", "locator", "test_id", "placeholder",
                                 "aria-label", "label", "index", "exact", "optional",
                                 "value", "checked", "timeout", "frame"):
                        if isinstance(v, str):
                            parts.append(f"{k}: '{v}'")
                        elif isinstance(v, bool):
                            parts.append(f"{k}: {str(v).capitalize()}")
                        else:
                            parts.append(f"{k}: {v}")

                new_line = " " * indent + step_name + ": { " + ", ".join(parts) + " }\n"
                lines[i] = new_line

                # If original was multi-line (no inline dict), delete the child lines below
                if not is_inline:
                    j = i + 1
                    while j < len(lines):
                        child_stripped = lines[j].lstrip()
                        child_indent = len(lines[j]) - len(child_stripped)
                        # Stop when we hit a line at same or lower indent (next step, next case, or blank)
                        if child_stripped and child_indent <= indent:
                            break
                        # Also stop at case boundary
                        if child_stripped and not child_stripped.startswith("#") and child_indent <= case_indent:
                            break
                        j += 1
                    # Remove lines (i+1) through (j-1)
                    if j > i + 1:
                        del lines[i + 1:j]

                with open(yaml_path, "w", encoding="utf-8") as f:
                    f.write("".join(lines))
                return True

        print(f"  [ERROR] Step '{step_name}' not found in case '{case_name}' in {yaml_path}")
        return False

    except Exception as e:
        print(f"  [ERROR] Failed to apply fix: {e}")
        return False


if __name__ == "__main__":
    main()
