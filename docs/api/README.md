# Katana API 文档

Katana 平台后端接口文档（由 `katana-server` 代码自动生成，每日 9:00 定时同步）。

## 文件说明

| 文件 | 说明 |
|---|---|
| `katana-server-api-docs.html` | **主交付物**：纯静态自包含 HTML（无 SwaggerUI、零渲染框架，秒开不转圈），支持按模块浏览、搜索、折叠、curl 示例、数据模型，浏览器打开即用 |
| `katana-server.openapi.yaml` | OpenAPI 3.0.3 规范源文件（可导入 Apifox / Postman / 其他工具） |
| `katana-server.openapi.json` | 同一规范的 JSON 版 |
| `extract_controllers.py` | 从 `katana-server/src` 解析 controller 路由端点（输出 `/tmp/katana_endpoints.json`） |
| `build_openapi.py` | 组装 OpenAPI YAML/JSON（读取 `/tmp/katana_endpoints.json` + 扫描 DTO/枚举） |
| `build_html.py` | 从 openapi.json 生成纯静态交互 HTML |

## 当前统计（2026-10-23 同步）

| 指标 | 数量 |
|---|---|
| API 路径 | 940 |
| API 操作（端点） | 1063 |
| 数据模型（schemas） | 346 |
| 类定义 | 1377 |
| 枚举 | 131 |
| 功能模块 | 131 |
| servers | `https://release.katana-api.1m.app`（release 环境） |

## 如何更新（代码变更后）

```bash
cd /Users/a123456/Documents/Pear code/katana-openapi
python3 extract_controllers.py          # 解析最新 controller 端点 → /tmp/katana_endpoints.json
python3 build_openapi.py                # 生成 openapi.yaml / openapi.json
python3 build_html.py                   # 从 openapi.json 生成 katana-server-api-docs.html
cp katana-server-api-docs.html katana-server.openapi.yaml katana-server.openapi.json build_*.py extract_controllers.py "/Users/a123456/Desktop/Pear automation/docs/api/"
```
