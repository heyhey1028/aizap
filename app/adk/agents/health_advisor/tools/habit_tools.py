"""習慣計画（Habit）操作ツール

Habits テーブルへの書き込みと読み込みを行うツールを提供する。
"""

from datetime import datetime
from typing import Any

from google.adk.tools import ToolContext

from ..db.config import get_async_session
from ..db.repositories import HabitRepository
from ..logger import get_logger

logger = get_logger(__name__)


async def create_exercise_habit(
    tool_context: ToolContext,
    title: str,
    frequency: str,
    goal_id: str | None = None,
    description: str | None = None,
    routine_id: str | None = None,
    routine_name: str | None = None,
    order_in_routine: int | None = None,
    exercise_name: str | None = None,
    category: str | None = None,
    muscle_group: str | None = None,
    target_sets: int | None = None,
    target_reps: int | None = None,
    target_duration: int | None = None,
    target_distance: float | None = None,
    target_weight: float | None = None,
    days_of_week: list[str] | None = None,
    time_of_day: str | None = None,
    is_active: bool = True,
    start_date: str | None = None,
    end_date: str | None = None,
    notes: str | None = None,
    priority: int | None = None,
) -> dict:
    """運動習慣計画を作成する。

    Args:
        tool_context: ADK が提供する ToolContext
        title: タイトル（例: ベンチプレス、モーニングランニング）
        frequency: 頻度（"daily", "weekly", "custom"）
        goal_id: 関連する目標 ID（オプション）
        description: 説明
        routine_id: ルーティン ID（複数の習慣をグループ化）
        routine_name: ルーティン名
        order_in_routine: ルーティン内の順序
        exercise_name: 運動名（例: ベンチプレス、ランニング）
        category: カテゴリ（例: strength, cardio, flexibility）
        muscle_group: 対象筋肉群（例: chest, legs, back）
        target_sets: 目標セット数
        target_reps: 目標レップ数
        target_duration: 目標時間（秒）
        target_distance: 目標距離（km）
        target_weight: 目標重量（kg）
        days_of_week: 曜日リスト（例: ["monday", "wednesday", "friday"]）
        time_of_day: 時刻（HH:MM 形式、例: "18:00"）
        is_active: アクティブ状態（デフォルト: True）
        start_date: 開始日時（ISO 8601 形式、省略時は現在時刻）
        end_date: 終了日時（ISO 8601 形式）
        notes: メモ・備考
        priority: 優先度（1-5）

    Returns:
        作成結果を含む辞書:
        - status: "success" または "error"
        - message: 結果メッセージ
        - habit_id: 作成された習慣計画の ID（成功時のみ）
        - habit_type: "exercise"（成功時のみ）
        - title: タイトル（成功時のみ）

    Examples:
        # 筋トレ習慣の作成
        >>> await create_exercise_habit(
        ...     tool_context=ctx,
        ...     title="ベンチプレス",
        ...     frequency="weekly",
        ...     exercise_name="ベンチプレス",
        ...     category="strength",
        ...     muscle_group="chest",
        ...     target_sets=3,
        ...     target_reps=10,
        ...     target_weight=60.0,
        ...     days_of_week=["monday", "thursday"],
        ...     time_of_day="18:00",
        ... )

        # 有酸素運動習慣の作成
        >>> await create_exercise_habit(
        ...     tool_context=ctx,
        ...     title="モーニングランニング",
        ...     frequency="daily",
        ...     exercise_name="ランニング",
        ...     category="cardio",
        ...     target_duration=1800,
        ...     target_distance=5.0,
        ...     time_of_day="06:00",
        ... )
    """
    user_id = tool_context.user_id

    try:
        # 日付文字列を datetime に変換
        start_date_dt = None
        end_date_dt = None

        if start_date:
            try:
                start_date_dt = datetime.fromisoformat(start_date)
            except ValueError as e:
                logger.warning(
                    "start_date の解析に失敗、現在時刻を使用します",
                    start_date=start_date,
                    error=str(e),
                )

        if end_date:
            try:
                end_date_dt = datetime.fromisoformat(end_date)
            except ValueError as e:
                logger.warning(
                    "end_date の解析に失敗しました",
                    end_date=end_date,
                    error=str(e),
                )
                end_date_dt = None

        async with get_async_session() as session:
            repo = HabitRepository(session)

            # 運動習慣計画を作成
            habit = await repo.create_habit(
                user_id=user_id,
                habit_type="exercise",
                title=title,
                frequency=frequency,
                goal_id=goal_id,
                description=description,
                routine_id=routine_id,
                routine_name=routine_name,
                order_in_routine=order_in_routine,
                exercise_name=exercise_name,
                category=category,
                muscle_group=muscle_group,
                target_sets=target_sets,
                target_reps=target_reps,
                target_duration=target_duration,
                target_distance=target_distance,
                target_weight=target_weight,
                days_of_week=days_of_week,
                time_of_day=time_of_day,
                is_active=is_active,
                start_date=start_date_dt,
                end_date=end_date_dt,
                notes=notes,
                priority=priority,
            )

            logger.info(
                "運動習慣計画を作成しました",
                user_id=user_id,
                habit_id=habit.id,
                title=title,
            )

            return {
                "status": "success",
                "message": f"運動習慣計画を作成しました: {title}",
                "habit_id": habit.id,
                "habit_type": habit.habit_type,
                "title": habit.title,
                "frequency": habit.frequency,
                "is_active": habit.is_active,
            }

    except Exception as e:
        logger.error(
            "運動習慣計画の作成に失敗しました",
            user_id=user_id,
            title=title,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"運動習慣計画の作成中にエラーが発生しました: {str(e)}",
        }


