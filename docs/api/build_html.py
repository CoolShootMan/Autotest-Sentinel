#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_html.py —— Katana Server API 静态接口文档生成器（自包含单文件 HTML）
从 katana-server.openapi.json 生成纯静态、零外部依赖、零渲染框架的 HTML。
设计目标：任何浏览器秒开、不转圈；搜索 / 折叠 / 复制 curl 可用。
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(BASE, "katana-server.openapi.json")
OUT_FILE = os.path.join(BASE, "katana-server-api-docs.html")

METHOD_COLORS = {
    "get": "#61affe", "post": "#49cc90", "put": "#fca130",
    "patch": "#50e3c2", "delete": "#f93e3e", "head": "#9012fe",
    "options": "#0d5aa7", "trace": "#0d5aa7",
}


def esc(s):
    """HTML 转义"""
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def esc_attr(s):
    return esc(s).replace("'", "&#39;")


def param_rows(params):
    """参数表行 HTML"""
    if not params:
        return ""
    rows = []
    for p in params:
        name = p.get("name", "")
        loc = p.get("in", "")
        req = "是" if p.get("required") else "否"
        schema = p.get("schema", {})
        stype = schema.get("type", "")
        if not stype and "items" in schema:
            stype = "array[" + schema["items"].get("type", "?") + "]"
        desc = p.get("description", "")
        rows.append(
            f'<tr><td><code>{esc(name)}</code></td><td>{esc(loc)}</td>'
            f'<td>{esc(stype)}</td><td>{req}</td><td>{esc(desc)}</td></tr>'
        )
    return "".join(rows)


def schema_short(schema, schemas, depth=0):
    """把 schema 转成简短类型描述；避免无限递归"""
    if not schema:
        return "object"
    if "$ref" in schema:
        name = schema["$ref"].split("/")[-1]
        return f'<a class="sref" href="#schema-{esc_attr(name)}">{esc(name)}</a>'
    t = schema.get("type", "object")
    if t == "array":
        return "array&lt;" + schema_short(schema.get("items", {}), schemas, depth + 1) + "&gt;"
    if t == "object" and "properties" in schema:
        if depth > 2:
            return "object"
        props = schema["properties"]
        n = len(props)
        return f"object（{n} 字段）"
    if t == "string":
        return "string"
    if t == "integer":
        return "integer"
    if t == "number":
        return "number"
    if t == "boolean":
        return "boolean"
    if "enum" in schema:
        return "enum:" + ",".join(str(e) for e in schema["enum"][:6])
    if "example" in schema:
        return esc(schema["example"])[:80]
    return esc(t or "object")


def curl_example(method, op, path, server):
    """生成 curl 示例"""
    m = method
    # path 模板参数示例
    sample_path = path
    params = op.get("parameters", [])
    path_params = [p for p in params if p.get("in") == "path"]
    query_params = [p for p in params if p.get("in") == "query"]
    body_params = [p for p in params if p.get("in") == "body"]
    has_body = "requestBody" in op or body_params
    for p in path_params:
        sample_path = sample_path.replace(
            "{" + p.get("name", "") + "}", "{" + p.get("name", "") + "}"
        )  # 保持模板形式，另行示例
    query_str = ""
    if query_params:
        qs = "&".join(f"{p.get('name','')}=&lt;value&gt;" for p in query_params[:5])
        sep = "&" if "?" in sample_path else "?"
        query_str = sep + qs
    parts = [f"curl -X {m.upper()} \\", f'  "{server}{sample_path}{query_str}"']
    if has_body:
        parts.append('  -H "Content-Type: application/json" \\')
        parts.append('  -d \'{\\"key\\": \\"value\\"}\'')
    return "<br/>".join(parts) + "\n"


def response_blocks(op):
    """响应状态码展示"""
    resp = op.get("responses", {})
    if not resp:
        return ""
    rows = []
    for code, r in resp.items():
        desc = r.get("description", "")
        rows.append(f'<span class="rcode">{esc(code)}</span> {esc(desc)}')
    return "&nbsp;&nbsp;".join(rows) if rows else ""


