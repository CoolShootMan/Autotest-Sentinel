#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 katana-server/src 解析所有 controller，提取 OpenAPI paths 所需信息。"""
import os, re, json, sys

ROOT = "/Users/a123456/Documents/Pear code/katana-server/src"

METHOD_MAP = {"Get": "get", "Post": "post", "Put": "put", "Patch": "patch",
              "Delete": "delete", "Options": "options", "Head": "head"}

def strip_comments(text):
    # 去掉 /* */ 与 // 注释（保留字符串内 // 的基本防护：不处理字符串，接受少量误伤）
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return text

def parse_controller(filepath):
    """解析单个 controller 文件，返回端点列表。"""
    with open(filepath, encoding="utf-8") as f:
        raw = f.read()
    text = strip_comments(raw)
    module = os.path.basename(os.path.dirname(filepath))

    # 类装饰器路由前缀：@Controller('x') 或 @Controller({ path: 'x', ... })
    prefix = ""
    m = re.search(r'@Controller\(\s*[\'"]([^\'"]+)[\'"]', text)
    if m:
        prefix = m.group(1)
    else:
        m = re.search(r'@Controller\(\s*\{\s*path\s*:\s*[\'"]([^\'"]+)[\'"]', text)
        if m:
            prefix = m.group(1)

    endpoints = []
    # 逐个方法定义块解析
    # 先找所有方法装饰器位置，再就近找方法签名
    for meth in METHOD_MAP:
        for dm in re.finditer(r'@%s\s*(?:\(\s*)?' % meth, text):
            # 装饰器可能带参数 @Get('path') 或 @Get({path:'x', version:'1'})
            seg = text[dm.start():]
            arg = ""
            cm = re.match(r'@%s\s*\(\s*([^)]*)\)' % meth, seg)
            if cm:
                arg = cm.group(1).strip()
            sub = ""
            if re.match(r'^[\'"][^\'"]*[\'"]$', arg):
                sub = arg.strip('\'"')
            else:
                om = re.search(r'path\s*:\s*[\'"]([^\'"]+)[\'"]', arg)
                if om:
                    sub = om.group(1)

            # 找方法签名（装饰器后最近的方法定义）
            after = seg[seg.find(')') + 1:] if ')' in seg else seg
            sm = re.search(r'\b(?:async\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(', after)
            if not sm:
                continue
            handler = sm.group(1)
            # 提取参数（含装饰器与类型）
            # 找到 '(' 到匹配 ')' 的签名参数段
            sig_start = after.find('(')
            sig_end = find_matching_paren(after, sig_start)
            if sig_end < 0:
                continue
            params_src = after[sig_start + 1:sig_end]

            params = parse_params(params_src)
            path = join_path(prefix, sub)
            endpoints.append({
                "module": module,
                "method": METHOD_MAP[meth],
                "path": path,
                "handler": handler,
                "params": params,
                "file": os.path.basename(filepath),
            })
    return endpoints

def find_matching_paren(s, start):
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1

def parse_params(src):
    """解析方法参数段：@Param('id') id: string、@Body() dto: CreateDto 等。"""
    params = []
    # 按逗号切分（忽略括号内的逗号）
    parts = split_top_level(src)
    for p in parts:
        p = p.strip()
        if not p:
            continue
        decorators = []
        body = p
        while body.startswith('@'):
            dm = re.match(r'@(\w+)\s*(?:\(([^)]*)\))?', body)
            if not dm:
                break
            decorators.append({"name": dm.group(1), "arg": (dm.group(2) or "").strip()})
            body = body[dm.end():].strip()
        # 变量名与类型
        vm = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^\s]+)', body)
        if not vm:
            vm = re.match(r'([A-Za-z_][A-Za-z0-9_]*)', body)
            name = vm.group(1) if vm else ""
            typ = ""
        else:
            name = vm.group(1)
            typ = vm.group(2).strip()
        # 去掉可选标记
        optional = body.replace(' ', '').startswith(name + '?:')
        params.append({"name": name, "type": typ.rstrip(','), "optional": optional, "decorators": decorators})
    return params

def split_top_level(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == '(' or ch == '[' or ch == '{':
            depth += 1
        elif ch == ')' or ch == ']' or ch == '}':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts

def join_path(prefix, sub):
    p = prefix.strip('/')
    s = sub.strip('/') if sub else ""
    if not s:
        return '/' + p if p else '/'
    if not p:
        return '/' + s
    return '/' + p + '/' + s

def main():
    all_endpoints = []
    for dirpath, _, files in os.walk(ROOT):
        for fn in files:
            if fn.endswith('.controller.ts'):
                fp = os.path.join(dirpath, fn)
                try:
                    eps = parse_controller(fp)
                    all_endpoints.extend(eps)
                except Exception as e:
                    print(f"ERROR {fp}: {e}", file=sys.stderr)
    # 去重（同 path+method）
    seen = set()
    dedup = []
    for e in all_endpoints:
        k = (e["method"], e["path"])
        if k in seen:
            continue
        seen.add(k)
        dedup.append(e)
    print(f"controllers 文件: {len(set(e['file'] for e in all_endpoints))} | 端点总数(去重前): {len(all_endpoints)} | 去重后: {len(dedup)}")
    mods = {}
    for e in dedup:
        mods.setdefault(e["module"], 0)
        mods[e["module"]] += 1
    print("模块数:", len(mods))
    for k in sorted(mods, key=lambda x: -mods[x])[:15]:
        print(f"  {k}: {mods[k]}")
    with open("/tmp/katana_endpoints.json", "w", encoding="utf-8") as f:
        json.dump(dedup, f, ensure_ascii=False, indent=1)
    # 抽样检查
    print("\n样例端点:")
    for e in dedup[:8]:
        print(" ", e["method"].upper(), e["path"], "->", e["handler"], "| params:", [(p['name'], p['type']) for p in e['params']])

if __name__ == "__main__":
    main()
