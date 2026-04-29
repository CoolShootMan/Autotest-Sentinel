#!/usr/bin/env python3
"""
环境切换脚本 - 一键替换 YAML/Python 中的 URL 前缀

用法:
    python tools/switch_env.py --to=staging   # 切换到开发环境
    python tools/switch_env.py --to=release   # 切换到测试环境
    python tools/switch_env.py --to=prod       # 切换到生产环境
    python tools/switch_env.py --dry-run=staging  # 预览模式（不改文件）
    python tools/switch_env.py --list          # 列出所有环境
"""

import argparse
import os
import re
import shutil
import sys
import glob
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "env_config.yaml"


def load_config():
    """加载环境配置"""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(cfg):
    """保存环境配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def get_target_files(scan_patterns):
    """获取需要扫描的文件列表（排除 example 和 __pycache__）"""
    files = []
    for pattern in scan_patterns:
        full_pattern = BASE_DIR / pattern
        for path in glob.glob(str(full_pattern), recursive=True):
            # 排除 example 文件和 pycache
            if "__pycache__" in path or "example" in path.lower():
                continue
            files.append(Path(path))
    return sorted(set(files))


def replace_content(text, old_base, new_base, old_env, new_env):
    """
    在文本中替换 URL 前缀和 cookie 文件名。
    替换内容：
      1. URL: https://release.pear.us → https://staging.pear.us
      2. Cookie 文件名: cookie_release.json → cookie_staging.json 等
    """
    # 1. 替换 URL 前缀
    url_pattern = re.escape(old_base) + r"(?=/|\?|#|$)"
    text = re.sub(url_pattern, new_base, text)

    # 2. 替换 cookie 文件名（统一用 _{env}.json 后缀）
    # 匹配形如 "cookie_旧环境名" 的文件名引用
    cookie_patterns = [
        # 标准命名: cookie_release.json → cookie_staging.json
        (re.escape(f"cookie_{old_env}.json"), f"cookie_{new_env}.json"),
        # co_seller: cookie_release_co_seller.json → cookie_staging_co_seller.json
        (re.escape(f"cookie_{old_env}_co_seller.json"), f"cookie_{new_env}_co_seller.json"),
        # partner_coseller: cookie_partner_coseller_release.json → cookie_partner_coseller_staging.json
        #                   cookie_partner_release.json → cookie_partner_staging.json
        (re.escape(f"cookie_partner_coseller_{old_env}.json"), f"cookie_partner_coseller_{new_env}.json"),
        (re.escape(f"cookie_partner_{old_env}.json"), f"cookie_partner_{new_env}.json"),
        (re.escape(f"cookie_{old_env}_partner_coseller.json"), f"cookie_{new_env}_partner_coseller.json"),
        (re.escape(f"cookie_{old_env}_partner.json"), f"cookie_{new_env}_partner.json"),
        # standalone: cookie_release_co_seller.json (old pattern)
        (re.escape(f"cookie_release_co_seller.json"), f"cookie_{new_env}_co_seller.json"),
        (re.escape(f"cookie_partner_coseller_release.json"), f"cookie_partner_coseller_{new_env}.json"),
    ]
    for old_pattern, new_replacement in cookie_patterns:
        text = re.sub(old_pattern, new_replacement, text)

    return text


def process_file(filepath, old_base, new_base, old_env, new_env, dry_run=False, verbose=False):
    """处理单个文件，返回替换数量"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  [跳过] {filepath} - 读取失败: {e}")
        return 0

    new_content = replace_content(content, old_base, new_base, old_env, new_env)

    if new_content == content:
        return 0  # 无变化

    url_count = len(re.findall(re.escape(old_base) + r"(?=/|\?|#|$)", content))
    cookie_count = 0
    cookie_patterns = [
        (re.escape(f"cookie_{old_env}.json"), f"cookie_{new_env}.json"),
        (re.escape(f"cookie_{old_env}_co_seller.json"), f"cookie_{new_env}_co_seller.json"),
        (re.escape(f"cookie_partner_coseller_{old_env}.json"), f"cookie_partner_coseller_{new_env}.json"),
        (re.escape(f"cookie_partner_{old_env}.json"), f"cookie_partner_{new_env}.json"),
        (re.escape(f"cookie_{old_env}_partner_coseller.json"), f"cookie_{new_env}_partner_coseller.json"),
        (re.escape(f"cookie_{old_env}_partner.json"), f"cookie_{new_env}_partner.json"),
        (re.escape("cookie_release_co_seller.json"), f"cookie_{new_env}_co_seller.json"),
        (re.escape("cookie_partner_coseller_release.json"), f"cookie_partner_coseller_{new_env}.json"),
    ]
    for old_pattern, _ in cookie_patterns:
        cookie_count += len(re.findall(old_pattern, content))
    total_count = url_count + cookie_count

    if dry_run:
        print(f"  [DRY] {filepath}  →  将替换 {total_count} 处 (URL:{url_count} + cookie:{cookie_count})")
        if verbose:
            lines = content.split("\n")
            new_lines = new_content.split("\n")
            for i, (old_l, new_l) in enumerate(zip(lines, new_lines)):
                if old_l != new_l:
                    print(f"       行 {i+1}: {old_l.strip()[:80]}")
                    print(f"       →    {new_l.strip()[:80]}")
    else:
        # 备份
        backup_path = filepath.with_suffix(filepath.suffix + ".bak")
        shutil.copy2(filepath, backup_path)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  [修改] {filepath}  ({total_count} 处: URL×{url_count} cookie×{cookie_count})  |  备份: {backup_path.name}")

    return total_count


