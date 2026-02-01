"""リポジトリ基底クラス

共通の CRUD 操作を提供する。
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base

# 型変数: SQLAlchemy モデル
ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """リポジトリ基底クラス

    各テーブルに対する共通の CRUD 操作を提供する。

    使用例:
        class GoalRepository(BaseRepository[Goal]):
            def __init__(self, session: AsyncSession):
                super().__init__(session, Goal)
    """

    def __init__(self, session: AsyncSession, model: type[ModelT]):
        """リポジトリを初期化する。

        Args:
            session: SQLAlchemy 非同期セッション
            model: 対象のモデルクラス
        """
        self._session = session
        self._model = model

    async def get_by_id(self, id: str) -> ModelT | None:
        """ID でレコードを取得する。

        Args:
            id: レコードの ID

        Returns:
            レコード、存在しない場合は None
        """
        return await self._session.get(self._model, id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """全レコードを取得する。

        Args:
            limit: 取得件数の上限
            offset: 取得開始位置

        Returns:
            レコードのリスト
        """
        stmt = select(self._model).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelT:
        """レコードを作成する。

        Args:
            **kwargs: モデルのフィールド値

        Returns:
            作成されたレコード
        """
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def update(self, id: str, **kwargs: Any) -> ModelT | None:
        """レコードを更新する。

        Args:
            id: レコードの ID
            **kwargs: 更新するフィールド値

        Returns:
            更新されたレコード、存在しない場合は None
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def delete(self, id: str) -> bool:
        """レコードを削除する。

        Args:
            id: レコードの ID

        Returns:
            削除に成功した場合は True、レコードが存在しない場合は False
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self._session.delete(instance)
        await self._session.flush()
        return True
