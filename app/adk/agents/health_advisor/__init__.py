"""health_advisor エージェント

ADK の get_fast_api_app() がエージェントを自動検出するために、
root_agent を直接エクスポートする必要があります。
"""

from .agent import root_agent

__all__ = ["root_agent"]
