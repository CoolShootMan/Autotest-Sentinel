# Auto Test Framework v4.3

> UI Automation Testing with AI Self-Healing using Python + Pytest + Playwright + Allure + Gemini Vision AI

English | [简体中文](./README.md)

---

## ✨ Features

- **Keyword-Driven Testing**: Define test cases in YAML — no coding required
- **Action Registry Pattern**: Modular action registry supporting team collaboration
- **AI Self-Healing**: When traditional locators fail, Gemini Vision AI automatically identifies and repairs element targeting
- **RAG Knowledge Base**: FAISS + SentenceTransformers powered domain knowledge retrieval for AI context
- **Execution History Tracking**: Records successful steps to provide AI with current test flow state
- **Multi-Environment Support**: Switch between staging/release via `--env` parameter
- **Dynamic Assertions**: Multiple assertion types (text visibility, element existence, visual height, etc.)
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Failed Case Diagnosis**: Auto-replay failed cases with screenshots + DOM snapshots + multi-strategy probing, generates HTML diagnosis reports
- **Fast Startup**: AI modules disabled by default, startup time reduced from ~20s to ~0.6s, enable on demand

---

## 💻 System Requirements

- **Python:** 3.9+ (recommended 3.10+)
- **Operating System:** Windows 10+, macOS 11+, or mainstream Linux distributions
- **Browser:** Chromium (automatically installed by Playwright)
- **Memory:** 8GB+ RAM recommended
- **Disk Space:** At least 2GB free space

---

## 🚀 Quick Start

### 1. Environment Setup (Automated)

This project supports cross-platform one-click deployment. The script automatically detects your OS, creates a suitable virtual environment, and installs all dependencies (including Playwright browsers).

**macOS/Linux:**
```bash
./setup_env.sh
```

