#!/usr/bin/env python3
"""从 Apifox cases_raw 导出中提取某 case 的步骤名 + 前后置脚本断言，便于与迁移后 pytest 对照。

用法:
    python tools/_dump_apifox_case.py <case_json> [--full]
"""
from __future__ import annotations

import argparse
import json
import re


def emit(name: str, body: str, full: bool) -> None:
    text = body or ""
    if not full:
        # 只保留含断言/赋值的行，降低噪音
        keep = [
            ln
            for ln in text.splitlines()
            if re.search(r"pm\.(test|expect|environment|variables)|await pm|assert", ln)
        ]
        text = "\n".join(keep)
    if text.strip():
        print(f"\n--- {name} ---")
        print(text.strip())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()

    d = json.load(open(a.case, encoding="utf-8"))
    root = d.get("steps") or {}
    if isinstance(root, dict):
        print(f"### case: {root.get('name')}")
        steps = root.get("steps") or []
    else:
        steps = root
    for i, st in enumerate(steps, 1):
        label = st.get("name") or st.get("type") or "?"
        print(f"\n===== step {i}: {label} =====")
        for key in ("preProcessors", "postProcessors"):
            for p in st.get(key) or []:
                emit(f"{key}:{p.get('type', '')}", p.get("data") or p.get("script") or "", a.full)
    # case 级脚本
    for key in ("preProcessors", "postProcessors"):
        for p in (root.get(key) if isinstance(root, dict) else None) or []:
            emit(f"CASE:{key}:{p.get('type', '')}", p.get("data") or p.get("script") or "", a.full)


if __name__ == "__main__":
    main()
