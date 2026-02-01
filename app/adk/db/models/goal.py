"""Goal モデル

健康目標を管理する。
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user_session import UserSession


class Goal(Base):
    """健康目標

    Prisma モデル: Goal
    テーブル名: goals
    """

    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_sessions.user_id"), nullable=False
    )
    details: Mapped[str] = mapped_column(Text, nullable=False)
    habits: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )

    # リレーション
    user: Mapped["UserSession"] = relationship("UserSession", back_populates="goals")

    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, user_id={self.user_id})>"
