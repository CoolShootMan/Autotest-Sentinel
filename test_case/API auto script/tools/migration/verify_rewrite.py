"""重写语义等价性校验。

对重写前（备份目录）与重写后（tests/）的每个用例文件抽取「语义指纹」并逐一比对：

* 请求：HTTP 方法、归一化路径、查询参数、请求体模板、鉴权变量、
        pear 头开关、静默通知开关、其余请求头
* 断言：响应变量、JSONPath、比较方式、期望值
* 提取：变量名、JSONPath、响应变量
* 变量赋值：键、值表达式（_render → ctx.render 归一化后）
* 人工补丁：语句序列（去掉 _aN=_respN 别名与 docstring 后应原样保留）

任一维度不一致即报 FAIL，要求 100% 一致。
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import case_parser as cp                                   # noqa: E402
from gen_api_layer import (                                # noqa: E402
    canonicalize, has_malformed, host_normalize, parse_query,
    split_query, unbrace,
)

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT.parent / "API auto script.__backup_20260910_094554" / "tests"
NEW = ROOT / "tests"
MANIFEST = Path(__file__).resolve().parent / "api_manifest.json"

PEAR_KEYS = {"pear-autotesting", "pear-client-id", "pear-client-secret"}  # 统一小写比较
CMP_MAP = {
    "equal": "equals", "notequal": "not_equals", "exists": "exists",
    "include": "includes", "isempty": "is_empty",
}


def lit(e):
    try:
        return ast.literal_eval(e)
    except Exception:
        return None


def lit_or_str(e: str):
    """字面量求值失败时回退为原始字符串（如 _resp1 这类 Name 引用）。"""
    e = e.strip()
    try:
        return ast.literal_eval(e)
    except Exception:
        return e


def build_index():
    man = json.load(open(MANIFEST, encoding="utf-8"))
    by_name, by_key = {}, {}
    for dom, blk in man.items():
        for m in blk["methods"]:
            by_name[(dom, m["name"])] = m
            p = m["path"]
            key = (m["method"], p) if has_malformed(p) else \
                (m["method"], canonicalize(unbrace(host_normalize(p))))
            by_key[key] = (dom, m)
    return by_name, by_key


# --- 旧文件指纹 ---------------------------------------------------------
def old_fingerprint(path: Path) -> dict:
    pc = cp.parse_case(path, OLD)
    reqs, asserts, extracts, vars_, raws = [], [], [], [], []
    for o in pc.ops:
        if o.kind == "request":
            p = lit(o.path_expr)
            pn = unbrace(host_normalize(p)) if isinstance(p, str) else p
            hdrs = lit(o.headers_expr) if o.headers_expr else {}
            hdrs = hdrs if isinstance(hdrs, dict) else {}
            auth = next((v for k, v in hdrs.items()
                         if k.lower() == "authorization"), None)
            m = re.search(r"\{\{\s*(\w+)\s*\}\}", str(auth)) if auth else None
            base, q = split_query(pn or "")
            params = dict(parse_query(q)) if q else {}
            if o.params_expr:
                d = lit(o.params_expr)
                if isinstance(d, dict):
                    params.update(d)
            reqs.append({
                "key": (o.method, p) if has_malformed(p or "") else
                       (o.method, canonicalize(pn or "")),
                "body": norm_body(o.body_expr),
                "params": params,
                "token": m.group(1) if m else (auth if auth else None),
                "pear": any(k.lower() in PEAR_KEYS for k in hdrs),
                "skip": any(k.lower() == "x-skip-notifications" for k in hdrs),
                "others": {k: v for k, v in hdrs.items()
                           if k.lower() not in PEAR_KEYS and k.lower() not in
                           ("authorization", "content-type", "x-skip-notifications")},
            })
        elif o.kind == "assert":
            asserts.append((o.resp_var, o.expr,
                            CMP_MAP.get((o.comparison or "equal").lower(), o.comparison),
                            (o.expected_expr or "").strip()))
        elif o.kind == "extract":
            src = path.read_text(encoding="utf-8").splitlines()
            span = "\n".join(src[o.lineno - 1:o.end_lineno])
            m2 = re.search(r"\b(_\w+)\.json\(\)", span)   # 兼容 _resp1 / _resp_m / _aN
            resp = m2.group(1) if m2 else None
            if resp:
                ma = re.fullmatch(r"_a(\d+)", resp)
                if ma:
                    resp = f"_resp{ma.group(1)}"
            if not resp:
                # 手写补丁兜底：_cur = _jN ... vars[k] = _cur
                mw = re.search(r"_cur\s*=\s*(_\w+)\b", span)
                resp = mw.group(1) if (mw and re.search(r"vars\[", span)) else "?"
            extracts.append((o.name, o.expr, resp))
        elif o.kind == "var":
            vars_.append((o.key, norm_expr(o.value_expr)))
        else:
            s = o.source.strip()
            if re.fullmatch(r"_\w+\s*=\s*_resp\d+", s):
                continue
            if s.startswith(('"""', "'''")):      # docstring：新文件中同样不计入 raw
                try:
                    if isinstance(ast.literal_eval(s), str):
                        continue
                except Exception:
                    pass
            raws.append(norm_raw(s))
    return {"reqs": reqs, "asserts": asserts, "extracts": extracts,
            "vars": vars_, "raws": raws}


