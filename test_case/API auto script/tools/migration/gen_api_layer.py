"""从既有用例中抽取「接口清单」，生成 ``api/`` 业务服务层。

设计要点
--------
1. **接口去重**：1203 个裸调用只落在 181 个接口上。同一个接口被调用 188 次
   （``POST /auth/sign-in``）只需一个具名方法。

2. **路径参数名不是接口身份**。实测 223 个「方法+路径」中有 42 个只是路径参数
   变量名不同，例如 ``GET /order/merchant/{x}/detail/{y}/v2`` 被拆成了
   merchantId / P1_merchantIDa / M1_merchantIDe … 共 13 个「接口」。
   归一后按**路径形状**建接口，路径参数变成**显式关键字参数**。

3. **环境解耦**。迁移前 79 处把 release 域名写死在用例里，切 Staging 就会打错环境。
   生成时统一剥掉被测主体域名，改由当前环境的 ``base_url`` / ``adminurl`` 解析。

4. **请求头归属**。实测 178/203 个接口的请求头形态稳定，因此
   ``app_headers`` / ``skip_notifications`` 固化为**方法签名默认值**；
   而 ``Authorization`` 的变量名随角色变化，保留为调用参数 ``token``。

5. **``Content-Type``** 由 :class:`~core.http_client.ApiClient` 依据「有无 JSON 请求体」
   自动补全（迁移前由 659 处手写请求头承担）。

输出：``api/<domain>.py`` + ``api/__init__.py``（门面）+ ``api_manifest.json``（清单）
"""
from __future__ import annotations

import ast
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import parse_qsl

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.migration.case_parser import parse_case  # noqa: E402

TESTS_DIR = ROOT / "tests"
API_DIR = ROOT / "api"

PEAR = {"pear-autotesting", "pear-client-id", "pear-client-secret"}
SKIP_HDR = "x-skip-notifications"
CT = "content-type"
AUTH = "authorization"

#: 这些「变量」是主机前缀而非路径参数，不参与接口身份归一
HOST_VARS = {"adminurl", "base_admin_api_url", "base_app_url"}

#: 主机变量归一（两者在 Release 下同值，且 base_app_url 等同 base_url）
HOST_VAR_ALIAS = {
    "base_admin_api_url": "adminurl",   # 指向同一后台域名
    "base_app_url": "",                 # 等同 base_url，直接剥掉
}

#: 真正的第三方依赖（仅联调用，不属于被测主体）
EXTERNAL_HOSTS = ("api.stripe.com", ".notip.com.cn")

#: 被测主体域名后缀。命中后剥掉「协议+域名」，改由环境 ``base_url`` 解析。
SUT_HOST_SUFFIX = "katana-api.1m.app"
ADMIN_HOST_MARK = "admin.katana-api.1m.app"

# --- 业务域划分（长前缀优先匹配）---------------------------------------
DOMAIN_PREFIXES = {
    "/auth": "auth",
    "/cart": "cart",
    "/address": "address",
    "/users": "users",
    "/user-link": "links",
    "/short-link": "links",
    "/user-contact-form": "misc",
    "/posts": "posts",
    "/post": "posts",
    "/order": "orders",
    "/orders": "orders",
    "/merchant-orders": "orders",
    "/product-event": "events",
    "/event-collaborators": "events",
    "/event": "events",
    "/events": "events",
    "/v2/products": "products",
    "/merchant/product": "products",
    "/merchant": "merchants",
    "/merchants": "merchants",
    "/promoter-earning": "earnings",
    "/promoter-invitation-link": "promoters",
    "/promoter-association": "promoters",
    "/promoter-subscription": "promoters",
    "/promoter": "promoters",
    "/promote-invitation": "promoters",
    "/payout": "earnings",
    "/earnings": "earnings",
    "/sales": "earnings",
    "/campaigns": "campaigns",
    "/payment": "payments",
    "/analytics": "analytics",
    "/tracking": "analytics",
    "/purchase-approvals": "approvals",
    "/store-front": "storefront",
}
_PREFIX_ORDER = sorted(DOMAIN_PREFIXES, key=len, reverse=True)

