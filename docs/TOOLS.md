# tools 工具链速查 · Tools Reference

> `tools/` 下 50+ 个独立脚本，**全部在仓库根执行**（`py -3.9 tools/<script>.py`）。
> 按用途分 9 类；标 🧪 的是历史通用件（2021–2022 遗留，仍可用但非主线），标 ⚠️ 的是会改动远端/数据的操作型脚本。

## 1. 登录态与环境

| 脚本 | 用途 |
|------|------|
| `get_all_cookies.py` | 依次登录三个测试账号，分别保存 `cookie_*.json`（登录态刷新主入口） |
| `check_auth_cookies.py` | 预检：三个 UI 测试账号的 cookie 是否仍为「已登录」 |
| `inject_cookie.py` | 生成 Playwright `browser_run_code_unsafe` 片段，用于往浏览器注入 cookie |
| `switch_env.py` | 一键替换 YAML/Python 文件里的 URL 前缀（环境切换） |
| `probe_routes.py` | 路由健康探测：区分 404 / 被踢到登录页 / 真能打开 |
| `dismiss_edu.py` | 关闭 Katana 的 EDU（应用内引导）弹窗，UI 套件前置 |

```bash
py -3.9 tools/get_all_cookies.py
py -3.9 tools/check_auth_cookies.py
```

## 2. 用例编写与定位器维护

| 脚本 | 用途 |
|------|------|
| `locator_lint.py` | YAML 用例静态检查（`--errors-only` 只看错误） |
| `locator_updater.py` | YAML 定位器批量更新 |
| `ui_snapshot.py` | DOM 快照 + diff 检测 |
| `dom_kb.py` | DOM 向量知识库：构建索引 / 相似元素查询（RAG 自愈底座） |
| `kb_capture_flow.py` | 把「点击才能到达的页面」补录进 DOM 知识库 |
| `step_capture.py` | 用例内步骤级抓取模块 |
| `step_analyzer.py` | 步骤级离线分析（替代旧 replay 引擎） |
| `paths.py` | 仓库路径单一来源（`UI_ROOT` 等），被其他脚本 import |

```bash
py -3.9 tools/locator_lint.py --errors-only
py -3.9 tools/dom_kb.py --build
```

## 3. 诊断与报告

| 脚本 | 用途 |
|------|------|
| `diagnose_failed.py` | 失败用例诊断：自动重放 + 截图 + DOM 快照 + 9 种探查 + AI RAG 建议 → HTML 报告 |
| `gen_report.py` | 生成 v4 自定义布局的 Allure 报告 |
| `patch_report.py` | 给诊断报告打补丁（补路径，供 import） |
| `allure_summary.py` | 读 allure-results JSON 统计 PASS/FAIL/BROKEN/SKIP，并回写 YAML 行内标记 |
| `parse_allure_status.py` | 从 `behaviors.json` 解析用例状态 |
| `ci_summary.py` | 生成 CI 的「完整测试结果」汇总（Job Summary + 运行页注解） |

```bash
py -3.9 tools/diagnose_failed.py
py -3.9 tools/diagnose_failed.py --allure-dir <run_id> --headed
```

## 4. ONES 用例 / 计划集成

| 脚本 | 用途 |
|------|------|
| `ones_reader.py` | 把 ONES 用例链接读成结构化 JSON / Markdown |
| `ones_writer.py` | 通过 ONES REST API 创建用例 |
| `ones_create_module.py` | 通过 REST 建用例（子）模块（body 需包一层 `{"module": {...}}`） |
| `ones_create_plan_v3.py` | UI 建测试计划 + API 关联既有用例 |
| `ones_plan_result.py` | 回写计划级「执行结果」（未执行 → passed/failed/…） |
| `ones_update_steps.py` | 批量更新用例步骤 |
| `ones_case_diff.py` | 对比两份 ONES 用例快照，判断手上用例是否最新 |
| `update_test_status.py` | ONES 测试状态更新 v5（带调试输出，UI 登录方式） |

