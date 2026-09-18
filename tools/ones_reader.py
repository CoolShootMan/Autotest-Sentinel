#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONES Test Case Reader — 把 ONES 用例链接读成结构化 JSON / Markdown。

与 ones_writer.py 配套：writer 负责写入（建用例 / 建计划），reader 负责读取。
纯只读，不产生任何写操作。

用法（在仓库根目录执行）:
    # 计划级链接
    py -3.9 tools/ones_reader.py "https://ones.cn/project/#/testcase/team/T7u1zXum/plan/JxAZP9Xw/library"

    # 模块级链接（模块下用例）
    py -3.9 tools/ones_reader.py "https://ones.cn/project/#/testcase/team/T7u1zXum/plan/QCuFwDdq/library/XcAFFViB/module/3moKQuHE" \
        --grep "form" --out data/KAT-11397_ones_cases.json --markdown

    # 单条用例
    py -3.9 tools/ones_reader.py --case RasykFr3 --markdown

    # 只列模块树（找 module uuid）
    py -3.9 tools/ones_reader.py --list-modules

实测确认（2026-09-17，sz.ones.cn / ones.cn 同源 team T7u1zXum）:

  1) GraphQL  POST /project/api/project/team/{team}/items/graphql
     testcaseCases(filter: {testcaseModule_in: ["<module>"]}, limit: N) {
        uuid name number condition desc priority{uuid} testcaseModule{uuid name} }
     -> 模块维度 **服务端过滤**，一次拿全元数据。（testcasePlan_in 对 testcaseCases 非法）

     testcaseCaseSteps(filter: {testcaseCase_in: ["<uuid>", ...]}) {
        testcaseCase{uuid} desc result index }
     -> **批量取步骤**，一次调用可拿多条例用步骤（可分块）。

  2) REST
     GET  /testcase/libraries                  -> 库 + 全模块树（用于 uuid→名称）
     GET  /testcase/library/{lib}/cases        -> 全库用例（**忽略一切过滤/分页参数**，实测 4768 条全返）
     GET  /testcase/library/{lib}/case/{uuid}  -> 单条用例（含 steps）
     GET  /testcase/plan/{plan}/cases          -> 计划内用例（steps 恒为空）
     GET  /project/api/project/users/me        -> token 校验

注意:
  - ONES token 约 1 小时过期；失效时本脚本默认自动调 ones_writer.refresh_token_via_playwright()
    重登刷新（会弹浏览器）。加 --no-refresh 可禁用。
  - 本仓库两处优先级记录对 P3/P4 不一致（见 PRIORITY_NAMES 注释），本项目只用 P0/P1，未实测项不臆造。
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
ENV_PATH = PROJECT_DIR / "backend" / ".env"

STEPS_CHUNK = 100

# P0/P1/P2 三处记录一致；P3/P4 在 SKILL.md 与 references 里互相矛盾（3DvJC11V / R7wMSiP3 谁 low 谁 lowest 未实测），
# 本项目约定只用 P0/P1，遇到 P3/P4 时按 UI 实际标签核对后再补。
PRIORITY_NAMES = {
    "3g7bLpa1": "P0",
    "VRXHXgbp": "P1",
    "JoEcqaCe": "P2",
}
TYPE_NAMES = {
    "7qLS7W5f": "functional",
    "Av5GQKDJ": "performance",
}


# ---------------------------------------------------------------------------
# env / auth
# ---------------------------------------------------------------------------

def load_env() -> dict:
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def refresh_token():
    """复用 ones_writer 的 Playwright 刷新逻辑，避免重复实现。"""
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from ones_writer import refresh_token_via_playwright
    except Exception as e:  # pragma: no cover
        print(f"无法导入 ones_writer 刷新 token: {e}", file=sys.stderr)
        sys.exit(1)
    return refresh_token_via_playwright()