DOMAIN_TITLES = {
    "auth": "鉴权（登录 / 注册 / 验证码）",
    "cart": "购物车",
    "address": "收货地址",
    "users": "用户与账户",
    "orders": "订单（下单 / 结算 / 履约 / 退款）",
    "posts": "帖子（策展人 / 消费者 / 推广者）",
    "events": "活动与票务",
    "products": "商品",
    "merchants": "商户",
    "promoters": "推广者与分销",
    "earnings": "收益与结算",
    "campaigns": "营销活动",
    "payments": "支付方式",
    "analytics": "埋点与统计",
    "approvals": "采购审批",
    "storefront": "店铺装修",
    "links": "短链与用户链接",
    "admin": "管理后台接口（{{adminurl}}）",
    "app": "前端站点接口（{{base_app_url}}）",
    "external": "外部依赖（Stripe 等，仅联调）",
    "misc": "其它",
}

RE_BRACE = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
RE_INNER_VAR = re.compile(r"\{([^{}]+)\}")
RE_URL = re.compile(r"^(https?)://([^/]+)(/.*)?$")
#: 畸形占位符判定：``{{`` 后面还嵌着 ``{``（如 ``{l{lineup_id}}``）。
#: 模板引擎不会匹配它，原样发到服务端 —— 属迁移遗留缺陷。生成时**保持原样**并单独标记，
#: 不做静默「修复」，以免改变既有行为。
RE_PY_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def has_malformed(path: str) -> bool:
    """判断路径是否含畸形占位符。

    做法：先归一 ``{{x}}`` -> ``{x}``，再剔除所有合法占位符，
    若仍残留花括号则说明存在嵌套畸形。
    """
    residue = RE_INNER_VAR.sub("", unbrace(path))
    return "{" in residue or "}" in residue


# --- 路径归一 -----------------------------------------------------------
def unbrace(path: str) -> str:
    """``{{ x }}`` -> ``{x}``（去掉内部空格，统一单花括号形态）。"""
    return RE_BRACE.sub(r"{\1}", path)


def host_normalize(path: str) -> str:
    """剥掉被测主体域名 / 归一主机变量，使路径与环境解耦。"""
    for alias, target in HOST_VAR_ALIAS.items():
        path = path.replace("{{" + alias + "}}", "{{" + target + "}}" if target else "")
        path = path.replace("{" + alias + "}", "{" + target + "}" if target else "")

    m = RE_URL.match(path)
    if not m:
        return path
    host, rest = m.group(2), m.group(3) or "/"
    if any(h in host for h in EXTERNAL_HOSTS):
        return path
    if ADMIN_HOST_MARK in host:
        return "{{adminurl}}" + rest
    if host.endswith(SUT_HOST_SUFFIX):
        return rest
    return path


def canonicalize(path: str) -> str:
    """归一为「接口身份」：路径参数一律记作 ``{*}``，主机变量保留。"""
    path = unbrace(path)
    base, _ = split_query(path)

    def _sub(m):
        name = m.group(1)
        if name in HOST_VARS:
            return "{{" + name + "}}"
        return "{*}"

    return RE_INNER_VAR.sub(_sub, base)


def split_query(path: str) -> tuple[str, str]:
    if "?" in path:
        base, q = path.split("?", 1)
        return base, q
    return path, ""


def parse_query(q: str) -> dict:
    out: dict = {}
    for k, v in parse_qsl(q, keep_blank_values=True):
        out.setdefault(k, v)
    return out


def path_vars_of(path: str) -> list[str]:
    """按出现顺序取出路径参数名（排除主机变量）。"""
    return [n for n in RE_INNER_VAR.findall(unbrace(path))
            if n not in HOST_VARS and not n.startswith("*")]


def to_ident(name: str) -> str:
    """把路径参数名转成合法的 Python 标识符（``co-hostid`` -> ``co_hostid``）。"""
    out = re.sub(r"[^0-9A-Za-z_]+", "_", name).strip("_")
    if not out:
        out = "id"
    if out[0].isdigit():
        out = "v_" + out
    return out