def build_op_block(method, path, op, server, tag):
    color = METHOD_COLORS.get(method, "#777")
    summary = op.get("summary", "") or ""
    operation_id = op.get("operationId", "")
    params = op.get("parameters", [])
    q_params = [p for p in params if p.get("in") == "query"]
    p_params = [p for p in params if p.get("in") == "path"]
    h_params = [p for p in params if p.get("in") == "header"]
    all_rows = param_rows(p_params) + param_rows(q_params) + param_rows(h_params)
    # requestBody
    rb_html = ""
    if "requestBody" in op:
        rb = op["requestBody"]
        for mt, content in rb.get("content", {}).items():
            sch = content.get("schema", {})
            rb_html += (
                f'<p class="rb">请求体 <code>{esc(mt)}</code>：'
                f'{schema_short(sch, {})}</p>'
            )
    curl = curl_example(method, op, path, server)
    resp = response_blocks(op)
    desc = op.get("description", "") or ""

    head_id = f"op-{tag}-{method}-{path}".replace("/", "-").replace("{", "").replace("}", "")
    return f"""
<div class="op" id="{esc_attr(head_id)}" data-search="{esc_attr((method + ' ' + path + ' ' + summary + ' ' + operation_id).lower())}">
  <div class="op-head" onclick="toggleOp(this)">
    <span class="method" style="background:{color}">{method.upper()}</span>
    <code class="path">{esc(path)}</code>
    <span class="summary">{esc(summary)}</span>
    <span class="opid">{esc(operation_id)}</span>
    <span class="chev">▸</span>
  </div>
  <div class="op-body">
    {f'<p class="odesc">{esc(desc)}</p>' if desc else ''}
    {all_rows and '<h4>Parameters</h4><table class="ptable"><thead><tr><th>名称</th><th>位置</th><th>类型</th><th>必填</th><th>说明</th></tr></thead><tbody>' + all_rows + '</tbody></table>' or ''}
    {rb_html}
    {resp and f'<h4>Responses</h4><p class="resp">{resp}</p>' or ''}
    {curl and f'<h4>cURL</h4><pre class="curl">{curl}</pre>' or ''}
  </div>
</div>
"""


def build_schema_cards(schemas):
    """schemas 卡片（折叠展示字段）"""
    if not schemas:
        return ""
    cards = []
    for name, sch in schemas.items():
        props = sch.get("properties", {})
        type_txt = sch.get("type", "object")
        items_html = ""
        rows = []
        for pname, psch in list(props.items())[:40]:
            pdesc = psch.get("description", "")
            req = "是" if pname in sch.get("required", []) else "否"
            rows.append(
                f'<tr><td><code>{esc(pname)}</code></td>'
                f'<td>{schema_short(psch, schemas, 1)}</td>'
                f'<td>{req}</td><td>{esc(pdesc)}</td></tr>'
            )
        if rows:
            items_html = ('<table class="ptable"><thead><tr><th>字段</th><th>类型</th>'
                          '<th>必填</th><th>说明</th></tr></thead><tbody>'
                          + "".join(rows) + "</tbody></table>")
        elif sch.get("type") == "array":
            items_html = f'<p>数组元素：{schema_short(sch.get("items", {}), schemas, 1)}</p>'
        else:
            items_html = f'<p>类型：{esc(type_txt)}</p>'
        cards.append(
            f'<details class="schema" id="schema-{esc_attr(name)}">'
            f'<summary><code>{esc(name)}</code>'
            f'<span class="scount">{len(props)} 字段</span></summary>'
            f'<div class="schema-body">{items_html}</div></details>'
        )
    return "".join(cards)


