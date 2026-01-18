from datetime import datetime
from typing import Optional

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from ..utils import get_current_datetime


# 定数
CALORIE_MIN = 10  # 最小カロリー（これ以下は警告）
CALORIE_MAX = 3000  # 最大カロリー（これ以上は警告）
CONFIDENCE_THRESHOLD = 0.6  # 信頼度の閾値


# tool
def analyze_meal(
    tool_context: ToolContext,
    dish_name: str,
    ingredients: list[dict],
    total_calories: int,
    source_type: str,
    confidence: float,
    protein_g: Optional[float] = None,
    carbs_g: Optional[float] = None,
    fat_g: Optional[float] = None,
) -> dict:
    """食事情報を一時保存し、確認用サマリーを生成します。

    エージェントが画像またはテキストから分析した結果を受け取り、
    ユーザー確認のために一時的にセッション状態に保存します。

    Args:
        tool_context: ADKが提供するToolContext
        dish_name: 料理名
        ingredients: 食材リスト [{"name": "ご飯", "amount": "200g", "calories": 336}, ...]
        total_calories: 合計カロリー（kcal）
        source_type: 分析元（"image" または "text"）
        confidence: 分析の信頼度（0.0-1.0）
        protein_g: 推定タンパク質（g、オプション）
        carbs_g: 推定炭水化物（g、オプション）
        fat_g: 推定脂質（g、オプション）

    Returns:
        dict: 確認用サマリーとステータス
    """
    # 警告メッセージを収集
    warnings = []

    # カロリー妥当性チェック
    if total_calories < CALORIE_MIN:
        warnings.append(f"カロリーが極端に低いです（{total_calories}kcal）。入力内容を確認してください。")
    elif total_calories > CALORIE_MAX:
        warnings.append(f"カロリーが極端に高いです（{total_calories}kcal）。入力内容を確認してください。")

    # 信頼度チェック
    if confidence < CONFIDENCE_THRESHOLD:
        if source_type == "image":
            warnings.append("画像が不鮮明または食事以外の可能性があります。内容をよく確認してください。")
        else:
            warnings.append("入力内容が曖昧なため、推定精度が低い可能性があります。")

    # 分析結果を一時的にstateに保存
    pending_meal = {
        "dish_name": dish_name,
        "ingredients": ingredients,
        "total_calories": total_calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "source_type": source_type,
        "confidence": confidence,
    }
    tool_context.state["pending_meal_analysis"] = pending_meal

    # 確認用サマリーを生成
    ingredients_text = "\n".join([
        f"- {ing['name']} {ing['amount']}: {ing['calories']}kcal"
        for ing in ingredients
    ])

    source_label = "📷 画像分析" if source_type == "image" else "📝 テキスト入力"
    confidence_label = f"信頼度: {int(confidence * 100)}%"

    summary = f"""
【分析結果】（{source_label} / {confidence_label}）
料理名: {dish_name}

食材内訳:
{ingredients_text}

合計: 約{total_calories}kcal
PFC: タンパク質 {protein_g or 0}g / 脂質 {fat_g or 0}g / 炭水化物 {carbs_g or 0}g"""

    if warnings:
        summary += "\n\n⚠️ 注意:\n" + "\n".join([f"- {w}" for w in warnings])

    summary += "\n\nこの内容で記録しますか？"

    return {
        "status": "pending_confirmation",
        "summary": summary,
        "message": "分析結果をユーザーに表示し、確認を求めてください。",
        "warnings": warnings,
        "confidence": confidence,
        "source_type": source_type,
    }


