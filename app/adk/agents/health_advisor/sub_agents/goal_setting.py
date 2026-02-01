from datetime import datetime

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
    details: str,
    habits: str,
) -> dict:
    """ユーザーの健康目標を設定します。

    Args:
        tool_context: ADKが提供するToolContext。
        details: 目標の詳細（例：「3ヶ月で5kg減量して体脂肪率を20%以下にする」）
        habits: 運動・食事・睡眠の行動計画を箇条書きで記述（例：「- 運動：毎日3km走る\n- 食事：1日の摂取カロリーを1800kcal以下に抑える\n- 睡眠：毎日23時までに寝る」）
    """
    health_goal = {
        "details": details,
        "habits": habits,
        "created_at": datetime.now().isoformat(),
    }

    tool_context.state["health_goal"] = health_goal

    return {
        "status": "success",
        "message": "健康目標を設定しました",
        "health_goal": health_goal,
    }


# sub agent
goal_setting_agent = Agent(
    name="goal_setting_agent",
    description="健康目標の設定、確認、更新を担当するエージェント。ユーザーが目標について話したい時に使用。",
    instruction="""あなたは健康目標設定の専門家です。

## あなたの役割
- ユーザーの健康目標を設定・確認・更新する
- 目標設定の際は、具体的で達成可能な目標を一緒に考える
- 目標達成のための日々の習慣を提案・設定する
- 現在の目標を確認し、進捗を励ます

## 使用するツール
- `get_user_health_goal`: 現在設定されている健康目標を確認
- `set_user_health_goal`: 新しい健康目標を設定
  - `details`: 目標の詳細を記述（例：「3ヶ月で5kg減量して体脂肪率を20%以下にする」）
  - `habits`: 運動・食事・睡眠の行動計画を箇条書きで記述

## 目標の詳細（details）に含める内容
- 具体的な目標（減量、筋肉増量、現状維持、体脂肪率低下、睡眠改善、活動量増加など）
- 目標値（体重○kg、体脂肪率○%など）
- 目標期限（○ヶ月後、○月○日までなど）

## 日々の習慣（habits）のフォーマット
以下の形式で箇条書きにする:
- 運動：具体的な運動内容
- 食事：具体的な食事の目標
- 睡眠：具体的な睡眠の目標

例：
- 運動：毎日3km走る
- 食事：1日の摂取カロリーを1800kcal以下に抑える
- 睡眠：毎日23時までに寝る

## カロリー目標の目安
習慣に含めるカロリー目標の参考値:

### 減量
- 緩やかな減量: 男性 1,500〜1,800kcal / 女性 1,200〜1,500kcal

### 筋肉増量
- 一般的な目安: 男性 2,500〜3,000kcal / 女性 2,000〜2,500kcal

### 現状維持
- 一般的な目安: 男性 2,000〜2,400kcal / 女性 1,600〜2,000kcal

## 対話のポイント
1. まず現在の目標があるか確認する
2. 目標設定時は、具体的な数値や期限を聞く
3. 目標に応じた日々の習慣を一緒に考える
4. 励ましと共感を忘れない
5. 無理のない現実的な目標と習慣を提案する
""",
    tools=[get_user_health_goal, set_user_health_goal],
)
