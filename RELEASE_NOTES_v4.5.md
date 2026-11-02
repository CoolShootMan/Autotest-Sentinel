# Release Notes — v4.5 (2026-11-02)

## 一句话总结
文档补齐：从"只有 UI 主线有介绍"升级为**全仓库模块覆盖**——API 自动化、性能/缓存回归、backend、50+ 工具、三条 CI 全部有据可查，并新增模块地图与工具速查两份独立文档。

---

## 新增文档

### 1. `docs/MODULES.md` — 项目模块全景
- 一张表看清 7 个模块的**路径 / 入口 / 技术栈**
- 逐模块说明：UI、API 自动化（四层架构）、性能测试、缓存回归（`X-DB-Query-Count` 0-DB 审计）、backend（FastAPI）、tools、CI
- 运行时产物目录清单（哪些是生成物、哪些不能删，如仓库自带 `allure/` CLI）
- 环境与依赖说明，含 **Python 3.9 安装 4 个钉版本需放宽**的提示

### 2. `docs/TOOLS.md` — tools 工具链速查
- 50+ 脚本按 9 类归档：登录态与环境、用例与定位器、诊断与报告、ONES、Jira、发布同步、数据与勘查、二维码/票券、内部辅助
- 每个脚本一句话用途 + 高频命令
- 附「按场景选工具」对照表（登录态失效 / 用例挂了 / 页面改版 / 同步 ONES …）

---

## 文档更新

- `README.zh-CN.md` 升级 v4.5：
  - 新增「📦 模块一览」表（UI / API / 性能 / 缓存回归 / Backend / 工具链）
  - 新增「⚙️ CI / 每日自动化」章节（此前中文版缺失）
  - 目录结构树补全 `API auto script/`、`performance testing/`、`backend/`、`docs/`、`allure/`
- `README.md`（英文）同步：
  - Modules 表新增 Performance / Cache Regression / Backend Service / Tools 四行
  - CI 表补上 `cache-regression-daily`
  - 目录结构树同步
- `TECHNICAL_GUIDE.md` 升级 v4.5：
  - 新增「19. 多模块索引」，指到 MODULES / TOOLS / API ONBOARDING
  - 16.1 工具总览标注"完整清单见 docs/TOOLS.md"
- `docs/MODULES.md` 顶部提供「文档地图」，明确各文档适合谁看

> 此前 `test_case/API auto script/ONBOARDING.md`（530 行）已存在但根文档无入口，本次在 README、技术指南、模块地图三处建立链接。

---

## 环境说明（非代码变更）

- **CI 统一 Python 3.11**；本地约定 `py -3.9`。
- ⚠️ `venv_requirements.txt` 为 3.11 的 freeze，在 3.9 上安装时需放宽四个钉版本：
  `psycopg2-binary==2.9.13` → `2.9.12`、`pandas==3.0.2` → `<3`、`grpcio` / `grpcio-status` 不钉版本。
- Allure CLI 已随仓库提供（`allure/bin/allure.bat`，2.26.0），只需 Java 8+；`JAVA_HOME` 必须指向 JDK **根目录**（不是 `bin`）。

---

## 升级指南

1. 拉取代码（无需新增依赖）
2. 先读 `docs/MODULES.md` 建立全仓库认知，再按角色深入：
   - UI → 根 README + `TECHNICAL_GUIDE.md`
   - API → `test_case/API auto script/ONBOARDING.md`
   - 日常排障 → `docs/TOOLS.md`
3. 新增模块/工具时，按 `docs/MODULES.md` 末尾约定同步更新文档

---

## 文件变更

```
docs/MODULES.md          | 新增（模块全景）
docs/TOOLS.md            | 新增（工具速查）
README.zh-CN.md          | 模块一览 + CI 章节 + 目录树 + 版本号
README.md                | Modules/CI 表 + 目录树
TECHNICAL_GUIDE.md       | 版本号 + §19 多模块索引 + §16.1 指向
RELEASE_NOTES_v4.5.md    | 新增（本文件）
```
