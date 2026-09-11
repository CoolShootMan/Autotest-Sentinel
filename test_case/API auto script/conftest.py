"""pytest 配置 —— 组合根（composition root）。

职责
----
1. 装配三层框架：``config``（环境变量装载）→ ``core``（HTTP 客户端 / 上下文 / 断言）
   → ``api``（业务服务门面），并以 ``ctx`` fixture 注入用例。
2. 用例筛选（沿用既有入口）：
   - pytest 原生：目录 / ``-k`` / node id / ``-m`` marker
   - 自定义选项：``--case-ids`` / ``--folder`` / ``--tags`` / ``--list-cases``
   - 套件文件：  ``python run_suite.py suites/smoke.yaml``
3. 运行归档（默认开启，见 ``core/run_archive.py``）::

       results/runs/<run_id>/   summary.md · failures.json · meta.json · junit.xml · http.log
       results/latest           符号链接 → 最近一次运行目录
       results/http.log         符号链接 → 最近一次运行的 HTTP 报文
       results/RUNS.md          运行历史索引（一次运行一行）

   ``--run-label <name>`` 给本次运行打标签（``run_suite.py`` 自动传入套件名），
   ``--no-archive`` 关闭归档（HTTP 日志回到旧的全局 ``results/http.log``）。
   ``--collect-only`` / ``--list-cases`` 不产生归档。

自动 marker（来自 case_index 扫描）：
  ``folder_<slug>``、``p<priority>``、``case_<id>``（Apifox 溯源，仅标识用）。

用例通过 ``ctx`` 获得全部能力::

    def test_xxx(ctx):
        resp = ctx.api.auth.sign_in(body=...)
        expect(resp).json("$.code").equals("200")
        ctx.extract("token", resp, "$.data.token")

``ctx`` 同时是 ``MutableMapping``——用例里 ``vars['x']`` / ``vars.get('x')``
等手写逻辑无需改动（迁移兼容约定 ``vars = ctx``）。
"""
from pathlib import Path

import pytest

import case_index as ci
from api import Api
from config import env_loader
from core import run_archive, token_refresh
from core.context import Context
from core.http_client import ApiClient

ROOT = Path(__file__).parent
_ENTRIES = ci.scan_tests()
_BY_PATH = {e["path"]: e for e in _ENTRIES}
_BY_FUNC = {e["func"]: e for e in _ENTRIES if e.get("func")}

#: 默认环境；用例模块可声明自己的 ``ENV_NAME`` 覆盖
ENV_NAME = "Release"


def _entry_of(item):
    # match by collected path then by function name
    p = getattr(item, "path", None) or getattr(item, "fspath", None)
    if p is not None:
        try:
            rel = Path(str(p)).resolve().relative_to(ROOT.resolve())
            e = _BY_PATH.get(str(rel))
            if e:
                return e
        except (ValueError, OSError):
            pass
    return _BY_FUNC.get(item.name, {})


def _entry_of_nodeid(nodeid: str) -> dict:
    """从 ``tests/<...>/test_x.py::test_y`` 反查 case_index 条目（归档报告用）。"""
    path_part, _, func = (nodeid or "").partition("::")
    if path_part:
        try:
            rel = str(Path(path_part).resolve().relative_to(ROOT.resolve()))
            e = _BY_PATH.get(rel)
            if e:
                return e
        except (ValueError, OSError):
            pass
        suffix = "/" + path_part
        for key, e in _BY_PATH.items():           # 兜底：rootdir 与 nodeid 前缀不一致时
            if key.endswith(suffix):
                return e
    return _BY_FUNC.get(func, {})


# --- 组合根 -------------------------------------------------------------
@pytest.fixture(scope="module")
def ctx(request):
    """单用例模块的变量上下文 + HTTP 客户端 + 业务服务门面。

    变量四层合并（高者覆盖低者）::

        Global.yaml → <ENV_NAME>.yaml → _runtime_tokens.yaml → <case>.vars.yaml

    ``ENV_NAME`` 取用例模块声明，缺省 ``Release``。
    """
    env_name = getattr(request.module, "ENV_NAME", None) or ENV_NAME
    case_file = Path(str(getattr(request, "path", None)
                         or getattr(request, "fspath", None)))
    data = env_loader.load_case_vars(case_file, env_name)

    context = Context(
        data["base_url"], data["variables"],
        env_name=env_name, case_vars_file=data.get("case_vars_file", ""),
    )
    client = ApiClient(data["base_url"], ctx=context)
    context.client = client
    context.api = Api(client, context)
    return context


@pytest.fixture(autouse=True)
def _ensure_runtime_tokens(ctx, request):
    """每条用例执行前，按需续期它引用的角色 token。

    后端签发的角色 JWT 只有 120 秒寿命，而回归集跑完远超此窗口；不续期的话，
    排在后面的用例会拿过期 token 请求并收到 403，表现为「响应体里没有 code」。
    详见 :mod:`core.token_refresh`。
    """
    source = getattr(request, "path", None) or getattr(request, "fspath", None)
    token_refresh.ensure_fresh(ctx, source_file=source)
    yield


@pytest.fixture(scope="module")
def _ctx(ctx):
    """旧签名兼容垫片：仍以 dict 形态访问的遗留代码使用。"""
    return {"client": ctx.client, "base_url": ctx.base_url, "vars": ctx}


