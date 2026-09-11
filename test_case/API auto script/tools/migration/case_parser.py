"""用例解析器：把迁移生成的 ``test_*.py`` 解析成结构化中间表示（IR）。

为什么是「解析既有 .py」而不是「从 Apifox 原始 JSON 重新生成」
--------------------------------------------------------------
``_apifox_export/cases_raw/`` 是 2026-09-07 的**过期快照**，而 ``tests/`` 下的脚本
是 09-08~09-09 重新抓取并人工修补后的产物。实测 **134/146** 个文件内容不一致，
且脚本侧内容**更多**（个别用例 raw 为 0 个请求、脚本有 31 个）。

因此以脚本为唯一权威源，本解析器负责无损抽取其中的：

* 模块元数据（NAME / TAGS / PRIORITY / CASE_ID）
* 请求（method / path / headers / params / body）
* 断言（JSONPath / 比较方式 / 期望值）
* 提取器（变量名 / JSONPath）
* **人工补丁**（裸 assert、for/if 逻辑、中间变量、print、import）—— 原样保留

生成器产出的代码形态高度规整，因此采用「AST 定位语句 + 源码行读取标签注释」的混合策略：

* 比较方式（equal / exists / include / isEmpty）从 ``# assertion ...: responseJson <cmp>`` 标签读取
  ——因为 ``exists`` 与 ``equal ''`` 在代码层面无法区分（这正是旧生成器的缺陷）
* JSONPath 原表达式从 ``_parts = [...] if '<EXPR>'.startswith('$')`` 里精确还原
  ——比用 segments 反推更可靠（``..`` 递归语义不会丢）
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

# --- 标签注释 -----------------------------------------------------------
RE_STEP = re.compile(r"^#\s*step\s+(\d+)\s*:?\s*(.*)$")
RE_ASSERT_LABEL = re.compile(r"^#\s*assertion\s+(\S+?):\s*(\S+)\s+(\S+)\s*(.*)$")
RE_EXTRACT_LABEL = re.compile(r"^#\s*extractor:\s*(\w+)\s*=\s*(.+?)\s*$")
RE_CASE_ID_HDR = re.compile(r"^#\s*Apifox Case ID:\s*(\d+)", re.M)
RE_HEADER_CASE = re.compile(r"^#\s*Case:\s*(.+)$", re.M)
RE_HEADER_PRI = re.compile(r"^#\s*Priority:\s*P?(\d+)", re.M)
RE_FOLDER_HDR = re.compile(r"^#\s*Folder:\s*(.*)$", re.M)


@dataclass
class Op:
    """一个测试步骤内的原子操作。"""
    kind: str                  # request | assert | extract | var | raw
    lineno: int = 0
    end_lineno: int = 0
    # request
    var: str = ""              # _respN
    method: str = ""
    path_expr: str = ""        # Python 源码表达式（可能是字面量或 f-string）
    headers_expr: str = ""     # dict 字面量源码
    params_expr: str = ""      # dict 字面量源码
    body_expr: str = ""        # 字符串字面量源码，或 "" 表示无 body
    step_label: str = ""
    # assert
    resp_var: str = ""
    expr: str = ""             # JSONPath
    comparison: str = ""       # equal | exists | include | isEmpty | ...
    expected_expr: str = ""    # 期望值源码表达式
    label: str = ""
    # extract
    name: str = ""
    # var
    key: str = ""
    value_expr: str = ""
    # raw
    source: str = ""


@dataclass
class ParsedCase:
    path: Path
    folder: str
    case_id: int | None = None
    name: str = ""
    tags: list = field(default_factory=list)
    priority: int | None = None
    func: str = ""
    ops: list = field(default_factory=list)
    has_custom_fixture: bool = False
    url_variant: str = "A"
    warnings: list = field(default_factory=list)

    @property
    def slug(self) -> str:
        return self.path.stem


# --- 工具 ---------------------------------------------------------------
def _src_of(node: ast.AST, lines: list[str]) -> str:
    """取节点对应的源码片段（保留首行缩进，重写器直接可用）。

    .. note::
       ``ast.get_source_segment(padded=True)`` 对**单行语句不补缩进**
       （CPython 只对多行片段做 padding），此处统一补上语句所在行的前导空白。
    """
    seg = ast.get_source_segment("\n".join(lines), node, padded=True) or ""
    if seg and not seg[0] in " \t" and 0 < node.lineno <= len(lines):
        indent = re.match(r"[ \t]*", lines[node.lineno - 1]).group(0)
        seg = indent + seg
    return seg


def _const(node) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _labels_above(lines: list[str], lineno: int) -> list[str]:
    """收集紧邻语句上方的连续注释行（1-based lineno）。"""
    out: list[str] = []
    i = lineno - 2  # 转 0-based 并上移一行
    while i >= 0:
        s = lines[i].strip()
        if s.startswith("#"):
            out.append(s)
            i -= 1
        elif s == "":
            # 允许注释块与语句之间夹空行（生成器偶尔会留）
            if out:
                break
            i -= 1
        elif re.fullmatch(r"\w+\s*=\s*\w+", s) and not out:
            # 生成器空转行（_respN = _respN / _aN = _respN）常隔在标签与语句之间
            i -= 1
        else:
            break
    return list(reversed(out))


# --- 请求解析 -----------------------------------------------------------
def _parse_request(node: ast.Assign, lines: list[str]) -> Op | None:
    if not isinstance(node.targets[0], ast.Name):
        return None
    var = node.targets[0].id
    if not var.startswith("_resp"):
        return None
    call = node.value
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and call.func.attr == "request"):
        return None

    op = Op(kind="request", var=var, lineno=node.lineno, end_lineno=node.end_lineno or node.lineno)

    # method
    if call.args:
        op.method = (_const(call.args[0]) or "").upper()

    # path
    if len(call.args) >= 2:
        a1 = call.args[1]
        if isinstance(a1, ast.Call) and getattr(a1.func, "id", "") == "_url" and len(a1.args) >= 2:
            op.path_expr = ast.unparse(a1.args[1])
        else:
            op.path_expr = ast.unparse(a1)

    # headers / params / data
    for kw in call.keywords:
        if kw.arg == "headers":
            op.headers_expr = _headers_to_expr(kw.value)
        elif kw.arg == "params":
            op.params_expr = ast.unparse(kw.value)
        elif kw.arg == "data":
            op.body_expr = _body_to_expr(kw.value)

    # step label
    for lab in _labels_above(lines, node.lineno):
        m = RE_STEP.match(lab)
        if m:
            op.step_label = m.group(2).strip()
    return op


def _headers_to_expr(node: ast.AST) -> str:
    """把 ``{k:_render(v, vars) for k, v in [(k, v), ...]}`` 还原成 dict 字面量源码。"""
    # 形态一：字典推导 + 元组列表（生成器标准写法）
    if isinstance(node, ast.DictComp):
        gen = node.generators[0]
        it = gen.iter
        if isinstance(it, (ast.List, ast.Tuple)):
            pairs = []
            for elt in it.elts:
                if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                    k = _const(elt.elts[0])
                    v = _const(elt.elts[1])
                    if k is not None:
                        pairs.append((k, v if v is not None else ast.unparse(elt.elts[1])))
            return "{" + ", ".join(f"{k!r}: {v!r}" for k, v in pairs) + "}"
    # 形态二：普通 dict 字面量
    if isinstance(node, ast.Dict):
        return ast.unparse(node)
    return ast.unparse(node)


def _body_to_expr(node: ast.AST) -> str:
    """还原请求体模板源码；无 body 返回空串。"""
    # 形态：_render('...', vars) if True else None
    if isinstance(node, ast.IfExp):
        node = node.body
    if isinstance(node, ast.Constant) and node.value is None:
        return ""
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_render":
        if node.args:
            c = _const(node.args[0])
            if c is not None:
                return repr(c)
            return ast.unparse(node.args[0])
    c = _const(node)
    if c is not None:
        return repr(c)
    return ast.unparse(node)


# --- 断言解析 -----------------------------------------------------------
def _extract_jsonpath(node: ast.AST) -> str:
    """从 ``_parts = [...] if '<EXPR>'.startswith('$') else []`` 还原原表达式。"""
    if isinstance(node, ast.IfExp):
        test = node.test
        if isinstance(test, ast.Call) and isinstance(test.func, ast.Attribute) \
                and test.func.attr == "startswith" and test.args:
            # 主体才是 JSONPath（'<EXPR>'.startswith('$')），参数只是前缀 '$'
            c = _const(test.func.value)
            if c is not None:
                return c
    return ""


def _parse_assertion(try_node: ast.Try, lines: list[str]) -> Op | None:
    """识别断言块（handler 为 AssertionError）。"""
    if not try_node.handlers:
        return None
    h = try_node.handlers[0]
    if getattr(h.type, "id", None) != "AssertionError":
        return None

    op = Op(kind="assert", lineno=try_node.lineno, end_lineno=try_node.end_lineno or try_node.lineno)

    assert_stmt = None
    for st in try_node.body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name):
            t = st.targets[0].id
            if t.startswith("_a"):
                src = _src_of(st.value, lines)
                if isinstance(st.value, ast.Name):
                    op.resp_var = st.value.id
                else:
                    # _a4 = _resp4 之外还可能带后缀
                    op.resp_var = src.strip()
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Name) \
                and st.targets[0].id == "_parts":
            op.expr = _extract_jsonpath(st.value)
        if isinstance(st, ast.Assert):
            assert_stmt = st

    if assert_stmt is None:
        return None

    # 比较方式：优先读标签注释，其次按代码形态推断
    for lab in _labels_above(lines, try_node.lineno):
        m = RE_ASSERT_LABEL.match(lab)
        if m:
            # 组结构: (1)=标签 (2)=subject (3)=comparison (4)=期望值
            op.comparison = m.group(3).strip()
            op.label = m.group(1).strip()
            break

    if not op.comparison:
        op.comparison = _infer_comparison(assert_stmt)

    op.expected_expr = _expected_of(assert_stmt, op.comparison)
    return op


def _infer_comparison(node: ast.Assert) -> str:
    """按 assert 代码形态推断比较方式（标签缺失时的兜底）。"""
    src = ast.unparse(node.test)
    if src.startswith("any("):
        return "include"
    if src.startswith("not "):
        return "isEmpty"
    if "is not None" in src:
        # assert _cur is not None and str(_cur) != '' —— Apifox exists 断言的标准生成形态
        return "exists"
    return "equal"


def _expected_of(node: ast.Assert, comparison: str) -> str:
    """从 assert 语句提取期望值源码表达式。"""
    test = node.test
    if comparison == "isEmpty":
        return ""
    if comparison in ("exists", "not_exists", "notExists"):
        return ""
    if comparison == "include" and isinstance(test, ast.Call):
        # any(str(v) == <EXPECTED> for v in _cur)
        if test.args:
            cmp_node = test.args[0]
            if isinstance(cmp_node, ast.GeneratorExp):
                cmp_node = cmp_node.elt          # any( <Compare> for v in _cur )
            if isinstance(cmp_node, ast.Compare) and len(cmp_node.comparators) == 1:
                return _strip_render(cmp_node.comparators[0])
        return ""
    if isinstance(test, ast.Compare) and len(test.comparators) == 1:
        return _strip_render(test.comparators[0])
    return ""


def _strip_render(node: ast.AST) -> str:
    """去掉 ``_render(x, vars)`` 外壳，返回 x 的源码；``_render('', vars)`` 返回空串。"""
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_render":
        if node.args:
            c = _const(node.args[0])
            if c is not None:
                return repr(c) if c != "" else "''"
            return ast.unparse(node.args[0])
    return ast.unparse(node)


# --- 提取器解析 ---------------------------------------------------------
def _parse_extractor(try_node: ast.Try, lines: list[str]) -> Op | None:
    """识别提取器块（handler 为 Exception，且体内写 ``vars[...]``）。"""
    if not try_node.handlers:
        return None
    if getattr(try_node.handlers[0].type, "id", None) != "Exception":
        return None

    target = None
    for st in try_node.body:
        if isinstance(st, ast.Assign) and isinstance(st.targets[0], ast.Subscript) \
                and getattr(st.targets[0].value, "id", "") == "vars":
            key = _const(st.targets[0].slice)
            if key:
                target = key
    if not target:
        return None

    op = Op(kind="extract", name=target, lineno=try_node.lineno,
            end_lineno=try_node.end_lineno or try_node.lineno)

    # 优先用标签注释里的表达式（对 ``..`` 递归提取无损）
    for lab in _labels_above(lines, try_node.lineno):
        m = RE_EXTRACT_LABEL.match(lab)
        if m:
            op.expr = m.group(2).strip()
            break

    # 兜底：从 ``for _p in ['data', 'token']: ...`` 还原
    if not op.expr:
        segs = _segments_of(try_node)
        if segs:
            recursive = any(s == "" for s in segs)
            if recursive:
                op.expr = "$" + "..".join(s for s in segs if s)
            else:
                op.expr = "$." + ".".join(segs)
    if not op.expr:
        return None
    return op


def _segments_of(try_node: ast.Try) -> list[str]:
    for st in try_node.body:
        for sub in ast.walk(st):
            if isinstance(sub, ast.For) and isinstance(sub.iter, (ast.List, ast.Tuple)):
                segs = [_const(e) for e in sub.iter.elts]
                if all(s is not None for s in segs):
                    return segs
    return []


# --- 顶层解析 -----------------------------------------------------------
def parse_case(path: Path, tests_root: Path | None = None) -> ParsedCase:
    """解析单个用例文件。"""
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    tree = ast.parse(src)

    root = tests_root or path.parent
    try:
        rel = path.relative_to(root)
        folder = str(rel.parent)
    except ValueError:
        folder = path.parent.name
    pc = ParsedCase(path=path, folder="" if folder == "." else folder)

    # 模块级元数据
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            k = node.targets[0].id
            try:
                v = ast.literal_eval(node.value)
            except Exception:
                continue
            if k == "NAME":
                pc.name = str(v)
            elif k == "TAGS" and isinstance(v, (list, tuple)):
                pc.tags = [str(x) for x in v]
            elif k == "PRIORITY":
                pc.priority = int(v)
            elif k == "CASE_ID":
                pc.case_id = int(v)

    m = RE_CASE_ID_HDR.search(src)
    if pc.case_id is None and m:
        pc.case_id = int(m.group(1))
    if not pc.name:
        m2 = RE_HEADER_CASE.search(src)
        if m2:
            pc.name = re.sub(r"^\([^)]*\)\s*T?\d+\s*", "", m2.group(1)).strip()
    if pc.priority is None:
        m3 = RE_HEADER_PRI.search(src)
        if m3:
            pc.priority = int(m3.group(1))
    if not pc.name:
        pc.name = pc.path.stem

    # 自定义 fixture / URL 变体
    pc.has_custom_fixture = bool(re.search(r"^@pytest\.fixture[^\n]*\n(?:.*\n)?def _ctx", src, re.M))
    if "if '://' in p" in src:
        pc.url_variant = "B"

    # 测试函数
    fns = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test")]
    if not fns:
        pc.warnings.append("未找到 test_* 函数")
        return pc
    fn = fns[0]
    pc.func = fn.name

    # 逐个语句分类
    for node in fn.body:
        if isinstance(node, ast.Assign):
            tgt = node.targets[0]
            if isinstance(tgt, ast.Subscript) and getattr(tgt.value, "id", "") == "vars":
                key = _const(tgt.slice)
                if key:
                    pc.ops.append(Op(kind="var", key=key, value_expr=ast.unparse(node.value),
                                     lineno=node.lineno, end_lineno=node.end_lineno or node.lineno))
                    continue
            if isinstance(tgt, ast.Name):
                # 前置样板
                if tgt.id in ("client", "base_url", "vars"):
                    continue
                # 生成器空转：_resp7 = _resp7
                if isinstance(node.value, ast.Name) and node.value.id == tgt.id:
                    continue
                req = _parse_request(node, lines)
                if req:
                    pc.ops.append(req)
                    continue
            pc.ops.append(_raw_op(node, lines))
            continue

        if isinstance(node, ast.Try):
            h = node.handlers[0] if node.handlers else None
            hname = getattr(getattr(h, "type", None), "id", None)
            if hname == "AssertionError":
                op = _parse_assertion(node, lines)
                if op:
                    pc.ops.append(op)
                    continue
            elif hname == "Exception":
                op = _parse_extractor(node, lines)
                if op:
                    pc.ops.append(op)
                    continue
            pc.ops.append(_raw_op(node, lines))
            continue

        pc.ops.append(_raw_op(node, lines))

    return pc


def _raw_op(node: ast.AST, lines: list[str]) -> Op:
    src = _src_of(node, lines) or ast.unparse(node)
    return Op(kind="raw", source=src, lineno=node.lineno,
              end_lineno=node.end_lineno or node.lineno)
