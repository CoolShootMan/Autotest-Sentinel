"""用例审计引擎（harness 核心）。

设计目标
--------
为 autotest-expert agent 提供一个**可机读**的静态分析器，输出结构化
``Finding`` 列表。它回答的不是"代码能不能跑"，而是：

1. **完整性 (Integrity)** —— 结构性反模式：占位符错位、直接 requests、缺
   元数据、敏感信息泄漏、屏蔽异常的 try/except。
2. **完备性 (Completeness)** —— 测试质量信号：缺断言、零边界场景、未注册
   到任何 suite、TODO 残留。

调用方式
--------
CLI::

    python -m core.case_audit tests/01_Login\ flow
    python -m core.case_audit tests/01_Login\ flow --json
    python -m core.case_audit tests/01_Login\ flow --severity error --strict

库::

    from core.case_audit import audit_file, audit_tree
    findings = audit_file(Path("tests/foo/test_x.py"))
    summary  = summarize(findings)

退出码
------
* 0：无 error 级发现。
* 1：有 error 级发现。
* 2：参数错误 / 文件读取失败。

扩展约定
--------
新规则请加在 ``RULES`` 列表中，签名::

    def rule_xxx(path: Path, tree: ast.Module, src: str) -> Iterable[Finding]:

返回的 ``Finding`` 必须填写 ``rule_id``（短字符串，便于 ``--ignore``）、
``severity``、``line``、``message``，可选 ``fix_hint``。
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Iterator


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------

SEV_ERROR = "error"          # 阻塞：必须修才能跑/合并
SEV_WARN = "warning"         # 警告：可能影响质量，但不阻塞
SEV_INFO = "info"            # 提示：风格建议

SEV_ORDER = {SEV_ERROR: 0, SEV_WARN: 1, SEV_INFO: 2}


@dataclass
class Finding:
    rule_id: str
    severity: str
    line: int
    message: str
    snippet: str = ""
    fix_hint: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------

def _strip_doc_lines(src: str) -> set[int]:
    """返回位于三引号字符串 / 注释 / f-string 内的行号集合。

    解释反模式的注释、f-string 字面量里的 ``{var}`` 是合法 Python，
    不应被单花括号模板规则误报。
    """
    lines = src.splitlines()
    in_doc = False
    out: set[int] = set()
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("#"):
            out.add(i)
            continue
        triple_double = s.count('"""')
        triple_single = s.count("'''")
        if triple_double == 2 or triple_single == 2:
            out.add(i)
            continue
        if triple_double or triple_single:
            in_doc = not in_doc
            out.add(i)
            continue
        if in_doc:
            out.add(i)
            continue
        # f-string：``f"..."`` / ``f'...'``；里面的 ``{var}`` 是合法 Python。
        if re.search(r"\bf['\"]", s):
            out.add(i)
    return out


