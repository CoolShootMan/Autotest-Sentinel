# Jira / ONES 取数接口与工具

> 实测确认于 2026-09-17（`sz.ones.cn`，team `T7u1zXum`，library `XcAFFViB` = Katana）。
> 脚本是事实来源；本文件用于理解与排障，字段有疑问先看脚本 docstring。

## 链接格式

| 系统 | 形态 | 解析要点 |
|------|------|----------|
| Jira | `https://pearshop.atlassian.net/browse/KAT-11397` | `/browse/<KEY>` |
| ONES 计划级 | `https://ones.cn/project/#/testcase/team/<team>/plan/<plan_uuid>/library` | 计划内用例 |
| ONES 模块级 | `.../plan/<plan>/library/<lib>/module/<module_uuid>` | 模块是真实作用域 |
| ONES 单条 | `.../testcase/case/<case_uuid>` 或 `?caseUuid=<uuid>` | 直接取该条 |

`ones_reader.parse_link()` 同时支持 path 与 `?caseUuid=/planUuid=/moduleUuid=` 参数形式；**裸 uuid 当成用例 uuid**。

## 工具与用法

```bash
# Jira 读
py -3.9 tools/jira_reader.py <KEY> --format text
py -3.9 tools/jira_reader.py <KEY> --comments-only --format text

# Jira 写（补全 bug 票描述 / 发评论）；描述是 ADF，别手拼 JSON
py -3.9 tools/jira_writer.py <KEY> --show-description --out tmp.txt    # 先看原文（--out 避免控制台乱码）
py -3.9 tools/jira_writer.py <KEY> --description-file d.md --keep-media --dry-run
py -3.9 tools/jira_writer.py <KEY> --description-file d.md --keep-media       # 整体替换
py -3.9 tools/jira_writer.py <KEY> --append-description-file d.md             # 追加（最小侵入）
py -3.9 tools/jira_writer.py <KEY> --comment-file c.md

# ONES 读
py -3.9 tools/ones_reader.py "<ONES_LINK>" --out data/verify/<KEY>/ones_cases.json --markdown
py -3.9 tools/ones_reader.py "<ONES_LINK>" --grep "<kw>" --limit 20
py -3.9 tools/ones_reader.py --plan <plan_uuid> | --module <module_uuid> | --case <uuid,<uuid>>
py -3.9 tools/ones_reader.py --list-modules          # 找 module uuid
py -3.9 tools/ones_reader.py "<LINK>" --no-detail    # 只要清单不要步骤（快）

# ONES 写 / 计划（属 jira-ones-testflow 环节，本流程默认不做）
py -3.9 tools/ones_writer.py refresh-token           # token 失效时手动刷新
py -3.9 tools/ones_writer.py modules | plans

# ONES 回写"计划内执行结果"（Phase 4 默认要做，否则计划看板全是「未执行」）
py -3.9 tools/ones_plan_result.py --plan <uuid> --json data/verify/<KEY>/ones_results.json
py -3.9 tools/ones_plan_result.py --plan <uuid> --show
```

**🔴 Jira 描述里的截图是 ADF 的 `mediaSingle` 节点**（不是附件引用）。整体替换描述时**必须** `--keep-media`
并在 markdown 里放一个 `<!--MEDIA-->` 占位，否则**描述里的图会消失**。工具会读回校验媒体节点数。

## ONES 接口事实（实测）

### GraphQL —— 读用例首选（`POST /project/api/project/team/{team}/items/graphql`）

```graphql
# 1) 按模块过滤拿元数据（服务端过滤，一次调用）
query ($f: Filter, $n: Int) {
  testcaseCases(filter: $f, limit: $n) {
    uuid name number condition desc
    priority { uuid }
    testcaseModule { uuid name }
  }
}
# variables: {"f": {"testcaseModule_in": ["3moKQuHE"]}, "n": 1000}

# 2) 批量取步骤（一次调用可拿多条例用，分块 100 条）
query ($f: testcaseCaseStepsFilter) {
  testcaseCaseSteps(filter: $f) { testcaseCase { uuid } desc result index }
}
# variables: {"f": {"testcaseCase_in": ["RasykFr3", "C2WVmVUe"]}}
```

两条查询合起来 = 读一个模块的完整用例（含步骤）只需 **2 次请求**。

坑：