async def create_meal_habit(
    tool_context: ToolContext,
    title: str,
    frequency: str,
    goal_id: str | None = None,
    description: str | None = None,
    routine_id: str | None = None,
    routine_name: str | None = None,
    order_in_routine: int | None = None,
    meal_type: str | None = None,
    target_calories: int | None = None,
    target_proteins: int | None = None,
    target_fats: int | None = None,
    target_carbohydrates: int | None = None,
    meal_guidelines: str | None = None,
    days_of_week: list[str] | None = None,
    time_of_day: str | None = None,
    is_active: bool = True,
    start_date: str | None = None,
    end_date: str | None = None,
    notes: str | None = None,
    priority: int | None = None,
) -> dict:
    """食事習慣計画を作成する。

    Args:
        tool_context: ADK が提供する ToolContext
        title: タイトル（例: 朝食、プロテイン摂取）
        frequency: 頻度（"daily", "weekly", "custom"）
        goal_id: 関連する目標 ID（オプション）
        description: 説明
        routine_id: ルーティン ID（複数の習慣をグループ化）
        routine_name: ルーティン名
        order_in_routine: ルーティン内の順序
        meal_type: 食事タイプ（例: breakfast, lunch, dinner, snack）
        target_calories: 目標カロリー
        target_proteins: 目標タンパク質（g）
        target_fats: 目標脂質（g）
        target_carbohydrates: 目標炭水化物（g）
        meal_guidelines: 食事ガイドライン
        days_of_week: 曜日リスト（例: ["monday", "wednesday", "friday"]）
        time_of_day: 時刻（HH:MM 形式、例: "07:00"）
        is_active: アクティブ状態（デフォルト: True）
        start_date: 開始日時（ISO 8601 形式、省略時は現在時刻）
        end_date: 終了日時（ISO 8601 形式）
        notes: メモ・備考
        priority: 優先度（1-5）

    Returns:
        作成結果を含む辞書:
        - status: "success" または "error"
        - message: 結果メッセージ
        - habit_id: 作成された習慣計画の ID（成功時のみ）
        - habit_type: "meal"（成功時のみ）
        - title: タイトル（成功時のみ）

    Examples:
        # 朝食習慣の作成
        >>> await create_meal_habit(
        ...     tool_context=ctx,
        ...     title="朝食",
        ...     frequency="daily",
        ...     meal_type="breakfast",
        ...     target_calories=500,
        ...     target_proteins=30,
        ...     target_fats=15,
        ...     target_carbohydrates=50,
        ...     time_of_day="07:00",
        ... )

        # プロテイン摂取習慣の作成
        >>> await create_meal_habit(
        ...     tool_context=ctx,
        ...     title="トレーニング後プロテイン",
        ...     frequency="weekly",
        ...     meal_type="snack",
        ...     target_calories=150,
        ...     target_proteins=25,
        ...     days_of_week=["monday", "wednesday", "friday"],
        ...     time_of_day="19:00",
        ... )
    """
    user_id = tool_context.user_id

    try:
        # 日付文字列を datetime に変換
        start_date_dt = None
        end_date_dt = None

        if start_date:
            try:
                start_date_dt = datetime.fromisoformat(start_date)
            except ValueError as e:
                logger.warning(
                    "start_date の解析に失敗、現在時刻を使用します",
                    start_date=start_date,
                    error=str(e),
                )

        if end_date:
            try:
                end_date_dt = datetime.fromisoformat(end_date)
            except ValueError as e:
                logger.warning(
                    "end_date の解析に失敗しました",
                    end_date=end_date,
                    error=str(e),
                )
                end_date_dt = None

        async with get_async_session() as session:
            repo = HabitRepository(session)

            # 食事習慣計画を作成
            habit = await repo.create_habit(
                user_id=user_id,
                habit_type="meal",
                title=title,
                frequency=frequency,
                goal_id=goal_id,
                description=description,
                routine_id=routine_id,
                routine_name=routine_name,
                order_in_routine=order_in_routine,
                meal_type=meal_type,
                target_calories=target_calories,
                target_proteins=target_proteins,
                target_fats=target_fats,
                target_carbohydrates=target_carbohydrates,
                meal_guidelines=meal_guidelines,
                days_of_week=days_of_week,
                time_of_day=time_of_day,
                is_active=is_active,
                start_date=start_date_dt,
                end_date=end_date_dt,
                notes=notes,
                priority=priority,
            )

            logger.info(
                "食事習慣計画を作成しました",
                user_id=user_id,
                habit_id=habit.id,
                title=title,
            )

            return {
                "status": "success",
                "message": f"食事習慣計画を作成しました: {title}",
                "habit_id": habit.id,
                "habit_type": habit.habit_type,
                "title": habit.title,
                "frequency": habit.frequency,
                "is_active": habit.is_active,
            }

    except Exception as e:
        logger.error(
            "食事習慣計画の作成に失敗しました",
            user_id=user_id,
            title=title,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"食事習慣計画の作成中にエラーが発生しました: {str(e)}",
        }


