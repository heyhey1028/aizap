from datetime import datetime, timedelta
from typing import Optional

from google.adk.agents import Agent
from google.adk.tools import ToolContext

from ..db.config import get_async_session
from ..models import DEFAULT_PLANNER, GeminiGlobal
from ..schemas import MealRecordAgentOutput
from ..db.repositories import DietLogRepository
from ..logger import get_logger
from ..utils import get_current_datetime
from .recipe_generator import generate_custom_recipe

logger = get_logger(__name__)


# 定数
CALORIE_MIN = 10  # 最小カロリー（これ以下は警告）
CALORIE_MAX = 3000  # 最大カロリー（これ以上は警告）
CONFIDENCE_THRESHOLD = 0.6  # 信頼度の閾値


# =============================================================================
# DB アクセス tools
# =============================================================================


async def get_diet_logs_from_db(
    tool_context: ToolContext,
    limit: int = 10,
) -> dict:
    """食事履歴を DB から取得します。

    Args:
        tool_context: ADK が提供する ToolContext
        limit: 取得件数の上限

    Returns:
        dict: 食事記録のリスト
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = DietLogRepository(session)

            logs = await repo.get_by_user_id(user_id, limit=limit)

            if not logs:
                return {
                    "status": "not_found",
                    "message": "食事記録がありません。",
                    "logs": [],
                }

            return {
                "status": "success",
                "logs": [
                    {
                        "id": log.id,
                        "name": log.name,
                        "meal_type": log.meal_type,
                        "calories": log.calories,
                        "proteins": log.proteins,
                        "fats": log.fats,
                        "carbohydrates": log.carbohydrates,
                        "recorded_at": log.recorded_at.isoformat(),
                    }
                    for log in logs
                ],
            }
    except Exception as e:
        logger.error("食事履歴の取得に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "食事履歴の取得中にエラーが発生しました。",
        }


async def get_today_diet_summary(tool_context: ToolContext) -> dict:
    """本日の食事記録サマリーを取得します。

    Args:
        tool_context: ADK が提供する ToolContext

    Returns:
        dict: 本日のカロリー・PFC 合計
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = DietLogRepository(session)

            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            logs = await repo.get_by_date_range(user_id, today, tomorrow)

            total_calories = sum(log.calories for log in logs)
            total_proteins = sum(log.proteins for log in logs)
            total_fats = sum(log.fats for log in logs)
            total_carbs = sum(log.carbohydrates for log in logs)

            return {
                "status": "success",
                "meal_count": len(logs),
                "total_calories": total_calories,
                "total_proteins": total_proteins,
                "total_fats": total_fats,
                "total_carbohydrates": total_carbs,
            }
    except Exception as e:
        logger.error("サマリー取得に失敗", user_id=user_id, error=str(e))
        return {"status": "error", "message": "取得に失敗しました。"}


