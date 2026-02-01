"""UserSession リポジトリ

ユーザーセッションの CRUD 操作を提供する。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import UserSession
from .base import BaseRepository


class UserSessionRepository(BaseRepository[UserSession]):
    """UserSession リポジトリ"""

    def __init__(self, session: AsyncSession):
        """リポジトリを初期化する。

        Args:
            session: SQLAlchemy 非同期セッション
        """
        super().__init__(session, UserSession)

    async def get_by_user_id(self, user_id: str) -> UserSession | None:
        """ユーザー ID でセッションを取得する。

        Args:
            user_id: ユーザー ID（LINE ユーザー ID など）

        Returns:
            UserSession、存在しない場合は None
        """
        return await self.get_by_id(user_id)

    async def upsert(self, user_id: str, session_id: str) -> UserSession:
        """ユーザーセッションを作成または更新する。

        Args:
            user_id: ユーザー ID
            session_id: セッション ID

        Returns:
            作成または更新された UserSession
        """
        existing = await self.get_by_user_id(user_id)
        if existing is not None:
            # 既存のセッションを更新
            return await self.update(user_id, session_id=session_id)  # type: ignore
        else:
            # 新規作成
            return await self.create(user_id=user_id, session_id=session_id)
