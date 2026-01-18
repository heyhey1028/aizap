from datetime import datetime, timedelta
from typing import Optional

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from ..rakuten_recipe_api import (
    RakutenRecipeClient,
    RECIPE_CATEGORIES,
    CATEGORY_NAMES,
    estimate_nutrition_from_materials,
)
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


def suggest_recipes(
    tool_context: ToolContext,
    meal_type: Optional[str] = None,
    keyword: Optional[str] = None,
) -> dict:
  """ユーザーの残りカロリー・健康目標に基づいてレシピを提案します。

  Args:
      tool_context: ADKが提供するToolContext。
      meal_type: 食事タイプ（breakfast/lunch/dinner）。省略時は現在時刻から自動判定。
      keyword: 検索キーワード（例: "鶏むね肉", "ヘルシー"）。指定時はキーワードでカテゴリを検索。

  Returns:
      おすすめレシピ、残りカロリー情報、提案理由を含む辞書
  """
  # 1. 健康目標を取得
  health_goal = tool_context.state.get("health_goal")
  daily_calorie_target = None
  goal_type = None

  if health_goal:
    daily_calorie_target = health_goal.get("daily_calorie_target")
    goal_type = health_goal.get("goal_type")

  # 2. 今日の摂取カロリーを計算
  meal_records = tool_context.state.get("meal_records", [])
  today = datetime.now().strftime("%Y-%m-%d")
  today_calories = sum(
      r["estimated_calories"]
      for r in meal_records
      if r["recorded_at"].startswith(today)
  )

  # 3. 残りカロリーを算出
  remaining_calories = None
  if daily_calorie_target:
    remaining_calories = daily_calorie_target - today_calories

  # 4. 現在時刻から食事タイプを判定
  now = datetime.now()
  hour = now.hour

  if meal_type is None:
    if 5 <= hour < 10:
      meal_type = "breakfast"
    elif 10 <= hour < 15:
      meal_type = "lunch"
    else:
      meal_type = "dinner"

  # 5. 楽天APIクライアントを初期化
  client = RakutenRecipeClient()

  # 6. 状況に応じたカテゴリを選択
  category_id = None
  suggestion_reason = ""
  searched_keyword = None
  matched_category = None

  # キーワードが指定された場合、カテゴリを検索
  if keyword:
    searched_keyword = keyword
    if client.is_configured():
      matched_categories = client.search_category_by_keyword(keyword)
      if matched_categories:
        # 中カテゴリを優先、次に小カテゴリ、最後に大カテゴリ
        for cat_type in ["medium", "small", "large"]:
          for cat in matched_categories:
            if cat["category_type"] == cat_type:
              category_id = cat["category_id"]
              matched_category = cat["category_name"]
              suggestion_reason = f"「{keyword}」で検索し、「{matched_category}」カテゴリのレシピをおすすめします。"
              break
          if category_id:
            break
      else:
        # キーワードにマッチするカテゴリが見つからない場合
        return {
            "status": "no_category_match",
            "message": f"「{keyword}」に該当するカテゴリが見つかりませんでした。",
            "searched_keyword": searched_keyword,
            "remaining_calories": remaining_calories,
            "today_calories": today_calories,
            "daily_calorie_target": daily_calorie_target,
            "meal_type": meal_type,
            "general_advice": _get_general_advice(meal_type, goal_type, remaining_calories),
        }

  # キーワード未指定または検索失敗の場合、従来のロジック
  if category_id is None:
    if remaining_calories is not None and remaining_calories < 400:
      category_id = RECIPE_CATEGORIES["healthy"]
      suggestion_reason = f"本日の残りカロリーが{remaining_calories}kcalと少なめのため、ヘルシーなレシピをおすすめします。"
    elif goal_type == "weight_loss":
      category_id = RECIPE_CATEGORIES["healthy"]
      suggestion_reason = "減量目標に合わせて、ヘルシーなレシピをおすすめします。"
    elif goal_type == "muscle_gain":
      category_id = RECIPE_CATEGORIES["main_dish"]
      suggestion_reason = "筋肉増量目標に合わせて、タンパク質が豊富な主菜レシピをおすすめします。"
    elif meal_type == "breakfast":
      category_id = RECIPE_CATEGORIES["rice"]
      suggestion_reason = "朝食にぴったりのご飯ものレシピをおすすめします。"
    elif meal_type == "lunch":
      category_id = RECIPE_CATEGORIES["main_dish"]
      suggestion_reason = "昼食にしっかり食べられる主菜レシピをおすすめします。"
    else:  # dinner
      category_id = RECIPE_CATEGORIES["main_dish"]
      suggestion_reason = "夕食におすすめの主菜レシピをご紹介します。"

  # 7. 楽天APIでレシピ取得

  if not client.is_configured():
    return {
        "status": "api_not_configured",
        "message": "レシピAPIが設定されていません。一般的なアドバイスをご提供します。",
        "suggestion_reason": suggestion_reason,
        "remaining_calories": remaining_calories,
        "today_calories": today_calories,
        "daily_calorie_target": daily_calorie_target,
        "meal_type": meal_type,
        "general_advice": _get_general_advice(meal_type, goal_type, remaining_calories),
    }

  api_result = client.get_ranking(category_id)

  if "error" in api_result:
    return {
        "status": "api_error",
        "message": f"レシピの取得に失敗しました: {api_result['error']}",
        "suggestion_reason": suggestion_reason,
        "searched_keyword": searched_keyword,
        "remaining_calories": remaining_calories,
        "today_calories": today_calories,
        "daily_calorie_target": daily_calorie_target,
        "meal_type": meal_type,
        "general_advice": _get_general_advice(meal_type, goal_type, remaining_calories),
    }

  # 8. レスポンスを整形（栄養情報の概算を含む）
  recipes = []
  for recipe in api_result.get("result", []):
    materials = recipe.get("recipeMaterial", [])
    nutrition = estimate_nutrition_from_materials(materials)

    recipes.append({
        "title": recipe.get("recipeTitle"),
        "url": recipe.get("recipeUrl"),
        "image_url": recipe.get("foodImageUrl"),
        "materials": materials,
        "indication": recipe.get("recipeIndication"),
        "cost": recipe.get("recipeCost"),
        "estimated_nutrition": {
            "calories": nutrition["estimated_calories"],
            "protein": nutrition["estimated_protein"],
            "fat": nutrition["estimated_fat"],
            "carbs": nutrition["estimated_carbs"],
            "is_estimate": True,
        },
    })

  # キーワード検索でマッチした場合はマッチしたカテゴリ名、それ以外は従来のカテゴリ名
  category_name = matched_category if matched_category else CATEGORY_NAMES.get(category_id, "おすすめ")

  return {
      "status": "success",
      "recipes": recipes,
      "category": category_name,
      "suggestion_reason": suggestion_reason,
      "searched_keyword": searched_keyword,
      "matched_category": matched_category,
      "remaining_calories": remaining_calories,
      "today_calories": today_calories,
      "daily_calorie_target": daily_calorie_target,
      "meal_type": meal_type,
      "credit": "【楽天レシピ】",
  }


