---
name: jira-ones-testflow
description: Onboard test cases and a test plan from a Jira ticket into the ONES test management platform, then backfill the ONES plan link into the Jira ticket. Use this skill when the user wants to create/record test cases in ONES for a Jira ticket (e.g. KAT-XXXX), build a test plan, link cases to the plan, and fill the plan URL back into Jira. Triggers include "录入测试用例", "创建测试计划", "把用例录到 ONES", "回填 Jira 测试链接", "test case onboarding", "ONES test plan".
agent_created: true
---

# Jira → ONES Test Onboarding Flow

## Overview

End-to-end pipeline that turns a Jira ticket (e.g. `KAT-11397`) into a fully populated ONES test plan: read the requirement from Jira, generate test cases, create them via the ONES REST API, create a test plan via UI automation, link the cases to the plan via API, and backfill the ONES plan URL into the Jira ticket's `Test Case Link for QA` field. The pipeline is project-specific and depends on the tools already present in this repo.

## Prerequisites

- Managed Python venv `C:\Users\tester\.workbuddy\binaries\python\envs\default\Scripts\python.exe` with `playwright` installed. If it is missing deps, install them with:
  ```
  C:\Users\tester\.workbuddy\binaries\python\versions\3.13.12\python.exe -m venv C:\Users\tester\.workbuddy\binaries\python\envs\default
  C:\Users\tester\.workbuddy\binaries\python\envs\default\Scripts\python.exe -m pip install playwright
  C:\Users\tester\.workbuddy\binaries\python\envs\default\Scripts\python.exe -m playwright install chromium
  ```
- Run from the repo root so relative paths resolve.

### Credential setup (first-time onboarding)

All credentials live in `backend/.env`. They fall into two groups:

**Personal credentials** (each teammate uses their own — the agent should ask for these interactively on first run):
| Field | How to obtain |
|-------|---------------|
| `JIRA_EMAIL` | The teammate's Jira login email |
| `JIRA_API_TOKEN` | Atlassian → Profile → **Security → API tokens → Create API token** (shown once) |
| `ONES_EMAIL` | The teammate's ONES login email |
| `ONES_PASSWORD` | The teammate's ONES login password |
| `FIGMA_TOKEN` | Figma → Avatar → **Settings → Personal access tokens → Generate new token**; select only `file_content:read` and `file_metadata:read` |

`ONES_AUTH_TOKEN` does **not** need manual entry — `ones_writer.py refresh-token` logs in with email+password and writes it automatically.

**Team-shared constants** (same for everyone — copy verbatim):
```
JIRA_BASE_URL=https://pearshop.atlassian.net
ONES_URL=https://sz.ones.cn
ONES_ORG_UUID=ATfPf79v
ONES_TEAM_UUID=T7u1zXum
ONES_LIBRARY_UUID=XcAFFViB
ONES_PRIORITY_HIGHEST=3g7bLpa1
ONES_PRIORITY_HIGH=VRXHXgbp
ONES_PRIORITY_NORMAL=JoEcqaCe
ONES_PRIORITY_LOW=R7wMSiP3
ONES_PRIORITY_LOWEST=3DvJC11V
ONES_TYPE_FUNCTIONAL=7qLS7W5f
```

`ONES_USER_ID` is personal but auto-discovered — after the first `refresh-token` run, read it from the login response and backfill into `.env`.

**Agent behaviour on first run**: Before Step 1, check whether `backend/.env` exists and contains the personal credentials. If any are missing, **stop and ask the user** for their Jira email, Jira API token, ONES email, ONES password, and Figma token, then write all fields (personal + team constants) into `backend/.env` and run `ones_writer.py refresh-token`. Do not proceed until credentials are in place. The user only needs to provide a Jira ticket link — the agent handles the rest.

## Field & UUID Reference

See `references/ones_jira_reference.md` for the authoritative list of ONES UUIDs, priority map, Jira custom field IDs, and UI selectors. Load it whenever exact IDs are needed.

