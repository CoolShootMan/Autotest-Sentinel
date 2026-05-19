#!/usr/bin/env python3
"""
locator_updater.py — YAML 测试用例定位器批量更新工具

功能：
  元素定位器发生变动时，一键查找所有受影响的 YAML 步骤并批量修复。

用法示例：
  # 1. 搜索：找出所有包含某个定位器的步骤（不改任何东西）
  python tools/locator_updater.py search --role button --name "Edit post"

  # 2. Dry-run：预览改动，不写入文件
  python tools/locator_updater.py update --role button --name "Edit post" --new-name "Edit style" --dry-run

  # 3. Apply：确认后真正写入
  python tools/locator_updater.py update --role button --name "Edit post" --new-name "Edit style"

  # 4. 替换 locator 字符串
  python tools/locator_updater.py update --locator "text=Edit post" --new-locator "text=Edit style" --dry-run

  # 5. 替换 test_id
  python tools/locator_updater.py update --test-id "old-btn-id" --new-test-id "new-btn-id" --dry-run

  # 6. 指定特定 YAML 文件（不指定则扫描全部）
  python tools/locator_updater.py search --role tab --name "Posts" --files smoke_testing.yaml

支持的定位器类型：
  role + name   →  { role: 'button', name: 'Save' }
  locator       →  { locator: "button[data-testid='save']" }
  test_id       →  { test_id: 'save-btn' }
  placeholder   →  { placeholder: 'Enter name' }
  aria-label    →  { aria-label: 'close dialog' }
"""

import argparse
import copy
import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple, Dict

import yaml

# ── 项目根路径 & 默认 YAML 搜索目录 ──────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
YAML_SEARCH_DIRS = [
    PROJECT_ROOT / "test_case" / "UI" / "Test_Katana",
]

# ── ANSI 颜色 ─────────────────────────────────────────────────────────────
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def c(color, text): return f"{color}{text}{RESET}"


# ── YAML 文件收集 ─────────────────────────────────────────────────────────

def collect_yaml_files(file_args: Optional[List[str]]) -> List[Path]:
    """收集要扫描的 YAML 文件列表"""
    if file_args:
        result = []
        for f in file_args:
            p = Path(f)
            if not p.is_absolute():
                # 先尝试相对 cwd，再尝试相对项目根
                for base in [Path.cwd(), PROJECT_ROOT]:
                    candidate = base / f
                    if candidate.exists():
                        p = candidate
                        break
            if p.exists():
                result.append(p.resolve())
            else:
                # 在默认目录中递归搜索同名文件
                found = []
                for search_dir in YAML_SEARCH_DIRS:
                    found.extend(search_dir.rglob(p.name))
                if found:
                    result.extend(found)
                else:
                    print(c(YELLOW, f"[WARN] 找不到文件: {f}，已跳过"))
        return result

    # 扫描默认目录（排除 example/ 和 __pycache__）
    files = []
    for search_dir in YAML_SEARCH_DIRS:
        for p in sorted(search_dir.rglob("*.yaml")):
            parts = p.parts
            if any(x in parts for x in ("example", "__pycache__", "actions")):
                continue
            files.append(p)
    return files


# ── 步骤遍历 & 匹配 ───────────────────────────────────────────────────────

def _is_step_dict(obj) -> bool:
    """判断一个 dict 是否是 action 步骤（含定位器字段）"""
    LOCATOR_KEYS = {"locator", "role", "test_id", "placeholder", "name",
                    "aria-label", "aria_label", "label"}
    return isinstance(obj, dict) and bool(LOCATOR_KEYS & obj.keys())


def _matches(step: dict, criteria: dict) -> bool:
    """
    检查 step 是否匹配查询条件。
    criteria 中每个 key 都必须匹配（AND 逻辑）。
    字符串匹配默认大小写不敏感。
    """
    for key, expected in criteria.items():
        actual = step.get(key)
        if actual is None:
            return False
        # 支持模糊匹配（部分包含）
        if isinstance(expected, str) and isinstance(actual, str):
            if expected.lower() not in actual.lower():
                return False
        else:
            if actual != expected:
                return False
    return True