def _get_general_advice(
    meal_type: str,
    goal_type: Optional[str],
    remaining_calories: Optional[int],
) -> str:
  """API未設定時の一般的なアドバイスを生成"""
  advice = []

  if remaining_calories is not None and remaining_calories < 400:
    advice.append("残りカロリーが少なめなので、野菜中心の軽めの食事がおすすめです。")
    advice.append("サラダや野菜スープ、蒸し野菜などはいかがでしょうか。")
  elif goal_type == "weight_loss":
    advice.append("減量中は、高タンパク・低カロリーの食事を心がけましょう。")
    advice.append("鶏むね肉のサラダ、豆腐ステーキ、魚の蒸し料理などがおすすめです。")
  elif goal_type == "muscle_gain":
    advice.append("筋肉増量には、タンパク質をしっかり摂りましょう。")
    advice.append("鶏肉、牛肉、魚、卵、大豆製品を積極的に取り入れてください。")
  elif meal_type == "breakfast":
    advice.append("朝食は1日のエネルギー源です。")
    advice.append("ご飯と味噌汁、卵料理などバランスの良い朝食がおすすめです。")
  elif meal_type == "lunch":
    advice.append("昼食は午後の活動に向けてしっかり食べましょう。")
    advice.append("主菜と副菜のバランスを意識してください。")
  else:
    advice.append("夕食は翌日に向けて栄養を補給する大切な食事です。")
    advice.append("野菜を多めに、消化の良いものを選びましょう。")

  return "\n".join(advice)


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
- `suggest_recipes`: ユーザーの状況に合わせたレシピを提案（**積極的に使用してください**）

## suggest_recipesツールについて
このツールは楽天レシピAPIを使用して、ユーザーの状況に最適なレシピを提案します。

### keyword引数について
- keyword引数で食材や料理ジャンルを指定可能
- 例: keyword="鶏むね肉" → 鶏むね肉を使ったレシピ
- 例: keyword="ヘルシー" → ヘルシー料理のレシピ
- 例: keyword="豚肉" → 豚肉を使ったレシピ
- ユーザーが特定の食材や料理を指定した場合は、keyword引数を使用してください

### keywordを省略した場合の動作
- 残りカロリーが少ない場合 → ヘルシーレシピを提案
- 減量目標の場合 → ヘルシーレシピを提案
- 筋肉増量目標の場合 → 主菜（肉料理）を提案
- それ以外 → 時間帯に応じたレシピを提案

## アドバイスのポイント
1. 現在時刻から食事のタイミング（朝食/昼食/夕食）を判断
2. 過去の食事記録があれば、栄養バランスを考慮
3. 健康目標があれば、それに沿った提案
4. 具体的なメニュー例を挙げる
5. 画像が送られてきた場合は、その食材を使ったレシピを提案

## レシピ提案時の注意事項
- **必ずクレジット表記を含めてください**: レシピを紹介する際は「【楽天レシピ】」のクレジットを表示
- **提案理由を説明してください**: なぜそのレシピをおすすめするのか、ユーザーの状況に合わせて説明
- **残りカロリー情報を活用**: 残りカロリーがある場合は、その情報も伝える
- **栄養情報を表示**: 各レシピの`estimated_nutrition`を使って、カロリー・PFCバランスを表示

## 栄養情報について
各レシピには`estimated_nutrition`フィールドが含まれています：
- `calories`: 推定カロリー（kcal）
- `protein`: 推定タンパク質（g）
- `fat`: 推定脂質（g）
- `carbs`: 推定炭水化物（g）
- `is_estimate`: 概算値であることを示すフラグ

これらは材料から概算した推定値です。実際の値とは異なる場合があります。

## 回答例
「今日は既に1,200kcal摂取されていて、残り600kcalですね。
夕食には、タンパク質をしっかり摂れる鶏胸肉のサラダはいかがでしょうか？

【楽天レシピ】おすすめレシピ：
1. 鶏むね肉のさっぱり煮（約30分）
   📊 推定栄養: 約350kcal | P: 35g | F: 5g | C: 20g
   材料: 鶏むね肉、酢、醤油...
   https://recipe.rakuten.co.jp/...

※栄養情報は材料からの概算値です。

減量目標に合わせて、ヘルシーなレシピをおすすめしました。」
""",
    tools=[get_current_datetime, get_meal_history, suggest_recipes],
)