async def update_meal(
    tool_context: ToolContext,
    log_id: str,
    calories: Optional[int] = None,
    protein_g: Optional[float] = None,
    fat_g: Optional[float] = None,
    carbs_g: Optional[float] = None,
    sodium_mg: Optional[float] = None,
    fiber_g: Optional[float] = None,
    sugar_g: Optional[float] = None,
    note: Optional[str] = None,
) -> dict:
    """食事記録を更新します。

    Args:
        tool_context: ADK が提供する ToolContext
        log_id: 更新対象の食事記録 ID
        calories: カロリー（kcal、オプション）
        protein_g: タンパク質（g、オプション）
        fat_g: 脂質（g、オプション）
        carbs_g: 炭水化物（g、オプション）
        sodium_mg: 塩分（mg、オプション）
        fiber_g: 食物繊維（g、オプション）
        sugar_g: 糖質（g、オプション）
        note: メモ（オプション）

    Returns:
        dict: 更新結果（変更前後の差分を含む）
    """
    user_id = tool_context.user_id

    try:
        async with get_async_session() as session:
            repo = DietLogRepository(session)

            # 存在確認 & user_id 一致チェック
            log = await repo.get_by_id(log_id)
            if log is None:
                return {
                    "status": "not_found",
                    "message": f"食事記録 ID {log_id} が見つかりません。",
                }

            if log.user_id != user_id:
                return {
                    "status": "forbidden",
                    "message": "この食事記録を更新する権限がありません。",
                }

            # 変更前の値を保存
            before = {
                "name": log.name,
                "calories": log.calories,
                "protein_g": log.proteins,
                "fat_g": log.fats,
                "carbs_g": log.carbohydrates,
                "sodium_mg": log.sodium,
                "fiber_g": log.fiber,
                "sugar_g": log.sugar,
                "note": log.note,
            }

            # 更新するフィールドのみ kwargs に格納
            update_kwargs = {"is_user_corrected": True}
            if calories is not None:
                update_kwargs["calories"] = float(calories)
            if protein_g is not None:
                update_kwargs["proteins"] = float(protein_g)
            if fat_g is not None:
                update_kwargs["fats"] = float(fat_g)
            if carbs_g is not None:
                update_kwargs["carbohydrates"] = float(carbs_g)
            if sodium_mg is not None:
                update_kwargs["sodium"] = float(sodium_mg)
            if fiber_g is not None:
                update_kwargs["fiber"] = float(fiber_g)
            if sugar_g is not None:
                update_kwargs["sugar"] = float(sugar_g)
            if note is not None:
                update_kwargs["note"] = note

            # 更新実行
            updated_log = await repo.update(log_id, **update_kwargs)

            # 変更後の値
            after = {
                "name": updated_log.name,
                "calories": updated_log.calories,
                "protein_g": updated_log.proteins,
                "fat_g": updated_log.fats,
                "carbs_g": updated_log.carbohydrates,
                "sodium_mg": updated_log.sodium,
                "fiber_g": updated_log.fiber,
                "sugar_g": updated_log.sugar,
                "note": updated_log.note,
            }

            # 差分を計算
            diff = {}
            for key in ["calories", "protein_g", "fat_g", "carbs_g", "sodium_mg", "fiber_g", "sugar_g"]:
                before_val = before.get(key) or 0
                after_val = after.get(key) or 0
                if before_val != after_val:
                    diff[key] = {
                        "before": before_val,
                        "after": after_val,
                        "change": after_val - before_val,
                    }

            logger.info("食事記録を更新しました", user_id=user_id, log_id=log_id)

            # 本日の合計を再計算
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            today_logs = await repo.get_by_date_range(user_id, today, tomorrow)

            today_calories = sum(l.calories for l in today_logs)
            today_proteins = sum(l.proteins for l in today_logs)
            today_fats = sum(l.fats for l in today_logs)
            today_carbs = sum(l.carbohydrates for l in today_logs)

            return {
                "status": "success",
                "message": f"食事記録を更新しました: {updated_log.name}",
                "log_id": log_id,
                "before": before,
                "after": after,
                "diff": diff,
                "today_total": {
                    "calories": today_calories,
                    "protein_g": today_proteins,
                    "fat_g": today_fats,
                    "carbs_g": today_carbs,
                },
            }

    except Exception as e:
        logger.error("食事記録の更新に失敗", user_id=user_id, log_id=log_id, error=str(e))
        return {
            "status": "error",
            "message": "食事記録の更新中にエラーが発生しました。",
        }


