"""
step_capture.py - In-test step-level capture module

Captures screenshot + DOM snapshot after each interactive step
DIRECTLY inside pytest execution — no replay engine needed.

Data format (per step):
{
    "step_num": 3,
    "step_key": "R_click",
    "step_value": {"name": "Scan", "role": "button"},
    "status": "passed",
    "url": "https://release.pear.us/events",
    "screenshot_b64": "...",       # base64 PNG (only if configured)
    "dom_snapshot": [              # extracted interactive elements
        {"key": "button|Scan", "tag": "button", "role": "button", ...},
    ],
    "dom_raw": "<html>...</html>", # full page HTML (only if configured)
    "timestamp": "2026-06-05T14:30:00",
    "error_msg": null
}

Usage in conftest.py / test_ui.py:
    from tools.step_capture import StepCapture

    capture = StepCapture(case_name="testT3981_Concurrency_01")
    capture.step_start(step_key, step_value)
    # ... execute step ...
    capture.step_end(page, status="passed", error_msg=None)
    # After test:
    capture.finalize(test_passed=True)

CLI option:
    --step-capture on|on-failure|off   (default: on-failure)
"""

import base64
import json
import os
import sys
import time
import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

# Reuse the same JS extraction snippet from ui_snapshot
JS_EXTRACT_INTERACTIVE = """
() => {
    const SELECTORS = [
        'button',
        'a',
        '[role="menuitem"]',
        '[role="tab"]',
        '[role="dialog"]',
        '[role="option"]',
        '[role="listbox"]',
        '[role="combobox"]',
        'input',
        'select',
        'textarea',
        '[data-testid]',
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
                name:       (el.getAttribute('aria-label') || el.innerText || '').trim().substring(0, 80),
                testid:     el.getAttribute('data-testid') || '',
                type:       el.getAttribute('type') || '',
                placeholder: el.getAttribute('placeholder') || '',
                text:       (el.innerText || '').trim().substring(0, 80),
                href:       el.getAttribute('href') || '',
                className:  (el.className || '').substring(0, 60),
            };
            const key = entry.testid || (entry.role + '|' + (entry.name || entry.text || ''));
            if (key) results.push({ key: key, ...entry });
        });
    });
    return results;
}
"""

# Steps that are NOT interactive — skip capture for these
SKIP_CAPTURE_KEYS = {"sleep", "wait", "smart_sleep", "smart_wait",
                     "wait_for_selector", "wait_for_url", "wait_toast",
                     "screenshot", "save_html", "add_cookies", "clear_cookies",
                     "scroll", "page_scroll", "scroll_tab_content", "scroll_to_bottom"}


