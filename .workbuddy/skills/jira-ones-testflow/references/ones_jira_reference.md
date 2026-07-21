# ONES & Jira Reference

## ONES UUIDs (team T7u1zXum)

| Entity | UUID |
|--------|------|
| team | `T7u1zXum` |
| org | `ATfPf79v` |
| library (Katana) | `XcAFFViB` |
| current user | `HKJxJn4E` |
| default module | `2ojXUdsv` |
| Contact us form module | `8tMnELNg` |

## Priority Map (P0/P1 only for this project)

| Label | UUID | Color |
|-------|------|-------|
| highest (P0) | `3g7bLpa1` | red |
| high (P1) | `VRXHXgbp` | orange |
| normal (P2) | `JoEcqaCe` | yellow |
| low (P3) | `3DvJC11V` | green |
| lowest (P4) | `R7wMSiP3` | grey |

Type: functional = `7qLS7W5f`.

## Jira Custom Fields

| Field | ID | Type | Notes |
|-------|----|------|-------|
| QA | `customfield_10083` | array | `[{displayName: "..."}]` — becomes the test plan owner |
| Test Case Link for QA | `customfield_10090` | string | ONES plan URL backfilled here |

## API Endpoints

### ONES REST (domain: `sz.ones.cn`)
- Auth: `Authorization: Bearer <JWT>` + header `x-request-csrf-token: 1`
- Create case: `POST /project/api/project/team/T7u1zXum/items/add`
- List plans: `GET /project/api/project/team/T7u1zXum/testcase/plans`
- Token check: `GET /project/api/project/users/me`

### ONES GraphQL
- Endpoint: `POST .../items/graphql?t=<QUERY_NAME>`
- Modules: GraphQL `QUERY_MODULES_IN_LIBRARY` (REST 404)
- Update case priority: `updateTestcaseCase(input: {key: "testcase_case-<UUID>", priority: "<UUID>"})`
- Link cases to plan: `addTestcasePlanCase(plan: <UUID>, cases: ["testcase_case-<UUID>"])`
- **No** `createTestcasePlan` / `updateTestcasePlan` mutation exists.

### Jira REST (domain: from `JIRA_BASE_URL`)
- Auth: `Basic base64(email:token)`
- Get issue: `GET /rest/api/3/issue/<KEY>?fields=...`
- Update field: `PUT /rest/api/3/issue/<KEY>` with `{"fields": {...}}` → 204 on success
- List all fields: `GET /rest/api/3/field`

## ONES UI (workspace: `ones.cn`)

- Test management entry: `https://ones.cn/project/#/testcase/team/T7u1zXum/index`
- Plan detail: `https://ones.cn/project/#/testcase/team/T7u1zXum/plan/<PLAN_UUID>/library`
- Login: `https://ones.cn/auth/login` (email + password)
- Class prefix is `ones-` (not `ant-`):
  - Person selector: `.ones-user-select`
  - Date picker: `.ones-picker`
  - Select dropdown: `.ones-select`, options `.ones-select-item-option`
  - Modal: `.ones-modal-wrap`
- Plan form field order: 名称 → 负责人(person) → 测试阶段(select) → 执行日期(date) → Case Reviewer
- Phase dropdown default is 冒烟测试; select 功能测试 for ticket-driven plans.

## Current KAT-11397 State

- Plan UUID: `36T5CRZt`
- Plan URL: `https://ones.cn/project/#/testcase/team/T7u1zXum/plan/36T5CRZt/library`
- Owner: Yuxiao Zhu (from Jira QA)
- Phase: 功能测试
- Linked cases: RasykFr3, KYHLfaYw, VPJX3dus, 3Terx3zi, DKhUPRof, GUJzYYhE, XPWbZjfm
- Jira `customfield_10090` already backfilled with the plan URL.
