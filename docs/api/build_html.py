#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 katana-server.openapi.json 生成自包含 Swagger UI 交互文档 HTML。
用法：python3 build_html.py [输入json] [输出html]
"""
import json, os, sys

SRC = "/Users/a123456/Documents/Pear code/katana-openapi/katana-server.openapi.json"
OUT = "/Users/a123456/Documents/Pear code/katana-openapi/katana-server-api-docs.html"

def build(src, out):
    spec = json.load(open(src, encoding="utf-8"))
    spec["info"]["title"] = "Katana Server API（交互文档）"
    inline = json.dumps(spec, ensure_ascii=False).replace("</", "<\\/")

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Katana Server API - Swagger UI</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"/>
<style>
  html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
  *, *:before, *:after { box-sizing: inherit; }
  body { margin: 0; background: #fafafa; }
  .swagger-ui .topbar { display: none; }
  #swagger-ui { max-width: 1460px; margin: 0 auto; }
</style>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
window.onload = function() {
  const spec = __SPEC__;
  window.ui = SwaggerUIBundle({
    spec: spec,
    dom_id: '#swagger-ui',
    deepLinking: true,
    displayOperationId: true,
    defaultModelsExpandDepth: 1,
    defaultModelExpandDepth: 1,
    presets: [SwaggerUIBundle.presets.apis],
    layout: 'BaseLayout'
  });
};
</script>
</body>
</html>
"""
    html = html.replace("__SPEC__", inline)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML 生成完成: {out} ({os.path.getsize(out)//1024} KB)")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else SRC
    out = sys.argv[2] if len(sys.argv) > 2 else OUT
    build(src, out)