class OnesClient:
    def __init__(self, env: dict):
        self.base = env.get("ONES_URL", "https://sz.ones.cn").rstrip("/")
        self.team = env.get("ONES_TEAM_UUID", "T7u1zXum")
        self.library = env.get("ONES_LIBRARY_UUID", "XcAFFViB")
        self.token = env.get("ONES_AUTH_TOKEN", "")

    # --- transport ---

    def _req(self, path: str, body=None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(
            f"{self.base}{path}", data=data,
            method="POST" if data is not None else "GET",
            headers={"Authorization": f"Bearer {self.token}",
                     "Content-Type": "application/json",
                     "x-request-csrf-token": "1"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode("utf-8", "replace")
                try:
                    return r.status, json.loads(raw)
                except json.JSONDecodeError:
                    return r.status, raw
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")
        except Exception as e:
            return 0, str(e)

    def gql(self, query: str, variables: dict):
        return self._req(f"/project/api/project/team/{self.team}/items/graphql",
                         {"query": query, "variables": variables})

    # --- meta ---

    def check_token(self) -> bool:
        status, _ = self._req("/project/api/project/users/me")
        return status == 200

    def libraries(self):
        status, resp = self._req(f"/project/api/project/team/{self.team}/testcase/libraries")
        return resp.get("libraries", []) if status == 200 and isinstance(resp, dict) else []

    def library_name(self) -> str:
        for lib in self.libraries():
            if lib.get("uuid") == self.library:
                return lib.get("name", "")
        return ""

    def module_names(self) -> dict:
        """uuid -> '祖 / 父 / 模块' 完整名称。只解析目标库，跨库合并会串名。"""
        out = {}
        for lib in self.libraries():
            if lib.get("uuid") != self.library:
                continue
            flat = {m["uuid"]: m for m in lib.get("modules", [])}
            for uuid, m in flat.items():
                chain, cur, guard = [m["name"]], m.get("parent_uuid", ""), 0
                while cur and cur in flat and guard < 10:
                    chain.append(flat[cur]["name"])
                    cur = flat[cur].get("parent_uuid", "")
                    guard += 1
                out[uuid] = " / ".join(reversed(chain))
        return out

    # --- case collection ---

    def cases_by_module(self, module_uuid: str) -> list:
        """GraphQL 服务端按模块过滤（一次拿全元数据）。失败返回 None 由调用方回退 REST。"""
        q = """query ($f: Filter, $n: Int) {
          testcaseCases(filter: $f, limit: $n) {
            uuid name number condition desc
            priority { uuid }
            testcaseModule { uuid name }
          }
        }"""
        status, resp = self.gql(q, {"f": {"testcaseModule_in": [module_uuid]}, "n": 1000})
        if status == 200 and isinstance(resp, dict) and resp.get("data"):
            return resp["data"].get("testcaseCases") or []
        print(f"  ! GraphQL 模块过滤失败({status})，回退 REST 全库本地过滤", file=sys.stderr)
        return None

    def cases_by_plan(self, plan_uuid: str) -> list:
        status, resp = self._req(
            f"/project/api/project/team/{self.team}/testcase/plan/{plan_uuid}/cases")
        if status != 200 or not isinstance(resp, dict):
            print(f"  ! 拉取计划用例失败 ({status}): {str(resp)[:200]}", file=sys.stderr)
            return []
        return resp.get("cases", [])

    def cases_by_library(self) -> list:
        status, resp = self._req(
            f"/project/api/project/team/{self.team}/testcase/library/{self.library}/cases")
        if status != 200 or not isinstance(resp, dict):
            print(f"  ! 拉取库用例失败 ({status}): {str(resp)[:200]}", file=sys.stderr)
            return []
        return resp.get("cases", [])

    def case_detail(self, case_uuid: str):
        status, resp = self._req(
            f"/project/api/project/team/{self.team}/testcase/library/{self.library}/case/{case_uuid}")
        if status != 200 or not isinstance(resp, dict):
            print(f"  ! 用例 {case_uuid} 详情拉取失败 ({status})", file=sys.stderr)
            return None
        return resp

    def steps_bulk(self, uuids: list) -> dict:
        """批量取步骤：{case_uuid: [ {index, desc, result, execute_result, actual_result} ]}。"""
        q = """query ($f: testcaseCaseStepsFilter) {
          testcaseCaseSteps(filter: $f) {
            testcaseCase { uuid }
            desc result index
          }
        }"""
        out = {}
        for i in range(0, len(uuids), STEPS_CHUNK):
            chunk = uuids[i:i + STEPS_CHUNK]
            status, resp = self.gql(q, {"f": {"testcaseCase_in": chunk}})
            if status != 200 or not isinstance(resp, dict) or not resp.get("data"):
                print(f"  ! 批量取步骤失败 ({status}): {str(resp)[:160]}", file=sys.stderr)
                return None
            for s in resp["data"].get("testcaseCaseSteps") or []:
                cu = (s.get("testcaseCase") or {}).get("uuid", "")
                out.setdefault(cu, []).append({
                    "desc": s.get("desc", ""),
                    "result": s.get("result", ""),
                    "index": s.get("index", 0),
                })
        for v in out.values():
            v.sort(key=lambda x: x.get("index", 0))
        return out


# ---------------------------------------------------------------------------
# link parsing
# ---------------------------------------------------------------------------

UUID_RE = r"[A-Za-z0-9_-]{6,}"
LINK_KEYS = ("team", "plan", "library", "module", "case")


def parse_link(text: str) -> dict:
    """把 ONES 链接（或裸 uuid）解析成 {team, plan, library, module, case}。"""
    out = {}
    if not text:
        return out
    for key in LINK_KEYS:
        m = re.search(rf"/{key}/({UUID_RE})", text)
        if m:
            out[key] = m.group(1)
    for key in ("caseUuid", "case_uuid", "planUuid", "plan_uuid",
                "moduleUuid", "module_uuid", "libraryUuid"):
        m = re.search(rf"[?&#]{key}=({UUID_RE})", text)
        if m:
            out.setdefault(key.split("_")[0].replace("Uuid", ""), m.group(1))
    if not out and re.fullmatch(UUID_RE, text.strip()):
        out["case"] = text.strip()
    return out


# ---------------------------------------------------------------------------
# shaping
# ---------------------------------------------------------------------------

def _num_to_id(meta: dict) -> str:
    if meta.get("id"):
        return meta["id"]
    n = meta.get("number")
    return f"T{n}" if n else ""


def shape_case(meta: dict, steps: list, module_names: dict) -> dict:
    pri = meta.get("priority", "")
    if isinstance(pri, dict):
        pri = pri.get("uuid", "")
    typ = meta.get("type", "")
    if isinstance(typ, dict):
        typ = typ.get("uuid", "")
    mod = meta.get("testcaseModule") or {}
    mod_uuid = mod.get("uuid") or meta.get("module_uuid", "")
    shaped_steps = []
    for i, s in enumerate(steps or [], 1):
        if isinstance(s, str):
            shaped_steps.append({"index": i, "desc": s, "result": ""})
        else:
            shaped_steps.append({
                "index": i,
                "desc": s.get("desc", ""),
                "result": s.get("result", ""),
                "execute_result": s.get("execute_result", ""),
                "actual_result": s.get("actual_result", ""),
            })
    return {
        "id": _num_to_id(meta),
        "uuid": meta.get("uuid", ""),
        "name": meta.get("name", ""),
        "module": module_names.get(mod_uuid) or mod.get("name") or mod_uuid,
        "module_uuid": mod_uuid,
        "priority": PRIORITY_NAMES.get(pri, pri),
        "type": TYPE_NAMES.get(typ, typ),
        "condition": meta.get("condition", ""),
        "desc": meta.get("desc", ""),
        "steps": shaped_steps,
    }


def to_markdown(result: dict) -> str:
    src = result["source"]
    lines = [f"# ONES 用例清单 — {src.get('raw') or '(uuid 直取)'}", ""]
    lines.append(f"- 库：{result.get('library_name', '')} (`{src.get('library', '')}`)")
    if src.get("plan"):
        lines.append(f"- 计划：`{src['plan']}`")
    if src.get("module"):
        lines.append(f"- 模块：`{src['module']}`")
    lines.append(f"- 拉取时间：{result['fetched_at']}    用例数：{result['count']}")
    lines.append("")
    for c in result["cases"]:
        lines.append(f"## [{c['id']}] {c['name']}")
        lines.append("")
        lines.append(f"- 模块：{c['module']}    优先级：{c['priority']}    类型：{c['type']}    uuid：`{c['uuid']}`")
        if c["condition"]:
            lines.append(f"- 前置条件：{c['condition']}")
        if c["desc"]:
            lines.append(f"- 说明：{c['desc']}")
        lines.append("")
        if c["steps"]:
            lines.append("| # | 步骤 | 预期结果 |")
            lines.append("|---|------|----------|")
            for s in c["steps"]:
                d = s["desc"].replace("|", "\\|").replace("\n", " ")
                r = s["result"].replace("|", "\\|").replace("\n", " ")
                lines.append(f"| {s['index']} | {d} | {r} |")
        else:
            lines.append("_（无步骤）_")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="读取 ONES 测试用例（链接 / 计划 / 模块 / 单条）为 JSON 或 Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("link", nargs="?", help="ONES 用例/计划/模块链接，或裸 uuid")
    ap.add_argument("--plan", help="测试计划 uuid")
    ap.add_argument("--module", help="模块 uuid")
    ap.add_argument("--case", help="用例 uuid，多个用逗号分隔")
    ap.add_argument("--library", help="覆盖库 uuid")
    ap.add_argument("--grep", help="按用例名/前置/说明/步骤内容过滤（不区分大小写）")
    ap.add_argument("--limit", type=int, help="最多输出多少条用例")
    ap.add_argument("--out", help="JSON 输出路径（默认只打印摘要到 stdout）")
    ap.add_argument("--markdown", nargs="?", const="-", help="输出 Markdown（可跟路径）")
    ap.add_argument("--json", action="store_true", dest="dump_json", help="JSON 打印到 stdout")
    ap.add_argument("--list-modules", action="store_true", help="只打印库内模块树")
    ap.add_argument("--no-detail", action="store_true", help="不取步骤（快，steps 为空）")
    ap.add_argument("--no-refresh", action="store_true", help="token 失效时不自动重登刷新")
    args = ap.parse_args()

    src = parse_link(args.link or "")
    for k in ("plan", "module", "case", "library"):
        if getattr(args, k):
            src[k] = getattr(args, k)
    src["raw"] = args.link or ""

    env = load_env()
    client = OnesClient(env)
    if src.get("library"):
        client.library = src["library"]
    if not client.token or not client.check_token():
        if args.no_refresh:
            print("ONES token 已失效；先执行：py -3.9 tools/ones_writer.py refresh-token",
                  file=sys.stderr)
            sys.exit(1)
        print("ONES token 失效，正在刷新（会弹出浏览器登录）...")
        client.token = refresh_token()

    if args.list_modules:
        names = client.module_names()
        print(f"库 {client.library}（{client.library_name()}）模块 {len(names)} 个：")
        for uuid, name in sorted(names.items(), key=lambda kv: kv[1]):
            print(f"  {uuid}  {name}")
        return

    module_names = client.module_names()

    # --- 1. 收集元数据 ---
    metas, steps_map = [], {}

    if src.get("case"):
        case_uuids = [u for u in re.split(r"[,\s]+", src["case"]) if u]
        for u in case_uuids:
            d = client.case_detail(u)
            if d:
                metas.append(d)
                steps_map[u] = d.get("steps") or []

    elif src.get("module"):
        metas = client.cases_by_module(src["module"])
        if metas is None:  # GraphQL 失败 → REST 全库本地过滤
            metas = [c for c in client.cases_by_library()
                     if c.get("module_uuid") == src["module"]]
        if not metas and src.get("plan"):
            plan_metas = [c for c in client.cases_by_plan(src["plan"])
                          if c.get("module_uuid") == src["module"]]
            if plan_metas:
                metas = plan_metas
            else:
                print(f"计划 {src['plan']} 与该模块无交集，已按库内模块取数", file=sys.stderr)

    elif src.get("plan"):
        metas = client.cases_by_plan(src["plan"])

    else:
        metas = client.cases_by_library()
        print(f"未指定 plan/module/case，返回整库 {len(metas)} 条（建议加 --module 或 --grep）。",
              file=sys.stderr)

    if not metas:
        print("没有取到任何用例。", file=sys.stderr)
        sys.exit(0)

    # --- 2. 批量取步骤（单条模式已在详情里带 steps） ---
    if not args.no_detail:
        need = [m["uuid"] for m in metas if not steps_map.get(m["uuid"])]
        if need:
            bulk = client.steps_bulk(need)
            if bulk is not None:
                steps_map.update(bulk)

    cases = [shape_case(m, steps_map.get(m.get("uuid", ""), []), module_names)
             for m in metas]

    if args.grep:
        kw = args.grep.lower()

        def hit(c):
            blob = " ".join([c["name"], c["condition"], c["desc"]] +
                            [f"{s['desc']} {s['result']}" for s in c["steps"]]).lower()
            return kw in blob

        cases = [c for c in cases if hit(c)]
    if args.limit:
        cases = cases[:args.limit]

    result = {
        "source": src,
        "library_name": client.library_name(),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(cases),
        "cases": cases,
    }

    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON -> {p}")
    if args.dump_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.markdown:
        md = to_markdown(result)
        if args.markdown == "-":
            print(md)
        else:
            p = Path(args.markdown)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(md, encoding="utf-8")
            print(f"Markdown -> {p}")

    if not args.out and not args.markdown and not args.dump_json:
        print(f"共 {result['count']} 条用例：")
        for c in cases:
            print(f"  [{c['id']}] {c['name'][:70]}  ({c['module']}, {c['priority']}, {len(c['steps'])} steps)")


if __name__ == "__main__":
    main()
