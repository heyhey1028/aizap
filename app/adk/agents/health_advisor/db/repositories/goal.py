"""Goal リポジトリ

健康目標の CRUD 操作を提供する。
"""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Goal
from .base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    """Goal リポジトリ"""

    def __init__(self, session: AsyncSession):
        """リポジトリを初期化する。

        Args:
            session: SQLAlchemy 非同期セッション
        """
        super().__init__(session, Goal)

    async def get_by_user_id(self, user_id: str) -> Goal | None:
        """ユーザー ID で最新の目標を取得する。

        Args:
            user_id: ユーザー ID

        Returns:
            最新の Goal、存在しない場合は None
        """
        stmt = (
            select(Goal)
            .where(Goal.user_id == user_id)
            .order_by(Goal.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, user_id: str) -> list[Goal]:
        """ユーザー ID で全ての目標を取得する。

        Args:
            user_id: ユーザー ID

        Returns:
            Goal のリスト（作成日時の降順）
        """
        stmt = (
            select(Goal)
            .where(Goal.user_id == user_id)
            .order_by(Goal.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_goal(self, user_id: str, details: str, habits: str) -> Goal:
        """健康目標を作成する。

        Args:
            user_id: ユーザー ID
            details: 目標の詳細
            habits: 習慣

        Returns:
            作成された Goal
        """
        goal_id = str(uuid.uuid4())
        return await self.create(
            id=goal_id,
            user_id=user_id,
            details=details,
            habits=habits,
        )
