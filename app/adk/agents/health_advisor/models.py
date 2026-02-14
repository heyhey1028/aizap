"""共通モデル設定

Agent Engine が asia-northeast1 にデプロイされているため、
グローバルリージョンでのみ提供されるモデルを使用するには
location="global" を明示的に指定する必要がある。

すべてのエージェントで使用するモデルを一元管理する。
変更時はここを修正するだけで全エージェントに反映される。

参考: https://github.com/google/adk-python/issues/1095
"""

import os
from functools import cached_property

from google.adk.models import Gemini
from google.genai import Client, types


class _GeminiGlobal(Gemini):
    """グローバルエンドポイントを使用する Gemini モデル。

    通常の Gemini クラスではデフォルトのロケーション解決ロジックにより、
    asia-northeast1 等で提供されていないモデルの呼び出しに失敗する。
    このサブクラスでは Client に location="global" を明示的に渡すことで回避する。
    """

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


DEFAULT_MODEL = _GeminiGlobal(model="gemini-2.5-flash-lite")
