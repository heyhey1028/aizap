"""DB アクセス層の動作確認スクリプト

使用方法:
    cd app/adk
    uv sync
    gcloud auth application-default login
    export CLOUD_SQL_INSTANCE=aizap-dev:asia-northeast1:aizap-postgres-dev
    export DB_NAME=aizap
    uv run python test_db.py
"""

import asyncio
import os
import sys

from google.cloud.sql.connector import Connector


def get_db_user() -> str:
    """DB_USER 環境変数または ADC から取得"""
    db_user = os.environ.get("DB_USER")
    if db_user:
        return db_user
    
    # ADC から取得（偽装を使っている場合）
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
    
    raise ValueError(
        "DB_USER が設定されていません。\n"
        "ローカル開発の場合は以下を実行してください:\n"
        "gcloud auth application-default login "
        "--impersonate-service-account=aizap-adk-sa@PROJECT.iam.gserviceaccount.com"
    )


async def test_connection() -> bool:
    """DB 接続と基本的なクエリをテスト"""
    print("=" * 50)
    print("DB アクセス層 動作確認")
    print("=" * 50)

    instance = os.environ.get("CLOUD_SQL_INSTANCE")
    db_name = os.environ.get("DB_NAME")
    db_user = get_db_user()

    print(f"\nインスタンス: {instance}")
    print(f"データベース: {db_name}")
    print(f"ユーザー: {db_user}")

    if not instance or not db_name:
        print("\n✗ 環境変数が設定されていません")
        return False

    connector = None
    conn = None

    try:
        # 現在のイベントループを取得して Connector を初期化
        loop = asyncio.get_running_loop()
        connector = Connector(loop=loop)

        conn = await connector.connect_async(
            instance,
            "asyncpg",
            user=db_user,
            db=db_name,
            enable_iam_auth=True,
        )
        print("\n✓ DB 接続成功")

        # 接続情報を確認
        print("\n--- 接続情報 ---")
        db_info = await conn.fetchrow("SELECT current_database(), current_user, current_schema()")
        print(f"  データベース: {db_info[0]}")
        print(f"  ユーザー: {db_info[1]}")
        print(f"  スキーマ: {db_info[2]}")

        # 既存のテーブル一覧を取得
        print("\n--- 既存のテーブル一覧 ---")
        rows = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        if not rows:
            print("  テーブルが存在しません")
            print("  → Worker 側でマイグレーションを実行してください")
            print("    cd app/worker && pnpm prisma migrate deploy")
        else:
            for row in rows:
                print(f"  - {row['table_name']}")

            # 各テーブルの件数を確認
            print("\n--- テーブル件数 ---")
            for row in rows:
                table_name = row["table_name"]
                if table_name.startswith("_"):  # Prisma の内部テーブルはスキップ
                    continue
                count_row = await conn.fetchrow(f'SELECT COUNT(*) as count FROM "{table_name}"')
                print(f"  {table_name}: {count_row['count']} 件")

        print("\n" + "=" * 50)
        print("✓ DB 接続テスト完了")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"\n✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if conn:
            await conn.close()
        if connector:
            await connector.close_async()


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