def walk_and_collect(obj, path: list, criteria: dict, results: list, yaml_path: Path,
                     tc_name: str = "", parent_key: str = ""):
    """
    递归遍历 YAML 对象，收集所有匹配步骤。
    results 中每项: {yaml_path, tc_name, step_key, step_val, obj_ref, key_in_parent}
    """
    if isinstance(obj, dict):
        for key, val in obj.items():
            cur_path = path + [key]
            if _is_step_dict(val) and _matches(val, criteria):
                results.append({
                    "yaml_path": yaml_path,
                    "tc_name": tc_name or (path[0] if path else "?"),
                    "step_key": key,
                    "step_val": copy.deepcopy(val),
                    "obj_ref": obj,       # 对原始对象的引用，用于修改
                    "key_in_parent": key,
                })
            # 递归，传递 tc_name
            next_tc = tc_name
            if not tc_name and not path:
                next_tc = key  # 顶层 key 即为 tc_name
            walk_and_collect(val, cur_path, criteria, results, yaml_path,
                             next_tc, key)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            walk_and_collect(item, path + [str(i)], criteria, results,
                             yaml_path, tc_name, parent_key)


# ── 打印 diff ─────────────────────────────────────────────────────────────

def print_match(match: dict, new_step: Optional[dict] = None, index: int = 0):
    """打印一个匹配结果，可选显示修改后的值"""
    yaml_rel = match["yaml_path"].relative_to(PROJECT_ROOT)
    tc = match["tc_name"]
    step_key = match["step_key"]
    old_val = match["step_val"]

    prefix = c(CYAN, f"[{index+1}]")
    print(f"{prefix} {c(BOLD, str(yaml_rel))}  |  tc: {c(YELLOW, tc)}  |  step: {c(CYAN, step_key)}")

    if new_step is None:
        print(f"     {c(GREEN, 'current:')} {_fmt_step(old_val)}")
    else:
        print(f"     {c(RED,   'before: ')} {_fmt_step(old_val)}")
        print(f"     {c(GREEN, 'after:  ')} {_fmt_step(new_step)}")
    print()


def _fmt_step(step: dict) -> str:
    """将步骤 dict 格式化成 YAML inline 风格，便于阅读"""
    parts = []
    for k in ("role", "name", "locator", "test_id", "placeholder",
              "aria-label", "label", "index", "exact", "optional",
              "value", "checked"):
        if k in step:
            v = step[k]
            if isinstance(v, str):
                parts.append(f"{k}: '{v}'")
            else:
                parts.append(f"{k}: {v}")
    # 其余 key
    for k, v in step.items():
        if k not in ("role", "name", "locator", "test_id", "placeholder",
                     "aria-label", "label", "index", "exact", "optional",
                     "value", "checked"):
            parts.append(f"{k}: {repr(v)}")
    return "{ " + ", ".join(parts) + " }"


# ── 构建新步骤 ────────────────────────────────────────────────────────────

def build_new_step(old_step: dict, updates: dict) -> dict:
    """
    在 old_step 基础上应用 updates，返回新 step。
    updates 中 value 为 None 表示删除该字段。
    """
    new_step = copy.deepcopy(old_step)
    for k, v in updates.items():
        if v is None:
            new_step.pop(k, None)
        else:
            new_step[k] = v
    return new_step


# ── YAML 文件读写（保留注释尽量原样）────────────────────────────────────────
# 注：ruamel.yaml 保留注释，但项目中不一定安装。
# 我们用「读取原始文本 + 行级替换」的方式，避免破坏格式。

def _step_to_inline(step: dict) -> str:
    """生成 YAML inline 格式的步骤字符串（不带大括号外的内容）"""
    parts = []
    for k in ("role", "name", "locator", "test_id", "placeholder",
              "aria-label", "label", "index", "exact", "optional",
              "value", "checked", "timeout", "frame"):
        if k in step:
            v = step[k]
            if isinstance(v, str):
                # 根据原始风格决定用单引号还是双引号
                parts.append(f"{k}: '{v}'")
            elif isinstance(v, bool):
                parts.append(f"{k}: {str(v).capitalize()}")
            else:
                parts.append(f"{k}: {v}")
    for k, v in step.items():
        if k not in ("role", "name", "locator", "test_id", "placeholder",
                     "aria-label", "label", "index", "exact", "optional",
                     "value", "checked", "timeout", "frame"):
            if isinstance(v, str):
                parts.append(f"{k}: '{v}'")
            elif isinstance(v, bool):
                parts.append(f"{k}: {str(v).capitalize()}")
            else:
                parts.append(f"{k}: {v}")
    return "{ " + ", ".join(parts) + " }"


