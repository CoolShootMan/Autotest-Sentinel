"""用例重写器：把 146 条迁移用例改写成「瘦用例」。

输入
----
* ``tests/`` 下的旧结构用例（``client.session().request(...)`` + try/except 样板）
* ``tools/migration/api_manifest.json``（gen_api_layer.py 产出的接口清单）

输出
----
同路径覆写的瘦用例：

* 请求    → ``_respN = ctx.api.<域>.<方法>(...)``
* 断言    → ``expect(_respN).json(expr).equals(...)``（一行替代 8~9 行 try/except）
* 提取器  → ``ctx.extract('name', _respN, expr)``
* 人工补丁（裸 assert / for / if / 中间变量）→ **原样保留**
* Apifox 追溯注释（# pre: / # post[...]）→ 原样保留
* ``_render`` / ``_url`` / 自定义 ``_ctx`` fixture / ApifoxDB import → 删除

语义保真策略
------------
1. ``_respN`` 变量名逐个保留——人工补丁里的引用不断链。
2. 请求头按归属拆解：pear-* → ``app_headers``、Authorization → ``token``、
   X-Skip-Notifications → ``skip_notifications``、Content-Type 交给客户端推导；
   与接口方法默认值一致时不传参（瘦调用）。
3. 路径参数名与接口多数派不一致时用 ``path_vars={"std": "{{actual}}"}`` 覆盖，
   其余情况靠上下文渲染 ``{{var}}``（与迁移前行为一致）。
4. 简单前置脚本 ``pm.environment.set("k", "字面量")``：若 ``k`` 已被
   env/.vars.yaml 覆盖则视为已迁移（保留注释）；否则提升为函数开头的
   ``vars['k'] = '字面量'``。
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # 工程根
sys.path.insert(0, str(Path(__file__).resolve().parent))      # tools/migration

import case_parser as cp                                     # noqa: E402
from gen_api_layer import (                                  # noqa: E402
    canonicalize, has_malformed, host_normalize, parse_query,
    path_vars_of, split_query, unbrace,
)

ROOT = Path(__file__).resolve().parents[2]
TESTS = ROOT / "tests"
MANIFEST = Path(__file__).resolve().parent / "api_manifest.json"

PEAR_KEYS = {"Pear-AutoTesting", "Pear-Client-Id", "Pear-Client-Secret"}
DROP_HEADER_LC = {"content-type", "x-skip-notifications", "authorization"} | \
                 {k.lower() for k in PEAR_KEYS}

RE_PRE_SET = re.compile(
    r'^#\s*pre:\s*pm\.(?:environment|variables)\.set\(\s*"([^"\\]+)"\s*,\s*"([^"\\]*)"\s*\)\s*;?\s*$'
)
RE_ALIAS = re.compile(r"^_\w+\s*=\s*(_resp\d+)$")
RE_RESP_REF = re.compile(r"\b(_\w+)\.json\(\)")   # 兼容 _resp1 / _resp_m 等命名
RE_A_REF = re.compile(r"\b_a(\d+)\.json\(\)")
RE_NAME_REF = {
    name: re.compile(r"(?<![\w.])" + name + r"\b")
    for name in ("_get_path", "_render", "_url", "client", "base_url",
                 "json", "re", "requests", "pytest")
}

CMP_MAP = {
    "equal": "equals", "equals": "equals",
    "notequal": "not_equals", "not_equal": "not_equals",
    "exists": "exists", "notexists": "not_exists", "not_exists": "not_exists",
    "include": "includes", "includes": "includes",
    "notinclude": "not_includes", "not_includes": "not_includes",
    "isempty": "is_empty", "is_empty": "is_empty", "empty": "is_empty",
    "notempty": "is_not_empty", "is_not_empty": "is_not_empty",
    "gt": "greater_than", "greaterthan": "greater_than",
    "lt": "less_than", "lessthan": "less_than",
    "contains": "contains", "length": "length", "matches": "matches",
}


# --- manifest 索引 -------------------------------------------------------
def build_index() -> dict:
    man = json.load(open(MANIFEST, encoding="utf-8"))
    idx = {}
    for dom, blk in man.items():
        for m in blk["methods"]:
            p = m["path"]
            key = (m["method"], p) if has_malformed(p) else \
                (m["method"], canonicalize(unbrace(host_normalize(p))))
            idx[key] = (dom, m)
    return idx


# --- 表达式工具 ---------------------------------------------------------
def literal(expr: str):
    """安全求值字面量；失败返回 None。"""
    try:
        return ast.literal_eval(expr)
    except Exception:
        return None


def params_to_dict(expr: str) -> str | None:
    """把 params 的 dict-comp 源码还原成普通 dict 字面量源码。"""
    if not expr or expr.strip() in ("{}", "None"):
        return None
    v = literal(expr)
    if isinstance(v, dict):
        return expr if expr.strip().startswith("{") else None
    try:
        node = ast.parse(expr.strip(), mode="eval").body
    except SyntaxError:
        return None
    # {k: _render(v, vars) for k, v in [('a','b'),...]} → {'a': 'b'}
    if isinstance(node, ast.DictComp):
        it = node.generators[0].iter
        if isinstance(it, (ast.List, ast.Tuple)):
            pairs = []
            for elt in it.elts:
                if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                    k = literal(ast.unparse(elt.elts[0]))
                    if k is None:
                        return None
                    pairs.append((k, ast.unparse(elt.elts[1])))
            return "{" + ", ".join(f"{k!r}: {v}" for k, v in pairs) + "}"
    return None


class _LegacyCallRewriter(ast.NodeTransformer):
    """把 ``_render(x, vars)`` → ``ctx.render(x)``、``_url(a,b,vars)`` → 保留原样。"""

    def visit_Call(self, node):
        self.generic_visit(node)
        if getattr(node.func, "id", "") == "_render" and len(node.args) >= 1:
            return ast.copy_location(
                ast.Call(func=ast.Attribute(value=ast.Name("ctx", ast.Load()),
                                            attr="render", ctx=ast.Load()),
                         args=[node.args[0]], keywords=[]), node)
        return node


def rewrite_value_expr(expr: str) -> str:
    """var 赋值右侧表达式：_render(x, vars) → ctx.render(x)。"""
    try:
        tree = ast.parse(expr.strip(), mode="eval")
        tree = _LegacyCallRewriter().visit(tree)
        return ast.unparse(tree)
    except SyntaxError:
        return expr


# --- 请求 → api 调用 ----------------------------------------------------
def gen_call(op: "cp.Op", idx: dict, warn: list) -> str | None:
    p = literal(op.path_expr)
    if not isinstance(p, str):
        warn.append(f"非字面量路径: {op.path_expr[:60]}")
        return None
    pn = unbrace(host_normalize(p))
    key = (op.method, p) if has_malformed(p) else (op.method, canonicalize(pn))
    hit = idx.get(key)
    if hit is None:
        warn.append(f"接口未命中: {op.method} {p[:80]}")
        return None
    dom, minfo = hit
    kw: list[str] = []

    # body
    if op.body_expr and op.body_expr.strip() not in ("''", '""'):
        kw.append(f"body={op.body_expr}")

    # params（路径查询串 + 显式 params 合并）
    base, q = split_query(pn)
    merged: dict = {}
    if q:
        merged.update(parse_query(q))
    if op.params_expr:
        d = literal(op.params_expr) or literal(params_to_dict(op.params_expr) or "")
        if isinstance(d, dict) and d:
            for k, v in d.items():
                merged[k] = v
    if merged:
        mpath = minfo["path"]
        if "?" in mpath:
            # 接口模板已含查询串，避免重复
            tpath_q = parse_query(split_query(mpath)[1])
            if {k: str(v) for k, v in merged.items()} == tpath_q:
                pass  # 与模板一致，无需传参
            else:
                kw.append(f"params={merged!r}")
        else:
            kw.append(f"params={merged!r}")

    # headers 归属拆解
    hdrs = literal(op.headers_expr) if op.headers_expr else None
    hdrs = hdrs if isinstance(hdrs, dict) else {}
    pear_lc = {k.lower() for k in PEAR_KEYS}
    has_pear = any(k.lower() in pear_lc for k in hdrs)   # 大小写不敏感：旧文件存在小写 pear-* 头
    has_skip = any(k.lower() == "x-skip-notifications" for k in hdrs)
    if has_pear != bool(minfo.get("app_headers")):
        kw.append(f"app_headers={has_pear!r}")
    if has_skip != bool(minfo.get("skip_notifications")):
        kw.append(f"skip_notifications={has_skip!r}")
    auth = next((v for k, v in hdrs.items() if k.lower() == "authorization"), None)
    if auth:
        m = re.search(r"\{\{\s*(\w+)\s*\}\}", str(auth))
        kw.append(f"token={m.group(1)!r}" if m else f"token={str(auth)!r}")
    others = {k: v for k, v in hdrs.items() if k.lower() not in DROP_HEADER_LC}
    if others:
        kw.append(f"headers={others!r}")

    # path_vars：变量名与接口多数派不一致时覆盖
    actual = path_vars_of(base)
    tmpl = path_vars_of(split_query(minfo["path"])[0])
    overrides = {}
    if len(actual) == len(tmpl):
        for std, act in zip(tmpl, actual):
            if std != act:
                overrides[std] = "{{" + act + "}}"
    elif tmpl:
        warn.append(f"路径参数个数不一致: {op.method} {p[:70]} 模板{tmpl} 实际{actual}")
    if overrides:
        kw.append(f"path_vars={overrides!r}")

    args = ", ".join(kw)
    return f"{op.var} = ctx.api.{dom}.{minfo['name']}({args})"


# --- 断言 / 提取 --------------------------------------------------------
def gen_assert(op: "cp.Op", src_lines: list[str], alias_map: dict) -> str | None:
    cmp_ = (op.comparison or "equal").strip()
    method = CMP_MAP.get(cmp_.lower().replace("_", ""))
    if not method:
        return None
    resp = op.resp_var or ""
    if not resp:
        # `_aN = _respN` 别名在 try 块外时，从语句源码里找回响应变量
        span = "\n".join(src_lines[op.lineno - 1:op.end_lineno])
        m = RE_RESP_REF.search(span)
        if m:
            resp = m.group(1)
        else:
            m = re.search(r"\b_a(\d+)\b", span)
            resp = alias_map.get(f"_a{m.group(1)}", f"_resp{m.group(1)}") if m else ""
    if not resp:
        return None
    expr = op.expr if op.expr.startswith("$") else f"$.{op.expr}"
    expected = op.expected_expr.strip()
    if method in ("exists", "not_exists", "is_empty", "is_not_empty"):
        # 无期望值断言：exists/is_empty 系不需要 expected 参数
        return f"expect({resp}).json({expr!r}).{method}()"
    if expected:
        # 期望值是含 {{}} 的字面量时，按迁移前语义先渲染
        lit = literal(expected)
        if isinstance(lit, str) and "{{" in lit:
            expected = f"ctx.render_text({expected})"
        return f"expect({resp}).json({expr!r}).{method}({expected})"
    return None


def gen_extract(op: "cp.Op", src_lines: list[str], alias_map: dict) -> str | None:
    span = "\n".join(src_lines[op.lineno - 1:op.end_lineno])
    m = RE_RESP_REF.search(span) or RE_A_REF.search(span)
    mw = None
    if not m:
        # 手写补丁：_cur = _jN; for _p in [...]: _cur = (...); vars[k] = _cur
        mw = re.search(r"_cur\s*=\s*(_\w+)\b", span)
        if not (mw and re.search(r"vars\[", span)):
            return None
    if mw:                                       # 手写补丁兜底：group(1) 即响应变量名
        resp = mw.group(1)
    elif m.re is RE_RESP_REF:
        resp = m.group(1)
    else:                                        # _aN → 翻译
        resp = f"_resp{m.group(1)}"
    ma = re.fullmatch(r"_a(\d+)", resp)
    if ma:                                       # _aN 别名已被重写器丢弃
        resp = alias_map.get(resp, f"_resp{ma.group(1)}")
    return f"ctx.extract({op.name!r}, {resp}, {op.expr!r})"


# --- 单文件重写 ---------------------------------------------------------
def rewrite_file(path: Path, idx: dict, case_vars_keys: set | None) -> dict:
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    tree = ast.parse(src)
    stats = {"requests": 0, "asserts": 0, "extracts": 0, "vars": 0,
             "raw_kept": 0, "warn": []}

    # 定位模块级删除区间与测试函数
    fn = None
    del_ranges = []          # (start, end) 1-based 闭区间
    first_import_at = None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if first_import_at is None:
                first_import_at = node.lineno
            del_ranges.append((node.lineno, node.end_lineno))
        elif isinstance(node, ast.FunctionDef):
            if node.name in ("_render", "_url"):
                del_ranges.append((node.lineno, node.end_lineno))
            elif node.name.startswith("test"):
                fn = node
        elif isinstance(node, ast.Assign):
            t = node.targets[0]
            if isinstance(t, ast.Name) and t.id in ("PROJECT_ID", "PROJECT"):
                del_ranges.append((node.lineno, node.end_lineno))
        elif isinstance(node, ast.ClassDef):
            pass
    # 自定义 _ctx fixture（@pytest.fixture 装饰）
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_ctx":
            start = min([d.lineno for d in node.decorator_list] + [node.lineno])
            del_ranges.append((start, node.end_lineno))

    if fn is None:
        stats["warn"].append("未找到 test_* 函数")
        return stats

    # 前置脚本：未被 env/.vars.yaml 覆盖的简单 set 提升为代码
    hoisted: list[str] = []
    drop_lines = set()
    if case_vars_keys is not None:
        for i, ln in enumerate(lines, 1):
            m = RE_PRE_SET.match(ln.strip())
            if m and m.group(1) not in case_vars_keys:
                hoisted.append(f"    vars[{m.group(1)!r}] = {m.group(2)!r}"
                               f"  # from Apifox pre-script")
                drop_lines.add(i)

    # --- 重建测试函数体 ---
    pc = cp.parse_case(path, TESTS)
    # 同一行可能有多条分号语句（case_parser 各生成一个 op），按 lineno 分组为队列，
    # 语句循环按访问顺序弹出，保证同行多语句 1:1 对应（否则会互相覆盖/重复输出）。
    ops_by_line: dict[int, list] = {}
    for o in pc.ops:
        ops_by_line.setdefault(o.lineno, []).append(o)
    body: list[str] = []
    refs = set()
    pending: list[str] = []          # 注释缓冲
    alias_map: dict = {}             # _aN -> _respN
    last_end = fn.lineno             # def 行
    fn_doc = ast.get_docstring(fn)

    def flush_pending():
        body.extend(pending)
        pending.clear()

    for stmt in fn.body:
        # 收集上一语句与本语句之间的注释
        for i in range(last_end + 1, stmt.lineno):
            s = lines[i - 1]
            if s.strip().startswith("#") and i not in drop_lines:
                pending.append(s)
        last_end = stmt.end_lineno or stmt.lineno

        # 函数 docstring 由函数头部统一输出，这里跳过
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
                and stmt.value.value == fn_doc):
            continue

        ops = ops_by_line.get(stmt.lineno)
        op = ops.pop(0) if ops else None
        if op is None:
            continue                 # 前置样板（client/base_url/vars 赋值）

        if op.kind == "request":
            flush_pending()
            call = gen_call(op, idx, stats["warn"])
            if call:
                body.append("    " + call)
                stats["requests"] += 1
            else:
                body.append("    " + cp_source(lines, stmt))
                stats["raw_kept"] += 1
                collect_refs(cp_source(lines, stmt), refs)

        elif op.kind == "assert":
            one = gen_assert(op, lines, alias_map)
            if one:
                flush_pending()
                body.append("    " + one)
                stats["asserts"] += 1
            else:
                flush_pending()
                body.append(cp_source(lines, stmt))
                stats["raw_kept"] += 1
                collect_refs(cp_source(lines, stmt), refs)

        elif op.kind == "extract":
            one = gen_extract(op, lines, alias_map)
            if one:
                flush_pending()
                body.append("    " + one)
                stats["extracts"] += 1
            else:
                flush_pending()
                body.append(cp_source(lines, stmt))
                stats["raw_kept"] += 1
                collect_refs(cp_source(lines, stmt), refs)

        elif op.kind == "var":
            flush_pending()
            body.append(f"    vars[{op.key!r}] = {rewrite_value_expr(op.value_expr)}")
            stats["vars"] += 1
            collect_refs(op.value_expr, refs)

        else:  # raw
            s = op.source.rstrip("\n")
            m = RE_ALIAS.match(s.strip())
            if m:
                # _aN = _respN 别名：expect() 直接吃响应，仅登记映射供断言回查
                alias_map[s.strip().split("=")[0].strip()] = m.group(1)
                continue
            # 旧框架 API → 新框架等价物（唯一已知形态）
            s = re.sub(r"case_vars\.save_runtime_tokens\((\w+)\)",
                       r"ctx.save_runtime(list(\1))", s)
            flush_pending()
            body.append(s)
            stats["raw_kept"] += 1
            collect_refs(s, refs)

    # 尾部注释（函数末尾语句之后的）
    for i in range(last_end + 1, (fn.end_lineno or fn.lineno) + 1):
        s = lines[i - 1]
        if s.strip().startswith("#"):
            pending.append(s)
    flush_pending()

    # --- 组装函数 ---
    doc = ast.get_docstring(fn)
    head = [f"def {fn.name}(ctx):"]
    if doc:
        head.append(f'    """{doc}"""')
    head.append("    vars = ctx  # Context 别名：人工补丁里的 vars['x'] 继续可用")
    if "base_url" in refs:
        head.append("    base_url = ctx.base_url")
    if "client" in refs:
        head.append("    client = LegacyClient(ctx)")
    if "_render" in refs:
        head.append("    _render = legacy_render(ctx)")
    if "_url" in refs:
        head.append("    _url = legacy_url(ctx)")
    for h in hoisted:
        head.append(h)
    new_fn = "\n".join(head + body) + "\n"

    # --- 组装模块 ---
    out: list[str] = []
    fn_range = (fn.lineno, fn.end_lineno)
    skip = set()
    for a, b in del_ranges:
        if (a, b) != fn_range:
            for i in range(a, b + 1):
                skip.add(i)
    imports_block = build_imports(refs)
    for i, ln in enumerate(lines, 1):
        if i in skip or i in drop_lines:
            continue
        if fn_range[0] <= i <= fn_range[1]:
            if i == fn_range[0]:
                out.append(imports_block)
                out.append("")
                out.append(new_fn.rstrip("\n"))
            continue
        if first_import_at and i == first_import_at:
            continue                 # 旧 import 行由新 import 块取代（在函数前插入）
        out.append(ln)

    text = "\n".join(out).rstrip("\n") + "\n"
    # 校验可解析
    try:
        ast.parse(text)
    except SyntaxError as e:
        ctx_lines = text.splitlines()
        lo, hi = max(0, e.lineno - 6), min(len(ctx_lines), e.lineno + 4)
        stats["warn"].append(
            f"生成代码语法错误: {e}\n" +
            "\n".join(f"{i+1:4d}| {ctx_lines[i]}" for i in range(lo, hi)))
        return stats
    path.write_text(text, encoding="utf-8")
    return stats


def cp_source(lines: list[str], stmt) -> str:
    seg = ast.get_source_segment("\n".join(lines), stmt, padded=True) or ast.unparse(stmt)
    if seg and seg[0] not in " \t" and 0 < stmt.lineno <= len(lines):
        indent = re.match(r"[ \t]*", lines[stmt.lineno - 1]).group(0)
        seg = indent + seg
    return seg.rstrip("\n")


def collect_refs(src: str, refs: set) -> None:
    for name, pat in RE_NAME_REF.items():
        if pat.search(src):
            refs.add(name)


def build_imports(refs: set) -> str:
    std = [m for m in ("json", "re", "requests", "pytest") if m in refs]
    lines = []
    for m in std:
        lines.append(f"import {m}")
    if std:
        lines.append("")
    lines.append("from core.assertions import expect")
    imports = []
    if "_get_path" in refs:
        imports.append("from core.compat import get_path as _get_path")
    cls = []
    if "client" in refs or "LegacyClient" in refs:
        cls.append("LegacyClient")
    if "_render" in refs:
        cls.append("legacy_render")
    if "_url" in refs:
        cls.append("legacy_url")
    if cls:
        imports.append(f"from core.compat import {', '.join(cls)}")
    if imports:
        lines.append("")
        lines.extend(imports)
    return "\n".join(lines)


# --- 主流程 -------------------------------------------------------------
def main():
    idx = build_index()
    files = sorted(TESTS.rglob("test_*.py"))
    print(f"待重写用例: {len(files)}")

    # 用例变量键集合（判断 pre-script 是否已被 yaml 覆盖）
    from config import env_loader
    tot = {"requests": 0, "asserts": 0, "extracts": 0, "vars": 0,
           "raw_kept": 0}
    fails = []
    for f in files:
        try:
            data = env_loader.load_case_vars(f, None)
            keys = set(data.get("variables") or {})
        except Exception:
            keys = None
        st = rewrite_file(f, idx, keys)
        for k in tot:
            tot[k] += st[k]
        if st["warn"]:
            fails.append((f, st["warn"]))
    print(f"请求→api调用: {tot['requests']}  断言→expect: {tot['asserts']}  "
          f"提取→ctx.extract: {tot['extracts']}  var: {tot['vars']}  "
          f"原样保留(raw): {tot['raw_kept']}")
    if fails:
        print(f"\n=== {len(fails)} 个文件有告警 ===")
        for f, ws in fails:
            print(f"--- {f.relative_to(ROOT)} ---")
            for w in ws:
                print("   ", w)


if __name__ == "__main__":
    main()
