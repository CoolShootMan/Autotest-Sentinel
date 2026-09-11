"""
Scaffold a new API test case as a Python script (no Apifox needed).

Usage
-----
    python new_case.py --folder "Login flow" \
                       --name "Verify login with invalid password" \
                       --tags p1,login \
                       --priority 1

This writes tests/<folder>/test_<slug>.py with:
  * module-level NAME / TAGS / PRIORITY / CASE_ID metadata (CASE_ID=None: script-authored)
  * an ApifoxClient _ctx fixture (Release env) and _url/_render helpers
  * a ready-to-fill test_<slug>() skeleton

Then run it:
    python run_suite.py <suite>.yaml
    python -m pytest tests/<folder> --tags p1,login -v
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).parent
TESTS_DIR = ROOT / "tests"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (name or "").lower()).strip("_")


#: Anti-patterns that cost a lot of debugging time during the Apifox migration.
#: Each is (human label, regex) — they run on the *generated* file.
_GUARDS = [
    ("单花括号模板：``{var}`` 不会被渲染，应为 ``{{var}}``（会发原始 body 导致 400）",
     re.compile(r"(?<!\{)\{[A-Za-z_][\w]*\}(?!\})")),
    ("字面量占位：``vars['k'] = 'k'`` 说明提取器翻译失败，应改为真实提取",
     re.compile(r"""vars\[['"]([A-Za-z_]\w*)['"]\]\s*=\s*['"](\1)['"]""")),
    ("本地定义 ``_get_path`` 会遮蔽 core.compat 的导入，务必改用 import",
     re.compile(r"^\s*def\s+_get_path\b", re.M)),
]


def audit(text: str) -> list:
    """Return [(label, line_no, snippet)] for each known anti-pattern found.

    Pure-comment lines are skipped: the template deliberately shows the WRONG
    form inside its explanatory comments, and flagging those is noise.
    """
    issues = []
    lines = text.splitlines()
    # a line is "documentation" when it is a # comment or inside a triple-quoted
    # docstring; the template intentionally documents the WRONG form there
    indoc = False
    doc_lines = set()
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("#"):
            doc_lines.add(i)
        if '"""' in s or "'''" in s:
            if s.count('"""') + s.count("'''") >= 2 and len(s) <= 3 + 6:
                pass  # one-line docstring: handled below
            indoc = not indoc
            doc_lines.add(i)
            continue
        if indoc:
            doc_lines.add(i)

    for label, rx in _GUARDS:
        for m in rx.finditer(text):
            ln = text.count("\n", 0, m.start()) + 1
            if ln in doc_lines:
                continue
            issues.append((label, ln, m.group(0)[:60]))
    return issues


TEMPLATE = '''"""Auto-generated script case: {name}"""
NAME = "{name}"
TAGS = [{tags}]
PRIORITY = {priority}
CASE_ID = None  # script-authored case, no Apifox id

import pytest
import requests
from apifox_client import ApifoxClient

PROJECT_ID = 5446866
ENV_NAME = "Release"


# NOTE: the _ctx fixture (client + base_url + vars) is provided globally by
# conftest.py. It loads variables from:
#   * env/Release.yaml                  (shared, global: base URLs, client creds, passwords)
#   * <this_file_stem>.vars.yaml        (per-case; overrides global on conflict - case-first)
# Put this case's own parameters in tests/<folder>/<slug>.vars.yaml, e.g.:
#   variables:
#     some_id: "abc123"
# and reference them in request bodies as {{{{some_id}}}}. Nothing is fetched from Apifox at runtime.
#
# CAUTION (this template goes through str.format below):
#   To emit a literal ``{{some_id}}`` into the generated file you must write
#   ``{{{{some_id}}}}`` here. Getting this wrong is what produced the famous
#   "variantId must be a UUID" bug -- single braces are NOT rendered by the
#   runtime template engine, so the request silently sent ``{{{{some_id}}}}``.


def _render(tmpl, vars):
    if not isinstance(tmpl, str):
        return tmpl
    for k, v in vars.items():
        tmpl = tmpl.replace("{{" + k + "}}", str(v))
    return tmpl


def _url(base, path, vars):
    """Path may already be absolute (scheme://host...) or resolve to a host via
    {{{{var}}}}; in both cases treat it as a full URL. Only bare relative paths
    (starting with '/') are joined onto base_url."""
    p = _render(path, vars)
    if "://" in p:
        return p
    head = p.split("/", 1)[0]
    if head and "." in head and not head.startswith("{{"):
        return "https://" + p
    return _render(base, vars) + p


def test_{slug}(_ctx):
    """{name}"""
    client = _ctx["client"]
    base_url = _ctx["base_url"]
    vars = dict(_ctx["vars"])
    # TODO: implement request(s) + assertions. Example:
    # resp = client.session().request("GET", _url(base_url, "/health", vars), headers={{}})
    # assert resp.status_code == 200
    raise NotImplementedError("fill in the request and assertions")
'''


def main():
    ap = argparse.ArgumentParser(description="Scaffold a new API test case script")
    ap.add_argument("--folder", required=True, help="Target folder under tests/ (created if missing)")
    ap.add_argument("--name", required=True, help="Human-readable case name")
    ap.add_argument("--tags", default="", help="Comma separated tags, e.g. p1,login")
    ap.add_argument("--priority", type=int, default=1, help="Priority 0/1/2 (default 1)")
    ap.add_argument("--dry-run", action="store_true", help="Print the path, do not write")
    args = ap.parse_args()

    folder = args.folder.strip().strip("/")
    s = slug(args.name)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if f"p{args.priority}" not in tags:
        tags.insert(0, f"p{args.priority}")
    tags_lit = ", ".join(f'"{t}"' for t in tags)

    target_dir = TESTS_DIR / folder
    target = target_dir / f"test_{s}.py"
    content = TEMPLATE.format(
        name=args.name, tags=tags_lit, priority=args.priority, slug=s,
    )

    print(f"Folder : {folder}")
    print(f"Name   : {args.name}")
    print(f"Tags   : {tags}")
    print(f"Target : {target}")

    # audit first so that --dry-run also surfaces any anti-pattern
    issues = audit(content)
    if issues:
        print("\n[防呆自检] 生成内容命中已知反模式：")
        for label, ln, snip in issues:
            print(f"  行 {ln}: {label}\n          {snip}")
    else:
        print("[防呆自检] 通过（无单花括号 / 无字面量占位 / 无 _get_path 遮蔽）")

    if args.dry_run:
        print("\n--- dry-run, nothing written ---")
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    if target.exists():
        print(f"ERROR: {target} already exists. Aborting to avoid overwrite.")
        return
    target.write_text(content, encoding="utf-8")
    print("\nCreated. Next: fill in the request + assertions, then run with:")
    print(f'  python -m pytest "{target}" -v')


if __name__ == "__main__":
    main()
