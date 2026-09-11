# 挑选用例 / 建测试套 速查

146 条用例以**纯脚本方式**管理在 `tests/`（目录即分组，文件名即用例 slug）。
用例元数据由 `case_index.py` 扫描 `tests/` 自动抽取，**不再依赖 Apifox 运行时**。

## 1) 命令行直接挑（最快）

```bash
# 按目录名（支持子串，父子目录一起选中）
pytest tests/ --folder "Login flow"
pytest tests/ --folder "Event and ticket and redeemed"   # 含全部子目录

# 按 tag（AND 语义，必须全部命中）—— 推荐
pytest tests/ --tags p0,account                 # 优先级 P0 且属于 account 目录
pytest tests/ --tags suite:linda               # Linda 日常回归集（82 条）
pytest tests/ --tags suite:lury                # Lury 日常回归集（47 条）

# 按 func slug / 旧 Apifox id（兼容）
pytest tests/ --case-ids test_linda_t917_verify_in_payment_methods_it_can_add_or_delete_new_cards
pytest tests/ --case-ids 6112669,8712026

# 按 pytest 原生 marker（conftest 自动生成）
pytest tests/ -m "p0"                  # 优先级 P0
pytest tests/ -m "folder_module"       # Module 目录
pytest tests/ -m "case_6112669"        # 单条（旧 id，仅可追溯）

# pytest 原生方式
pytest "tests/Login flow/"             # 按路径
pytest -k "Analytics"                  # 按名字关键字
```

> 说明：每条用例自动获得 tag `p<priority>`、`folder_<slug>`、`suite:linda`/`suite:lury`（仅对应套成员）。
> 用例文件为 `test_<slug>.py`，例如 `tests/Account/test_linda_t1569_verify_the_consumer_can_follow_a_shop.py`。

## 2) 只看不跑

```bash
pytest tests/ --folder "Login flow" --list-cases    # 列出 目录/名称/标签
python run_suite.py suites/smoke.yaml --dry-run     # 列出某套会跑哪些
```

## 3) 测试套文件（推荐用于固定场景）

放 `suites/*.yaml`，然后：

```bash
python run_suite.py --list                    # 查看已有套
python run_suite.py suites/linda.yaml         # 跑
python run_suite.py suites/linda.yaml --dry-run   # 只看
python run_suite.py suites/readonly.yaml --collect
```

套文件格式（include 任一命中即选中，exclude 优先）：

```yaml
name: my-suite
description: 说明
include:
  folders:            # 目录路径包含任一即选中（OR）
    - Login flow
    - Analytics
  tags:               # 必须全部命中（AND）
    - suite:linda
  names:              # 逐条列出用例名（推荐用于固定回归集：一眼看清包含哪些、增删直观）
    - Precondition - obtain all accounts token
    - Verify partner can search campaign on campaign list
  case_ids:           # func slug 或旧 Apifox id
    - test_yuxiao_t2668_...
  markers:            # p0 / p1 / p2 / folder_<slug> / case_<id>
    - p0
exclude:              # 排除优先
  folders:
    - Consumer Purchase flow
  tags:
    - suite:lury
pytest_args:
  - "-v"
```

现有套：

| 套 | 条数 | 说明 |
|---|---|---|
| `linda.yaml` | 82 | Linda 日常回归集，逐条列出用例名（`include.names`），便于查看/增删 |
| `lury.yaml` | 47 | Lury 日常回归集，逐条列出用例名（`include.names`），便于查看/增删 |
| `readonly.yaml` | 17 | 只读安全集，不产生脏数据（按目录） |
| `smoke.yaml` | 7 | 登录链路 + 只读查询，最快验证环境 |
| `web_ui_test.yaml` | 2 | 从 Web UI 保存的临时套（旧 id 形式，待迁移） |

> `linda.yaml` / `lury.yaml` 已改为逐条列出用例名（`include.names`），取代原先的 `tags: [suite:linda/lury]` 整组引用——一眼可见包含哪些用例、增删更直观。
> 原 Apifox 数字 id 同步文件已移入 `suites/_legacy_apifox/`。

## 4) 增量迁移（可选，仅在 Apifox 有更新时）

```bash
python apifox_migrate.py fetch --ids 6112669,8712026   # 只重拉指定用例
python apifox_migrate.py convert --ids 6112669         # 只重新生成
python apifox_migrate.py convert --all                 # 纯本地全量重建（不调 API）
```

新增用例请用脚手架（自动建目录 + 注入 NAME/TAGS/PRIORITY/CASE_ID 元数据）：

```bash
python new_case.py --folder Account --name "Verify xxx" --priority 1 --tags account
```

## 自动 tag / marker 一览

`conftest.py` 根据 `case_index.scan_tests()` 给每条用例自动打标：

| tag / marker | 例 | 来源 |
|---|---|---|
| `p<priority>` | `p0` / `p1` / `p2` | 用例 `PRIORITY` |
| `folder_<slug>` | `folder_login_flow` | 所在目录（小写下划线） |
| `suite:linda` / `suite:lury` | `suite:linda` | 原 Apifox 套成员关系 |
| `case_<id>` | `case_6112669` | 旧 Apifox id（仅可追溯，运行不依赖） |

## 注意

- 跑 `-m p0` 或全量会触发**真实写操作**（下单/退款/建帖/结算），会污染 Release 共享测试账号。
  先跑 `readonly` / `smoke` 确认环境正常。
- 运行请用**受管 Python 3.13**：`/Users/a123456/.workbuddy/binaries/python/envs/default/bin/python`
  （系统 python3 为 3.9 + LibreSSL，跑 https 会随机 SSLEOFError）。
- 可视化 UI：`bash start_ui.sh` 后访问 `http://<LAN_IP>:8765`，数据同样来自 `case_index.scan_tests()`。
