"""食事前アドバイザーエージェント

Single Responsibility: 食事前のアドバイスとレシピ提案のエージェント定義を担う
"""

from datetime import datetime, timedelta
from typing import Optional

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from ..schemas import PreMealAdvisorAgentOutput
from ..rakuten_recipe_api import (
    RakutenRecipeClient,
    RECIPE_CATEGORIES,
    CATEGORY_NAMES,
    estimate_nutrition_from_materials,
)
from ..utils import get_current_datetime
from .recipe_generator import generate_custom_recipe


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
        keyword: 検索キーワード（例: "鶏むね肉", "ヘルシー"）。

    Returns:
        おすすめレシピ、残りカロリー情報、提案理由を含む辞書
    """
    health_goal = tool_context.state.get("health_goal")
    daily_calorie_target = health_goal.get("daily_calorie_target") if health_goal else None
    goal_type = health_goal.get("goal_type") if health_goal else None

    meal_records = tool_context.state.get("meal_records", [])
    today = datetime.now().strftime("%Y-%m-%d")
    today_calories = sum(
        r["estimated_calories"]
        for r in meal_records
        if r["recorded_at"].startswith(today)
    )

    remaining_calories = daily_calorie_target - today_calories if daily_calorie_target else None

    if meal_type is None:
        hour = datetime.now().hour
        if 5 <= hour < 10:
            meal_type = "breakfast"
        elif 10 <= hour < 15:
            meal_type = "lunch"
        else:
            meal_type = "dinner"

    client = RakutenRecipeClient()
    category_id = None
    suggestion_reason = ""
    searched_keyword = None
    matched_category = None

    if keyword:
        searched_keyword = keyword
        if client.is_configured():
            matched_categories = client.search_category_by_keyword(keyword)
            if matched_categories:
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

    if category_id is None:
        category_id, suggestion_reason = _select_category(
            remaining_calories, goal_type, meal_type
        )

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


def _select_category(
    remaining_calories: Optional[int],
    goal_type: Optional[str],
    meal_type: str,
) -> tuple[str, str]:
    """状況に応じたカテゴリを選択"""
    if remaining_calories is not None and remaining_calories < 400:
        return RECIPE_CATEGORIES["healthy"], f"本日の残りカロリーが{remaining_calories}kcalと少なめのため、ヘルシーなレシピをおすすめします。"
    if goal_type == "weight_loss":
        return RECIPE_CATEGORIES["healthy"], "減量目標に合わせて、ヘルシーなレシピをおすすめします。"
    if goal_type == "muscle_gain":
        return RECIPE_CATEGORIES["main_dish"], "筋肉増量目標に合わせて、タンパク質が豊富な主菜レシピをおすすめします。"
    if meal_type == "breakfast":
        return RECIPE_CATEGORIES["rice"], "朝食にぴったりのご飯ものレシピをおすすめします。"
    if meal_type == "lunch":
        return RECIPE_CATEGORIES["main_dish"], "昼食にしっかり食べられる主菜レシピをおすすめします。"
    return RECIPE_CATEGORIES["main_dish"], "夕食におすすめの主菜レシピをご紹介します。"


def _get_general_advice(
    meal_type: str,
    goal_type: Optional[str],
    remaining_calories: Optional[int],
) -> str:
    """API未設定時の一般的なアドバイスを生成"""
    if remaining_calories is not None and remaining_calories < 400:
        return "残りカロリーが少なめなので、野菜中心の軽めの食事がおすすめです。\nサラダや野菜スープ、蒸し野菜などはいかがでしょうか。"
    if goal_type == "weight_loss":
        return "減量中は、高タンパク・低カロリーの食事を心がけましょう。\n鶏むね肉のサラダ、豆腐ステーキ、魚の蒸し料理などがおすすめです。"
    if goal_type == "muscle_gain":
        return "筋肉増量には、タンパク質をしっかり摂りましょう。\n鶏肉、牛肉、魚、卵、大豆製品を積極的に取り入れてください。"
    if meal_type == "breakfast":
        return "朝食は1日のエネルギー源です。\nご飯と味噌汁、卵料理などバランスの良い朝食がおすすめです。"
    if meal_type == "lunch":
        return "昼食は午後の活動に向けてしっかり食べましょう。\n主菜と副菜のバランスを意識してください。"
    return "夕食は翌日に向けて栄養を補給する大切な食事です。\n野菜を多めに、消化の良いものを選びましょう。"


PRE_MEAL_ADVISOR_INSTRUCTION = """あなたは食事アドバイスの専門家です。

## あなたの役割
- 食事前にユーザーに適切な食事をアドバイスする
- 健康目標、過去の食事を考慮した提案をする
- レシピや食材の提案も行う

## 使用するツール
- `get_current_datetime`: 現在時刻を確認（朝食/昼食/夕食の判断に使用）
- `get_meal_history`: 過去の食事記録を確認
- `generate_custom_recipe`: ユーザー条件に基づくカスタムレシピ生成（**推奨**）
- `suggest_recipes`: 楽天レシピAPIからのレシピ検索

---

## レシピ提案の2つのモード

### モード1: カスタムレシピ生成（推奨）
ユーザーが具体的な条件を指定した場合に使用します。

**使用するケース:**
- 「残り300kcalで満腹になりたい」
- 「高タンパク低脂質なレシピ」
- 「400kcal以内で高タンパクなもの」

**手順:**
1. `generate_custom_recipe`で条件を整理
2. 返された条件とガイドラインを元に、あなた自身がレシピを創作
3. `suggest_recipes`で楽天の関連レシピを参考表示

**引数の対応表:**
| ユーザーの要望 | priority引数 |
|--------------|-------------|
| 高タンパク、筋肉 | "high_protein" |
| 低脂質 | "low_fat" |
| 低糖質 | "low_carb" |
| 満腹 | "filling" |
| バランス良く | "balanced" |

### モード2: 楽天レシピ検索（従来）
食材やカテゴリを指定した場合に使用します。

**使用するケース:**
- 「鶏むね肉のレシピを教えて」
- 「おすすめのレシピは？」

---

## 注意事項
- カスタムレシピ生成後は、必ず`suggest_recipes`で関連レシピも表示
- 楽天レシピを紹介する際は「【楽天レシピ】」のクレジットを表示
- 栄養情報は概算値であることを明記

## 出力形式
最終応答は必ず JSON で **text** と **senderId** の2つを含める。senderId は **4** を返す（食事前アドバイスエージェントのID）。
"""


pre_meal_advisor_agent = Agent(
    name="pre_meal_advisor_agent",
    description="食事前のアドバイスやレシピ提案を担当。「何を食べればいい？」「おすすめのレシピは？」等の質問に対応。",
    instruction=PRE_MEAL_ADVISOR_INSTRUCTION,
    tools=[get_current_datetime, get_meal_history, generate_custom_recipe, suggest_recipes],
    output_schema=PreMealAdvisorAgentOutput,
    output_key="pre_meal_advisor_output",
)