def main():
    with open(SPEC_FILE, encoding="utf-8") as f:
        spec = json.load(f)

    server = spec["servers"][0]["url"] if spec.get("servers") else ""
    info = spec.get("info", {})
    title = info.get("title", "Katana Server API")
    desc = info.get("description", "")
    version = info.get("version", "")

    paths = spec.get("paths", {})
    schemas = spec.get("components", {}).get("schemas", {})
    tags_def = spec.get("tags", [])

    # 按模块（tag）聚合端点
    tag_ops = {}
    tag_count = {}
    for path, ops in paths.items():
        for method, op in ops.items():
            if method not in METHOD_COLORS:
                continue
            tags = op.get("tags") or ["default"]
            t = tags[0]
            tag_ops.setdefault(t, []).append((method, path, op))
            tag_count[t] = tag_count.get(t, 0) + 1

    # 模块顺序按 tags 定义
    ordered = []
    seen = set()
    for td in tags_def:
        t = td["name"]
        if t in tag_ops and t not in seen:
            ordered.append((t, tag_ops[t]))
            seen.add(t)
    for t in tag_ops:
        if t not in seen:
            ordered.append((t, tag_ops[t]))
            seen.add(t)

    sections = []
    nav = []
    for t, ops in ordered:
        nav.append(f'<a href="#tag-{esc_attr(t)}" class="nav-item">{esc(t)}'
                   f'<span class="nav-count">{tag_count[t]}</span></a>')
        blocks = "".join(
            build_op_block(m, p, o, server, t) for m, p, o in ops
        )
        sections.append(
            f'<section class="tag-section" id="tag-{esc_attr(t)}">'
            f'<h2>{esc(t)} <span class="tag-n">{tag_count[t]} 个端点</span></h2>'
            f'{blocks}</section>'
        )

    total_ops = sum(tag_count.values())
    schema_cards = build_schema_cards(schemas)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(title)} · 接口文档</title>
