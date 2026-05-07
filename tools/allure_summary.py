#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
allure_summary.py
-----------------
用途：
  1. 读取最新（或指定）allure-results 原始 JSON，统计 PASS/FAIL/BROKEN/SKIP
  2. 把结果以 inline 注释写回 YAML 用例文件，格式：
       testT3554:  # [LAST: PASS 2026-05-06]

用法：
  python tools/allure_summary.py                   # 统计 + 标记（用 main.py 中 yaml_files 对应的文件）
  python tools/allure_summary.py --dry-run          # 只打印，不改文件
  python tools/allure_summary.py --results-dir <dir> --dry-run
  python tools/allure_summary.py --yaml <f1> <f2>   # 只标记指定文件

注：必须从项目根目录运行，或者把根目录加入 PYTHONPATH。
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime

# ─── 项目结构常量 ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_ROOT = os.path.join(BASE_DIR, 'allure-results')
YAML_BASE = os.path.join(BASE_DIR, 'test_case', 'UI', 'Test_Katana')

# 内联注释的正则：匹配旧标记，方便替换
_MARKER_RE = re.compile(r'\s*#\s*\[LAST:.*?\]\s*$')

# ─── 1. 获取最新 results 目录 ─────────────────────────────────────

def get_latest_results_dir():
    subdirs = sorted(
        (d for d in os.listdir(RESULTS_ROOT)
         if os.path.isdir(os.path.join(RESULTS_ROOT, d))),
        reverse=True
    )
    if not subdirs:
        print("[ERROR] allure-results/ 下没有找到任何子目录")
        return None
    latest = os.path.join(RESULTS_ROOT, subdirs[0])
    print(f"[INFO] 使用最新结果目录: {latest}")
    return latest


# ─── 2. 解析原始 result.json ──────────────────────────────────────

def parse_results(results_dir: str) -> dict:
    """
    返回 { test_name: {'status': str, 'message': str} }
    status: 'passed' | 'failed' | 'broken' | 'skipped'
    """
    result_files = glob.glob(os.path.join(results_dir, '*-result.json'))
    data = {}
    for f in result_files:
        try:
            with open(f, encoding='utf-8') as fp:
                d = json.load(fp)
            name = d.get('name', '')
            if not name:
                continue
            status = d.get('status', 'unknown').lower()
            message = d.get('statusDetails', {}).get('message', '') or ''
            # 去掉 message 中多余的换行，只保留第一行
            message = message.split('\n')[0].strip()[:120]
            data[name] = {'status': status, 'message': message}
        except Exception as e:
            print(f"[WARN] 解析 {f} 失败: {e}")
    return data


# ─── 3. 打印统计摘要 ─────────────────────────────────────────────

def print_summary(results: dict, date_str: str):
    buckets = {'passed': [], 'failed': [], 'broken': [], 'skipped': []}
    for name, info in results.items():
        s = info['status']
        buckets.setdefault(s, []).append(name)

    icons = {'passed': '✅', 'failed': '❌', 'broken': '💥', 'skipped': '⏭ '}
    total = len(results)

    print(f"\n{'='*60}")
    print(f"  Allure 测试结果摘要  ({date_str})  共 {total} 条")
    print(f"{'='*60}")
    for status in ('passed', 'failed', 'broken', 'skipped'):
        names = sorted(buckets.get(status, []))
        icon = icons.get(status, '?')
        print(f"\n{icon} {status.upper()} ({len(names)}):")
        for n in names:
            msg = results[n]['message']
            suffix = f"  → {msg}" if msg and status != 'passed' else ''
            print(f"    {n}{suffix}")

    print(f"\n{'─'*60}")
    counts = {s: len(v) for s, v in buckets.items()}
    print(f"  PASS:{counts.get('passed',0)}  "
          f"FAIL:{counts.get('failed',0)}  "
          f"BROKEN:{counts.get('broken',0)}  "
          f"SKIP:{counts.get('skipped',0)}")
    print(f"{'='*60}\n")