def patch_yaml_file(yaml_path: Path, matches_with_new: List[Tuple]) -> int:
    """
    用行级文本替换更新 YAML 文件。
    matches_with_new: list of (match_dict, new_step_dict)
    返回实际替换的行数。
    """
    text = yaml_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changed = 0

    for match, new_step in matches_with_new:
        step_key = match["key_in_parent"]
        old_step = match["step_val"]
        old_inline = _step_to_inline(old_step)
        new_inline = _step_to_inline(new_step)

        # 在文件中找到对应行并替换（匹配 `step_key: { ... }` 形式）
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            # 行必须以 step_key 开头，且内容包含旧定位器的关键字段
            if not stripped.startswith(step_key + ":"):
                continue
            # 验证：行内包含旧步骤的某个关键字段值（防误替换）
            key_field = _get_discriminant_field(old_step)
            if key_field and key_field not in line:
                continue
            # 找到了，执行替换
            indent = len(line) - len(line.lstrip())
            new_line = " " * indent + step_key + ": " + new_inline + "\n"
            lines[i] = new_line
            changed += 1
            break

    if changed:
        yaml_path.write_text("".join(lines), encoding="utf-8")
    return changed


def _get_discriminant_field(step: dict) -> Optional[str]:
    """从步骤中取一个最具辨别性的字段值，用于行匹配验证"""
    for k in ("locator", "test_id", "name", "placeholder", "aria-label"):
        if k in step:
            v = step[k]
            # 取值的一部分（前 20 字符），避免转义问题
            return str(v)[:20]
    return None


# ── 主命令实现 ────────────────────────────────────────────────────────────

def cmd_search(args):
    """search 子命令：扫描并展示所有匹配步骤"""
    criteria = _build_criteria(args)
    if not criteria:
        print(c(RED, "[ERROR] 请至少指定一个搜索条件 (--role, --name, --locator, --test-id, --placeholder)"))
        sys.exit(1)

    files = collect_yaml_files(args.files)
    print(c(BOLD, f"\n扫描 {len(files)} 个 YAML 文件..."))
    print(c(CYAN, f"搜索条件: {criteria}\n"))

    all_results = []
    for yaml_path in files:
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data:
                continue
            results = []
            walk_and_collect(data, [], criteria, results, yaml_path)
            all_results.extend(results)
        except Exception as e:
            print(c(YELLOW, f"[WARN] 解析 {yaml_path.name} 失败: {e}"))

    if not all_results:
        print(c(YELLOW, "未找到任何匹配步骤。"))
        return

    print(c(GREEN, f"找到 {len(all_results)} 个匹配步骤：\n"))
    for i, m in enumerate(all_results):
        print_match(m, index=i)

    # 统计受影响的文件
    affected_files = {str(m["yaml_path"]) for m in all_results}
    print(c(BOLD, f"共涉及 {len(affected_files)} 个文件："))
    for f in sorted(affected_files):
        rel = Path(f).relative_to(PROJECT_ROOT)
        print(f"  • {rel}")