> 凭据来自 `backend/.env`（`ONES_EMAIL` / `ONES_PASSWORD` / `ONES_AUTH_TOKEN`），不入库。

## 5. Jira 集成

| 脚本 | 用途 |
|------|------|
| `jira_reader.py` | 读 Jira 票并提炼结构化信息 |
| `jira_writer.py` | 更新 issue description / 追加评论（简化 markdown → ADF） |
| `jira_backfill_test_link.py` | 把 ONES 计划 URL 回填 Jira 自定义字段 `customfield_10090` |

## 6. 发布与仓库维护

| 脚本 | 用途 |
|------|------|
| `gh_push.py` | 经 Windows 凭据管理器推送当前分支（支持多远端、`--dry-run`、`--force-with-lease`）⚠️ |
| `gh_pr.py` | 用 GitHub REST API 开 / 合 PR（替代未安装的 `gh` CLI）⚠️ |
| `sync_personal.py` | 把 `main` 的「通用件子集」过滤后同步到个人仓（DENY 名单裁剪）⚠️ |
| `backup_memory.py` | 本地备份 `.workbuddy/memory`（记忆不入 git，仅本地快照） |

```bash
py -3.9 tools/gh_push.py --dry-run
py -3.9 tools/sync_personal.py --dry-run
```

## 7. 测试数据与页面勘查

| 脚本 | 用途 |
|------|------|
| `generate_data.py` | 生成随机测试数据 |
| `hunt_forms.py` | 扫描 Forms 页面元素（页面勘查） |
| `get_btn_coords.py` | 取 Forms 按钮坐标 |
| `measure_icons.py` | 量图标尺寸（移动端视口） |
| `figma_reader.py` | Figma 设计稿截图 |
| `figma_api_reader.py` | Figma REST API 读取（设计数据） |
| `data_process.py` 🧪 | 通用数据处理类 `DataProcess` |
| `read_file.py` 🧪 | 通用文件读取类 `ReadFile` |
| `sql_operate.py` 🧪 | SQL 操作封装 `Sqloperate` |
| `email_send.py` 🧪 | 邮件发送（`email_send(subject, content)`） |
| `encode.py` 🧪 | 请求/响应体加解密（`encode_request` / `decode_response` 等） |

## 8. 二维码 / 票券专项

| 脚本 | 用途 |
|------|------|
| `convert_qrs.py` | 图片转 Y4M 视频（供扫码用例当"摄像头输入"） |
| `trim_video.py` | 裁剪 Y4M 帧数（`num_frames`） |
| `run_ticket_c.py` | 隔离启动 Chrome 跑 Ticket C 扫码 |
| `test_ab.py` | 扫码 A/B 手动测试（指定 y4m） |
| `run_invalid_qr.py` | 用「错误活动的二维码」扫码，验证提示 "QR code is for a different event"（由 `execute_not_recognized_scan` action 调用） |

## 9. 浏览器自动化与内部辅助

| 脚本 | 用途 |
|------|------|
| `ab.py` | 可靠驱动 agent-browser 的封装（node+argv 直调，规避 PowerShell 管道假死） |
| `__init__.py` | 包标记（使 `tools` 可被 import） |

---

## 附：按场景选工具

| 我想… | 用哪个 |
|-------|--------|
| 登录态失效了 | `get_all_cookies.py` → `check_auth_cookies.py` |
| 用例跑挂了，想看原因 | `diagnose_failed.py` |
| 页面改版，定位器大面积失效 | `locator_lint.py --errors-only` → `ui_snapshot.py` → `locator_updater.py` |
| 想让 AI 认识新页面 | `kb_capture_flow.py` / `dom_kb.py --build` |
| 同步 ONES 用例 / 回写结果 | `ones_reader.py` / `ones_plan_result.py` |
| 提交前检查 YAML | `locator_lint.py` |
| 不知道怎么推代码 | `gh_push.py --dry-run`（先看再推） |
