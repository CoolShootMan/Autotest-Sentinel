#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 katana-server 标准 OpenAPI 3.0 文档（YAML）。
输入：/tmp/katana_endpoints.json（controller 解析结果）
过程：扫描 src 下 class 定义（class-validator 装饰器 → JSON Schema），组装 paths + components.schemas。
"""
import os, re, json, sys

ROOT = "/Users/a123456/Documents/Pear code/katana-server/src"
ENDPOINTS = json.load(open("/tmp/katana_endpoints.json", encoding="utf-8"))

# ---------- 1. 扫描 class 定义与枚举 ----------
TYPE_MAP = {
    "IsString": ("string", None),
    "IsUUID": ("string", "uuid"),
    "IsEmail": ("string", "email"),
    "IsUrl": ("string", "uri"),
    "IsDateString": ("string", "date-time"),
    "IsISO8601": ("string", "date-time"),
    "IsNumber": ("number", None),
    "IsInt": ("integer", "int32"),
    "IsPositive": ("number", None),
    "IsBoolean": ("boolean", None),
    "IsArray": ("array", None),
    "IsNotEmptyObject": ("object", None),
    "IsPhoneNumber": ("string", None),
    "IsHexadecimal": ("string", None),
    "IsAlphanumeric": ("string", None),
    "IsLowercase": ("string", None),
    "IsUppercase": ("string", None),
    "IsEnum": ("string", None),
    "IsDate": ("string", "date"),
    "IsJsonString": ("string", None),
    "IsObject": ("object", None),
    "IsIn": ("string", None),
}

def collect_classes():
    """返回 {ClassName: {"fields": {name: {type, format, required, $ref, items}}, "raw": 定义片段}}"""
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
            text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
            # 枚举：enum X { A = 'a' } 或 const X = {...} as const
            for em in re.finditer(r'enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]*)\}', text):
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
            for cm in re.finditer(r'export\s+class\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{', text):
                cname = cm.group(1)
                # 找类体
                start = cm.end() - 1
                depth = 0
                for i in range(start, len(text)):
                    if text[i] == '{':
                        depth += 1
                    elif text[i] == '}':
                        depth -= 1
                        if depth == 0:
                            body = text[cm.start():i + 1]
                            classes[cname] = parse_class(body, enums, text)
                            break
    return classes, enums

def parse_class(body, enums, file_text):
    """解析类体：字段名 + 装饰器 → schema 属性。"""
    fields = {}
    # 提取类体内所有字段声明：装饰器序列 + name[:]? type;
    # 简化：先按 "字段名: 类型;" 提取，再向前收集装饰器
    field_re = re.compile(r'(?:^|\n)\s*((?:@[A-Za-z]+\([^;]*?\)\s*|@[A-Za-z]+\s*)+)?\s*([A-Za-z_][A-Za-z0-9_]*)\s*(\??)\s*:\s*([^;\n]+);', re.M)
    for fm in field_re.finditer(body):
        decorators_src = fm.group(1) or ""
        name = fm.group(2)
        optional_mark = fm.group(3) == '?'
        type_src = fm.group(4).strip()
        decs = re.findall(r'@(\w+)', decorators_src)
        schema = build_field_schema(decs, decorators_src, type_src, enums, file_text)
        if schema is not None:
            schema["required"] = not (optional_mark or "IsOptional" in decs)
            fields[name] = schema
    return {"fields": fields}

def build_field_schema(decs, decorators_src, type_src, enums, file_text):
    schema = {}
    # 数组优先：@IsArray / @ValidateNested({each:true}) / TS 类型 Array<X> 或 X[]
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
                if "each" in decorators_src or type_src.startswith(("Array<", "[")) or "[]" in type_src:
                    schema["type"] = "array"
                    schema["items"] = {"$ref": f"#/components/schemas/{ref}"}
                else:
                    schema["$ref"] = f"#/components/schemas/{ref}"
    if not schema:
        # 从 TS 类型推断兜底
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
            # 可能是引用类型 → 尝试 $ref
            if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', base):
                schema = {"$ref": f"#/components/schemas/{base}"}
    return schema

def infer_array_item(decs, decorators_src, type_src, enums):
    """数组元素类型：优先 each:true 的验证器，其次 TS 类型。"""
    for d in decs:
        if d in ("IsUUID", "IsString", "IsEmail", "IsNumber", "IsInt", "IsBoolean", "IsEnum", "IsDateString", "IsUrl"):
            # 检查是否 each:true
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

# ---------- 2. 组装 OpenAPI ----------
def main():
    classes, enums = collect_classes()
    print(f"class 定义: {len(classes)} | 枚举: {len(enums)}", file=sys.stderr)

    # 修正模块名：src/controllers 下文件用文件名主体
    for e in ENDPOINTS:
        if e["module"] == "controllers":
            e["module"] = e["file"].replace(".controller.ts", "")

    tags = {}
    for e in ENDPOINTS:
        tags.setdefault(e["module"], 0)
        tags[e["module"]] += 1

    paths = {}
    for e in ENDPOINTS:
        path = e["path"].replace(':id', '{id}')
        # 把所有 :xxx 转 {xxx}
        path = re.sub(r':([A-Za-z0-9_]+)', r'{\1}', path)
        op = {"tags": [e["module"]], "operationId": e["handler"], "summary": f"{e['method'].upper()} {e['path']}", "responses": {}}
        parameters = []
        body_ref = None
        for p in e["params"]:
            ptype = p["type"].rstrip(',')
            dec = {d["name"]: d["arg"] for d in p["decorators"]}
            def first_str(s):
                m = re.search(r"[\"']([^\"']+)[\"']", s)
                return m.group(1) if m else ""
            if "Param" in dec:
                name = first_str(dec["Param"]) or p["name"]
                parameters.append({"name": name, "in": "path", "required": True, "schema": {"type": "string"}})
            elif "Query" in dec:
                name = first_str(dec["Query"]) or p["name"]
                parameters.append({"name": name, "in": "query", "schema": {"type": "string"}, "required": False})
            elif "Body" in dec:
                if ptype and ptype not in ("any", "unknown"):
                    body_ref = ptype
        if parameters:
            op["parameters"] = parameters
        if body_ref:
            op["requestBody"] = {"required": True, "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{body_ref}"}}}}
        # 通用响应
        op["responses"] = {
            "200": {"description": "成功", "content": {"application/json": {"schema": {"type": "object"}}}},
            "400": {"description": "请求参数错误（Bad Request）"},
            "401": {"description": "未登录 / Token 失效（Unauthorized）"},
            "403": {"description": "无权限（Forbidden）"},
            "404": {"description": "资源不存在（Not Found）"},
            "500": {"description": "服务端错误（Internal Server Error）"},
        }
        paths.setdefault(path, {})[e["method"]] = op

    # schemas：只保留被引用或 Request/Response/Dto 类
    referenced = set()
    for p in paths.values():
        for op in p.values():
            if "requestBody" in op:
                ref = op["requestBody"]["content"]["application/json"]["schema"]["$ref"]
                referenced.add(ref.split("/")[-1])
            for param in op.get("parameters", []):
                pass
    # 递归收集被引用 schema 的嵌套引用
    schemas = {}
    def collect_refs(name, visited):
        if name in visited or name not in classes:
            return
        visited.add(name)
        schemas[name] = {}
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

    # 组装文档
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

    # ---------- 3. 清理悬空 $ref ----------
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

    # 输出 YAML
    try:
        import yaml
    except ImportError:
        print("PyYAML 未安装，尝试 pip 安装", file=sys.stderr)
        os.system("pip3 install pyyaml -q")
        import yaml
    yaml_safe_dump = yaml.safe_dump
    out = yaml_safe_dump(doc, allow_unicode=True, sort_keys=False, width=200)
    with open("/Users/a123456/Documents/Pear code/katana-openapi/katana-server.openapi.yaml", "w", encoding="utf-8") as f:
        f.write(out)
    with open("/Users/a123456/Documents/Pear code/katana-openapi/katana-server.openapi.json", "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"写入完成: paths={len(paths)} 个路径 / {sum(len(v) for v in paths.values())} 个操作 | schemas={len(schemas)} | YAML 约 {len(out)//1024} KB", file=sys.stderr)
    # 校验
    d2 = yaml.safe_load(out)
    assert d2["openapi"].startswith("3."), "openapi 版本错误"
    assert "paths" in d2, "缺少 paths"
    assert "components" in d2, "缺少 components"
    print("YAML 校验通过", file=sys.stderr)

if __name__ == "__main__":
    main()
