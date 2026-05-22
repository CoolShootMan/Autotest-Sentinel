import os
path = r"C:\Users\tester\.workbuddy\plans\blazing-pulse-lovelace.md"
os.makedirs(os.path.dirname(path), exist_ok=True)
lines = []
lines.append('# Autotest-monster Project Exploration Report')

> Task: Pure exploration - no code changes
> Project: d:\monster_test\Autotest-monster\\

> Date: 2026-05-21

---

## 1. YAML Test Case Format

File: Post_setting.yaml (2600+ lines)

### 1.1 Test Case Level Schema

- Case ID (YAML key): testT5033_5034_VerifyPartner
- description [required]: Human-readable purpose
- guest [optional bool]: Guest mode, default false
- is_coseller [optional bool]: Co-seller mode flag
- pre_condition [optional dict]: Pre-condition steps
- test_step [required dict]: Core steps
- expect_result [required dict]: description + assertions array
- teardown_step [optional dict]: Cleanup steps

Full Example: testT5033_5034_VerifyPartner at lines 1725-1836

### 1.2 Step Schema - Two Forms

Form A (simple): open=URL string, sleep_N=null, swipe_up=null
Form B (dict): role/name/type/placeholder/value/index/skip_if_disabled

### 1.3 Step Types (~25 prefix families)

R_click/click/l_click -> smart_click() AI fallback scan
smart_click_optional -> silent skip if missing
smart_click_retry -> retry N times
fill -> smart_fill()
check/uncheck -> smart_check()
verify -> verify_text_visible()
wait_toast -> wait_toast()
wait_ -> smart_wait()
open* -> open_url() with cookie_file support
sleep_* -> smart_sleep()
swipe/page_scroll -> swipe_avoid_plus()
session management: create/switch/close_session
handle_modal/if_/execute_js/drag_element/delete_coseller_if_exists

Dispatch: actions/__init__.py get_action() L218-340
Phase 1: Exact match in ACTIONS dict L98-215
Phase 2: Prefix fallback matching

### 1.4 expect_result Format

7 assertion types:
element_visible_by_text(text)
element_visible(role+name|locator)
element_visible_by_locator(locator)
element_not_visible / element_not_visible_by_text
element_checked / element_not_checked(role+name)
Execution: test_ui.py L190-310

### 1.5 cookie_file Patterns

Pattern 1 (inline, L384/2404/2441): open: {url, cookie_file}
Pattern 2 (multi-line): open_post: {url, cookie_file}
Injection: base.py open_url() L65-73 -> _inject_cookies L2660-2683
Supports {ENV} runtime placeholder

---

## 2. Allure Report Structure

Directory: allure-results/ (latest: 20260521_145529, 272 files)

*-result.json ~72: per-test-case result with uuid/name/status/steps/parameters/statusDetails/attachments
*-container.json ~136: container with children UUIDs + befores/afters fixtures
*.png/*.webm ~32 each: failure screenshots and recordings

Status values: passed/failed/broken/skipped
Error info: message(~120 chars) + trace(~9000 chars) in statusDetails
Step nesting: test_step > action > sub-action

---

## 3. tools/allure_summary.py (220 lines)

parse_results() L54-75: glob result JSONs -> extract name/status/message[:120]
print_summary() L80-107: console table with counts
annotate_yaml() L117-158: write #[LAST: STATUS date] to YAML files
Default YAMLs L164-171: 6 files including Post_setting.yaml
Supplementary: parse_allure_status.py for ONES integration with T-number splitting

---

## 4. tools/ui_snapshot.py DOM Snapshot (559 lines)

JS_EXTRACT L70-112: Extract key/tag/role/ariaLabel/name/testid/type/placeholder/text
Targets: button,a,[role=*],input,select,[data-testid]
Filter hidden elements
9 monitored URLs: events,autotestshop,catalog,dashboard,post/create,events/create,events/settings,collabs,shop

API: take_snapshot(L181), save_snapshot(L274), load_latest(L285), diff_snapshots(L313), find_affected_yaml(L361)
Storage: ui_snapshots/{label}__{env}__{timestamp}.json
Structure: {urls:{template:[elements]}, env, account, base_url, cookie, timestamp}

---

## 5. Key File Index

| File | Lines | Role |
| Post_setting.yaml | 1-2600+ | YAML definitions |
| test_ui.py | 1-330 | Execution engine |
| actions/__init__.py | 98-340 | Registry + dispatch |
| actions/base.py | 65-73,430-660,2660-2683 | Implementations |
| allure_summary.py | 54-158 | Allure parser + annotation |
| parse_allure_status.py | 1-235 | ONES integration |
| ui_snapshot.py | 70-112,181,313 | DOM snapshot tool |

---

## 6. Call Chain

YAML -> pytest -> test_ui.py -> get_action() -> base.py handlers -> assertions -> teardown -> Allure -> summary annotate
