"""ExerciseLog モデル

運動ログを管理する。
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user_session import UserSession


class ExerciseLog(Base):
    """運動ログ

    Prisma モデル: ExerciseLog
    テーブル名: exercise_logs
    """

    __tablename__ = "exercise_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("user_sessions.user_id", ondelete="CASCADE"), nullable=False
    )
    exercise_name: Mapped[str] = mapped_column(String, nullable=False)
    sets: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    muscle_group: Mapped[str | None] = mapped_column(String, nullable=True)
    total_sets: Mapped[int] = mapped_column(Integer, nullable=False)
    total_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )

    # リレーション
    user: Mapped["UserSession"] = relationship(
        "UserSession", back_populates="exercise_logs"
    )

    # インデックス（Prisma と同じ）
    __table_args__ = (
        Index("ix_exercise_logs_user_id_recorded_at", "user_id", recorded_at.desc()),
        Index(
            "ix_exercise_logs_user_id_exercise_name_recorded_at",
            "user_id",
            "exercise_name",
            recorded_at.desc(),
        ),
    )

    def __repr__(self) -> str:
        return f"<ExerciseLog(id={self.id}, exercise_name={self.exercise_name})>"
