"""DB アクセス層の動作確認スクリプト

各テーブルに対して CRUD 操作をテストし、最後にテストデータを削除する。

使用方法:
    cd app/adk/agents/health_advisor
    gcloud auth application-default login \
        --impersonate-service-account=aizap-adk-sa@aizap-dev.iam.gserviceaccount.com
    export CLOUD_SQL_INSTANCE=aizap-dev:asia-northeast1:aizap-postgres-dev
    export DB_NAME=aizap
    uv run --project ../.. python db/test_db.py
"""

import asyncio
import os
import sys
import uuid

# app/adk をパスに追加（db/ フォルダから実行する場合に必要）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud.sql.connector import Connector
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.models import UserSession, Goal, ExerciseLog
from db.repositories import UserSessionRepository, GoalRepository, ExerciseLogRepository


def get_db_user() -> str:
    """DB_USER 環境変数または ADC から取得"""
    db_user = os.environ.get("DB_USER")
    if db_user:
        return db_user

    import google.auth

    try:
        credentials, _ = google.auth.default()
        if hasattr(credentials, "service_account_email"):
            return credentials.service_account_email
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


async def test_crud() -> bool:
    """各テーブルに対して CRUD 操作をテスト"""
    print("=" * 60)
    print("DB アクセス層 CRUD テスト")
    print("=" * 60)

    instance = os.environ.get("CLOUD_SQL_INSTANCE")
    db_name = os.environ.get("DB_NAME")
    db_user = get_db_user()

    print(f"\nインスタンス: {instance}")
    print(f"データベース: {db_name}")
    print(f"ユーザー: {db_user}")

    if not instance or not db_name:
        print("\n✗ 環境変数が設定されていません")
        return False

    # テスト用の一意な ID を生成
    test_id = f"test-{uuid.uuid4().hex[:8]}"
    test_user_id = f"U{test_id}"
    test_session_id = f"S{test_id}"

    print(f"\nテスト ID: {test_id}")

    connector = None
    created_resources: dict[str, list[str]] = {
        "user_session": [],
        "goal": [],
        "exercise_log": [],
    }

    try:
        loop = asyncio.get_running_loop()
        connector = Connector(loop=loop)

        async def get_conn():
            return await connector.connect_async(
                instance,
                "asyncpg",
                user=db_user,
                db=db_name,
                enable_iam_auth=True,
            )

        engine = create_async_engine("postgresql+asyncpg://", async_creator=get_conn)
        session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        print("\n✓ DB 接続成功")

        # === UserSession CRUD ===
        print("\n" + "-" * 60)
        print("UserSession CRUD テスト")
        print("-" * 60)

        async with session_maker() as session:
            repo = UserSessionRepository(session)

            # Create
            print("\n[CREATE] UserSession を作成...")
            user_session = await repo.upsert(
                user_id=test_user_id, session_id=test_session_id
            )
            created_resources["user_session"].append(test_user_id)
            print(f"  ✓ 作成完了: user_id={user_session.user_id}")

            # Read
            print("\n[READ] UserSession を取得...")
            fetched = await repo.get_by_user_id(test_user_id)
            assert fetched is not None, "UserSession が見つかりません"
            assert fetched.user_id == test_user_id
            print(f"  ✓ 取得完了: session_id={fetched.session_id}")

            # Update
            print("\n[UPDATE] UserSession を更新...")
            new_session_id = f"S{test_id}-updated"
            updated = await repo.upsert(user_id=test_user_id, session_id=new_session_id)
            assert updated.session_id == new_session_id
            print(f"  ✓ 更新完了: session_id={updated.session_id}")

            await session.commit()

        # === Goal CRUD ===
        print("\n" + "-" * 60)
        print("Goal CRUD テスト")
        print("-" * 60)

        async with session_maker() as session:
            repo = GoalRepository(session)

            # Create
            print("\n[CREATE] Goal を作成...")
            goal = await repo.create_goal(
                user_id=test_user_id,
                details='{"goal_type": "test", "description": "テスト目標"}',
                habits="test_habit",
            )
            created_resources["goal"].append(goal.id)
            print(f"  ✓ 作成完了: id={goal.id[:20]}...")

            # Read
            print("\n[READ] Goal を取得...")
            fetched = await repo.get_by_user_id(test_user_id)
            assert fetched is not None, "Goal が見つかりません"
            print(f"  ✓ 取得完了: habits={fetched.habits}")

            # Update
            print("\n[UPDATE] Goal を更新...")
            updated = await repo.update(
                goal.id, details='{"goal_type": "test", "description": "更新済み"}'
            )
            assert updated is not None
            print(f"  ✓ 更新完了: details={updated.details[:30]}...")

            await session.commit()

        # === ExerciseLog CRUD ===
        print("\n" + "-" * 60)
        print("ExerciseLog CRUD テスト")
        print("-" * 60)

        async with session_maker() as session:
            repo = ExerciseLogRepository(session)

            # Create
            print("\n[CREATE] ExerciseLog を作成...")
            log = await repo.create_log(
                user_id=test_user_id,
                exercise_name="テストウォーキング",
                sets=[{"reps": 1, "duration": 1800}],
                total_sets=1,
                total_duration=1800,
                note="テスト用の運動記録",
            )
            created_resources["exercise_log"].append(log.id)
            print(f"  ✓ 作成完了: id={log.id[:20]}...")

            # Read
            print("\n[READ] ExerciseLog を取得...")
            logs = await repo.get_by_user_id(test_user_id)
            assert len(logs) > 0, "ExerciseLog が見つかりません"
            fetched = logs[0]
            print(f"  ✓ 取得完了: exercise_name={fetched.exercise_name}")

            # Update
            print("\n[UPDATE] ExerciseLog を更新...")
            updated = await repo.update(log.id, total_duration=2700, note="更新済み")
            assert updated is not None
            print(f"  ✓ 更新完了: total_duration={updated.total_duration}秒")

            await session.commit()

        # === Cleanup ===
        print("\n" + "-" * 60)
        print("クリーンアップ")
        print("-" * 60)

        async with session_maker() as session:
            # ExerciseLog 削除
            repo = ExerciseLogRepository(session)
            for log_id in created_resources["exercise_log"]:
                print(f"\n[DELETE] ExerciseLog を削除: {log_id[:20]}...")
                await repo.delete(log_id)
                print("  ✓ 削除完了")

            # Goal 削除
            repo = GoalRepository(session)
            for goal_id in created_resources["goal"]:
                print(f"\n[DELETE] Goal を削除: {goal_id[:20]}...")
                await repo.delete(goal_id)
                print("  ✓ 削除完了")

            # UserSession 削除
            repo = UserSessionRepository(session)
            for user_id in created_resources["user_session"]:
                print(f"\n[DELETE] UserSession を削除: {user_id}...")
                await repo.delete(user_id)
                print("  ✓ 削除完了")

            await session.commit()

        await engine.dispose()

        print("\n" + "=" * 60)
        print("✓ すべての CRUD テストが成功しました")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ エラー: {e}")
        import traceback

        traceback.print_exc()

        # エラー時もクリーンアップを試みる
        print("\n[CLEANUP] エラー発生時のクリーンアップを試行...")
        try:
            async with session_maker() as session:
                for log_id in created_resources["exercise_log"]:
                    await session.execute(
                        text("DELETE FROM exercise_logs WHERE id = :id"),
                        {"id": log_id},
                    )
                for goal_id in created_resources["goal"]:
                    await session.execute(
                        text("DELETE FROM goals WHERE id = :id"), {"id": goal_id}
                    )
                for user_id in created_resources["user_session"]:
                    await session.execute(
                        text("DELETE FROM user_sessions WHERE user_id = :id"),
                        {"id": user_id},
                    )
                await session.commit()
                print("  ✓ クリーンアップ完了")
        except Exception as cleanup_error:
            print(f"  ✗ クリーンアップ失敗: {cleanup_error}")

        return False

    finally:
        if connector:
            await connector.close_async()


if __name__ == "__main__":
    success = asyncio.run(test_crud())
    sys.exit(0 if success else 1)
