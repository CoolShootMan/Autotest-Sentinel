"""
step_analyzer.py - Offline step-level analysis (replaces replay engine)

Reads captured step data from step_captures/ and produces structured
diagnosis: root cause classification + repair plan JSON.

No replay needed — all data was captured during the actual pytest run.

Usage:
    # Analyze a specific failed case
    python tools/step_analyzer.py analyze --case testT3981_Concurrency_01

    # Analyze cases that failed in the latest Allure report (recommended)
    python tools/step_analyzer.py analyze --from-report

    # Analyze all captured failures (legacy, scans entire step_captures/)
    python tools/step_analyzer.py analyze --all-failed

    # List available captures
    python tools/step_analyzer.py list

    # Generate HTML report
    python tools/step_analyzer.py report --case testT3981_Concurrency_01

Output format (repair-plan.json):
{
    "case_name": "testT3981_Concurrency_01",
    "yaml_path": ".../Scanner.yaml",
    "analysis_time": "2026-06-05T14:30:00",
    "failures": [
        {
            "step_num": 5,
            "step_key": "R_click",
            "step_value": {"name": "Scan", "role": "button"},
            "error_msg": "...",
            "failure_type": "selector_broken",     # 8-category classification
            "root_cause": "...",
            "repair_plan": {
                "action": "update_name",            # What to change
                "target_step": 5,
                "delta": {"name": "Start scan"},    # Concrete change
                "confidence": 0.85,
                "evidence": [...]                   # DOM elements that support this
            }
        }
    ],
    "selector_health": {                            # Phase 2 preview
        "healthy": 12,
        "risky": 2,
        "broken": 1
    }
}
"""

import json
import os
import sys
import argparse
import datetime
import re
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURES_DIR = os.path.join(PROJECT_ROOT, "step_captures")
ALLURE_RESULTS_DIR = os.path.join(PROJECT_ROOT, "allure-results")

# ---------------------------------------------------------------------------
# Failure type classification (8 categories, inspired by web-ui-autotest)
# ---------------------------------------------------------------------------

FAILURE_TYPES = {
    "selector_broken":   "Element locator no longer matches any element on page",
    "selector_ambiguous": "Locator matches multiple elements, cannot determine which one to interact with",
    "element_obscured":  "Element exists but is covered by modal/dialog/overlay",
    "timeout":           "Element not found within timeout — may not exist or page not loaded",
    "auth_expired":      "Cookie/session expired, page shows login or auth error",
    "api_error":         "Backend API error or empty state preventing interaction",
    "navigation_error":  "Wrong page/URL reached, element not on current page",
    "data_stale":        "Test data conflict from previous run (residual data)",
}


# ---------------------------------------------------------------------------
# Gemini AI + DOM Knowledge Base (for AI RAG suggestions)
# ---------------------------------------------------------------------------
_gemini_client = None
_gemini_model_name = None
_gemini_api_keys = []
_gemini_current_key_idx = 0
_gemini_model_idx = 0
_dom_kb_loaded = False

_GEMINI_MODEL_CHAIN = [
    # Ordered by free-tier quota (highest first), per Google AI Studio 2026-06
    # gemini-2.5-flash-lite:   30 RPM / 1,500 RPD / 1M TPM  (largest, weakest capability)
    # gemini-3.1-flash-lite:   30 RPM / 1,500 RPD / 1M TPM  (new May 2026, free tier available)
    # gemini-2.5-flash:        15 RPM / 1,500 RPD / 1M TPM  (good value for coding tasks)
    # gemini-2.5-pro:           5 RPM / 50 RPD / 250K TPM   (strongest but very tight quota, last resort)
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

# Rate limiting: minimum seconds between API calls to avoid 429
_GEMINI_CALL_INTERVAL = 2.0
_last_gemini_call_time = 0.0


def _load_gemini_keys():
    """Load Gemini API keys from backend/.env."""
    global _gemini_api_keys, _gemini_model_name
    if _gemini_api_keys:
        return True
    try:
        from dotenv import load_dotenv as _ld
        _backend_env = os.path.join(PROJECT_ROOT, "backend", ".env")
        if os.path.exists(_backend_env):
            _ld(_backend_env, override=True)
        keys_str = os.getenv("GEMINI_API_KEYS", "")
        if not keys_str:
            return False
        keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if not keys:
            return False
        _gemini_api_keys = keys
        _gemini_model_name = _GEMINI_MODEL_CHAIN[_gemini_model_idx]
        return True
    except Exception:
        return False


def _load_gemini(force_model: str = None):
    """Lazy-load Gemini client. Falls back to HTTP if SDK not available."""
    global _gemini_client, _gemini_api_keys, _gemini_current_key_idx, _gemini_model_idx, _gemini_model_name
    if _gemini_client is not None and force_model is None:
        return _gemini_client
    if not _load_gemini_keys():
        return None
    try:
        from google import genai as genai_mod
        _gemini_model_name = force_model or _GEMINI_MODEL_CHAIN[_gemini_model_idx]
        _gemini_client = genai_mod.Client(api_key=_gemini_api_keys[0])
        return _gemini_client
    except Exception:
        # SDK not available — will use HTTP fallback
        _gemini_client = "HTTP_FALLBACK"
        return _gemini_client


def _rotate_gemini_key():
    """Rotate to next API key. Returns True if rotated."""
    global _gemini_client, _gemini_current_key_idx
    if len(_gemini_api_keys) <= 1:
        return False
    _gemini_current_key_idx = (_gemini_current_key_idx + 1) % len(_gemini_api_keys)
    if _gemini_current_key_idx == 0:
        return False
    try:
        if _gemini_client != "HTTP_FALLBACK":
            from google import genai as genai_mod
            _gemini_client = genai_mod.Client(api_key=_gemini_api_keys[_gemini_current_key_idx])
        return True
    except Exception:
        return False


def _downgrade_gemini_model():
    """Downgrade to next model in fallback chain."""
    global _gemini_client, _gemini_model_idx, _gemini_current_key_idx, _gemini_model_name
    if _gemini_model_idx >= len(_GEMINI_MODEL_CHAIN) - 1:
        return False
    _gemini_model_idx += 1
    _gemini_current_key_idx = 0
    _gemini_model_name = _GEMINI_MODEL_CHAIN[_gemini_model_idx]
    try:
        if _gemini_client != "HTTP_FALLBACK":
            from google import genai as genai_mod
            _gemini_client = genai_mod.Client(api_key=_gemini_api_keys[0])
        return True
    except Exception:
        return False


def _call_gemini_http(prompt_text: str, image_b64: bytes = None) -> str:
    """Call Gemini via HTTP REST API (fallback when SDK not available)."""
    import urllib.request
    import urllib.error

    api_key = _gemini_api_keys[_gemini_current_key_idx] if _gemini_api_keys else ""
    if not api_key:
        raise RuntimeError("No Gemini API key available")

    model = _gemini_model_name or _GEMINI_MODEL_CHAIN[0]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    parts = [{"text": prompt_text}]
    if image_b64:
        import base64
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_b64).decode("ascii")
            }
        })

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # Extract text from response
    candidates = result.get("candidates", [])
    if not candidates:
        raise RuntimeError("No candidates in response")
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        raise RuntimeError("No parts in response")
    return parts[0].get("text", "")


