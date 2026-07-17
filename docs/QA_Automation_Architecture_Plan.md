# QA 自动化架构计划书

> **版本**: v1.0  
> **日期**: 2026-07-15  
> **作者**: QA Automation Team  
> **状态**: Proposed

---

## 1. 背景与目标

### 1.1 问题陈述

当前 QA 流程存在大量手工环节，从拿到 Jira 票到最终在 ONES 上创建测试计划并关联用例，整个过程依赖人工操作：

- 需求分析靠人读 Jira + 看 Figma，容易遗漏边界条件
- 用例编写后需手动登录 ONES 逐条录入
- 测试计划创建、用例关联均为手动点击
- 测试执行后的状态回填使用 Playwright UI 自动化（`update_test_status.py`），逐个搜索 + 点击，50 条用例需数分钟

### 1.2 目标

构建一套分层 QA 自动化系统，覆盖从需求分析到测试计划管理的全流程：

| 目标 | 衡量标准 |
|------|---------|
| 用例状态回填从 Playwright 逐个点击改为 API 批量更新 | 50 条用例 < 3 秒 |
| AI 辅助需求分析，输出漏洞报告 | 覆盖率 ≥ 人工审查的 80% |
| 用例录入从手动改为 API 自动创建 | 录入 20 条用例 < 5 秒 |
| 测试计划创建 + 用例关联自动化 | 一键完成，无需手动操作 ONES 界面 |

### 1.3 范围

**包含**：
- ONES API 客户端库（`ones_api` 包）
- 用例状态批量回填脚本（重构 `update_test_status.py`）
- 测试计划创建脚本
- 用例同步脚本
- QA Workflow Skill（AI 需求分析 + 用例生成 + 流程编排）

**不包含**：
- Jira API 集成（Phase 3 通过 WebFetch 抓取，不建独立客户端）
- Figma API 集成（通过浏览器截图 + AI 视觉分析）
- CI/CD 流水线改造（保持现有 pytest + Allure 架构不变）

---

## 2. 现状分析

### 2.1 已有资产

| 组件 | 位置 | 状态 | 备注 |
|------|------|:----:|------|
| `update_test_status.py` | `tools/` | 活跃 | Playwright UI 自动化，逐个搜索点击改状态 |
| `step_analyzer.py` | `tools/` | 活跃 | AI 失败诊断工具，Gemini 多模态 |
| `step_capture.py` | `tools/` | 活跃 | 运行时 step 级截图 + DOM 采集 |
| ONES 账号 | — | 活跃 | `yuxiao.zhu.ext@1m.app`，已有访问权限 |
| Allure 报告 | `allure-results/` | 活跃 | 带时间戳子目录，JSON 格式 |

### 2.2 痛点

1. **`update_test_status.py` 依赖浏览器**：Playwright 启动慢、DOM selector 脆弱、ONES UI 改版即 break
2. **用例录入纯手动**：20 条用例需 30+ 分钟手工填写
3. **需求分析无工具辅助**：完全靠 QA 个人经验，漏洞发现率不稳定
4. **状态映射不完整**：已修复（broken→阻塞, skipped→跳过），但整体架构仍是 UI 自动化

---

## 3. 架构设计

### 3.1 分层架构总览

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3 — Orchestration (Skill)                         │
│  AI reasoning + human-in-the-loop + workflow             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │ QA Workflow  │ │ Requirement  │ │ Test Case        │ │
│  │ Skill        │ │ Analysis     │ │ Generation       │ │
│  └──────┬───────┘ └──────┬───────┘ └────────┬─────────┘ │
└─────────┼────────────────┼──────────────────┼───────────┘
          │ calls           │ calls            │ calls
