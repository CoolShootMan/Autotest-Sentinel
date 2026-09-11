"""
Per-case environment-variable loader.

Replaces the live ``ApifoxClient.get_environments()`` call. Each case's ``_ctx``
fixture now gets its ``vars``/``base_url`` from local YAML instead of Apifox, so
the suite no longer depends on a live Apifox session to resolve parameters.

Layering (Apifox-like precedence, case-first):
  1. Apifox global variables  ->  env/Global.yaml
  2. Environment variables    ->  env/<ENV_NAME>.yaml     (overrides global)
  3. Per-case override        ->  <case_file_stem>.vars.yaml (overrides env/global)

When a key exists in multiple layers, the **topmost layer wins**:
per-case > env > global. This matches Apifox behavior and the user's
requirement "重复不覆盖" (shared values stay shared; case-specific values stay
isolated in their own file).

"不要覆盖" guarantee:
  Each case owns its own ``<slug>.vars.yaml`` file, so one case's parameters can
  NEVER overwrite another case's config. ``check()`` prints any per-case key that
  overrides a global/env key, so duplicate intent stays visible/reviewable.

Usage (inside the shared ``_ctx`` fixture in conftest.py):
    data = load_case_vars(request.path, ENV_NAME)
    # -> {"base_url": str, "vars": dict, "case_vars_file": str}
"""
from __future__ import annotations

import yaml
from pathlib import Path

ROOT = Path(__file__).parent
ENV_DIR = ROOT / "env"
# Runtime tokens produced by precondition cases (e.g. t0000) and shared with all
# later cases. Created on demand; absent until a precondition runs.
RUNTIME_TOKENS_FILE = ENV_DIR / "_runtime_tokens.yaml"


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_runtime_tokens() -> dict:
    """Return runtime tokens written by precondition cases (empty if none)."""
    return dict((_load_yaml(RUNTIME_TOKENS_FILE).get("variables") or {}))


def save_runtime_tokens(tokens: dict) -> None:
    """Merge ``tokens`` into the shared runtime-tokens file.

    Used by precondition cases (e.g. t0000) so that freshly obtained login
    tokens become available to every later case via ``load_case_vars``.
    """
    data = _load_yaml(RUNTIME_TOKENS_FILE)
    if not isinstance(data, dict):
        data = {}
    variables = dict(data.get("variables") or {})
    variables.update({k: v for k, v in tokens.items() if v is not None})
    data["variables"] = variables
    RUNTIME_TOKENS_FILE.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def load_case_vars(case_file, env_name: str = "Release") -> dict:
    """Load merged variables for a single test case.

    Merge precedence: per-case > env > global.

    Args:
        case_file: path to the test_*.py file (str or Path).
        env_name:  name of the env file under env/ (default "Release").

    Returns:
        {"base_url": str, "vars": dict, "case_vars_file": str (or "")}
    """
    case_file = Path(case_file)

    # 1) Apifox global variables
    g = _load_yaml(ENV_DIR / "Global.yaml")
    base_url = g.get("base_url", "")
    merged = dict(g.get("variables") or {})

    # 2) Environment variables (Release / Staging / etc.)
    e = _load_yaml(ENV_DIR / f"{env_name}.yaml")
    if isinstance(e, dict):
        if e.get("base_url"):
            base_url = e["base_url"]
        for k, v in (e.get("variables") or {}).items():
            merged[k] = v  # env overrides global

    # 2.5) Runtime tokens produced by precondition cases (e.g. t0000).
    # Freshly-obtained tokens override static placeholders, but a case's own
    # per-case override (step 3) still wins.
    for k, v in load_runtime_tokens().items():
        merged[k] = v

    # 3) per-case override (highest precedence)
    pc_file = case_file.with_name(case_file.stem + ".vars.yaml")
    pc = _load_yaml(pc_file)
    if isinstance(pc, dict):
        if pc.get("base_url"):
            base_url = pc["base_url"]
        for k, v in (pc.get("variables") or {}).items():
            merged[k] = v  # case overrides env/global

    return {
        "base_url": base_url,
        "vars": merged,
        "case_vars_file": str(pc_file) if pc_file.exists() else "",
    }


def check(env_name: str = "Release", tests_dir: str = "tests") -> list[str]:
    """Report override keys across the three layers (duplicate visibility).

    Returns a list of human-readable warning strings.
    """
    g = _load_yaml(ENV_DIR / "Global.yaml")
    gvars = set((g.get("variables") or {}).keys())
    e = _load_yaml(ENV_DIR / f"{env_name}.yaml")
    evars = set((e.get("variables") or {}).keys())

    warnings: list[str] = []

    # env overrides global
    env_over_global = sorted(evars & gvars)
    if env_over_global:
        warnings.append(f"env/{env_name}.yaml overrides env/Global.yaml keys: {', '.join(env_over_global)}")

    # per-case overrides global/env
    for pc in sorted(Path(tests_dir).rglob("*.vars.yaml")):
        pcv = _load_yaml(pc)
        if not isinstance(pcv, dict):
            continue
        pc_keys = set((pcv.get("variables") or {}).keys())
        dup = sorted(pc_keys & (gvars | evars))
        if dup:
            rel = pc.relative_to(Path(tests_dir).parent)
            warnings.append(f"{rel}: overrides global/env keys -> {', '.join(dup)}")

    if not warnings:
        warnings.append("OK: no env or per-case file overrides a global key.")
    return warnings


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "check":
        for line in check():
            print(line)
    else:
        # debug: print merged vars for a given case file
        print(load_case_vars(Path(mode)))
