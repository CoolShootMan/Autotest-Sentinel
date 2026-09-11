# Autotest-Sentinel · API Automation Onboarding

> 目标读者：第一次接触本仓库的 QA / SDET 同事。
> 阅读时长：约 20 分钟，建议边看边跟着命令敲一遍。

---

## 0. 仓库在哪 / 它是什么

| 维度 | 说明 |
|---|---|
| 仓库 | `https://github.com/CoolShootMan/Autotest-Sentinel.git` |
| 子目录 | `test_case/API auto script/`（所有命令默认在此执行） |
| 默认分支 | `main`；日常开发分支 **`linda`**（GitFlow） |
| 任务来源 | 历史 Apifox 测试集 → 已迁移为本仓 pytest 用例 |
| 远程基线 | `release.pear.us`（Release 环境），其它 env 见 `config/environments/` |
| 触发方式 | 本地手动跑 / 后续接 Jenkins 手动触发 |

> 项目里所有"敏感"文件（**LIVE token、密码、SQL 密码、`_apifox_export/*`**）都
> 由父目录的 `.gitignore` 排除，**绝对不能**提交到 origin。本文档也会反复强调。

---

## 1. 30 秒全景图

```
┌────────────────────────────────────────────────────────────────┐
│  tests/<NN_Folder>/test_<slug>.py      ← 用例（脚本）          │
│        │                                                       │
│        │ 依赖                                                  │
│        ▼                                                       │
│  ┌──────────┐    ┌──────────┐    ┌───────────────────────┐    │
│  │  api/*   │ →  │  core/*  │ →  │  config/env_loader.py │    │
│  │ 业务门面 │    │ HTTP/ctx │    │ 环境 YAML + 占位符渲染 │    │
│  └──────────┘    └──────────┘    └───────────────────────┘    │
│       ▲              ▲                    ▲                    │
│       │              │                    │                    │
│   release.pear.us   Context        Global / Release /         │
│   pearapp.com      fixture         *_runtime_tokens.yaml      │
└────────────────────────────────────────────────────────────────┘
                ▲
                │   python run_suite.py suites/linda.yaml
                │
        pytest (managed python 3.13)
                │
                ▼
        results/runs/<run_id>/ + results/latest
```

记忆口诀：**tests 写用例 · core 做执行 · api 做门面 · config 决定环境**。

---

## 2. 环境准备

> 本节默认面向 **macOS** 团队成员（项目已从 Windows/WSL 迁到 mac）。
> Windows 同事需要用 WSL2 + Ubuntu 22.04，工具对应替换；mac 用户照抄即可。

### 2.0 工具清单

按"装不装跑得动"分三档。**硬性依赖**缺一个就跑不起来；**强烈建议**是日常体验
/ 团队协作必备；**可选**是锦上添花。

#### 2.0.1 硬性依赖（必装）

| 工具 | 版本 | 用途 | 安装 / 验证 |
|---|---|---|---|
| **Git** | ≥ 2.30 | 拉代码、PR、归档 | `brew install git` · `git --version` |
| **Python** | ≥ 3.10 | 跑 pytest / run_suite.py | 见 §2.1，推荐托管 3.13 |
| **pip** | ≥ 22 | 装 requirements | mac 自带，跟随 Python 升级 |
| **curl** | 系统自带 | OAuth、SSO 抓 token、临时探测 | `curl --version` |
| **make**（可选但建议） | 系统自带 | 后期 CI / 本地脚本可能要 `make` | `make --version` |

#### 2.0.2 强烈建议

| 工具 | 推荐 | 用途 | 安装 |
|---|---|---|---|
| **iTerm2** | 最新版 | 终端（mac 自带 Terminal 也行，但 iTerm2 切分屏体验好很多） | https://iterm2.com |
| **Homebrew** | 最新版 | macOS 包管理统一入口 | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| **VS Code** 或 **PyCharm CE** | 任意稳定版 | IDE；VS Code 配 Python 扩展即可 | https://code.visualstudio.com |
| **VS Code 扩展**（如用 VS Code） | — | Python、Pylance、YAML、GitLens、Error Lens | 装好后搜名字一键 install |
| **DBeaver** 或 **TablePlus** | 最新版 | 查 PostgreSQL / MySQL 库（用例里 `run_db` 经常要核对） | https://dbeaver.io · https://tableplus.com |
| **Slack** | 桌面端 | 团队通知、CI 告警 | 公司自带安装包 |
| **Apifox**（账号需申请） | 桌面端 | **原测试用例出处**——用 `case_id` 溯源、查接口原始定义、看 Mock | 找 TL 申请账号（项目 ID 5446866） |
| **Chrome** | 最新版 | 看 Allure 报告、UI 验证 | https://google.com/chrome |