┌─────────▼────────────────▼──────────────────▼───────────┐
│  Layer 2 — Domain Scripts (deterministic, no AI)         │
│  ┌────────────────┐ ┌─────────────────┐ ┌─────────────┐ │
│  │ update_test    │ │ create_test     │ │ sync_test   │ │
│  │ _status.py     │ │ _plan.py        │ │ _cases.py   │ │
│  │ (automation)   │ │ (on-demand)     │ │ (on-demand) │ │
│  └───────┬────────┘ └───────┬─────────┘ └──────┬──────┘ │
└──────────┼──────────────────┼──────────────────┼────────┘
           │ depends on       │ depends on       │
┌──────────▼──────────────────▼──────────────────▼────────┐
│  Layer 1 — Infrastructure Library (ones_api package)     │
│  ┌────────┐ ┌────────────┐ ┌─────────────┐ ┌──────────┐ │
│  │ Auth   │ │ Test cases │ │ Test plans  │ │ Results  │ │
│  │ client │ │ CRUD       │ │ CRUD + link │ │ batch    │ │
│  └────────┘ └────────────┘ └─────────────┘ └──────────┘ │
│  Pure Python. No AI. No Playwright.                      │
└─────────────────────────────────────────────────────────┘
```

### 3.2 设计原则

1. **依赖方向自上而下**：Layer 3 → Layer 2 → Layer 1。下层不知道上层存在
2. **Layer 1 零外部依赖**：纯 `requests` 库，不依赖 Playwright / AI SDK
3. **Layer 2 可独立运行**：每个脚本有 CLI 入口，可脱离 Skill 单独执行
4. **Layer 3 有人审 checkpoint**：AI 分析结果和生成的用例必须经人工确认后才录入

### 3.3 Layer 1: `ones_api` 基础设施包

**目录结构**:
```
tools/ones_api/
├── __init__.py          # 包入口，导出 OnesClient
├── client.py            # OnesClient: 认证、请求封装、token 缓存
├── testcases.py         # TestCaseService: 用例 CRUD、模块管理
├── testplans.py         # TestPlanService: 计划创建、用例关联、回归 copy
├── results.py           # ResultService: 批量更新执行结果
├── models.py            # 数据模型: Case, Plan, Module, Result
└── config.py            # 配置: host, credentials, team_uuid
```

**核心类设计**:
```python
class OnesClient:
    """ONES API 客户端，管理认证和请求"""
    def __init__(self, host, email, password, team_uuid)
    def login(self) -> None
    def request(self, method, path, **kwargs) -> dict

class TestCaseService:
    """测试用例管理"""
    def list_libraries(self) -> list[Library]
    def list_modules(self, library_uuid) -> list[Module]
    def create_module(self, library_uuid, name) -> Module
    def create_case(self, library_uuid, module_uuid, case_data) -> Case
    def list_cases(self, library_uuid, **filters) -> list[Case]

class TestPlanService:
    """测试计划管理"""
    def create_plan(self, name, project_uuid) -> Plan
    def link_cases(self, plan_uuid, case_uuids) -> None
    def copy_regression_cases(self, plan_uuid, source_plan_uuid) -> None
    def list_plans(self, project_uuid) -> list[Plan]

class ResultService:
    """执行结果管理"""
    def batch_update(self, plan_uuid, results: list[CaseResult]) -> None
```

**Trade-off**:  
- **选择纯 `requests` 而非 `httpx`/`aiohttp`**: 项目 Python 3.9 环境，`requests` 已安装，无额外依赖。异步收益不大（ONES API 调用量小，非高并发场景）
- **选择类而非函数**: 4 个 service 共享同一个 client 实例（认证状态），类方法自然持有这个上下文。函数式需要传 client 参数，噪音大

### 3.4 Layer 2: 领域脚本

#### 3.4.1 `update_test_status.py`（重构）

**当前**: Playwright 打开 ONES → 逐个搜索用例 → 点击状态按钮  
**目标**: 读 Allure JSON → 映射状态 → 一次 API 批量更新

```python
# 输入: allure-results/{timestamp}/ 目录
# 输出: ONES 测试计划中所有用例状态更新

