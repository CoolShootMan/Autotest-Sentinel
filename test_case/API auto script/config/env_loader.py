"""环境变量装载。

分层优先级（与迁移前 ``case_vars.load_case_vars`` 保持一致，高层覆盖低层）：

    1. 全局变量     config/environments/Global.yaml
    2. 环境变量     config/environments/<ENV_NAME>.yaml
    3. 运行期令牌   config/environments/_runtime_tokens.yaml   （前置用例产出）
    4. 用例私有变量 <case>.vars.yaml / data/cases/<slug>.yaml   （优先级最高）

``base_url`` 单独抽出（不在 variables 里），因为它是请求拼接的根。
"""
from __future__ import annotations

from pathlib import Path

import yaml

from config import settings
from core.errors import ConfigError


def load_yaml(path: Path) -> dict:
    """安全读取 YAML；文件不存在或为空返回 ``{}``。"""
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # YAML 语法错误必须显式报错，不能静默成空配置
        raise ConfigError(f"YAML 解析失败: {path}: {exc}") from exc
    return data if isinstance(data, dict) else {}


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

    Raises:
        ConfigError: 环境文件缺失，或最终未能解析出 ``base_url``。
    """
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