async def get_habits(
    tool_context: ToolContext,
    habit_type: str | None = None,
    is_active: bool | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """ユーザーの習慣計画を取得する。

    Args:
        tool_context: ADK が提供する ToolContext
        habit_type: 習慣タイプでフィルタ（"exercise" または "meal"）
        is_active: アクティブ状態でフィルタ（True: アクティブのみ、False: 非アクティブのみ）
        limit: 取得件数の上限（デフォルト: 100）
        offset: 取得開始位置（デフォルト: 0）

    Returns:
        取得結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - habits: 習慣計画のリスト（取得時のみ）
        - total_count: 取得した記録数（取得時のみ）

    Examples:
        # 全習慣を取得
        >>> await get_habits(tool_context=ctx)

        # アクティブな運動習慣のみ取得
        >>> await get_habits(
        ...     tool_context=ctx,
        ...     habit_type="exercise",
        ...     is_active=True
        ... )
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = HabitRepository(session)

            # 習慣計画を取得（開始日の降順）
            habits = await repo.get_by_user_id(
                user_id=user_id,
                habit_type=habit_type,
                is_active=is_active,
                limit=limit,
                offset=offset,
            )

            if not habits:
                logger.info("習慣計画が見つかりません", user_id=user_id)
                return {
                    "status": "not_found",
                    "message": "習慣計画がありません。",
                    "habits": [],
                    "total_count": 0,
                }

            logger.info(
                "習慣計画を取得しました",
                user_id=user_id,
                count=len(habits),
                habit_type=habit_type,
                is_active=is_active,
            )

            return {
                "status": "success",
                "message": f"{len(habits)} 件の習慣計画を取得しました。",
                "habits": [
                    {
                        "id": habit.id,
                        "habit_type": habit.habit_type,
                        "title": habit.title,
                        "description": habit.description,
                        "routine_id": habit.routine_id,
                        "routine_name": habit.routine_name,
                        "order_in_routine": habit.order_in_routine,
                        "exercise_name": habit.exercise_name,
                        "category": habit.category,
                        "muscle_group": habit.muscle_group,
                        "target_sets": habit.target_sets,
                        "target_reps": habit.target_reps,
                        "target_duration": habit.target_duration,
                        "target_distance": habit.target_distance,
                        "target_weight": habit.target_weight,
                        "meal_type": habit.meal_type,
                        "target_calories": habit.target_calories,
                        "target_proteins": habit.target_proteins,
                        "target_fats": habit.target_fats,
                        "target_carbohydrates": habit.target_carbohydrates,
                        "meal_guidelines": habit.meal_guidelines,
                        "frequency": habit.frequency,
                        "days_of_week": habit.days_of_week,
                        "time_of_day": habit.time_of_day,
                        "is_active": habit.is_active,
                        "start_date": habit.start_date.isoformat(),
                        "end_date": habit.end_date.isoformat() if habit.end_date else None,
                        "notes": habit.notes,
                        "priority": habit.priority,
                        "created_at": habit.created_at.isoformat(),
                        "updated_at": habit.updated_at.isoformat(),
                    }
                    for habit in habits
                ],
                "total_count": len(habits),
            }

    except Exception as e:
        logger.error(
            "習慣計画の取得に失敗しました",
            user_id=user_id,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"習慣計画の取得中にエラーが発生しました: {str(e)}",
        }


async def get_habits_by_goal(
    tool_context: ToolContext,
    goal_id: str,
    is_active: bool | None = None,
    limit: int = 100,
) -> dict:
    """目標 ID に紐づく習慣計画を取得する。

    Args:
        tool_context: ADK が提供する ToolContext
        goal_id: 目標 ID
        is_active: アクティブ状態でフィルタ
        limit: 取得件数の上限（デフォルト: 100）

    Returns:
        取得結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - goal_id: 検索した目標 ID
        - habits: 習慣計画のリスト（取得時のみ）
        - total_count: 取得した記録数（取得時のみ）

    Examples:
        >>> await get_habits_by_goal(
        ...     tool_context=ctx,
        ...     goal_id="goal-123",
        ...     is_active=True
        ... )
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = HabitRepository(session)

            # 目標 ID で習慣計画を取得
            habits = await repo.get_by_goal_id(
                goal_id=goal_id,
                is_active=is_active,
                limit=limit,
            )

            if not habits:
                logger.info(
                    "指定された目標の習慣計画が見つかりません",
                    user_id=user_id,
                    goal_id=goal_id,
                )
                return {
                    "status": "not_found",
                    "message": f"目標 ID「{goal_id}」に関連する習慣計画がありません。",
                    "goal_id": goal_id,
                    "habits": [],
                    "total_count": 0,
                }

            logger.info(
                "習慣計画を取得しました",
                user_id=user_id,
                goal_id=goal_id,
                count=len(habits),
            )

            return {
                "status": "success",
                "message": f"目標に関連する習慣計画を {len(habits)} 件取得しました。",
                "goal_id": goal_id,
                "habits": [
                    {
                        "id": habit.id,
                        "habit_type": habit.habit_type,
                        "title": habit.title,
                        "description": habit.description,
                        "exercise_name": habit.exercise_name,
                        "category": habit.category,
                        "target_sets": habit.target_sets,
                        "target_reps": habit.target_reps,
                        "frequency": habit.frequency,
                        "is_active": habit.is_active,
                        "priority": habit.priority,
                        "start_date": habit.start_date.isoformat(),
                        "created_at": habit.created_at.isoformat(),
                    }
                    for habit in habits
                ],
                "total_count": len(habits),
            }

    except Exception as e:
        logger.error(
            "習慣計画の取得に失敗しました",
            user_id=user_id,
            goal_id=goal_id,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"習慣計画の取得中にエラーが発生しました: {str(e)}",
        }


async def get_habits_by_routine(
    tool_context: ToolContext,
    routine_id: str,
    is_active: bool | None = None,
) -> dict:
    """ルーティン ID に紐づく習慣計画を取得する。

    Args:
        tool_context: ADK が提供する ToolContext
        routine_id: ルーティン ID
        is_active: アクティブ状態でフィルタ

    Returns:
        取得結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - routine_id: 検索したルーティン ID
        - habits: 習慣計画のリスト（ルーティン内の順序順、取得時のみ）
        - total_count: 取得した記録数（取得時のみ）

    Examples:
        >>> await get_habits_by_routine(
        ...     tool_context=ctx,
        ...     routine_id="morning-routine",
        ...     is_active=True
        ... )
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = HabitRepository(session)

            # ルーティン ID で習慣計画を取得
            habits = await repo.get_by_routine_id(
                user_id=user_id,
                routine_id=routine_id,
                is_active=is_active,
            )

            if not habits:
                logger.info(
                    "指定されたルーティンの習慣計画が見つかりません",
                    user_id=user_id,
                    routine_id=routine_id,
                )
                return {
                    "status": "not_found",
                    "message": f"ルーティン ID「{routine_id}」に関連する習慣計画がありません。",
                    "routine_id": routine_id,
                    "habits": [],
                    "total_count": 0,
                }

            logger.info(
                "習慣計画を取得しました",
                user_id=user_id,
                routine_id=routine_id,
                count=len(habits),
            )

            return {
                "status": "success",
                "message": f"ルーティンに関連する習慣計画を {len(habits)} 件取得しました。",
                "routine_id": routine_id,
                "habits": [
                    {
                        "id": habit.id,
                        "habit_type": habit.habit_type,
                        "title": habit.title,
                        "order_in_routine": habit.order_in_routine,
                        "exercise_name": habit.exercise_name,
                        "category": habit.category,
                        "target_sets": habit.target_sets,
                        "target_reps": habit.target_reps,
                        "is_active": habit.is_active,
                        "created_at": habit.created_at.isoformat(),
                    }
                    for habit in habits
                ],
                "total_count": len(habits),
            }

    except Exception as e:
        logger.error(
            "習慣計画の取得に失敗しました",
            user_id=user_id,
            routine_id=routine_id,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"習慣計画の取得中にエラーが発生しました: {str(e)}",
        }


async def update_habit(
    tool_context: ToolContext,
    habit_id: str,
    **kwargs: Any,
) -> dict:
    """習慣計画を更新する。

    Args:
        tool_context: ADK が提供する ToolContext
        habit_id: 習慣計画 ID
        **kwargs: 更新するフィールド値（例: title, target_sets, is_active等）

    Returns:
        更新結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - habit_id: 更新された習慣計画の ID（成功時のみ）

    Examples:
        # タイトルを更新
        >>> await update_habit(
        ...     tool_context=ctx,
        ...     habit_id="habit-123",
        ...     title="新しいタイトル"
        ... )

        # 目標値を更新
        >>> await update_habit(
        ...     tool_context=ctx,
        ...     habit_id="habit-123",
        ...     target_sets=4,
        ...     target_reps=12
        ... )
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = HabitRepository(session)

            # 習慣計画を更新
            habit = await repo.update_habit(habit_id=habit_id, **kwargs)

            if not habit:
                logger.warning(
                    "習慣計画が見つかりません",
                    user_id=user_id,
                    habit_id=habit_id,
                )
                return {
                    "status": "not_found",
                    "message": f"習慣計画 ID「{habit_id}」が見つかりません。",
                }

            logger.info(
                "習慣計画を更新しました",
                user_id=user_id,
                habit_id=habit_id,
                updated_fields=list(kwargs.keys()),
            )

            return {
                "status": "success",
                "message": f"習慣計画を更新しました: {habit.title}",
                "habit_id": habit.id,
                "title": habit.title,
            }

    except Exception as e:
        logger.error(
            "習慣計画の更新に失敗しました",
            user_id=user_id,
            habit_id=habit_id,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"習慣計画の更新中にエラーが発生しました: {str(e)}",
        }


async def deactivate_habit(
    tool_context: ToolContext,
    habit_id: str,
) -> dict:
    """習慣計画を非アクティブ化する。

    Args:
        tool_context: ADK が提供する ToolContext
        habit_id: 習慣計画 ID

    Returns:
        更新結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - habit_id: 非アクティブ化された習慣計画の ID（成功時のみ）

    Examples:
        >>> await deactivate_habit(
        ...     tool_context=ctx,
        ...     habit_id="habit-123"
        ... )
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = HabitRepository(session)

            # 習慣計画を非アクティブ化
            habit = await repo.deactivate_habit(habit_id=habit_id)

            if not habit:
                logger.warning(
                    "習慣計画が見つかりません",
                    user_id=user_id,
                    habit_id=habit_id,
                )
                return {
                    "status": "not_found",
                    "message": f"習慣計画 ID「{habit_id}」が見つかりません。",
                }

            logger.info(
                "習慣計画を非アクティブ化しました",
                user_id=user_id,
                habit_id=habit_id,
                title=habit.title,
            )

            return {
                "status": "success",
                "message": f"習慣計画を非アクティブ化しました: {habit.title}",
                "habit_id": habit.id,
            }

    except Exception as e:
        logger.error(
            "習慣計画の非アクティブ化に失敗しました",
            user_id=user_id,
            habit_id=habit_id,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"習慣計画の非アクティブ化中にエラーが発生しました: {str(e)}",
        }


async def activate_habit(
    tool_context: ToolContext,
    habit_id: str,
) -> dict:
    """習慣計画をアクティブ化する。

    Args:
        tool_context: ADK が提供する ToolContext
        habit_id: 習慣計画 ID

    Returns:
        更新結果を含む辞書:
        - status: "success", "not_found", または "error"
        - message: 結果メッセージ
        - habit_id: アクティブ化された習慣計画の ID（成功時のみ）

    Examples:
        >>> await activate_habit(
        ...     tool_context=ctx,
        ...     habit_id="habit-123"
        ... )
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = HabitRepository(session)

            # 習慣計画をアクティブ化
            habit = await repo.activate_habit(habit_id=habit_id)

            if not habit:
                logger.warning(
                    "習慣計画が見つかりません",
                    user_id=user_id,
                    habit_id=habit_id,
                )
                return {
                    "status": "not_found",
                    "message": f"習慣計画 ID「{habit_id}」が見つかりません。",
                }

            logger.info(
                "習慣計画をアクティブ化しました",
                user_id=user_id,
                habit_id=habit_id,
                title=habit.title,
            )

            return {
                "status": "success",
                "message": f"習慣計画をアクティブ化しました: {habit.title}",
                "habit_id": habit.id,
            }

    except Exception as e:
        logger.error(
            "習慣計画のアクティブ化に失敗しました",
            user_id=user_id,
            habit_id=habit_id,
            error=str(e),
        )
        return {
            "status": "error",
            "message": f"習慣計画のアクティブ化中にエラーが発生しました: {str(e)}",
        }
