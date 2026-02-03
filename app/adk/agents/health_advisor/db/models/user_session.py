"""UserSession モデル

ユーザーセッションを管理する。
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .goal import Goal
    from .exercise_log import ExerciseLog
    from .diet_log import DietLog
    from .habit import Habit


class UserSession(Base):
    """ユーザーセッション

    Prisma モデル: UserSession
    テーブル名: user_sessions
    """

    __tablename__ = "user_sessions"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), onupdate=func.now()
    )

    # リレーション
    goals: Mapped[list["Goal"]] = relationship(
        "Goal", back_populates="user", cascade="all, delete-orphan"
    )
    exercise_logs: Mapped[list["ExerciseLog"]] = relationship(
        "ExerciseLog", back_populates="user", cascade="all, delete-orphan"
    )
    diet_logs: Mapped[list["DietLog"]] = relationship(
        "DietLog", back_populates="user", cascade="all, delete-orphan"
    )
    habits: Mapped[list["Habit"]] = relationship(
        "Habit", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<UserSession(user_id={self.user_id})>"
