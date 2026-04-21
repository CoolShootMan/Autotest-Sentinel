## Auto Test Framework v4.0

> UI Automation Testing with AI Self-Healing using Python + Pytest + Playwright + Allure + Gemini Vision AI

English | [简体中文](./README.md)

## Features

- **Keyword-Driven Testing**: Define test cases in YAML — no coding required
- **Action Registry Pattern**: Modular action registry supporting team collaboration
- **AI Self-Healing**: When traditional locators fail, Gemini Vision AI automatically identifies and repairs element targeting
- **RAG Knowledge Base**: FAISS + SentenceTransformers powered domain knowledge retrieval for AI context
- **Execution History Tracking**: Records successful steps to provide AI with current test flow state
- **Page-level Search** `[v4.1 NEW]`: Automatically fallback to full-page scanning when an element is outside the current Modal area. Zero Token consumption and extremely low latency.
- **MUI Controlled-Input Self-healing** `[v4.1 NEW]`: Automatically handles React/MUI controlled components (Switch/Checkbox) interception issues by force-clicking the parent wrapper.
- **Native test_id Support** `[v4.1 NEW]`: `smart_click` now supports the `test_id` parameter directly for the most stable locator strategy.
- **Multi-Environment Support**: Switch between staging/release via `--env` parameter
- **Dynamic Assertions**: Multiple assertion types (text visibility, element existence, visual height, etc.)
- **Auto-generated Allure Reports**
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Architecture Overview

```
YAML Test Definitions
    ↓
test_ui.py (Step Dispatcher + Execution History Tracker)
    ↓
actions/ (Action Registry)
    ├── base.py → smart_click / smart_fill / smart_check
    ├── module.py / product.py / form.py ...
    ↓
┌─ Level 1: Traditional Playwright Locators (role/text/test_id/locator)
│   Success → Continue
│   Failure ↓
├─ Level 2: Page-level Search [v4.1] (Zero Token Full-page Scan)
│   Iterates all matches → Clicks first visible candidate
│   Success → Continue
│   Failure ↓
├─ Level 2b: MUI Controlled-Input Fallback [v4.1] (smart_check only)
│   JS node.checked verification → Force click parent wrapper
│   Success → Continue
│   Failure ↓
└─ Level 3: AI Self-Healing Engine (utils/ai_vision.py)
       ├── Screenshot + SOM Overlay
       ├── RAG Knowledge Base Query (utils/rag_knowledge.py)
       ├── Execution History Context Injection
       └── Gemini Vision Analysis → Target Element ID
              ↓
         Healed Action Continues
              ↓
         Allure Report + Screenshots/Recordings
```

## Directory Structure

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
│       │  ├─module.py     # Module-related actions
│       │  ├─product.py    # Product-related actions
│       │  ├─form.py       # Form-related actions
│       │  └─layout.py     # Layout verification actions
│       ├─utils/           # [NEW v4.0] AI Self-Healing Toolkit
│       │  ├─ai_vision.py  # Gemini Vision AI Service (SOM + Multi API Key Rotation)
│       │  ├─rag_knowledge.py  # RAG Knowledge Base (FAISS + SentenceTransformers)
│       │  └─Knowledge_Base.md # Domain Knowledge Document
│       ├─conftest.py      # Pytest fixtures (multi-env + auth)
│       ├─test_ui.py       # Core test execution engine (with execution history)
│       └─Katana_curator_smoke_release.yaml  # Release environment test cases
├─tools                    # Utilities
│  ├─__init__.py           # Allure integration
│  └─get_cookie.py         # Cookie retrieval
├─requirements.txt         # Project dependencies
├─setup_env.sh            # macOS/Linux environment setup script
├─setup_env.bat           # Windows environment setup script
└─main.py                  # Main entry point
```

## Quick Start

### 1. Environment Setup (Recommended)

Run the appropriate setup script for your operating system:

**macOS/Linux:**

```bash
./setup_env.sh
```

**Windows:**

```bash
setup_env.bat
```

This script will automatically:

- Detect and create a virtual environment suitable for your OS
- Install all Python dependencies
- Install Playwright browsers

### 2. Manual Installation (Optional)

If you prefer to set up the environment manually:

```bash
# Create virtual environment
python3 -m venv venv          # macOS/Linux
python -m venv venv            # Windows

# Activate virtual environment
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate.bat      # Windows CMD

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 3. Environment Configuration

Create a `.env` file in the project **root** directory (or set environment variables) with Gemini API Keys (multiple keys are supported for rate-limit rotation):