## Workflow

### Step 1 — Read the Jira requirement

```
"C:/Users/tester/.workbuddy/binaries/python/envs/default/Scripts/python.exe" tools/jira_reader.py KAT-11397 --format text
```

Extract: summary (becomes the test plan title suffix), description (test case source), and `QA` field (`customfield_10083`) — the QA person becomes the test plan owner.

### Step 1.5 — Analyse Figma designs (for large/complex tickets)

If the Jira description contains a Figma link, **always** pull the design via the Figma REST API before writing cases. Do not rely solely on the Jira text — UI details (button labels, field order, error states) live in Figma.

```
"C:/Users/tester/.workbuddy/binaries/python/envs/default/Scripts/python.exe" tools/figma_api_reader.py --url "<FIGMA_URL>" --output data/figma_<TICKET> --analyze
```

`figma_api_reader.py`:
- Extracts the full node tree and all text content from the Figma file.
- Downloads high-resolution PNGs of key screens in batches (5–7 nodes per request to respect API limits).
- Writes a structured analysis (`analysis.md`) with user flows, key screens, and suggested test-case categories.

**Required token**: `FIGMA_TOKEN` in `backend/.env` with `file_content:read` and `file_metadata:read` permissions only.

**Fallback**: If the Figma API is unavailable, ask the user to screenshot the key screens (one per user scenario) and describe them.

### Step 1.6 — Record open questions and validate with the user

Before generating cases, the agent must explicitly list:
1. The user scenarios it identified from Jira + Figma.
2. The module it intends to use in ONES (see Step 2).
3. Any unclear requirements, missing edge cases, or contradictory information.

**Do not proceed to Step 2 until the user confirms or answers**. This prevents rework. Example:

> "I see two Collabs modules in ONES: `Collabs` under My Shop (53 cases) and top-level `Collabs` (4 cases). KAT-11654 is about the co-seller invitation flow, so I plan to use the My Shop → Collabs module (`3pfH7pm8`). Please confirm."

### Step 2 — Generate test cases

Analyse the Jira description and Figma analysis and draft `data/<TICKET>_test_cases.json`. Each case:
```json
{
  "title": "...",
  "description": "...",
  "precondition": "...",
  "steps": [{"desc": "...", "expect": "..."}],
  "priority": "P0" | "P1",
  "module_uuid": "<module UUID>"
}
```

**Module selection** (must be decided per ticket — never hardcode):
- Run `python tools/ones_writer.py modules` to list all modules with their full paths.
- Pick the module that matches the ticket's feature area (e.g. Collabs → My Shop → Collabs).
- Set `ONES_DEFAULT_MODULE_UUID=<uuid>` in `backend/.env` **temporarily for this ticket**, or pass `--module <uuid>` to `ones_writer.py batch`, or set `module_uuid` on each case in the JSON.
- If unsure, ask the user before creating cases.

Only use **P0 and P1** priorities (user convention). Map to ONES priority UUIDs via the reference file.

### ⛔ CRITICAL — Modifying existing cases (T4101 incident, 2026-07-22)

When a ticket's feature is "copied" to a new flow (e.g. post preferences appear both in Collabs settings AND invite acceptance flow):

1. **NEVER overwrite existing case steps.** Before any modification:
   - FETCH the current case detail (name, condition, assign, steps) via GraphQL
   - Save a backup to `data/<TICKET>_case_backup_<UUID>.json`
   - Only modify the specific fields that need changing
   - When adding steps, APPEND to the existing steps array — never replace it

2. **NEVER change the assignee.** The `assign` field must be preserved from the original case. Do not set it to the current user unless explicitly told to.

3. **If the feature exists in its original module, do NOT modify that case.** Instead:
   - Create a NEW case in the new flow's module (or the ticket's module)
   - Reference the original case's steps as a guide
   - The original case stays untouched — the feature was not removed from its original location