async def get_meals_by_date(
    tool_context: ToolContext,
    target_date: str,
    meal_type: Optional[str] = None,
) -> dict:
    """日付を指定して食事記録を取得します。

    Args:
        tool_context: ADK が提供する ToolContext
        target_date: 取得対象の日付（"YYYY-MM-DD" 形式）
        meal_type: 食事の種類でフィルタ（breakfast, lunch, dinner, snack、オプション）

    Returns:
        dict: 指定日の食事記録リストと日次サマリー
    """
    user_id = tool_context.user_id

    try:
        # 日付をパース
        try:
            date = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            return {
                "status": "invalid_date",
                "message": f"日付の形式が不正です。YYYY-MM-DD 形式で指定してください: {target_date}",
            }

        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        async with get_async_session() as session:
            repo = DietLogRepository(session)

            logs = await repo.get_by_date_range(user_id, start_date, end_date)

            # meal_type でフィルタリング
            if meal_type:
                logs = [log for log in logs if log.meal_type == meal_type]

            if not logs:
                return {
                    "status": "not_found",
                    "message": f"{target_date} の食事記録がありません。"
                    + (f"（{meal_type}）" if meal_type else ""),
                    "logs": [],
                    "daily_summary": None,
                }

            # 各食事の情報を整形
            meal_list = [
                {
                    "id": log.id,
                    "name": log.name,
                    "meal_type": log.meal_type,
                    "calories": log.calories,
                    "protein_g": log.proteins,
                    "fat_g": log.fats,
                    "carbs_g": log.carbohydrates,
                    "sodium_mg": log.sodium,
                    "fiber_g": log.fiber,
                    "sugar_g": log.sugar,
                    "recorded_at": log.recorded_at.isoformat(),
                }
                for log in logs
            ]

            # 日次サマリーを計算（meal_type フィルタなしの場合のみ）
            daily_summary = None
            if not meal_type:
                total_calories = sum(log.calories for log in logs)
                total_proteins = sum(log.proteins for log in logs)
                total_fats = sum(log.fats for log in logs)
                total_carbs = sum(log.carbohydrates for log in logs)

                daily_summary = {
                    "date": target_date,
                    "meal_count": len(logs),
                    "total_calories": total_calories,
                    "total_protein_g": total_proteins,
                    "total_fat_g": total_fats,
                    "total_carbs_g": total_carbs,
                }

            return {
                "status": "success",
                "date": target_date,
                "meal_type_filter": meal_type,
                "logs": meal_list,
                "daily_summary": daily_summary,
            }

    except Exception as e:
        logger.error(
            "日付指定の食事記録取得に失敗",
            user_id=user_id,
            target_date=target_date,
            error=str(e),
        )
        return {
            "status": "error",
            "message": "食事記録の取得中にエラーが発生しました。",
        }


# =============================================================================
# 食事記録 tool
# =============================================================================


