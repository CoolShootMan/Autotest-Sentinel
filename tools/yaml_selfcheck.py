#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yaml_selfcheck.py — UI YAML 用例静态自检（三件套 + 递归嵌套）

用法:
    ./venv/bin/python tools/yaml_selfcheck.py <yaml> [<yaml> ...]
    ./venv/bin/python tools/yaml_selfcheck.py "test_case/UI/All_YAML/Events/Event_settings/*.yaml"

自检项（镜像 test_ui.py 的真实分发逻辑）:
  1. 严格 YAML 解析 —— 自写 Strict loader，重复键直接报错（PyYAML 默认静默覆盖，是 bug 源头）。
  2. 顶层必备三键 —— description / test_step / expect_result（runner 强制要求，缺则 KeyError）。
  3. 步骤键可解析 —— 逐键走 get_action()，并先按 test_ui.py 的
     `session_<name>__<action>` 规则剥离 session 前缀；解析不到 = 运行必报 "Step not found"。
  4. 递归嵌套 —— `if_*` 块的 then/else 子步骤、pre_condition.test_step、teardown_step
     （注意 base.py:375 的 if 块子步骤 **不剥离 session 前缀**，本工具同规则）。
  5. 去 JS 化度量 —— 统计 execute_js / run_workflow_script 数量（>0 需人工确认是否属允许场景）。

退出码: 0 = 全绿；1 = 有 ERROR。
"""
import os
import re
import sys
import glob
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(ROOT, "test_case", "UI")


# ---------------------------------------------------------------- Strict YAML
class _StrictLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader, node, deep=False):
    keys = set()
    for k_node, _ in node.value:
        k = loader.construct_object(k_node, deep=deep)
        if isinstance(k, (str, int, float, bool)) and k in keys:
            raise yaml.constructor.ConstructorError(
                None, None, f"found duplicate key: {k!r}", node.start_mark)
        keys.add(k)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


_StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_strict(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=_StrictLoader)


# ---------------------------------------------------------------- get_action
def _load_get_action():
    """Import the REAL get_action used at runtime (test_case.UI.actions.get_action)."""
    for p in (UI_DIR, ROOT):
        if p not in sys.path:
            sys.path.insert(0, p)
    from test_case.UI.actions import get_action  # noqa: E402
    return get_action


def strip_session(key):
    """Mirror test_ui.py:116-129. Returns (session_or_None, action_name)."""
    if key.startswith("session_") and "__" in key:
        parts = key[len("session_"):].split("__", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
    return None, key


NESTED_KEYS = ("then", "else", "steps")


def walk_steps(steps, get_action, path, out, ctx="main"):
    """Recursively collect unresolved step keys."""
    if not isinstance(steps, dict):
        return
    for k, v in steps.items():
        if not isinstance(k, str):
            continue
        # inside an if-block (ctx == "after_if") the session prefix is NOT stripped
        if ctx == "main":
            _sess, action_name = strip_session(k)
        else:
            action_name = k
        if get_action(action_name) is None:
            out.append((path + [k], k, action_name))
        if isinstance(v, dict):
            for nk in NESTED_KEYS:
                if nk in v:
                    walk_steps(v[nk], get_action, path + [k, nk], out, ctx="after_if")


def count_js(steps, path, out):
    if not isinstance(steps, dict):
        return
    for k, v in steps.items():
        if not isinstance(k, str):
            continue
        _sess, action_name = strip_session(k)
        if action_name.startswith("execute_js") or action_name.startswith("run_workflow_script"):
            out.append(path + [k])
        if isinstance(v, dict):
            for nk in NESTED_KEYS:
                if nk in v:
                    count_js(v[nk], path + [k, nk], out)


# ------------------------------------------------- 变量覆盖检查 (refs ⊆ saved)
VAR_RE = re.compile(r"\{\{([^{}]+)\}\}")
SAVE_ACTIONS = ("extract_value", "extract_row_value", "compute_value", "set_value",
                "select_event_with_sellable_product", "execute_js", "run_workflow_script")


def _iter_nodes(node):
    """Yield every dict node in `node` (recursively)."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _iter_nodes(v)
    elif isinstance(node, list):
        for v in node:
            yield from _iter_nodes(v)


def _iter_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _iter_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _iter_strings(v)