**Windows:**
```bash
setup_env.bat
```
*(Note: If you prefer to set up the environment manually, see the [Environment Management](#environment-management) section below.)*

### 2. Environment Configuration (`.env` File)

After cloning the project, create a `.env` file in the project **root** directory. A template is provided — just copy and edit it:

```bash
cp .env.example .env   # macOS/Linux
copy .env.example .env  # Windows
```

The `.env` file contains two configuration sections:

#### 2-1. Test Environment (`BASE_URL`)

`BASE_URL` controls which environment your tests run against, and **simultaneously** governs three things:

| Scope | Description |
|-------|-------------|
| `{BASE_URL}` placeholder | Domain substitution in YAML test cases |
| Cookie file | Auto-matches the corresponding `cookie_<env>.json` (e.g. `cookie_release.json`) |
| `{ENV}` placeholder | Environment name substitution in YAML files |

Available values:

```env
BASE_URL=https://staging.pear.us    # Development environment
BASE_URL=https://release.pear.us    # Test/Staging environment (default)
BASE_URL=https://pear.us            # Production environment
```

> **💡 Tip**: If `BASE_URL` is not set, the framework defaults to the `release` environment (`https://release.pear.us`).  
> You can temporarily override the `.env` value via the CLI flag `--env staging`.

#### 2-2. Gemini AI Keys (`GEMINI_API_KEYS`)

Configure Gemini API Keys for AI self-healing. Multiple keys are supported for automatic rotation to avoid rate limits:

```env
# Recommended: multiple keys, comma-separated — the framework rotates them automatically
GEMINI_API_KEYS=key1,key2,key3

# Or a single key (legacy support)
GEMINI_API_KEY=your_single_key_here
```

> **⚠️ Note**: The `.env` file contains sensitive credentials. It is listed in `.gitignore` — **never commit it to the repository**.

#### 2-3. AI Vision Toggle (`ENABLE_AI_VISION`)

AI self-healing (Gemini Vision + RAG Knowledge Base) is **disabled by default** to avoid loading ~20s of models on every run. Enable it when needed:

```env
ENABLE_AI_VISION=1
```

> **💡 Tip**: No need to enable AI for daily debugging and test runs. Only turn it on when locators frequently fail and you need AI self-healing. With AI disabled, all python/pytest commands start in ~0.6s.

### 3. Run Tests

The recommended way to run tests is via the `runner.py` intelligent launcher:

```bash
# Interactive mode: terminal shows a hierarchical menu, navigate into directories,
# select specific YAML files, or run all tests in a directory with one keypress!
python runner.py
```

### 4. Record Test Scripts (Codegen)

This project provides `codegen.py` and `codegen.sh` to quickly launch the Playwright recording tool, automatically loading the corresponding login cookie based on role and environment — so you never have to log in manually during recording.

**Usage:**
```bash
# Using the Python script (recommended)
./codegen.py

# Or using the Shell script
./codegen.sh
```

**Interactive recording workflow:**
1. **Select Role**: Supports `partner`, `guest`, `co-seller`. Selecting `guest` loads no cookie.
2. **Select Environment**: Supports `staging`, `release`, `prod`. The tool automatically looks for files like `cookie_release.json` or `cookie_coseller_prod.json` and loads them.
3. **Enter URL**: Input the page URL you want to jump directly to for recording (press Enter to skip and start from a blank page).
*(Tip: Enter `q` or press `Ctrl+C` at any prompt to exit safely.)*

### 5. View Test Reports

After test execution completes, an Allure report is automatically generated and opened.

---

## 📖 Detailed Usage Guide

### Test Execution & Common Commands

In addition to the interactive `runner.py`, you can also pass arguments directly via the command line or use raw pytest commands.

**Using `runner.py` shortcuts:**
```bash
# Run a single test case (--headed -v by default)
python runner.py testT4718

# Run multiple test cases (OR logic by default)
python runner.py testT4718 testT4718_guest

# Pass extra pytest arguments (e.g. headless mode, environment override)
python runner.py testT4718 --headless --env release
```
> **💡 Tip:** When executing an entire file or directory, `runner.py` automatically parses the YAML to extract each individual `testTxxxx` test case and runs them **one by one**. If one case fails, it does **not** interrupt the others.

**Using raw `pytest` commands:**
```bash
# Test a specific case
pytest test_case/UI/Test_Katana/test_ui.py -k testT3554 --yaml All_YAML/Module/Module.yaml --headed -v --env release

# Test multiple cases
pytest test_case/UI/Test_Katana/test_ui.py -k "testT3554 or testT4660" --yaml All_YAML/Module/Module.yaml --headed -v

# Generate Allure report
pytest --alluredir=allure-results test_case/UI/Test_Katana/test_ui.py
allure serve allure-results
```

### Test Parameters

| Parameter | Description | Example |
| --------- | ----------- | ------- |
| `-k` | Filter tests by name | `-k testT3554` |
| `-v` / `-vv` | Verbose / extra verbose output | `-vv` |
| `-s` | Show print output | `-s` |
| `--headed` | Show browser window | `--headed` |
| `--headless` | Headless mode | `--headless` |
| `--storage-state` | Use saved session | `--storage-state cookie.json` |
| `--env` | Specify environment | `--env release` or `staging` |
| `--yaml` | Specify config file | `--yaml config.yaml` |

### Environment Management

For manual intervention, environment rebuilds, or cross-platform migrations:

```bash
# 1. Activate / Deactivate virtual environment
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate.bat   # Windows
deactivate                  # Deactivate

# 2. Rebuild environment (use when switching platforms or environment is broken)
rm -rf venv && ./setup_env.sh          # macOS/Linux
rmdir /s venv && setup_env.bat         # Windows

# 3. Manual dependency & browser installation (if not using the setup script)
python3 -m venv venv                   # Create virtual environment
pip install -r requirements.txt        # Install dependencies
playwright install                      # Install browsers
```

---

## 🧠 Architecture & Core Mechanisms

### Architecture Overview

```
YAML Test Definitions
    ↓
test_ui.py (Step Dispatcher + Execution History Tracker)
    ↓
actions/ (Action Registry)
    ├── base.py → smart_click / smart_fill (with AI Fallback)
    ├── module.py / product.py / form.py ...
    ↓
┌─ Traditional Playwright Locators (role/text/locator)
│   Success → Continue
│   Failure ↓
└─ AI Self-Healing Engine (utils/ai_vision.py)  ← Disabled by default; set ENABLE_AI_VISION=1
       ├── Screenshot + SOM Overlay
       ├── RAG Knowledge Base Query (utils/rag_knowledge.py)
       ├── Execution History Context Injection
       └── Gemini Vision Analysis → Target Element ID
              ↓
         Healed Action Continues
              ↓
         Allure Report + Screenshots/Recordings
              ↓
    [Failed Cases] → diagnose_failed.py → Replay + Screenshots + DOM + Multi-Strategy Probing → HTML Report
```

### V4.0 AI Self-Healing Deep Dive

1. **Execution Strategy**: `smart_click` first attempts traditional Playwright locators (role/name/text).
2. **Fallback Mechanism**: If timeout after 5s, triggers Legacy Fallback (15s grace period).
3. **AI Intervention**: If still failing, triggers **AI Self-Healing**:
   - Screenshots the current page and injects **SOM (Set-of-Mark)** overlays.
   - Queries the **RAG Knowledge Base** (`utils/Knowledge_Base.md`) for system business rules and navigation patterns.
   - Sends the screenshot, target description, execution history, and RAG knowledge to Gemini Vision.
   - AI returns the diagnosis and target element ID; the framework completes the operation.
4. **Knowledge Evolution**: When AI makes incorrect decisions, engineers can add business rules to `Knowledge_Base.md`. The AI will automatically retrieve and learn from them on the next run.

---

## 📂 Directory Structure

```shell
├─config
│  └─config.yaml          # Configuration file
├─page
│  └─home.py              # UI layer base encapsulation
├─recordings              # Playwright codegen recorded scripts
├─test_case
│  └─UI
│    └─Test_Katana
│       ├─actions/         # Action Registry
│       │  ├─__init__.py   # Registry entry point
│       │  ├─base.py       # Base actions (smart_click, smart_fill, AI Fallback)
│       │  └─...           # Domain-specific action modules
│       ├─utils/           # [NEW v4.0] AI Self-Healing Toolkit
│       │  ├─ai_vision.py  # Gemini Vision AI Service (SOM + Multi API Key Rotation)
│       │  ├─rag_knowledge.py  # RAG Knowledge Base (FAISS + SentenceTransformers)
│       │  └─Knowledge_Base.md # Domain Knowledge Document
│       ├─conftest.py      # Pytest fixtures (multi-env + auth)
│       ├─test_ui.py       # Core test execution engine (with execution history)
│       └─*.yaml           # Test case definitions
├─tools                    # Utilities
│  ├─diagnose_failed.py    # [NEW v4.3] Failed test case diagnosis report tool
│  ├─ui_snapshot.py        # DOM snapshot + diff detection
│  ├─locator_updater.py    # YAML locator batch update tool
│  └─...                   # Other utility scripts
├─requirements.txt         # Project core dependencies (pytest, playwright, allure, FAISS, Gemini, etc.)
├─setup_env.sh / .bat      # Cross-platform one-click environment setup script
└─main.py                  # Main entry point
```

---

## 💡 Best Practices

1. **Environment Isolation**: Always activate the virtual environment before running tests or developing.
2. **Debugging**: Use `--headed` mode for visual debugging when tests fail or when writing new cases.
3. **CI/CD**: Ensure all smoke tests pass before committing code.
4. **Knowledge Accumulation**: When AI locators misbehave or you encounter special business components, update `Knowledge_Base.md` promptly for true "self-healing evolution."
5. **Dependency Updates**: Regularly update dependencies and test compatibility (`pip install --upgrade -r requirements.txt`).

---

## 🔧 Troubleshooting & Support

### Common Issues

| Issue | Solution |
| ----- | -------- |
| Virtual environment won't activate | Re-run `./setup_env.sh` or `setup_env.bat` |
| Playwright browsers not found | After activating environment, run `playwright install` |
| Tests timeout | Increase `--timeout` parameter or check network connection |
| Element not found | Check selectors; use `--headed` mode to assist diagnosis |
| Module import errors | Confirm virtual environment is activated; reinstall dependencies |
| Permission errors (macOS/Linux) | Run `chmod +x setup_env.sh` to grant execute permission |

### Before Seeking Support

1. Python version meets 3.9+ requirement (`python --version`)
2. `.env` file's Gemini API Key is correctly configured and not over quota
3. Check AI diagnostic logs in console output to locate root cause

---

## Page-level Search — On-Demand Only, Avoid Unnecessary Slowdowns

**Background**: Page-level Search works great for nested modals and multi-layer Drawers, but triggering it indiscriminately by default causes every test case — even those with no modal interactions — to run an extra full-page enumeration round, significantly increasing total execution time.

**v4.1 Change — Page-level Search is now opt-in**:

`smart_click`'s default behavior has been optimized for **fast, precise targeting** and no longer triggers Page-level Search by default. It only enters the full fallback chain when `fallback_scan: true` is explicitly declared.

```yaml
# ✅ Normal cases (recommended — fast by default, no page enumeration)
R_click_save: { name: 'Save' }
click_submit: { role: 'button', name: 'Submit' }

# ✅ Difficult scenarios (explicitly enable Page-level Search + AI fallback)
R_click_save_hard: { name: 'Save', fallback_scan: true }
R_click_scan: { name: 'Get Tickets' }   # Always enables full fallback

# ✅ Explicit action name (recommended for complex scenarios)
R_click_scan_save: { name: 'Save' }     # Equivalent to fallback_scan: true
```

**Performance Gain**: Depending on the number of test steps, indiscriminate Page-level Search can add 0.5–2 seconds per step. Switching to opt-in can speed up normal cases by **30–50%**.

**Advantage**: Compared to AI healing, Page-level Search is **Zero Token cost, Zero extra latency**, and often more accurate (page button enumeration uses exact matching; AI vision is probabilistic).

### MUI Controlled-Input Self-Healing — Handling React Interception

**Background**: Material-UI Switches/Checkboxes use controlled component patterns where the native `<input>` is wrapped by visual layers. Playwright's `set_checked()` may throw:

```
Locator.set_checked: Clicking the checkbox did not change its state
<div class="MuiStack-root ..."> intercepts pointer events
```

**Mechanism**: When `smart_check` detects this error, it automatically executes a three-step fallback:
1. Read the real state via JS `node.checked` to avoid unnecessary toggles.
2. Locate the parent wrapper node (where React's onClick handler is actually bound).
3. `force=True` click the parent node through the overlay.

#### `smart_check` Typical Usage Scenarios:

*   **Scenario 1: Standard MUI Switch (Controlled Component)**
    ```yaml
    # No need to worry about "Clicking... did not change state" errors
    check_allow_copy: { name: "Allow others to copy", checked: true }
    ```

*   **Scenario 2: Modal vs Background Name Collision (Smart Domain Awareness)**
    ```yaml
    # Automatically scopes to the latest modal viewport to avoid mis-clicking background elements
    check_modal_default: { role: 'checkbox', index: 0 }
    ```

*   **Scenario 3: Breaking the Sandbox (Manual Cross-Domain)**
    ```yaml
    # Use no_modal_scope if you need to check a background element while a modal/drawer is open
    check_background_sync: { role: 'checkbox', name: 'Sync now', no_modal_scope: true }
    ```

*   **Scenario 4: Maximum Stability (`test_id` + `check`)**
    ```yaml
    # Combines the most stable test_id strategy with the smartest check action
    check_publish_toggle: { test_id: 'publish-switch-input', checked: true }
    ```

### Native test_id Support

`smart_click` now supports the `test_id` parameter as the **highest priority locator strategy** (ahead of role/name/locator):

```yaml
# Supported in any clickable step
click_cta: { test_id: 'enhance-button-cta' }
click_confirm: { test_id: 'confirm-button' }
```

### smart_check Modal Domain Awareness

`smart_check` is now synchronized with `smart_click`, automatically detecting active Modals/Dialogs/Drawers and restricting checkbox search scope, preventing accidental interactions with background checkboxes.

---

## v4.2 New Features (2026-04-23)

### verify_no_sibling_text — Verify Element/Text Absence

**Use Case**: Verify that a specific text is **NOT visible** within a given scope. For example, verifying "Choose call-to-action type" is invisible when the CTA options are collapsed.

**Location**: `actions/base.py` → `verify_no_sibling_text()`

**Two Patterns**:

```yaml
# Pattern 1: Anchor on an element, verify its siblings do NOT contain the text
verify_no_sibling_add_new:
    locator: '[data-testid="base-more-horiz-icon-cta"]'
    index: -1
    text: 'Add new'

# Pattern 2: Directly verify text is NOT visible within a container scope (recommended)
verify_cta_type_4:
    text: 'Choose call-to-action type'
    container: 'test_general_products'
```

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `locator` | string | - | Element selector to anchor on (mutually exclusive with `container`) |
| `index` | int | -1 | Element index, supports negative (e.g., -1 = last) |
| `text` | string | required | Text that should NOT exist |
| `container` | string | - | Container scope text (mutually exclusive with `locator`) |
| `timeout` | int | 5000 | Timeout in milliseconds |

### execute_js — Execute JavaScript

**Use Case**: Run arbitrary JavaScript directly in the browser context for custom operations, DOM data extraction, or triggering special events.

**Location**: `actions/base.py` → `execute_js()`

```yaml
# 1. Inline script (automatically wrapped as arrow function)
execute_js: { script: "document.title" }

# 2. Script with arguments
execute_js:
    script: "(selector) => document.querySelector(selector).innerText"
    args: "h1"

# 3. Multiple arguments
execute_js:
    script: "(a, b) => a + b"
    args: [1, 2]

# 4. External JS file
execute_js: { file: "scripts/scroll_to_top.js" }

# 5. Assert return value
execute_js:
    script: "() => document.querySelectorAll('.item').length"
    assert_equals: 5

# 6. Save return value to workflow context
execute_js:
    script: "() => document.querySelector('.price').textContent"
    save_as: "price_text"
```

### Allure HTTP Server — Share Reports Over LAN

**Background**: Running `allure open` in CI/CD blocks the main process, and machines with multiple virtual NICs may report random IPs, making it hard for LAN colleagues to access the report.

**Solution**: `http_server.py` runs as an independent subprocess HTTP server, auto-detecting the LAN IP (excluding VirtualBox/VMware/Hyper-V virtual NICs).

**Usage**:

```bash
# Start (independent window, does not block pytest main process)
python http_server.py <report_dir> <port>

# Example
python http_server.py report/html/2026-04-23_11-00 8080
```

**Auto-print after startup**:

```
Allure report server started!
====================================
LAN access: http://192.168.50.92:8080
Local Allure: auto-opened
====================================
Press Ctrl+C to stop
```

**main.py Integration**: `main.py` automatically starts the HTTP Server and prints the LAN access address after test completion.

---

## v4.3 New Features (2026-05-22)

### Failed Case Diagnosis Tool (`diagnose_failed.py`)

**Background**: After test failures, Allure report error messages alone are often insufficient to pinpoint root causes. Manually opening a browser and debugging step by step is time-consuming.

**Solution**: Automatically replay failed cases with step-by-step screenshots + DOM snapshots, multi-strategy probing at failure points, and standalone HTML report generation.

**Usage**:
```bash
# Diagnose all failed cases from the latest run
python tools/diagnose_failed.py

# Specify a particular Allure run directory
python tools/diagnose_failed.py --allure-dir 20260521_144342

# Diagnose a single specific case
python tools/diagnose_failed.py --case testT1928

# Watch the replay in a real browser window
python tools/diagnose_failed.py --case testT1928 --headed
```

**Report Contents**:
- **Summary Dashboard**: Failed case overview + reproduction rate
- **Step-by-Step Replay**: Before/after screenshots + DOM snapshots per step
- **Multi-Strategy Probing**: At failure — text search, role search, test_id search, locator check, modal detection, aria-label search
- **Flaky Detection**: Cases that pass on replay are flagged as potentially flaky
- **Standalone HTML**: Single file with base64-embedded screenshots, can be sent directly to teammates

**Key Features**:
- Full pre_condition execution (all prerequisite steps replayed, not skipped)
- Cookie injection via `storage_state` (consistent with conftest.py)
- Compatible with project Action Registry (104 registered actions supported via fallback)
- Optional steps auto-skipped (step names containing "optional" marked as SKIPPED)
- Mock AI modules for fast startup (no SentenceTransformer loading)

### AI Vision On-Demand Loading (`ENABLE_AI_VISION`)

**Background**: SentenceTransformer + FAISS initialization takes ~20 seconds. Daily debugging rarely needs AI self-healing.

**Change**: `base.py` and `rag_knowledge.py` now gate on an environment variable:

```env
# .env file
ENABLE_AI_VISION=1    # Enable AI self-healing + RAG (requires Gemini API Key)
# Not set or 0 = Disabled (default)
```

**Scope**: All `python` and `pytest` commands, including `main.py`, `runner.py`, and `diagnose_failed.py`.

**Performance Impact**:
| Mode | Startup Time | AI Self-Healing | RAG Knowledge |
|------|-------------|-----------------|---------------|
| Default (off) | ~0.6s | Unavailable | Not loaded |
| `ENABLE_AI_VISION=1` | ~20s | Available | Available |

### DOM Snapshot Tool (`ui_snapshot.py`)

Monitor page DOM changes and detect the impact of UI refactors on test cases:

```bash
# Save baseline snapshot
python tools/ui_snapshot.py snapshot --env release --account main --label baseline

# Save current snapshot
python tools/ui_snapshot.py snapshot --env release --account main --label current

# Compare two snapshots
python tools/ui_snapshot.py diff --env release --base baseline --target current

# One-shot: snapshot + diff + list affected YAML files
python tools/ui_snapshot.py check --env release --account main --label current --base baseline
```

### Locator Batch Update Tool (`locator_updater.py`)

Batch-fix YAML locators after UI changes:

```bash
# Search for steps containing a specific locator (read-only)
python tools/locator_updater.py search --role button --name "Edit post"

# Preview changes without writing
python tools/locator_updater.py update --role button --name "Edit post" --new-name "Edit style" --dry-run

# Apply changes after confirmation
python tools/locator_updater.py update --role button --name "Edit post" --new-name "Edit style"
```

---

**Version:** v4.3 | **Last Updated:** 2026-05-22 | **Maintained by:** Autotest-monster Team