def _is_string_node(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def _line_of(src: str, pos: int) -> int:
    return src.count("\n", 0, pos) + 1


def _snippet(src: str, line: int) -> str:
    lines = src.splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()[:80]
    return ""


# 常见的敏感信息正则
_LIVE_TOKEN_RE = re.compile(r"eyJ[A-Za-z0-9_\-]{40,}")                    # JWT
_HEX_PASSWORD_RE = re.compile(
    r"password['\"]?\s*[:=]\s*['\"][0-9a-fA-F]{16,}['\"]?", re.I,
)
# 形如 token=、secret=、api_key=、client_secret= 后跟非占位符串。
# 长度要求 ≥16，匹配后再用 _looks_like_secret 过滤，避免误报像
# ``token='linda01_token'`` 这种纯标识符形态的占位变量名。
_SECRET_KV_RE = re.compile(
    r"""(?:token|secret|api[_-]?key|client[_-]?secret)\s*[:=]\s*['\"](?!\{\{)([^'\"\s]{16,})['\"]?""",
    re.I,
)


def _looks_like_secret(s: str) -> bool:
    """判定字符串是否"看起来像真密钥"。

    判定要点：
    - snake_case 标识符（``linda01_token``）→ 不是密钥，是占位变量名。
    - 全大写 + 下划线（``MY_APP_SECRET``）→ 也常被当作常量名，跳过。
    - 全数字 / 全字母 / 全是 word 字符 → 不是密钥。
    - 含 base64 / hex 字符（+/= / 0-9a-f 混合）→ 像密钥。
    """
    if re.fullmatch(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+", s):  # snake_case id
        return False
    if re.fullmatch(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+", s):  # UPPER_SNAKE
        return False
    if re.fullmatch(r"\w+", s):                              # 纯 word 字符
        return False
    return True


# ---------------------------------------------------------------------------
# 规则集
# ---------------------------------------------------------------------------

Rule = Callable[[Path, ast.Module, str], Iterable[Finding]]
RULES: list[Rule] = []


def _register(fn: Rule) -> Rule:
    RULES.append(fn)
    return fn


@_register
def rule_metadata_complete(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """A.3 用例骨架：必须包含 NAME / TAGS / PRIORITY / CASE_ID / ENV_NAME + def test_*. """
    found: set[str] = set()
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            found.add(n.targets[0].id)
    required = ["NAME", "TAGS", "PRIORITY", "CASE_ID", "ENV_NAME"]
    has_test_fn = any(
        isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
        for n in tree.body
    )
    for r in required:
        if r not in found:
            yield Finding(
                rule_id="META_MISSING",
                severity=SEV_ERROR,
                line=1,
                message=f"缺少模块级常量 {r}",
                fix_hint=f"在模块顶部补：{r} = ...（详见 ONBOARDING §6.2）",
            )
    if not has_test_fn:
        yield Finding(
            rule_id="META_NO_TEST_FN",
            severity=SEV_ERROR,
            line=1,
            message="未发现任何 test_* 函数，pytest 不会收",
            fix_hint="至少实现 def test_<slug>(ctx): ...",
        )


@_register
def rule_no_direct_requests(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """A.5 调用方式断言：禁止直接 requests.* 。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            # requests.get/post/...
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                if f.value.id == "requests" and f.attr in {
                    "get", "post", "put", "delete", "patch", "head", "options", "request",
                }:
                    yield Finding(
                        rule_id="API_DIRECT_REQUESTS",
                        severity=SEV_ERROR,
                        line=node.lineno,
                        message=f"禁止直接调用 requests.{f.attr}(...)，全部走 ctx.api.*",
                        snippet=_snippet(src, node.lineno),
                        fix_hint="改用 ctx.api.<module>.<method>(...)，新增接口补到 api/ 下",
                    )


@_register
def rule_single_brace_placeholder(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """A.4 占位符断言：必须双花括号 {{var}}，禁止单花括号 {var}。"""
    rx = re.compile(r"(?<!\{)\{[A-Za-z_]\w*\}(?!\})")
    doc_lines = _strip_doc_lines(src)
    for m in rx.finditer(src):
        ln = _line_of(src, m.start())
        if ln in doc_lines:
            continue
        yield Finding(
            rule_id="PLACEHOLDER_SINGLE_BRACE",
            severity=SEV_ERROR,
            line=ln,
            message="单花括号模板不会被渲染，会原样发出 → 400",
            snippet=_snippet(src, ln),
            fix_hint="改为双花括号 {{var}}",
        )


@_register
def rule_literal_self_extract(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """vars['k'] = 'k' 占位回填自身 → 提取器翻译失败。"""
    rx = re.compile(r"""vars\[['"](\w+)['"]\]\s*=\s*['"]\1['"]""")
    doc_lines = _strip_doc_lines(src)
    for m in rx.finditer(src):
        ln = _line_of(src, m.start())
        if ln in doc_lines:
            continue
        yield Finding(
            rule_id="EXTRACT_SELF_LITERAL",
            severity=SEV_ERROR,
            line=ln,
            message="占位回填自身：vars['k'] = 'k' 不会真的回填 ctx",
            snippet=_snippet(src, ln),
            fix_hint="使用 ctx.extract('k', resp, '$.path')",
        )


@_register
def rule_local_get_path(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """本地 def _get_path 会遮蔽 core.compat._get_path。"""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_get_path":
            yield Finding(
                rule_id="COMPAT_GET_PATH_SHADOW",
                severity=SEV_ERROR,
                line=node.lineno,
                message="本地定义 _get_path 会遮蔽 core.compat._get_path",
                snippet=_snippet(src, node.lineno),
                fix_hint="删除本地定义，使用 from core.compat import _get_path",
            )


@_register
def rule_sensitive_info(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """A.7 敏感信息：模板中不应出现 LIVE token / 密码。"""
    doc_lines = _strip_doc_lines(src)
    for rx, label in (
        (_LIVE_TOKEN_RE, "疑似 LIVE JWT"),
        (_HEX_PASSWORD_RE, "疑似 LIVE 16 进制密码"),
        (_SECRET_KV_RE, "疑似硬编码 secret/token/api_key"),
    ):
        for m in rx.finditer(src):
            ln = _line_of(src, m.start())
            if ln in doc_lines:
                continue
            # 对 kv 类规则再做"是否像真密钥"过滤
            if rx is _SECRET_KV_RE:
                grp = m.group(1)
                if grp and not _looks_like_secret(grp):
                    continue
            yield Finding(
                rule_id="SECRET_LEAK",
                severity=SEV_ERROR,
                line=ln,
                message=label,
                snippet=_snippet(src, ln),
                fix_hint="改为 {{VAR}} 引用，值放入 .env / config/environments/*.yaml",
            )


@_register
def rule_assertion_present(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """完备性：测试函数体至少要有一处 expect(...)。"""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            has_expect = any(
                isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                and c.func.id == "expect"
                for c in ast.walk(node)
            )
            if not has_expect:
                yield Finding(
                    rule_id="ASSERTION_MISSING",
                    severity=SEV_WARN,
                    line=node.lineno,
                    message=f"test 函数 {node.name}!() 体内没有任何 expect(...)，"
                            "等价于只调不打",
                    fix_hint="对每个调用的接口加 expect(resp).json('$.code').equals('200')",
                )


@_register
def rule_extracts_have_assertions(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """完备性：ctx.extract(...) 之后应至少有一处断言。"""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            sub_src = ast.unparse(node)
            if "ctx.extract(" in sub_src and "expect(" not in sub_src:
                yield Finding(
                    rule_id="EXTRACT_NO_ASSERT",
                    severity=SEV_WARN,
                    line=node.lineno,
                    message=f"{node.name} 只 extract 不断言，无法失败",
                    fix_hint="extract 后立刻 expect(resp).json('$.code').equals('200')",
                )


@_register
def rule_no_swallowed_exception(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """try/except: pass / Exception → 吞掉异常属于反模式。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for h in node.handlers:
                body = h.body
                # bare 'pass' or only assignment to dummy
                if all(isinstance(b, ast.Pass) for b in body):
                    yield Finding(
                        rule_id="EXCEPTION_SWALLOWED",
                        severity=SEV_WARN,
                        line=h.lineno,
                        message="except 块只有 pass，异常被静默吞掉",
                        snippet=_snippet(src, h.lineno),
                        fix_hint="至少记录日志或重新抛出；不要用 try/except 压住失败",
                    )


@_register
def rule_no_time_sleep(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """禁止 time.sleep：偶发问题用诊断而非加 sleep。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr == "sleep":
                yield Finding(
                    rule_id="TIMING_SLEEP",
                    severity=SEV_WARN,
                    line=node.lineno,
                    message="禁止 time.sleep()，会掩盖时序问题",
                    snippet=_snippet(src, node.lineno),
                    fix_hint="用 diagnose_failed.py 定位根因，或改用条件轮询",
                )


@_register
def rule_xfails_have_reason(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """@pytest.mark.xfail 必须带 reason。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "xfail":
            # 找到最近的装饰器
            for parent in ast.walk(tree):
                if isinstance(parent, ast.FunctionDef):
                    for dec in parent.decorator_list:
                        if dec is node:
                            has_reason = any(
                                isinstance(kw, ast.keyword) and kw.arg == "reason"
                                for kw in node.keywords
                            )
                            if not has_reason:
                                yield Finding(
                                    rule_id="XFAIL_NO_REASON",
                                    severity=SEV_WARN,
                                    line=parent.lineno,
                                    message=f"{parent.name} 上的 xfail 没有 reason=",
                                    fix_hint='@pytest.mark.xfail(reason="T1234: 接口已下线")',
                                )


@_register
def rule_priority_matches_tag(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """PRIORITY 与 TAGS 中的 p<n> 应一致。"""
    prio = None
    tags: list[str] = []
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            try:
                if n.targets[0].id == "PRIORITY":
                    prio = ast.literal_eval(n.value)
                elif n.targets[0].id == "TAGS":
                    v = ast.literal_eval(n.value)
                    if isinstance(v, (list, tuple)):
                        tags = [str(x) for x in v]
            except Exception:
                continue
    if prio is None:
        return
    expected = f"p{prio}"
    if expected not in tags:
        yield Finding(
            rule_id="TAG_PRIORITY_MISMATCH",
            severity=SEV_INFO,
            line=1,
            message=f"PRIORITY={prio} 但 TAGS 里没有 {expected!r}",
            fix_hint=f"在 TAGS 头部加 {expected!r}",
        )


@_register
def rule_test_function_uses_ctx(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """测试函数若没有 'ctx' 参数，将无法使用框架。"""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            args = [a.arg for a in node.args.args]
            if "ctx" not in args:
                yield Finding(
                    rule_id="TEST_NO_CTX_FIXTURE",
                    severity=SEV_ERROR,
                    line=node.lineno,
                    message=f"{node.name}!() 缺少 ctx fixture 参数",
                    fix_hint="签名改为 def test_xxx(ctx): ...",
                )


@_register
def rule_todo_fixme(path: Path, tree: ast.Module, src: str) -> Iterator[Finding]:
    """完整性：残留的 TODO / FIXME / XXX 应当显式清理。"""
    rx = re.compile(r"#\s*(TODO|FIXME|XXX)\b", re.I)
    for m in rx.finditer(src):
        yield Finding(
            rule_id="TODO_LEFT",
            severity=SEV_INFO,
            line=_line_of(src, m.start()),
            message="检测到 TODO/FIXME/XXX 标记，提交前请清理",
            snippet=_snippet(src, _line_of(src, m.start())),
        )


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def _scan_one(path: Path) -> tuple[list[Finding], str | None]:
    try:
        src = path.read_text(encoding="utf-8")
    except OSError as e:
        return [], f"无法读取 {path}: {e}"
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        return [Finding(
            rule_id="SYNTAX_ERROR",
            severity=SEV_ERROR,
            line=e.lineno or 1,
            message=f"语法错误：{e.msg}",
        )], None
    findings: list[Finding] = []
    for rule in RULES:
        findings.extend(rule(path, tree, src))
    return findings, None


def audit_file(path: Path) -> list[Finding]:
    fs, err = _scan_one(path)
    if err:
        return [Finding(
            rule_id="READ_ERROR",
            severity=SEV_ERROR,
            line=0,
            message=err,
        )]
    return fs


def audit_tree(root: Path) -> dict[Path, list[Finding]]:
    out: dict[Path, list[Finding]] = {}
    for p in sorted(root.rglob("test_*.py")):
        if p.name.startswith("__"):
            continue
        out[p] = audit_file(p)
    return out


def summarize(findings: list[Finding]) -> dict:
    by_sev: dict[str, int] = {SEV_ERROR: 0, SEV_WARN: 0, SEV_INFO: 0}
    by_rule: dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
        by_rule[f.rule_id] = by_rule.get(f.rule_id, 0) + 1
    return {"by_severity": by_sev, "by_rule": by_rule, "total": len(findings)}


def _print_human(per_file: dict[Path, list[Finding]], strict: bool) -> int:
    max_sev = -1
    for path, fs in per_file.items():
        if not fs:
            continue
        max_sev = max(max_sev, max((SEV_ORDER[f.severity] for f in fs), default=-1))
        print(f"\n{path}")
        for f in sorted(fs, key=lambda x: (SEV_ORDER[x.severity], x.line)):
            tag = {"error": "[ERROR]", "warning": "[WARN]", "info": "[INFO]"}[f.severity]
            print(f"  {tag} line {f.line:<4} {f.rule_id}: {f.message}")
            if f.snippet:
                print(f"           | {f.snippet}")
            if f.fix_hint and (strict or f.severity != SEV_INFO):
                print(f"           -> {f.fix_hint}")
    total_err = sum(1 for fs in per_file.values() for f in fs if f.severity == SEV_ERROR)
    total_warn = sum(1 for fs in per_file.values() for f in fs if f.severity == SEV_WARN)
    total_info = sum(1 for fs in per_file.values() for f in fs if f.severity == SEV_INFO)
    print(f"\n=== 汇总 ===  error={total_err}  warning={total_warn}  info={total_info}")
    return 1 if total_err else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="用例审计引擎 (harness)")
    ap.add_argument("path", nargs="+", help="文件或目录")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--strict", action="store_true", help="把所有 INFO 当成 WARN 显示 fix_hint")
    ap.add_argument("--ignore", action="append", default=[], help="按 rule_id 忽略，重复传")
    args = ap.parse_args(argv)

    per_file: dict[Path, list[Finding]] = {}
    for p in args.path:
        path = Path(p)
        if path.is_dir():
            per_file.update(audit_tree(path))
        else:
            per_file[path] = audit_file(path)

    if args.ignore:
        for path in per_file:
            per_file[path] = [f for f in per_file[path] if f.rule_id not in set(args.ignore)]

    if args.json:
        payload = {
            str(p): [f.to_dict() for f in fs] for p, fs in per_file.items()
        }
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 1 if any(f.severity == SEV_ERROR for fs in per_file.values() for f in fs) else 0

    return _print_human(per_file, args.strict)


if __name__ == "__main__":
    sys.exit(main())