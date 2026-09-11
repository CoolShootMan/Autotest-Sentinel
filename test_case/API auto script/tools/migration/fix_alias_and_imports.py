"""Post-migration repair pass for two classes of rewrite defects.

The Apifox -> pytest rewriter (`rewrite_cases.py`) normalized
``_respN = client.session().request(...)`` into ``_respN = ctx.api.<domain>.<m>(...)``,
but two things fell through:

1. **Dropped response aliases.** The original scripts contained a noise-looking
   line ``_aN = _respN`` right after each request. The rewriter skipped it as an
   empty-code continuation, yet assertions / extractors further down still
   referenced ``_aN`` -- producing ``NameError: name '_a1' is not defined``
   at run time. The mapping is strictly 1:1 (``_a3 -> _resp3``), so the fix is a
   pure rename of the dangling load references.

2. **Dropped pre-script imports.** Apifox pre-scripts such as
   ``import datetime`` / ``import random`` / ``import uuid`` / ``import string``
   were not carried into the generated module, so any body that called
   ``datetime.now()`` or ``"".join(random.choices(string.digits, k=4))`` blew up.
   The fix is to re-add the missing ``import`` statements.

3. **Inconsistent ``datetime`` call style.** Hand-written patches mix
   ``from datetime import datetime`` with module-style access. The rest of the
   file uses ``datetime.timedelta`` / ``datetime.datetime.strptime``, which needs
   ``import datetime``; a bare ``datetime.now()`` then dies with
   ``AttributeError: module 'datetime' has no attribute 'now'``. Normalizing to
   ``datetime.datetime.now()`` keeps one import style across the repo.

4. **Bare ``timedelta`` / ``timezone`` names.** The dropped hand-patch import
   ``from datetime import datetime, timedelta`` left calls like
   ``_today - timedelta(days=8)`` referencing a name that no longer exists
   (``NameError: name 'timedelta' is not defined``). Since every other file uses
   module-style access, these are rewritten to ``datetime.timedelta(...)``.

Usage
-----
    python tools/migration/fix_alias_and_imports.py --check     # report only
    python tools/migration/fix_alias_and_imports.py --apply     # rewrite files

Only real AST identifier loads are renamed -- comments and string literals are
never touched. Imports are inserted just before the first module-level import.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
TESTS = ROOT / "tests"

# Modules that show up in Apifox pre-scripts and are safe to import at module top.
CANDIDATE_MODULES = [
    "datetime", "random", "uuid", "string", "time", "math",
    "hashlib", "base64", "json", "re", "os", "decimal", "itertools",
    "urllib.parse", "copy", "collections",
]

ALIAS_RE = re.compile(r"^_a(\d+)$")

# ``datetime.X`` accesses that only exist on the *class*, not the module.
# ``datetime.date`` / ``datetime.timedelta`` / ``datetime.datetime`` are valid
# module attributes and must be left alone.
BARE_DATETIME_RE = re.compile(r"(?<!\.)\bdatetime\.(now|today|utcnow|strptime|fromtimestamp)\(")

# Bare names that live on the ``datetime`` module but were imported with
# ``from datetime import ...`` in a dropped hand-patch. ``\b`` before the name
# plus the ``(?<![\w.])`` lookbehind keeps ``datetime.timedelta(`` untouched.
BARE_NAME_RE = re.compile(r"(?<![\w.])(timedelta|timezone)\s*\(")


def _module_uses(src: str, mod: str) -> bool:
    """True if `mod.` is used in live code (comment lines ignored)."""
    top = mod.split(".")[0]
    for line in src.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if re.search(rf"\b{re.escape(top)}\.", line):
            return True
    return False


def _imported_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                names.add(a.asname or a.name)
    return names


def _assigned_names(tree: ast.Module) -> set[str]:
    return {
        n.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
    }


def analyse(path: pathlib.Path) -> dict:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)

    # --- dangling _aN loads -------------------------------------------------
    assigned = _assigned_names(tree)
    resp_seen = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    dangling: dict[str, str] = {}
    offsets: list[tuple[int, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            m = ALIAS_RE.match(node.id)
            if not m or node.id in assigned:
                continue
            target = f"_resp{m.group(1)}"
            if target not in resp_seen:
                dangling[node.id] = ""  # unresolvable -- reported, not rewritten
                continue
            dangling[node.id] = target
            # col_offset is a byte offset on Python 3.8+ for utf-8 sources
            line = src.splitlines(keepends=True)[node.lineno - 1]
            col = len(line[: node.col_offset].encode("utf-8"))
            end = col + len(node.id)
            offsets.append((node.lineno - 1, col, end, target))

    # --- missing imports ----------------------------------------------------
    imported = _imported_names(tree)
    missing = []
    for mod in CANDIDATE_MODULES:
        top = mod.split(".")[0]
        if top in imported:
            continue
        if _module_uses(src, mod):
            missing.append(mod)

    # --- bare datetime.<classmethod> calls --------------------------------
    dt_hits = BARE_DATETIME_RE.findall(src)
    # --- bare timedelta( / timezone( names ---------------------------------
    bare_hits = [m for m in BARE_NAME_RE.findall(src)]
    # ignore occurrences inside comment lines
    live_lines = [
        ln for ln in src.splitlines()
        if not ln.lstrip().startswith("#")
    ]
    bare_live = [m for m in BARE_NAME_RE.findall("\n".join(live_lines))]
    dt_hits = dt_hits + bare_live

    return {
        "path": path,
        "src": src,
        "offsets": offsets,
        "dangling": dangling,
        "missing": missing,
        "dt_hits": dt_hits,
        "tree": tree,
    }


def _apply_alias_fix(src: str, offsets: list[tuple[int, int, int, str]]) -> str:
    lines = src.splitlines(keepends=True)
    # group by line, apply right-to-left so earlier offsets stay valid
    by_line: dict[int, list[tuple[int, int, str]]] = {}
    for ln, start, end, target in offsets:
        by_line.setdefault(ln, []).append((start, end, target))
    for ln, edits in by_line.items():
        raw = lines[ln].encode("utf-8")
        for start, end, target in sorted(edits, key=lambda e: -e[0]):
            raw = raw[:start] + target.encode("utf-8") + raw[end:]
        lines[ln] = raw.decode("utf-8")
    return "".join(lines)


def _insertion_line(tree: ast.Module) -> tuple[int, str]:
    """Return (0-based line index, newline style) to insert imports at."""
    first_import = None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                continue
            first_import = node
            break
    if first_import is not None:
        return first_import.lineno - 1, "\n"
    # no module-level import at all: fall back to first top-level def/assign
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign)):
            return node.lineno - 1, "\n"
    return 0, "\n"


def _apply_datetime_fix(src: str) -> str:
    """Normalize to module-style access.

    ``datetime.now()``      -> ``datetime.datetime.now()``
    bare ``timedelta(...)`` -> ``datetime.timedelta(...)``
    """
    out = BARE_DATETIME_RE.sub(lambda m: f"datetime.datetime.{m.group(1)}(", src)
    keep: list[str] = []
    for line in out.splitlines(keepends=True):
        if line.lstrip().startswith("#"):
            keep.append(line)
        else:
            keep.append(BARE_NAME_RE.sub(lambda m: f"datetime.{m.group(1)}(", line))
    return "".join(keep)


def _apply_import_fix(src: str, tree: ast.Module, modules: list[str]) -> str:
    if not modules:
        return src
    lines = src.splitlines(keepends=True)
    idx, _ = _insertion_line(tree)
    block = "".join(f"import {m}\n" for m in modules)
    lines.insert(idx, block)
    return "".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="report only, change nothing")
    g.add_argument("--apply", action="store_true", help="rewrite files in place")
    args = ap.parse_args()

    files = sorted(TESTS.rglob("test_*.py"))
    alias_files = 0
    alias_refs = 0
    import_files = 0
    import_mods = 0
    dt_files = 0
    dt_hits = 0
    unresolved: list[str] = []

    for path in files:
        try:
            info = analyse(path)
        except SyntaxError as exc:  # pragma: no cover
            print(f"  ! syntax error, skipped: {path} ({exc})")
            continue

        rel = path.relative_to(ROOT)
        if info["offsets"]:
            alias_files += 1
            alias_refs += len(info["offsets"])
            pairs = ", ".join(sorted({f"{a}->{b}" for a, b in info["dangling"].items() if b}))
            print(f"  alias  {rel}\n         {pairs}")
        if any(v == "" for v in info["dangling"].values()):
            unresolved.append(str(rel))
        if info["missing"]:
            import_files += 1
            import_mods += len(info["missing"])
            print(f"  import {rel}\n         + {', '.join(info['missing'])}")

        if info["dt_hits"]:
            dt_files += 1
            dt_hits += len(info["dt_hits"])
            print(f"  datetime {rel}\n         {', '.join(sorted(set(info['dt_hits'])))}")

        if args.apply and (info["offsets"] or info["missing"] or info["dt_hits"]):
            new = info["src"]
            # order matters: alias offsets were measured on the original source,
            # so rename aliases BEFORE any call that changes line lengths.
            if info["offsets"]:
                new = _apply_alias_fix(new, info["offsets"])
            if info["dt_hits"]:
                new = _apply_datetime_fix(new)
                new = _apply_alias_fix(new, info["offsets"])
            if info["missing"]:
                # re-parse: offsets shifted after the alias rename is fine,
                # but the import insertion point must come from current source
                new = _apply_import_fix(new, ast.parse(new), info["missing"])
            path.write_text(new, encoding="utf-8")

    verb = "rewrote" if args.apply else "would rewrite"
    print(
        f"\n{verb} {alias_refs} dangling alias ref(s) across {alias_files} file(s); "
        f"{import_mods} import(s) across {import_files} file(s); "
        f"{dt_hits} datetime call(s) across {dt_files} file(s)"
    )
    if unresolved:
        print(f"! {len(unresolved)} file(s) had aliases with no matching _respN (left untouched):")
        for u in unresolved:
            print(f"    {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
