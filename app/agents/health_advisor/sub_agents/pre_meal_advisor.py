from datetime import datetime, timedelta

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from ..utils import get_current_datetime


# tool
def get_meal_history(
    tool_context: ToolContext,
    days: int = 1,
) -> dict:
  """食事履歴を取得します。

  Args:
      tool_context: ADKが提供するToolContext。
      days: 取得する日数（デフォルト: 1日 = 今日のみ）
  """
  meal_records = tool_context.state.get("meal_records", [])

  if not meal_records:
    return {
        "status": "no_records",
        "message": "食事記録がありません。",
        "meals": [],
    }

  cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
  filtered_meals = [
      r for r in meal_records
      if r["recorded_at"] >= cutoff_date
  ]

  # 日ごとの集計
  daily_summary = {}
  for meal in filtered_meals:
    date = meal["recorded_at"][:10]
    if date not in daily_summary:
      daily_summary[date] = {
          "total_calories": 0,
          "meal_count": 0,
          "meals": [],
      }
    daily_summary[date]["total_calories"] += meal["estimated_calories"]
    daily_summary[date]["meal_count"] += 1
    daily_summary[date]["meals"].append(meal)

  return {
      "status": "success",
      "days_requested": days,
      "total_meals": len(filtered_meals),
      "daily_summary": daily_summary,
      "meals": filtered_meals,
  }


# sub agent
pre_meal_advisor_agent = Agent(
    name="pre_meal_advisor_agent",
    description="食事前のアドバイスやレシピ提案を担当。「何を食べればいい？」「おすすめのレシピは？」等の質問に対応。",
    instruction="""あなたは食事アドバイスの専門家です。

## あなたの役割
- 食事前にユーザーに適切な食事をアドバイスする
- 健康目標、過去の食事を考慮した提案をする
- レシピや食材の提案も行う

## 使用するツール
- `get_current_datetime`: 現在時刻を確認（朝食/昼食/夕食の判断に使用）
- `get_meal_history`: 過去の食事記録を確認

## アドバイスのポイント
1. 現在時刻から食事のタイミング（朝食/昼食/夕食）を判断
2. 過去の食事記録があれば、栄養バランスを考慮
3. 健康目標があれば、それに沿った提案
4. 具体的なメニュー例を挙げる
5. 画像が送られてきた場合は、その食材を使ったレシピを提案

## 回答例
「昼食には、タンパク質をしっかり摂れる鶏胸肉のサラダはいかがでしょうか？
約400kcalで満足感もあります。」
""",
    tools=[get_current_datetime, get_meal_history],
)
