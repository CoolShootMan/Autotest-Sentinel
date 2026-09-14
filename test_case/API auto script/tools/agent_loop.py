"""Agent-loop 编排器（harness 的"发动机"）。

本脚本是 autotest-expert agent 的**外部化 checklist**：agent 每完成一步
后调用本脚本，把状态固化下来——CI / 本地可以机械化追溯 agent 是否真的
走完了 7 步。

7 步闭环（参考 autotest-expert.md §零）
----------------------------------------
1. REQUIRE   —— 解析需求（参数、目标接口、断言方向）
2. DISCOVER  —— 在 tests/ + api/ 中检索相似用例与可用方法
3. SCAFFOLD  —— 调用 new_case.py 生成骨架
4. FILL      —— agent 把真实 body / 断言填入
5. AUDIT     —— 调用 core.case_audit 做静态审查
6. SCORE     —— 调用 tools/case_completeness.py 跑完备性评分
7. VERIFY    —— pytest --collect-only，确认可被 pytest 收集

调用方式
--------
CLI（CI 用）::

    python tools/agent_loop.py scaffold --folder "Login flow" --name "Verify X"
    python tools/agent_loop.py audit     path/to/test_x.py
    python tools/agent_loop.py score     path/to/test_x.py
    python tools/agent_loop.py verify    path/to/test_x.py
    python tools/agent_loop.py full      path/to/test_x.py  # 4 → 5 → 6 → 7 一条龙

每条命令会输出 ``LOOP_STEP=<name> STATUS=<ok|fail> ...``，方便
CI 解析。退出码：0=全绿，1=发现 error 级问题。
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import case_audit  # noqa: E402

PYTHON = sys.executable


# ---------------------------------------------------------------------------
# 步骤 1 — REQUIRE
# ---------------------------------------------------------------------------

REQUIRE_QUESTIONS = [
    "目标模块（api.<x>）是什么？",
    "走的是 happy / sad / boundary / permission 哪条？",
    "下游哪些用例依赖本条产出（要 extract 哪些变量）？",
    "期望返回 code 是 200/401/403/... 哪一个？",
    "本用例是否需要进入某个 suite？",
]


def cmd_require(_args: argparse.Namespace) -> int:
    print("LOOP_STEP=REQUIRE STATUS=prompt")
    for i, q in enumerate(REQUIRE_QUESTIONS, 1):
        print(f"  Q{i}. {q}")
    print("\n(把以上 5 个问题的答案交给 agent；agent 应把它们写进骨架注释。)")
    return 0


# ---------------------------------------------------------------------------
# 步骤 2 — DISCOVER
# ---------------------------------------------------------------------------

def _list_methods(module: str) -> list[str]:
    p = ROOT / "api" / f"{module}.py"
    if not p.exists():
        return []
    src = p.read_text(encoding="utf-8")
    return re.findall(r"def\s+(\w+)\s*\(", src)


def cmd_discover(args: argparse.Namespace) -> int:
    print(f"LOOP_STEP=DISCOVER STATUS=ok module={args.module}")
    methods = _list_methods(args.module)
    if not methods:
        print(f"  ! api/{args.module}.py 不存在或无方法定义")
        return 1
    print(f"  api/{args.module}.py 中可用方法: {methods}")

    # 找相似用例
    matches = []
    rx_method = re.compile(rf"ctx\.api\.{re.escape(args.module)}\.(\w+)")
    for p in (ROOT / "tests").rglob("test_*.py"):
        try:
            src = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in rx_method.finditer(src):
            matches.append((m.group(1), str(p.relative_to(ROOT))))
    if matches:
        print(f"  相似历史用例 ({len(matches)} 处):")
        for method, path in matches[:10]:
            print(f"    - {method}  {path}")
    else:
        print("  无历史用例，骨架将以 happy_path 为默认。")
    return 0


# ---------------------------------------------------------------------------
# 步骤 3 — SCAFFOLD  (wrapper)
# ---------------------------------------------------------------------------

def cmd_scaffold(args: argparse.Namespace) -> int:
    cmd = [
        PYTHON, str(ROOT / "new_case.py"),
        "--folder", args.folder,
        "--name", args.name,
        "--tags", args.tags or "",
        "--priority", str(args.priority),
        "--profile", args.profile,
        "--module", args.module,
        "--method", args.method,
    ]
    if args.dry_run:
        cmd.append("--dry-run")
    print(f"LOOP_STEP=SCAFFOLD STATUS=running cmd={' '.join(cmd)}")
    return subprocess.call(cmd)


# ---------------------------------------------------------------------------
# 步骤 4 — FILL  (noop; agent has to do this in its own context)
# ---------------------------------------------------------------------------

def cmd_fill(args: argparse.Namespace) -> int:
    p = Path(args.path)
    if not p.exists():
        print(f"LOOP_STEP=FILL STATUS=fail reason=missing {p}", file=sys.stderr)
        return 1
    print("LOOP_STEP=FILL STATUS=ok")
    print("  agent 请在此文件中:")
    print("  - 替换 TODO 处的请求体；")
    print("  - 调整 expect 断言的实际值；")
    print("  - 必要时 ctx.extract('var', resp, '$.path')。")
    return 0


# ---------------------------------------------------------------------------
# 步骤 5 — AUDIT
# ---------------------------------------------------------------------------

def cmd_audit(args: argparse.Namespace) -> int:
    p = Path(args.path)
    fs = case_audit.audit_file(p)
    err = sum(1 for f in fs if f.severity == "error")
    warn = sum(1 for f in fs if f.severity == "warning")
    info = sum(1 for f in fs if f.severity == "info")
    print(f"LOOP_STEP=AUDIT STATUS={'fail' if err else 'ok'} "
          f"error={err} warning={warn} info={info} file={p}")
    for f in fs:
        tag = {"error": "ERROR", "warning": "WARN ", "info": "INFO "}[f.severity]
        print(f"  [{tag}] line {f.line:<4} {f.rule_id}: {f.message}")
        if f.snippet:
            print(f"          | {f.snippet}")
        if f.fix_hint and (args.strict or f.severity != "info"):
            print(f"          -> {f.fix_hint}")
    return 1 if err else 0


# ---------------------------------------------------------------------------
# 步骤 6 — SCORE
# ---------------------------------------------------------------------------

def cmd_score(args: argparse.Namespace) -> int:
    p = Path(args.path)
    if not p.exists():
        print(f"LOOP_STEP=SCORE STATUS=fail reason=missing {p}", file=sys.stderr)
        return 1
    out = subprocess.run(
        [PYTHON, str(ROOT / "tools" / "case_completeness.py"),
         str(p), "--json"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        print(out.stdout)
        print(out.stderr, file=sys.stderr)
        return out.returncode
    try:
        reports = json.loads(out.stdout)
    except json.JSONDecodeError as e:
        print(f"LOOP_STEP=SCORE STATUS=fail reason=json {e}", file=sys.stderr)
        return 1
    for r in reports:
        ok = r["score"] >= args.threshold
        status = "ok" if ok else "fail"
        print(f"LOOP_STEP=SCORE STATUS={status} file={r['path']} "
              f"score={r['score']:.1f} threshold={args.threshold}")
        print(f"  structural={r['structural']:.1f}  "
              f"assertion_density={r['assertion_density']:.1f}  "
              f"scenario_coverage={r['scenario_coverage']:.1f}  "
              f"traceability={r['traceability']:.1f}  "
              f"context_consistency={r['context_consistency']:.1f}")
        for n in r["notes"]:
            print(f"    - {n}")
    return 0 if all(r["score"] >= args.threshold for r in reports) else 1


# ---------------------------------------------------------------------------
# 步骤 7 — VERIFY  (pytest --collect-only)
# ---------------------------------------------------------------------------

def cmd_verify(args: argparse.Namespace) -> int:
    p = Path(args.path)
    if not p.exists():
        print(f"LOOP_STEP=VERIFY STATUS=fail reason=missing {p}", file=sys.stderr)
        return 1
    out = subprocess.run(
        [PYTHON, "-m", "pytest", str(p), "--collect-only", "-q",
         "--no-header"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    status = "ok" if out.returncode == 0 else "fail"
    print(f"LOOP_STEP=VERIFY STATUS={status} file={p}")
    print(out.stdout)
    if out.returncode != 0:
        print(out.stderr, file=sys.stderr)
    return out.returncode


# ---------------------------------------------------------------------------
# FULL  (一条龙)
# ---------------------------------------------------------------------------

def cmd_full(args: argparse.Namespace) -> int:
    steps = [
        ("audit",  lambda: cmd_audit(argparse.Namespace(path=args.path, strict=False))),
        ("score",  lambda: cmd_score(argparse.Namespace(path=args.path, threshold=80.0))),
        ("verify", lambda: cmd_verify(argparse.Namespace(path=args.path))),
    ]
    failed = []
    for name, fn in steps:
        rc = fn()
        if rc != 0:
            failed.append(name)
            if not args.keep_going:
                return rc
    if failed:
        print(f"LOOP_STEP=FULL STATUS=fail failed={failed}", file=sys.stderr)
        return 1
    print("LOOP_STEP=FULL STATUS=ok")
    return 0


# ---------------------------------------------------------------------------
# entry
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Agent-loop 编排器")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_req = sub.add_parser("require", help="步骤 1：打印 REQUIRE 提问清单")
    p_req.set_defaults(func=cmd_require)

    p_dis = sub.add_parser("discover", help="步骤 2：检索可用方法与相似用例")
    p_dis.add_argument("--module", required=True)
    p_dis.set_defaults(func=cmd_discover)

    p_sc = sub.add_parser("scaffold", help="步骤 3：调用 new_case.py 生成骨架")
    p_sc.add_argument("--folder", required=True)
    p_sc.add_argument("--name", required=True)
    p_sc.add_argument("--tags", default="")
    p_sc.add_argument("--priority", type=int, default=1)
    p_sc.add_argument("--profile", default="happy_path",
                      choices=list(["happy_path", "sad_path", "boundary",
                                    "auth_required", "extract_only"]))
    p_sc.add_argument("--module", default="auth")
    p_sc.add_argument("--method", default="sign_in")
    p_sc.add_argument("--dry-run", action="store_true")
    p_sc.set_defaults(func=cmd_scaffold)

    p_fill = sub.add_parser("fill", help="步骤 4：提示 agent 编辑文件")
    p_fill.add_argument("--path", required=True)
    p_fill.set_defaults(func=cmd_fill)

    p_au = sub.add_parser("audit", help="步骤 5：审计")
    p_au.add_argument("--path", required=True)
    p_au.add_argument("--strict", action="store_true")
    p_au.set_defaults(func=cmd_audit)

    p_sc2 = sub.add_parser("score", help="步骤 6：完备性评分")
    p_sc2.add_argument("--path", required=True)
    p_sc2.add_argument("--threshold", type=float, default=80.0)
    p_sc2.set_defaults(func=cmd_score)

    p_v = sub.add_parser("verify", help="步骤 7：pytest --collect-only")
    p_v.add_argument("--path", required=True)
    p_v.set_defaults(func=cmd_verify)

    p_full = sub.add_parser("full", help="一次跑 audit+score+verify")
    p_full.add_argument("--path", required=True)
    p_full.add_argument("--keep-going", action="store_true",
                        help="失败也继续（用于诊断）")
    p_full.set_defaults(func=cmd_full)

    args = ap.parse_args()
    return args.func(args)


import re  # noqa: E402  (used in cmd_discover)


if __name__ == "__main__":
    sys.exit(main())