def domain_of(path: str) -> tuple[str, str]:
    base, _ = split_query(path)
    segs = [s for s in base.split("/") if s]

    m = RE_URL.match(base)
    if m:
        host, rest = m.group(2), m.group(3) or "/"   # group(1)=协议, group(2)=主机
        if any(h in host for h in EXTERNAL_HOSTS):
            return "external", rest
        return _domain_by_prefix(rest)

    if segs and segs[0].startswith("{{"):
        var = segs[0].strip("{} ")
        dom = {"adminurl": "admin", "base_app_url": "app"}.get(var, "misc")
        return dom, "/" + "/".join(segs[1:]) if len(segs) > 1 else "/"

    return _domain_by_prefix(base)


def _domain_by_prefix(path: str) -> tuple[str, str]:
    for pref in _PREFIX_ORDER:
        if path == pref or path.startswith(pref + "/"):
            return DOMAIN_PREFIXES[pref], path[len(pref):]
    return "misc", path


# --- 方法命名 -----------------------------------------------------------
_VERB_BY_METHOD = {"GET": "list", "POST": "create", "PUT": "update",
                   "PATCH": "patch", "DELETE": "delete"}


def method_name(rest: str, method: str) -> str:
    base, _ = split_query(unbrace(rest))
    segs = [s for s in base.split("/") if s]
    if not segs:
        return _VERB_BY_METHOD.get(method, "call")

    parts: list[str] = []
    for i, s in enumerate(segs):
        inner = RE_INNER_VAR.fullmatch(s)
        if inner:
            var = inner.group(1)
            if var in HOST_VARS:
                parts.append(var)
            elif i == len(segs) - 1:
                parts.append("by_" + _snake(var))
        else:
            parts.append(_snake(s))
    name = "_".join(p for p in parts if p) or "call"
    return ("v_" + name) if name[0].isdigit() else name


def _snake(text: str) -> str:
    text = RE_INNER_VAR.sub(lambda m: "_" + m.group(1) + "_", text)
    text = re.sub(r"[^0-9A-Za-z]+", "_", text)
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", text)
    return re.sub(r"_+", "_", text).strip("_").lower()


# --- 扫描 ---------------------------------------------------------------
def scan() -> dict:
    """扫描全部用例，汇总接口画像。"""
    endpoints: dict = defaultdict(lambda: {
        "count": 0, "app_headers": Counter(), "skip": Counter(),
        "tokens": Counter(), "queries": Counter(), "files": set(),
        "var_choices": defaultdict(Counter),   # 位置 -> 变量名频次
        "paths": Counter(), "malformed": False,
    })

    for f in sorted(TESTS_DIR.rglob("test_*.py")):
        try:
            pc = parse_case(f, TESTS_DIR)
        except Exception as exc:  # pragma: no cover
            print(f"  [解析失败] {f.name}: {exc}")
            continue
        for op in pc.ops:
            if op.kind != "request":
                continue
            try:
                path_str = ast.literal_eval(op.path_expr)
            except Exception:
                continue
            if not isinstance(path_str, str):
                continue

            path_n = unbrace(host_normalize(path_str))
            base, query = split_query(path_n)
            if has_malformed(path_str):
                # 畸形占位符：原样保留，不做归一（避免改变既有行为）
                key = (op.method.upper(), path_str)
            else:
                key = (op.method.upper(), canonicalize(path_n))
            e = endpoints[key]
            e["malformed"] = e["malformed"] or has_malformed(path_str)
            e["count"] += 1
            e["paths"][base] += 1
            e["files"].add(f.name)
            if query:
                e["queries"][query] += 1

            if not e["malformed"]:
                for pos, var in enumerate(path_vars_of(base)):
                    e["var_choices"][pos][var] += 1

            try:
                hdrs = ast.literal_eval(op.headers_expr) if op.headers_expr else {}
            except Exception:
                hdrs = {}
            if not isinstance(hdrs, dict):
                hdrs = {}
            low = {str(k).lower(): str(v) for k, v in hdrs.items()}
            e["app_headers"][any(k in PEAR for k in low)] += 1
            e["skip"][SKIP_HDR in low] += 1
            if AUTH in low:
                e["tokens"][low[AUTH]] += 1

    return endpoints


