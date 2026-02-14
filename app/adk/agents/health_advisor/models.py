"""共通モデル設定

すべてのエージェントで使用するモデルと thinking 設定を一元管理する。
変更時はここを修正するだけで全エージェントに反映される。

Agent Engine が asia-northeast1 にデプロイされているため、
gemini-3-flash-preview はリージョナルエンドポイントで利用できない。
_GeminiGlobal で location="global" を指定してグローバルエンドポイント経由で呼び出す。

参考: https://github.com/google/adk-python/issues/1095
"""

import os
from functools import cached_property

from google.adk.models import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai import Client, types


class _GeminiGlobal(Gemini):
    """グローバルエンドポイントを使用する Gemini モデル。"""

    @cached_property
    def api_client(self) -> Client:
        """グローバルエンドポイントで初期化された API クライアントを提供する。"""
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT 環境変数が設定されていません。"
            )

        return Client(
            project=project,
            location="global",
            http_options=types.HttpOptions(
                headers=self._tracking_headers(),
                retry_options=self.retry_options,
            ),
        )


DEFAULT_MODEL = _GeminiGlobal(model="gemini-3-flash-preview")

# thinking を MINIMAL に設定（レイテンシ・コスト最小化）
DEFAULT_PLANNER = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_level="MINIMAL",
    )
)
