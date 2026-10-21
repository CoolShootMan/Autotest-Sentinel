#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 katana-server 标准 OpenAPI 3.0 文档（增强版）。
输入：/tmp/katana_endpoints.json（controller 解析结果，含 jsdoc/returns/calls/http_code）
增强：默认响应码按 NestJS 语义（POST/PUT/PATCH=201，GET/DELETE=200，@HttpCode 覆盖）；
      @Query DTO 展开为具体 query 参数；@Body('field') 拆分为内联字段；
      operation description 优先取 JSDoc，其次生成 service 调用链；200 schema 由 return 表达式推断；
      DTO 字段提取行尾注释；修复 @Type(() => Date) 悬空 $ref。
"""
import os, re, json, sys

ROOT = "/Users/a123456/Documents/Pear code/katana-server/src"
ENDPOINTS = json.load(open("/tmp/katana_endpoints.json", encoding="utf-8"))

TYPE_MAP = {
    "IsString": ("string", None), "IsUUID": ("string", "uuid"), "IsEmail": ("string", "email"),
    "IsUrl": ("string", "uri"), "IsDateString": ("string", "date-time"), "IsISO8601": ("string", "date-time"),
    "IsNumber": ("number", None), "IsInt": ("integer", "int32"), "IsPositive": ("number", None),
    "IsBoolean": ("boolean", None), "IsArray": ("array", None), "IsNotEmptyObject": ("object", None),
    "IsPhoneNumber": ("string", None), "IsHexadecimal": ("string", None), "IsAlphanumeric": ("string", None),
    "IsLowercase": ("string", None), "IsUppercase": ("string", None), "IsEnum": ("string", None),
    "IsDate": ("string", "date"), "IsJsonString": ("string", None), "IsObject": ("object", None),
    "IsIn": ("string", None),
}

def collect_classes():
    """返回 {ClassName: {"fields": {...}}, "raw": 定义片段}；同时收集枚举。"""
    classes = {}
    enums = {}
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            if not fn.endswith(".ts"):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                text = open(fp, encoding="utf-8").read()
            except Exception:
                continue
            text_wo_block = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
            for em in re.finditer(r'enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]*)\}', text_wo_block):
                vals = []
                for line in em.group(2).split(','):
                    line = line.strip()
                    if not line:
                        continue
                    vm = re.match(r'[A-Za-z_][A-Za-z0-9_]*\s*(?:=\s*([^\s]+))?', line)
                    if vm:
                        v = (vm.group(1) or line.split('=')[0].strip()).strip('\'"')
                        vals.append(v)
                enums[em.group(1)] = vals
            for cm in re.finditer(r'export\s+class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{', text_wo_block):
                cname = cm.group(1)
                start = cm.end() - 1
                depth = 0
                for i in range(start, len(text_wo_block)):
                    if text_wo_block[i] == '{':
                        depth += 1
                    elif text_wo_block[i] == '}':
                        depth -= 1
                        if depth == 0:
                            body = text_wo_block[cm.start():i + 1]
                            classes[cname] = parse_class(body, enums)
                            break
    return classes, enums

def parse_class(body, enums):
    """解析类体：字段名 + 装饰器 → schema 属性；提取行尾注释。"""
    fields = {}
    field_re = re.compile(
        r'(?:^|\n)\s*((?:@[A-Za-z]+\([^;]*?\)\s*|@[A-Za-z]+\s*)+)?\s*([A-Za-z_][A-Za-z0-9_]*)\s*(\??)\s*:\s*([^;\n]+?)\s*(?=;|$)\s*(?://([^\n]*))?',
        re.M)
    for fm in field_re.finditer(body):
        decorators_src = fm.group(1) or ""
        name = fm.group(2)
        optional_mark = fm.group(3) == '?'
        type_src = fm.group(4).strip()
        comment = (fm.group(5) or "").strip()
        decs = re.findall(r'@(\w+)', decorators_src)
        schema = build_field_schema(decs, decorators_src, type_src, enums)
        if schema is not None:
            schema["required"] = not (optional_mark or "IsOptional" in decs)
            if comment:
                schema["description"] = comment
            fields[name] = schema
    return {"fields": fields}

def build_field_schema(decs, decorators_src, type_src, enums):
    schema = {}
    is_array = "IsArray" in decs or "each" in decorators_src
    if not is_array and (type_src.startswith("Array<") or type_src.endswith("[]")):
        is_array = True
    if is_array:
        items = infer_array_item(decs, decorators_src, type_src, enums)
        return {"type": "array", "items": items} if items else {"type": "array", "items": {"type": "string"}}
    for d in decs:
        if d == "IsOptional":
            continue
        if d in TYPE_MAP:
            t, fmt = TYPE_MAP[d]
            schema["type"] = t
            if fmt:
                schema["format"] = fmt
        elif d == "IsEnum":
            em = re.search(r'@IsEnum\(([A-Za-z0-9_.]+)\)', decorators_src)
            if em:
                ename = em.group(1).split('.')[-1]
                if ename in enums and enums[ename]:
                    schema["enum"] = enums[ename]
                    schema.setdefault("type", "string")
        elif d in ("ValidateNested", "Type"):
            tm = re.search(r'@Type\(\(\)\s*=>\s*([A-Za-z0-9_]+)', decorators_src)
            if tm:
                ref = tm.group(1)
                if ref == "Date":  # @Type(() => Date)：不要生成悬空 $ref，直接用 date-time
                    schema = {"type": "string", "format": "date-time"}
                    continue
                if "each" in decorators_src or type_src.startswith(("Array<", "[")) or "[]" in type_src:
                    schema["type"] = "array"
                    schema["items"] = {"$ref": f"#/components/schemas/{ref}"}
                else:
                    schema["$ref"] = f"#/components/schemas/{ref}"
    if not schema:
        base = type_src.split('|')[0].strip()
        if base.startswith("Array<"):
            schema["type"] = "array"
            item = base[6:-1]
            if item in ("string", "number", "boolean"):
                schema["items"] = {"type": item}
            elif item.startswith(("{[", "Record")):
                schema["items"] = {"type": "object"}
            else:
                schema["items"] = {"$ref": f"#/components/schemas/{item}"}
        elif base == "string":
            schema["type"] = "string"
        elif base == "number":
            schema["type"] = "number"
        elif base == "boolean":
            schema["type"] = "boolean"
        elif base == "Date":
            schema = {"type": "string", "format": "date-time"}
        elif base in ("any", "unknown"):
            return {"description": "any"}
        elif base.startswith("{[") or base == "object" or base.startswith("Record"):
            schema = {"type": "object"}
        else:
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', base):
                schema = {"$ref": f"#/components/schemas/{base}"}
    return schema

def infer_array_item(decs, decorators_src, type_src, enums):
    for d in decs:
        if d in ("IsUUID", "IsString", "IsEmail", "IsNumber", "IsInt", "IsBoolean", "IsEnum", "IsDateString", "IsUrl"):
            if re.search(r'@%s\([^)]*each:\s*true' % d, decorators_src):
                t, fmt = TYPE_MAP.get(d, ("string", None))
                if d == "IsEnum":
                    em = re.search(r'@IsEnum\(([A-Za-z0-9_.]+)\)', decorators_src)
                    if em and em.group(1).split('.')[-1] in enums:
                        return {"type": "string", "enum": enums[em.group(1).split('.')[-1]]}
                items = {"type": t}
                if fmt:
                    items["format"] = fmt
                return items
    tm = re.search(r'@Type\(\(\)\s*=>\s*([A-Za-z0-9_]+)', decorators_src)
    if tm:
        if tm.group(1) == "Date":
            return {"type": "string", "format": "date-time"}
        return {"$ref": f"#/components/schemas/{tm.group(1)}"}
    base = type_src.split('|')[0].strip()
    if base.startswith("Array<"):
        item = base[6:-1]
    elif base.endswith("[]"):
        item = base[:-2]
    else:
        return None
    if item in ("string", "number", "boolean"):
        return {"type": item}
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', item):
        return {"$ref": f"#/components/schemas/{item}"}
    return {"type": "object"}

# ---------- TS 类型 → OpenAPI 简单映射（参数级） ----------
def ts_type_schema(type_src):
    """把 TS 参数类型转成 schema（string/number/boolean/string[]/number[] 等）。"""
    base = type_src.strip().rstrip(',')
    if base.startswith("Array<") and base.endswith(">"):
        item = base[6:-1]
        inner = ts_type_schema(item)
        return {"type": "array", "items": inner or {"type": "string"}}
    if base.endswith("[]"):
        item = base[:-2]
        inner = ts_type_schema(item)
        return {"type": "array", "items": inner or {"type": "string"}}
    if base.startswith("{[") or base == "object" or base.startswith("Record"):
        return {"type": "object"}
    if base.startswith("Promise<"):
        return ts_type_schema(base[8:-1])
    if base == "string":
        return {"type": "string"}
    if base == "number":
        return {"type": "number"}
    if base == "boolean":
        return {"type": "boolean"}
    if base == "Date":
        return {"type": "string", "format": "date-time"}
    if base in ("any", "unknown"):
        return None
    return None  # 类引用 → 调用方处理

# ---------- 主流程 ----------
def main():
    classes, enums = collect_classes()
    print(f"class 定义: {len(classes)} | 枚举: {len(enums)}", file=sys.stderr)

    for e in ENDPOINTS:
        if e["module"] == "controllers":
            e["module"] = e["file"].replace(".controller.ts", "")

    tags = {}
    for e in ENDPOINTS:
        tags.setdefault(e["module"], 0)
        tags[e["module"]] += 1

    paths = {}
    for e in ENDPOINTS:
        path = e["path"]
        path = re.sub(r':([A-Za-z0-9_]+)', r'{\1}', path)
        method = e["method"]
        op = {
            "tags": [e["module"]],
            "operationId": e["handler"],
            "summary": f"{method.upper()} {path}",
            "responses": {},
        }
        # description：JSDoc 优先，其次 service 调用链
        desc_parts = []
        if e.get("jsdoc"):
            desc_parts.append(e["jsdoc"].strip().replace("\n", " "))
        calls = e.get("calls") or []
        if calls:
            chain = " → ".join(f"{c['service']}.{c['method']}" for c in calls)
            if not e.get("jsdoc"):
                desc_parts.append(f"内部流程：{chain}。")
        if desc_parts:
            op["description"] = " ".join(desc_parts)

        parameters = []
        body_ref = None          # @Body() dto: XxxDto
        body_fields = []         # @Body('field') f: Type
        query_dto_ref = None     # @Query() dto: XxxDto
        for p in e["params"]:
            ptype = p["type"].rstrip(',')
            dec = {d["name"]: d["arg"] for d in p["decorators"]}
            def first_str(s):
                m = re.search(r"[\"']([^\"']+)[\"']", s)
                return m.group(1) if m else ""
            if "Param" in dec:
                name = first_str(dec["Param"]) or p["name"]
                sch = ts_type_schema(ptype) or {"type": "string"}
                if sch.get("type") == "array":
                    sch = {"type": "string"}  # path 参数不允许数组
                parameters.append({"name": name, "in": "path", "required": True, "schema": sch})
            elif "Query" in dec:
                name = first_str(dec["Query"])
                if name:
                    parameters.append({"name": name, "in": "query", "schema": ts_type_schema(ptype) or {"type": "string"}, "required": False})
                elif ptype and ptype not in ("any", "unknown") and re.match(r'^[A-Za-z_]\w*$', ptype):
                    query_dto_ref = ptype  # @Query() dto: ListXxxDto → 展开
                else:
                    parameters.append({"name": p["name"], "in": "query", "schema": {"type": "string"}, "required": False})
            elif "Body" in dec:
                field = first_str(dec["Body"])
                if field:
                    body_fields.append({"name": field, "schema": ts_type_schema(ptype) or {"type": "string"}})
                elif ptype and ptype not in ("any", "unknown") and re.match(r'^[A-Za-z_]\w*$', ptype):
                    body_ref = ptype
        # @Query DTO 展开
        if query_dto_ref and query_dto_ref in classes:
            for fname, f in classes[query_dto_ref]["fields"].items():
                sch = {k: v for k, v in f.items() if k != "required"}
                parameters.append({
                    "name": fname, "in": "query",
                    "schema": sch, "required": bool(f.get("required", False)),
                })
        if parameters:
            op["parameters"] = parameters

        # requestBody
        if body_ref:
            op["requestBody"] = {"required": True, "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{body_ref}"}}}}
        elif body_fields:
            props = {}
            for bf in body_fields:
                props[bf["name"]] = bf["schema"]
            op["requestBody"] = {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": props}}}}

        # 响应码：默认按 NestJS 语义；@HttpCode 覆盖
        if e.get("http_code"):
            status = str(e["http_code"])
        elif method in ("post", "put", "patch"):
            status = "201"
        else:
            status = "200"
        # 200 schema：由 return 表达式推断（不编造具体 DTO）
        resp_schema = {"type": "object"}
        for r in e.get("returns") or []:
            if "!!" in r:
                resp_schema = {"type": "boolean"}
                break
            if re.match(r'^\{\s*\}$', r):
                resp_schema = {"type": "object", "description": "空对象"}
                break
        op["responses"] = {
            status: {"description": "成功", "content": {"application/json": {"schema": resp_schema}}},
            "400": {"description": "请求参数错误（Bad Request）"},
            "401": {"description": "未登录 / Token 失效（Unauthorized）"},
            "403": {"description": "无权限（Forbidden）"},
            "404": {"description": "资源不存在（Not Found）"},
            "500": {"description": "服务端错误（Internal Server Error）"},
        }
        paths.setdefault(path, {})[method] = op

    # schemas：只保留被引用或 Request/Response/Dto 类
    referenced = set()
    for p in paths.values():
        for op in p.values():
            if "requestBody" in op:
                sch = op["requestBody"]["content"]["application/json"]["schema"]
                if "$ref" in sch:
                    referenced.add(sch["$ref"].split("/")[-1])
            for param in op.get("parameters", []):
                sch = param.get("schema", {})
                if "$ref" in sch:
                    referenced.add(sch["$ref"].split("/")[-1])
                if "items" in sch and isinstance(sch["items"], dict) and "$ref" in sch["items"]:
                    referenced.add(sch["items"]["$ref"].split("/")[-1])

    schemas = {}
    def collect_refs(name, visited):
        if name in visited or name not in classes:
            return
        visited.add(name)
        props = {}
        req = []
        for fname, f in classes[name]["fields"].items():
            props[fname] = {k: v for k, v in f.items() if k != "required"}
            if "$ref" in f:
                collect_refs(f["$ref"].split("/")[-1], visited)
            if "items" in f and isinstance(f["items"], dict) and "$ref" in f["items"]:
                collect_refs(f["items"]["$ref"].split("/")[-1], visited)
            if f.get("required"):
                req.append(fname)
        s = {"type": "object", "properties": props}
        if req:
            s["required"] = req
        schemas[name] = s

    for ref in referenced:
        collect_refs(ref, set())

    doc = {
        "openapi": "3.0.3",
        "info": {
            "title": "Katana Server API",
            "description": "Katana 平台后端接口文档（由 katana-server 代码自动提取生成）。支付以 PayPal / Stripe（银行卡、Apple Pay、Google Pay、ACH）为主；对外提供社交电商、活动票务、创作者分销与结算等能力。",
            "version": "1.0.0（自动生成）",
        },
        "servers": [{"url": "https://release.katana-api.1m.app", "description": "Release 环境（默认）"}],
        "tags": [{"name": m, "description": f"{m} 模块（{n} 个端点）"} for m, n in sorted(tags.items(), key=lambda x: -x[1])],
        "paths": paths,
        "components": {"schemas": schemas},
    }

    def fix_dangling(obj):
        if isinstance(obj, dict):
            for k, v in list(obj.items()):
                if k == "$ref":
                    name = v.split("/")[-1]
                    if name.endswith("[]"):
                        item = name[:-2]
                        items = {"type": item} if item in ("string", "number", "boolean", "object") else {"type": "object"}
                        obj.clear()
                        obj.update({"type": "array", "items": items})
                    elif name not in doc["components"]["schemas"]:
                        obj.clear()
                        obj.update({"type": "object", "description": f"原引用 {name}（未生成 schema）"})
                else:
                    fix_dangling(v)
        elif isinstance(obj, list):
            for x in obj:
                fix_dangling(x)
    fix_dangling(doc)

    try:
        import yaml
    except ImportError:
        print("PyYAML 未安装，尝试 pip 安装", file=sys.stderr)
        os.system("pip3 install pyyaml -q")
        import yaml
    out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
    with open("/Users/a123456/Documents/Pear code/katana-openapi/katana-server.openapi.yaml", "w", encoding="utf-8") as f:
        f.write(out)
    with open("/Users/a123456/Documents/Pear code/katana-openapi/katana-server.openapi.json", "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    n_desc = sum(1 for p in paths.values() for op in p.values() if "description" in op)
    n_201 = sum(1 for p in paths.values() for op in p.values() if "201" in op["responses"])
    n_query_dto = sum(1 for p in paths.values() for op in p.values() if any(x.get("in") == "query" for x in op.get("parameters", [])))
    n_body_fields = sum(1 for p in paths.values() for op in p.values() if "requestBody" in op and "properties" in op["requestBody"]["content"]["application/json"]["schema"])
    print(f"写入完成: paths={len(paths)} 个路径 / {sum(len(v) for v in paths.values())} 个操作 | schemas={len(schemas)} | YAML 约 {len(out)//1024} KB", file=sys.stderr)
    print(f"带描述操作: {n_desc} | 201 响应: {n_201} | 含 query 参数操作: {n_query_dto} | @Body 字段拆分: {n_body_fields}", file=sys.stderr)
    d2 = yaml.safe_load(out)
    assert d2["openapi"].startswith("3."), "openapi 版本错误"
    assert "paths" in d2, "缺少 paths"
    assert "components" in d2, "缺少 components"
    print("YAML 校验通过", file=sys.stderr)

if __name__ == "__main__":
    main()