#### 2.0.3 可选（按需）

| 工具 | 适用场景 | 安装 |
|---|---|---|
| **python-dotenv** | 让 `.env` 文件在 `python run_suite.py` 时**自动**生效；不装就只能 `export` 到 shell | `pip install python-dotenv`（见 §2.2） |
| **Allure CommandLine** | 本地渲染 Allure 报告（默认走 HTTP 共享也够用） | `brew install allure` |
| **Docker Desktop** | 跑本地 mock 后端、隔离测试数据库 | https://docker.com/products/docker-desktop |
| **Postman / Insomnia** | 临时手敲一条请求调试；日常用 `ctx.api.*` 即可 | 官网下载 |
| **WorkBuddy / agent-browser** | 跑 UI 自动化（`Autotest-monster.git` 那个项目要用） | 公司内部工具，找 TL |
| **PixPin / ShareX** | 截图打 ticket | 公司内常用哪个装哪个 |
| **Jenkins 浏览器访问** | 触发 CI 流水线（本项目 Jenkins 是**手动触发**模式） | 找 DevOps 要地址（默认本机 `http://localhost:8080`） |
| **局域网 IP 工具**（mac 自带 `ifconfig` 够用） | 查看本机 IP 让别人访问你的 Allure 报告 | 系统自带 |

#### 2.0.4 macOS 系统级准备

```bash
# 1) 命令行工具（Git 之外还需要一些编译工具链）
xcode-select --install

# 2) 同意 license（如已装 Xcode）
sudo xcodebuild -license accept

# 3) 关掉 macOS 全局 HTTP 代理（如果公司有 PAC/WPAD），避免 requests SSL 握手失败
#    系统设置 → 网络 → 详情 → 代理 → 关掉"自动代理发现" / "HTTPS 代理"
#    （已踩过坑：开着全局代理会让 release.pear.us 接口随机 SSL 报错）
```

#### 2.0.5 一键自检脚本

第一次装完后跑这个，确认环境就绪：

```bash
echo "== git ==" && git --version
echo "== python ==" && python3 --version     # 系统 python，只看版本
echo "== managed python ==" && /Users/a123456/.workbuddy/binaries/python/envs/default/bin/python --version 2>/dev/null || echo "（未安装托管 Python，找 TL）"
echo "== pip ==" && python3 -m pip --version
echo "== curl ==" && curl --version | head -1
echo "== brew ==" && brew --version | head -1
echo "== docker (可选) ==" && docker --version 2>/dev/null || echo "（跳过）"
echo "== allure (可选) ==" && allure --version 2>/dev/null || echo "（跳过）"

# 期望输出（版本号可以不同）：
# == git ==
# git version 2.39.x
# == python ==
# Python 3.9.x                       ← 系统 python，不必是 3.10+
# == managed python ==
# Python 3.13.x                      ← 托管 python，必须 ≥ 3.10
# == pip ==
# pip 23.x
# == curl ==
# curl 8.x
# == brew ==
# Homebrew 4.x
```

如果 **managed python** 那行打印"未安装"，请联系 TL——**不能**只用系统 Python，
否则一上来就会撞上 PEP 604 报错。

### 2.1 Python（强约束）

- **必须 Python ≥ 3.10**：本仓大量使用 PEP 604 `X | None`、pytest 9。
- macOS 自带的 `python3 = 3.9` 会在 import 阶段直接抛 `TypeError: unsupported operand type(s) for |`。
- 推荐直接用**托管 Python**：

  ```bash
  /Users/a123456/.workbuddy/binaries/python/envs/default/bin/python --version
  ```
  > `run_suite.py` 会在 sys.version < 3.10 时**自动 re-exec 到上面这个路径**，
  > 所以日常你只管 `python run_suite.py suites/linda.yaml` 即可。

### 2.2 安装依赖

```bash
cd "/Users/a123456/Desktop/UI Automation/test_case/API auto script"

python -m pip install -r requirements.txt     # pytest / requests / sqlalchemy / psycopg2 / pymysql
# 可选（让 .env 自动生效；不装也能跑，只需 export 到 shell 即可）
python -m pip install python-dotenv
```

### 2.3 拉代码

```bash
git clone https://github.com/CoolShootMan/Autotest-Sentinel.git
cd Autotest-Sentinel/test_case/API\ auto\ script
git checkout linda          # 日常在 linda 上开发
```

---