4. **For "modify existing case" tasks:** clearly distinguish between:
   - "Update title + ADD steps" (append only) — the default
   - "Update title + REPLACE steps" (full overwrite) — only when the user explicitly says the entire flow changed

**Title naming convention**:
- Do NOT prefix case titles with the ticket number or internal tracking IDs (e.g. `KAT-11397 T1:`).
- Start the title with a clear action verb, preferably **`Verify ...`** (e.g. `Verify redirect URL works after form submission`, `Verify invalid redirect URL format is rejected`). This makes the test intent immediately obvious, matching the T5506 style in ONES.
- Keep it concise and scenario-focused.

### Step 3 — Create cases in ONES (REST API)

```
"C:/Users/tester/.workbuddy/binaries/python/envs/default/Scripts/python.exe" tools/ones_writer.py batch data/<TICKET>_test_cases.json
```

Creates cases under the target module. Results (with new UUIDs) are written to `data/ones_create_results.json`.

To override the module for the whole batch (e.g. when `ONES_DEFAULT_MODULE_UUID` is not set and the JSON lacks `module_uuid`):
```
"C:/Users/tester/.workbuddy/binaries/python/envs/default/Scripts/python.exe" tools/ones_writer.py batch data/<TICKET>_test_cases.json --module <MODULE_UUID>
```

**Steps are written in a separate call**: ONES `items/add` silently ignores the `steps` field (and `testcase_case_steps: []` in the body will clear them). `ones_writer.py` handles this automatically — after `items/add` returns the new UUID, it calls the correct endpoint:
```
POST /project/api/project/team/{team}/testcase/library/{library_uuid}/cases/update
```
with a `cases[]` body containing `steps[]` (each step: `desc`, `result`, `index`, `key`, `testcaseCase: {uuid}`, `uuid`). If steps are ever missing, run `tools/ones_update_steps.py` to batch-write them.

### Step 4 — Set case priorities (REST API)

ONES `items/add` cannot set priority reliably. The GraphQL `updateTestcaseCase` mutation returns `"unknown field testcaseCase"` error (schema mismatch as of 2026-07). **Use the REST `cases/update` endpoint instead**, which accepts `priority` in the body:

```
POST /project/api/project/team/{team}/testcase/library/{library_uuid}/cases/update
```
Body:
```json
{
  "cases": [{
    "uuid": "<CASE_UUID>",
    "library_uuid": "<LIBRARY_UUID>",
    "module_uuid": "<MODULE_UUID>",
    "name": "<CASE_NAME>",
    "assign": "<USER_UUID>",
    "type": "7qLS7W5f",
    "priority": "<PRIORITY_UUID>",
    "condition": "",
    "desc": "",
    "steps": []
  }]
}
```
P0=`3g7bLpa1` (highest), P1=`VRXHXgbp` (high). Only use P0/P1 for this project.

**Note**: `steps: []` in this call is safe — it won't clear existing steps (the endpoint only updates fields that differ). But if you want to be safe, include the existing steps in the array.

### Step 5 — Create the test plan (UI automation)

```
"C:/Users/tester/.workbuddy/binaries/python/envs/default/Scripts/python.exe" tools/ones_create_plan_v3.py <TICKET> --owner <OWNER_QUERY>
```

**Parameters**:
- `<TICKET>` — the Jira ticket key (e.g. `KAT-11397`), used to fetch the summary (becomes plan name) and QA owner.
- `--owner <OWNER_QUERY>` — the search term to type into the ONES owner dropdown. Derive this from the Jira QA field's `displayName`: take the **first name in lowercase** (e.g. `"Yuxiao Zhu"` → `"yuxiao"`). This must be unique enough to match exactly one person in the dropdown.
- `--plan-name` (optional) — override the auto-generated `"TICKET: <jira summary>"` plan name.