# --- 命令行选项 ---------------------------------------------------------
def pytest_addoption(parser):
    group = parser.getgroup("apifox")
    group.addoption(
        "--case-ids", action="store", default=None,
        help="Run only these case ids OR func slugs (comma separated), e.g. --case-ids 6112669,Linda_T917_Verify_...",
    )
    group.addoption(
        "--folder", action="store", default=None,
        help="Run only cases whose folder path contains this text, e.g. --folder 'Login flow'",
    )
    group.addoption(
        "--tags", action="store", default=None,
        help="Run only cases whose tags include ALL of these (comma separated), e.g. --tags p0,account",
    )
    group.addoption(
        "--list-cases", action="store_true", default=False,
        help="Print the collected cases (folder, name, tags) and exit without running.",
    )
    group.addoption(
        "--run-label", action="store", default=None,
        help="Tag this run, e.g. --run-label linda → results/runs/<ts>_linda/",
    )
    group.addoption(
        "--no-archive", action="store_true", default=False,
        help="Disable per-run archiving (results/runs/<run_id>/); HTTP log falls back "
             "to the legacy results/http.log.",
    )


# --- 运行归档 -----------------------------------------------------------
# 每次运行独占 results/runs/<run_id>/，内含 summary.md / failures.json /
# meta.json / junit.xml / http.log。见 core/run_archive.py，--no-archive 可关闭。
@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    if getattr(config, "workerinput", None) is not None:
        return                                    # xdist worker 不归档（master 负责）
    if config.option.collectonly or config.getoption("--list-cases"):
        return                                    # 只收集 / 只列用例：不产生归档
    if config.getoption("--no-archive"):
        run_archive.detach()                      # 回到全局 results/http.log
        return
    args = list(getattr(config.invocation_params, "args", None) or [])
    run_dir = run_archive.begin(config.getoption("--run-label"), args)
    if not getattr(config.option, "xmlpath", None):   # 用户显式 --junitxml 时尊重用户
        config.option.xmlpath = str(run_dir / "junit.xml")


def pytest_runtest_logreport(report):
    """Snapshot http.log growth per test so failure attribution stays exact.

    ``run_archive.finish`` runs at session end; without this snapshot every
    failure would report the last request of the whole run.
    """
    if not run_archive.active():
        return
    if getattr(report, "when", "") == "call":
        run_archive.mark_test_end(report.nodeid)


def pytest_sessionfinish(session, exitstatus):
    if not run_archive.active():
        return
    run_archive.finish(
        session.config, session,
        session.config.pluginmanager.get_plugin("terminalreporter"),
        _entry_of_nodeid,
    )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    line = run_archive.summary_line()
    if line:
        terminalreporter.write_sep("-", "run archive")
        terminalreporter.write_line(line)


def pytest_collection_modifyitems(config, items):
    ids_opt = config.getoption("--case-ids")
    folder_opt = config.getoption("--folder")
    tags_opt = config.getoption("--tags")
    list_only = config.getoption("--list-cases")

    wanted_ids = {x.strip() for x in ids_opt.split(",") if x.strip()} if ids_opt else None
    wanted_tags = [t.strip() for t in tags_opt.split(",") if t.strip()] if tags_opt else None

    kept = []
    for item in items:
        e = _entry_of(item)
        folder = e.get("folder", "")
        tags = e.get("tags", [])
        case_id = e.get("case_id")

        # --- auto markers ------------------------------------------------
        if case_id is not None:
            item.add_marker(getattr(pytest.mark, f"case_{case_id}"))
        if folder:
            item.add_marker(getattr(pytest.mark, f"folder_{ci.slug(folder)}"))
        prio = e.get("priority")
        if prio is not None:
            item.add_marker(getattr(pytest.mark, f"p{prio}"))

        # --- filtering ---------------------------------------------------
        if wanted_ids is not None:
            hit = (case_id is not None and str(case_id) in wanted_ids) or \
                  (e.get("func") and e["func"] in wanted_ids) or \
                  (e.get("slug") and e["slug"] in wanted_ids)
            if not hit:
                continue
        if folder_opt and folder_opt.lower() not in folder.lower():
            continue
        if wanted_tags and not all(t in tags for t in wanted_tags):
            continue
        kept.append(item)

    # Sort selected cases to match the Apifox sidebar order (case_sort_key from case_index)
    def _sort_key(item):
        e = _entry_of(item)
        return e.get("case_sort_key", [99999])

    kept.sort(key=_sort_key)

    if wanted_ids is not None or folder_opt or wanted_tags:
        print(f"[select] selected {len(kept)}/{len(items)} case(s)")

    if list_only:
        print("\n{:<42}  {:<40}  {}".format("FOLDER", "NAME", "TAGS"))
        print("-" * 120)
        for item in kept:
            e = _entry_of(item)
            print("{:<40}  {:<38}  {}".format(
                (e.get("folder") or "-")[:40],
                (e.get("name") or item.name)[:38],
                ",".join(e.get("tags", []))[:50],
            ))
        print(f"\n{len(kept)} case(s) selected\n")
        items[:] = []
        return

    items[:] = kept
