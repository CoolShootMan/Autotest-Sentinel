# 项目模块全景 · Module Map

> 本文件回答一个问题：**这个仓库里到底有哪些东西，各自从哪进、看哪份文档。**
> 根 README 只覆盖 UI 自动化主线；API 自动化、性能/缓存回归、backend 服务、tools 工具链的完整说明都在这里汇总。

## 0. 文档地图

| 文档 | 内容 | 适合谁 |
|------|------|--------|
| [README.zh-CN.md](../README.zh-CN.md) / [README.md](../README.md) | 项目介绍、快速开始、UI 用例编写、v4.x 新特性 | 所有人（入口） |
| [TECHNICAL_GUIDE.md](../TECHNICAL_GUIDE.md) | UI 框架内部机制：Action Registry、AI 自愈、兜底策略 | 框架开发者 |
| **docs/MODULES.md**（本文） | 全仓库模块地图：UI / API / 性能 / backend / CI / 产物目录 | 新人、交接、排障 |
| [docs/TOOLS.md](./TOOLS.md) | `tools/` 下 50+ 脚本的分类速查（用途 + 常用命令） | 日常执行、排障 |
| [test_case/API auto script/ONBOARDING.md](../test_case/API%20auto%20script/ONBOARDING.md) | API 自动化上手：环境、目录、套件、写用例 | API 测试同学（**必读**） |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | 分支/提交/PR/仓库卫生/文档约定 | 贡献者 |
| [RELEASE_NOTES_v4.5.md](../RELEASE_NOTES_v4.5.md) | 各版本变更记录 | 所有人 |

---

## 1. 模块总览

| 模块 | 路径 | 入口 | 技术栈 |
|------|------|------|--------|
| **UI 自动化** | `test_case/UI/` | `pytest`（仓库根）、`test_case/UI/main.py`（CI）、`test_case/UI/runner.py`（交互式） | pytest + Playwright + YAML + Allure + Gemini |
| **API 自动化** | `test_case/API auto script/` | `python run_suite.py suites/<suite>.yaml` | pytest + Requests + YAML/JSON 模板 |
| **性能测试** | `test_case/performance testing/` | `python Pear_FE_BE_performance.py` | Playwright 并发浏览器 + Navigation Timing |
| **缓存回归** | `test_case/performance testing/cache-regression/` | `pytest`（该目录内） | pytest + 响应头审计（X-DB-Query-Count） |
| **Backend 服务** | `backend/` | `uvicorn backend.main:app` | FastAPI + Celery/Redis + Gemini |
| **工具链** | `tools/` | 各脚本 `--help` | Python（Playwright / REST / SQL） |
| **CI** | `.github/workflows/` | GitHub Actions（3 条 daily） | Ubuntu + Python 3.11 + Allure CLI |

---

## 2. UI 自动化（主线）

- **用例**：`test_case/UI/All_YAML/`，按业务分目录；关键字驱动，无需写 Python。
- **执行引擎**：`test_case/UI/test_ui.py`（唯一的 `test_case` 参数化入口）+ `actions/`（Action Registry）。
- **业务封装**：`test_case/UI/page/`。
- **AI 自愈**：`test_case/UI/utils/ai_vision.py`（Gemini Vision + SOM）、`utils/rag_knowledge.py`（FAISS + SentenceTransformers）、`utils/Knowledge_Base.md`。
- **配置**：仓库根 `pytest.ini`（`testpaths = test_case/UI`、`python_files = test_ui.py`）；`.env` 管 `BASE_URL` 与 Gemini Key。
- **报告**：Allure（`allure-results/` → `allure generate` → `allure-report/`），`main.py` 串起完整链路并起局域网 HTTP 服务。

> 细节见 [TECHNICAL_GUIDE.md](../TECHNICAL_GUIDE.md)：Action Registry、三层兜底、MUI 受控组件、可选点击/重试等。

---

## 3. API 自动化

`test_case/API auto script/` 是一个**独立 pytest 工程**（自带 `pytest.ini` / `conftest.py` / `requirements.txt`），与 UI 套件互不干扰。