<style>
:root {{ --bg:#f6f7f9; --card:#fff; --border:#e2e4e8; --text:#2b2f36; --muted:#6b7280; --accent:#3b82f6; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); }}
header {{ position:sticky; top:0; z-index:10; background:#1f2937; color:#fff; padding:14px 20px; box-shadow:0 2px 8px rgba(0,0,0,.15); }}
header h1 {{ margin:0 0 8px; font-size:20px; }}
header .meta {{ font-size:12px; color:#9ca3af; }}
.search-wrap {{ display:flex; gap:8px; margin-top:10px; }}
#search {{ flex:1; max-width:520px; padding:9px 12px; border-radius:8px; border:1px solid #374151; background:#111827; color:#fff; font-size:14px; outline:none; }}
#search:focus {{ border-color:var(--accent); }}
.stats {{ font-size:12px; color:#9ca3af; margin-top:8px; }}
.wrap {{ display:flex; max-width:1440px; margin:0 auto; }}
nav {{ width:220px; flex-shrink:0; position:sticky; top:118px; height:calc(100vh - 130px); overflow-y:auto; padding:14px 10px; }}
.nav-item {{ display:flex; justify-content:space-between; align-items:center; padding:6px 10px; border-radius:6px; color:#374151; text-decoration:none; font-size:13px; margin-bottom:2px; }}
.nav-item:hover {{ background:#e5e7eb; }}
.nav-count {{ background:#e5e7eb; border-radius:10px; font-size:11px; padding:1px 7px; color:#4b5563; }}
main {{ flex:1; padding:16px 20px 60px; min-width:0; }}
.tag-section {{ margin-bottom:28px; }}
.tag-section h2 {{ font-size:18px; border-bottom:2px solid var(--border); padding-bottom:8px; margin:0 0 12px; }}
.tag-n {{ font-size:12px; color:var(--muted); font-weight:normal; }}
.op {{ background:var(--card); border:1px solid var(--border); border-radius:8px; margin-bottom:8px; overflow:hidden; }}
.op-head {{ display:flex; align-items:center; gap:10px; padding:10px 14px; cursor:pointer; flex-wrap:wrap; }}
.op-head:hover {{ background:#f9fafb; }}
.method {{ color:#fff; font-weight:700; font-size:11px; padding:3px 10px; border-radius:4px; min-width:64px; text-align:center; }}
.path {{ font-size:13px; font-weight:600; color:#0f172a; word-break:break-all; }}
.summary {{ font-size:13px; color:var(--muted); flex:1; min-width:120px; }}
.opid {{ font-size:11px; color:#9ca3af; font-family:monospace; }}
.chev {{ color:#9ca3af; transition:transform .15s; }}
.op.open .chev {{ transform:rotate(90deg); }}
.op-body {{ display:none; padding:4px 16px 16px; border-top:1px solid var(--border); }}
.op.open .op-body {{ display:block; }}
.op-body h4 {{ margin:12px 0 6px; font-size:13px; color:#374151; }}
.ptable {{ width:100%; border-collapse:collapse; font-size:12px; }}
.ptable th {{ background:#f3f4f6; text-align:left; padding:6px 8px; border:1px solid var(--border); }}
.ptable td {{ padding:6px 8px; border:1px solid var(--border); vertical-align:top; }}
.ptable code {{ background:#f3f4f6; padding:1px 5px; border-radius:4px; font-size:11px; }}
.rb {{ font-size:12px; color:#374151; }}
.resp {{ font-size:12px; }}
.rcode {{ font-weight:700; background:#eef2ff; padding:1px 8px; border-radius:4px; margin-right:8px; }}
.curl {{ background:#111827; color:#d1fae5; padding:12px 14px; border-radius:6px; font-size:12px; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; overflow-x:auto; white-space:pre-wrap; word-break:break-all; }}
.sref {{ color:var(--accent); text-decoration:none; }}
details.schema {{ background:var(--card); border:1px solid var(--border); border-radius:8px; margin-bottom:6px; }}
details.schema summary {{ padding:10px 14px; cursor:pointer; font-size:13px; display:flex; justify-content:space-between; align-items:center; }}
.scount {{ color:var(--muted); font-size:11px; }}
.schema-body {{ padding:0 14px 14px; }}
.no-result {{ padding:30px; text-align:center; color:var(--muted); display:none; }}
@media (max-width:900px) {{ nav {{ display:none; }} }}
</style>
</head>
<body>
<header>
  <h1>{esc(title)} · 接口文档</h1>
  <div class="meta">版本 {esc(version)} · 服务地址 <code>{esc(server)}</code> · {esc(desc[:120])}</div>
  <div class="search-wrap">
    <input id="search" type="search" placeholder="搜索接口：路径 / 方法 / 摘要 / operationId…"/>
  </div>
  <div class="stats" id="stats">共 {total_ops} 个端点 · {len(paths)} 条路径 · {len(schemas)} 个数据模型</div>
</header>
<div class="wrap">
  <nav id="nav">{''.join(nav)}</nav>
  <main id="main">
    <div class="no-result" id="noResult">没有匹配的接口，换个关键词试试。</div>
    {''.join(sections)}
    <section class="tag-section" id="schemas-section">
      <h2>数据模型（Schemas） <span class="tag-n">{len(schemas)} 个</span></h2>
      {schema_cards}
    </section>
  </main>
</div>
<script>
function toggleOp(el) {{ el.closest('.op').classList.toggle('open'); }}
var search = document.getElementById('search');
var ops = Array.prototype.slice.call(document.querySelectorAll('.op'));
var sections = Array.prototype.slice.call(document.querySelectorAll('.tag-section'));
var noResult = document.getElementById('noResult');
search.addEventListener('input', function() {{
  var q = this.value.trim().toLowerCase();
  var total = 0;
  ops.forEach(function(op) {{
    var hit = !q || op.dataset.search.indexOf(q) >= 0;
    op.style.display = hit ? '' : 'none';
    if (hit) total++;
  }});
  sections.forEach(function(sec) {{
    var visible = sec.querySelectorAll('.op').length === 0
      ? true : Array.prototype.some.call(sec.querySelectorAll('.op'), function(o) {{ return o.style.display !== 'none'; }});
    if (sec.id === 'schemas-section') {{
      var sc = sec.querySelectorAll('details.schema');
      var hit = !q || Array.prototype.some.call(sc, function(d) {{ return (d.textContent || '').toLowerCase().indexOf(q) >= 0; }});
      sc.forEach(function(d) {{ d.style.display = hit ? '' : 'none'; }});
      visible = hit;
    }}
    sec.style.display = visible ? '' : 'none';
  }});
  noResult.style.display = total === 0 && q ? '' : 'none';
}});
</script>
</body>
</html>"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"静态 HTML 生成完成: {OUT_FILE}")
    print(f"大小: {os.path.getsize(OUT_FILE) // 1024} KB | 端点 {total_ops} | 路径 {len(paths)} | schemas {len(schemas)} | 模块 {len(ordered)}")


if __name__ == "__main__":
    main()
