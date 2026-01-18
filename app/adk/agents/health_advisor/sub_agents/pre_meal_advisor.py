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

    # 4. 目標カロリーの決定
    if target_calories is None:
        if remaining_calories is not None:
            # 残りカロリーの70-80%を目安に
            target_calories = int(remaining_calories * 0.75)
        else:
            # デフォルト値
            target_calories = 500

    # 5. 現在時刻から食事タイプを判定
    now = datetime.now()
    hour = now.hour
    if 5 <= hour < 10:
        meal_type = "breakfast"
    elif 10 <= hour < 15:
        meal_type = "lunch"
    else:
        meal_type = "dinner"

    # 6. 優先事項に応じたPFC目安を設定
    pfc_guidelines = _get_pfc_guidelines(priority, target_calories)

    # 7. レシピ生成のためのガイドライン
    recipe_guidelines = {
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

    guidelines = recipe_guidelines.get(priority, recipe_guidelines["balanced"])

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
        "user_context": {
            "remaining_calories": remaining_calories,
            "today_calories": today_calories,
            "daily_calorie_target": daily_calorie_target,
            "goal_type": goal_type,
        },
        "pfc_guidelines": pfc_guidelines,
        "recipe_guidelines": guidelines,
        "instruction": """
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
""",
    }


def _get_pfc_guidelines(priority: Optional[str], target_calories: int) -> dict:
    """優先事項に応じたPFC（タンパク質・脂質・炭水化物）の目安を返す"""
    if priority == "high_protein":
        # タンパク質30-35%, 脂質25%, 炭水化物40-45%
        protein = int(target_calories * 0.32 / 4)  # 4kcal/g
        fat = int(target_calories * 0.25 / 9)      # 9kcal/g
        carbs = int(target_calories * 0.43 / 4)   # 4kcal/g
    elif priority == "low_fat":
        # タンパク質25%, 脂質15-20%, 炭水化物55-60%
        protein = int(target_calories * 0.25 / 4)
        fat = int(target_calories * 0.17 / 9)
        carbs = int(target_calories * 0.58 / 4)
    elif priority == "low_carb":
        # タンパク質30%, 脂質40%, 炭水化物30%
        protein = int(target_calories * 0.30 / 4)
        fat = int(target_calories * 0.40 / 9)
        carbs = int(target_calories * 0.30 / 4)
    elif priority == "filling":
        # 満腹感重視: タンパク質30%, 脂質25%, 炭水化物45%
        protein = int(target_calories * 0.30 / 4)
        fat = int(target_calories * 0.25 / 9)
        carbs = int(target_calories * 0.45 / 4)
    else:  # balanced
        # バランス型: タンパク質20%, 脂質25%, 炭水化物55%
        protein = int(target_calories * 0.20 / 4)
        fat = int(target_calories * 0.25 / 9)
        carbs = int(target_calories * 0.55 / 4)

    return {
        "protein_g": protein,
        "fat_g": fat,
        "carbs_g": carbs,
        "description": {
            "high_protein": "高タンパク（筋肉維持・満腹感）",
            "low_fat": "低脂質（カロリー抑制）",
            "low_carb": "低糖質（血糖値コントロール）",
            "filling": "満腹感重視（食物繊維・タンパク質）",
            "balanced": "バランス型",
        }.get(priority, "バランス型"),
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
- 「低糖質で簡単に作れるもの」

**手順:**
1. `generate_custom_recipe`で条件を整理
2. 返された条件とガイドラインを元に、あなた自身がレシピを創作
3. `suggest_recipes`で楽天の関連レシピを参考表示

**引数の対応表:**
| ユーザーの要望 | priority引数 |
|--------------|-------------|
| 高タンパク、筋肉、タンパク質 | "high_protein" |
| 低脂質、脂肪控えめ | "low_fat" |
| 低糖質、糖質制限 | "low_carb" |
| 満腹、お腹いっぱい | "filling" |
| バランス良く | "balanced" |

### モード2: 楽天レシピ検索（従来）
食材やカテゴリを指定した場合に使用します。

**使用するケース:**
- 「鶏むね肉のレシピを教えて」
- 「おすすめのレシピは？」
- 「ヘルシーな料理は？」

**手順:**
- `suggest_recipes`で楽天APIからレシピ取得

---

## カスタムレシピ生成のガイドライン

レシピを創作する際は以下を守ってください：
- 目標カロリー内に収まるよう材料量を調整
- PFCバランスは`pfc_guidelines`に従う
- 調理時間は指定に合わせる（quick=15分、normal=30分、slow=60分以上）
- 材料は一般的なスーパーで入手可能なもの
- 出力フォーマットは`instruction`フィールドに従う

---

## 回答例（モード1: カスタムレシピ生成）

**ユーザー:** 「残り400kcalで高タンパクなレシピを教えて」

**あなたの回答:**
```
残り400kcal・高タンパクに最適なレシピをご提案します！

## 【鶏むね肉の塩麹焼き 野菜たっぷり】

📊 **栄養情報（推定）**
- カロリー: 約320kcal
- タンパク質: 38g
- 脂質: 8g
- 炭水化物: 15g

⏱️ **調理時間**: 約25分

### 材料（1人分）
- 鶏むね肉: 150g
- 塩麹: 大さじ1
- ブロッコリー: 80g
- パプリカ: 1/2個
- オリーブオイル: 小さじ1

### 作り方
1. 鶏むね肉に塩麹を揉み込み、15分置く
2. ブロッコリーは小房に分け、パプリカは一口大に切る
3. フライパンにオリーブオイルを熱し、鶏肉を焼く
4. 野菜を加えて蒸し焼きにする

### ポイント
- 塩麹で柔らかく仕上がります
- 野菜でボリュームアップ！

---

📚 **楽天レシピで関連レシピを見る:**
【楽天レシピ】
1. 鶏むね肉のさっぱり煮（約350kcal）
   https://recipe.rakuten.co.jp/...
```

---

## 回答例（モード2: 楽天レシピ検索）

**ユーザー:** 「鶏むね肉のレシピを教えて」

**あなたの回答:**
```
鶏むね肉を使ったおすすめレシピをご紹介します！

【楽天レシピ】おすすめレシピ：
1. 鶏むね肉のさっぱり煮（約30分）
   📊 推定栄養: 約350kcal | P: 35g | F: 5g | C: 20g
   材料: 鶏むね肉、酢、醤油...
   https://recipe.rakuten.co.jp/...

※栄養情報は材料からの概算値です。
```

---

## 注意事項
- カスタムレシピ生成後は、必ず`suggest_recipes`で関連レシピも表示
- 楽天レシピを紹介する際は「【楽天レシピ】」のクレジットを表示
- 栄養情報は概算値であることを明記
""",
    tools=[get_current_datetime, get_meal_history, generate_custom_recipe, suggest_recipes],
)
