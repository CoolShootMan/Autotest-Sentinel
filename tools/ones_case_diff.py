#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diff 两份 ONES 用例快照，回答"我手上的用例是不是最新的？"

背景：用例维护者会随时改 ONES 用例（改步骤、改期望结果、整条重写）。
执行前如果复用上一次跑留下的本地快照，就会按**已废弃的步骤/期望**跑，
得出"预期未实现"的假 FAIL（KAT-12069/T5727 实测踩过）。

用法：
    # 1) 先拉一份最新的
    py -3.9 tools/ones_reader.py "<ONES_LINK>" --out data/verify/<KEY>/ones_cases_live.json

    # 2) 与本地旧快照 diff（旧快照通常是 ones_cases.json）
    py -3.9 tools/ones_case_diff.py \
        data/verify/<KEY>/ones_cases.json \
        data/verify/<KEY>/ones_cases_live.json

默认输出 <NEW_JSON 同目录>/case_diff.md 与 case_diff.json；
若 diff 结果显示"没有任何用例发生变化"，才说明你可以安全复用当前快照。

读取全程只读，不碰 ONES。
"""
from __future__ import annotations  # 兼容 py 3.9（本机唯一带 playwright 的解释器）

import argparse
import json
import os
import sys

FIELDS = ("name", "condition", "desc", "priority", "type", "module")


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    # 兼容 {"cases": [...]} 与裸 list 两种形态
    cases = data["cases"] if isinstance(data, dict) else data
    fetched_at = data.get("fetched_at") if isinstance(data, dict) else None
    return {c["id"]: c for c in cases}, fetched_at


def steps_of(case):
    return [
        (s.get("index"), (s.get("desc") or "").strip(), (s.get("result") or "").strip())
        for s in case.get("steps", [])
    ]


def sort_key(cid):
    digits = "".join(ch for ch in cid if ch.isdigit())
    return (0, int(digits)) if digits else (1, cid)


def build_report(old, old_at, new, new_at, old_label, new_label):
    lines = []
    lines.append("# ONES 用例快照同步核查（本地镜像 vs 线上最新）")
    lines.append("")
    lines.append(f"- 基准 `{old_label}`：fetched_at = **{old_at}**")
    lines.append(f"- 对照 `{new_label}`：fetched_at = **{new_at}**")
    lines.append(f"- 用例数：旧 {len(old)} / 新 {len(new)}")
    lines.append("")

    only_old = sorted(set(old) - set(new), key=sort_key)
    only_new = sorted(set(new) - set(old), key=sort_key)
    if only_old:
        lines.append(f"⚠️ 只存在于旧快照（可能已被删除/移出模块）：{only_old}")
    if only_new:
        lines.append(f"⚠️ 只存在于线上（新增用例）：{only_new}")
    if not only_old and not only_new:
        lines.append("用例集合一致。")

    changed = []
    for cid in sorted(set(old) & set(new), key=sort_key):
        o, n = old[cid], new[cid]
        diffs = []
        for field in FIELDS:
            if (o.get(field) or "").strip() != (n.get(field) or "").strip():
                diffs.append({"field": field, "old": o.get(field), "new": n.get(field)})
        so, sn = steps_of(o), steps_of(n)
        if so != sn:
            diffs.append({"field": "steps", "old": so, "new": sn})
        if diffs:
            changed.append((cid, n.get("name") or o.get("name"), diffs))

    lines.append("")
    if not changed:
        lines.append("## ✅ 没有任何用例发生变化")
        lines.append("")
        lines.append("→ 当前本地快照与线上一致，可以安全复用。")
    else:
        lines.append(f"## ⚠️ 有 **{len(changed)}** 条用例与旧快照不一致")
        lines.append("")
        lines.append("→ 说明线上用例已更新，**必须以线上版为准**；旧快照不可再用于执行。")
        lines.append("")
        for cid, name, diffs in changed:
            lines.append(f"### {cid} — {name}")
            lines.append("")
            for d in diffs:
                if d["field"] == "steps":
                    lines.append("**steps 有差异**（旧 → 新）：")
                    lines.append("")
                    lines.append("| # | 旧 desc | 旧 result | 新 desc | 新 result |")
                    lines.append("|---|---------|-----------|---------|-----------|")
                    maxlen = max(len(d["old"]), len(d["new"]))
                    for i in range(maxlen):
                        oi = d["old"][i] if i < len(d["old"]) else ("", "", "")
                        ni = d["new"][i] if i < len(d["new"]) else ("", "", "")
                        mark = "" if oi[1:] == ni[1:] else " ⚠️"
                        lines.append(f"| {i + 1}{mark} | {oi[1]} | {oi[2]} | {ni[1]} | {ni[2]} |")
                    lines.append("")
                else:
                    lines.append(f"**{d['field']}**")
                    lines.append("")
                    lines.append(f"- 旧：`{d['old']}`")
                    lines.append(f"- 新：`{d['new']}`")
                    lines.append("")
    return "\n".join(lines), changed, only_old, only_new


def main():
    ap = argparse.ArgumentParser(description="Diff 两份 ONES 用例快照")
    ap.add_argument("old", help="旧快照 JSON（本地遗留）")
    ap.add_argument("new", help="线上最新 JSON（ones_reader --out 产物）")
    ap.add_argument("--out-md", default=None, help="diff markdown 输出路径")
    ap.add_argument("--out-json", default=None, help="diff 摘要 JSON 输出路径")
    args = ap.parse_args()

    new_dir = os.path.dirname(os.path.abspath(args.new))
    out_md = args.out_md or os.path.join(new_dir, "case_diff.md")
    out_json = args.out_json or os.path.join(new_dir, "case_diff.json")

    old, old_at = load(args.old)
    new, new_at = load(args.new)
    md, changed, only_old, only_new = build_report(
        old, old_at, new, new_at,
        os.path.basename(args.old), os.path.basename(args.new),
    )

    with open(out_md, "w", encoding="utf-8") as fh:
        fh.write(md)

    summary = {
        "old_fetched_at": old_at,
        "new_fetched_at": new_at,
        "changed_cases": [c[0] for c in changed],
        "changed_count": len(changed),
        "only_old": only_old,
        "only_new": only_new,
    }
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)

    print(f"changed={len(changed)} only_old={len(only_old)} only_new={len(only_new)}")
    print(f"md  -> {out_md}")
    print(f"json-> {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
