# Pear Automation Test

> End-to-end test automation for Pear / Ticket.com — UI + API + CI, powered by Python, Pytest, Playwright and Allure.

English | [简体中文](./README.zh-CN.md)

---

## 📦 What's in this repo

| Module | Tech | Description |
|--------|------|-------------|
| **UI Automation** | Pytest + Playwright + YAML | Keyword-driven test cases defined in YAML, no coding required. AI self-healing via Gemini Vision. |
| **API Automation** | Pytest + Requests + Apifox | 20+ test suites covering login, purchase flow, post settings, resell, Shopify, admin tools, etc. |
| **CI/CD** | GitHub Actions | Scheduled daily runs on `ubuntu-latest`, Allure reports on GitHub Pages, Slack notifications. |
| **Data Prefill** | API scripts | Automatically creates test posts, events, products and tickets before UI runs. |

---

## ✨ Key Features

- **YAML Keyword-Driven**: Write UI test steps in YAML (clicks, fills, verifications) — no Python needed for new cases.
- **Action Registry**: Reusable actions (`R_click_*`, `fill_*`, `verify_*`, `execute_js_*`, `run_workflow_script`, etc.) shared across all YAML cases.
- **API Test Suites**: Organized by business domain under `test_case/API auto script/tests/` — from login flow to purchase, resell, refunds, tax, Shopify and admin.
- **Data Prefill**: `00_UI Prefill` suite seeds test posts/events/products/tickets via API before UI tests run.
- **Multi-Environment**: Switch between `staging` / `release` / production via `BASE_URL` in `.env`.
- **CI Reports**: Every run publishes an Allure report to GitHub Pages; Slack notifications summarize pass/fail counts.
- **Failed Case Diagnosis**: Auto-capture screenshots, DOM snapshots and step videos on failure.
- **AI Self-Healing** (optional): Gemini Vision AI can repair broken locators — disabled by default for fast CI.

---

## 📁 Repository Structure

```
├── test_case/
│   ├── UI/                          # UI automation (Playwright)
│   │   ├── All_YAML/                # YAML test cases by module
│   │   │   ├── Post/                # Post settings, announcements, venue map
│   │   │   ├── Events/              # Scanner, event flows
│   │   │   ├── Admin tools/         # Feature flags, admin settings
│   │   │   ├── Form/                # Storefront forms
│   │   │   └── Meta Pixel record/   # Pixel event verification
│   │  �── actions/                   # Action registry (click, fill, verify, etc.)
│   │   ├── ui_workflow/             # Reusable Python workflows (reset ticket, etc.)
│   │   └── test_ui.py               # YAML runner
│   └── API auto script/             # API automation (pytest)
│       ├── api/                     # Reusable API clients (login, orders, posts...)
│       ├── tests/                   # Test suites by domain
│       │   ├── 00_UI Prefill/       # Seed test data via API
│       │   ├── 01_Login flow/       # Account login & token
│       │   ├── 03_Consumer Purchase/ # Full checkout, tax, refund
│       │   ├── 07_Post validation/  # Post settings, coupons, coselling
│       │   └── ...                  # 20+ suites total
│       └── core/                    # API test framework core
├── tools/                           # Utilities (cookie fetch, CI summary, etc.)
├── .github/workflows/               # CI pipelines
│   ├── ui-automation-daily.yml      # UI: daily 20:00 Beijing time
│   ├── api-automation-daily.yml     # API: daily 08:00 Beijing time
│   └── cache-regression-daily.yml   # Regression suite
└── config/                          # Env, cookies, Slack config
```

---

## 🚀 Quick Start

### 1. Setup environment

```bash
./setup_env.sh        # macOS / Linux
setup_env.bat         # Windows
```

This creates a virtualenv, installs dependencies, and downloads Playwright Chromium.

### 2. Configure `.env`

```bash
cp .env.example .env
```

Set `BASE_URL` (default: `https://release.pear.us`).

### 3. Get login cookies

```bash
python3 tools/get_all_cookies.py
```

### 4. Run tests

**Run a single UI YAML case:**
```bash
cd test_case/UI
python3 -m pytest test_ui.py -k "testT4038" --yaml="All_YAML/Post/Post_setting.yaml"
```

**Run UI suite via main.py:**
```bash
python3 main.py
```

**Run API tests:**
```bash
cd "test_case/API auto script"
python3 -m pytest tests/ -k "testT2487"
```

---

## ⚙️ CI / Daily Automation

| Workflow | Schedule (Beijing) | What it does |
|----------|-------------------|--------------|
| `ui-automation-daily` | **20:00** every night | Full UI suite on `ubuntu-latest`, headless. Publishes Allure report to GitHub Pages, sends Slack summary. |
| `api-automation-daily` | **08:00** every morning | API suites (linda + lury). Slack notification with pass/fail counts. |
| `cache-regression-daily` | Scheduled | Regression test suite. |

All workflows support `workflow_dispatch` for manual triggering.

**Slack channel**: `#api-ui-automation-result-daily-report`

---

## 🧪 Writing a New UI Case

Create a YAML file under `test_case/UI/All_YAML/<Module>/`:

```yaml
testT9999:
    description: "Verify my new feature"
    test_step:
        open: "{BASE_URL}/events"
        sleep_step: 2000
        R_click_my_event: { locator: "text=My Event", exact: true }
        fill_title: { locator: 'input[name="title"]', value: "Auto test" }
        R_click_save: { role: 'button', name: 'Save' }
    expect_result:
        description: "Feature works correctly"
        assertions:
            - assertion_type: "text_visible"
              text: "Saved successfully"
```

Add the file name to `main.py`'s `yaml_files` list to include it in CI runs.

---

## 📄 Tech Stack

- **Python 3.11+**, **Pytest**, **Playwright** (Chromium headless on CI)
- **Allure** for test reporting (published to GitHub Pages)
- **GitHub Actions** for scheduled CI
- **Requests / Apifox** for API testing
- **OpenCV / QRCode** for scanner (fake camera y4m injection)

---

## 📚 More Docs

- [TECHNICAL_GUIDE.md](./TECHNICAL_GUIDE.md) — Framework internals
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Contribution guidelines
- [RELEASE_NOTES_v4.4.md](./RELEASE_NOTES_v4.4.md) — Changelog
