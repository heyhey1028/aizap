"""ExerciseLog リポジトリ

運動ログの CRUD 操作を提供する。
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ExerciseLog
from .base import BaseRepository


class ExerciseLogRepository(BaseRepository[ExerciseLog]):
    """ExerciseLog リポジトリ"""

    def __init__(self, session: AsyncSession):
        """リポジトリを初期化する。

        Args:
            session: SQLAlchemy 非同期セッション
        """
        super().__init__(session, ExerciseLog)

    async def get_by_user_id(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[ExerciseLog]:
        """ユーザー ID で運動ログを取得する。

        Args:
            user_id: ユーザー ID
            limit: 取得件数の上限
            offset: 取得開始位置

        Returns:
            ExerciseLog のリスト（記録日時の降順）
        """
        stmt = (
            select(ExerciseLog)
            .where(ExerciseLog.user_id == user_id)
            .order_by(ExerciseLog.recorded_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_exercise(
        self,
        user_id: str,
        exercise_name: str,
        limit: int = 10,
    ) -> list[ExerciseLog]:
        """ユーザー ID と運動名で運動ログを取得する。

        Args:
            user_id: ユーザー ID
            exercise_name: 運動名
            limit: 取得件数の上限

        Returns:
            ExerciseLog のリスト（記録日時の降順）
        """
        stmt = (
            select(ExerciseLog)
            .where(ExerciseLog.user_id == user_id)
            .where(ExerciseLog.exercise_name == exercise_name)
            .order_by(ExerciseLog.recorded_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_log(
        self,
        user_id: str,
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
        recorded_at: datetime | None = None,
    ) -> ExerciseLog:
        """運動ログを作成する。

        Args:
            user_id: ユーザー ID
            exercise_name: 運動名
            sets: セット情報（JSON）
            total_sets: 総セット数
            category: カテゴリ
            muscle_group: 筋肉群
            total_reps: 総レップ数
            total_duration: 総時間（秒）
            total_distance: 総距離（km）
            total_volume: 総ボリューム（kg）
            note: メモ
            recorded_at: 記録日時（省略時は現在時刻）

        Returns:
            作成された ExerciseLog
        """
        log_id = str(uuid.uuid4())
        return await self.create(
            id=log_id,
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
            recorded_at=recorded_at or datetime.now(),
        )