def collect_vars(case):
    """Return (saved, declared_external, refs, published_globals) for a case dict.

    saved            = every `save_as` written by a save-capable action
    declared_external= vars listed in `verify_defined*.vars` (explicit cross-case dependency)
    refs             = every {{name}} consumed anywhere in the case (locator `{{@..}}` excluded)
    published_globals= subset of `saved` carrying `global: true` (published for other cases —
                       "never referenced in this file" is NORMAL for them, not dead code)
    """
    saved, declared, refs, published = set(), set(), set(), set()
    for node in _iter_nodes(case):
        sa = node.get("save_as")
        if isinstance(sa, str) and sa:
            saved.add(sa)
            if node.get("global") is True:
                published.add(sa)
        vars_ = node.get("vars")
        if isinstance(vars_, list):
            declared.update(str(x) for x in vars_)
    for s in _iter_strings(case):
        for m in VAR_RE.finditer(s):
            name = m.group(1).strip()
            if name.startswith("@"):        # locators.py placeholder namespace
                continue
            refs.add(name)
    return saved, declared, refs, published


# ---------------------------------------------------------------- main
def check_file(path, get_action, verbose=False):
    errors, warns, notes = [], [], []
    try:
        data = load_strict(path)
    except Exception as e:
        return [f"YAML 解析失败: {e}"], [], []

    if not isinstance(data, dict):
        return [f"顶层必须是 mapping，实际是 {type(data).__name__}"], [], []

    for case_name, case in data.items():
        if not isinstance(case, dict) or "test_step" not in case:
            warns.append(f"{case_name}: 没有 test_step（不是用例？跳过）")
            continue

        # --- 顶层三键 ---
        for req in ("description", "test_step", "expect_result"):
            if req not in case:
                errors.append(f"{case_name}: 缺顶层必备键 '{req}'")

        # --- 步骤解析 ---
        unresolved = []
        walk_steps(case["test_step"], get_action, [], unresolved, ctx="main")
        for p, key, act in unresolved:
            errors.append(f"{case_name}: 步骤键无法解析 -> {' / '.join(p)}  (解析名 '{act}') -> get_action=None")

        # --- pre_condition / teardown ---
        pre = case.get("pre_condition") or {}
        if isinstance(pre, dict) and isinstance(pre.get("test_step"), dict):
            bad = []
            walk_steps(pre["test_step"], get_action, ["pre_condition"], bad, ctx="main")
            for p, key, act in bad:
                errors.append(f"{case_name}: pre_condition 步骤键无法解析 -> {' / '.join(p)} -> '{act}'")

        te = case.get("teardown_step") or {}
        if isinstance(te, dict):
            bad = []
            walk_steps(te, get_action, ["teardown_step"], bad, ctx="main")
            for p, key, act in bad:
                errors.append(f"{case_name}: teardown_step 键无法解析 -> {' / '.join(p)} -> '{act}'")

        # --- 变量覆盖检查 (refs ⊆ saved ∪ declared_external) ---
        saved, declared, refs, published = collect_vars(case)
        missing = sorted(refs - saved - declared)
        if missing:
            errors.append(f"{case_name}: 引用了未定义变量 -> {missing}"
                          f"（本文件既无 save_as，也未用 verify_defined 声明；"
                          f"单独跑必挂 Undefined/字面量 {{var}}）")
        unused = sorted(saved - refs - published)
        if unused:
            notes.append(f"{case_name}: save_as 但从未被引用 -> {unused}（可清理）")
        if published:
            notes.append(f"{case_name}: 发布跨用例全局 -> {sorted(published)}")

        # --- 统计 ---
        js = []
        count_js(case["test_step"], [], js)
        n_steps = len(case["test_step"])
        notes.append(f"{case_name}: {n_steps} 步, execute_js={len(js)}"
                     + (f" -> {' / '.join(x[-1] for x in js)}" if js else ""))
        if js:
            warns.append(f"{case_name}: 含 {len(js)} 处 execute_js/run_workflow_script，"
                         f"需确认是否属『框架无原生能力』的允许场景")
        if case.get("title") is None:
            pass

    return errors, warns, notes


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    paths = []
    for a in argv:
        paths.extend(sorted(glob.glob(a)) or [a])

    get_action = _load_get_action()

    all_err, all_warn, all_note = [], [], []
    for p in paths:
        e, w, n = check_file(p, get_action)
        rel = os.path.relpath(p, ROOT)
        print(f"\n=== {rel} ===")
        for x in e:
            print(f"  [ERROR] {x}")
        for x in w:
            print(f"  [WARN ] {x}")
        for x in n:
            print(f"  [ OK  ] {x}")
        all_err += e
        all_warn += w
        all_note += n

    print(f"\n---- 汇总: {len(paths)} 文件 / {len(all_note)} 用例 / "
          f"{len(all_err)} ERROR / {len(all_warn)} WARN ----")
    return 1 if all_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
