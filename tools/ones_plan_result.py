#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONES 测试计划 —— 回写用例「执行结果」（把"未执行"改成 passed/failed/...）。

背景：用例建出来后，计划里每条用例的执行状态默认是 `to_do`（ONES UI 显示「未执行」）。
浏览器验完只写 report.md 是不够的 —— 计划看板上仍是「未执行」。本工具负责把结论落回 ONES。

实测端点（2026-09-18 于 sz.ones.cn / team T7u1zXum / plan UjmD4hzp 验证通过）：

    POST /project/api/project/team/{team}/testcase/plan/{plan}/cases/update
    body: {"cases": [{"uuid": "<case_uuid>", "result": "passed", "note": "..."}]}
    resp: {"success_cases": [...], "not_found_cases": [...], "no_permission_cases": [...]}

`result` 合法枚举（其余值返 400 InvalidParameter.TestCase.Result.InvalidType）：
    to_do   未执行（默认）
    passed  通过
    failed  失败
    blocked 阻塞
    skipped 跳过

`note` 为计划内备注（可空字符串）。

读回：GET /project/api/project/team/{team}/testcase/plan/{plan}/cases
      -> {"cases": [{uuid, result, note, executor, ...}]}

用法：
    # 单条/多条
    py -3.9 tools/ones_plan_result.py --plan UjmD4hzp \
        --set 7UdpmKjo=failed:"关闭开关无法保存" --set Ds8QUXpQ=passed

    # 从 JSON 文件批量
    py -3.9 tools/ones_plan_result.py --plan UjmD4hzp --json data/results.json
    #   data/results.json: {"Ds8QUXpQ": {"result":"passed","note":""}, ...}
    #   或简写 {"Ds8QUXpQ": "passed"}

    # 只读回当前状态
    py -3.9 tools/ones_plan_result.py --plan UjmD4hzp --show
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ones_writer import load_env, api_call, ensure_token  # noqa: E402

VALID_RESULTS = {"to_do", "passed", "failed", "blocked", "skipped"}


def plan_cases(plan_uuid: str, env: dict):
    team = env.get("ONES_TEAM_UUID", "T7u1zXum")
    status, resp = api_call(
        "GET", f"/project/api/project/team/{team}/testcase/plan/{plan_uuid}/cases", env=env
    )
    if status == 200 and isinstance(resp, dict):
        return resp.get("cases", [])
    raise RuntimeError(f"读取计划用例失败 {status}: {str(resp)[:300]}")


def update_results(plan_uuid: str, entries: list, env: dict):
    """entries: [{"uuid":..., "result":..., "note":...}]"""
    team = env.get("ONES_TEAM_UUID", "T7u1zXum")
    status, resp = api_call(
        "POST",
        f"/project/api/project/team/{team}/testcase/plan/{plan_uuid}/cases/update",
        {"cases": entries},
        env=env,
    )
    return status, resp


def parse_set(raw: str):
    """解析 `uuid=result[:note]`"""
    if "=" not in raw:
        raise argparse.ArgumentTypeError(f"--set 需要 uuid=result[:note]，收到 {raw!r}")
    uuid_, rest = raw.split("=", 1)
    if ":" in rest:
        result, note = rest.split(":", 1)
    else:
        result, note = rest, ""
    result = result.strip()
    if result not in VALID_RESULTS:
        raise argparse.ArgumentTypeError(
            f"result 必须是 {sorted(VALID_RESULTS)} 之一，收到 {result!r}"
        )
    return {"uuid": uuid_.strip(), "result": result, "note": note}


def load_json_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    entries = []
    for uuid_, v in data.items():
        if isinstance(v, str):
            entries.append({"uuid": uuid_, "result": v, "note": ""})
        else:
            entries.append({
                "uuid": uuid_,
                "result": v.get("result", "to_do"),
                "note": v.get("note", ""),
            })
    return entries


def main():
    ap = argparse.ArgumentParser(description="回写 ONES 测试计划用例执行结果")
    ap.add_argument("--plan", required=True, help="测试计划 uuid")
    ap.add_argument("--set", action="append", default=[], metavar="UUID=RESULT[:NOTE]",
                    help="单条结果，可重复")
    ap.add_argument("--json", metavar="FILE", help="JSON 文件批量结果")
    ap.add_argument("--show", action="store_true", help="只打印当前计划内用例的执行状态")
    args = ap.parse_args()

    env = load_env()
    ensure_token(env)

    if args.show or (not args.set and not args.json):
        cases = plan_cases(args.plan, env)
        print(f"plan {args.plan} — {len(cases)} cases")
        print("-" * 78)
        counts = {}
        for c in cases:
            r = c.get("result", "?")
            counts[r] = counts.get(r, 0) + 1
            print(f"  {c.get('uuid','?'):10s}  {r:8s}  {c.get('name','')[:56]}")
        print("-" * 78)
        print("summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
        return

    entries = []
    for raw in args.set:
        entries.append(parse_set(raw))
    if args.json:
        entries.extend(load_json_file(args.json))

    unknown = [e["uuid"] for e in entries if e["result"] not in VALID_RESULTS]
    if unknown:
        print(f"ERROR: 非法 result 的用例: {unknown}", file=sys.stderr)
        sys.exit(1)

    print(f"回写 {len(entries)} 条到 plan {args.plan} ...")
    status, resp = update_results(args.plan, entries, env)
    print(f"  HTTP {status}")
    if status == 200 and isinstance(resp, dict):
        print(f"  success: {len(resp.get('success_cases', []))}")
        for k in ("not_found_cases", "no_permission_cases", "not_handle_cases"):
            if resp.get(k):
                print(f"  {k}: {resp[k]}")
        # 读回校验
        cases = plan_cases(args.plan, env)
        got = {c["uuid"]: c.get("result") for c in cases}
        bad = [e["uuid"] for e in entries if got.get(e["uuid"]) != e["result"]]
        print("  校验: " + ("全部一致 OK" if not bad else f"不一致 -> {bad}"))
        if bad:
            sys.exit(1)
    else:
        print(f"  FAILED: {str(resp)[:400]}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
