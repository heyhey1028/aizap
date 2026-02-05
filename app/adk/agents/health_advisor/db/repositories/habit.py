"""Habit リポジトリ

運動・食事習慣計画の CRUD 操作を提供する。
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Habit
from .base import BaseRepository


class HabitRepository(BaseRepository[Habit]):
    """Habit リポジトリ"""

    def __init__(self, session: AsyncSession):
        """リポジトリを初期化する。

        Args:
            session: SQLAlchemy 非同期セッション
        """
        super().__init__(session, Habit)

    async def get_by_user_id(
        self,
        user_id: str,
        habit_type: str | None = None,
        is_active: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Habit]:
        """ユーザー ID で習慣を取得する。

        Args:
            user_id: ユーザー ID
            habit_type: 習慣タイプでフィルタ（"exercise" または "meal"）
            is_active: アクティブ状態でフィルタ
            limit: 取得件数の上限
            offset: 取得開始位置

        Returns:
            Habit のリスト（開始日の降順）
        """
        stmt = select(Habit).where(Habit.user_id == user_id)

        if habit_type is not None:
            stmt = stmt.where(Habit.habit_type == habit_type)
        if is_active is not None:
            stmt = stmt.where(Habit.is_active == is_active)

        stmt = stmt.order_by(Habit.start_date.desc()).limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_goal_id(
        self,
        goal_id: str,
        is_active: bool | None = None,
        limit: int = 100,
    ) -> list[Habit]:
        """目標 ID で習慣を取得する。

        Args:
            goal_id: 目標 ID
            is_active: アクティブ状態でフィルタ
            limit: 取得件数の上限

        Returns:
            Habit のリスト（優先度の降順、開始日の降順）
        """
        stmt = select(Habit).where(Habit.goal_id == goal_id)

        if is_active is not None:
            stmt = stmt.where(Habit.is_active == is_active)

        stmt = stmt.order_by(Habit.priority.desc(), Habit.start_date.desc()).limit(limit)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_routine_id(
        self,
        user_id: str,
        routine_id: str,
        is_active: bool | None = None,
    ) -> list[Habit]:
        """ルーティン ID で習慣を取得する。

        Args:
            user_id: ユーザー ID
            routine_id: ルーティン ID
            is_active: アクティブ状態でフィルタ

        Returns:
            Habit のリスト（ルーティン内の順序順）
        """
        stmt = (
            select(Habit)
            .where(Habit.user_id == user_id)
            .where(Habit.routine_id == routine_id)
        )

        if is_active is not None:
            stmt = stmt.where(Habit.is_active == is_active)

        stmt = stmt.order_by(Habit.order_in_routine.asc())

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_habit(
        self,
        user_id: str,
        habit_type: str,
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
        meal_type: str | None = None,
        target_calories: int | None = None,
        target_proteins: int | None = None,
        target_fats: int | None = None,
        target_carbohydrates: int | None = None,
        meal_guidelines: str | None = None,
        days_of_week: list[str] | None = None,
        time_of_day: str | None = None,
        is_active: bool = True,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        notes: str | None = None,
        priority: int | None = None,
    ) -> Habit:
        """習慣を作成する。

        Args:
            user_id: ユーザー ID
            habit_type: 習慣タイプ（"exercise" または "meal"）
            title: タイトル
            frequency: 頻度（"daily", "weekly", "custom"）
            goal_id: 目標 ID（オプション）
            description: 説明
            routine_id: ルーティン ID
            routine_name: ルーティン名
            order_in_routine: ルーティン内の順序
            exercise_name: 運動名（運動習慣の場合）
            category: カテゴリ
            muscle_group: 筋肉群
            target_sets: 目標セット数
            target_reps: 目標レップ数
            target_duration: 目標時間（秒）
            target_distance: 目標距離（km）
            target_weight: 目標重量（kg）
            meal_type: 食事タイプ（食事習慣の場合）
            target_calories: 目標カロリー
            target_proteins: 目標タンパク質（g）
            target_fats: 目標脂質（g）
            target_carbohydrates: 目標炭水化物（g）
            meal_guidelines: 食事ガイドライン
            days_of_week: 曜日リスト（["monday", "wednesday"]等）
            time_of_day: 時刻（"HH:MM"形式）
            is_active: アクティブ状態
            start_date: 開始日（省略時は現在時刻）
            end_date: 終了日
            notes: メモ
            priority: 優先度（1-5）

        Returns:
            作成された Habit
        """
        habit_id = str(uuid.uuid4())
        return await self.create(
            id=habit_id,
            user_id=user_id,
            goal_id=goal_id,
            habit_type=habit_type,
            title=title,
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
            meal_type=meal_type,
            target_calories=target_calories,
            target_proteins=target_proteins,
            target_fats=target_fats,
            target_carbohydrates=target_carbohydrates,
            meal_guidelines=meal_guidelines,
            frequency=frequency,
            days_of_week=days_of_week,
            time_of_day=time_of_day,
            is_active=is_active,
            start_date=start_date or datetime.now(),
            end_date=end_date,
            notes=notes,
            priority=priority,
        )

    async def update_habit(
        self,
        habit_id: str,
        **kwargs: Any,
    ) -> Habit | None:
        """習慣を更新する。

        Args:
            habit_id: 習慣 ID
            **kwargs: 更新するフィールド値

        Returns:
            更新された Habit、存在しない場合は None
        """
        return await self.update(habit_id, **kwargs)

    async def deactivate_habit(self, habit_id: str) -> Habit | None:
        """習慣を非アクティブ化する。

        Args:
            habit_id: 習慣 ID

        Returns:
            更新された Habit、存在しない場合は None
        """
        return await self.update(habit_id, is_active=False)

    async def activate_habit(self, habit_id: str) -> Habit | None:
        """習慣をアクティブ化する。

        Args:
            habit_id: 習慣 ID

        Returns:
            更新された Habit、存在しない場合は None
        """
        return await self.update(habit_id, is_active=True)
