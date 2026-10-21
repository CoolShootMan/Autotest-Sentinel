# Katana API 文档

Katana 平台后端接口文档（由 `katana-server` 代码自动生成）。

## 文件说明

| 文件 | 说明 |
|---|---|
| `katana-server-api-docs.html` | Swagger UI 交互文档（**主交付物**，浏览器打开即用：按模块浏览全部接口、查看参数/请求体/枚举、在线 Try it out） |
| `katana-server.openapi.yaml` | OpenAPI 3.0.3 规范源文件（可导入 Swagger UI / Apifox / Postman） |
| `katana-server.openapi.json` | 同一规范的 JSON 版 |
| `extract_controllers.py` | 从 `katana-server/src` 解析 controller 路由端点（输出 `/tmp/katana_endpoints.json`） |
| `build_openapi.py` | 组装 OpenAPI YAML/JSON（读取 `/tmp/katana_endpoints.json` + 扫描 DTO/枚举） |
| `build_html.py` | 从 openapi.json 生成 Swagger UI 交互 HTML |

## 如何更新（代码变更后）

```bash
cd /Users/a123456/Documents/Pear code/katana-openapi
python3 extract_controllers.py          # 解析最新 controller 端点 → /tmp/katana_endpoints.json
python3 build_openapi.py                # 生成 openapi.yaml / openapi.json
python3 build_html.py                   # 从 openapi.json 生成 katana-server-api-docs.html
cp katana-server-api-docs.html katana-server.openapi.yaml katana-server.openapi.json build_*.py extract_controllers.py "/Users/a123456/Desktop/Pear automation/docs/api/"
```
