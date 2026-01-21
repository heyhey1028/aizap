from datetime import datetime
from typing import Optional

from google.adk.agents import Agent
from google.adk.tools import ToolContext


# tool
def get_user_health_goal(tool_context: ToolContext) -> dict:
  """ユーザーの健康目標を取得します。

  Session Stateから健康目標を読み取ります。
  設定されていない場合は、未設定であることを返します。
  """
  health_goal = tool_context.state.get("health_goal")

  if health_goal is None:
    return {
        "status": "not_set",
        "message": "健康目標がまだ設定されていません。目標を設定しましょう！",
    }

  return {
      "status": "success",
      "health_goal": health_goal,
  }


def set_user_health_goal(
    tool_context: ToolContext,
    goal_type: str,
    description: str,
    target_value: Optional[float] = None,
    current_value: Optional[float] = None,
    target_date: Optional[str] = None,
    daily_calorie_target: Optional[int] = None,
) -> dict:
  """ユーザーの健康目標を設定します。

  Args:
      tool_context: ADKが提供するToolContext。
      goal_type: 目標の種類（weight_loss, muscle_gain, maintain, improve_sleep等）
      description: 目標の詳細説明
      target_value: 目標値（体重kg、体脂肪率%等、オプション）
      current_value: 現在値（体重kg、体脂肪率%等、オプション）
      target_date: 目標達成日（YYYY-MM-DD形式、オプション）
      daily_calorie_target: 1日の目標摂取カロリー（kcal、オプション）
  """
  health_goal = {
      "goal_type": goal_type,
      "description": description,
      "target_value": target_value,
      "current_value": current_value,
      "target_date": target_date,
      "daily_calorie_target": daily_calorie_target,
      "created_at": datetime.now().isoformat(),
  }

  tool_context.state["health_goal"] = health_goal

  response = {
      "status": "success",
      "message": f"健康目標を設定しました: {goal_type}",
      "health_goal": health_goal,
  }

  if daily_calorie_target:
      response["message"] += f"（1日の目標カロリー: {daily_calorie_target}kcal）"

  return response


# sub agent
goal_setting_agent = Agent(
    name="goal_setting_agent",
    description="健康目標の設定、確認、更新を担当するエージェント。ユーザーが目標について話したい時に使用。",
    instruction="""あなたは健康目標設定の専門家です。

## あなたの役割
- ユーザーの健康目標を設定・確認・更新する
- 目標設定の際は、具体的で達成可能な目標を一緒に考える
- 目標達成のための1日のカロリー目標を提案・設定する
- 現在の目標を確認し、進捗を励ます

## 使用するツール
- `get_user_health_goal`: 現在設定されている健康目標を確認
- `set_user_health_goal`: 新しい健康目標を設定

## 目標タイプの例
- weight_loss: 減量
- muscle_gain: 筋肉増量
- maintain: 現状維持
- reduce_body_fat: 体脂肪率低下
- improve_sleep: 睡眠改善
- increase_activity: 活動量増加

## 1日の目標カロリー設定の目安
目標タイプに応じて適切なカロリー目標を提案する:

### 減量（weight_loss）
- 緩やかな減量: 基礎代謝 × 1.2〜1.4（月1〜2kg減）
- 一般的な目安: 男性 1,500〜1,800kcal / 女性 1,200〜1,500kcal

### 筋肉増量（muscle_gain）
- 基礎代謝 × 1.5〜1.7 + 200〜300kcal
- 一般的な目安: 男性 2,500〜3,000kcal / 女性 2,000〜2,500kcal

### 現状維持（maintain）
- 基礎代謝 × 活動係数（1.2〜1.9）
- 一般的な目安: 男性 2,000〜2,400kcal / 女性 1,600〜2,000kcal

## 対話のポイント
1. まず現在の目標があるか確認する
2. 目標設定時は、具体的な数値や期限を聞く
3. 目標に応じた1日のカロリー目標を提案する
4. 励ましと共感を忘れない
5. 無理のない現実的な目標を提案する
""",
    tools=[get_user_health_goal, set_user_health_goal],
)