# --- 代码生成 -----------------------------------------------------------
def _majority(counter: Counter, fallback=False):
    return counter.most_common(1)[0][0] if counter else fallback


def _canonical_path(template: str, e: dict) -> tuple[str, list]:
    """把 ``{*}`` 占位换回「该位置最常见」的变量名，得到方法内的标准路径。

    Returns:
        (标准路径模板, [{"arg": 形参名, "var": 模板变量名}, ...])
    """
    names = [e["var_choices"][pos].most_common(1)[0][0]
             for pos in sorted(e["var_choices"])]

    idx = 0
    used: dict = {}

    def _sub(m):
        nonlocal idx
        if m.group(1) != "*":
            return m.group(0)
        var = names[idx] if idx < len(names) else "id"
        idx += 1
        arg = to_ident(var)
        # 形参名去重（不同变量名可能规范化后撞名）
        if arg in used:
            n = 2
            while f"{arg}_{n}" in used:
                n += 1
            arg = f"{arg}_{n}"
        used[arg] = var
        return "{{" + var + "}}"

    path = RE_INNER_VAR.sub(_sub, template)
    params = [{"arg": a, "var": v} for a, v in used.items()]
    return path, params


def gen_module(domain: str, items: list) -> str:
    title = DOMAIN_TITLES.get(domain, domain)
    cls = domain.title().replace("_", "") + "Api"
    lines = [
        f'"""{domain} —— {title}。',
        "",
        "由 ``tools/migration/gen_api_layer.py`` 从既有用例抽取生成，描述**接口事实**",
        "（方法 / 路径 / 路径参数 / 默认请求头），不含任何用例场景。",
        "新增或调整接口请直接编辑本文件。",
        '"""',
        "from __future__ import annotations",
        "",
        "from api.base import BaseApi, _pv",
        "",
        "",
        f"class {cls}(BaseApi):",
        f'    """{title}。"""',
        "",
        f'    domain = "{domain}"',
        "",
    ]
    for it in items:
        pparams = it["path_params"]
        lines.append(f"    def {it['name']}(")
        lines.append("        self, *,")
        if pparams:
            lines.append(f"        {', '.join(p['arg'] + '=None' for p in pparams)},")
        lines.append("        body=None, token=None, params=None, headers=None,")
        lines.append(f"        app_headers={it['app_headers']!r}, skip_notifications={it['skip']!r},")
        lines.append("        path_vars=None,")
        lines.append("    ):")
        doc = f'        """{it["method"]} {it["path"]}'
        if it["count"] > 1:
            doc += f'  （用例中出现 {it["count"]} 次）'
        if it["malformed"]:
            doc += "\n\n        .. warning:: 路径含畸形占位符（迁移遗留），已原样保留。"
        if it["path"].startswith("http"):
            doc += ("\n\n        .. warning:: 该接口的域名写死在路径里（迁移遗留），"
                    "切换环境时需要一并修改；建议后续改为环境变量。")
        doc += '"""'
        lines.append(doc)
        lines.append("        return self._call(")
        lines.append(f'            "{it["method"]}", {it["path"]!r},')
        if pparams:
            pairs = ", ".join(f'("{p["var"]}", {p["arg"]})' for p in pparams)
            lines.append(f"            path_vars=_pv({pairs}, extra=path_vars),")
        else:
            lines.append("            path_vars=path_vars,")
        lines.append("            params=params,")
        lines.append("            body=body, token=token, headers=headers,")
        lines.append("            app_headers=app_headers, skip_notifications=skip_notifications,")
        lines.append("        )")
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def main():
    print("扫描用例 ...")
    endpoints = scan()
    print(f"  归一去重后接口 {len(endpoints)} 个")

    by_domain: dict = defaultdict(list)
    malformed_count = 0
    for (method, canon), e in endpoints.items():
        # 先还原路径参数名，再据此推导业务域与方法名
        path, pparams = _canonical_path(canon, e)
        dom, rest = domain_of(path)
        query = e["queries"].most_common(1)[0][0] if e["queries"] else ""
        if e["malformed"]:
            malformed_count += e["count"]
        by_domain[dom].append({
            "method": method,
            "path": path,
            "name": method_name(rest, method),
            "count": e["count"],
            "path_params": pparams,
            "malformed": e["malformed"],
            "app_headers": _majority(e["app_headers"], False),
            "skip": _majority(e["skip"], False),
            "tokens": e["tokens"],
            "query": query,
            "params": parse_query(query) if query else {},
            "files": e["files"],
        })
    if malformed_count:
        print(f"  [注意] {malformed_count} 处调用含畸形占位符，已原样保留（见下方报告）")

    # 方法名去重
    total = 0
    for dom, items in by_domain.items():
        used: dict = {}
        for it in sorted(items, key=lambda x: (-x["count"], x["path"])):
            name = it["name"]
            if name in used:
                n = 2
                while f"{name}_{n}" in used:
                    n += 1
                it["name"] = f"{name}_{n}"
            used[it["name"]] = it
        items[:] = sorted(used.values(), key=lambda x: x["name"])
        total += len(items)

    API_DIR.mkdir(exist_ok=True)
    manifest = {}
    for dom in sorted(by_domain):
        items = by_domain[dom]
        (API_DIR / f"{dom}.py").write_text(gen_module(dom, items), encoding="utf-8")
        manifest[dom] = {
            "class": dom.title().replace("_", "") + "Api",
            "methods": [
                {"name": i["name"], "method": i["method"], "path": i["path"],
                 "calls": i["count"], "path_params": i["path_params"],
                 "app_headers": i["app_headers"], "skip_notifications": i["skip"],
                 # 用例中出现过的查询串，**仅作参考**：查询串属于调用侧数据
                 # （含分页、搜索词、甚至一次性令牌），不写进方法默认值。
                 "query": i["query"], "params": i["params"]}
                for i in items
            ],
        }
        print(f"  api/{dom}.py  {len(items):3d} 个接口")

    write_init(manifest)
    (ROOT / "tools" / "migration" / "api_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n合计 {total} 个具名接口方法，{len(manifest)} 个业务域模块")
    print("  清单 -> tools/migration/api_manifest.json")