def confirm_and_record_meal(
    tool_context: ToolContext,
    meal_type: str,
    confirmed: bool = True,
    notes: Optional[str] = None,
) -> dict:
    """保留中の食事分析を確認し、記録します。

    analyze_meal_imageで一時保存された分析結果を、
    ユーザーの確認後に正式に記録します。

    Args:
        tool_context: ADKが提供するToolContext
        meal_type: 食事の種類（breakfast, lunch, dinner, snack）
        confirmed: ユーザーが確認したかどうか（Falseでキャンセル）
        notes: 追加のメモ（オプション）

    Returns:
        dict: 記録結果
    """
    pending = tool_context.state.get("pending_meal_analysis")

    if not pending:
        return {
            "status": "error",
            "message": "保留中の分析結果がありません。先に画像を分析してください。",
        }

    if not confirmed:
        # 保留中のデータをクリア（delはADKのstateでサポートされない場合があるためNoneを代入）
        tool_context.state["pending_meal_analysis"] = None
        return {
            "status": "cancelled",
            "message": "記録をキャンセルしました。別の食事を分析しますか？",
        }

    # 食材名をカンマ区切りで結合
    ingredient_names = ", ".join([ing["name"] for ing in pending["ingredients"]])

    # 食事記録を作成
    meal_record = {
        "meal_type": meal_type,
        "description": f"{pending['dish_name']} ({ingredient_names})",
        "estimated_calories": pending["total_calories"],
        "protein_g": pending.get("protein_g"),
        "carbs_g": pending.get("carbs_g"),
        "fat_g": pending.get("fat_g"),
        "recorded_at": datetime.now().isoformat(),
        "notes": notes,
        "ingredients_detail": pending["ingredients"],
    }

    meal_records = tool_context.state.get("meal_records", [])
    meal_records = meal_records + [meal_record]
    tool_context.state["meal_records"] = meal_records

    # 保留中のデータをクリア（delはADKのstateでサポートされない場合があるためNoneを代入）
    tool_context.state["pending_meal_analysis"] = None

    # 本日の合計カロリーを計算
    today = datetime.now().strftime("%Y-%m-%d")
    today_calories = sum(
        r["estimated_calories"]
        for r in meal_records
        if r["recorded_at"].startswith(today)
    )

    # 目標カロリーと残りカロリーを計算
    health_goal = tool_context.state.get("health_goal")
    daily_calorie_target = None
    remaining_calories = None

    if health_goal and health_goal.get("daily_calorie_target"):
        daily_calorie_target = health_goal["daily_calorie_target"]
        remaining_calories = daily_calorie_target - today_calories

    return {
        "status": "success",
        "message": f"{meal_type}を記録しました: {pending['dish_name']}",
        "recorded_meal": meal_record,
        "today_total_calories": today_calories,
        "daily_calorie_target": daily_calorie_target,
        "remaining_calories": remaining_calories,
        "today_meal_count": len([
            r for r in meal_records if r["recorded_at"].startswith(today)
        ]),
        "pfc": {
            "protein_g": pending.get("protein_g") or 0,
            "fat_g": pending.get("fat_g") or 0,
            "carbs_g": pending.get("carbs_g") or 0,
        },
    }