def cmd_update(args):
    """update 子命令：批量更新定位器"""
    criteria = _build_criteria(args)
    updates  = _build_updates(args)

    if not criteria:
        print(c(RED, "[ERROR] 请指定要查找的旧定位器 (--role/--name/--locator/--test-id/--placeholder)"))
        sys.exit(1)
    if not updates:
        print(c(RED, "[ERROR] 请指定至少一个新值 (--new-name/--new-locator/--new-test-id/--new-placeholder/--new-role)"))
        sys.exit(1)

    files = collect_yaml_files(args.files)
    dry_run = args.dry_run

    mode_str = c(YELLOW, "[DRY-RUN]") if dry_run else c(GREEN, "[APPLY]")
    print(c(BOLD, f"\n{mode_str} 扫描 {len(files)} 个 YAML 文件..."))
    print(c(CYAN,  f"查找条件: {criteria}"))
    print(c(GREEN, f"更新内容: {updates}\n"))

    all_matches = []
    file_match_map: Dict[Path, list] = {}  # path -> list of (match, new_step)

    for yaml_path in files:
        try:
            with open(yaml_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data:
                continue
            results = []
            walk_and_collect(data, [], criteria, results, yaml_path)
            if results:
                pairs = [(m, build_new_step(m["step_val"], updates)) for m in results]
                file_match_map[yaml_path] = pairs
                all_matches.extend(results)
        except Exception as e:
            print(c(YELLOW, f"[WARN] 解析 {yaml_path.name} 失败: {e}"))

    if not all_matches:
        print(c(YELLOW, "未找到任何匹配步骤，无需更新。"))
        return

    # 打印所有 diff
    idx = 0
    for yaml_path, pairs in file_match_map.items():
        for match, new_step in pairs:
            print_match(match, new_step, index=idx)
            idx += 1

    print(c(BOLD, f"共 {len(all_matches)} 处改动，涉及 {len(file_match_map)} 个文件"))

    if dry_run:
        print(c(YELLOW, "\n[DRY-RUN 模式] 以上为预览，文件未被修改。"))
        print(c(CYAN,   "去掉 --dry-run 参数可真正写入文件。"))
        return

    # 非 dry-run：询问确认
    ans = input(c(BOLD, "\n确认写入以上修改？[y/N] ")).strip().lower()
    if ans != "y":
        print(c(YELLOW, "已取消，文件未被修改。"))
        return

    total_changed = 0
    for yaml_path, pairs in file_match_map.items():
        changed = patch_yaml_file(yaml_path, pairs)
        rel = yaml_path.relative_to(PROJECT_ROOT)
        print(c(GREEN, f"  ✓ {rel}  ({changed} 行已更新)"))
        total_changed += changed

    print(c(GREEN, c(BOLD, f"\n完成！共更新 {total_changed} 行。")))


# ── 参数解析辅助 ──────────────────────────────────────────────────────────

def _build_criteria(args) -> dict:
    """从 args 中提取搜索条件"""
    criteria = {}
    if getattr(args, "role", None):       criteria["role"] = args.role
    if getattr(args, "name", None):       criteria["name"] = args.name
    if getattr(args, "locator", None):    criteria["locator"] = args.locator
    if getattr(args, "test_id", None):    criteria["test_id"] = args.test_id
    if getattr(args, "placeholder", None): criteria["placeholder"] = args.placeholder
    if getattr(args, "aria_label", None): criteria["aria-label"] = args.aria_label
    return criteria


def _build_updates(args) -> dict:
    """从 args 中提取要更新的字段"""
    updates = {}
    if getattr(args, "new_role", None):        updates["role"] = args.new_role
    if getattr(args, "new_name", None):        updates["name"] = args.new_name
    if getattr(args, "new_locator", None):     updates["locator"] = args.new_locator
    if getattr(args, "new_test_id", None):     updates["test_id"] = args.new_test_id
    if getattr(args, "new_placeholder", None): updates["placeholder"] = args.new_placeholder
    if getattr(args, "new_aria_label", None):  updates["aria-label"] = args.new_aria_label
    # 删除旧字段（例如：从 locator 切换到 role+name，需要删除 locator）
    if getattr(args, "remove_key", None):
        for k in args.remove_key:
            updates[k] = None
    return updates


# ── CLI 入口 ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="locator_updater",
        description="YAML 测试用例定位器批量更新工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── 公共参数 ──
    def add_common_args(p):
        p.add_argument("--role",        help="匹配 role 字段，如 'button'")
        p.add_argument("--name",        help="匹配 name 字段（支持部分匹配）")
        p.add_argument("--locator",     help="匹配 locator 字段（支持部分匹配）")
        p.add_argument("--test-id",     dest="test_id", help="匹配 test_id 字段")
        p.add_argument("--placeholder", help="匹配 placeholder 字段（支持部分匹配）")
        p.add_argument("--aria-label",  dest="aria_label", help="匹配 aria-label 字段")
        p.add_argument("--files",       nargs="+", metavar="FILE",
                       help="只扫描指定文件（文件名或相对路径），默认扫描全部 YAML")

    # ── search ──
    p_search = sub.add_parser("search", help="查找所有匹配步骤（只读）")
    add_common_args(p_search)
    p_search.set_defaults(func=cmd_search)

    # ── update ──
    p_update = sub.add_parser("update", help="批量更新定位器")
    add_common_args(p_update)
    p_update.add_argument("--new-role",        dest="new_role",        help="新的 role 值")
    p_update.add_argument("--new-name",        dest="new_name",        help="新的 name 值")
    p_update.add_argument("--new-locator",     dest="new_locator",     help="新的 locator 值")
    p_update.add_argument("--new-test-id",     dest="new_test_id",     help="新的 test_id 值")
    p_update.add_argument("--new-placeholder", dest="new_placeholder", help="新的 placeholder 值")
    p_update.add_argument("--new-aria-label",  dest="new_aria_label",  help="新的 aria-label 值")
    p_update.add_argument("--remove-key",      dest="remove_key", nargs="+",
                          help="删除指定字段（如 --remove-key locator）")
    p_update.add_argument("--dry-run", action="store_true",
                          help="仅预览改动，不写入文件")
    p_update.set_defaults(func=cmd_update)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
