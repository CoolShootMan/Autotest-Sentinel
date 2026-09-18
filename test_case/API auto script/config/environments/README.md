# config/environments/

环境变量目录。

> ## ⚠️ 2026-09-18 政策变更
>
> 仓库已从 **public 转为 private**，按团队约定 **`Global.yaml` 与 `Release.yaml`
> 的实体文件改为入库**，目的是让同伴 `git clone` 后**零配置直接跑**。
>
> 这两个实体里的凭据写的是**实值**（不是 `{{占位符}}`），所以同伴**不需要 `.env`**，
> 也不需要 `cp *.yaml.template`。
>
> 变更前它们由 `.gitignore` 排除；变更后 `.gitignore` 只保留
> `Staging/Production/Local`、`.env`、`_runtime_tokens.yaml` 的排除规则。

## 文件清单

| 文件 | 用途 | 是否入库 |
|---|---|---|
| `Global.yaml` | 全局变量（含 LIVE 凭据，**实值**） | ✅ **入库** |
| `Release.yaml` | Release 环境变量（含 LIVE 凭据，**实值**） | ✅ **入库** |
| `Global.yaml.template` / `Release.yaml.template` | 占位符版模板（结构清单，无真值） | ✅ 入库 |
| `Staging.yaml.template` / `Production.yaml.template` / `Local.yaml.template` | 其它环境模板 | ✅ 入库 |
| `Staging.yaml` / `Production.yaml` / `Local.yaml` | 其它环境实体（**当前全仓无任何用例引用**） | ❌ 排除 |
| `.env.example` | 占位符变量名清单（无真实值） | ✅ 入库 |
| `.env` | 本机实际环境变量值 | ❌ 排除 |
| `_runtime_tokens.yaml` | 运行期角色 JWT 缓存（120s 寿命，跑用例时自动再生） | ❌ 排除 |

> 为什么 `_runtime_tokens.yaml` 不入库：它是 `core/token_refresh.py` 在跑用例时
> **自动生成并续期**的（`env_loader.save_runtime_tokens` 会按需建目录写入），
> 入库一份会过期的 JWT 不但没用，还可能盖住新签发的令牌。

## 首次部署到新机器

### A. 只跑 Release（默认）—— 零配置

147 条用例全部声明 `ENV_NAME = "Release"`，`config/settings.py` 的默认值也是
`Release`，而 `Global.yaml` / `Release.yaml` 已随仓库下发：

```bash
git clone <repo> && cd <repo>/test_case/API\ auto\ script
python3 run_suite.py suites/linda.yaml
```

不需要 `cp`、不需要 `.env`、不需要任何环境变量。

### B. 跑 Staging / Production / Local —— 需手工生成

这几个环境的实体目前不入库（也没有用例在用）：

```bash
cd config/environments/
cp Staging.yaml.template Staging.yaml      # 打开填真值
cp Production.yaml.template Production.yaml
cp Local.yaml.template Local.yaml
```

若模板里含 `{{占位符}}`，还需按 `.env.example` 在工程根 `.env` 里补齐对应变量
（`env_loader` 在实体缺值时不会回退读模板）。

## 占位符规则

`config/env_loader.py` 在加载 YAML 时会把任何字符串里的 `{{VAR}}` 替换为
`os.environ['VAR']`。**未设置时直接抛 `ConfigError`**，避免静默成空值。

占位符语法示例（见 `Release.yaml.template` 第 8 行）：

```yaml
variables:
  token: 'Bearer {{RELEASE_TOKEN}}'           # ← 这就是占位符
  release_sql_password: '{{RELEASE_SQL_PASSWORD}}'
```

注意：**模板里有占位符，实体里没有** —— 实体是已经解析成真值的版本，
所以加载实体时不需要任何环境变量。

支持：
- 大写字母、数字、下划线（`[A-Z0-9_]+`）
- 多个占位符可在同一字符串内混排：`Bearer {{A}}.{{B}}.{{C}}`

不支持：
- 默认值 `{{VAR|default}}`：故意不引入。失败应当显式上报，而不是用错误凭据走错环境。

## 分层与合并优先级

实际生效的变量按下面顺序合并（后层覆盖前层）：

```
1. config/environments/Global.yaml              ← 入库
2. config/environments/<ENV_NAME>.yaml          ← Release.yaml 入库
3. config/environments/_runtime_tokens.yaml     ← 运行期自动再生，不入库
4. <case>.vars.yaml                             ← 用例私有，最高
```

`base_url` 单独抽出（不在 `variables` 里），因为它是请求拼接的根。

## 加新变量流程（贡献者）

分两种情况：

**1. 跨环境通用、且不含凭据的变量**（如各用例的 `T2487_post_id`、`T4259_event_id`）

- 直接写进 `Global.yaml` 或 `Release.yaml`，PR 会带上 → 同伴立即拿到；
- **同时**补进对应的 `.template`，让"仓库里该有哪些键"保持可见。

**2. 含 LIVE 凭据的新字段**

- 在 `.template` 里写占位符 `{{NEW_VAR}}`；
- 在 `.env.example` 加同名 `NEW_VAR=`（带注释）；
- 若 Release 环境必须用到它，也写进 `Release.yaml` 实体并同步 `.template`；
- PR review 时对照 `.template` 检查键是否齐全（结构对不上会导致同伴拉到就跑不起来）。

## 凭据轮换

- `Global.yaml` / `Release.yaml` 实体**已入库** → 轮换凭据时**必须连带提交一份改动**，
  否则同伴拉到的仍是旧值；同时轮换 `.template` 无需改动（那里只有占位符名）。
- Staging/Production/Local（走 `.env` 方案）仍是修改本地 `.env` 后重启进程，YAML 实体不动。
