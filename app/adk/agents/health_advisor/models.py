"""カスタム Gemini モデルクラス

Gemini 3.0 Flash など、グローバルエンドポイントが必要なモデル向けのワークアラウンド。
標準の Gemini クラスではリージョナルエンドポイントの解決に失敗するため、
location="global" を明示的に指定してクライアントを初期化する。

参考: https://github.com/google/adk-python/issues/1095
"""

import os
from functools import cached_property

from google.adk.models import Gemini
from google.genai import Client, types


class GeminiGlobal(Gemini):
    """グローバルエンドポイントを使用する Gemini モデル。

    通常の Gemini クラスではデフォルトのロケーション解決ロジックにより、
    特定のモデル（gemini-3.0-flash 等）でデプロイに失敗する場合がある。
    このサブクラスでは Client に project と location="global" を明示的に渡すことで回避する。

    使用例:
    ```python
    agent = Agent(
        model=GeminiGlobal(model="gemini-3-flash-preview"),
        name="my_agent",
        ...
    )
    ```
    """

    @cached_property
    def api_client(self) -> Client:
        """明示的な設定で API クライアントを提供する。

        Returns:
            グローバルエンドポイントで初期化された API クライアント。
        """
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
