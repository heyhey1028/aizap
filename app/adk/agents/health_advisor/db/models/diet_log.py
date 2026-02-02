"""DietLog モデル

食事記録を管理する。
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user_session import UserSession


class DietLog(Base):
    """食事記録

    Prisma モデル: DietLog
    テーブル名: diet_logs
    """

    __tablename__ = "diet_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_sessions.user_id", ondelete="CASCADE"), nullable=False
    )

    # 食事の基本情報
    name: Mapped[str] = mapped_column(String, nullable=False)
    meal_type: Mapped[str] = mapped_column(String, nullable=False)  # "breakfast", "lunch", "dinner", "snack"

    # 必須栄養素
    calories: Mapped[float] = mapped_column(Float, nullable=False)  # kcal
    proteins: Mapped[float] = mapped_column(Float, nullable=False)  # g
    fats: Mapped[float] = mapped_column(Float, nullable=False)  # g
    carbohydrates: Mapped[float] = mapped_column(Float, nullable=False)  # g

    # 追加栄養素（オプション）
    sodium: Mapped[float | None] = mapped_column(Float, nullable=True)  # mg
    fiber: Mapped[float | None] = mapped_column(Float, nullable=True)  # g
    sugar: Mapped[float | None] = mapped_column(Float, nullable=True)  # g

    # AI推定関連
    estimation_source: Mapped[str] = mapped_column(String, nullable=False)  # "text", "image"
    is_user_corrected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # メタデータ
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), onupdate=func.now()
    )

    # リレーション
    user: Mapped["UserSession"] = relationship(
        "UserSession", back_populates="diet_logs"
    )

    # インデックス（Prisma と同じ）
    __table_args__ = (
        Index("ix_diet_logs_user_id_recorded_at", "user_id", recorded_at.desc()),
        Index(
            "ix_diet_logs_user_id_meal_type_recorded_at",
            "user_id",
            "meal_type",
            recorded_at.desc(),
        ),
    )

    def __repr__(self) -> str:
        return f"<DietLog(id={self.id}, name={self.name}, meal_type={self.meal_type})>"
