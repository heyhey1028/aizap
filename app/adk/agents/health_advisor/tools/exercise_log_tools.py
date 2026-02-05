"""運動記録（ExerciseLog）操作ツール

ExerciseLogs テーブルへの書き込みと読み込みを行うツールを提供する。
"""

from datetime import datetime
from typing import Any

from google.adk.tools import ToolContext

from ..db.config import get_async_session
from ..db.repositories import ExerciseLogRepository
from ..logger import get_logger

logger = get_logger(__name__)


async def create_exercise_log(
    tool_context: ToolContext,
    exercise_name: str,
    sets: list[dict[str, Any]],
    total_sets: int,
    category: str | None = None,
    muscle_group: str | None = None,
    total_reps: int | None = None,
    total_duration: int | None = None,
    total_distance: float | None = None,
    total_volume: float | None = None,
    note: str | None = None,
    recorded_at: str | None = None,
) -> dict:
    """運動記録を作成する。

    Args:
        tool_context: ADK が提供する ToolContext
        exercise_name: 運動名（例: ベンチプレス、スクワット、ランニング）
        sets: セット情報のリスト。例:
            - 筋トレ: [{"reps": 10, "weight": 50}, {"reps": 8, "weight": 55}]
            - 有酸素: [{"duration": 1800, "distance": 5.0}]
        total_sets: 総セット数
        category: カテゴリ（例: strength, cardio, flexibility）
        muscle_group: 対象筋肉群（例: chest, legs, back）
        total_reps: 総レップ数（筋トレの場合）
        total_duration: 総時間（秒）
        total_distance: 総距離（km）
        total_volume: 総ボリューム（kg）= Σ(reps × weight)
        note: メモ・備考
        recorded_at: 記録日時（ISO 8601 形式、省略時は現在時刻）

    Returns:
        作成結果を含む辞書:
        - status: "success" または "error"
        - message: 結果メッセージ
        - log_id: 作成された運動記録の ID（成功時のみ）
        - exercise_name: 運動名（成功時のみ）
        - recorded_at: 記録日時（成功時のみ）

    Examples:
        # 筋トレの記録
        >>> await create_exercise_log(
        ...     tool_context=ctx,
        ...     exercise_name="ベンチプレス",
        ...     sets=[{"reps": 10, "weight": 50}, {"reps": 8, "weight": 55}],
        ...     total_sets=2,
        ...     category="strength",
        ...     muscle_group="chest",
        ...     total_reps=18,
        ...     total_volume=950.0,
        ... )

        # 有酸素運動の記録
        >>> await create_exercise_log(
        ...     tool_context=ctx,
        ...     exercise_name="ランニング",
        ...     sets=[{"duration": 1800, "distance": 5.0}],
        ...     total_sets=1,
        ...     category="cardio",
        ...     total_duration=1800,
        ...     total_distance=5.0,
        ... )
    """
    user_id = tool_context.user_id

    try:
        # recorded_at が指定されている場合は datetime に変換
        recorded_at_dt = None
        if recorded_at:
            try:
                recorded_at_dt = datetime.fromisoformat(recorded_at)
            except ValueError as e:
                logger.warning(
                    "recorded_at の解析に失敗、現在時刻を使用します",
                    recorded_at=recorded_at,
                    error=str(e),
                )

        async with get_async_session() as session:
            repo = ExerciseLogRepository(session)

            # 運動記録を作成
            log = await repo.create_log(
                user_id=user_id,
                exercise_name=exercise_name,
                sets=sets,
                total_sets=total_sets,
                category=category,
                muscle_group=muscle_group,
                total_reps=total_reps,
                total_duration=total_duration,
                total_distance=total_distance,
                total_volume=total_volume,
                note=note,
                recorded_at=recorded_at_dt,
            )

            logger.info(
                "運動記録を作成しました",
                user_id=user_id,
                log_id=log.id,
                exercise_name=exercise_name,
                total_sets=total_sets,
            )

            return {
                "status": "success",
                "message": f"運動記録を作成しました: {exercise_name}",
                "log_id": log.id,
                "exercise_name": log.exercise_name,
                "total_sets": log.total_sets,
                "recorded_at": log.recorded_at.isoformat(),
            }

    except Exception as e:
        logger.error(
            "運動記録の作成に失敗しました",
            user_id=user_id,
            exercise_name=exercise_name,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"運動記録の作成中にエラーが発生しました: {str(e)}",
        }


