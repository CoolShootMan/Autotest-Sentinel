#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 katana-server/src 解析所有 controller，提取 OpenAPI paths 所需信息（增强版）。
相比旧版新增：JSDoc 注释、@HttpCode、handler 返回表达式、service 调用链、参数类型精确化、@Body 字段拆分。"""
import os, re, json, sys

ROOT = "/Users/a123456/Documents/Pear code/katana-server/src"

METHOD_MAP = {"Get": "get", "Post": "post", "Put": "put", "Patch": "patch",
              "Delete": "delete", "Options": "options", "Head": "head"}

def strip_comments(text):
    # 用等长空格替换块注释，保持字符串索引与原文一致（JSDoc 需按 raw 偏移提取）
    text = re.sub(r'/\*.*?\*/', lambda m: ' ' * len(m.group(0)), text, flags=re.S)
    return text

def find_matching(s, start, open_c, close_c):
    depth = 0
    for i in range(start, len(s)):
        if s[i] == open_c:
            depth += 1
        elif s[i] == close_c:
            depth -= 1
            if depth == 0:
                return i
    return -1

def parse_controller(filepath):
    with open(filepath, encoding="utf-8") as f:
        raw = f.read()
    text = strip_comments(raw)
    module = os.path.basename(os.path.dirname(filepath))

    prefix = ""
    m = re.search(r'@Controller\(\s*[\'"]([^\'"]+)[\'"]', text)
    if m:
        prefix = m.group(1)
    else:
        m = re.search(r'@Controller\(\s*\{\s*path\s*:\s*[\'"]([^\'"]+)[\'"]', text)
        if m:
            prefix = m.group(1)

    endpoints = []
    for meth in METHOD_MAP:
        for dm in re.finditer(r'@%s\s*(?:\(\s*)?' % meth, text):
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

            # JSDoc：方法装饰器前的最后一个 /** ... */ 注释块
            jsdoc = ""
            before = raw[:dm.start()]
            jm = re.findall(r'/\*\*([^*].*?)\*/', before, flags=re.S)
            if jm:
                cand = jm[-1].strip()
                # 与装饰器之间只能有空白或其它装饰器
                tail = before[before.rfind('*/') + 2:] if before.rfind('*/') >= 0 else before
                if not re.search(r'\S', re.sub(r'@\w+\s*(?:\([^)]*\))?\s*', '', tail)):
                    jsdoc = cand

            # @HttpCode：装饰器区（@Get 之前的若干行）中的 @HttpCode(N)
            http_code = None
            hc = re.finditer(r'@HttpCode\(\s*(\d+)\s*\)', before)
            for h in hc:
                tail = before[h.end():]
                if not re.search(r'\S', re.sub(r'@\w+\s*(?:\([^)]*\))?\s*', '', tail)):
                    http_code = int(h.group(1))

            after = seg[seg.find(')') + 1:] if ')' in seg else seg
            sm = re.search(r'\b(?:async\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(', after)
            if not sm:
                continue
            handler = sm.group(1)
            sig_start = after.find('(')
            sig_end = find_matching(after, sig_start, '(', ')')
            if sig_end < 0:
                continue
            params_src = after[sig_start + 1:sig_end]
            params = parse_params(params_src)

            # 方法体
            body = ""
            b_open = after.find('{', sig_end + 1)
            b_close = find_matching(after, b_open, '{', '}') if b_open >= 0 else -1
            if b_close > b_open:
                body = after[b_open + 1:b_close]

            # return 表达式（逐行）
            returns = []
            for rm in re.finditer(r'return\s+([^;\n]+)', body):
                expr = rm.group(1).strip()
                if expr and expr != "void":
                    returns.append(expr)
            # service 调用链（this.xxx.method(...)）
            calls = []
            seen_c = set()
            for cm_ in re.finditer(r'this\.(\w+)\.(\w+)\s*\(', body):
                key = (cm_.group(1), cm_.group(2))
                if key not in seen_c:
                    seen_c.add(key)
                    calls.append({"service": cm_.group(1), "method": cm_.group(2)})

            path = join_path(prefix, sub)
            endpoints.append({
                "module": module,
                "method": METHOD_MAP[meth],
                "path": path,
                "handler": handler,
                "params": params,
                "file": os.path.basename(filepath),
                "jsdoc": jsdoc,
                "http_code": http_code,
                "returns": returns[:8],
                "calls": calls[:12],
            })
    return endpoints

def parse_params(src):
    """解析方法参数段：@Param('id') id: string、@Body() dto: CreateDto、@Body('field') f: string[] 等。"""
    params = []
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
        vm = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*(?:\?)?\s*:\s*([^\s]+)', body)
        if not vm:
            vm = re.match(r'([A-Za-z_][A-Za-z0-9_]*)', body)
            name = vm.group(1) if vm else ""
            typ = ""
        else:
            name = vm.group(1)
            typ = vm.group(2).strip()
        optional = body.replace(' ', '').startswith(name + '?:')
        params.append({"name": name, "type": typ.rstrip(','), "optional": optional, "decorators": decorators})
    return params

def split_top_level(s):
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch in '([{':
            depth += 1
        elif ch in ')]}':
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
    seen = set()
    dedup = []
    for e in all_endpoints:
        k = (e["method"], e["path"])
        if k in seen:
            continue
        seen.add(k)
        dedup.append(e)
    print(f"controllers 文件: {len(set(e['file'] for e in all_endpoints))} | 端点总数(去重前): {len(all_endpoints)} | 去重后: {len(dedup)}", file=sys.stderr)
    mods = {}
    for e in dedup:
        mods.setdefault(e["module"], 0)
        mods[e["module"]] += 1
    # 统计增强字段覆盖率
    n_jsdoc = sum(1 for e in dedup if e["jsdoc"])
    n_hc = sum(1 for e in dedup if e["http_code"])
    n_ret = sum(1 for e in dedup if e["returns"])
    n_call = sum(1 for e in dedup if e["calls"])
    n_typed = sum(1 for e in dedup for p in e["params"] if p["type"])
    print(f"JSDoc: {n_jsdoc} | @HttpCode: {n_hc} | return 表达式: {n_ret} | service 调用链: {n_call} | 有类型参数: {n_typed}", file=sys.stderr)
    with open("/tmp/katana_endpoints.json", "w", encoding="utf-8") as f:
        json.dump(dedup, f, ensure_ascii=False, indent=1)
    print("\n样例端点:")
    for e in dedup[:6]:
        print(" ", e["method"].upper(), e["path"], "->", e["handler"])
        if e["jsdoc"]:
            print("    jsdoc:", e["jsdoc"][:80].replace("\n", " "))
        if e["calls"]:
            print("    calls:", " → ".join(f"{c['service']}.{c['method']}" for c in e["calls"][:3]))

if __name__ == "__main__":
    main()