def _query_dom_kb(step_value: dict, url_hint: str = "", top_k: int = 5):
    """Query DOM knowledge base for similar elements."""
    global _dom_kb_loaded
    if not _dom_kb_loaded:
        try:
            tools_dir = os.path.join(PROJECT_ROOT, "tools")
            if tools_dir not in sys.path:
                sys.path.insert(0, tools_dir)
            from dom_kb import query_for_failed_step
            import tools.dom_kb as _dk
            _query_dom_kb._fn = _dk.query_for_failed_step
        except Exception:
            _query_dom_kb._fn = None
        _dom_kb_loaded = True
    fn = getattr(_query_dom_kb, "_fn", None)
    if fn:
        try:
            return fn(step_value, url_hint=url_hint, top_k=top_k)
        except Exception:
            # DOM KB runtime error (e.g. faiss not installed, index missing)
            return []
    return []


def _read_screenshot_b64(screenshot_path: str) -> Optional[str]:
    """Read a JPEG screenshot and return base64-encoded bytes."""
    try:
        with open(screenshot_path, "rb") as f:
            return f.read()
    except Exception:
        return None


def _probe_ai_rag_suggestion(
    step_value: dict,
    error_msg: str = "",
    dom_snapshot: list = None,
    screenshot_path: str = None,
    preloaded_candidates: list = None,
) -> Optional[dict]:
    """AI RAG Suggestion — multimodal with static screenshot file.

    Returns dict with ai_suggestion, is_schema_mutation, confidence, analysis.
    """
    candidates = preloaded_candidates if preloaded_candidates is not None else _query_dom_kb(step_value, top_k=3)

    # Fallback: if DOM KB not available, extract candidates from dom_snapshot
    if not candidates and dom_snapshot:
        target_name = ""
        target_role = ""
        if isinstance(step_value, dict):
            target_name = step_value.get("name", "") or step_value.get("text", "")
            target_role = step_value.get("role", "")
            # Parse locator for :has-text or text content
            if not target_name and step_value.get("locator"):
                locator = step_value.get("locator", "")
                text_match = re.search(r':has-text\(["\']([^"\']+)["\']\)', locator)
                if not text_match:
                    text_match = re.search(r'text\(["\']([^"\']+)["\']\)', locator)
                if text_match:
                    target_name = text_match.group(1)
                role_match = re.search(r'\[role=["\']([^"\']+)["\']\]', locator)
                if role_match:
                    target_role = role_match.group(1)
        for el in dom_snapshot:
            el_name = el.get("name", "") or el.get("text", "") or el.get("ariaLabel", "")
            el_role = el.get("role", "")
            score = 0.0
            if target_name and target_name.lower() in el_name.lower():
                score = 0.8
            if target_role and target_role == el_role:
                score = max(score, 0.6)
            # Also collect interactive elements with non-empty text as weak candidates
            if score < 0.3 and el_role in ("button", "menuitem", "link", "tab", "option") and el_name.strip():
                score = 0.25
            if score >= 0.25:
                candidates.append({"element": el, "score": score})
        candidates.sort(key=lambda x: x.get("score", 0), reverse=True)
        # If we have a screenshot, send ALL candidates to AI (it can see the image)
        # Otherwise limit to top 5 to keep prompt short
        has_screenshot = screenshot_path and os.path.exists(screenshot_path)
        candidates = candidates[:10] if has_screenshot else candidates[:5]

    if not candidates:
        return {"ai_reason": "No DOM candidates found (neither from KB nor snapshot)", "score": 0.0}

    # Filter quality candidates
    def _is_quality(c):
        el = c["element"]
        score = c.get("score", 0)
        text = el.get("text", "")
        role = el.get("role", "")
        if role in ("dialog", "alertdialog", "presentation", "none"):
            return False
        if "name=" in text and len(text) < 30:
            return False
        # Lower threshold for offline analysis (DOM snapshot may have limited matches)
        if score < 0.25:
            return False
        if text.count(" ") > 8 and any(x in text.lower() for x in ("short", "long", "email", "phone", "paragraph")):
            return False
        return True

    filtered = [c for c in candidates if _is_quality(c)]
    # No quality candidates — not an API error, just nothing to analyze
    if not filtered:
        return {"ai_reason": "No quality DOM candidates found for AI analysis", "score": 0.0}

    # Build compact candidate descriptions
    candidate_descs = []
    for i, c in enumerate(filtered):
        el = c["element"]
        score = c.get("score", 0)
        _name = el.get("name", "")
        name_disp = _name if _name else "[EMPTY]"
        _al = el.get("ariaLabel", "")
        al_disp = _al if _al else "[EMPTY]"
        candidate_descs.append(
            f"  [{i+1}] score={score:.3f} | role={el.get('role','')} "
            f"testid={el.get('testid','')} ariaLabel={al_disp} "
            f"text={el.get('text','')[:60]} name={name_disp}"
        )

    orig_desc = ", ".join(f"{k}={v}" for k, v in step_value.items() if v) if isinstance(step_value, dict) else str(step_value)

    # Read screenshot if available
    screenshot_b64 = None
    if screenshot_path and os.path.exists(screenshot_path):
        screenshot_b64 = _read_screenshot_b64(screenshot_path)

    has_visual = screenshot_b64 is not None

    if has_visual:
        prompt_text = f"""You are a senior QA automation expert with 10 years of experience.
A UI test step FAILED because the element locator is outdated.

# Input Data
1. [FAILED STEP LOCATOR]: {orig_desc}
2. [ERROR]: {error_msg[:200] if error_msg else 'N/A'}
3. [VISUAL SCREENSHOT]: The attached image is the actual page state when the failure occurred.
4. [DOM CANDIDATES] — Latest elements found by semantic search:
{chr(10).join(candidate_descs)}

# Task — Chain of Thought
Use BOTH the image AND the DOM candidates to answer:

Step 1 VISUAL CHECK: In the image, does the element that should be "{step_value.get('name') or step_value.get('text') or ''}" still exist visually?
  - If YES: what does it look like now? (input box, dropdown, button, etc.)
  - This tells you whether the element still exists but changed form (schema mutation) or is genuinely missing.

Step 2 SEMANTIC ALIGNMENT: Cross-check the DOM candidates.
  - "text" = innerText (VISIBLE on screen). "ariaLabel" = ARIA label attribute. NEITHER is necessarily the "accessible name" that Playwright uses for get_by_role(role, name=...).
  - The accessible name is computed by the browser from multiple sources. It may be DIFFERENT from visible text.
  - Therefore: do NOT change "name" just because "text" or "ariaLabel" differs.

Step 3 DECISION (Occam's Razor — minimal change):
  - If visual + semantic both confirm SAME element, different role → set is_schema_mutation: true, only change "role". KEEP "name" unchanged.
  - If the element's accessible name genuinely changed → set is_schema_mutation: false, update "name".
  - If both changed → set is_schema_mutation: true, update both.
  - If no confident match → return {chr(123)}"reason": "brief explanation"{chr(125)}.

# Output Format (JSON only, no markdown)
{chr(123)}
  "is_schema_mutation": true/false,
  "visual_insight": "one sentence describing what you see in the image",
  "analysis": "one sentence semantic reasoning",
  "suggested_fix_delta": {chr(123)}"role": "combobox"{chr(125)}
{chr(125)}

RULE: In suggested_fix_delta, include ONLY fields that actually changed from the original step.
If the original "name" is still valid, do NOT include "name" in the delta."""
    else:
        prompt_text = f"""You are a QA automation expert. A UI test step FAILED because the element locator is outdated.

FAILED STEP: {orig_desc}
ERROR: {error_msg[:200] if error_msg else 'N/A'}

DOM Knowledge Base candidates (current page):
{chr(10).join(candidate_descs)}

TASK: Analyze each candidate vs the original step, then output the MINIMAL fix (delta only).

RULES:
- Pick the SEMANTIC match, not a text-exact match
- Prefer: test_id > role+name > role+ariaLabel > locator
- "text" in candidates is innerText — do NOT use it to infer "name" changes

DECISION FRAMEWORK:
- SCENARIO A: role changed, same function → ONLY change "role", KEEP "name"
- SCENARIO B: label/text changed, role same → update "name"
- SCENARIO C: both changed → semantic judgment, WHEN IN DOUBT only change "role"

If no good match, return {chr(123)}"reason": "brief explanation"{chr(125)}

RESPOND WITH JSON ONLY (no markdown):
{chr(123)}"is_schema_mutation": true/false, "analysis": "reasoning", "suggested_fix_delta": {chr(123)}"field": "value"{chr(125)}{chr(125)}"""

    model = _load_gemini()
    if model is None:
        return {"ai_reason": "Gemini API keys not configured (check backend/.env GEMINI_API_KEYS)", "score": 0.0}

    use_http = (model == "HTTP_FALLBACK")
    last_error = None
    _ssl_retry_count = 0
    _429_backoff = 2  # seconds, doubles on each consecutive 429
    while True:
        # --- Rate limiting: enforce minimum interval between calls ---
        global _last_gemini_call_time
        import time as _time_mod
        _now = _time_mod.time()
        _elapsed = _now - _last_gemini_call_time
        if _elapsed < _GEMINI_CALL_INTERVAL:
            _time_mod.sleep(_GEMINI_CALL_INTERVAL - _elapsed)
        _last_gemini_call_time = _time_mod.time()

        # Debug: show which model/key is being used
        print(f"    [Gemini] model={_gemini_model_name} key#{_gemini_current_key_idx + 1}/{len(_gemini_api_keys)}", flush=True)

        try:
            if use_http:
                raw = _call_gemini_http(prompt_text, image_b64=screenshot_b64 if has_visual else None)
            else:
                if has_visual:
                    from google.genai import types as genai_types
                    image_part = genai_types.Part.from_bytes(
                        data=screenshot_b64, mime_type="image/jpeg"
                    )
                    response = model.models.generate_content(
                        model=_gemini_model_name, contents=[prompt_text, image_part]
                    )
                else:
                    response = model.models.generate_content(
                        model=_gemini_model_name, contents=prompt_text
                    )
                raw = response.text.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
            result = json.loads(raw)

            ai_analysis = result.get("analysis", "")
            visual_insight = result.get("visual_insight", "")
            is_schema_mutation = bool(result.get("is_schema_mutation", False))
            delta = result.get("suggested_fix_delta", {})

            if visual_insight and ai_analysis:
                ai_analysis_full = f"[Visual] {visual_insight} | [Semantic] {ai_analysis}"
            elif visual_insight:
                ai_analysis_full = f"[Visual] {visual_insight}"
            else:
                ai_analysis_full = ai_analysis

            if "reason" in result and len(result) == 1:
                return {
                    "ai_reason": result["reason"],
                    "ai_analysis": ai_analysis_full,
                    "is_schema_mutation": False,
                    "score": 0.0,
                }

            suggested_fix = {}
            for k in ("test_id", "role", "name", "text", "label", "placeholder", "locator"):
                if k in delta and delta[k]:
                    suggested_fix[k] = delta[k]

            # Safety net: prevent AI from confusing innerText/ariaLabel with accessible name
            if "name" in suggested_fix and filtered:
                best_el = filtered[0].get("element", {})
                cand_name = best_el.get("name", "")
                cand_text = best_el.get("text", "")
                cand_aria = best_el.get("ariaLabel", "")
                suggested_name = str(suggested_fix["name"])
                orig_name = step_value.get("name") or step_value.get("text") or ""
                orig_name_lower = orig_name.lower()
                name_still_present = (
                    orig_name_lower in (cand_text or "").lower() or
                    orig_name_lower in (cand_aria or "").lower() or
                    orig_name == cand_name or orig_name == cand_text or orig_name == cand_aria
                )
                if name_still_present:
                    del suggested_fix["name"]
                elif not cand_name and (suggested_name == cand_text or suggested_name == cand_aria):
                    del suggested_fix["name"]

            if not suggested_fix:
                return {"ai_reason": "AI could not determine a concrete fix", "ai_analysis": ai_analysis_full, "score": 0.0}

            best_match = filtered[0]["element"] if filtered else {}
            return {
                "heuristic_suggestion": suggested_fix,
                "is_schema_mutation": is_schema_mutation,
                "ai_analysis": ai_analysis_full,
                "score": 0.92 if has_visual else 0.85,
                "matched_element": best_match,
                "has_visual": has_visual,
            }

        except Exception as e:
            err_str = str(e).lower()
            if any(kw in err_str for kw in ("ssl", "eof", "connection", "timeout")):
                _ssl_retry_count += 1
                if _ssl_retry_count <= 2:
                    import time
                    time.sleep(1)
                    continue
                if _rotate_gemini_key():
                    _ssl_retry_count = 0
                    continue
                break
            if "quota" in err_str or "rate limit" in err_str or "429" in err_str:
                # Exponential backoff: wait longer each time before retry
                _time_mod.sleep(_429_backoff)
                _429_backoff = min(_429_backoff * 2, 16)  # max 16s
                global _last_gemini_call_time
                _last_gemini_call_time = 0  # reset so next call doesn't double-wait
                if _rotate_gemini_key():
                    continue
                if _downgrade_gemini_model():
                    continue
            last_error = e
            break

    # All retries exhausted
    err_detail = str(last_error)[:120] if last_error else "All API keys and model fallbacks exhausted"
    return {"ai_reason": f"Gemini API unavailable: {err_detail}", "score": 0.0}


