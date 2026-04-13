## Auto Test Framework v4.0

> UI Automation Testing with AI Self-Healing using Python + Pytest + Playwright + Allure + Gemini Vision AI

English | [简体中文](./README.md)

## Features

- **Keyword-Driven Testing**: Define test cases in YAML — no coding required
- **Action Registry Pattern**: Modular action registry supporting team collaboration
- **AI Self-Healing**: When traditional locators fail, Gemini Vision AI automatically identifies and repairs element targeting
- **RAG Knowledge Base**: FAISS + SentenceTransformers powered domain knowledge retrieval for AI context
- **Execution History Tracking**: Records successful steps to provide AI with current test flow state
- **Multi-Environment Support**: Switch between staging/release via `--env` parameter
- **Dynamic Assertions**: Multiple assertion types (text visibility, element existence, etc.)
- **Auto-generated Allure Reports**
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Architecture Overview

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
└─ AI Self-Healing Engine (utils/ai_vision.py)
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

**Version:** v4.0  
**Last Updated:** 2026-04-10  
**Maintained by:** Autotest-monster Team
