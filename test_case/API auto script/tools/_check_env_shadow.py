"""检查 env 分层里的「空值遮蔽」—— Global.yaml 有值、但 <ENV>.yaml 用空串盖掉。

分层优先级: Global < <ENV>.yaml < _runtime_tokens.yaml < <case>.vars.yaml
所以 <ENV>.yaml 里任何 `KEY: ''` 都会把 Global.yaml 里同名键的真实值抹掉。
这类 bug 表现为「变量存在、但发出去是空串 / 字面量」，很难从报错看出。

用法:
    python tools/_check_env_shadow.py [ENV_NAME] [CASE_FILE]
默认 ENV_NAME=Release，CASE_FILE=主脚本 00_UI Prefill。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = ROOT / "config" / "environments"
DEFAULT_CASE = ROOT / "tests" / "00_UI Prefill" / "test_ui_prefill_data_configuration.py"

PH = re.compile(r"\{\{\s*([A-Za-z_][\w]*)\s*\}\}")


def _vars(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return dict(data.get("variables") or {})


def _is_empty(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip() == "")


def main() -> int:
    env_name = sys.argv[1] if len(sys.argv) > 1 else "Release"
    case_file = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_CASE

    g = _vars(ENV_DIR / "Global.yaml")
    e = _vars(ENV_DIR / f"{env_name}.yaml")
    rt = _vars(ENV_DIR / "_runtime_tokens.yaml")
    cv = _vars(case_file.with_name(case_file.stem + ".vars.yaml")) if case_file.exists() else {}

    rc = 0

    # --- 1. 空值遮蔽 ---------------------------------------------------
    shadowed = sorted(k for k in e if k in g and _is_empty(e[k]) and not _is_empty(g[k]))
    print(f"[1] {env_name}.yaml 用空串遮蔽 Global.yaml 真实值的键: {len(shadowed)}")
    for k in shadowed:
        print(f"    !! {k}: Global={g[k]!r}  ->  被 {env_name}='' 覆盖")
    if shadowed:
        rc = 1

    # --- 2. 主脚本占位符解析结果 --------------------------------------
    if case_file.exists():
        merged = {}
        merged.update(g)
        merged.update(e)
        merged.update(rt)
        merged.update(cv)
        refs = sorted(set(PH.findall(case_file.read_text(encoding="utf-8"))))
        missing = [n for n in refs if n not in merged]
        empty = [n for n in refs if n in merged and _is_empty(merged[n])]
        print(f"\n[2] 主脚本引用占位符: {len(refs)} 个")
        print(f"    未定义(连键都没有): {len(missing)}  {missing if missing else ''}")
        print(f"    定义但为空(运行时产出/或缺失): {len(empty)}")
        if empty:
            print(f"    {empty}")
        print(f"\n[3] 关键变量最终解析值 (Global+{env_name}+runtime+case):")
        for n in ("UIauto_partner_email", "UIauto_coseller_email", "UIauto_partner997_email",
                  "UIauto_consumer_email", "partner_vanityUrl", "partner_storeName",
                  "coseller_storeName", "coseller_vanityUrl", "partner997_vanityUrl",
                  "partner997_storeName", "release_sql_address", "release_sql_name"):
            src = ("case.vars" if n in cv else f"{env_name}" if n in e else
                   "_runtime" if n in rt else "Global")
            flag = ""
            if n in e and n in g and _is_empty(e[n]) and not _is_empty(g[n]):
                flag = "  <== 被遮蔽!"
            print(f"      {n:32s} = {merged.get(n, '<未定义>')!r:36s} [{src}]{flag}")
    else:
        print(f"\n[2] 主脚本不存在: {case_file}")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
