# config/environments/

环境变量目录。

## 文件清单

| 文件 | 用途 | 是否入库 |
|---|---|---|
| `Global.yaml.template` | 全局变量模板（含 LIVE JWT + DB 密码） | ✅ 入库 |
| `Release.yaml.template` | Release 环境模板 | ✅ 入库 |
| `Staging.yaml.template` | Staging 环境模板 | ✅ 入库 |
| `Production.yaml.template` | Production 环境模板 | ✅ 入库 |
| `Local.yaml.template` | 本地 mock 环境模板 | ✅ 入库 |
| `*.yaml`（去掉 .template 后缀的） | 实际生效配置，**含 LIVE 凭据** | ❌ `.gitignore` 排除 |
| `.env.example` | 占位符变量名清单（无真实值） | ✅ 入库 |
| `.env` | 本机实际环境变量值（含真实凭据） | ❌ `.gitignore` 排除 |
| `_runtime_tokens.yaml` | 运行期 token 缓存（用例产出） | ❌ `.gitignore` 排除 |

## 首次部署到新机器

```bash
cd config/environments/

# 1. 复制模板，生成实际生效的 yaml
for t in *.yaml.template; do cp "$t" "${t%.template}"; done

# 2. 复制 .env 模板并填值
cp .env.example ../../.env       # 工程根目录 .env
# 用编辑器打开 .env，按 .env.example 注释把每个 *required* 字段填上

# 3.（可选）目录级 .env 也可生效：cp .env.example .env
#    优先级：shell env > 工程根 .env > 本目录 .env

# 4. 跑一条最便宜的用例确认占位符解析成功
cd ../..
python3 run_suite.py suites/linda.yaml --case-ids 测试用例短标识
```

## 占位符规则

`config/env_loader.py` 在加载 YAML 时会把任何字符串里的 `{{VAR}}` 替换为
`os.environ['VAR']`。**未设置时直接抛 `ConfigError`**，避免静默成空值。

占位符语法示例（见 `Release.yaml.template` 第 8 行）：

```yaml
variables:
  token: 'Bearer {{RELEASE_TOKEN}}'           # ← 这就是占位符
  release_sql_password: '{{RELEASE_SQL_PASSWORD}}'
```

支持：
- 大写字母、数字、下划线（`[A-Z0-9_]+`）
- 多个占位符可在同一字符串内混排：`Bearer {{A}}.{{B}}.{{C}}`

不支持：
- 默认值 `{{VAR|default}}`：故意不引入。失败应当显式上报，而不是用错误凭据走错环境。

## 加新变量流程（贡献者）

1. 在 `Global.yaml.template` 或目标 env 的 `.template` 中插入 `{{NEW_VAR}}`
2. 在 `.env.example` 加同名 `NEW_VAR=`（带必要的注释）
3. 本地 `.env` 同步加 `NEW_VAR=<value>`
4. 若该字段含 LIVE 凭据，PR review 时**只看 .template 和 .env.example**——yaml 实体在 .gitignore 下，绝对不能误推到 origin

## 凭据轮换

只需修改本地 `.env` 后重启进程。YAML 实体不动。
