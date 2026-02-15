"""カスタムレシピ生成モジュール

Single Responsibility: ユーザー条件に基づくカスタムレシピ生成の責任を担う
"""

from typing import Optional

from google.adk.tools import ToolContext

from ..utils import get_jst_now


# PFC比率の定数定義
PFC_RATIOS = {
    "high_protein": {"protein": 0.32, "fat": 0.25, "carbs": 0.43},
    "low_fat": {"protein": 0.25, "fat": 0.17, "carbs": 0.58},
    "low_carb": {"protein": 0.30, "fat": 0.40, "carbs": 0.30},
    "filling": {"protein": 0.30, "fat": 0.25, "carbs": 0.45},
    "balanced": {"protein": 0.20, "fat": 0.25, "carbs": 0.55},
}

PFC_DESCRIPTIONS = {
    "high_protein": "高タンパク（筋肉維持・満腹感）",
    "low_fat": "低脂質（カロリー抑制）",
    "low_carb": "低糖質（血糖値コントロール）",
    "filling": "満腹感重視（食物繊維・タンパク質）",
    "balanced": "バランス型",
}

RECIPE_GUIDELINES = {
    "high_protein": [
        "鶏むね肉、ささみ、魚、豆腐、卵などを主役に",
        "野菜を多めに加えてボリュームアップ",
        "油は控えめに、蒸し・茹で・グリル調理を推奨",
    ],
    "low_fat": [
        "脂身の少ない肉、白身魚、豆腐を選択",
        "油は最小限に、ノンオイルドレッシング活用",
        "蒸し料理、煮物がおすすめ",
    ],
    "low_carb": [
        "主食を減らすか置き換え（カリフラワーライスなど）",
        "野菜、肉、魚を中心に",
        "砂糖・みりんは控えめに",
    ],
    "filling": [
        "食物繊維豊富な野菜・きのこ・こんにゃくを多めに",
        "スープ・汁物で水分を取る",
        "タンパク質をしっかり摂る",
        "咀嚼回数が増える食材を選ぶ",
    ],
    "balanced": [
        "主食・主菜・副菜をバランスよく",
        "野菜は1食で120g以上を目標",
        "タンパク質源を必ず含める",
    ],
}

RECIPE_OUTPUT_FORMAT = """
上記の条件に基づいて、オリジナルレシピを創作してください。

【出力フォーマット】
## 【料理名】

📊 **栄養情報（推定）**
- カロリー: 約○○kcal
- タンパク質: ○○g
- 脂質: ○○g
- 炭水化物: ○○g

⏱️ **調理時間**: 約○○分

### 材料（1人分）
- 材料1: 分量
- 材料2: 分量
...

### 作り方
1. ステップ1
2. ステップ2
...

### ポイント
- 調理のコツやアレンジ案
"""


def _calculate_pfc(priority: Optional[str], target_calories: int) -> dict:
    """優先事項に応じたPFC（タンパク質・脂質・炭水化物）の目安を計算"""
    ratios = PFC_RATIOS.get(priority, PFC_RATIOS["balanced"])

    return {
        "protein_g": int(target_calories * ratios["protein"] / 4),  # 4kcal/g
        "fat_g": int(target_calories * ratios["fat"] / 9),  # 9kcal/g
        "carbs_g": int(target_calories * ratios["carbs"] / 4),  # 4kcal/g
        "description": PFC_DESCRIPTIONS.get(priority, "バランス型"),
    }


def _get_user_calorie_context(tool_context: ToolContext) -> dict:
    """ユーザーのカロリーコンテキストを取得"""
    health_goal = tool_context.state.get("health_goal")
    daily_calorie_target = None
    goal_type = None

    if health_goal:
        daily_calorie_target = health_goal.get("daily_calorie_target")
        goal_type = health_goal.get("goal_type")

    meal_records = tool_context.state.get("meal_records", [])
    today = get_jst_now().strftime("%Y-%m-%d")
    today_calories = sum(
        r["estimated_calories"]
        for r in meal_records
        if r["recorded_at"].startswith(today)
    )

    remaining_calories = None
    if daily_calorie_target:
        remaining_calories = daily_calorie_target - today_calories

    return {
        "remaining_calories": remaining_calories,
        "today_calories": today_calories,
        "daily_calorie_target": daily_calorie_target,
        "goal_type": goal_type,
    }


def _get_meal_type_from_hour() -> str:
    """現在時刻から食事タイプを判定"""
    hour = get_jst_now().hour
    if 5 <= hour < 10:
        return "breakfast"
    elif 10 <= hour < 15:
        return "lunch"
    return "dinner"


def generate_custom_recipe(
    tool_context: ToolContext,
    target_calories: Optional[int] = None,
    priority: Optional[str] = None,
    main_ingredient: Optional[str] = None,
    cooking_time: Optional[str] = None,
) -> dict:
    """ユーザーの条件に基づきLLMがレシピを生成するための情報を返します。

    このツールは「LLMがレシピを生成するための条件情報」を返します。
    実際のレシピ生成はエージェント自身が行います（LLMの創造性を活用）。

    Args:
        tool_context: ADKが提供するToolContext。
        target_calories: 目標カロリー（kcal）。指定しない場合は残りカロリーから算出。
        priority: 優先事項。"high_protein"（高タンパク）, "low_fat"（低脂質）,
                  "low_carb"（低糖質）, "balanced"（バランス型）, "filling"（満腹感重視）
        main_ingredient: メインとなる食材（例: "鶏むね肉", "豆腐"）
        cooking_time: 調理時間。"quick"（15分以内）, "normal"（30分程度）, "slow"（60分以上）

    Returns:
        条件情報をまとめた辞書（エージェントがこれを元にレシピ生成）
    """
    user_context = _get_user_calorie_context(tool_context)

    # 目標カロリーの決定
    if target_calories is None:
        if user_context["remaining_calories"] is not None:
            target_calories = int(user_context["remaining_calories"] * 0.75)
        else:
            target_calories = 500

    meal_type = _get_meal_type_from_hour()
    pfc_guidelines = _calculate_pfc(priority, target_calories)
    guidelines = RECIPE_GUIDELINES.get(priority, RECIPE_GUIDELINES["balanced"])

    return {
        "status": "success",
        "message": "以下の条件に基づいてレシピを生成してください",
        "conditions": {
            "target_calories": target_calories,
            "priority": priority or "balanced",
            "main_ingredient": main_ingredient,
            "cooking_time": cooking_time or "normal",
            "meal_type": meal_type,
        },
        "user_context": user_context,
        "pfc_guidelines": pfc_guidelines,
        "recipe_guidelines": guidelines,
        "instruction": RECIPE_OUTPUT_FORMAT,
    }