class StepCapture:
    """Captures step-level data during test execution."""

    def __init__(self, case_name: str, output_dir: str = None,
                 capture_screenshot: bool = True,
                 capture_dom_raw: bool = False,
                 max_screenshot_kb: int = 200,
                 screenshot_mode: str = "always"):
        """
        Args:
            case_name: Test case identifier (e.g. "testT3981_Concurrency_01")
            output_dir: Base directory for captures (default: step_captures/ under project root)
            capture_screenshot: Whether to capture screenshots at all
            capture_dom_raw: Whether to capture full page HTML (can be large)
            max_screenshot_kb: Max screenshot size in KB (resize if larger)
            screenshot_mode: "always" — capture every step (for "on" mode)
                             "on-failure" — only capture screenshots for failed steps
        """
        self.case_name = case_name
        self.capture_screenshot = capture_screenshot
        self.capture_dom_raw = capture_dom_raw
        self.max_screenshot_kb = max_screenshot_kb
        self.screenshot_mode = screenshot_mode

        if output_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(project_root, "step_captures")
        self.output_dir = output_dir
        self.case_dir = os.path.join(output_dir, case_name)

        self._steps: List[Dict] = []
        self._step_num = 0
        self._current_step: Optional[Dict] = None

    @staticmethod
    def should_capture(step_key: str) -> bool:
        """Check if this step type should be captured."""
        # Normalize: strip session prefix
        key = step_key
        if key.startswith("session_") and "__" in key:
            key = key.split("__", 1)[1]

        key_lower = key.lower()
        for skip in SKIP_CAPTURE_KEYS:
            if key_lower.startswith(skip.lower()):
                return False
        return True

    def step_start(self, step_key: str, step_value: Any):
        """Mark the beginning of a step. Call BEFORE execution."""
        self._step_num += 1
        self._current_step = {
            "step_num": self._step_num,
            "step_key": step_key,
            "step_value": step_value if isinstance(step_value, (str, int, float, bool, type(None))) else dict(step_value) if isinstance(step_value, dict) else str(step_value),
            "status": "running",
            "url": None,
            "screenshot_b64": None,
            "dom_snapshot": None,
            "dom_raw": None,
            "timestamp": datetime.datetime.now().isoformat(),
            "error_msg": None,
        }

    def step_end(self, page, status: str = "passed", error_msg: str = None):
        """Capture page state AFTER step execution. Call AFTER execution (success or failure).

        Args:
            page: Playwright Page object (or session page)
            status: "passed" or "failed"
            error_msg: Exception message if failed
        """
        if self._current_step is None:
            return

        self._current_step["status"] = status
        self._current_step["error_msg"] = error_msg

        try:
            self._current_step["url"] = page.url
        except Exception:
            pass

        # Capture DOM interactive elements (always — lightweight, ~5-20KB)
        try:
            dom_elements = page.evaluate(JS_EXTRACT_INTERACTIVE)
            if dom_elements and isinstance(dom_elements, list):
                self._current_step["dom_snapshot"] = dom_elements
        except Exception as e:
            logger.debug(f"step_capture: DOM extract failed: {e}")

        # Capture screenshot (optional, ~50-200KB base64)
        # In "on-failure" screenshot_mode, only capture for failed steps
        should_screenshot = self.capture_screenshot
        if self.screenshot_mode == "on-failure" and status != "failed":
            should_screenshot = False
        if should_screenshot:
            try:
                screenshot_bytes = page.screenshot(type="jpeg", quality=60)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("ascii")
                size_kb = len(screenshot_b64) / 1024
                if size_kb > self.max_screenshot_kb:
                    # Too large — skip base64, save to file instead
                    self._current_step["screenshot_b64"] = None
                    self._current_step["screenshot_file"] = f"step_{self._step_num:03d}.jpg"
                else:
                    self._current_step["screenshot_b64"] = screenshot_b64
            except Exception as e:
                logger.debug(f"step_capture: screenshot failed: {e}")

        # Capture raw DOM (optional, can be very large)
        if self.capture_dom_raw:
            try:
                self._current_step["dom_raw"] = page.content()
            except Exception as e:
                logger.debug(f"step_capture: raw DOM failed: {e}")

        self._steps.append(self._current_step)
        self._current_step = None

    def finalize(self, test_passed: bool, case_metadata: Dict = None):
        """Write all captured data to disk. Call at test end.

        Args:
            test_passed: Whether the overall test passed
            case_metadata: Optional dict with case-level info (description, yaml_path, etc.)
        """
        if not self._steps:
            return

        os.makedirs(self.case_dir, exist_ok=True)

        # Save per-step screenshots as files (more efficient than base64)
        for step in self._steps:
            if step.get("screenshot_b64") and len(step.get("screenshot_b64", "")) > 1000:
                # Save large screenshots as files
                step_num = step["step_num"]
                img_path = os.path.join(self.case_dir, f"step_{step_num:03d}.jpg")
                try:
                    with open(img_path, "wb") as f:
                        f.write(base64.b64decode(step["screenshot_b64"]))
                    # Replace b64 with file reference
                    step["screenshot_file"] = f"step_{step_num:03d}.jpg"
                    step["screenshot_b64"] = None  # Free memory
                except Exception as e:
                    logger.debug(f"step_capture: save screenshot file failed: {e}")

        # Build manifest
        manifest = {
            "case_name": self.case_name,
            "test_passed": test_passed,
            "total_steps": len(self._steps),
            "failed_steps": [s["step_num"] for s in self._steps if s["status"] == "failed"],
            "capture_time": datetime.datetime.now().isoformat(),
            "metadata": case_metadata or {},
            "steps": self._steps,
        }

        manifest_path = os.path.join(self.case_dir, "manifest.json")
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            logger.info(f"step_capture: saved {len(self._steps)} steps to {self.case_dir}")
        except Exception as e:
            logger.error(f"step_capture: save manifest failed: {e}")

        return manifest_path

    def get_failed_step_data(self) -> List[Dict]:
        """Return data for failed steps only. Useful for on-failure analysis."""
        return [s for s in self._steps if s["status"] == "failed"]

    def get_step(self, step_num: int) -> Optional[Dict]:
        """Get data for a specific step number."""
        for s in self._steps:
            if s["step_num"] == step_num:
                return s
        return None


# ---------------------------------------------------------------------------
# Standalone utilities for reading captured data
# ---------------------------------------------------------------------------

def load_capture(case_name: str, captures_dir: str = None) -> Optional[Dict]:
    """Load a captured manifest by case name."""
    if captures_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        captures_dir = os.path.join(project_root, "step_captures")
    manifest_path = os.path.join(captures_dir, case_name, "manifest.json")
    if not os.path.exists(manifest_path):
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_captures(captures_dir: str = None) -> List[Dict]:
    """List all available captures with summary info."""
    if captures_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        captures_dir = os.path.join(project_root, "step_captures")
    if not os.path.isdir(captures_dir):
        return []
    results = []
    for case_dir in os.listdir(captures_dir):
        manifest_path = os.path.join(captures_dir, case_dir, "manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    m = json.load(f)
                results.append({
                    "case_name": m.get("case_name", case_dir),
                    "test_passed": m.get("test_passed", None),
                    "total_steps": m.get("total_steps", 0),
                    "failed_steps": m.get("failed_steps", []),
                    "capture_time": m.get("capture_time", ""),
                })
            except Exception:
                pass
    return results
