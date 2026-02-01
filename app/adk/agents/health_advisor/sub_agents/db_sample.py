"""DB アクセスのサンプルサブエージェント

このファイルは DB アクセスの書き方をチームメンバーに示すためのサンプルです。
後で削除することを前提としています。

## ポイント

1. user_id の取得: `tool_context.user_id` を使用
2. セッション管理: `async with get_async_session() as session:` でコンテキストマネージャー使用
3. リポジトリパターン: `Repository` クラスを通じて CRUD 操作
4. 構造化ログ: `utils.logger` の `get_logger` を使用
5. エラーハンドリング: try-except でエラーをキャッチしてログ出力
"""

import os
import sys

# app/adk をパスに追加（db, utils モジュールを参照するため）
_adk_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if _adk_root not in sys.path:
    sys.path.insert(0, _adk_root)

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from db.config import get_async_session
from db.repositories import UserSessionRepository, GoalRepository, ExerciseLogRepository
from utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# READ サンプル
# =============================================================================


async def get_user_session_from_db(tool_context: ToolContext) -> dict:
    """ユーザーセッションを DB から取得するサンプル

    tool_context.user_id から user_id を取得し、
    UserSessionRepository を使って DB からセッション情報を取得します。
    """
    # 1. user_id を ToolContext から取得
    user_id = tool_context.user_id

    try:
        # 2. セッションをコンテキストマネージャーで取得
        async with get_async_session() as session:
            # 3. リポジトリを初期化
            repo = UserSessionRepository(session)

            # 4. DB からデータを取得
            user_session = await repo.get_by_user_id(user_id)

            if user_session is None:
                logger.info("ユーザーセッションが見つかりません", user_id=user_id)
                return {
                    "status": "not_found",
                    "message": "ユーザーセッションが見つかりませんでした。",
                }

            # 5. 成功時のレスポンス
            logger.info("ユーザーセッションを取得しました", user_id=user_id)
            return {
                "status": "success",
                "user_id": user_session.user_id,
                "session_id": user_session.session_id,
                "created_at": user_session.created_at.isoformat(),
            }

    except Exception as e:
        # 6. エラーハンドリング
        logger.error("DB からの取得に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "データの取得中にエラーが発生しました。",
        }


async def create_user_session_in_db(tool_context: ToolContext) -> dict:
    """ユーザーセッションを DB に作成するサンプル

    Goal や ExerciseLog は user_sessions への外部キー制約があるため、
    先にユーザーセッションを作成しておく必要があります。
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = UserSessionRepository(session)

            # upsert: 存在すれば更新、なければ作成
            import uuid

            session_id = str(uuid.uuid4())
            user_session = await repo.upsert(user_id=user_id, session_id=session_id)

            logger.info(
                "ユーザーセッションを作成しました",
                user_id=user_id,
                session_id=user_session.session_id,
            )

            return {
                "status": "success",
                "message": "ユーザーセッションを作成しました。",
                "user_id": user_session.user_id,
                "session_id": user_session.session_id,
            }

    except Exception as e:
        logger.error("ユーザーセッションの作成に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "ユーザーセッションの作成中にエラーが発生しました。",
        }


async def get_user_goals_from_db(tool_context: ToolContext) -> dict:
    """ユーザーの目標一覧を DB から取得するサンプル

    複数件のデータを取得する場合の例です。
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = GoalRepository(session)

            # 複数件取得の例
            goals = await repo.get_all_by_user_id(user_id)

            if not goals:
                return {
                    "status": "not_found",
                    "message": "目標が設定されていません。",
                    "goals": [],
                }

            # リストで返す
            return {
                "status": "success",
                "goals": [
                    {
                        "id": goal.id,
                        "details": goal.details,
                        "habits": goal.habits,
                        "created_at": goal.created_at.isoformat(),
                    }
                    for goal in goals
                ],
            }

    except Exception as e:
        logger.error("目標の取得に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "目標の取得中にエラーが発生しました。",
        }


# =============================================================================
# CREATE サンプル
# =============================================================================