# 流程:
# 1. find_latest_allure_dir() → 定位最新报告
# 2. 读 *-result.json → 提取 case_name + status
# 3. status_map: passed→通过, failed→失败, broken→阻塞, skipped→跳过
# 4. ones_api.result_service.batch_update(plan_uuid, results)
```

**触发方式**: `python tools/update_test_status.py [--allure-dir <timestamp>] [--plan-uuid <uuid>]`

#### 3.4.2 `create_test_plan.py`（新增）

**输入**: Jira 票标题 + 项目 UUID  
**输出**: 测试计划 UUID

```python
# 流程:
# 1. ones_api.testplan_service.create_plan(name=title, project_uuid=...)
# 2. 打印 plan_uuid 供后续脚本使用
```

**触发方式**: `python tools/create_test_plan.py --title "TXXXX: 票标题" [--project-uuid <uuid>]`

#### 3.4.3 `sync_test_cases.py`（新增）

**输入**: 用例数据文件 (JSON/YAML) + 模块 UUID + 计划 UUID  
**输出**: 录入结果 + 关联结果

```python
# 流程:
# 1. 读用例数据文件
# 2. ones_api.testcase_service.create_case() 逐条创建
# 3. ones_api.testplan_service.link_cases(plan_uuid, new_case_uuids)
# 4. ones_api.testplan_service.copy_regression_cases(plan_uuid, source_plan_uuid)
```

**触发方式**: `python tools/sync_test_cases.py --file cases.yaml --module-uuid <uuid> --plan-uuid <uuid> [--copy-from <source_plan_uuid>]`

### 3.5 Layer 3: QA Workflow Skill

**用户交互流程**:

```
用户: "帮我分析这个 Jira 票 https://jira.xxx.com/browse/PROJ-123"
                    │
                    ▼
    ┌─── Skill: WebFetch 抓取 Jira 票内容 ───┐
    │  标题、描述、验收标准、附件链接          │
    └──────────────────┬──────────────────────┘
                       ▼
    ┌─── Skill: 请用户提供 Figma 截图 ────────┐
    │  用户上传截图 / Skill 用浏览器截图       │
    └──────────────────┬──────────────────────┘
                       ▼
    ┌─── AI: 交叉分析 Jira + Figma ───────────┐
    │  输出: 需求漏洞报告                      │
    │  ⏸ CHECKPOINT: 等用户确认               │
    └──────────────────┬──────────────────────┘
                       ▼
    ┌─── AI: 生成测试用例 ────────────────────┐
    │  输出: YAML 格式用例列表                 │
    │  ⏸ CHECKPOINT: 等用户确认/修改           │
    └──────────────────┬──────────────────────┘
                       ▼
    ┌─── Script: sync_test_cases.py ──────────┐
    │  API 创建用例 + 关联到测试计划           │
    └──────────────────┬──────────────────────┘
                       ▼
    ┌─── Script: create_test_plan.py ─────────┐
    │  API 创建测试计划 (标题=Jira票标题)      │
    │  API 关联新用例 + copy 回归用例          │
    └──────────────────┬──────────────────────┘
                       ▼
              返回测试计划链接
```

**Skill 目录结构**:
```
.workbuddy/skills/qa-workflow/
├── SKILL.md              # Skill 定义、触发条件、工作流
├── references/
│   ├── ones_api_guide.md # ONES API 使用指南
│   ├── case_template.yaml # 用例模板
│   └── review_checklist.md # 需求审查 checklist
└── scripts/
    └── (调用 Layer 2 脚本，不重复实现)