`ones_create_plan_v3.py` implements:
- Fetches the Jira summary and QA displayName automatically.
- Sets the **test phase to 功能测试** (not the default 冒烟测试).
- Picks today as the execution date.
- Saves the plan, extracts the new plan UUID, and links cases via API.
- Owner selection: types the query, then **only clicks the option that contains the query string** — never falls back to "first option". If no match, raises an error.

ONES has **no API to create a test plan** (no `createTestcasePlan` GraphQL mutation; REST `items/add` with `item_type=testcase_plan` returns 500). UI automation is the only path.

UI entry: `https://ones.cn/project/#/testcase/team/<TEAM>/index` → click 「新建测试计划」.

### Step 6 — Link cases to the plan (API)

`ones_create_plan_v3.py` auto-links cases from `data/ones_create_results.json` (newly created cases only). If you also modified existing cases, link them separately:
```
"C:/Users/tester/.workbuddy/binaries/python/envs/default/Scripts/python.exe" tools/ones_writer.py add-to-plan <PLAN_UUID> <CASE_UUID>...
```
Uses the `addTestcasePlanCase` GraphQL mutation.

### Step 7 — Backfill Jira

PUT the ONES plan URL into Jira's `Test Case Link for QA` field (`customfield_10090`, string):
```
PUT /rest/api/3/issue/<TICKET>
{"fields": {"customfield_10090": "<ONES_PLAN_URL>"}}
```
Success returns HTTP 204. Verify by re-fetching the field.

### Step 8 — Final verification (manual spot-check)

After the full pipeline, do a quick visual check in ONES and Jira:
- **ONES**: Open the test plan, verify all cases are linked, priorities are correct, and each case has steps with expected results.
- **ONES case titles**: Confirm titles start with `Verify ...` (or another clear action verb) and contain no internal tracking prefixes (`KAT-XXXX TN:`). If any slipped through, edit them inline in ONES UI — this is a 10-second manual fix, not worth automating.
- **Jira**: Confirm the `Test Case Link for QA` field shows the correct ONES plan URL.

## Critical Constraints & Pitfalls

- **Priority map is P0/P1 only** for this project. Do not use P2–P4.
- **Plan owner = Jira QA**, never hardcode or default to the first dropdown option. The `--owner` flag must be derived from the Jira QA field's displayName (first name, lowercase).
- **Module must be selected per ticket**: never reuse a historical module UUID (e.g. `2ojXUdsv`) by default. List modules, choose the one matching the feature area, and set `ONES_DEFAULT_MODULE_UUID` or use `--module`.
- **No hardcoded credentials**: all email/password/token values must come from `backend/.env`. Never hardcode personal credentials in source files.
- **Test phase = 功能测试** for ticket-driven plans, not 冒烟测试.
- ONES API domain is `sz.ones.cn` for REST, but the UI workspace is `ones.cn/project/#/...`. Do not confuse the two.
- Token expires ~1h; refresh with `python tools/ones_writer.py refresh-token` (uses Playwright login).
- ONES UI uses `ones-` class prefix (not `ant-`): `.ones-user-select`, `.ones-picker`, `.ones-select`.
- `updateTestcaseCase` requires `key: "testcase_case-<UUID>"` format, not bare `uuid`.
- Use the managed Python venv (`C:\Users\tester\.workbuddy\binaries\python\envs\default\Scripts\python.exe`) for all scripts. If it lacks `playwright`, install via the managed runtime (see Prerequisites).
- **Steps API**: `items/add` silently drops `steps`; use `cases/update` REST endpoint instead. `ones_writer.py` does this automatically; `ones_update_steps.py` can fix missing steps retroactively.
- **Point conservation**: Simple manual operations (editing a title, changing a dropdown) are cheaper for the user to do by hand than for the agent to automate. Reserve agent work for API calls, batch operations, and tasks requiring code.

## Cleanup

Temporary probe scripts (`tools/_*.py`) accumulate during exploration. After a ticket's flow is complete, delete them; only stable tools (without the `_` prefix) should remain.
