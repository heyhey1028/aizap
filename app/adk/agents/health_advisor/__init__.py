"""health_advisor エージェント

ADK の自動検出のために、root_agent と app をエクスポート。

- root_agent: エージェント本体
- app: App クラスでラップしたアプリケーション（Agent Engine デプロイ時に使用）

Agent Engine にデプロイする際は `--adk_app_object=app` を指定することで、
App クラスの設定（セッション管理など）が有効になる。
"""

from .agent import root_agent
from .app import app

__all__ = ["root_agent", "app"]
