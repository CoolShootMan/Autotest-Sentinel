"""Scaffold a new API test case (no Apifox needed).

This script is the **primary entrypoint** of the autotest-expert agent's
harness for *generating* a new case. It does three jobs:

1. **Profile-driven scaffolding** —— choose a profile (happy_path / sad_path /
   boundary / auth_required / extract_only) and emit the right skeleton.
2. **Auto-audit** —— invoke ``core.case_audit`` on the generated file. Fail
   the scaffold if any ``error``-level finding is raised (anti-patterns).
3. **Completeness hook** —— print a CompletenessReport-style preview so the
   agent knows what gaps remain to fill.

Backwards compatibility
-----------------------
* Old CLI (``--folder --name --tags --priority --dry-run``) still works.
* New flags: ``--profile``, ``--module`` (default auth), ``--method``,
  ``--vars-json``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from core import case_audit  # noqa: E402

TESTS_DIR = ROOT / "tests"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")


# ---------------------------------------------------------------------------
# Profile-based templates
# ---------------------------------------------------------------------------

PROFILES = {
    "happy_path": {
        "description": "正常路径：合法入参 → 期望成功 + 提取关键变量",
        "imports": "from core.assertions import expect",
        "body": '''    # ---- TODO: fill in legal inputs ----
    resp = ctx.api.{module}.{method}(
        body={{"key": "value"}},
    )
    expect(resp).json('$.code').equals('200')
    expect(resp).json('$.message').equals('success')
    # TODO: extract the variable that downstream cases depend on
    # ctx.extract('my_var', resp, '$.data.id')
''',
    },
    "sad_path": {
        "description": "异常路径：非法入参 → 期望 4xx + 错误消息",
        "imports": "import pytest\nfrom core.assertions import expect",
        "body": '''    resp = ctx.api.{module}.{method}(
        body={{"key": "INVALID"}},
    )
    expect(resp).json('$.code').equals('400')
    expect(resp).json('$.message').contains('invalid')
''',
    },
    "boundary": {
        "description": "边界：空值 / 极值 / 重复提交",
        "imports": "import pytest\nfrom core.assertions import expect",
        "body": '''    resp = ctx.api.{module}.{method}(
        body={{"key": ""}},        # empty boundary
    )
    # boundary assertions go here
    expect(resp).status().is_less_than(500)
''',
    },
    "auth_required": {
        "description": "权限：未登录 / 错误角色 → 401 / 403",
        "imports": "import pytest\nfrom core.assertions import expect",
        "body": '''    # guest call without token
    resp = ctx.api.{module}.{method}(
        body={{"key": "value"}},
    )
    expect(resp).json('$.code').equals('401')
''',
    },
    "extract_only": {
        "description": "数据准备：登录 / 拉取下游依赖的变量",
        "imports": "from core.assertions import expect",
        "body": '''    resp = ctx.api.{module}.{method}(
        body={{"email": "{{login_email}}", "password": "{{password}}"}},
        app_headers=True,
    )
    expect(resp).json('$.code').equals('200')
    ctx.extract('token', resp, '$.data.token')
''',
    },
}


HEADER = '''"""Auto-generated script case: {name}"""
NAME = "{name}"
TAGS = [{tags}]
PRIORITY = {priority}
CASE_ID = None  # script-authored case, no Apifox id

{imports}

ENV_NAME = "Release"

'''

VARS_YAML_TEMPLATE = '''# Per-case parameters for {stem}
# Inherits env/Release.yaml (case-first merge).
variables:
{vars_block}
'''


def _render(template: str, **kw) -> str:
    return template.format(**kw)


def _build(name: str, slug_value: str, tags_lit: str, priority: int,
           profile: str, module: str, method: str,
           vars_json: str | None) -> str:
    cfg = PROFILES[profile]
    imports = cfg["imports"]
    body = cfg["body"].format(module=module, method=method)
    head = _render(HEADER,
                   name=name, tags=tags_lit, priority=priority, imports=imports)
    test_fn = (
        f"def test_{slug_value}(ctx):\n"
        f"    \"\"\"{name}\"\"\"\n"
        f"    vars = ctx  # 历史写法 vars['x'] 继续可用\n"
        f"{body}"
    )
    return head + test_fn


def _make_vars_yaml(target: Path, vars_json: str | None) -> str | None:
    if not vars_json:
        return None
    try:
        d = json.loads(vars_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: --vars-json 不是合法 JSON: {e}", file=sys.stderr)
        return None
    if not isinstance(d, dict):
        print("ERROR: --vars-json 必须是 object {key: value}", file=sys.stderr)
        return None
    block = "\n".join(f"  {k}: {v!r}" for k, v in d.items())
    return VARS_YAML_TEMPLATE.format(stem=target.stem, vars_block=block)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a new API test case script")
    ap.add_argument("--folder", required=True, help="Target folder under tests/")
    ap.add_argument("--name", required=True, help="Human-readable case name")
    ap.add_argument("--tags", default="", help="Comma-separated tags, e.g. p1,login")
    ap.add_argument("--priority", type=int, default=1, help="0=p0, 1=p1 ...")
    ap.add_argument("--profile", choices=list(PROFILES),
                    default="happy_path", help="用例骨架 profile")
    ap.add_argument("--module", default="auth", help="ctx.api.<module>.*")
    ap.add_argument("--method", default="sign_in", help="ctx.api.<module>.<method>")
    ap.add_argument("--vars-json", default=None,
                    help="JSON 字符串，生成同名 .vars.yaml")
    ap.add_argument("--dry-run", action="store_true", help="只打印，不写文件")
    ap.add_argument("--no-audit", action="store_true",
                    help="跳过 audit（仅在调试 scaffold 自身时使用）")
    args = ap.parse_args()

    folder = args.folder.strip().strip("/")
    s = slug(args.name)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if f"p{args.priority}" not in tags:
        tags.insert(0, f"p{args.priority}")
    tags_lit = ", ".join(f'"{t}"' for t in tags)

    target_dir = TESTS_DIR / folder
    target = target_dir / f"test_{s}.py"
    content = _build(args.name, s, tags_lit, args.priority,
                     args.profile, args.module, args.method, args.vars_json)

    print(f"Profile : {args.profile} — {PROFILES[args.profile]['description']}")
    print(f"Folder  : {folder}")
    print(f"Name    : {args.name}")
    print(f"Tags    : {tags}")
    print(f"Target  : {target}")

    # ---- audit ----
    findings: list[case_audit.Finding] = []
    if not args.no_audit:
        # 跑一次内存审计
        import ast
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"\n[ERROR] 生成的骨架存在语法错误：{e}", file=sys.stderr)
            return 2
        for rule in case_audit.RULES:
            findings.extend(rule(target, tree, content))
        errs = [f for f in findings if f.severity == "error"]
        warns = [f for f in findings if f.severity == "warning"]
        print(f"\n[audit]  {len(errs)} error, {len(warns)} warning")
        for f in errs + warns:
            tag = "[ERROR]" if f.severity == "error" else "[WARN] "
            print(f"  {tag} line {f.line:<4} {f.rule_id}: {f.message}")
            if f.fix_hint:
                print(f"           -> {f.fix_hint}")
        if errs:
            print("\n[FAIL] 骨架命中 error 级反模式，请修正模板或加 --no-audit 后排查。",
                  file=sys.stderr)
            if not args.dry_run:
                return 1

    if args.dry_run:
        print("\n--- dry-run, nothing written ---")
        print("\n--- 内容预览 ---")
        print(content)
        return 0

    target_dir.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(f"ERROR: {target} already exists. Aborting to avoid overwrite.",
              file=sys.stderr)
        return 1
    target.write_text(content, encoding="utf-8")
    print(f"\nCreated {target}")

    vars_yaml = _make_vars_yaml(target, args.vars_json)
    if vars_yaml is not None:
        vp = target.with_suffix(".vars.yaml")
        if vp.exists():
            print(f"WARN: {vp} 已存在，跳过 vars.yaml 写入。")
        else:
            vp.write_text(vars_yaml, encoding="utf-8")
            print(f"Created {vp}")

    print("\nNext steps:")
    print("  1) 在 TODO 处填入真实请求体与断言；")
    print("  2) python tools/case_completeness.py", target)
    print("  3) python -m pytest", str(target), "-v")
    return 0


if __name__ == "__main__":
    sys.exit(main())