def _classify_failure(step_data: Dict, prev_step: Optional[Dict] = None) -> Tuple[str, str]:
    """Classify a failed step into one of 8 failure types.

    Returns:
        (failure_type, root_cause_description)
    """
    error_msg = step_data.get("error_msg", "") or ""
    dom = step_data.get("dom_snapshot", []) or []
    step_key = step_data.get("step_key", "")
    step_value = step_data.get("step_value", {})
    url = step_data.get("url", "")

    error_lower = error_msg.lower()

    # 1. Auth expired — check for login-related patterns in error or URL
    auth_indicators = ["login", "sign in", "signin", "unauthorized", "401", "403",
                       "authenticate", "session expired"]
    if any(ind in error_lower for ind in auth_indicators):
        return "auth_expired", "Session/cookie expired, page redirected to login"

    if any(ind in url.lower() for ind in ["login", "signin", "sign-in"]):
        return "auth_expired", "Page URL indicates login redirect — cookie likely expired"

    # 2. Element obscured — check DOM for modal/dialog/overlay
    modal_roles = {"dialog", "alertdialog", "modal"}
    modal_elements = [el for el in dom if el.get("role", "") in modal_roles]
    if modal_elements:
        # Check if step target is being obscured
        target_name = step_value.get("name", "") if isinstance(step_value, dict) else ""
        target_role = step_value.get("role", "") if isinstance(step_value, dict) else ""
        # If the target exists in DOM but action failed, it's likely obscured
        target_in_dom = False
        for el in dom:
            el_name = el.get("name", "") or el.get("text", "") or el.get("ariaLabel", "")
            if target_name and target_name in el_name:
                target_in_dom = True
                break
            if target_role and target_role == el.get("role", ""):
                target_in_dom = True
                break
        if target_in_dom:
            return "element_obscured", f"Element exists but obscured by {modal_elements[0].get('role', 'overlay')}: '{modal_elements[0].get('name', modal_elements[0].get('text', ''))}'"

    # 3. Timeout — error contains timeout keywords
    timeout_indicators = ["timeout", "timed out", "waiting for", "waited"]
    if any(ind in error_lower for ind in timeout_indicators):
        # Check if element exists in DOM at all
        target_name = step_value.get("name", "") if isinstance(step_value, dict) else ""
        if target_name:
            found = any(target_name in (el.get("name", "") or el.get("text", "") or el.get("ariaLabel", ""))
                       for el in dom)
            if found:
                return "element_obscured", f"Element '{target_name}' exists in DOM but timeout suggests it's not interactable"
            else:
                return "selector_broken", f"Element '{target_name}' not found in DOM — locator may be outdated"
        return "timeout", "Element not found within timeout — page may not be fully loaded"

    # 4. Navigation error — check URL
    expected_url_pattern = step_value.get("url", "") if isinstance(step_value, dict) else ""
    if expected_url_pattern and url and expected_url_pattern not in url:
        return "navigation_error", f"Expected URL containing '{expected_url_pattern}' but at '{url}'"

    # 5. API error — check DOM for error states
    error_indicators_dom = [el for el in dom
                           if any(kw in (el.get("text", "") or el.get("name", "")).lower()
                                 for kw in ["error", "failed", "something went wrong", "try again"])]
    if error_indicators_dom:
        return "api_error", f"Page shows error state: '{error_indicators_dom[0].get('text', '')[:60]}'"

    # 6. Selector broken — element not found in DOM
    if "not found" in error_lower or "no element" in error_lower or "strict mode" in error_lower:
        target_name = step_value.get("name", "") if isinstance(step_value, dict) else ""
        if target_name:
            found = any(target_name in (el.get("name", "") or el.get("text", "") or el.get("ariaLabel", ""))
                       for el in dom)
            if not found:
                # Look for similar elements
                similar = _find_similar_elements(target_name, step_value, dom)
                if similar:
                    return "selector_broken", f"Element '{target_name}' not found. Similar: {similar[0].get('name', similar[0].get('text', ''))}"
                return "selector_broken", f"Element '{target_name}' not found in DOM and no similar elements detected"
        return "selector_broken", "Element locator does not match any element on page"

    # 7. Selector ambiguous
    if "strict mode" in error_lower or "multiple elements" in error_lower or "ambiguous" in error_lower:
        return "selector_ambiguous", "Locator matches multiple elements — needs more specific selector"

    # 8. Default — data stale / unknown
    return "data_stale", f"Unclassified failure: {error_msg[:100]}"


