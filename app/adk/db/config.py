"""DB 接続設定

Cloud SQL Python Connector + IAM 認証を使用して PostgreSQL に接続する。
ローカル開発では ADC (Application Default Credentials) を、
Agent Engine ではサービスアカウントを使用する。

注意: ADK のツールは異なるイベントループで呼ばれる可能性があるため、
シングルトンパターンは使用せず、毎回新しい Connector を作成する。
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from google.cloud.sql.connector import Connector
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# 環境変数
# - GCP_PROJECT_ID: GCP プロジェクト ID
# - CLOUD_SQL_INSTANCE: Cloud SQL インスタンス接続名（例: project:region:instance）
# - DB_NAME: データベース名
# - DB_USER: IAM ユーザー（Agent Engine 用、ローカルでは不要）


def _get_instance_connection_name() -> str:
    """Cloud SQL インスタンス接続名を取得する。"""
    instance = os.environ.get("CLOUD_SQL_INSTANCE")
    if not instance:
        raise ValueError("CLOUD_SQL_INSTANCE 環境変数が設定されていません")
    return instance


def _get_db_name() -> str:
    """データベース名を取得する。"""
    db_name = os.environ.get("DB_NAME")
    if not db_name:
        raise ValueError("DB_NAME 環境変数が設定されていません")
    return db_name


def _get_db_user() -> str | None:
    """IAM ユーザーを取得する（Agent Engine 用）。

    ローカル開発では ADC が使用されるため、この値は不要。
    Agent Engine では サービスアカウント名@project.iam 形式で指定。
    """
    return os.environ.get("DB_USER")


def _get_db_user_from_adc() -> str | None:
    """ADC から IAM ユーザーを取得する（ローカル開発用）。

    偽装を使っている場合はサービスアカウントのメールアドレスを返す。
    通常の ADC の場合は None を返す（個人アカウントは Cloud SQL IAM 認証に使えない）。
    """
    import google.auth

    try:
        credentials, _ = google.auth.default()

        # 偽装を使っている場合（ImpersonatedCredentials）
        if hasattr(credentials, "service_account_email"):
            return credentials.service_account_email

        # 偽装の source_credentials をチェック
        if hasattr(credentials, "_source_credentials"):
            source = credentials._source_credentials
            if hasattr(source, "service_account_email"):
                return source.service_account_email

    except Exception:
        pass
    return None


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """非同期セッションを取得するコンテキストマネージャー。

    ADK のツールは異なるイベントループで呼ばれる可能性があるため、
    毎回新しい Connector を現在のイベントループで初期化する。

    使用例:
        async with get_async_session() as session:
            result = await session.execute(...)
    """
    instance_connection_name = _get_instance_connection_name()
    db_name = _get_db_name()
    db_user = _get_db_user()

    # DB_USER が設定されていない場合は ADC から取得（ローカル開発用）
    if db_user is None:
        db_user = _get_db_user_from_adc()
        if db_user is None:
            raise ValueError(
                "DB_USER 環境変数が設定されていません。\n"
                "ローカル開発の場合は以下を実行してください:\n"
                "gcloud auth application-default login "
                "--impersonate-service-account=aizap-adk-sa@PROJECT.iam.gserviceaccount.com"
            )

    # 現在のイベントループで Connector を初期化
    loop = asyncio.get_running_loop()
    connector = Connector(loop=loop)

    try:
        async def get_conn():
            return await connector.connect_async(
                instance_connection_name,
                "asyncpg",
                user=db_user,
                db=db_name,
                enable_iam_auth=True,
            )

        engine = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=get_conn,
            echo=os.environ.get("DB_ECHO", "false").lower() == "true",
        )

        session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    finally:
        # Connector を必ずクローズ
        await connector.close_async()