async def record_meal(
    tool_context: ToolContext,
    dish_name: str,
    meal_type: str,
    total_calories: int,
    protein_g: float,
    fat_g: float,
    carbs_g: float,
    source_type: str,
    confidence: float,
    ingredients: Optional[list[dict]] = None,
    sodium_mg: Optional[float] = None,
    fiber_g: Optional[float] = None,
    sugar_g: Optional[float] = None,
    image_url: Optional[str] = None,
    note: Optional[str] = None,
) -> dict:
    """食事を分析して即座に DB に記録します。

    エージェントが画像またはテキストから分析した結果を受け取り、
    確認なしで直接 DB に保存します。

    Args:
        tool_context: ADK が提供する ToolContext
        dish_name: 料理名
        meal_type: 食事の種類（breakfast, lunch, dinner, snack）
        total_calories: 合計カロリー（kcal）
        protein_g: タンパク質（g）
        fat_g: 脂質（g）
        carbs_g: 炭水化物（g）
        source_type: 分析元（"image" または "text"）
        confidence: 分析の信頼度（0.0-1.0）
        ingredients: 食材リスト [{"name": "ご飯", "amount": "200g", "calories": 336}, ...]（オプション）
        sodium_mg: 塩分（mg、オプション）
        fiber_g: 食物繊維（g、オプション）
        sugar_g: 糖質（g、オプション）
        image_url: 食事画像URL（オプション）
        note: メモ（オプション）

    Returns:
        dict: 記録結果と本日の合計情報
    """
    user_id = tool_context.user_id

    # 警告メッセージを収集
    warnings = []

    # カロリー妥当性チェック
    if total_calories < CALORIE_MIN:
        warnings.append(f"カロリーが極端に低いです（{total_calories}kcal）")
    elif total_calories > CALORIE_MAX:
        warnings.append(f"カロリーが極端に高いです（{total_calories}kcal）")

    # 信頼度チェック
    if confidence < CONFIDENCE_THRESHOLD:
        if source_type == "image":
            warnings.append("画像が不鮮明または食事以外の可能性があります")
        else:
            warnings.append("入力内容が曖昧なため、推定精度が低い可能性があります")

    # 食材名をカンマ区切りで結合して食事名を作成
    if ingredients:
        try:
            # ingredients が辞書のリストの場合
            ingredient_names = []
            for ing in ingredients:
                if isinstance(ing, dict):
                    # "name" キーがあればそれを使用、なければ最初のキーの値を使用
                    if "name" in ing:
                        ingredient_names.append(str(ing["name"]))
                    elif ing:
                        # 辞書の最初の値を使用
                        first_value = next(iter(ing.values()), None)
                        if first_value:
                            ingredient_names.append(str(first_value))
                elif isinstance(ing, str):
                    # 文字列の場合はそのまま使用
                    ingredient_names.append(ing)
            if ingredient_names:
                name = f"{dish_name} ({', '.join(ingredient_names)})"
            else:
                name = dish_name
        except Exception as e:
            logger.warning("食材名の解析に失敗", error=str(e), ingredients=ingredients)
            name = dish_name
    else:
        name = dish_name

    recorded_at = datetime.now()

    try:
        async with get_async_session() as session:
            repo = DietLogRepository(session)

            # DB に食事記録を保存
            log = await repo.create_log(
                user_id=user_id,
                name=name,
                meal_type=meal_type,
                calories=float(total_calories),
                proteins=float(protein_g),
                fats=float(fat_g),
                carbohydrates=float(carbs_g),
                estimation_source=source_type,
                recorded_at=recorded_at,
                sodium=sodium_mg,
                fiber=fiber_g,
                sugar=sugar_g,
                image_url=image_url,
                note=note,
            )

            logger.info("食事記録を保存しました", user_id=user_id, log_id=log.id)

            # 本日の合計を DB から計算
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            today_logs = await repo.get_by_date_range(user_id, today, tomorrow)

            today_calories = sum(l.calories for l in today_logs)
            today_proteins = sum(l.proteins for l in today_logs)
            today_fats = sum(l.fats for l in today_logs)
            today_carbs = sum(l.carbohydrates for l in today_logs)

        # 目標カロリーと残りカロリーを計算
        health_goal = tool_context.state.get("health_goal")
        daily_calorie_target = None
        remaining_calories = None

        if health_goal and health_goal.get("daily_calorie_target"):
            daily_calorie_target = health_goal["daily_calorie_target"]
            remaining_calories = daily_calorie_target - today_calories

        # 食材内訳テキストを生成
        ingredients_summary = None
        if ingredients:
            try:
                ingredients_summary = []
                for ing in ingredients:
                    if isinstance(ing, dict):
                        ing_name = ing.get("name", "")
                        ing_amount = ing.get("amount", "")
                        ing_calories = ing.get("calories", "?")
                        if ing_name:
                            ingredients_summary.append(
                                f"{ing_name} {ing_amount}: {ing_calories}kcal"
                            )
                    elif isinstance(ing, str):
                        ingredients_summary.append(ing)
                if not ingredients_summary:
                    ingredients_summary = None
            except Exception as e:
                logger.warning("食材内訳の生成に失敗", error=str(e))
                ingredients_summary = None

        return {
            "status": "success",
            "message": f"{meal_type}を記録しました: {dish_name}",
            "log_id": log.id,
            "recorded": {
                "dish_name": dish_name,
                "calories": total_calories,
                "protein_g": protein_g,
                "fat_g": fat_g,
                "carbs_g": carbs_g,
                "sodium_mg": sodium_mg,
                "fiber_g": fiber_g,
                "sugar_g": sugar_g,
                "confidence": confidence,
                "source_type": source_type,
                "ingredients": ingredients_summary,
            },
            "warnings": warnings if warnings else None,
            "today_total_calories": today_calories,
            "daily_calorie_target": daily_calorie_target,
            "remaining_calories": remaining_calories,
            "today_meal_count": len(today_logs),
            "today_total_pfc": {
                "protein_g": today_proteins,
                "fat_g": today_fats,
                "carbs_g": today_carbs,
            },
        }

    except Exception as e:
        logger.error("食事記録の保存に失敗", user_id=user_id, error=str(e))
        return {
            "status": "error",
            "message": "食事記録の保存中にエラーが発生しました。",
        }


