"""运行期令牌按需续期。

背景
----
``Linda_T0000_Precondition_obtain_all_accounts_token`` 会登录 9 个账号，把 JWT 写进
``config/environments/_runtime_tokens.yaml``，后续用例通过 ``token='linda01_token'``
之类的写法引用。

但后端签发的这批 JWT **有效期只有 120 秒**（``exp - iat == 120``）。整个回归集跑完
远超这个窗口，于是排在后面的用例拿着过期 token 发请求，被后端挡回::

    HTTP 403 {"message": "For your security, please log in again to continue."}

由于 403 响应体不是业务 JSON，``json_safe()`` 返回 ``{}``，断言只能看到 ``code=None``，
表象上很像「响应体断言在迁移中丢了」，实际是**鉴权过期**。

做法
----
在每条用例执行前做一次「按需续期」：

1. 从用例源码里扫出它引用了哪些角色 token（正则匹配 ``*_token``）；
2. 解析这些 token 的 ``exp``，只对「已过期 / 剩余寿命不足 ``threshold`` 秒」的做续期；
3. 用 T0000 私有变量层里登记的账号密码重新登录，回写 ``ctx`` 与运行期令牌文件。

未引用 token 的用例（纯只读、无需鉴权的）完全跳过，不产生额外请求；
token 仍然新鲜时也跳过，因此平均每 1~2 分钟才补一次。

令牌别名
--------
迁移后的用例里存在一批「名字不同、账号相同」的令牌，它们没有任何赋值来源
（``Release.yaml`` 里是空串），直接把空值发出去会被后端判成未登录：

============================  ==============================  ==========================
用例里使用的名字                 实际签发账号                       同账号的主令牌
============================  ==============================  ==========================
``merchant_token``            ``linda.zhou.ext+00@1m.app``     ``linda00_token``
``consumer_token``            ``linda.zhou.ext+10@1m.app``     ``linda10_token``
============================  ==============================  ==========================

实测同账号签发的 JWT 在 ``app_headers`` 开关下 claims 完全一致（``userId`` /
``userRole`` / ``userType`` / 120 秒寿命），因此 :data:`ALIASES` 让别名**直接复用**
主令牌，而不是再登录一次——既补齐了缺口，又不会把登录请求量顶上去
（服务端对重复登录有 ``Too many failed attempts`` 限流）。
"""
from __future__ import annotations

import base64
import json
import logging
import re
import time
from pathlib import Path
from typing import Any

from config import env_loader, settings

_log = logging.getLogger("api.framework")

#: 角色 token -> 登录配方。``email`` / ``password`` 是**变量名**，
#: 取值来自 T0000 的私有变量层（``*.vars.yaml``）与环境层。
RECIPES: dict[str, dict[str, Any]] = {
    "admin_token":     {"email": "admin_email",           "password": "adminpassword", "admin": True},
    "linda00_token":   {"email": "p00_email",             "password": "password"},
    "linda01_token":   {"email": "p01_email",             "password": "password"},
    "linda05_token":   {"email": "p05_email",             "password": "password"},
    "xuan22_token":    {"email": "xuan_email",            "password": "xuan_password"},
    "linda06_token":   {"email": "p06_email",             "password": "password"},
    "linda10_token":   {"email": "p10_email",             "password": "password"},
    "yuxiao999_token": {"email": "UIauto_partner_email",  "password": "password",      "app_headers": True},
    "yuxiao998_token": {"email": "UIauto_coseller_email", "password": "password",      "app_headers": True},
}

#: 与已有配方**同账号**的令牌别名（别名 -> 主令牌）。
#:
#: 它们没有独立配方，而是复用主令牌的 JWT——见模块文档「令牌别名」一节。
ALIASES: dict[str, str] = {
    "merchant_token": "linda00_token",
    "consumer_token": "linda10_token",
}

#: 前置用例文件名（账号密码来源），用于定位其 ``*.vars.yaml``。
PRECONDITION_STEM = "test_linda_t0000_precondition_obtain_all_accounts_token"

#: 剩余寿命低于该秒数就续期（留出一次登录 + 若干请求的余量）。
DEFAULT_THRESHOLD = 60

_TOKEN_REF_RE = re.compile(r"\b([A-Za-z_]\w*_token)\b")

_creds_cache: dict[str, Any] | None = None
_source_cache: dict[str, set[str]] = {}


# --- 凭证来源 -----------------------------------------------------------
def _precondition_vars_file() -> Path | None:
    """定位 T0000 的私有变量文件。"""
    if not settings.TESTS_DIR.exists():
        return None
    for p in settings.TESTS_DIR.rglob(PRECONDITION_STEM + ".vars.yaml"):
        return p
    return None


def credentials() -> dict[str, Any]:
    """读取 T0000 私有变量层（含各账号邮箱/密码），进程内缓存。"""
    global _creds_cache
    if _creds_cache is not None:
        return _creds_cache

    creds: dict[str, Any] = {}
    vars_file = _precondition_vars_file()
    if vars_file is not None:
        creds.update(env_loader.load_yaml(vars_file).get("variables") or {})

    # 环境层兜底（password / UIauto_* 等在 Global.yaml / Release.yaml 里）
    for key, value in (env_loader.load_env().get("variables") or {}).items():
        creds.setdefault(key, value)

    if vars_file is None:
        _log.warning("未找到前置用例变量文件 %s.vars.yaml，角色 token 无法自动续期。",
                     PRECONDITION_STEM)
    _creds_cache = creds
    return creds