def _find_similar_elements(target_name: str, step_value: Dict, dom: List[Dict]) -> List[Dict]:
    """Find DOM elements similar to the target for repair suggestions."""
    if not target_name or not dom:
        return []

    target_role = step_value.get("role", "") if isinstance(step_value, dict) else ""
    candidates = []

    for el in dom:
        el_name = el.get("name", "") or el.get("text", "") or el.get("ariaLabel", "")
        el_role = el.get("role", "")
        score = 0.0

        # Name similarity (substring match)
        if target_name.lower() in el_name.lower() or el_name.lower() in target_name.lower():
            score = 0.7
        # Role match
        if target_role and target_role == el_role:
            score = max(score, 0.6)
            if target_name.lower() in el_name.lower():
                score = 0.9
        # testid match (partial)
        target_testid = step_value.get("testid", "") if isinstance(step_value, dict) else ""
        if target_testid and target_testid in el.get("testid", ""):
            score = max(score, 0.85)

        if score >= 0.5:
            candidates.append({**el, "_score": score})

    candidates.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return candidates[:5]


def _build_repair_plan(step_data: Dict, failure_type: str, root_cause: str,
                       screenshot_path: str = None) -> Dict:
    """Build a structured repair plan for a failed step.

    Uses heuristic rules first, then calls AI RAG for enhancement if confidence
    is low or action is manual_review.
    """
    step_value = step_data.get("step_value", {})
    dom = step_data.get("dom_snapshot", []) or []
    step_num = step_data.get("step_num", 0)
    error_msg = step_data.get("error_msg", "")

    repair = {
        "action": "manual_review",
        "target_step": step_num,
        "delta": {},
        "confidence": 0.3,
        "evidence": [],
    }

    if failure_type == "selector_broken":
        target_name = step_value.get("name", "") if isinstance(step_value, dict) else ""
        similar = _find_similar_elements(target_name, step_value, dom)

        if similar:
            best = similar[0]
            new_name = best.get("name", "") or best.get("text", "") or best.get("ariaLabel", "")
            new_role = best.get("role", "")
            repair = {
                "action": "update_name" if new_name != target_name else "update_role",
                "target_step": step_num,
                "delta": {},
                "confidence": best.get("_score", 0.5),
                "evidence": [{"name": e.get("name", ""), "role": e.get("role", ""),
                              "testid": e.get("testid", ""), "score": e.get("_score", 0)}
                             for e in similar[:3]],
            }
            if new_name and new_name != target_name:
                repair["delta"]["name"] = new_name
            if new_role and new_role != step_value.get("role", ""):
                repair["delta"]["role"] = new_role

    elif failure_type == "element_obscured":
        # Suggest closing the modal first
        modal_roles = {"dialog", "alertdialog", "modal"}
        modals = [el for el in dom if el.get("role", "") in modal_roles]
        close_candidates = [el for el in dom
                           if el.get("role", "") == "button"
                           and any(kw in (el.get("name", "") or el.get("text", "")).lower()
                                   for kw in ["close", "cancel", "dismiss", "x"])]
        repair = {
            "action": "add_dismiss_step",
            "target_step": step_num,
            "delta": {"before_step": {"action": "click_modal_close"}},
            "confidence": 0.7,
            "evidence": [{"modal": m.get("name", m.get("text", "")), "role": m.get("role", "")}
                         for m in modals[:2]],
        }
        if close_candidates:
            repair["delta"]["before_step"] = {
                "action": "R_click",
                "name": close_candidates[0].get("name", close_candidates[0].get("text", "")),
                "role": "button",
            }

    elif failure_type == "auth_expired":
        repair = {
            "action": "refresh_cookie",
            "target_step": 0,
            "delta": {"note": "Cookie/session expired — regenerate cookie file"},
            "confidence": 0.9,
            "evidence": [{"url": step_data.get("url", "")}],
        }

    elif failure_type == "timeout":
        repair = {
            "action": "add_wait",
            "target_step": step_num,
            "delta": {"add_before": {"action": "wait_for_selector", "timeout": 15000}},
            "confidence": 0.5,
            "evidence": [],
        }

    elif failure_type == "navigation_error":
        repair = {
            "action": "update_url",
            "target_step": step_num,
            "delta": {"note": "Check if URL navigation is correct"},
            "confidence": 0.4,
            "evidence": [{"actual_url": step_data.get("url", "")}],
        }

    # ---- AI RAG Enhancement ----
    # Call AI when: confidence < 0.7, or action is manual_review, or selector_broken
    should_call_ai = (
        repair["action"] == "manual_review"
        or repair["confidence"] < 0.7
        or failure_type in ("selector_broken", "selector_ambiguous")
    )
    if should_call_ai:
        try:
            ai_result = _probe_ai_rag_suggestion(
                step_value=step_value,
                error_msg=error_msg,
                dom_snapshot=dom,
                screenshot_path=screenshot_path,
            )
            # ai_result is now always a dict (never None)
            if ai_result and ai_result.get("score", 0) > 0 and ai_result.get("heuristic_suggestion"):
                # AI gave a concrete suggestion
                repair["ai_suggestion"] = ai_result.get("heuristic_suggestion", {})
                repair["ai_analysis"] = ai_result.get("ai_analysis", "")
                repair["ai_confidence"] = ai_result.get("score", 0.0)
                repair["ai_has_visual"] = ai_result.get("has_visual", False)
                repair["ai_is_schema_mutation"] = ai_result.get("is_schema_mutation", False)
                # If AI gives a good suggestion, boost the overall confidence
                if ai_result.get("score", 0) > repair["confidence"]:
                    repair["confidence"] = ai_result["score"]
                    # If AI has a concrete suggestion and heuristic was manual_review, upgrade action
                    if repair["action"] == "manual_review" and ai_result.get("heuristic_suggestion"):
                        repair["action"] = "ai_suggested_update"
                        repair["delta"] = ai_result["heuristic_suggestion"]
            elif ai_result and ai_result.get("ai_reason"):
                # AI ran but couldn't produce a suggestion — propagate the reason
                repair["ai_error"] = ai_result["ai_reason"]
                repair["ai_analysis"] = ai_result.get("ai_analysis", "")
                repair["ai_has_visual"] = ai_result.get("has_visual", False)
        except Exception as e:
            err_str = str(e).lower()
            if "quota" in err_str or "429" in err_str:
                repair["ai_error"] = "Gemini API quota exhausted — AI suggestions unavailable until quota resets"
            elif "location" in err_str or "not supported" in err_str:
                repair["ai_error"] = "Gemini API region restricted — check network/proxy settings"
            elif "503" in err_str or "unavailable" in err_str:
                repair["ai_error"] = "Gemini API service temporarily unavailable — try again later"
            else:
                repair["ai_error"] = f"AI service error: {str(e)[:120]}"
            logger.warning(f"AI RAG suggestion failed for step {step_num}: {e}")

    return repair