### 3.1 分层（记忆口诀：tests 写用例 · core 做执行 · api 做门面 · config 定环境）

```
tests/<NN_Folder>/test_<slug>.py   ← 用例
        │
        ▼
     api/*   →   core/*   →   config/env_loader.py
   业务门面     HTTP/上下文     环境 YAML + 占位符渲染
```

- `api/`：按业务域切分的门面（`auth` `cart` `orders` `payments` `products` `posts` `events` `forms` `merchants` `storefront` `users` `admin` `analytics` `approvals` `campaigns` `earnings` `external` `links` `misc` `promoters` `address` …）。
- `core/`：`http_client`、`context`、`response`、`assertions`、`templating`、`token_refresh`、`db`、`case_audit`、`run_archive`、`logging_util`、`compat`、`jsonpath`、`errors`。
- `suites/`：套件清单（如 `linda.yaml`、`lury.yaml`），`run_suite.py` 按清单批量跑并归档到 `results/runs/<run_id>/`。
- `tests/`：真正的用例脚本；`case_index.py` / `case_vars.py` 管用例索引与变量。
- `_apifox_export/` + `apifox_client.py` / `apifox_db.py`：Apifox 导入/导出联动。
- `server.py`：本地调试/触发服务；`new_case.py`：新建用例脚手架；`start_ui.sh`：macOS 启动脚本。

### 3.2 运行

```bash
cd "test_case/API auto script"
python run_suite.py --list                 # 列出可用套件
python run_suite.py suites/linda.yaml      # 跑主套件
pytest tests/<dir>/test_xxx.py -k <name>   # 单条调试
```

> 环境、Python 版本约束（本机 managed Python 3.13）、IDE 接入、Apifox 细节见
> **[ONBOARDING.md](../test_case/API%20auto%20script/ONBOARDING.md)**（530 行，API 方向唯一权威上手文档）。

---

## 4. 性能测试与缓存回归

### 4.1 前端/后端性能（`Pear_FE_BE_performance.py`）

模拟 N 个并发**真实浏览器用户**访问目标 URL，采集：

- **FE**：Navigation Timing、Paint 等浏览器侧指标
- **BE**：接口响应时间

输出 Markdown 性能报告。

```bash
python "test_case/performance testing/Pear_FE_BE_performance.py" \
  --url "https://release.pear.us" --concurrent 20 [--headful]
```

依赖 Playwright Chromium（`playwright install chromium`）。

### 4.2 缓存回归（`cache-regression/`）

**目的**：防止"该命中缓存的接口偷偷打 DB"。

**机制**：后端在每个 API 响应头注入 `X-DB-Query-Count`（本次请求产生的 DB 查询次数）。
**判定**：缓存命中的请求该值必须为 `0`。

- **审计范围**：仅 C 端业务接口（`katana-api` 域 storefront 真实读写路径）。
- **admin 域不参与**：后台不要求缓存，且 admin GET 无埋点；入口统一过滤。
- **参数**：`API_Parameter_Release.csv` / `API_Parameter_Prod.csv`（按环境）。
- **用例**：`test_pdp` / `test_post` / `test_promotion` / `test_buy_now_journey` / `test_checkout_journey` / `test_concurrent_read` / `test_second_read`（第二次读必须 0 查询）。
- **辅助**：`audit_http.py`（审计 HTTP 层）、`dynamic_ids.py`（动态 ID）、`precondition_login.py`（登录前置）。

> 与性能测试同目录，但**属于功能回归**：CI 每天跑，结果写 Job Summary 并归档 artifact。

---

## 5. Backend 服务（`backend/`）

一个 FastAPI 服务，对外提供 "Autotest-monster Platform" 的 AI 测试能力（当前版本 0.1.0）：

- `backend/main.py`：FastAPI 应用（CORS 全开，`/` 健康检查）。
- `backend/core/ai_vision.py`：AI Vision 能力服务化。
- `backend/core/parser.py`：解析器。
- `demo_self_healing.py` / `list_models.py`：自愈演示与模型列表。
- 依赖：`backend/requirements.txt`（fastapi、uvicorn、celery、redis、sqlalchemy、asyncpg、google-generativeai、langchain、opencv、playwright …）。

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