## 3. 首次部署到本机（必读）

### 3.1 生成实际生效的环境配置

仓库里只有 `*.yaml.template`（已脱敏、可入库），本机需要：

```bash
cd config/environments/

# 1) 从模板生成实际生效的 YAML
for t in *.yaml.template; do cp "$t" "${t%.template}"; done

# 2) 生成 .env 占位（项目根 / 本目录都可以）
cp .env.example ..

# 3) 用编辑器打开项目根的 .env，按注释把 *required* 的变量填上
vim ../.env
```

**优先级（高 → 低）**：
1. shell 环境变量
2. 项目根 `.env`（推荐这个，跟着仓库走）
3. `config/environments/.env`

### 3.2 跑一条最便宜的用例验证

```bash
cd "../.."
python run_suite.py suites/linda.yaml --case-ids T2302
```

预期看到 `1 passed`。如果报 `ConfigError: …引用了未设置的环境变量 {{ XXX }}`，
说明 `.env` 没填全，回到上一步补齐。

### 3.3 接入编辑器 / IDE

- VS Code / PyCharm 直接打开 `test_case/API auto script/`。
- Python 解析器选 **托管 Python 3.13**（第 2.1 节路径）。
- 类型检查推荐 `mypy --ignore-missing-imports core/ api/`。

---

## 4. 目录结构速览

| 路径 | 作用 | 你会改它吗 |
|---|---|---|
| `tests/<NN_Folder>/test_*.py` | 155 条已迁移用例（22 个业务文件夹） | ✅ 主要改这里 |
| `tests/<NN_Folder>/test_*.vars.yaml` | 用例私有变量（如 `account_email_curator`） | ✅ 经常 |
| `suites/linda.yaml` 等 | 套件描述（`include.names` 逐条列出用例） | ✅ |
| `core/` | HTTP 客户端、上下文、断言、归档 | ⚠️ 谨慎 |
| `api/` | 业务门面（auth / events / posts / orders …） | ⚠️ 谨慎 |
| `config/env_loader.py` | YAML + 占位符 `{{VAR}}` 渲染 | ⚠️ 谨慎 |
| `config/environments/*.yaml.template` | **入库的脱敏模板** | ⚠️ PR review |
| `config/environments/*.yaml` | 本机 LIVE 凭据 | ❌ 不要提交 |
| `config/environments/_runtime_tokens.yaml` | T0000 用例产出，被其它用例依赖 | ❌ 不入库 |
| `data/` | 静态夹具（fixture 数据 / SQL 种子） | ✅ |
| `results/runs/<run_id>/` | 本次运行的归档（默认开启） | ❌ 不入库 |
| `results/RUNS.md` | 运行历史索引（按行追加） | ❌ 不入库 |
| `tools/migration/` | 一次性迁移脚本（已退役，仍保留可追溯） | ❌ |
| `_retired_20260910/` | 退役中间产物 | ❌ 不入库 |
| `_apifox_export/` | 历史 Apifox 导出（含 LIVE 凭据） | ❌ 不入库 |

---

## 5. 日常命令（复制即用）

> 所有命令均在 `test_case/API auto script/` 下执行。

### 5.1 跑套件（推荐入口）

```bash
# 列出所有可用套件
python run_suite.py --list

# 跑 Linda 主套件（约 80 条精选用例）
python run_suite.py suites/linda.yaml

# 只跑一个文件里的若干条
python run_suite.py suites/linda.yaml --case-ids T2302,T0000

# 只先看会跑哪些，不真跑
python run_suite.py suites/linda.yaml --dry-run
```

### 5.2 直接用 pytest（更灵活）

```bash
# 全量
python -m pytest

# 按文件夹
python -m pytest "tests/01_Login flow"

# 按 marker（自动 marker：folder_<slug> / p<priority> / case_<id>）
python -m pytest -m "p0 and login_flow"

# 按关键字
python -m pytest -k "t2302 or t0000"

# 看可选用例清单（不执行）
python -m pytest --collect-only -q
```

### 5.3 切换环境 / 调参

| 环境变量 | 默认值 | 含义 |
|---|---|---|
| `API_ENV` | `Release` | 选 `Release / Staging / Production / Local` |
| `API_TIMEOUT` | 45 | 单请求超时秒 |
| `API_RETRIES` | 3 | 瞬时故障重试次数（仅 429/5xx） |
| `API_LOG_LEVEL` | `INFO` | DEBUG/INFO/WARNING |
| `API_LOG_BODY` | `false` | 设为 `1` 打印请求/响应体 |
| `API_RUN_LABEL` | — | 给本次运行打标签（套件名自动传入） |

