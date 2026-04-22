# API / UI Workflow Scripts

本目录存放可通过 YAML 调用的 Python 工作流脚本，供 QA 直接调用后端 API 满足测试前置条件，或执行 UI 难以完成的操作。

## 调用方式

### 方式一：专用 Action（推荐）

直接使用 `actions/base.py` 中注册的专用 action，**自动使用 Playwright browser 的认证状态**（cookie + JS 动态生成的 auth header），无需手动配置 token：

```yaml
test_step:
    # 复制 Post（两步：verify + execute）
    duplicate_post: { post_id: "xxx", capture_key: "cloned_post_id" }

    # 后续步骤可通过 ${cloned_post_id} 引用返回值（待 base.py 支持变量替换后可用）
```

**为什么不用 subprocess + requests？**
Katana 后端使用 JS 动态生成 JWT token（每次请求都不同），无法从 cookie/localStorage 静态读取。专用 action 使用 Playwright `page.request` API，自动共享浏览器页面的认证状态。

### 方式二：通用 Wrapper（已废弃）

```yaml
test_step:
    run_workflow_script: { script: "xxx.py", args: { key: "value" } }
```

> subprocess + requests 方案已不支持动态 token 获取，不推荐新脚本使用。

## 目录结构

```
api/
└── ui_workflow/
    ├── README.md           # 本文件
    ├── __init__.py         # 包初始化（勿删）
    ├── api_token.txt       # Token 文件（已 gitignore，勿提交）
    └── *.py                # 工作流脚本
```

## 新增专用 Action 流程

1. 在 `actions/base.py` 中定义函数 `def xxx_action(page: Page, v: dict)`
2. 在 `actions/__init__.py` 中导入并注册到 `ACTIONS` 字典

## 已有 Action / 脚本

| Action / 脚本 | 用途 | 参数 |
|---------------|------|------|
| `duplicate_post` **(action)** | 复制 Post（两步 verify + execute） | `post_id`（必填），`capture_key`（可选，默认 `cloned_post_id`） |
| `duplicate_post.py` **(废弃)** | 旧脚本，请用 action | — |

## Token 配置（仅用于旧脚本 fallback）

新脚本不需要配置 token。

旧脚本需要身份认证 Token（两种方式，按优先级）：

1. **Playwright browser**（自动）：action 使用 `page.request`，自动携带浏览器认证
2. **本地文件**（fallback）：`api_token.txt`（不要 commit，已在 `.gitignore` 中忽略）

## Token 踩坑记录

> Katana 前端使用 Passport.js 将 JWT 序列化为 cookie（`release_katana_web_auth_token`），前端 JS 反序列化后动态注入 `Authorization: Bearer eyJ...` header 发 API。
>
> 因此：
> - `release_katana_web_auth_token` cookie 值是**序列化对象**，不是 JWT，直接用会 401
> - 真正的 JWT 存在于**浏览器运行时 JS 内存**中，无法静态读取
> - 解决方案：用 Playwright `page.request` API 劫持请求，自动携带 JS 动态注入的 header