async def save_goal_to_db(
    tool_context: ToolContext,
    goal_type: str,
    description: str,
) -> dict:
    """目標を DB に保存するサンプル

    Args:
        tool_context: ADK が提供する ToolContext
        goal_type: 目標の種類（weight_loss, muscle_gain 等）
        description: 目標の詳細説明
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = GoalRepository(session)

            # CREATE の例
            goal = await repo.create_goal(
                user_id=user_id,
                details=description,
                habits=goal_type,
            )

            logger.info("目標を保存しました", user_id=user_id, goal_id=goal.id)

            return {
                "status": "success",
                "message": f"目標を保存しました: {goal_type}",
                "goal_id": goal.id,
            }

    except Exception as e:
        logger.error("目標の保存に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "目標の保存中にエラーが発生しました。",
        }


# =============================================================================
# ExerciseLog サンプル（READ/CREATE）
# =============================================================================


async def get_exercise_logs_from_db(tool_context: ToolContext) -> dict:
    """運動記録を DB から取得するサンプル

    ExerciseLogRepository を使って運動記録を取得します。
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = ExerciseLogRepository(session)

            # 最新 5 件を取得
            logs = await repo.get_by_user_id(user_id, limit=5)

            if not logs:
                return {
                    "status": "not_found",
                    "message": "運動記録がありません。",
                    "logs": [],
                }

            return {
                "status": "success",
                "logs": [
                    {
                        "id": log.id,
                        "exercise_name": log.exercise_name,
                        "total_sets": log.total_sets,
                        "total_duration": log.total_duration,
                        "recorded_at": log.recorded_at.isoformat(),
                    }
                    for log in logs
                ],
            }

    except Exception as e:
        logger.error("運動記録の取得に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "運動記録の取得中にエラーが発生しました。",
        }


async def save_exercise_log_to_db(
    tool_context: ToolContext,
    exercise_name: str,
    duration_minutes: int,
) -> dict:
    """運動記録を DB に保存するサンプル

    Args:
        tool_context: ADK が提供する ToolContext
        exercise_name: 運動名（ウォーキング、ランニング等）
        duration_minutes: 運動時間（分）
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = ExerciseLogRepository(session)

            # 運動記録を作成
            log = await repo.create_log(
                user_id=user_id,
                exercise_name=exercise_name,
                sets=[{"duration": duration_minutes * 60}],  # 秒に変換
                total_sets=1,
                total_duration=duration_minutes * 60,
            )

            logger.info(
                "運動記録を保存しました",
                user_id=user_id,
                log_id=log.id,
                exercise_name=exercise_name,
            )

            return {
                "status": "success",
                "message": f"運動記録を保存しました: {exercise_name} ({duration_minutes}分)",
                "log_id": log.id,
            }

    except Exception as e:
        logger.error("運動記録の保存に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "運動記録の保存中にエラーが発生しました。",
        }


# =============================================================================
# サブエージェント定義
# =============================================================================

db_sample_agent = Agent(
    name="db_sample_agent",
    description="DB アクセスのサンプル（開発用）。DB からの読み取り・書き込みの動作確認に使用。",
    instruction="""あなたは DB アクセスのテスト用エージェントです。

## 役割
- DB からデータを読み取る
- DB にデータを書き込む
- DB アクセスの動作確認

## 使用するツール

### UserSession
- `get_user_session_from_db`: ユーザーセッションを取得
- `create_user_session_in_db`: ユーザーセッションを作成

### Goal
- `get_user_goals_from_db`: ユーザーの目標一覧を取得
- `save_goal_to_db`: 目標を保存

### ExerciseLog
- `get_exercise_logs_from_db`: 運動記録を取得
- `save_exercise_log_to_db`: 運動記録を保存

## 重要
Goal や ExerciseLog を保存する前に、ユーザーセッションが存在する必要があります。
セッションが存在しない場合は、先に `create_user_session_in_db` を呼び出してください。

## 注意
このエージェントは開発・テスト用です。本番では使用しないでください。
""",
    tools=[
        get_user_session_from_db,
        create_user_session_in_db,
        get_user_goals_from_db,
        save_goal_to_db,
        get_exercise_logs_from_db,
        save_exercise_log_to_db,
    ],
)