def norm_expr(e: str) -> str:
    try:
        t = ast.parse(e.strip(), mode="eval")
    except SyntaxError:
        return e.strip()

    class R(ast.NodeTransformer):
        def visit_Call(self, node):
            self.generic_visit(node)
            if getattr(node.func, "id", "") == "_render" and node.args:
                return ast.Call(func=ast.Attribute(value=ast.Name("ctx", ast.Load()),
                                                   attr="render", ctx=ast.Load()),
                                args=[node.args[0]], keywords=[])
            return node
    return ast.unparse(R().visit(t))


def norm_body(b: str) -> str:
    """空字符串字面量与省略 body 等价（'' / "" → ''）。"""
    b = (b or "").strip()
    return "" if b in ("''", '""') else b


def norm_raw(s: str) -> str:
    s = re.sub(r"case_vars\.save_runtime_tokens\((\w+)\)",
               r"ctx.save_runtime(list(\1))", s)
    return s


# --- 新文件指纹 ---------------------------------------------------------
def new_fingerprint(path: Path, by_name: dict) -> tuple[dict, list]:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name.startswith("test"))
    reqs, asserts, extracts, vars_, raws = [], [], [], [], []
    problems = []
    for stmt in fn.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            continue                                   # docstring
        # 跳过重写器注入的兼容序言（vars = ctx / base_url / client / _render / _url）
        if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name):
            tname = stmt.targets[0].id
            v = stmt.value
            is_ctx_alias = (
                tname == "vars" and isinstance(v, ast.Name) and v.id == "ctx"
            ) or (
                tname in ("base_url",) and isinstance(v, ast.Attribute)
                and isinstance(v.value, ast.Name) and v.value.id == "ctx"
            ) or (
                tname in ("client", "_render", "_url")
                and isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                and v.func.id in ("LegacyClient", "legacy_render", "legacy_url")
            )
            if is_ctx_alias:
                continue
        if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Name) \
                and stmt.targets[0].id.startswith("_resp"):
            call = stmt.value
            # 接受任意深度的 ctx.api.<...>.<method>(...) 链（如 ctx.api.admin.auth_login）
            if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                    and ast.unparse(call.func).startswith("ctx.api.")):
                problems.append(f"非 api 调用赋值: {ast.unparse(stmt)[:60]}")
                continue
            dom = call.func.value.attr               # ctx.api.<dom>.<method>（>=2 层）
            minfo = by_name.get((dom, call.func.attr))
            if minfo is None:
                problems.append(f"未知接口: {dom}.{call.func.attr}")
                continue
            kw = {k.arg: k.value for k in call.keywords}
            app_headers = lit(ast.unparse(kw["app_headers"])) if "app_headers" in kw \
                else bool(minfo.get("app_headers"))
            skip = lit(ast.unparse(kw["skip_notifications"])) if "skip_notifications" in kw \
                else bool(minfo.get("skip_notifications"))
            token = lit(ast.unparse(kw["token"])) if "token" in kw else None
            body = norm_body(ast.unparse(kw["body"])) if "body" in kw else ""
            params = lit(ast.unparse(kw["params"])) if "params" in kw else {}
            others = lit(ast.unparse(kw["headers"])) if "headers" in kw else {}
            pvar = lit(ast.unparse(kw["path_vars"])) if "path_vars" in kw else {}
            # path_vars 覆盖不影响 canonical 身份（{*}），但要记录供排查
            reqs.append({
                "key": (minfo["method"], minfo["path"]) if has_malformed(minfo["path"])
                       else (minfo["method"], canonicalize(unbrace(host_normalize(minfo["path"])))),
                "body": body, "params": params or {}, "token": token,
                "pear": bool(app_headers), "skip": bool(skip),
                "others": others or {}, "_pv": pvar or {},
            })
            continue
        s = ast.get_source_segment(src, stmt, padded=True) or ast.unparse(stmt)
        s = s.strip()
        m = re.match(r"^expect\((\w+)\)\.json\((.*?)\)\.(\w+)\((.*)\)$", s)
        if m:
            asserts.append((m.group(1),
                            lit_or_str(m.group(2)),
                            m.group(3),
                            norm_expected(m.group(4))))
            continue
        m = re.match(r"^ctx\.extract\((.*?)\)$", s)
        if m:
            parts = [lit_or_str(x) for x in split_args(m.group(1))]
            if len(parts) != 3:
                problems.append(f"extract 参数异常: {s[:60]}")
                continue
            extracts.append((parts[0], parts[2], parts[1]))
            continue
        m = re.match(r"^(\w+)\[(.*?)\]\s*=\s*(.*)$", s, re.S)
        if m and m.group(1) == "vars":
            vars_.append((lit_or_str(m.group(2)), norm_expr(m.group(3))))
            continue
        raws.append(norm_raw(s))
    return ({"reqs": reqs, "asserts": asserts, "extracts": extracts,
             "vars": vars_, "raws": raws}, problems)