```bash
API_ENV=Staging API_LOG_BODY=1 python -m pytest "tests/01_Login flow"
```

### 5.4 看运行归档

每次 pytest 结束（在 conftest 中默认开启归档）：

```
results/
├── RUNS.md                                          # 历史索引（一次一行）
├── latest → runs/2026-09-11_1129_linda/             # 软链（最近一次）
├── http.log  → runs/2026-09-11_1129_linda/http.log  # 软链
└── runs/2026-09-11_1129_linda/
    ├── summary.md      # 一句话 PASS/FAIL + 失败明细
    ├── failures.json   # 仅失败 case 的结构化数据
    ├── meta.json       # 运行配置（env / tag / 时长 / commit）
    ├── junit.xml       # pytest 标准输出
    └── http.log        # 完整 HTTP 报文
```

关掉归档：`python -m pytest --no-archive`（`run_suite.py` 透传）。

---

## 6. 写一条新用例

> 不需要 Apifox。本仓已完全脚本化。

### 6.1 用脚手架生成骨架

```bash
python new_case.py \
    --folder "Login flow" \
    --name "Verify login with invalid password" \
    --tags p1,login \
    --priority 1
```

生成 `tests/01_Login flow/test_login_with_invalid_password.py`，已包含：
- 模块级元数据 `NAME / TAGS / PRIORITY / CASE_ID`（`CASE_ID=None` 表示手工新写）
- `ENV_NAME = "Release"`
- 一个空的 `test_<slug>(ctx)` 函数

### 6.2 在骨架里写步骤

最小可用模板：

```python
from core.assertions import expect

NAME = "Verify login with invalid password"
TAGS = ["p1", "login_flow"]
PRIORITY = 1
CASE_ID = None                # 手工新增 = None；迁移用例保留 Apifox 原 ID

ENV_NAME = "Release"


def test_login_with_invalid_password(ctx):
    vars = ctx                # 别名：历史写法 vars['x'] 继续可用
    # ---- step 1 ----
    resp = ctx.api.auth.sign_in(
        body='{"email": "{{account_email_invalid}}", "password": "wrong-pwd"}',
        app_headers=True,
    )
    expect(resp).json("$.code").equals("401")
    expect(resp).json("$.message").contains("invalid credentials")
```

- `ctx.api.<module>.<method>(...)`：所有业务接口都封装在 `api/` 下，`method` 与 Apifox 一致。
- `ctx.extract(name, response, "$.data.token")`：把响应里的值抽到 `ctx`，后续用例可直接 `ctx["token"]`。
- `expect(resp).json(path).<matcher>(value)`：链式断言，支持 `.equals / .contains / .is_gt / .exists` 等。
- `ctx` 既是对象也是 `MutableMapping`：`ctx["x"] = ...` / `vars = ctx; vars["x"]` 都可以。

### 6.3 已知的反模式（脚手架会自动 audit）

| 反模式 | 后果 | 正确做法 |
|---|---|---|
| `{var}` 单花括号（应为 `{{var}}`） | body 原样发出 → 400 | 永远双花括号 |
| `vars['k'] = 'k'`（占位回填自身） | 提取器翻译失败 | 用 `ctx.extract(name, resp, path)` |
| 本地 `def _get_path(...)` | 遮蔽 `core.compat._get_path` | `from core.compat import _get_path` |
| 直接调 `requests.get(...)` | 绕过重试/归档/ctx | 全部走 `ctx.api.*` |

### 6.4 让用例被某个套件收录

打开 `suites/linda.yaml`，在 `include.names` 里加一行用例名（一行一条，**所见即所得**）：

```yaml
include:
  names:
  - Verify login with invalid password       # ← 新增
  - Verify user can login with email and password
  ...
```

> 优先用 `names` 而不是 `case_ids`：可读、易 diff、AI 改写歧义少。

---

## 7. 常见陷阱 / FAQ

### 7.1 占位符渲染

- 模板里所有 `{{VAR}}` 必须在加载时存在。
- 找不到 → `ConfigError: …引用了未设置的环境变量 {{ XXX }}`；**不会**静默变空串。
- 不支持 `{{VAR|default}}`：故意不引入——失败要显式上报，宁可红线也别用错凭据走错环境。

### 7.2 重试策略

`config/settings.py`：
- `RETRY_STATUS_FORCELIST = (429, 500, 502, 503, 504)`
- **不会**重试 4xx 业务错误（如 401 / 400 / 403）。
- 仅在网络层异常时重试：`ConnectionError / Timeout / SSLError / ChunkedEncodingError`。

