"""汎用ユーティリティツール

特定のテーブルに紐づかない、エージェント制御や共通処理用のツール。
全てのサブエージェントから利用可能。
"""

from google.adk.tools import ToolContext

from ..db.config import get_async_session
from ..db.repositories import GoalRepository
from ..logger import get_logger

logger = get_logger(__name__)


async def get_current_goal(tool_context: ToolContext) -> dict:
    """ユーザーの直近の健康目標（goal_id, details, habits）を取得する。

    運動習慣の作成やレトロスペクティブで目標と照らし合わせる際に使用する。
    設定されていない場合は未設定であることを返す。

    Returns:
        - status: "success" | "not_set" | "error"
        - health_goal: 成功時のみ。id, details, habits, created_at を含む
        - message: not_set / error 時のメッセージ
    """
    user_id = tool_context.user_id
    try:
        async with get_async_session() as session:
            repo = GoalRepository(session)
            goal = await repo.get_by_user_id(user_id)
            if goal is None:
                logger.info("健康目標が見つかりません", user_id=user_id)
                return {
                    "status": "not_set",
                    "message": "健康目標がまだ設定されていません。目標を設定しましょう！",
                }
            logger.info("健康目標を取得しました", user_id=user_id, goal_id=goal.id)
            return {
                "status": "success",
                "health_goal": {
                    "id": goal.id,
                    "details": goal.details,
                    "habits": goal.habits,
                    "created_at": goal.created_at.isoformat(),
                },
            }
    except Exception as e:
        logger.error("健康目標の取得に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "健康目標の取得中にエラーが発生しました。",
        }


def finish_task(summary: str, tool_context: ToolContext) -> dict:
    """タスク完了時に呼び出します。制御をルートエージェントに戻します。

    このツールを呼ぶと、対話権がルートエージェントに戻ります。
    呼び出し後は追加のメッセージを生成せず、処理を終了してください。

    Args:
        summary: 完了したタスクの要約（例: 記録した運動内容の要約）。ルートエージェントに渡されます。
        tool_context: ADKが提供するToolContext。
    """
    tool_context.actions.transfer_to_agent = "root_agent"
    return {
        "status": "success",
        "data": summary,
        "next_agent": "root_agent",
        "terminate_sub_segment": True,
    }