- `testcasePlan_in` 对 `testcaseCases` **非法**（400，pool 里没有 testcasePlan 字段）→ 计划维度用 REST `plan/{plan}/cases`，或 GraphQL `testcasePlanCases(filter:{testcasePlan_in:[...]})`。
- `orderBy: {position: ASC}` **非法**（testcase_case pool 无 position）→ 不要传 orderBy。
- `priority` / `type` 是**对象字段**，必须 `priority { uuid }`，裸 `priority` 报 "object field must have selections"。
- 没有字段字典接口（`/library/{lib}`、`/library/{lib}/fields`、`/library/{lib}/case/{uuid}/steps` 实测 404）→ 优先级/类型靠静态映射，未知 uuid 原样输出。

### REST

```
GET /testcase/libraries                     -> {libraries:[{uuid,name,modules:[...]}]}  全库模块树（uuid→名称）
GET /testcase/library/{lib}/cases           -> 全库用例（**忽略一切过滤/分页参数**，实测 module_uuid/testcase_module/module/path_modules/limit 五种写法全返 4768 条）
GET /testcase/library/{lib}/case/{uuid}     -> 单条用例（含 steps）
GET /testcase/plan/{plan}/cases             -> 计划内用例（steps 恒为空；**含 result = 执行状态**）
POST /testcase/plan/{plan}/cases/update     -> **回写用例执行结果**（见下）
GET /project/api/project/users/me           -> token 校验（200 = 有效）
```

**计划执行结果回写（2026-09-18 实测通过，`plan UjmD4hzp`）**

```
POST /project/api/project/team/{team}/testcase/plan/{plan}/cases/update
body: {"cases": [{"uuid": "7UdpmKjo", "result": "failed", "note": "一句结论 + 证据文件名"}]}
resp: {"success_cases": [...], "not_found_cases": [...], "no_permission_cases": [...]}
```

- `result` 枚举：`to_do`（未执行，默认）/ `passed` / `failed` / `blocked` / `skipped`。其它值 → 400 `InvalidParameter.TestCase.Result.InvalidType`（**有校验，不会静默写坏**）。
- **别混淆两套字段**：计划内 `result` ≠ 用例步骤上的 `execute_result/actual_result`。ONES UI 计划看板的「未执行」看的是**计划内 `result`**；不回写它，验完也显示「未执行」。
- 封装工具：`py -3.9 tools/ones_plan_result.py --plan <uuid> (--json f.json | --set uuid=result[:note] | --show)`，内置读回校验。
- 另：`POST .../testcase/plan/{plan}/case/{uuid}/update` 与 `.../plan/{plan}/cases` 均 **404**，不要试。

- **列表接口 steps 恒为 `[]`**，步骤只有单条详情或 GraphQL `testcaseCaseSteps` 才有。
- 模块名要自己拼：`modules[]` 有 `parent_uuid`，逐级向上；**只取目标库**，跨库合并会串名。
- 步骤结构：`{uuid, case_uuid, desc, result, execute_result, actual_result}`。`result` 是**预期结果**文本（不是执行状态）；`execute_result`/`actual_result` 属**步骤级**执行留痕，写入路径未验证。**执行状态请用计划级 `result`**（见上「计划执行结果回写」）。
- 优先级映射：`3g7bLpa1`=P0，`VRXHXgbp`=P1，`JoEcqaCe`=P2（三处记录一致）；**P3/P4 在本仓库两处记录互相矛盾（`3DvJC11V` / `R7wMSiP3` 谁 low 谁 lowest），未实测，遇到时以 ONES UI 标签为准**。本项目只用 P0/P1。
- 计划与模块可能无交集（模块是导航状态、计划是用例集合），`ones_reader` 会在"计划内该模块为空"时回退到"库内该模块"。

## 鉴权

- **ONES**：`Authorization: Bearer <ONES_AUTH_TOKEN>` + 头 `x-request-csrf-token: 1`；token = 登录 cookie `ones-lt`（约 1KB），**约 1 小时过期**（实测 15:34 有效、15:50 已 401）。失效时 `ones_reader` 默认自动调 `ones_writer.refresh_token_via_playwright()`（用 `ONES_EMAIL/ONES_PASSWORD` 弹浏览器登录并回写 `.env`）；`--no-refresh` 可禁用。
- **Jira**：`<base>/rest/api/3/issue/<KEY>`，Basic auth（`JIRA_EMAIL:JIRA_API_TOKEN`）。description/comment 是 ADF 格式，`jira_reader` 已做 ADF→纯文本（含 marks 超链接、inlineCard）。
- 自定义字段：QA = `customfield_10083`（数组，取 `displayName`）；`Test Case Link for QA` = `customfield_10090`（字符串）。
- 凭据都在 `backend/.env`，**不要写进报告、日志或提交**。