```env
# Required: Gemini API Keys (comma-separated for multiple keys)
GEMINI_API_KEYS=key1,key2,key3

# Or a single key (legacy support)
GEMINI_API_KEY=your_single_key_here
```

### 4. Run Tests

```bash
# Run a specific test case (headed mode)
pytest test_case/UI/Test_Katana/test_ui.py \
    --headed \
    -v \
    --env release \
    --yaml All_YAML/Module/Module.yaml \
    --storage-state test_case/UI/Test_Katana/cookie_release.json \
    -k "testT3842"

# Run all test cases and generate reports
python main.py
```

### 5. View Reports

Allure reports open automatically after test completion.

## Common Commands

### Activate/Deactivate Virtual Environment

**macOS/Linux:**

```bash
source venv/bin/activate    # Activate
deactivate                  # Deactivate
```

**Windows:**

```bash
venv\Scripts\activate.bat   # Activate
deactivate                  # Deactivate
```

### Running Tests

```bash
# Test specific case
pytest test_case/UI/Test_Katana/test_ui.py -k testT3554 --headed -v --env release --storage-state test_case/UI/Test_Katana/cookie_release.json

# Test multiple cases
pytest test_case/UI/Test_Katana/test_ui.py -k "testT3554 or testT4660" --headed -v

# Run all tests
pytest test_case/UI/Test_Katana/test_ui.py --headed -v

# Show verbose output
pytest -vv -s test_case/UI/Test_Katana/test_ui.py

# Generate Allure reports
pytest --alluredir=allure-results test_case/UI/Test_Katana/test_ui.py
allure serve allure-results
```

### Environment Management

```bash
# Rebuild environment (use when troubleshooting)
rm -rf venv && ./setup_env.sh          # macOS/Linux
rmdir /s venv && setup_env.bat         # Windows

# Update dependencies
pip install --upgrade -r requirements.txt

# Install new dependencies
pip install package_name
pip freeze > requirements.txt
```

## Test Parameters

| Parameter         | Description          | Example                       |
| ----------------- | -------------------- | ----------------------------- |
| `-k`              | Filter tests by name | `-k testT3554`                |
| `-v`              | Verbose output       | `-v`                          |
| `-vv`             | More verbose output  | `-vv`                         |
| `-s`              | Show print output    | `-s`                          |
| `--headed`        | Show browser window  | `--headed`                    |
| `--headless`      | Headless mode        | `--headless`                  |
| `--storage-state` | Use saved session    | `--storage-state cookie.json` |
| `--env`           | Specify environment  | `--env release`               |
| `--yaml`          | Specify config file  | `--yaml config.yaml`          |

## V4.0 AI Self-Healing Architecture

### Core Flow

1. `smart_click` first tries traditional Playwright locators (role/name/text)
2. If timeout after 5s, triggers Legacy Fallback (15s)
3. If still failing, triggers **AI Self-Healing**:
   - Screenshots current page with SOM (Set-of-Mark) overlay
   - Queries RAG knowledge base for relevant business context
   - Sends screenshot + target description + execution history + RAG knowledge to Gemini Vision
   - AI returns diagnosis and target element ID
   - Clicks the AI-identified element

### RAG Knowledge Base

`utils/Knowledge_Base.md` stores business rules and UI navigation patterns including:

- System architecture and module overview
- Common navigation patterns (FAB button, event management, etc.)
- UI element characteristics and locator strategies
- Known automation pitfalls and solutions

### How to Extend the Knowledge Base

When AI self-healing makes incorrect decisions, add the corresponding business rules to `Knowledge_Base.md`. The AI will automatically retrieve and reference them next time.

## Multi-Environment Support

```bash
# Staging environment
pytest --env staging ...

# Release environment
pytest --env release ...
```

## Cross-Platform Support

This project supports running on Windows, macOS, and Linux. The automatic setup scripts will:

1. **Automatically detect your operating system**
2. **Create a virtual environment suitable for that system**
3. **Install appropriate dependencies and browsers**

### Virtual Environment Compatibility

- **Windows**: Uses `venv/Scripts/` directory with `.exe` executables
- **macOS/Linux**: Uses `venv/bin/` directory with extension-less executables

### Resolving Cross-Platform Issues

If you switch between different operating systems and encounter virtual environment incompatibility:

```bash
# Delete old environment, recreate
rm -rf venv          # macOS/Linux
rmdir /s venv        # Windows

# Run setup script
./setup_env.sh       # macOS/Linux
setup_env.bat        # Windows
```

## Troubleshooting

