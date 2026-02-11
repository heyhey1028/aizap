"""エージェントの構造化出力スキーマ

各エージェントは text と senderId を返す。
senderId: 1=root, 2=goal_setting, 3=exercise_manager, 4=meal_record
"""

from pydantic import BaseModel, Field


class _AgentOutputBase(BaseModel):
    """共通: ユーザーへの応答テキストと送信元 ID。"""

    text: str = Field(description="ユーザーへの応答メッセージ。")
    sender_id: int = Field(
        description="送信元 ID（数値）。JSON では senderId で出力する。",
        alias="senderId",
        serialization_alias="senderId",
    )

    model_config = {"populate_by_name": True}


class RootAgentOutput(_AgentOutputBase):
    """ルートエージェントの最終出力（直接応答時は senderId=1）。"""

    sender_id: int = Field(
        default=1,
        description="送信元 ID。",
        alias="senderId",
        serialization_alias="senderId",
    )


class GoalSettingAgentOutput(_AgentOutputBase):
    """目標設定サブエージェントの出力。"""

    sender_id: int = Field(
        default=2,
        description="送信元 ID。",
        alias="senderId",
        serialization_alias="senderId",
    )


class ExerciseManagerAgentOutput(_AgentOutputBase):
    """運動管理サブエージェントの出力。"""

    sender_id: int = Field(
        default=3,
        description="送信元 ID。",
        alias="senderId",
        serialization_alias="senderId",
    )


class MealRecordAgentOutput(_AgentOutputBase):
    """食事管理サブエージェントの出力。"""

    sender_id: int = Field(
        default=4,
        description="送信元 ID。",
        alias="senderId",
        serialization_alias="senderId",
    )


class DbSampleAgentOutput(_AgentOutputBase):
    """DB サンプルサブエージェントの出力（開発用、senderId=1）。"""

    sender_id: int = Field(
        default=1,
        description="送信元 ID。",
        alias="senderId",
        serialization_alias="senderId",
    )
