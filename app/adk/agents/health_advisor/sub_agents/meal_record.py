from datetime import datetime
from typing import Optional

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from ..utils import get_current_datetime


# tool
def record_meal(
    tool_context: ToolContext,
    meal_type: str,
    description: str,
    estimated_calories: int,
    protein_g: Optional[float] = None,
    carbs_g: Optional[float] = None,
    fat_g: Optional[float] = None,
    notes: Optional[str] = None,
) -> dict:
  """食事を記録します。

  Args:
      tool_context: ADKが提供するToolContext。
      meal_type: 食事の種類（breakfast, lunch, dinner, snack）
      description: 食事内容の説明
      estimated_calories: 推定カロリー（kcal）
      protein_g: 推定タンパク質（g、オプション）
      carbs_g: 推定炭水化物（g、オプション）
      fat_g: 推定脂質（g、オプション）
      notes: 追加のメモ（オプション）
  """
  meal_record = {
      "meal_type": meal_type,
      "description": description,
      "estimated_calories": estimated_calories,
      "protein_g": protein_g,
      "carbs_g": carbs_g,
      "fat_g": fat_g,
      "recorded_at": datetime.now().isoformat(),
      "notes": notes,
  }

  meal_records = tool_context.state.get("meal_records", [])
  meal_records = meal_records + [meal_record]
  tool_context.state["meal_records"] = meal_records

  # 本日の合計カロリーを計算
  today = datetime.now().strftime("%Y-%m-%d")
  today_calories = sum(
      r["estimated_calories"]
      for r in meal_records
      if r["recorded_at"].startswith(today)
  )

  return {
      "status": "success",
      "message": f"{meal_type}を記録しました: {description}",
      "recorded_meal": meal_record,
      "today_total_calories": today_calories,
      "today_meal_count": len([
          r for r in meal_records if r["recorded_at"].startswith(today)
      ]),
  }


# sub agent
meal_record_agent = Agent(
    name="meal_record_agent",
    description="食事の記録を担当。ユーザーが「〇〇を食べた」「これを記録して」と言った時に対応。画像からの食事推定も可能。",
    instruction="""あなたは食事記録の専門家です。

## あなたの役割
- ユーザーが食べた食事を記録する
- テキストまたは画像から食事内容とカロリーを推定する
- 記録後に励ましのフィードバックを提供する

## 使用するツール
- `get_current_datetime`: 現在時刻を確認（食事タイプの判断に使用）
- `record_meal`: 食事を記録

## 食事タイプの判断
- 6:00-10:00: breakfast（朝食）
- 10:00-14:00: lunch（昼食）
- 14:00-17:00: snack（おやつ）
- 17:00-22:00: dinner（夕食）
- 22:00-6:00: snack（夜食）

## 記録のポイント
1. 食事内容を明確に把握する
2. カロリーは概算で良い（正確でなくてOK）
3. 画像が送られた場合は、見た目から食事内容とカロリーを推定
4. 記録後は「いいですね！」「バランス良いですね！」など励ます
5. 可能であればタンパク質・炭水化物・脂質も推定

## カロリー目安（参考）
- おにぎり1個: 約180kcal
- サラダ: 約50-150kcal
- ラーメン: 約500-800kcal
- 定食: 約600-800kcal
- サンドイッチ: 約300-400kcal
""",
    tools=[get_current_datetime, record_meal],
)
