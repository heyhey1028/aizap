"""構造化ロギング

structlog を使用した構造化ログ出力。
Cloud Logging と互換性のある JSON 形式で出力する。
"""

import logging
import os
import sys

import structlog


def _get_log_level() -> str:
    """ログレベルを取得する。

    環境変数 LOG_LEVEL で設定可能（デフォルト: INFO）。
    """
    return os.environ.get("LOG_LEVEL", "INFO").upper()


def configure_logging() -> None:
    """ロギングを設定する。

    アプリケーション起動時に一度だけ呼び出す。
    Cloud Logging と互換性のある JSON 形式で出力する。
    """
    log_level = _get_log_level()

    # 標準 logging の設定
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level, logging.INFO),
    )

    # structlog の設定
    structlog.configure(
        processors=[
            # コンテキスト情報を追加
            structlog.contextvars.merge_contextvars,
            # ログレベルを追加
            structlog.stdlib.add_log_level,
            # ロガー名を追加
            structlog.stdlib.add_logger_name,
            # タイムスタンプを追加（ISO 8601 形式）
            structlog.processors.TimeStamper(fmt="iso"),
            # スタックトレースを追加（例外時）
            structlog.processors.StackInfoRenderer(),
            # 例外情報をフォーマット
            structlog.processors.format_exc_info,
            # Cloud Logging 互換の JSON 形式で出力
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """ロガーを取得する。

    Args:
        name: ロガー名（省略時は呼び出し元のモジュール名）

    Returns:
        構造化ロガー

    使用例:
        from utils.logger import get_logger

        logger = get_logger(__name__)
        logger.info("処理開始", user_id="123", action="create")
        logger.error("エラー発生", error=str(e), user_id="123")
    """
    return structlog.get_logger(name)


# モジュール読み込み時に自動設定
configure_logging()