> 注意：backend 是**独立服务**，不参与 UI/API 每日测试；它依赖的 Python 版本与主套件不同（需要较新的 3.x）。

---

## 6. 工具链（`tools/`）

50+ 脚本，按用途分 9 类：登录态与环境、用例编写与定位器、诊断与报告、ONES、Jira、发布同步、数据与勘查、二维码/票券、其他。
完整清单（每个脚本一句话用途 + 常用命令）见 **[docs/TOOLS.md](./TOOLS.md)**。

高频入口：

```bash
py -3.9 tools/get_all_cookies.py          # 刷新三账号登录态
py -3.9 tools/diagnose_failed.py          # 诊断最近失败用例
py -3.9 tools/locator_lint.py --errors-only
py -3.9 tools/ui_snapshot.py --help       # DOM 快照/diff
py -3.9 tools/gh_push.py --dry-run        # 安全推送（凭据管理器）
```

---

## 7. CI / 每日自动化

三条 GitHub Actions，全部 Ubuntu + **Python 3.11**：

| Workflow | 时间（北京时间） | 内容 |
|----------|------------------|------|
| `ui-automation-daily` | **20:00** 每天 | 无头跑全量 UI 套件（`main.py`），Allure 报告发布 GitHub Pages，Slack 汇总；含 NotRecognized 扫码用例 |
| `api-automation-daily` | **08:00** 每天 | 跑 `linda` + `lury` 两套 API 套件，`tools/ci_report.py --step-summary` 写运行页，Slack 通知 |
| `cache-regression-daily` | **10:00** 每天 | 缓存 0-DB 审计，报告写 Job Summary + 上传 artifact + Slack 汇总 |

三条均支持 `workflow_dispatch` 手动触发。UI workflow 会先 `Setup Java`（仓库自带 Allure CLI 需要 JRE）。

---

## 8. 运行时产物目录（不入库）

| 目录 | 产生方 | 说明 |
|------|--------|------|
| `allure-results/` / `allure-report/` | pytest + allure | 原始结果与生成报告 |
| `report/` | `tools/gen_report.py` | 自定义布局报告 |
| `dom_kb/` | `tools/dom_kb.py` | DOM 向量知识库索引（构建物） |
| `ui_snapshots/` | `tools/ui_snapshot.py` | DOM 快照基线/差异 |
| `step_captures/` | `tools/step_capture.py` | 步骤级抓取 |
| `test-results/` | pytest-playwright | 截图/录屏/trace |
| `log/` / `recordings/` | 运行与 codegen | 日志、录制脚本 |
| `scratch/` | 临时脚本 | 个人草稿，不入库 |

> `allure/` **不是产物**——它是仓库自带的 Allure CLI 2.26.0（`allure/bin/allure.bat`），CI 与 `main.py` 都依赖它，勿删。

---

## 9. 环境与依赖说明

- **CI 统一 Python 3.11**；**本地约定 `py -3.9`**（Windows）。CI 与本地需保持语法兼容（勿写 3.10+ 语法）。
- 主依赖清单：`venv_requirements.txt`（UI/工具链）、`backend/requirements.txt`（服务）、`test_case/API auto script/requirements.txt`（API 套件）、`requirements-kb.txt`（DOM 知识库可选，会拉 torch ~2GB）。
- ⚠️ **Python 3.9 安装注意**：`venv_requirements.txt` 是 3.11 的 freeze，其中
  `psycopg2-binary==2.9.13`、`pandas==3.0.2`、`grpcio==1.78.0`、`grpcio-status==1.71.2`
  均要求 ≥3.10。在 3.9 上安装需放宽为 `psycopg2-binary==2.9.12`、`pandas<3`、`grpcio`/`grpcio-status` 不钉版本。
- **JAVA_HOME**：跑 Allure CLI 需 JRE 8+；`JAVA_HOME` 必须指向 JDK 根目录（不是 `bin`）。
- 三账号登录态靠 `cookie_*.json`（不入库）；`.env` 与 `backend/.env` 存密钥（均已 gitignore）。