def preview_change(content, old_base, new_base):
    """预览替换后的差异（简单字符差异）"""
    new_content = replace_content(content, old_base, new_base)
    if new_content == content:
        return None
    return new_content


def switch_env(target_env, dry_run=False, verbose=False):
    """执行环境切换"""
    cfg = load_config()
    envs = cfg.get("envs", {})

    if target_env not in envs:
        print(f"[错误] 未知环境: {target_env}")
        print("可用环境:", list(envs.keys()))
        return False

    current_env = cfg.get("current_env", "release")
    if target_env == current_env and not dry_run:
        print(f"[提示] 当前已是 {target_env} ({envs[target_env]['desc']})，无需切换。")
        return True

    old_base = envs[current_env]["base"]
    new_base = envs[target_env]["base"]

    print(f"\n{'='*60}")
    print(f"环境切换:  {current_env} ({old_base})")
    print(f"       →  {target_env} ({new_base})")
    print(f"模式:     {'DRY-RUN（预览，不改文件）' if dry_run else '正式执行'}")
    print(f"{'='*60}\n")

    scan_patterns = cfg.get("scan_patterns", [])
    files = get_target_files(scan_patterns)
    print(f"扫描文件数: {len(files)}\n")

    total_replacements = 0
    for filepath in files:
        count = process_file(filepath, old_base, new_base, current_env, target_env,
                              dry_run=dry_run, verbose=verbose)
        total_replacements += count

    print(f"\n{'='*60}")
    if dry_run:
        print(f"DRY-RUN 完成: 共发现 {total_replacements} 处需要替换")
        print("运行时不加 --dry-run 即可正式执行替换。")
    else:
        print(f"切换完成: {total_replacements} 处已替换")
        print(f"备份文件 (*.bak) 在各自目录中，可手动删除。")
        # 更新当前环境
        cfg["current_env"] = target_env
        save_config(cfg)
        print(f"\n[OK] config/env_config.yaml 已更新，当前环境 = {target_env}")
    print(f"{'='*60}\n")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="一键切换测试环境 URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python tools/switch_env.py --to=staging    # 切换到开发环境
  python tools/switch_env.py --to=prod         # 切换到生产环境
  python tools/switch_env.py --dry-run=release # 预览切换到测试环境（不改文件）
  python tools/switch_env.py --list            # 列出所有环境
  python tools/switch_env.py --to=staging -v   # 显示详细替换行
        """
    )
    parser.add_argument("--to", dest="target", help="目标环境 (staging / release / prod)")
    parser.add_argument("--dry-run", dest="dry_run", help="预览模式，值为目标环境")
    parser.add_argument("--list", action="store_true", help="列出所有可用环境")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细替换行")

    args = parser.parse_args()

    # 优先级: --dry-run > --to > --list
    if args.dry_run:
        success = switch_env(args.dry_run, dry_run=True, verbose=args.verbose)
    elif args.target:
        success = switch_env(args.target, dry_run=False, verbose=args.verbose)
    elif args.list:
        cfg = load_config()
        list_envs(cfg)
        success = True
    else:
        parser.print_help()
        print()
        cfg = load_config()
        list_envs(cfg)
        success = True

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