| Issue                              | Solution                                                        |
| ---------------------------------- | --------------------------------------------------------------- |
| Virtual environment won't activate | Re-run `./setup_env.sh` or `setup_env.bat`                      |
| Playwright browsers not found      | After activating environment, run `playwright install`          |
| Tests timeout                      | Increase `--timeout` parameter or check network connection      |
| Element not found                  | Check selectors, use `--headed` mode for debugging              |
| Import errors                      | Ensure virtual environment is activated, reinstall dependencies |
| Permission errors (macOS/Linux)    | Run `chmod +x setup_env.sh`                                     |

## System Requirements

- **Python:** 3.9+ (recommended 3.10+)
- **Operating System:** Windows 10+, macOS 11+, or mainstream Linux distributions
- **Browser:** Chromium (automatically installed by Playwright)
- **Memory:** 8GB+ RAM recommended
- **Disk Space:** At least 2GB free space

## Best Practices

1. **Always activate virtual environment before use**
2. **Use `--headed` mode when debugging test failures**
3. **Regularly update dependencies and test compatibility**
4. **Ensure all tests pass before committing code**
5. **Update RAG knowledge base promptly when AI misidentifies elements**

## Dependencies

Main dependencies include:

- `pytest` - Testing framework
- `playwright` - Browser automation
- `allure-pytest` - Test reporting
- `pandas` - Data processing
- `sentence-transformers` - AI/ML functionality
- `faiss-cpu` - Vector search
- `google-generativeai` - Gemini Vision AI

See `requirements.txt` for complete dependency list.

## Support

If you encounter issues, please check:

1. Python version meets requirements (`python --version`)
2. Virtual environment is properly activated
3. Dependencies are completely installed
4. Playwright browsers are installed
5. API Key in `.env` file is correctly configured

---

## V4.1 New Features (2026-04-14)

### Page-level Search — Zero Token Page-wide Fallback

**Context**: Traditional locators fail when the target button/element is outside the current Modal area (e.g., in a Drawer or Post Editor panel) while the framework has scoped the search to the active modal.

**Mechanism**: `smart_click` automatically triggers a page-wide scan for elements with `role='button'` if Level 1 and Level 2 locators fail:

```python
# No YAML changes required; the framework handles fallback automatically:
R_click_save: { role: 'button', name: 'Save' }
```

**Advantages**: Compared to AI healing, Page-level Search is **Zero Token cost, Zero additional latency**, and often more precise as it uses exact string matching.

### MUI Controlled-Input Self-healing — Handling React Interception

**Context**: Material-UI Switches/Checkboxes often wrap the native `<input>` within multiple `div` layers. Playwright's `set_checked()` might throw:
```
Locator.set_checked: Clicking the checkbox did not change its state
<div class="MuiStack-root ..."> intercepts pointer events
```

**Mechanism**: `smart_check` detects such errors and executes a three-step fallback:
1. Verify real state via JS `node.checked` to avoid unnecessary toggles.
2. Locate the parent wrapper node (where React usually attaches the onClick handler).
3. `force=True` click the parent wrapper.

#### `smart_check` Usage Scenarios:

*   **Scenario 1: Standard MUI Switch**
    ```yaml
    # No need to worry about "Clicking... did not change state" errors
    check_allow_copy: { name: "Allow others to copy", checked: true }
    ```

*   **Scenario 2: Modal vs Background Conflict**
    ```yaml
    # Automatically scopes to the active modal to avoid mis-clicking background elements
    check_modal_default: { role: 'checkbox', index: 0 } 
    ```

*   **Scenario 3: Breaking the Sandbox**
    ```yaml
    # Use no_modal_scope if you explicitly need to check a background element while a modal is open
    check_background_sync: { role: 'checkbox', name: 'Sync now', no_modal_scope: true }
    ```

*   **Scenario 4: Maximum Stability (`test_id` + `check`)**
    ```yaml
    # Combine the most stable test_id strategy with the smartest check action
    check_publish_toggle: { test_id: 'publish-switch-input', checked: true }
    ```

### Native test_id Support

`smart_click` now supports the `test_id` parameter as the **highest priority strategy** (ahead of role/name/locator):

```yaml
# Supported in any clickable steps
click_cta: { test_id: 'enhance-button-cta' }
click_confirm: { test_id: 'confirm-button' }
```

### smart_check Modal Domain Awareness

`smart_check` is now synchronized with `smart_click`, automatically detecting active Modals/Dialogs/Drawers to restrict searching scope, preventing accidental interactions with background checkboxes.

---

**Version:** v4.1  
**Last Updated:** 2026-04-15  
**Maintained by:** Autotest-monster Team