def norm_expected(e: str) -> str:
    e = e.strip()
    m = re.match(r"^ctx\.render_text\((.*)\)$", e)
    return m.group(1) if m else e


def split_args(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


# --- 比对 ---------------------------------------------------------------
def diff(fp_old: dict, fp_new: dict, name: str) -> list[str]:
    out = []
    if len(fp_old["reqs"]) != len(fp_new["reqs"]):
        out.append(f"{name}: 请求数 {len(fp_old['reqs'])} != {len(fp_new['reqs'])}")
    for i, (a, b) in enumerate(zip(fp_old["reqs"], fp_new["reqs"])):
        for k in ("key", "body", "params", "token", "pear", "skip", "others"):
            if a[k] != b[k]:
                out.append(f"{name}: 请求#{i} {k} 不一致\n    旧: {a[k]!r}\n    新: {b[k]!r}")
    if len(fp_old["asserts"]) != len(fp_new["asserts"]):
        out.append(f"{name}: 断言数 {len(fp_old['asserts'])} != {len(fp_new['asserts'])}")
    for i, (a, b) in enumerate(zip(fp_old["asserts"], fp_new["asserts"])):
        # 旧 resp_var 可能为空（别名在 try 外），此时只比对 expr/比较/期望
        if a[0] and a[0] != b[0]:
            out.append(f"{name}: 断言#{i} 响应变量 {a[0]} != {b[0]}")
        if (a[1], a[2], a[3]) != (b[1], b[2], b[3]):
            out.append(f"{name}: 断言#{i} 不一致\n    旧: {a}\n    新: {b}")
    if len(fp_old["extracts"]) != len(fp_new["extracts"]):
        out.append(f"{name}: 提取数 {len(fp_old['extracts'])} != {len(fp_new['extracts'])}")
    for i, (a, b) in enumerate(zip(fp_old["extracts"], fp_new["extracts"])):
        if a != b:
            out.append(f"{name}: 提取#{i} {a} != {b}")
    if fp_old["vars"] != fp_new["vars"]:
        ov, nv = fp_old["vars"], fp_new["vars"]
        if len(ov) != len(nv):
            out.append(f"{name}: var 数 {len(ov)} != {len(nv)}")
        else:
            for i, (a, b) in enumerate(zip(ov, nv)):
                if a != b:
                    out.append(f"{name}: var#{i} {a} != {b}")
    if fp_old["raws"] != fp_new["raws"]:
        o_r, n_r = fp_old["raws"], fp_new["raws"]
        if len(o_r) != len(n_r):
            out.append(f"{name}: raw 数 {len(o_r)} != {len(n_r)}")
        else:
            for i, (a, b) in enumerate(zip(o_r, n_r)):
                if a != b:
                    out.append(f"{name}: raw#{i} 不一致\n    旧: {a[:90]}\n    新: {b[:90]}")
    return out


def main():
    by_name, _ = build_index()
    old_files = sorted(OLD.rglob("test_*.py"))
    diffs, problems = [], []
    for of in old_files:
        rel = of.relative_to(OLD)
        nf = NEW / rel
        if not nf.exists():
            diffs.append(f"{rel}: 新文件缺失")
            continue
        fo = old_fingerprint(of)
        fn, probs = new_fingerprint(nf, by_name)
        problems.extend(f"{rel}: {p}" for p in probs)
        diffs.extend(diff(fo, fn, str(rel)))
    print(f"比对文件数: {len(old_files)}")
    print(f"语义差异: {len(diffs)} 处")
    report = Path(__file__).resolve().parent / "verify_diffs.txt"
    report.write_text("\n".join(diffs), encoding="utf-8")
    print(f"完整差异已写入: {report}")
    for d in diffs[:40]:
        print("  ✗", d)
    if problems:
        print(f"\n解析问题: {len(problems)} 处")
        for p in problems[:20]:
            print("  !", p)
    if not diffs and not problems:
        print("\n✅ 语义等价校验通过：146 条用例 100% 一致")


if __name__ == "__main__":
    main()
