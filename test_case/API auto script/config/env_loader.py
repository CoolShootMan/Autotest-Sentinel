"""环境变量装载。

分层优先级（与迁移前 ``case_vars.load_case_vars`` 保持一致，高层覆盖低层）：

    1. 全局变量     config/environments/Global.yaml
    2. 环境变量     config/environments/<ENV_NAME>.yaml
    3. 运行期令牌   config/environments/_runtime_tokens.yaml   （前置用例产出）
    4. 用例私有变量 <case>.vars.yaml / data/cases/<slug>.yaml   （优先级最高）

``base_url`` 单独抽出（不在 variables 里），因为它是请求拼接的根。

占位符渲染
----------
加载后的任意字符串中若包含 ``{{VAR}}``，会被 ``os.environ['VAR']`` 的值替换。
缺失变量即抛 :class:`ConfigError`，避免上线时静默成空值走错环境。
对 .env 文件的兼容由 ``python-dotenv`` 提供（如已安装），但 **不强制依赖**——只要把
变量放进 shell 环境即可。所有占位符值集中记录在 ``config/environments/.env.example``。
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

from config import settings
from core.errors import ConfigError

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")


def _try_load_dotenv() -> None:
    """Best-effort: 如果 python-dotenv 已安装，把 .env 注入 os.environ。"""
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return
    # 项目根与 env 子目录都尝试，存在哪个就加载哪个
    for cand in (settings.ROOT, settings.ENV_DIR):
        env_file = cand / ".env"
        if env_file.exists():
            load_dotenv(env_file, override=False)


def _expand_placeholders(obj, src_file: Path) -> object:
    """递归把 dict/list/str 中的 ``{{VAR}}`` 替换为 ``os.environ['VAR']``。

    找不到的变量抛 :class:`ConfigError`（带文件路径 + 变量名 + 出现位置的子串）。
    """
    if isinstance(obj, dict):
        return {k: _expand_placeholders(v, src_file) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_placeholders(v, src_file) for v in obj]
    if isinstance(obj, str):
        def replace(m: re.Match) -> str:
            var = m.group(1)
            val = os.environ.get(var)
            if val is None:
                raise ConfigError(
                    f"{src_file} 引用了未设置的环境变量 {{{{ {var} }}}}; "
                    f"请在 shell 或 .env 中 export {var}=..."
                )
            return val
        return _PLACEHOLDER_RE.sub(replace, obj)
    return obj


def load_yaml(path: Path) -> dict:
    """安全读取 YAML；文件不存在或为空返回 ``{}``。

    加载后会扫描字符串值里的 ``{{VAR}}`` 占位符并替换为 ``os.environ['VAR']``。
    """
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # YAML 语法错误必须显式报错，不能静默成空配置
        raise ConfigError(f"YAML 解析失败: {path}: {exc}") from exc
    if not isinstance(data, dict):
        return {}
    return _expand_placeholders(data, path)


def save_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def load_runtime_tokens() -> dict:
    """读取前置用例写入的运行期令牌。"""
    return dict(load_yaml(settings.RUNTIME_TOKENS_FILE).get("variables") or {})


def save_runtime_tokens(tokens: dict) -> None:
    """把令牌合并进运行期令牌文件（值为 ``None`` 的键不写入）。"""
    data = load_yaml(settings.RUNTIME_TOKENS_FILE) or {}
    variables = dict(data.get("variables") or {})
    variables.update({k: v for k, v in tokens.items() if v is not None})
    data["variables"] = variables
    save_yaml(settings.RUNTIME_TOKENS_FILE, data)


def clear_runtime_tokens() -> None:
    """清空运行期令牌（前置用例重新跑之前调用）。"""
    save_yaml(settings.RUNTIME_TOKENS_FILE, {"variables": {}})


def load_env(env_name: str | None = None) -> dict:
    """装载分层环境变量，返回 ``{"base_url": str, "variables": dict, "env_name": str}``。

    占位符规则同 :func:`load_yaml`；缺失变量会抛 ``ConfigError``。

    Raises:
        ConfigError: 环境文件缺失，或最终未能解析出 ``base_url``。
    """
    _try_load_dotenv()
    env_name = env_name or settings.ENV_NAME

    global_file = settings.ENV_DIR / "Global.yaml"
    env_file = settings.ENV_DIR / f"{env_name}.yaml"

    if not global_file.exists():
        raise ConfigError(f"全局配置缺失: {global_file}")
    if not env_file.exists():
        available = sorted(p.stem for p in settings.ENV_DIR.glob("*.yaml")
                           if not p.name.startswith("_"))
        raise ConfigError(
            f"环境配置缺失: {env_file}；可选环境: {', '.join(available) or '(无)'}"
        )

    g = load_yaml(global_file)
    e = load_yaml(env_file)

    base_url = g.get("base_url", "") or ""
    merged = dict(g.get("variables") or {})

    if e.get("base_url"):
        base_url = e["base_url"]
    merged.update(e.get("variables") or {})

    merged.update(load_runtime_tokens())

    if not base_url:
        raise ConfigError(f"{env_file} 与 Global.yaml 均未定义 base_url")

    return {"base_url": base_url, "variables": merged, "env_name": env_name}


def case_vars_path(case_file) -> Path:
    """用例私有变量文件路径（``<case>.vars.yaml``，与用例同目录同名）。"""
    case_file = Path(case_file)
    return case_file.with_name(case_file.stem + ".vars.yaml")


def load_case_vars(case_file, env_name: str | None = None) -> dict:
    """装载单条用例的合并变量（``load_env`` 之上再叠加用例私有层）。

    合并优先级（高者覆盖低者）::

        1. config/environments/Global.yaml
        2. config/environments/<ENV_NAME>.yaml
        3. config/environments/_runtime_tokens.yaml   （前置用例产出）
        4. <case>.vars.yaml                            （用例私有，最高）

    ``base_url`` 单独抽出，因为它是请求拼接的根；用例私有层可覆盖它
    （少数用例需要指向另一个域名）。

    Args:
        case_file: 用例文件路径（``tests/**/test_*.py``）。
        env_name:  环境名，缺省取 ``settings.ENV_NAME``。

    Returns:
        ``{"base_url": str, "variables": dict, "env_name": str, "case_vars_file": str}``
    """
    data = load_env(env_name)

    pc_file = case_vars_path(case_file)
    pc = load_yaml(pc_file)
    if pc:
        if pc.get("base_url"):
            data["base_url"] = pc["base_url"]
        data["variables"].update(pc.get("variables") or {})

    data["case_vars_file"] = str(pc_file) if pc_file.exists() else ""
    return data
