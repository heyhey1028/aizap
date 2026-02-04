"""DietLog リポジトリ

食事記録の CRUD 操作を提供する。
"""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DietLog
from .base import BaseRepository


class DietLogRepository(BaseRepository[DietLog]):
    """DietLog リポジトリ"""

    def __init__(self, session: AsyncSession):
        """リポジトリを初期化する。

        Args:
            session: SQLAlchemy 非同期セッション
        """
        super().__init__(session, DietLog)

    async def get_by_user_id(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[DietLog]:
        """ユーザー ID で食事記録を取得する。

        Args:
            user_id: ユーザー ID
            limit: 取得件数の上限
            offset: 取得開始位置

        Returns:
            DietLog のリスト（記録日時の降順）
        """
        stmt = (
            select(DietLog)
            .where(DietLog.user_id == user_id)
            .order_by(DietLog.recorded_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[DietLog]:
        """ユーザー ID と日付範囲で食事記録を取得する。

        1日のPFC達成率を計算する際に使用する。

        Args:
            user_id: ユーザー ID
            start_date: 開始日時
            end_date: 終了日時

        Returns:
            DietLog のリスト（記録日時の降順）
        """
        stmt = (
            select(DietLog)
            .where(DietLog.user_id == user_id)
            .where(DietLog.recorded_at >= start_date)
            .where(DietLog.recorded_at < end_date)
            .order_by(DietLog.recorded_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_log(
        self,
        user_id: str,
        name: str,
        meal_type: str,
        calories: float,
        proteins: float,
        fats: float,
        carbohydrates: float,
        estimation_source: str,
        recorded_at: datetime,
        sodium: float | None = None,
        fiber: float | None = None,
        sugar: float | None = None,
        is_user_corrected: bool = False,
        image_url: str | None = None,
        note: str | None = None,
    ) -> DietLog:
        """食事記録を作成する。

        Args:
            user_id: ユーザー ID
            name: 食事名
            meal_type: 食事種別 ("breakfast", "lunch", "dinner", "snack")
            calories: カロリー (kcal)
            proteins: タンパク質 (g)
            fats: 脂質 (g)
            carbohydrates: 炭水化物 (g)
            estimation_source: 推定元 ("text", "image")
            recorded_at: 食事日時
            sodium: 塩分 (mg)
            fiber: 食物繊維 (g)
            sugar: 糖質 (g)
            is_user_corrected: ユーザー修正有無
            image_url: 食事画像URL
            note: メモ

        Returns:
            作成された DietLog
        """
        log_id = str(uuid.uuid4())
        return await self.create(
            id=log_id,
            user_id=user_id,
            name=name,
            meal_type=meal_type,
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbohydrates=carbohydrates,
            estimation_source=estimation_source,
            recorded_at=recorded_at,
            sodium=sodium,
            fiber=fiber,
            sugar=sugar,
            is_user_corrected=is_user_corrected,
            image_url=image_url,
            note=note,
        )
