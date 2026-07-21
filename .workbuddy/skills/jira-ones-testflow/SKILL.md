---
name: jira-ones-testflow
description: Onboard test cases and a test plan from a Jira ticket into the ONES test management platform, then backfill the ONES plan link into the Jira ticket. Use this skill when the user wants to create/record test cases in ONES for a Jira ticket (e.g. KAT-XXXX), build a test plan, link cases to the plan, and fill the plan URL back into Jira. Triggers include "录入测试用例", "创建测试计划", "把用例录到 ONES", "回填 Jira 测试链接", "test case onboarding", "ONES test plan".
agent_created: true
---

# Jira → ONES Test Onboarding Flow

## Overview

End-to-end pipeline that turns a Jira ticket (e.g. `KAT-11397`) into a fully populated ONES test plan: read the requirement from Jira, generate test cases, create them via the ONES REST API, create a test plan via UI automation, link the cases to the plan via API, and backfill the ONES plan URL into the Jira ticket's `Test Case Link for QA` field. The pipeline is project-specific and depends on the tools already present in this repo.

## Prerequisites

- System Python `D:\Program Files\python.exe` with `playwright` installed (the managed Python lacks project deps).
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

**Agent behaviour on first run**: Before Step 1, check whether `backend/.env` exists and contains the personal credentials. If any are missing, **stop and ask the user** for their Jira email, Jira API token, ONES email, and ONES password, then write all fields (personal + team constants) into `backend/.env` and run `ones_writer.py refresh-token`. Do not proceed until credentials are in place. The user only needs to provide a Jira ticket link — the agent handles the rest.

## Field & UUID Reference

See `references/ones_jira_reference.md` for the authoritative list of ONES UUIDs, priority map, Jira custom field IDs, and UI selectors. Load it whenever exact IDs are needed.

## Workflow

### Step 1 — Read the Jira requirement

```
"D:/Program Files/python.exe" tools/jira_reader.py KAT-11397 --format text
```

Extract: summary (becomes the test plan title suffix), description (test case source), and `QA` field (`customfield_10083`) — the QA person becomes the test plan owner.

### Step 2 — Generate test cases

Analyse the Jira description and draft `data/<TICKET>_test_cases.json`. Each case:
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

Only use **P0 and P1** priorities (user convention). Map to ONES priority UUIDs via the reference file.

**Title naming convention**:
- Do NOT prefix case titles with the ticket number or internal tracking IDs (e.g. `KAT-11397 T1:`).
- Start the title with a clear action verb, preferably **`Verify ...`** (e.g. `Verify redirect URL works after form submission`, `Verify invalid redirect URL format is rejected`). This makes the test intent immediately obvious, matching the T5506 style in ONES.
- Keep it concise and scenario-focused.

### Step 3 — Create cases in ONES (REST API)

```
"D:/Program Files/python.exe" tools/ones_writer.py batch data/<TICKET>_test_cases.json
```

Creates cases under the target module. Results (with new UUIDs) are written to `data/ones_create_results.json`.

**Steps are written in a separate call**: ONES `items/add` silently ignores the `steps` field (and `testcase_case_steps: []` in the body will clear them). `ones_writer.py` handles this automatically — after `items/add` returns the new UUID, it calls the correct endpoint:
```
POST /project/api/project/team/{team}/testcase/library/{library_uuid}/cases/update
```
with a `cases[]` body containing `steps[]` (each step: `desc`, `result`, `index`, `key`, `testcaseCase: {uuid}`, `uuid`). If steps are ever missing, run `tools/ones_update_steps.py` to batch-write them.

### Step 4 — Set case priorities (GraphQL)

ONES `items/add` cannot set priority reliably; use the `updateTestcaseCase` GraphQL mutation:
```graphql
mutation {
  updateTestcaseCase(input: { key: "testcase_case-<UUID>", priority: "<PRIORITY_UUID>" }) {
    testcaseCase { uuid title priority { uuid value } }
  }
}
```
`key` must be `"testcase_case-<UUID>"` (not the bare `uuid`). P0=`3g7bLpa1`, P1=`VRXHXgbp`.

### Step 5 — Create the test plan (UI automation)

```
"D:/Program Files/python.exe" tools/_ones_create_plan_v3.py
```

`_ones_create_plan_v3.py` already implements the corrected logic:
- Parses the Jira key from the plan name.
- Reads the **QA field** (`customfield_10083`) from Jira and uses that person as the **test plan owner**.
- Sets the **test phase to 功能测试** (not the default 冒烟测试).
- Picks today as the execution date.
- Saves the plan, extracts the new plan UUID, and links cases via API.

ONES has **no API to create a test plan** (no `createTestcasePlan` GraphQL mutation; REST `items/add` with `item_type=testcase_plan` returns 500). UI automation is the only path.

UI entry: `https://ones.cn/project/#/testcase/team/<TEAM>/index` → click 「新建测试计划」.

### Step 6 — Link cases to the plan (API)

Done automatically by `_ones_create_plan_v3.py` after plan creation:
```
"D:/Program Files/python.exe" tools/ones_writer.py add-to-plan <PLAN_UUID> <CASE_UUID>...
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
- **Plan owner = Jira QA**, never hardcode or default to the first dropdown option.
- **Test phase = 功能测试** for ticket-driven plans, not 冒烟测试.
- ONES API domain is `sz.ones.cn` for REST, but the UI workspace is `ones.cn/project/#/...`. Do not confuse the two.
- Token expires ~1h; refresh with `python tools/ones_writer.py refresh-token` (uses Playwright login).
- ONES UI uses `ones-` class prefix (not `ant-`): `.ones-user-select`, `.ones-picker`, `.ones-select`.
- `updateTestcaseCase` requires `key: "testcase_case-<UUID>"` format, not bare `uuid`.
- Use system Python (`D:\Program Files\python.exe`) for all scripts — it has playwright and project deps.
- **Steps API**: `items/add` silently drops `steps`; use `cases/update` REST endpoint instead. `ones_writer.py` does this automatically; `ones_update_steps.py` can fix missing steps retroactively.
- **Point conservation**: Simple manual operations (editing a title, changing a dropdown) are cheaper for the user to do by hand than for the agent to automate. Reserve agent work for API calls, batch operations, and tasks requiring code.

## Cleanup

Temporary probe scripts (`tools/_ones_*.py`) accumulate during exploration. The only one worth keeping is `_ones_create_plan_v3.py` (the stable plan-creation flow). Offer to delete the rest once a ticket's flow is complete.