def write_init(manifest: dict) -> None:
    lines = [
        '"""业务服务层（被测系统的接口语义）。',
        "",
        "用例通过 ``ctx.api`` 访问各业务域，例如::",
        "",
        '    ctx.api.auth.sign_in(body=..., token=None)',
        '    ctx.api.orders.promoter_detail(promoterOrderId=ctx["P1_OrderId"])',
        "",
        "本层只描述**接口**，场景留在 ``tests/`` 里。",
        '"""',
        "from __future__ import annotations",
        "",
        "from api.base import BaseApi",
    ]
    for dom in sorted(manifest):
        lines.append(f"from api.{dom} import {manifest[dom]['class']}")
    lines += ["", "__all__ = [", '    "Api",', '    "BaseApi",']
    for dom in sorted(manifest):
        lines.append(f'    "{manifest[dom]["class"]}",')
    lines += ["]", "", "", "class Api:", '    """业务服务门面：``ctx.api.<domain>.<method>()``。"""', ""]
    lines += [
        "    def __init__(self, client, ctx):",
        "        self._client = client",
        "        self._ctx = ctx",
        "        self._cache = {}",
        "",
        "    def _svc(self, key, cls):",
        "        if key not in self._cache:",
        "            self._cache[key] = cls(self._client, self._ctx)",
        "        return self._cache[key]",
        "",
    ]
    for dom in sorted(manifest):
        n = len(manifest[dom]["methods"])
        lines += [
            "    @property",
            f"    def {dom}(self) -> {manifest[dom]['class']}:",
            f'        """{DOMAIN_TITLES.get(dom, dom)}（{n} 个接口）。"""',
            f'        return self._svc("{dom}", {manifest[dom]["class"]})',
            "",
        ]
    lines += [
        "    # --- 逃生口 ---------------------------------------------------",
        "    def call(self, method: str, path: str, **kw):",
        '        """直接调用未封装接口（新增接口请优先补进对应业务域模块）。"""',
        "        return self._client.request(method, path, **kw)",
        "",
    ]
    (API_DIR / "__init__.py").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
