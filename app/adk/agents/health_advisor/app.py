"""ADK アプリケーション設定

Agent Engine にデプロイする際のアプリケーション設定。
App クラスを使用することで、セッション管理やイベント圧縮などの
追加機能を有効にできる。

Note: Agent Engine にデプロイすると、VertexAiSessionService が
自動的に使用され、会話履歴がセッション内で維持される。
"""

from google.adk.apps import App

from .agent import root_agent

# ADK アプリケーションを作成
# Agent Engine にデプロイすると、セッション管理が自動的に有効になる
app = App(
    name="health_advisor",
    root_agent=root_agent,
)
