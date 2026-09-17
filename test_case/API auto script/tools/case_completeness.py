"""用例完备性评分器（harness 完整性子系统）。

设计目标
--------
审计引擎回答"是否写得对"，**完备性评分**回答"是否覆盖到位"。两者
一起，才能保证 agent 生成的用例质量。

评分维度（每项 0~100，最终加权平均）：
1. **结构完整 (StructuralIntegrity, 25%)** —— 元数据齐全、有 test_*
   函数、签名带 ctx、import 完整。
2. **断言密度 (AssertionDensity, 25%)** —— expect 调用数 / ctx.api
   调用数，太低说明只调不打。
3. **场景多样性 (ScenarioCoverage, 20%)** —— happy/sad/boundary/
   permission 四个维度有没有覆盖（用关键字/TAG 启发式判断）。
4. **可追溯性 (Traceability, 15%)** —— CASE_ID 存在、TAGS 含
   folder marker、suite 注册。
5. **上下文自洽 (ContextConsistency, 15%)** —— 变量是否在 vars.yaml
   中声明、extract 的变量后续是否使用。

调用方式
--------
CLI::

    python tools/case_completeness.py tests/01_Login\\ flow
    python tools/case_completeness.py tests --json --top 10

输出 ``score >= 80`` 视为合格。
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests"
SUITES_DIR = ROOT / "suites"


@dataclass
class CompletenessReport:
    path: str
    name: str | None
    case_id: int | None
    priority: int | None
    tags: list[str] = field(default_factory=list)
    api_calls: int = 0
    api_modules: list[str] = field(default_factory=list)
    expect_calls: int = 0
    extract_calls: int = 0
    has_xfail: bool = False
    has_skip: bool = False
    in_suite: list[str] = field(default_factory=list)
    declared_vars: set[str] = field(default_factory=set)
    used_vars: set[str] = field(default_factory=set)
    extracted_vars: set[str] = field(default_factory=set)
    structural: float = 0.0
    assertion_density: float = 0.0
    scenario_coverage: float = 0.0
    traceability: float = 0.0
    context_consistency: float = 0.0
    score: float = 0.0
    notes: list[str] = field(default_factory=list)


# ---------- 场景维度启发式 ----------------------------------------------------

_SCENARIO_KEYWORDS = {
    "happy":     ["verify", "成功", "可以", "can", "正常", "正常路径"],
    "sad":       ["error", "fail", "invalid", "拒绝", "401", "403", "404",
                  "异常", "失败", "wrong"],
    "boundary":  ["边界", "空", "极大", "极小", "上限", "下限", "empty",
                  "max", "min", "boundary", "edge"],
    "permission": ["permission", "权限", "未授权", "unauth", "guest",
                   "游客", "different user"],
}


# ---------- 套件注册探测 ------------------------------------------------------

def _scan_suites() -> dict[str, list[str]]:
    """name -> 出现在哪些 suite 文件里。"""
    out: dict[str, list[str]] = {}
    if not SUITES_DIR.exists():
        return out
    for suite in SUITES_DIR.glob("*.yaml"):
        try:
            import yaml  # type: ignore
            data = yaml.safe_load(suite.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        include = data.get("include") or {}
        for nm in include.get("names") or []:
            out.setdefault(str(nm), []).append(suite.name)
    return out


def _vars_yaml_keys(py_path: Path) -> set[str]:
    """从同名 .vars.yaml 提取 variables.* 的键集合。"""
    p = py_path.with_suffix(".vars.yaml")
    if not p.exists():
        return set()
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception:
        return set()
    if not isinstance(data, dict):
        return set()
    variables = data.get("variables") or {}
    if not isinstance(variables, dict):
        return set()
    return {str(k) for k in variables}


# ---------- AST 提取 ----------------------------------------------------------

_PLACEHOLDER_RX = re.compile(r"\{\{\s*([A-Za-z_]\w*)\s*\}\}")


def _is_str(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def _extract_calls(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr == "extract":
                if isinstance(f.value, ast.Name) and f.value.id == "ctx":
                    if node.args and _is_str(node.args[0]):
                        names.append(node.args[0].value)  # type: ignore[attr-defined]
    return names


def _api_call_stats(tree: ast.Module) -> tuple[int, list[str]]:
    """检测 ``ctx.api.<module>.<method>`` 调用。

    算法：沿 ``node.func`` 的 Attribute 链向上走，看是否出现过
    ``Attribute(value=Name('ctx'), attr='api')``，记录最后一个 attr
    （即最右侧的方法名）。
    """
    n = 0
    mods: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue      # 非 ctx.api.<mod>.<method> 形态不可能置起 seen_api
        chain = func
        seen_api = False
        while isinstance(chain, ast.Attribute):
            if (isinstance(chain.value, ast.Name) and chain.value.id == "ctx"
                    and chain.attr == "api"):
                seen_api = True
                break
            chain = chain.value
        if seen_api:
            n += 1
            mods.append(func.attr)
    return n, sorted(set(mods))


def _expect_count(tree: ast.Module) -> int:
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "expect":
            n += 1
    return n


def _has_xfail_skip(tree: ast.Module) -> tuple[bool, bool]:
    has_xfail = False
    has_skip = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if node.attr == "xfail":
                has_xfail = True
            if node.attr == "skip":
                has_skip = True
    return has_xfail, has_skip


def _placeholder_vars(src: str) -> set[str]:
    return set(_PLACEHOLDER_RX.findall(src))


def _module_assigns(tree: ast.Module) -> dict[str, object]:
    out: dict[str, object] = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            try:
                out[n.targets[0].id] = ast.literal_eval(n.value)
            except Exception:
                pass
    return out


def _test_func(tree: ast.Module) -> ast.FunctionDef | None:
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"):
            return n
    return None


# ---------- 评分 --------------------------------------------------------------

def _score_structural(name: str | None, priority: int | None, tags: list[str],
                       has_test: bool, ctx_ok: bool) -> float:
    score = 0.0
    if name:           score += 20
    if priority is not None: score += 20
    if tags:           score += 20
    if has_test:       score += 20
    if ctx_ok:         score += 20
    return score


def _score_assertion_density(api_calls: int, expect_calls: int) -> float:
    if api_calls == 0:
        return 0.0 if expect_calls == 0 else 60.0
    ratio = expect_calls / api_calls
    # 理想：每接口至少 1 断言，>=2.0 给满分
    return min(ratio / 2.0, 1.0) * 100


def _score_scenario(name: str | None, tags: list[str]) -> float:
    pool = ((name or "") + " " + " ".join(tags)).lower()
    hits = 0
    for dim, kws in _SCENARIO_KEYWORDS.items():
        if any(kw.lower() in pool for kw in kws):
            hits += 1
    if hits == 0:
        return 50.0
    if hits >= 2:
        return 100.0
    return 70.0


def _score_traceability(case_id: int | None, tags: list[str],
                         in_suite: list[str]) -> float:
    s = 0.0
    if case_id is not None:
        s += 40
    folder_tag = any(t.startswith("folder_") or "_flow" in t for t in tags)
    if folder_tag:
        s += 20
    if in_suite:
        s += 40
    return s


def _score_context(declared: set[str], used: set[str], extracted: set[str]) -> float:
    if not used and not extracted:
        return 100.0
    if not declared:
        return 0.0
    pool = used | extracted
    coverage = len(pool & declared) / max(1, len(pool))
    return coverage * 100


# ---------- 入口 --------------------------------------------------------------

def _analyze(path: Path, suite_index: dict[str, list[str]]) -> CompletenessReport:
    # 兼容：用户传相对路径
    abs_path = path if path.is_absolute() else (ROOT / path)
    abs_path = abs_path.resolve()
    r = CompletenessReport(
        path=str(abs_path.relative_to(ROOT)),
        name=None, case_id=None, priority=None,
    )
    try:
        src = abs_path.read_text(encoding="utf-8")
    except OSError as e:
        r.notes.append(f"读取失败: {e}")
        return r
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        r.notes.append(f"语法错误: {e.msg}")
        return r

    assigns = _module_assigns(tree)
    r.name = assigns.get("NAME") if isinstance(assigns.get("NAME"), str) else None  # type: ignore[assignment]
    r.case_id = assigns.get("CASE_ID") if isinstance(assigns.get("CASE_ID"), int) else None  # type: ignore[assignment]
    r.priority = assigns.get("PRIORITY") if isinstance(assigns.get("PRIORITY"), int) else None  # type: ignore[assignment]
    r.tags = list(assigns.get("TAGS") or []) if isinstance(assigns.get("TAGS"), (list, tuple)) else []  # type: ignore[arg-type]

    test_fn = _test_func(tree)
    has_test = test_fn is not None
    ctx_ok = bool(test_fn) and "ctx" in [a.arg for a in test_fn.args.args]  # type: ignore[union-attr]

    r.api_calls, r.api_modules = _api_call_stats(tree)
    r.expect_calls = _expect_count(tree)
    r.extract_calls = len(_extract_calls(tree))
    r.has_xfail, r.has_skip = _has_xfail_skip(tree)

    r.declared_vars = _vars_yaml_keys(abs_path)
    r.used_vars = _placeholder_vars(src)
    r.extracted_vars = set(_extract_calls(tree))

    if r.name:
        r.in_suite = suite_index.get(r.name, [])

    r.structural = _score_structural(r.name, r.priority, r.tags, has_test, ctx_ok)
    r.assertion_density = _score_assertion_density(r.api_calls, r.expect_calls)
    r.scenario_coverage = _score_scenario(r.name, r.tags)
    r.traceability = _score_traceability(r.case_id, r.tags, r.in_suite)
    r.context_consistency = _score_context(r.declared_vars, r.used_vars, r.extracted_vars)

    r.score = (
        r.structural * 0.25
        + r.assertion_density * 0.25
        + r.scenario_coverage * 0.20
        + r.traceability * 0.15
        + r.context_consistency * 0.15
    )

    if r.expect_calls == 0:
        r.notes.append("没有任何 expect(...) 断言")
    if r.api_calls == 0:
        r.notes.append("没有 ctx.api.* 调用")
    if not r.in_suite:
        r.notes.append("未被任何 suites/*.yaml 收录")
    if r.declared_vars and (r.used_vars - r.declared_vars):
        r.notes.append("占位符未在 .vars.yaml 声明: "
                       + ", ".join(sorted(r.used_vars - r.declared_vars)))
    return r


def analyze_tree(root: Path) -> list[CompletenessReport]:
    suite_index = _scan_suites()
    out: list[CompletenessReport] = []
    if root.is_file():
        candidates = [root]
    else:
        candidates = list(root.rglob("test_*.py"))
    for p in sorted(candidates):
        if p.name.startswith("__"):
            continue
        out.append(_analyze(p, suite_index))
    return out


def _set_to_list(obj):
    if isinstance(obj, set):
        return sorted(obj)
    return obj


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="用例完备性评分器")
    ap.add_argument("path", nargs="?", default=str(TESTS_DIR),
                    help=f"待扫描根目录（默认 {TESTS_DIR.relative_to(ROOT)}）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--top", type=int, default=20, help="人类可读输出时显示分数最低的 N 个")
    args = ap.parse_args(argv)

    reports = analyze_tree(Path(args.path))
    if args.json:
        payload = []
        for r in reports:
            d = asdict(r)
            # 转 set -> list，便于 JSON 序列化
            for k, v in d.items():
                if isinstance(v, set):
                    d[k] = sorted(v)
            payload.append(d)
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    avg = sum(r.score for r in reports) / max(1, len(reports))
    print(f"用例完备性报告  共 {len(reports)} 条用例  平均分 {avg:.1f}/100")
    print(f"{'分':>5}  {'结构':>5}  {'断言':>5}  {'场景':>5}  {'追溯':>5}  {'上下文':>5}  文件")
    worst = sorted(reports, key=lambda r: r.score)[: args.top]
    for r in worst:
        print(f"{r.score:5.1f}  {r.structural:5.1f}  {r.assertion_density:5.1f}  "
              f"{r.scenario_coverage:5.1f}  {r.traceability:5.1f}  {r.context_consistency:5.1f}  "
              f"{r.path}")
        for n in r.notes:
            print(f"        - {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())