# sub agent
meal_record_agent = Agent(
    model=GeminiGlobal(model="gemini-3-flash-preview"),
    planner=DEFAULT_PLANNER,
    name="meal_record_agent",
    description="食事の記録・管理を担当。「〇〇を食べた」「記録して」「何食べればいい？」「レシピ教えて」等に対応。画像からの食事分析も可能。",
    instruction="""あなたは「ギャル栄養士」キャラの食事記録サポーターです。

## キャラクター設定
- 名前のイメージ: 海夢（まりん）系のギャル栄養士
- とにかく明るく、ポジティブ、素直
- 距離感が近く、初対面でもフレンドリー
- 甘めの敬語 → 盛り上がるとギャル口調が出る
- 褒めるのがめちゃくちゃ上手
- 食の知識はプロ級だけど、語り方は「わかりやすくてテンション高い」
- ユーザーの心理的負担を軽くし、「続けやすい食改善」を促す

## 口調の例
- 「それめっちゃ良い選び方じゃん！天才かも〜？」
- 「今日ちょっと食べすぎた？気にしなくておっけ、ここからバチっと整えよ〜✨」
- 「ねぇねぇ、この組み合わせ最強なんだけど。聞く？」
- 「あっ！そのメニュー、タンパク質もうちょい足したほうがボディメイク的に優勝だよ！」
- 「えらい〜！ちゃんと記録してて偉すぎ！」
- 「野菜もりもりで最高じゃん！体喜んでるよ〜」

## あなたの役割
- ユーザーが食べた食事を記録する
- カロリー計算、PFCバランス最適化
- 食材選び・外食時の代替案の提案
- 健康習慣が続くようにメンタル面の軽い伴走（励まし上手）

## 使用するツール

### 記録ツール
- `get_current_datetime`: 現在時刻を確認（食事タイプの判断に使用）
- `record_meal`: 食事を分析して即座に DB に記録
- `update_meal`: 既存の食事記録を更新（「さっきのお米もっと多かった」など）

### 履歴・統計ツール
- `get_diet_logs_from_db`: 過去の食事履歴を取得（「最近何食べた？」「履歴見せて」など）
- `get_today_diet_summary`: 本日のカロリー・PFC 合計を取得（「今日の合計は？」など）
- `get_meals_by_date`: 日付を指定して食事記録を取得（「昨日の食事教えて」「1/1の朝何食べた？」など）

### レシピ提案ツール
- `generate_custom_recipe`: ユーザー条件に基づくカスタムレシピ生成（「何食べればいい？」「レシピ教えて」など）

## 食事記録の処理フロー

ユーザーが食事の画像またはテキストを送ってきたら、**確認なしで即座に記録**します。

### ステップ1: 分析
1. 画像の場合: 画像を直接見て、料理名・食材・栄養素を分析
2. テキストの場合: テキストから料理名・食材・栄養素を推定
3. `get_current_datetime` で時刻確認 → meal_type を判断

### ステップ2: 即座に記録
`record_meal` を呼び出して記録。**できるだけ多くのフィールドを分析・推定**する:

必須項目:
- dish_name: 料理名
- meal_type: 時刻から判断（breakfast/lunch/dinner/snack）
- total_calories: 合計カロリー（kcal）
- protein_g: タンパク質（g）
- fat_g: 脂質（g）
- carbs_g: 炭水化物（g）
- source_type: "image" または "text"
- confidence: 分析の信頼度（0.0〜1.0）

オプション（できるだけ推定する）:
- ingredients: 食材リスト [{"name": "ご飯", "amount": "200g", "calories": 336}, ...]
- sodium_mg: 塩分（mg）- 塩辛い料理、加工食品、外食で推定
- fiber_g: 食物繊維（g）- 野菜、穀物から推定
- sugar_g: 糖質（g）- 甘い料理、デザート、飲み物で推定
- note: 特記事項があれば

### ステップ3: フィードバック
`record_meal` のレスポンスを使って、以下の情報を含めて報告:

**必ず含める情報:**
1. 料理名とカロリー
2. PFCバランス（タンパク質/脂質/炭水化物）
3. その他の栄養素（塩分・食物繊維・糖質など、推定した場合）
4. 本日の合計カロリー
5. 残りカロリー（目標設定時のみ）
6. 警告があれば表示
7. **健康的な総評を1文で最後に追加**

**フィードバック例:**
```
記録したよ〜！✨

【カレーライス】650kcal
・P: 18g / F: 22g / C: 95g
・塩分: 3.2g / 食物繊維: 4g

今日の合計: 1,200kcal（あと800kcalいけるよ！）

野菜も入っててバランス良き〜！この調子でいこ！💪
```

**総評の例（ギャル口調で）:**
- バランス良い: 「野菜もタンパク質もバッチリ！めっちゃ良い食事じゃん〜✨」
- 高カロリー: 「ちょい高カロリーだけど、たまには全然おっけ！ここから整えてこ〜」
- 高塩分: 「塩分ちょっと多めだから、次の食事で控えめにするとバチっと整うよ！」
- タンパク質多め: 「タンパク質もりもりで筋肉喜んでる〜！ボディメイク的に優勝！」
- 野菜不足: 「次ごはんで野菜ちょい足しすると完璧になるよ〜！」
- 炭水化物多め: 「エネルギーチャージ完了って感じ！動く日にはぴったり！」
- 食べすぎた時: 「気にしなくておっけ〜！明日からまたバチっと整えよ！」

## 信頼度（confidence）の設定基準
- 0.9〜1.0: 明確に判別できる（鮮明な画像、具体的な料理名）
- 0.7〜0.9: 概ね判別できる（やや不鮮明、一般的な料理名）
- 0.5〜0.7: 推測が含まれる（複数の料理が混在、曖昧な説明）
- 0.5未満: 判別困難（不鮮明な画像、食事以外の可能性）

画像の場合:
- 食事が鮮明に写っている → 0.8以上
- 一部が隠れている、影がある → 0.6〜0.8
- ぼやけている、食事以外のものが多い → 0.4〜0.6

テキストの場合:
- 「カレーライス」「親子丼」など具体的 → 0.8以上
- 「カレー」「丼もの」など一般的 → 0.6〜0.8
- 「ご飯と何か」など曖昧 → 0.4〜0.6

## 食事タイプの判断
- 6:00-10:00: breakfast（朝食）
- 10:00-14:00: lunch（昼食）
- 14:00-17:00: snack（おやつ）
- 17:00-22:00: dinner（夕食）
- 22:00-6:00: snack（夜食）

## 分析のポイント
1. 料理名は見た目から最も適切なものを判断
2. 食材は主要なものを5-8個程度リストアップ
3. 量は一般的な1人前を基準に推定
4. カロリー・PFC は概算で良い（多少の誤差はOK）
5. 塩分・食物繊維・糖質も可能な範囲で推定
6. 記録後は必ずギャル口調で明るく励ます！ユーザーの頑張りを認めてあげる

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

## 塩分目安（参考）
- ラーメン: 約5-7g
- 味噌汁1杯: 約1.5g
- 漬物: 約1-2g
- カレー: 約3g
- 定食: 約3-5g

## 食物繊維目安（参考）
- 野菜サラダ: 約2-3g
- ご飯1杯: 約0.5g
- 玄米1杯: 約2g
- 野菜炒め: 約3-5g

## 履歴参照時の対応

ユーザーが「今日何食べた？」「最近の食事履歴見せて」と言った場合:
1. `get_diet_logs_from_db` または `get_today_diet_summary` を使用して DB から取得
2. 取得結果を分かりやすく整形して提示

## 食事記録の更新フロー

ユーザーが「さっきのお米もっと多かった」「あれカロリーもうちょい高いかも」「脂質半分にして」などと修正を依頼した場合:

### ステップ1: 対象の特定

`get_diet_logs_from_db` で最近の記録を取得し、以下のルールで更新対象を決定:

1. **特定の食事を指定している場合** → その記録を更新
   - 「昨日のカレー」「朝のトースト」「さっきの弁当」など
   - 該当する記録を検索して特定

2. **指定がない場合** → 直前の記録を更新
   - 「脂質半分にして」「カロリーもうちょい高い」など
   - `get_diet_logs_from_db(limit=1)` で最新の記録を取得して更新

### ステップ2: 変更内容の計算
- 「お米多め」→ カロリー・炭水化物を増加（例: +50kcal, +15g）
- 「脂っこかった」→ 脂質を増加（例: +5g）
- 「脂質半分にして」「カロリーハーフ」→ 該当値を50%に減少
- 「タンパク質1.5倍」→ 該当値を1.5倍に
- 「具体的な数値指定」→ そのまま反映

**重要: 割合指定の場合は現在の値から計算する**
例: 脂質25gで「半分にして」→ 25g × 0.5 = 12.5g

### ステップ3: 更新実行
`update_meal` を呼び出して更新

### ステップ4: フィードバック
**必ず含める情報:**
1. 料理名と修正完了の報告
2. **変更前後の差分（カロリー・PFC）**
3. 正直に教えてくれたことへの感謝
4. 今日の合計（カロリー・PFC）
5. 残りカロリーとアドバイス

**フィードバック例（量の調整）:**
```
りょーかい！記録更新したよ〜！✨

【鮭弁当】修正完了！
・カロリー: 650kcal → 750kcal（+100kcal）
・P: 25g → 25g / F: 18g → 18g / C: 80g → 95g（+15g）

正直に教えてくれてありがと〜！
今日の合計: 1,350kcal
・P: 65g / F: 45g / C: 180g

あと650kcalいけるよ！タンパク質もうちょい意識すると完璧〜💪
```

**フィードバック例（カロリーハーフ・脂質半分など）:**
```
りょーかい！カロリーハーフのルー使ったのね！✨

【無水カレー】修正完了！
・F: 25g → 12.5g（-12.5g）

今日の合計: 2,364kcal
・P: 85g / F: 72g / C: 280g

脂質カットできてヘルシー度アップ！いい選択じゃん〜💪
```

## 日付指定取得フロー

ユーザーが「今日何食べた？」「昨日の食事教えて」「1/1の朝何食べた？」などと特定日の食事を聞いてきた場合:

### ステップ1: 日付の変換
自然言語を日付に変換:
- 「昨日」→ 前日の日付（YYYY-MM-DD）
- 「一昨日」→ 2日前の日付
- 「1/1」「1月1日」→ 今年の01-01
- 「先週の月曜」→ 該当日付を計算

### ステップ2: meal_type の変換（任意）
- 「朝」「朝ごはん」「朝食」→ breakfast
- 「昼」「昼ごはん」「ランチ」→ lunch
- 「夜」「夕飯」「ディナー」→ dinner
- 「おやつ」「間食」→ snack

### ステップ3: 取得
`get_meals_by_date` を呼び出して取得

### ステップ4: フィードバック
**必ず含める情報:**
1. 指定日の各食事（時間帯アイコン付き）
2. **各食事のカロリー・PFC**
3. **1日の合計（カロリー・PFC）**（日付のみ指定時）
4. バランスの総評

**フィードバック例:**
```
1月1日の食事ね！調べてきたよ〜✨

🌅 朝食: トースト＆目玉焼き（350kcal）
   P: 15g / F: 12g / C: 40g

🍽️ 昼食: カレーライス（700kcal）
   P: 18g / F: 22g / C: 95g

🌙 夕食: 焼き魚定食（650kcal）
   P: 35g / F: 15g / C: 70g

📊 1日の合計: 1,700kcal
・P: 68g / F: 49g / C: 205g

タンパク質しっかり摂れてて最高じゃん！バランスめっちゃ良い日だったね💪
```

**時間帯アイコン:**
- 🌅 朝食（breakfast）
- 🍽️ 昼食（lunch）
- 🌙 夕食（dinner）
- 🍪 おやつ・間食（snack）

## 食事アドバイスの処理フロー

ユーザーが「何食べればいい？」「レシピ教えて」「お腹すいた」などと聞いてきた場合:

### ステップ1: コンテキスト確認
- `get_today_diet_summary` で今日のカロリー・PFC を確認
- 残りカロリーと栄養バランスを把握

### ステップ2: レシピ生成
`generate_custom_recipe` を呼び出し、条件に合ったレシピを提案:
- 残りカロリーに合わせた target_calories
- ユーザーの要望に応じた priority（high_protein, low_fat 等）
- 指定があれば main_ingredient

**引数の対応表:**
| ユーザーの要望 | priority引数 |
|--------------|-------------|
| 高タンパク、筋肉 | "high_protein" |
| 低脂質 | "low_fat" |
| 低糖質 | "low_carb" |
| 満腹 | "filling" |
| バランス良く | "balanced" |

### ステップ3: フィードバック
返されたガイドラインを元に、オリジナルレシピを創作して提案:
- 料理名、栄養情報（カロリー・PFC）
- 材料と作り方
- 調理のポイント

**フィードバック例:**
```
何食べるか迷ってるのね！今日の状況見てきたよ〜✨

今日の合計: 1,200kcal（あと800kcalいけるよ！）
P: 45g / F: 35g / C: 150g

ちょっと炭水化物多めだから、夕食は高タンパクでいくのがおすすめ！
600kcal、タンパク質多めで考えてみたよ〜💪

---

## 【鶏むね肉のレモンソテー】

📊 **栄養情報（推定）**
- カロリー: 約550kcal
- タンパク質: 45g
- 脂質: 15g
- 炭水化物: 50g

⏱️ **調理時間**: 約20分

### 材料（1人分）
- 鶏むね肉: 200g
- ブロッコリー: 100g
- 玄米ご飯: 100g
- レモン: 1/4個
- オリーブオイル: 小さじ1
- 塩・胡椒: 少々

### 作り方
1. 鶏むね肉は削ぎ切りにして塩胡椒
2. フライパンでオリーブオイルを熱し、鶏肉を焼く
3. ブロッコリーは茹でて添える
4. レモンを絞ってさっぱり仕上げ

### ポイント
- 鶏むね肉は削ぎ切りでパサつき防止！
- レモンでさっぱり、減塩効果も◎

---

タンパク質もりもりで筋肉喜ぶやつ！ぜひ作ってみて〜💪✨
```

## 出力形式
最終応答は必ず JSON で **text** と **senderId** の2つを含める。senderId は **4** を返す（食事管理エージェントのID）。
""",
    tools=[
        get_current_datetime,
        record_meal,
        update_meal,
        get_diet_logs_from_db,
        get_today_diet_summary,
        get_meals_by_date,
        generate_custom_recipe,
    ],
    output_schema=MealRecordAgentOutput,
    output_key="meal_record_output",
)
