"""Habit モデル

運動・食事習慣計画を管理する。
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .goal import Goal
    from .user_session import UserSession


class Habit(Base):
    """運動・食事習慣計画

    Prisma モデル: Habit
    テーブル名: habits
    """

    __tablename__ = "habits"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_sessions.user_id", ondelete="CASCADE"), nullable=False
    )
    goal_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("goals.id", ondelete="SET NULL"), nullable=True
    )

    # 習慣の基本情報
    habit_type: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # ルーティンのグルーピング
    routine_id: Mapped[str | None] = mapped_column(String, nullable=True)
    routine_name: Mapped[str | None] = mapped_column(String, nullable=True)
    order_in_routine: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 運動習慣の詳細（habit_type="exercise"の場合）
    exercise_name: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    muscle_group: Mapped[str | None] = mapped_column(String, nullable=True)
    target_sets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_weight: Mapped[float | None] = mapped_column(Float, nullable=True)

    # 食事習慣の詳細（habit_type="meal"の場合）※Phase 2で本格実装
    meal_type: Mapped[str | None] = mapped_column(String, nullable=True)
    target_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_proteins: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_fats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_carbohydrates: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meal_guidelines: Mapped[str | None] = mapped_column(String, nullable=True)

    # スケジュール設定
    frequency: Mapped[str] = mapped_column(String, nullable=False)
    days_of_week: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    time_of_day: Mapped[str | None] = mapped_column(String, nullable=True)

    # ステータスと期間
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # メタデータ
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # リレーション
    user: Mapped["UserSession"] = relationship("UserSession", back_populates="habits")
    goal: Mapped["Goal | None"] = relationship("Goal", back_populates="habit_details")

    # インデックス（Prisma と同じ）
    __table_args__ = (
        Index("ix_habits_user_id_habit_type_is_active", "user_id", "habit_type", "is_active"),
        Index("ix_habits_user_id_routine_id", "user_id", "routine_id"),
        Index("ix_habits_user_id_start_date", "user_id", "start_date"),
        Index("ix_habits_goal_id", "goal_id"),
    )

    def __repr__(self) -> str:
        return f"<Habit(id={self.id}, habit_type={self.habit_type}, title={self.title})>"