```

---

## 4. ONES API 端点映射

### 4.1 认证

| 操作 | 方法 | 端点 | 备注 |
|------|:----:|------|------|
| 登录 | POST | `/auth/login` | 返回 `user.token` + `user.uuid` |

**请求头** (所有后续请求):
```
Ones-Auth-Token: {token}
Ones-User-Id: {user_uuid}
```

**Token 策略**: 登录一次，缓存到 `tools/ones_api/.token_cache.json`，永不过期（除非改密码）。每次启动先读缓存，401 时重新登录。

### 4.2 测试用例管理

| 操作 | 方法 | 端点 | 对应流程步骤 |
|------|:----:|------|:------------|
| 列出用例库 | GET | `/libraries` | 找模块 |
| 列出模块 | GET | `/library/{libraryUUID}/modules` | 找模块 |
| 创建模块 | POST | `/modules/add` | 找模块（不存在时新建） |
| 创建用例 | POST | `/items/add` | 录入用例 |
| 列出用例 | GET | `/library/{libraryUUID}/cases` | 拉取用例 |

### 4.3 测试计划管理

| 操作 | 方法 | 端点 | 对应流程步骤 |
|------|:----:|------|:------------|
| 创建计划 | POST | `/testcase/plans/add` | 创建测试计划 |
| 关联用例 | POST | `/plan/{planUUID}/cases/add` | 拉取新用例 |
| 复制回归用例 | POST | `/plan/{planUUID}/cases/copy` | 拉取回归用例 |
| 批量更新结果 | POST | `/plan/{planUUID}/cases/update` | 更新执行状态 |
| 列出计划 | GET | `/project/{projectUUID}/plans` | 查找已有计划 |

### 4.4 API Base URL

```
https://{ones_host}/project/api/project/{endpoint}
```

> `{ones_host}` 待确认（用户需提供 ONES 部署地址）

---

## 5. 实施路线图

### Phase 1: 地基 + 状态回填重构

**目标**: `ones_api` 包可用，`update_test_status.py` 从 Playwright 迁移到 API

**交付物**:
- [ ] `tools/ones_api/` 包（client + testcases + testplans + results + models + config）
- [ ] `tools/ones_api/.token_cache.json` token 缓存机制
- [ ] 重构 `tools/update_test_status.py`，使用 `ones_api` 替代 Playwright
- [ ] 状态映射保持: passed→通过, failed→失败, broken→阻塞, skipped→跳过
- [ ] 单元测试: mock ONES API 响应，验证批量更新逻辑

**验收标准**:
- `python tools/update_test_status.py` 不再启动浏览器
- 50 条用例状态回填 < 3 秒
- ONES UI 改版不影响脚本运行

**前置条件**: 用户提供 ONES host 地址

---

### Phase 2: 测试计划 + 用例同步脚本

**目标**: 用例录入和测试计划创建自动化

**交付物**:
- [ ] `tools/create_test_plan.py` 脚本
- [ ] `tools/sync_test_cases.py` 脚本
- [ ] 用例数据格式定义（JSON schema 或 YAML template）
- [ ] 回归用例 copy 功能（从旧计划复制到新计划）

**验收标准**:
- `python tools/create_test_plan.py --title "TXXXX"` 创建计划并返回 UUID
- `python tools/sync_test_cases.py --file cases.yaml --plan-uuid <uuid>` 录入 20 条用例 < 5 秒
- 支持从指定旧计划复制回归用例

**前置条件**: Phase 1 完成

---

### Phase 3: QA Workflow Skill

**目标**: AI 驱动的端到端 QA 工作流

**交付物**:
- [ ] `.workbuddy/skills/qa-workflow/SKILL.md`
- [ ] 需求分析 prompt 模板（Jira + Figma 交叉分析）
- [ ] 用例生成 prompt 模板（输出 YAML 格式）
- [ ] 需求漏洞审查 checklist
- [ ] 流程编排逻辑（调用 Layer 2 脚本）

**验收标准**:
- 输入 Jira 链接 + Figma 截图 → 输出需求漏洞报告
- AI 生成的用例经确认后自动录入 ONES
- 自动创建测试计划并关联用例
- 人审 checkpoint 正常工作（AI 分析后暂停等确认）

**前置条件**: Phase 2 完成

---

### 里程碑总览

```
Phase 1 ████████░░░░░░░░░░░░  ones_api + update_test_status 重构
Phase 2 ░░░░░░░░████████░░░░░  create_test_plan + sync_test_cases
Phase 3 ░░░░░░░░░░░░░░░░██████  QA Workflow Skill
```

每个 Phase 可独立交付，Phase 1 完成后即有立竿见影的 ROI。

---

## 6. 架构决策记录 (ADR)

### ADR-001: 选择 ONES REST API 而非 Open API

**Status**: Accepted

**Context**: ONES 提供两套 API——v1 REST API（`/project/api/project/`）和 Open API（新版）。v1 文档标注"已废弃"。

**Decision**: 使用 v1 REST API。

**Consequences**:
- ✅ 立即可用，文档完整，24 个端点覆盖全部需求
- ✅ 认证简单（email + password → token）
- ✅ 后续迁移到 Open API 只需改 endpoint 路径，业务逻辑不变
- ⚠️ 官方可能在未来版本停止支持 v1（但目前无时间表）

---

### ADR-002: 选择三层架构而非单体脚本

**Status**: Accepted

**Context**: QA 流程包含 AI 驱动（需求分析、用例生成）和确定性（API 调用、状态更新）两类操作。

**Decision**: 分为 Layer 1（API 库）、Layer 2（脚本）、Layer 3（Skill）三层。

**Consequences**:
- ✅ 确定性任务可脱离 AI 独立运行（CI 自动化）
- ✅ API 客户端复用，不重复写认证逻辑
- ✅ Skill 只关注 AI 编排，不包含 HTTP 调用细节
- ⚠️ 层间有依赖，Phase 1 必须先完成才能建 Phase 2/3
- ⚠️ 代码分散在多个文件/目录，需文档维护依赖关系

---

### ADR-003: 选择 `requests` 而非 `httpx`/`aiohttp`

**Status**: Accepted

**Context**: Layer 1 需要一个 HTTP 客户端库。

**Decision**: 使用 `requests`。

**Consequences**:
- ✅ 零新依赖（Python 3.9 环境已安装）
- ✅ 同步调用足够（ONES API 调用量小，非高并发）
- ⚠️ 不支持异步，未来如果需要并发批量操作需引入 `httpx`

---

### ADR-004: AI 分析结果设人审 checkpoint

**Status**: Accepted

**Context**: AI 可能分析错误或遗漏，直接自动录入 ONES 风险大。

**Decision**: 需求漏洞报告和生成的用例在录入前必须经人工确认。

**Consequences**:
- ✅ 安全，不会因 AI 幻觉录入错误用例
- ✅ 用户可修改 AI 输出后再继续
- ⚠️ 不是完全自动化，需要人工介入
- ⚠️ Skill 实现需要支持暂停/恢复机制

---

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|:----:|:----:|---------|
| ONES API 变更或下线 | 低 | 高 | 封装在 Layer 1，变更只改一处；预留 Open API 迁移路径 |
| ONES 登录态过期 | 中 | 中 | token 缓存 + 401 自动重新登录 |
| Jira 票内容无法 WebFetch（需登录） | 中 | 中 | Phase 3 支持用户直接粘贴票内容作为备选输入 |
| Figma 截图质量影响 AI 分析 | 中 | 低 | 多页设计逐页截图；AI 分析结果有人审 checkpoint |
| AI 生成的用例不符合 ONES 格式 | 中 | 中 | 用例模板 + 格式校验；人审 checkpoint 兜底 |
| ONES API 速率限制 | 低 | 低 | 批量操作使用 batch endpoint；单条操作加 0.5s 间隔 |

---

## 8. 技术栈

| 组件 | 技术 | 版本要求 | 备注 |
|------|------|---------|------|
| Layer 1 HTTP | `requests` | ≥ 2.25 | 已安装 |
| Layer 1 数据模型 | `dataclasses` | Python 3.7+ | 标准库 |
| Layer 2 Allure 解析 | `json` | 标准库 | 读 `*-result.json` |
| Layer 2 CLI | `argparse` | 标准库 | 无额外依赖 |
| Layer 3 AI | WorkBuddy 内置 | — | Gemini 多模态 |
| Layer 3 网页抓取 | WebFetch / agent-browser | — | WorkBuddy 内置 |
| 配置管理 | `.env` + `os.environ` | — | 复用现有 `backend/.env` |

---

## 9. 配置项

### 9.1 环境变量

在 `backend/.env` 中新增：

```ini
# ONES API Configuration
ONES_HOST=https://your-ones-host.com
ONES_EMAIL=yuxiao.zhu.ext@1m.app
ONES_PASSWORD=your_password
ONES_TEAM_UUID=your_team_uuid
ONES_PROJECT_UUID=your_project_uuid
```

### 9.2 Token 缓存

```
tools/ones_api/.token_cache.json  (gitignored)
{
  "token": "xxx",
  "user_uuid": "xxx",
  "login_at": "2026-07-15T10:00:00"
}
```

---

## 10. 验收标准总表

| # | 验收项 | Phase | 验证方法 |
|---|--------|:-----:|---------|
| 1 | `ones_api` 包可 import 且 login 成功 | 1 | `python -c "from tools.ones_api import OnesClient; c = OnesClient(...); c.login()"` |
| 2 | token 缓存生效，第二次启动不重新登录 | 1 | 删除 `.token_cache.json` 后首次登录，再次启动不触发 login |
| 3 | `update_test_status.py` 不启动浏览器 | 1 | 运行时无 Playwright 进程 |
| 4 | 50 条用例状态回填 < 3 秒 | 1 | 计时验证 |
| 5 | `create_test_plan.py` 返回有效 plan UUID | 2 | ONES 界面可见新计划 |
| 6 | `sync_test_cases.py` 录入 20 条用例 < 5 秒 | 2 | 计时验证 |
| 7 | 回归用例 copy 成功 | 2 | 新计划中可见 copy 的用例 |
| 8 | Skill 接收 Jira 链接，输出需求漏洞报告 | 3 | 对话验证 |
| 9 | AI 生成的用例经确认后录入 ONES | 3 | ONES 界面可见新用例 |
| 10 | 人审 checkpoint 正常暂停 | 3 | Skill 在分析后暂停等待确认 |

---

## 附录 A: QA 流程 10 步映射

| # | 流程步骤 | 实现层 | 实现方式 |
|---|---------|:------:|---------|
| 1 | 打开 Jira 票 | L3 | WebFetch 抓取票面内容 |
| 2 | 查看票内容 | L3 | AI 提取标题/描述/验收标准 |
| 3 | 打开 Figma | L3 | 浏览器截图 + AI 视觉分析 |
| 4 | 结合分析需求 | L3 | AI 交叉比对 Jira + Figma |
| 5 | 抛出需求漏洞 | L3 | AI 输出漏洞报告 ⏸ 人审 |
| 6 | 编写用例 | L3 | AI 生成 YAML 用例 ⏸ 人审 |
| 7 | 登录用例平台 | L1 | `ones_api` client login |
| 8 | 找模块 + 录入用例 | L2 | `sync_test_cases.py` |
| 9 | 创建测试计划 | L2 | `create_test_plan.py` |
| 10 | 拉取用例（新+回归） | L2 | `sync_test_cases.py` + copy |

---

## 附录 B: 当前 `update_test_status.py` 改造对比

| 维度 | 当前 (Playwright) | 改造后 (API) |
|------|-------------------|-------------|
| 依赖 | Playwright + 浏览器 | `requests` 库 |
| 速度 | 50 条用例 ~3 分钟 | 50 条用例 < 3 秒 |
| 脆弱性 | ONES UI 改版即 break | API 不变则不受影响 |
| 状态映射 | 4 种（已修复） | 4 种（保持不变） |
| 触发方式 | 手动运行 / CI | 手动运行 / CI（更快） |
| 错误处理 | 超时 30s + 跳过 | HTTP 状态码 + 重试 |
| 日志 | Playwright 截图 | API 请求/响应 JSON |