# sub agent
meal_record_agent = Agent(
    name="meal_record_agent",
    description="食事の記録を担当。ユーザーが「〇〇を食べた」「これを記録して」と言った時に対応。画像からの食事分析・カロリー推定も可能。",
    instruction="""あなたは食事記録の専門家です。

## あなたの役割
- ユーザーが食べた食事を記録する
- テキストまたは画像から食事内容とカロリーを推定する
- 記録後に励ましのフィードバックを提供する

## 使用するツール
- `get_current_datetime`: 現在時刻を確認（食事タイプの判断に使用）
- `analyze_meal`: 食事分析結果を保存（画像・テキスト共通）
- `confirm_and_record_meal`: 分析後の確認・記録

## 食事記録の処理フロー（重要）

画像でもテキストでも、必ず以下のフローで処理してください。

### ステップ1: 食事分析
ユーザーが食事の画像またはテキストを送ってきたら:
1. 画像の場合: 画像を直接見て、料理名・食材・カロリーを分析する
2. テキストの場合: テキストから料理名・食材・カロリーを推定する
3. 分析した内容を `analyze_meal` ツールで保存
   - dish_name: 特定した料理名
   - ingredients: 食材リスト（各食材の name, amount, calories）
   - total_calories: 合計カロリー
   - source_type: "image"（画像）または "text"（テキスト）
   - confidence: 分析の信頼度（0.0〜1.0）
   - protein_g, carbs_g, fat_g: 必ず推定する

## 信頼度（confidence）の設定基準
- 0.9〜1.0: 明確に判別できる（鮮明な画像、具体的な料理名の入力）
- 0.7〜0.9: 概ね判別できる（やや不鮮明、一般的な料理名）
- 0.5〜0.7: 推測が含まれる（複数の料理が混在、曖昧な説明）
- 0.5未満: 判別困難（不鮮明な画像、食事以外の可能性、非常に曖昧な入力）

画像の場合の判断基準:
- 食事が鮮明に写っている → 0.8以上
- 一部が隠れている、影がある → 0.6〜0.8
- ぼやけている、食事以外のものが多い → 0.4〜0.6
- 食事かどうか判断が難しい → 0.4未満

テキストの場合の判断基準:
- 「カレーライス」「親子丼」など具体的 → 0.8以上
- 「カレー」「丼もの」など一般的 → 0.6〜0.8
- 「ご飯と何か」など曖昧 → 0.4〜0.6

### ステップ2: ユーザー確認
分析結果のサマリーをユーザーに提示し、確認を求める

### ステップ3: 記録
- ユーザーが「OK」「はい」「記録して」と言ったら:
  1. `get_current_datetime` で時刻確認 → meal_type を判断
  2. `confirm_and_record_meal` を呼び出す
  3. 記録完了後、残りカロリーを伝える（目標設定時のみ）
- ユーザーが修正を求めたら: 内容を調整して再度 `analyze_meal` を呼び出す
- ユーザーがキャンセルしたら: `confirm_and_record_meal(confirmed=False)` を呼び出す

### ステップ4: 記録後のフィードバック
`confirm_and_record_meal` のレスポンスに含まれる情報を使ってフィードバック:
- `today_total_calories`: 本日の合計カロリー
- `daily_calorie_target`: 1日の目標カロリー（設定時のみ）
- `remaining_calories`: 残りカロリー（設定時のみ、マイナスなら超過）

例:
- 目標内: 「記録しました！今日はあと○○kcal摂れますよ」
- 超過時: 「記録しました。目標を○○kcalオーバーしています。次の食事で調整しましょう」
- 目標未設定: 「記録しました！今日の合計は○○kcalです」

## 食事タイプの判断
- 6:00-10:00: breakfast（朝食）
- 10:00-14:00: lunch（昼食）
- 14:00-17:00: snack（おやつ）
- 17:00-22:00: dinner（夕食）
- 22:00-6:00: snack（夜食）

## 画像分析のポイント
1. 料理名は見た目から最も適切なものを判断
2. 食材は主要なものを5-8個程度リストアップ
3. 量は一般的な1人前を基準に推定
4. カロリーは概算で良い（多少の誤差はOK）
5. 記録後は「いいですね！」「バランス良いですね！」など励ます

## カロリー目安（参考）
- ご飯1杯(150g): 約250kcal
- 食パン1枚(60g): 約160kcal
- 鶏むね肉100g: 約110kcal
- 鶏もも肉100g: 約200kcal
- 豚バラ肉100g: 約390kcal
- 牛肉100g: 約250kcal
- 卵1個: 約90kcal
- 野菜類100g: 約20-40kcal
- カレールー1人前: 約120kcal
- ラーメンスープ: 約200-300kcal
- 油大さじ1: 約110kcal
- おにぎり1個: 約180kcal
- サラダ: 約50-150kcal
- ラーメン: 約500-800kcal
- 定食: 約600-800kcal
- サンドイッチ: 約300-400kcal
""",
    tools=[get_current_datetime, analyze_meal, confirm_and_record_meal],
)