### 7.3 `_runtime_tokens.yaml` 是干啥的

- 由 **T0000 (Precondition - obtain all accounts token)** 写入。
- 其它用例通过 `ctx["token"]` 隐式读取，**不需要**自己写 login。
- 如果你改了 T0000 或换了一批测试账号，请重新跑 T0000 让缓存重建。

### 7.4 xfail / skip

```python
import pytest

@pytest.mark.xfail(reason="T3028: /post/simplify/shop/linda 已下线", strict=False)
def test_xxx(ctx):
    ...
```

约定：
- 接口下线、字段弃用 → `xfail`（仍跑，仍上报）。
- 跑不动 / 缺外部依赖 → `skip`。

### 7.5 macOS SSL 报错

如果你看到 `ssl.SSLCertVerificationError` / LibreSSL 相关报错：
- 系统 python 是 LibreSSL，托管 python 是 OpenSSL 3.x，**用托管的**即可。
- 不要 `brew install openssl` 再 link，那是绕远路。

### 7.6 全量套件 vs 单跑偶发不一致

偶发 500 / PATCH 顺序敏感：先单跑确认无问题，再全量复现；如果单绿全红，
通常是**环境状态污染**（前面用例改了共享数据），记录到 ticket，不要在用例里加 sleep。

### 7.7 提交前自检

```bash
# 1) 确认没有 LIVE 凭据被误推到模板
grep -rE "eyJ[A-Za-z0-9_.-]{40,}|password:\s*['\"][0-9a-fA-F]{16,}['\"]" \
    config/environments/*.template .env.example 2>/dev/null
# （应 0 行）

# 2) 确认 yaml 实体文件没被 git 跟踪
git ls-files | grep -E "config/environments/[^/]+\.yaml$" | grep -v template
# （应空）

# 3) 单跑你改动的 case
python run_suite.py suites/linda.yaml --case-ids <your ids>
```

---

## 8. 凭据轮换

只需：

1. 编辑项目根 `.env`（或 `config/environments/.env`）的对应 `KEY=value`。
2. 重启 pytest / 进程。

YAML 实体不需要动；模板不需要动。轮换后**永远不要**让真实值进入任何
`.yaml.template` / `.env.example` / `git`。

---

## 9. CI 接入建议（待办）

Jenkins / GitHub Actions 都行，最小骨架如下：

```yaml
# .github-workflows/api-smoke.yml 概念示意（尚未合并）
- name: Smoke
  env:
    API_ENV: Staging
    RELEASE_TOKEN: ${{ secrets.RELEASE_TOKEN }}
    RELEASE_SQL_PASSWORD: ${{ secrets.RELEASE_SQL_PASSWORD }}
    # ... .env.example 里全部 *required* 都要在 secrets 里
  run: |
    pip install -r requirements.txt
    python run_suite.py suites/linda.yaml
```

要点：
- secrets 名字必须与 `.env.example` 里 `KEY=` **逐字**一致（占位符大小写敏感）。
- 跑完把 `results/runs/<run_id>/summary.md` 发布成 GitHub Step Summary。

---

## 10. 出问题找谁 / 看哪里

| 现象 | 第一站 |
|---|---|
| YAML 占位符 / .env | `config/environments/README.md`（本目录有一份） |
| pytest 配置 / marker | `pytest.ini` + `case_index.py` |
| HTTP 客户端行为 | `core/http_client.py` + `core/run_archive.py` |
| 业务方法找不到 | `api/__init__.py`（`Api` 聚合所有模块） |
| 运行没产物 | 看 `conftest.py` 里 `run_archive.collect_*` 是否关掉 |
| 套件准不准 | `python run_suite.py <suite> --dry-run --collect-only` |
| 团队协作流程 | PR 提到 `linda` 分支，base = `main`，配 Squash Merge |

---

## 11. 一页速查

```bash
# 一键自检（首次部署后跑一次）
cd "test_case/API auto script"
for t in config/environments/*.yaml.template; do cp "$t" "${t%.template}"; done
cp config/environments/.env.example .env
# 然后编辑 .env 填值

# 跑一条用例
python run_suite.py suites/linda.yaml --case-ids T2302

# 跑全部主套件
python run_suite.py suites/linda.yaml

# 写新用例
python new_case.py --folder "<folder>" --name "<name>" --tags p1,x --priority 1

# 看运行归档
cat results/latest/summary.md
less results/latest/http.log
```

---

> 文档版本：v1（2026-09-11 首版）。改动本仓库公共约定时，请同步更新本文件。