async def get_exercise_logs(
    tool_context: ToolContext,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    """ユーザーの運動記録を取得する。

    Args:
        tool_context: ADK が提供する ToolContext
        limit: 取得件数の上限（デフォルト: 10）
        offset: 取得開始位置（デフォルト: 0）

    Returns:
        取得結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - logs: 運動記録のリスト（取得時のみ）
        - total_count: 取得した記録数（取得時のみ）

    Examples:
        # 最新 10 件を取得
        >>> await get_exercise_logs(tool_context=ctx)

        # 最新 20 件を取得
        >>> await get_exercise_logs(tool_context=ctx, limit=20)

        # 11 件目から 10 件取得（ページネーション）
        >>> await get_exercise_logs(tool_context=ctx, limit=10, offset=10)
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = ExerciseLogRepository(session)

            # 運動記録を取得（記録日時の降順）
            logs = await repo.get_by_user_id(user_id, limit=limit, offset=offset)

            if not logs:
                logger.info("運動記録が見つかりません", user_id=user_id)
                return {
                    "status": "not_found",
                    "message": "運動記録がありません。",
                    "logs": [],
                    "total_count": 0,
                }

            logger.info(
                "運動記録を取得しました",
                user_id=user_id,
                count=len(logs),
                limit=limit,
                offset=offset,
            )

            return {
                "status": "success",
                "message": f"{len(logs)} 件の運動記録を取得しました。",
                "logs": [
                    {
                        "id": log.id,
                        "exercise_name": log.exercise_name,
                        "sets": log.sets,
                        "category": log.category,
                        "muscle_group": log.muscle_group,
                        "total_sets": log.total_sets,
                        "total_reps": log.total_reps,
                        "total_duration": log.total_duration,
                        "total_distance": log.total_distance,
                        "total_volume": log.total_volume,
                        "note": log.note,
                        "recorded_at": log.recorded_at.isoformat(),
                        "created_at": log.created_at.isoformat(),
                    }
                    for log in logs
                ],
                "total_count": len(logs),
            }

    except Exception as e:
        logger.error(
            "運動記録の取得に失敗しました",
            user_id=user_id,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"運動記録の取得中にエラーが発生しました: {str(e)}",
        }


async def get_exercise_logs_by_name(
    tool_context: ToolContext,
    exercise_name: str,
    limit: int = 10,
) -> dict:
    """特定の運動名で運動記録を取得する。

    Args:
        tool_context: ADK が提供する ToolContext
        exercise_name: 運動名（例: ベンチプレス、スクワット）
        limit: 取得件数の上限（デフォルト: 10）

    Returns:
        取得結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - exercise_name: 検索した運動名
        - logs: 運動記録のリスト（取得時のみ）
        - total_count: 取得した記録数（取得時のみ）

    Examples:
        # ベンチプレスの記録を取得
        >>> await get_exercise_logs_by_name(
        ...     tool_context=ctx,
        ...     exercise_name="ベンチプレス"
        ... )

        # ランニングの記録を最新 5 件取得
        >>> await get_exercise_logs_by_name(
        ...     tool_context=ctx,
        ...     exercise_name="ランニング",
        ...     limit=5
        ... )
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = ExerciseLogRepository(session)

            # 特定の運動名で記録を取得（記録日時の降順）
            logs = await repo.get_by_user_and_exercise(
                user_id=user_id,
                exercise_name=exercise_name,
                limit=limit,
            )

            if not logs:
                logger.info(
                    "指定された運動の記録が見つかりません",
                    user_id=user_id,
                    exercise_name=exercise_name,
                )
                return {
                    "status": "not_found",
                    "message": f"「{exercise_name}」の運動記録がありません。",
                    "exercise_name": exercise_name,
                    "logs": [],
                    "total_count": 0,
                }

            logger.info(
                "運動記録を取得しました",
                user_id=user_id,
                exercise_name=exercise_name,
                count=len(logs),
            )

            return {
                "status": "success",
                "message": f"「{exercise_name}」の運動記録を {len(logs)} 件取得しました。",
                "exercise_name": exercise_name,
                "logs": [
                    {
                        "id": log.id,
                        "exercise_name": log.exercise_name,
                        "sets": log.sets,
                        "category": log.category,
                        "muscle_group": log.muscle_group,
                        "total_sets": log.total_sets,
                        "total_reps": log.total_reps,
                        "total_duration": log.total_duration,
                        "total_distance": log.total_distance,
                        "total_volume": log.total_volume,
                        "note": log.note,
                        "recorded_at": log.recorded_at.isoformat(),
                        "created_at": log.created_at.isoformat(),
                    }
                    for log in logs
                ],
                "total_count": len(logs),
            }

    except Exception as e:
        logger.error(
            "運動記録の取得に失敗しました",
            user_id=user_id,
            exercise_name=exercise_name,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"運動記録の取得中にエラーが発生しました: {str(e)}",
        }


async def get_exercise_logs_by_date_range(
    tool_context: ToolContext,
    start_date: str,
    end_date: str,
    exercise_name: str | None = None,
    limit: int | None = None,
) -> dict:
    """日付範囲で運動記録を取得する。

    Args:
        tool_context: ADK が提供する ToolContext
        start_date: 開始日時（ISO 8601 形式、例: "2026-01-01T00:00:00"）
        end_date: 終了日時（ISO 8601 形式、例: "2026-01-31T23:59:59"）
        exercise_name: 運動名（省略時は全運動種目）
        limit: 取得件数の上限（省略時は制限なし）

    Returns:
        取得結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - start_date: 開始日時
        - end_date: 終了日時
        - exercise_name: 検索した運動名（指定時のみ）
        - logs: 運動記録のリスト（取得時のみ）
        - total_count: 取得した記録数（取得時のみ）

    Examples:
        # 2026年1月の全運動記録を取得
        >>> await get_exercise_logs_by_date_range(
        ...     tool_context=ctx,
        ...     start_date="2026-01-01T00:00:00",
        ...     end_date="2026-01-31T23:59:59"
        ... )

        # 2026年1月のランニング記録のみ取得
        >>> await get_exercise_logs_by_date_range(
        ...     tool_context=ctx,
        ...     start_date="2026-01-01T00:00:00",
        ...     end_date="2026-01-31T23:59:59",
        ...     exercise_name="ランニング"
        ... )

        # 過去7日間の記録を最大20件取得
        >>> await get_exercise_logs_by_date_range(
        ...     tool_context=ctx,
        ...     start_date="2026-01-24T00:00:00",
        ...     end_date="2026-01-30T23:59:59",
        ...     limit=20
        ... )
    """
    user_id = tool_context.user_id

    try:
        # 日付文字列を datetime に変換
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        except ValueError as e:
            logger.warning(
                "日付の解析に失敗しました",
                start_date=start_date,
                end_date=end_date,
                error=str(e),
            )
            return {
                "status": "error",
                "message": f"日付の形式が正しくありません。ISO 8601 形式（例: 2026-01-01T00:00:00）で指定してください。",
            }

        # 日付の妥当性チェック
        if start_dt > end_dt:
            return {
                "status": "error",
                "message": "開始日時は終了日時より前である必要があります。",
            }

        async with get_async_session() as session:
            repo = ExerciseLogRepository(session)

            # 日付範囲で記録を取得（記録日時の降順）
            logs = await repo.get_by_user_and_date_range(
                user_id=user_id,
                start_date=start_dt,
                end_date=end_dt,
                exercise_name=exercise_name,
                limit=limit,
            )

            if not logs:
                logger.info(
                    "指定された期間の運動記録が見つかりません",
                    user_id=user_id,
                    start_date=start_date,
                    end_date=end_date,
                    exercise_name=exercise_name,
                )
                result = {
                    "status": "not_found",
                    "message": f"{start_date} から {end_date} の期間に運動記録がありません。",
                    "start_date": start_date,
                    "end_date": end_date,
                    "logs": [],
                    "total_count": 0,
                }
                if exercise_name:
                    result["exercise_name"] = exercise_name
                    result["message"] = f"{start_date} から {end_date} の期間に「{exercise_name}」の運動記録がありません。"
                return result

            logger.info(
                "運動記録を取得しました",
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                exercise_name=exercise_name,
                count=len(logs),
            )

            message = f"{start_date} から {end_date} の期間の運動記録を {len(logs)} 件取得しました。"
            if exercise_name:
                message = f"{start_date} から {end_date} の期間の「{exercise_name}」の運動記録を {len(logs)} 件取得しました。"

            result = {
                "status": "success",
                "message": message,
                "start_date": start_date,
                "end_date": end_date,
                "logs": [
                    {
                        "id": log.id,
                        "exercise_name": log.exercise_name,
                        "sets": log.sets,
                        "category": log.category,
                        "muscle_group": log.muscle_group,
                        "total_sets": log.total_sets,
                        "total_reps": log.total_reps,
                        "total_duration": log.total_duration,
                        "total_distance": log.total_distance,
                        "total_volume": log.total_volume,
                        "note": log.note,
                        "recorded_at": log.recorded_at.isoformat(),
                        "created_at": log.created_at.isoformat(),
                    }
                    for log in logs
                ],
                "total_count": len(logs),
            }
            if exercise_name:
                result["exercise_name"] = exercise_name

            return result

    except Exception as e:
        logger.error(
            "運動記録の取得に失敗しました",
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            exercise_name=exercise_name,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"運動記録の取得中にエラーが発生しました: {str(e)}",
        }
