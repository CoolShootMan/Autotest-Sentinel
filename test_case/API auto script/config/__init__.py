"""配置层：运行参数 + 分层环境变量装载。

``settings``      运行参数（环境名、超时、重试、日志）
``env_loader``    Global / 环境 / 运行期令牌 的分层合并
``environments/`` 各环境的 YAML 配置
"""
from config import env_loader, settings

__all__ = ["settings", "env_loader"]