# ─── 4. 标记 YAML 文件 ────────────────────────────────────────────

def _make_marker(status: str, date_str: str) -> str:
    label = status.upper()
    return f"  # [LAST: {label} {date_str}]"


def annotate_yaml(yaml_rel_path: str, results: dict, date_str: str, dry_run: bool):
    """
    给 yaml_rel_path 中每个顶层 test key 追加 / 更新 inline 状态注释。
    yaml_rel_path 相对于 YAML_BASE。
    """
    yaml_path = os.path.join(YAML_BASE, yaml_rel_path.replace('/', os.sep))
    if not os.path.exists(yaml_path):
        print(f"[WARN] 文件不存在，跳过: {yaml_path}")
        return

    with open(yaml_path, encoding='utf-8') as f:
        lines = f.readlines()

    changed = 0
    new_lines = []
    for line in lines:
        # 判断是否是顶层 test key（行首非空格，以 test 开头，包含冒号）
        stripped = line.rstrip('\n')
        m = re.match(r'^(test\w+):\s*(#.*)?$', stripped)
        if m:
            key = m.group(1)
            if key in results:
                status = results[key]['status']
                # 去掉旧标记，重新追加
                base = _MARKER_RE.sub('', stripped)
                new_line = base + _make_marker(status, date_str) + '\n'
                if new_line != line:
                    changed += 1
                new_lines.append(new_line)
                continue
        new_lines.append(line)

    rel = yaml_rel_path
    if changed == 0:
        print(f"[INFO] {rel} — 无变化（{len(results)} 条结果，0 条命中此文件）")
    else:
        print(f"[INFO] {rel} — 标记 {changed} 条用例")

    if not dry_run and changed > 0:
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"       已写入 {yaml_path}")


# ─── 5. 主入口 ────────────────────────────────────────────────────

# 默认要标记的 YAML 文件列表（相对 YAML_BASE）
DEFAULT_YAMLS = [
    'All_YAML/Module/Module.yaml',
    'All_YAML/Form/Storefront_form.yaml',
    'All_YAML/Form/Storefront_product_with_form.yaml',
    'All_YAML/Post/Post_setting.yaml',
    'All_YAML/Events/Scanner.yaml',
    'All_YAML/Events/Sync_event_post.yaml',
]


def main():
    parser = argparse.ArgumentParser(description='统计 Allure 结果并标记 YAML 用例状态')
    parser.add_argument('--results-dir', default=None,
                        help='指定 allure-results 子目录（默认自动选最新）')
    parser.add_argument('--yaml', nargs='+', default=None,
                        help='要标记的 YAML 文件（相对 Test_Katana/，默认全部）')
    parser.add_argument('--dry-run', action='store_true',
                        help='只打印，不修改文件')
    args = parser.parse_args()

    # 1. 确定 results 目录
    results_dir = args.results_dir or get_latest_results_dir()
    if not results_dir:
        sys.exit(1)

    # 2. 解析结果
    results = parse_results(results_dir)
    if not results:
        print('[ERROR] 未找到任何 result.json，退出')
        sys.exit(1)

    # 3. 日期标记（从目录名取，例如 20260506_154240）
    dirname = os.path.basename(results_dir)
    try:
        date_str = datetime.strptime(dirname[:8], '%Y%m%d').strftime('%Y-%m-%d')
    except ValueError:
        date_str = datetime.now().strftime('%Y-%m-%d')

    # 4. 打印摘要
    print_summary(results, date_str)

    # 5. 标记 YAML
    yaml_files = args.yaml or DEFAULT_YAMLS
    if args.dry_run:
        print('[DRY-RUN] 不会修改任何文件\n')
    for yf in yaml_files:
        annotate_yaml(yf, results, date_str, dry_run=args.dry_run)

    if args.dry_run:
        print('\n[DRY-RUN 完成] 重新运行不带 --dry-run 即可写入文件')
    else:
        print('\n[完成] 所有 YAML 文件已更新')


if __name__ == '__main__':
    main()