# ---------------------------------------------------------------------------
# Selector Health Check (Phase 2 preview)
# ---------------------------------------------------------------------------

def _check_selector_health(manifest: Dict) -> Dict:
    """Check health of selectors by comparing step values against captured DOMs.

    For each step, verify that the step's locator still uniquely matches
    an element in the post-step DOM snapshot.
    """
    steps = manifest.get("steps", [])
    healthy = 0
    risky = 0
    broken = 0
    details = []

    for step in steps:
        if step.get("status") != "passed":
            continue

        step_value = step.get("step_value", {})
        if not isinstance(step_value, dict):
            continue

        target_name = step_value.get("name", "")
        target_role = step_value.get("role", "")
        target_testid = step_value.get("testid", "")
        dom = step.get("dom_snapshot", []) or []

        if not dom:
            continue

        # Count matches
        matches = 0
        for el in dom:
            if target_testid and target_testid == el.get("testid", ""):
                matches += 1
                continue
            if target_role and target_name:
                if target_role == el.get("role", "") and target_name in (el.get("name", "") or el.get("text", "") or el.get("ariaLabel", "")):
                    matches += 1
            elif target_name:
                if target_name in (el.get("name", "") or el.get("text", "") or el.get("ariaLabel", "")):
                    matches += 1

        if matches == 1:
            healthy += 1
        elif matches > 1:
            risky += 1
            details.append({"step_num": step["step_num"], "status": "risky", "matches": matches})
        else:
            broken += 1
            details.append({"step_num": step["step_num"], "status": "broken", "matches": 0,
                           "target_name": target_name, "target_role": target_role})

    return {
        "healthy": healthy,
        "risky": risky,
        "broken": broken,
        "total_checked": healthy + risky + broken,
        "details": details,
    }


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def analyze_case(case_name: str, captures_dir: str = None) -> Optional[Dict]:
    """Analyze a captured case and produce a repair plan."""
    from tools.step_capture import load_capture

    manifest = load_capture(case_name, captures_dir)
    if not manifest:
        logger.error(f"No capture data found for: {case_name}")
        return None

    if manifest.get("test_passed", True):
        logger.info(f"Case {case_name} passed — no failures to analyze")
        return None

    # Resolve captures dir and case dir early (needed for screenshot path resolution)
    if captures_dir is None:
        captures_dir = CAPTURES_DIR
    case_dir = os.path.join(captures_dir, case_name)

    steps = manifest.get("steps", [])
    failures = []

    for i, step in enumerate(steps):
        if step.get("status") != "failed":
            continue

        prev_step = steps[i - 1] if i > 0 else None
        failure_type, root_cause = _classify_failure(step, prev_step)

        # Resolve screenshot path for AI multimodal analysis
        screenshot_file = step.get("screenshot_file", "")
        screenshot_path = None
        if screenshot_file:
            _sp = os.path.join(case_dir, screenshot_file)
            if os.path.exists(_sp):
                screenshot_path = _sp

        repair_plan = _build_repair_plan(step, failure_type, root_cause, screenshot_path=screenshot_path)

        failures.append({
            "step_num": step["step_num"],
            "step_key": step["step_key"],
            "step_value": step.get("step_value", {}),
            "error_msg": step.get("error_msg", ""),
            "failure_type": failure_type,
            "failure_type_description": FAILURE_TYPES.get(failure_type, ""),
            "root_cause": root_cause,
            "url": step.get("url", ""),
            "repair_plan": repair_plan,
        })

    # Selector health check
    selector_health = _check_selector_health(manifest)

    result = {
        "case_name": case_name,
        "yaml_path": manifest.get("metadata", {}).get("yaml_path", ""),
        "analysis_time": datetime.datetime.now().isoformat(),
        "total_steps": manifest.get("total_steps", 0),
        "failed_steps": manifest.get("failed_steps", []),
        "failures": failures,
        "selector_health": selector_health,
    }

    # Save result
    os.makedirs(case_dir, exist_ok=True)
    result_path = os.path.join(case_dir, "repair-plan.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"Analysis saved to {result_path}")

    return result


# ---------------------------------------------------------------------------
# Allure Report Integration — get failed/broken cases from latest run
# ---------------------------------------------------------------------------

def find_latest_allure_dir() -> Optional[str]:
    """Find the latest timestamped subdirectory under allure-results/."""
    if not os.path.isdir(ALLURE_RESULTS_DIR):
        return None
    subdirs = sorted(
        [d for d in os.listdir(ALLURE_RESULTS_DIR)
         if os.path.isdir(os.path.join(ALLURE_RESULTS_DIR, d))],
        reverse=True
    )
    return os.path.join(ALLURE_RESULTS_DIR, subdirs[0]) if subdirs else None


def get_failed_cases_from_report(allure_dir: str = None) -> list[str]:
    """
    Parse *-result.json files from the given (or latest) Allure results dir.
    Returns a list of case names whose status is 'failed' or 'broken'.
    """
    import glob

    if allure_dir is None:
        allure_dir = find_latest_allure_dir()
        if not allure_dir:
            logger.warning("No Allure results directory found")
            return []

    result_files = glob.glob(os.path.join(allure_dir, "*-result.json"))
    case_names = []
    for f in result_files:
        try:
            d = json.load(open(f, encoding="utf-8"))
            status = d.get("status", "").lower()
            if status in ("failed", "broken"):
                case_names.append(d.get("name", ""))
        except Exception:
            continue
    return case_names


def analyze_all_failed(captures_dir: str = None, from_report: bool = False) -> List[Dict]:
    """Analyze all failed cases in the captures directory.

    Args:
        captures_dir: Custom captures directory path.
        from_report: If True, only analyze cases that appear as failed/broken
                     in the latest Allure report (instead of all captured failures).
    """
    from tools.step_capture import list_captures

    # Determine which cases to analyze
    if from_report:
        failed_names = set(get_failed_cases_from_report())
        if not failed_names:
            print("No failed/broken cases found in the latest Allure report.")
            print(f"  Searched: {find_latest_allure_dir() or 'N/A'}")
            return []
        print(f"Found {len(failed_names)} failed/broken case(s) in Allure report:")
        for n in sorted(failed_names):
            print(f"  - {n}")

    captures = list_captures(captures_dir)
    results = []
    analyzed_count = 0
    skipped_no_capture = 0

    for cap in captures:
        name = cap["case_name"]

        # When --from-report: skip cases not in the report's failure list
        if from_report and name not in failed_names:
            continue

        if not cap.get("test_passed", True):
            # Check capture data actually exists on disk (not just stale manifest)
            cap_path = os.path.join(captures_dir or CAPTURES_DIR, name)
            if not os.path.isdir(cap_path):
                skipped_no_capture += 1
                logger.warning(f"No capture data found (stale manifest): {name}")
                continue

            result = analyze_case(name, captures_dir)
            if result:
                results.append(result)
                analyzed_count += 1

    if from_report and skipped_no_capture > 0:
        logger.warning(
            f"{skipped_no_capture} case(s) had no step capture data "
            f"(re-run tests with step capture enabled)"
        )

    return results


# ---------------------------------------------------------------------------
# HTML Report Generation
# ---------------------------------------------------------------------------

def generate_html_report(case_name: str, captures_dir: str = None) -> str:
    """Generate an HTML report for a case's analysis."""
    from tools.step_capture import load_capture

    manifest = load_capture(case_name, captures_dir)
    if not manifest:
        return f"<p>No capture data found for: {case_name}</p>"

    # Load repair plan if available
    if captures_dir is None:
        captures_dir = CAPTURES_DIR
    plan_path = os.path.join(captures_dir, case_name, "repair-plan.json")
    plan = None
    if os.path.exists(plan_path):
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = json.load(f)

    # If no plan yet, run analysis first
    if not plan:
        plan = analyze_case(case_name, captures_dir)

    steps = manifest.get("steps", [])
    meta = manifest.get("metadata", {})

    html_parts = [
        "<html><head><meta charset='utf-8'>",
        "<style>",
        "body { font-family: -apple-system, sans-serif; margin: 20px; background: #f8f9fa; }",
        ".header { background: #1a1a2e; color: white; padding: 16px 24px; border-radius: 8px; margin-bottom: 20px; }",
        ".header h1 { margin: 0; font-size: 18px; }",
        ".header .meta { color: #a0a0b0; font-size: 13px; margin-top: 4px; }",
        ".step { background: white; border-radius: 8px; padding: 12px 16px; margin: 8px 0; border-left: 4px solid #4caf50; }",
        ".step.failed { border-left-color: #f44336; }",
        ".step .step-header { display: flex; justify-content: space-between; align-items: center; }",
        ".step .step-num { font-weight: 600; font-size: 14px; }",
        ".step .step-status { padding: 2px 8px; border-radius: 4px; font-size: 12px; }",
        ".step .status-passed { background: #e8f5e9; color: #2e7d32; }",
        ".step .status-failed { background: #ffebee; color: #c62828; }",
        ".step .detail { font-size: 13px; color: #666; margin-top: 6px; }",
        ".failure-analysis { background: #fff3e0; border-radius: 8px; padding: 12px 16px; margin: 8px 0; }",
        ".failure-analysis .type-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; background: #ff9800; color: white; font-size: 12px; }",
        ".repair-plan { background: #e3f2fd; border-radius: 8px; padding: 12px 16px; margin: 4px 0; }",
        ".ai-suggestion { background: #f3e8ff; border-radius: 8px; padding: 12px 16px; margin: 4px 0; border-left: 3px solid #8b5cf6; }",
        ".ai-suggestion .ai-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; background: #8b5cf6; color: white; font-size: 11px; font-weight: 600; }",
        ".ai-suggestion .ai-visual { color: #7c3aed; font-size: 12px; }",
        ".ai-suggestion .ai-delta { background: rgba(255,255,255,0.6); padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; margin-top: 4px; }",
        ".ai-suggestion .ai-analysis { color: #555; font-size: 12px; margin-top: 4px; font-style: italic; }",
        ".dom-count { font-size: 12px; color: #999; }",
        ".screenshot img { max-width: 300px; border-radius: 4px; border: 1px solid #ddd; margin: 4px 0; }",
        ".health { display: flex; gap: 12px; margin: 12px 0; }",
        ".health .stat { padding: 8px 16px; border-radius: 6px; text-align: center; }",
        ".health .ok { background: #e8f5e9; color: #2e7d32; }",
        ".health .warn { background: #fff3e0; color: #e65100; }",
        ".health .bad { background: #ffebee; color: #c62828; }",
        "</style></head><body>",
    ]

    # Header with back-to-summary nav (top-left)
    html_parts.append(f"""
    <div class='header'>
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
            <a href="../summary_report.html" style="color:#7dd3fc;text-decoration:none;font-size:13px;background:rgba(255,255,255,0.12);padding:6px 12px;border-radius:6px;white-space:nowrap;flex-shrink:0;margin-top:2px;display:inline-flex;align-items:center;gap:4px;">&#8592; Summary</a>
            <div style="min-width:0;">
                <h1>{case_name} — Step Analysis Report</h1>
                <div class='meta'>
                    {meta.get('description', '')} | YAML: {meta.get('yaml_path', 'N/A')} |
                    Steps: {len(steps)} | Result: {'PASSED' if manifest.get('test_passed') else 'FAILED'}
                </div>
            </div>
        </div>
    </div>
    """)

    # Selector health
    if plan and plan.get("selector_health"):
        sh = plan["selector_health"]
        html_parts.append(f"""
        <div class='health'>
            <div class='stat ok'>Healthy: {sh.get('healthy', 0)}</div>
            <div class='stat warn'>Risky: {sh.get('risky', 0)}</div>
            <div class='stat bad'>Broken: {sh.get('broken', 0)}</div>
        </div>
        """)

    # Steps
    for step in steps:
        status = step.get("status", "unknown")
        status_class = "failed" if status == "failed" else ""
        status_badge = f"status-{status}"
        dom_count = len(step.get("dom_snapshot", []) or [])
        screenshot_file = step.get("screenshot_file", "")

        html_parts.append(f"""
        <div class='step {status_class}'>
            <div class='step-header'>
                <span class='step-num'>Step {step['step_num']}: {step['step_key']}</span>
                <span class='step-status {status_badge}'>{status.upper()}</span>
            </div>
            <div class='detail'>
                Value: {json.dumps(step.get('step_value', {}), ensure_ascii=False)[:100]}
                <br>URL: {step.get('url', 'N/A')}
                <span class='dom-count'>| DOM elements: {dom_count}</span>
            </div>
        """)

        # Screenshot
        if screenshot_file:
            img_path = os.path.join(captures_dir or CAPTURES_DIR, case_name, screenshot_file)
            if os.path.exists(img_path):
                import base64
                with open(img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                html_parts.append(f'<div class="screenshot"><img src="data:image/jpeg;base64,{b64}" alt="Step {step["step_num"]}"></div>')

        if status == "failed" and plan:
            # Find matching failure analysis
            failure = next((f for f in plan.get("failures", [])
                          if f["step_num"] == step["step_num"]), None)
            if failure:
                html_parts.append(f"""
                <div class='failure-analysis'>
                    <span class='type-badge'>{failure['failure_type']}</span>
                    <strong>Root cause:</strong> {failure['root_cause']}
                    <br><strong>Error:</strong> {failure['error_msg'][:150]}
                </div>
                """)
                rp = failure.get("repair_plan", {})
                if rp.get("action") != "manual_review":
                    html_parts.append(f"""
                    <div class='repair-plan'>
                        <strong>Repair:</strong> {rp['action']} | Confidence: {rp.get('confidence', 0):.0%}
                        <br>Delta: <code>{json.dumps(rp.get('delta', {}), ensure_ascii=False)}</code>
                    </div>
                    """)
                # AI suggestion
                if rp.get("ai_suggestion"):
                    ai_delta = json.dumps(rp.get("ai_suggestion", {}), ensure_ascii=False)
                    visual_tag = "🖼️ Visual+Semantic" if rp.get("ai_has_visual") else "📝 Text-only"
                    html_parts.append(f"""
                    <div class='ai-suggestion'>
                        <span class='ai-badge'>AI Suggestion</span>
                        <span class='ai-visual'>{visual_tag}</span>
                        <span style="font-size:12px;color:#666;margin-left:8px;">Confidence: {rp.get('ai_confidence', 0):.0%}</span>
                        <div class='ai-delta'>{ai_delta}</div>
                        <div class='ai-analysis'>{rp.get('ai_analysis', '')}</div>
                    </div>
                    """)
                elif rp.get("ai_error"):
                    # Distinguish API error vs AI analysis with no match
                    ai_err = rp.get("ai_error", "")
                    is_api_error = any(kw in ai_err.lower() for kw in
                        ["api unavailable", "quota", "503", "429", "region", "not configured", "all api keys"])
                    if is_api_error:
                        html_parts.append(f"""
                    <div class='ai-suggestion' style="background:#fef3c7;border-left-color:#f59e0b;">
                        <span class='ai-badge' style="background:#f59e0b;">AI Unavailable</span>
                        <span style="font-size:12px;color:#92400e;">{ai_err}</span>
                    </div>
                    """)
                    else:
                        # AI analyzed but couldn't find a confident match — show its reasoning
                        html_parts.append(f"""
                    <div class='ai-suggestion' style="background:#eff6ff;border-left-color:#3b82f6;">
                        <span class='ai-badge' style="background:#3b82f6;">AI Analysis</span>
                        <span style="font-size:12px;color:#1e40af;">No confident fix found</span>
                        <div style="font-size:12px;color:#555;margin-top:4px;">{ai_err}</div>
                    </div>
                    """)

        html_parts.append("</div>")

    html_parts.append("</body></html>")
    return "".join(html_parts)


def generate_summary_report(results: List[Dict], captures_dir: str = None) -> str:
    """Generate a summary HTML report for all analyzed failed cases."""
    if captures_dir is None:
        captures_dir = CAPTURES_DIR

    html_parts = ["""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Failure Analysis Summary</title>
<style>
  body { font-family: system-ui, -apple-system, sans-serif; margin: 20px; background: #fafafa; color: #333; }
  h1 { font-size: 18px; color: #1a1a1a; border-bottom: 2px solid #e24b4a; padding-bottom: 8px; }
  .summary { background: #fff; border-radius: 8px; padding: 16px; margin: 12px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .stats { display: flex; gap: 24px; margin-bottom: 16px; }
  .stat { text-align: center; }
  .stat .num { font-size: 28px; font-weight: 700; }
  .stat .label { font-size: 12px; color: #888; }
  .case-card { background: #fff; border-radius: 8px; padding: 16px; margin: 8px 0; border-left: 4px solid #e24b4a; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
  .case-card.pasSED { border-left-color: #22c55e; }
  .case-name { font-weight: 600; font-size: 14px; margin-bottom: 8px; }
  .failure-row { display: flex; gap: 12px; align-items: center; padding: 4px 0; font-size: 13px; }
  .type-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; color: #fff; }
  .type-selector_broken { background: #ef4444; }
  .type-selector_ambiguous { background: #f97316; }
  .type-element_obscured { background: #eab308; color: #333; }
  .type-timeout { background: #8b5cf6; }
  .type-auth_expired { background: #ec4899; }
  .type-api_error { background: #6366f1; }
  .type-navigation_error { background: #14b8a6; }
  .type-data_stale { background: #64748b; }
  .confidence { font-size: 12px; color: #888; }
  .repair { background: #f0fdf4; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-top: 4px; }
  .repair.manual { background: #fef3c7; }
  .link { color: #3b82f6; text-decoration: none; font-size: 12px; }
  .link:hover { text-decoration: underline; }
  /* AI status badges */
  .ai-badge { display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; margin-left: 6px; vertical-align: middle; }
  .ai-ok { background: #ede9fe; color: #7c3aed; }
  .ai-none { background: #fef2f2; color: #dc2626; }
</style></head><body>
<h1>Failure Analysis Summary</h1>
"""]

    # Stats
    total_cases = len(results)
    total_failures = sum(len(r.get("failures", [])) for r in results)
    high_conf = sum(1 for r in results for f in r.get("failures", [])
                    if f.get("repair_plan", {}).get("confidence", 0) >= 0.7)
    html_parts.append(f"""
<div class="summary">
  <div class="stats">
    <div class="stat"><div class="num" style="color:#e24b4a">{total_cases}</div><div class="label">Failed cases</div></div>
    <div class="stat"><div class="num">{total_failures}</div><div class="label">Total failures</div></div>
    <div class="stat"><div class="num" style="color:#22c55e">{high_conf}</div><div class="label">High-confidence fixes</div></div>
  </div>
</div>
""")

    # Per-case cards
    for result in results:
        case_name = result.get("case_name", "unknown")
        failures = result.get("failures", [])
        detail_path = os.path.join(captures_dir, case_name, "analysis_report.html")
        detail_link = f"./{case_name}/analysis_report.html" if os.path.exists(detail_path) else ""

        html_parts.append(f'<div class="case-card">')
        # Check AI suggestion status across all failures
        has_ai = any(f.get("repair_plan", {}).get("ai_suggestion") for f in failures)
        ai_badge = '<span class="ai-badge ai-ok">AI OK</span>' if has_ai else '<span class="ai-badge ai-none">No AI</span>'
        html_parts.append(f'<div class="case-name">{case_name} ({len(failures)} failure{"s" if len(failures) != 1 else ""}) {ai_badge}')
        if detail_link:
            html_parts.append(f' <a class="link" href="{detail_link}">detail</a>')
        html_parts.append('</div>')

        for f in failures:
            ft = f.get("failure_type", "unknown")
            step_num = f.get("step_num", "?")
            step_key = f.get("step_key", "?")
            root_cause = f.get("root_cause", "")[:120]
            rp = f.get("repair_plan", {})
            conf = rp.get("confidence", 0)
            action = rp.get("action", "manual_review")

            html_parts.append(f"""
<div class="failure-row">
  <span class="type-badge type-{ft}">{ft}</span>
  <span>Step {step_num} ({step_key})</span>
  <span style="color:#666">{root_cause}</span>
  <span class="confidence">{conf:.0%}</span>
</div>""")
            if action != "manual_review":
                delta = json.dumps(rp.get("delta", {}), ensure_ascii=False)
                html_parts.append(f'<div class="repair">{action}: <code>{delta}</code></div>')
            else:
                html_parts.append(f'<div class="repair manual">Needs manual review</div>')

        html_parts.append('</div>')

    html_parts.append("</body></html>")
    return "".join(html_parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Step-level test analysis (offline)")
    sub = parser.add_subparsers(dest="command")

    # list
    sub_list = sub.add_parser("list", help="List available step captures")
    sub_list.add_argument("--captures-dir", default=None, help="Custom captures directory")

    # analyze
    sub_analyze = sub.add_parser("analyze", help="Analyze failed steps")
    sub_analyze.add_argument("--case", help="Specific case name to analyze")
    sub_analyze.add_argument("--all-failed", action="store_true",
                             help="Analyze all failed cases from step_captures (legacy)")
    sub_analyze.add_argument("--from-report", action="store_true",
                             help="Analyze only cases that are failed/broken in the latest Allure report")
    sub_analyze.add_argument("--allure-dir", type=str, default=None,
                             help="Specific Allure results dir name (e.g. 20260618_144200)")
    sub_analyze.add_argument("--captures-dir", default=None, help="Custom captures directory")

    # report
    sub_report = sub.add_parser("report", help="Generate HTML report")
    sub_report.add_argument("--case", required=True, help="Case name")
    sub_report.add_argument("--output", default=None, help="Output HTML path")
    sub_report.add_argument("--captures-dir", default=None, help="Custom captures directory")

    args = parser.parse_args()

    # Add project root to path for imports
    sys.path.insert(0, PROJECT_ROOT)

    if args.command == "list":
        from tools.step_capture import list_captures
        captures = list_captures(args.captures_dir)
        if not captures:
            print("No captures found.")
        for c in captures:
            status = "PASSED" if c.get("test_passed") else "FAILED"
            failed = c.get("failed_steps", [])
            print(f"  {c['case_name']:40s} {status:8s} steps={c.get('total_steps', 0)} failed={len(failed)} {c.get('capture_time', '')}")

    elif args.command == "analyze":
        if args.case:
            result = analyze_case(args.case, args.captures_dir)
            if result:
                for f in result.get("failures", []):
                    print(f"\n  Step {f['step_num']} ({f['step_key']}): [{f['failure_type']}] {f['root_cause']}")
                    rp = f.get("repair_plan", {})
                    if rp.get("action") != "manual_review":
                        print(f"    Repair: {rp['action']} delta={json.dumps(rp.get('delta', {}), ensure_ascii=False)} confidence={rp.get('confidence', 0):.0%}")
                sh = result.get("selector_health", {})
                print(f"\n  Selector health: {sh.get('healthy', 0)} ok / {sh.get('risky', 0)} risky / {sh.get('broken', 0)} broken")
        elif args.from_report:
            # Use specific allure dir or find latest
            allure_dir = None
            if args.allure_dir:
                allure_dir = os.path.join(ALLURE_RESULTS_DIR, args.allure_dir)
            failed_names = get_failed_cases_from_report(allure_dir)
            if not failed_names:
                print("No failed/broken cases found in Allure report.")
                if not allure_dir:
                    latest = find_latest_allure_dir()
                    if latest:
                        print(f"  Latest report dir: {latest}")
                    else:
                        print("  No Allure results found at all.")
                sys.exit(0)

            # Cross-reference with captures
            from tools.step_capture import list_captures
            captures_list = list_captures(args.captures_dir)
            capture_map = {c["case_name"]: c for c in captures_list}
            to_analyze = []
            for name in failed_names:
                cap = capture_map.get(name)
                if not cap:
                    print(f"  [SKIP] {name} — no step capture data (need to re-run)")
                    continue
                if cap.get("test_passed", True):
                    print(f"  [SKIP] {name} — capture shows PASSED (stale data?)")
                    continue
                to_analyze.append(name)

            if not to_analyze:
                print("\nNone of the reported failures have matching capture data.")
                print("Re-run the test suite with step capture enabled, then retry.")
                sys.exit(0)

            print(f"\nAnalyzing {len(to_analyze)} case(s) with capture data...")
            results = []
            for name in to_analyze:
                print(f"\n{'='*60}")
                print(f"Analyzing: {name}")
                result = analyze_case(name, args.captures_dir)
                if result:
                    results.append(result)
                    for f in result.get("failures", []):
                        print(f"  Step {f['step_num']} ({f['step_key']}): [{f['failure_type']}] {f['root_cause']}")

            # Generate per-case HTML + summary
            captures_dir = args.captures_dir or CAPTURES_DIR
            for result in results:
                case_name = result.get("case_name", "unknown")
                html = generate_html_report(case_name, args.captures_dir)
                output_path = os.path.join(captures_dir, case_name, "analysis_report.html")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"  Report: {output_path}")
            if results:
                try:
                    summary_html = generate_summary_report(results, captures_dir)
                    summary_path = os.path.join(captures_dir, "summary_report.html")
                    with open(summary_path, "w", encoding="utf-8") as f:
                        f.write(summary_html)
                    print(f"\n  Summary: {summary_path}")
                except Exception as e_summ:
                    print(f"\n  [WARN] Summary report failed: {str(e_summ)[:80]}")

        elif args.all_failed:
            results = analyze_all_failed(args.captures_dir)
            print(f"\nAnalyzed {len(results)} failed cases")
            # Generate per-case HTML reports
            captures_dir = args.captures_dir or CAPTURES_DIR
            for result in results:
                case_name = result.get("case_name", "unknown")
                html = generate_html_report(case_name, args.captures_dir)
                output_path = os.path.join(captures_dir, case_name, "analysis_report.html")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"  Report: {output_path}")
            # Generate summary report
            if results:
                try:
                    summary_html = generate_summary_report(results, captures_dir)
                    summary_path = os.path.join(captures_dir, "summary_report.html")
                    with open(summary_path, "w", encoding="utf-8") as f:
                        f.write(summary_html)
                    print(f"\n  Summary: {summary_path}")
                except Exception as e_summ:
                    print(f"\n  [WARN] Summary report failed: {str(e_summ)[:80]}")
        else:
            print("Specify --case or --all-failed")

    elif args.command == "report":
        html = generate_html_report(args.case, args.captures_dir)
        output_path = args.output
        if not output_path:
            output_dir = os.path.join(args.captures_dir or CAPTURES_DIR, args.case)
            output_path = os.path.join(output_dir, "analysis_report.html")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Report saved to {output_path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