# --- token 解析 ---------------------------------------------------------
def token_exp(token: Any) -> float | None:
    """解析 JWT 的 ``exp``；非 JWT / 无 ``exp`` 时返回 ``None``。"""
    if not token or not isinstance(token, str):
        return None
    parts = token.split(".")
    if len(parts) < 2:
        return None
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        data = json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return None
    exp = data.get("exp")
    return float(exp) if isinstance(exp, (int, float)) else None


def seconds_left(token: Any) -> float | None:
    """token 剩余寿命（秒）；无 ``exp`` 时返回 ``None`` 表示「不过期」。"""
    exp = token_exp(token)
    return None if exp is None else exp - time.time()


# --- 引用扫描 -----------------------------------------------------------
def referenced_tokens(source_file) -> set[str]:
    """扫描用例源码，返回其中引用到的角色 token 名（结果按文件缓存）。"""
    known = set(RECIPES) | set(ALIASES)
    if not source_file:
        return set(known)
    key = str(source_file)
    hit = _source_cache.get(key)
    if hit is not None:
        return hit
    try:
        text = Path(key).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set(known)
    found = {m.group(1) for m in _TOKEN_REF_RE.finditer(text)} & known
    _source_cache[key] = found
    return found


# --- 续期 ---------------------------------------------------------------
def _login(ctx, name: str, recipe: dict) -> str | None:
    """按配方登录并返回新 token；失败返回 ``None``（不抛，避免带崩用例）。"""
    creds = credentials()
    email = creds.get(recipe["email"]) or ""
    password = creds.get(recipe["password"]) or ""
    if not email or not password:
        _log.warning("续期 %s 失败：凭证 %s / %s 缺失。",
                     name, recipe["email"], recipe["password"])
        return None

    body = json.dumps({"email": email, "password": password})
    try:
        if recipe.get("admin"):
            resp = ctx.api.admin.auth_login(body=body)
        else:
            resp = ctx.api.auth.sign_in(body=body, app_headers=bool(recipe.get("app_headers")))
    except Exception as exc:  # 网络异常不应中断用例
        _log.warning("续期 %s 请求异常：%s", name, exc)
        return None

    token = resp.path("$.data.token")
    if not token:
        _log.warning("续期 %s 失败：响应未返回 data.token（HTTP %s）。", name, resp.status_code)
        return None
    return token


def ensure_fresh(ctx, *, source_file=None, threshold: float = DEFAULT_THRESHOLD,
                 force: bool = False) -> dict[str, str]:
    """按需续期 ``ctx`` 中的角色 token。

    Args:
        ctx:         用例上下文（``conftest`` 的 ``ctx`` fixture）。
        source_file: 用例文件路径；用于确定「这条用例引用了哪些 token」。
        threshold:   剩余寿命低于该秒数即续期。
        force:       忽略 ``exp`` 与阈值，强制续期。

    Returns:
        ``{token 名: 处置结果}``，结果为 ``fresh`` / ``renewed`` / ``failed``。
    """
    if ctx is None or getattr(ctx, "api", None) is None:
        return {}

    # 前置用例自己就是签发方，不需要（也不应该）在它之前续期
    if source_file and Path(str(source_file)).stem == PRECONDITION_STEM:
        return {}

    outcome: dict[str, str] = {}
    requested = referenced_tokens(source_file)

    # 引用别名时，把它对应的主令牌一并纳入续期（别名要靠主令牌取值）
    names = {n for n in requested if n in RECIPES}
    for alias, source in ALIASES.items():
        if alias in requested and source in RECIPES:
            names.add(source)

    for name in sorted(names):
        recipe = RECIPES[name]
        current = ctx.get(name)
        current_str = current if isinstance(current, str) else None

        if not force:
            left = seconds_left(current_str)
            if left is not None and left > threshold:
                outcome[name] = "fresh"
                continue
            if left is None and current_str and "{{" not in current_str:
                # 无 exp 声明的令牌（如 admin 会话令牌）视为长期有效
                outcome[name] = "fresh"
                continue

        token = _login(ctx, name, recipe)
        if token:
            ctx.set(name, token)
            env_loader.save_runtime_tokens({name: token})
            outcome[name] = "renewed"
        else:
            outcome[name] = "failed"

    # 别名：复用主令牌中「剩余寿命更长」的那个（同账号，claims 等价）
    for alias, source in ALIASES.items():
        if alias not in requested:
            continue
        src_val = ctx.get(source)
        cur_val = ctx.get(alias)
        src_str = src_val if isinstance(src_val, str) and src_val else None
        cur_str = cur_val if isinstance(cur_val, str) and cur_val else None
        src_left = seconds_left(src_str) or -1.0
        cur_left = seconds_left(cur_str) or -1.0
        # 两个都是无 exp 的长效令牌时，src_left/cur_left 同为 -1，此时按有值优先
        pick = src_str if (src_left, bool(src_str)) >= (cur_left, bool(cur_str)) else cur_str
        if pick:
            ctx.set(alias, pick)
            env_loader.save_runtime_tokens({alias: pick})
            outcome[alias] = f"alias<-{source}"
        else:
            outcome[alias] = "failed"

    renewed = [k for k, v in outcome.items() if v == "renewed"]
    failed = [k for k, v in outcome.items() if v == "failed"]
    if renewed:
        _log.info("[token] 已续期 %d 个角色令牌：%s", len(renewed), ", ".join(renewed))
    if failed:
        _log.warning("[token] 续期失败：%s", ", ".join(failed))
    return outcome
