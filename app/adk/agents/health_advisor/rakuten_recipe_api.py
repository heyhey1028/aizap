"""楽天レシピAPIクライアント"""

import os
from typing import Optional

import httpx


class RakutenRecipeClient:
    """楽天レシピAPIのクライアント"""

    BASE_URL = "https://app.rakuten.co.jp/services/api/Recipe"
    API_VERSION = "20170426"

    def __init__(self):
        self.app_id = os.environ.get("RAKUTEN_APPLICATION_ID")

    def is_configured(self) -> bool:
        """APIが設定されているか確認"""
        return bool(self.app_id)

    def get_categories(self) -> dict:
        """カテゴリ一覧を取得

        Returns:
            カテゴリ情報を含む辞書
        """
        if not self.is_configured():
            return {"error": "RAKUTEN_APPLICATION_ID is not set"}

        url = f"{self.BASE_URL}/CategoryList/{self.API_VERSION}"
        params = {"applicationId": self.app_id}

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"error": f"API request failed: {str(e)}"}

    def get_ranking(self, category_id: Optional[str] = None) -> dict:
        """カテゴリ別ランキングを取得（最大4件）

        Args:
            category_id: カテゴリID（省略時は総合ランキング）

        Returns:
            レシピランキング情報を含む辞書
        """
        if not self.is_configured():
            return {"error": "RAKUTEN_APPLICATION_ID is not set"}

        url = f"{self.BASE_URL}/CategoryRanking/{self.API_VERSION}"
        params = {"applicationId": self.app_id}

        if category_id:
            params["categoryId"] = category_id

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            return {"error": f"API request failed: {str(e)}"}

    def search_category_by_keyword(self, keyword: str) -> list[dict]:
        """キーワードでカテゴリを検索

        Args:
            keyword: 検索キーワード（例: "鶏むね肉", "ヘルシー"）

        Returns:
            マッチしたカテゴリのリスト
            [{"category_id": "10-276", "category_name": "鶏むね肉", "category_type": "medium"}]

        Note:
            CategoryRanking APIで使用するcategory_idのフォーマット:
            - 大カテゴリ: "10"
            - 中カテゴリ: "10-276" (大カテゴリID-中カテゴリID)
            - 小カテゴリ: "10-276-824" (大カテゴリID-中カテゴリID-小カテゴリID)
        """
        if not self.is_configured():
            return []

        categories_data = self.get_categories()
        if "error" in categories_data:
            return []

        result = categories_data.get("result", {})
        matched_categories = []

        # 中カテゴリのルックアップマップを作成（小カテゴリのフルパス構築用）
        # medium_id -> large_id のマッピング
        # NOTE: APIが数値を返す可能性があるため、すべてstrに変換
        medium_to_large = {}
        for cat in result.get("medium", []):
            medium_id = str(cat.get("categoryId", ""))
            large_id = str(cat.get("parentCategoryId", ""))
            medium_to_large[medium_id] = large_id

        # 大カテゴリを検索（IDはそのまま使用）
        for cat in result.get("large", []):
            if keyword in cat.get("categoryName", ""):
                matched_categories.append({
                    "category_id": str(cat.get("categoryId", "")),
                    "category_name": cat.get("categoryName"),
                    "category_type": "large",
                })

        # 中カテゴリを検索（大カテゴリID-中カテゴリID形式）
        for cat in result.get("medium", []):
            if keyword in cat.get("categoryName", ""):
                large_id = str(cat.get("parentCategoryId", ""))
                medium_id = str(cat.get("categoryId", ""))
                full_category_id = f"{large_id}-{medium_id}"
                matched_categories.append({
                    "category_id": full_category_id,
                    "category_name": cat.get("categoryName"),
                    "category_type": "medium",
                    "parent_category_id": large_id,
                })

        # 小カテゴリを検索（大カテゴリID-中カテゴリID-小カテゴリID形式）
        for cat in result.get("small", []):
            if keyword in cat.get("categoryName", ""):
                medium_id = str(cat.get("parentCategoryId", ""))  # 中カテゴリID
                small_id = str(cat.get("categoryId", ""))
                large_id = medium_to_large.get(medium_id, "")
                if large_id:
                    full_category_id = f"{large_id}-{medium_id}-{small_id}"
                else:
                    # フォールバック: 中カテゴリIDと小カテゴリIDのみ
                    full_category_id = f"{medium_id}-{small_id}"
                matched_categories.append({
                    "category_id": full_category_id,
                    "category_name": cat.get("categoryName"),
                    "category_type": "small",
                    "parent_category_id": medium_id,
                })

        return matched_categories


# カテゴリIDの定義
RECIPE_CATEGORIES = {
    "rice": "10",       # 主食・ご飯もの
    "main_dish": "11",  # 主菜
    "side_dish": "12",  # 副菜
    "healthy": "30",    # ヘルシー料理
    "soup": "15",       # 汁物・スープ
    "salad": "16",      # サラダ
}

# カテゴリ名のマッピング（日本語）
CATEGORY_NAMES = {
    "10": "ご飯もの",
    "11": "主菜",
    "12": "副菜",
    "15": "汁物・スープ",
    "16": "サラダ",
    "30": "ヘルシー料理",
}


# 食材の栄養情報データベース（100gあたり）
# {"キーワード": {"calories": kcal, "protein": g, "fat": g, "carbs": g, "typical_amount": g}}
INGREDIENT_NUTRITION_DB = {
    # 肉類
    "鶏むね": {"calories": 108, "protein": 22.3, "fat": 1.5, "carbs": 0, "typical_amount": 150},
    "鶏もも": {"calories": 200, "protein": 16.2, "fat": 14.0, "carbs": 0, "typical_amount": 150},
    "鶏肉": {"calories": 150, "protein": 19.0, "fat": 8.0, "carbs": 0, "typical_amount": 150},
    "ささみ": {"calories": 105, "protein": 23.0, "fat": 0.8, "carbs": 0, "typical_amount": 100},
    "豚肉": {"calories": 216, "protein": 18.5, "fat": 15.1, "carbs": 0.2, "typical_amount": 100},
    "豚バラ": {"calories": 386, "protein": 14.2, "fat": 34.6, "carbs": 0.1, "typical_amount": 100},
    "豚ロース": {"calories": 263, "protein": 19.3, "fat": 19.2, "carbs": 0.2, "typical_amount": 100},
    "牛肉": {"calories": 250, "protein": 17.0, "fat": 20.0, "carbs": 0.3, "typical_amount": 100},
    "ひき肉": {"calories": 220, "protein": 17.0, "fat": 16.0, "carbs": 0.5, "typical_amount": 100},
    "ベーコン": {"calories": 405, "protein": 12.9, "fat": 39.1, "carbs": 0.3, "typical_amount": 30},
    "ハム": {"calories": 196, "protein": 16.5, "fat": 13.9, "carbs": 1.8, "typical_amount": 30},
    "ソーセージ": {"calories": 321, "protein": 11.5, "fat": 28.5, "carbs": 3.0, "typical_amount": 50},
    # 魚介類
    "鮭": {"calories": 133, "protein": 22.3, "fat": 4.1, "carbs": 0.1, "typical_amount": 80},
    "サーモン": {"calories": 133, "protein": 22.3, "fat": 4.1, "carbs": 0.1, "typical_amount": 80},
    "まぐろ": {"calories": 125, "protein": 26.4, "fat": 1.4, "carbs": 0.1, "typical_amount": 80},
    "ツナ": {"calories": 97, "protein": 18.0, "fat": 2.5, "carbs": 0.4, "typical_amount": 70},
    "さば": {"calories": 202, "protein": 20.7, "fat": 12.1, "carbs": 0.3, "typical_amount": 80},
    "えび": {"calories": 83, "protein": 18.4, "fat": 0.6, "carbs": 0.3, "typical_amount": 60},
    "いか": {"calories": 88, "protein": 18.1, "fat": 1.2, "carbs": 0.2, "typical_amount": 80},
    "たこ": {"calories": 76, "protein": 16.4, "fat": 0.7, "carbs": 0.1, "typical_amount": 60},
    # 卵・乳製品
    "卵": {"calories": 151, "protein": 12.3, "fat": 10.3, "carbs": 0.3, "typical_amount": 60},
    "たまご": {"calories": 151, "protein": 12.3, "fat": 10.3, "carbs": 0.3, "typical_amount": 60},
    "チーズ": {"calories": 339, "protein": 22.7, "fat": 26.0, "carbs": 1.4, "typical_amount": 20},
    "牛乳": {"calories": 67, "protein": 3.3, "fat": 3.8, "carbs": 4.8, "typical_amount": 200},
    "ヨーグルト": {"calories": 62, "protein": 3.6, "fat": 3.0, "carbs": 4.9, "typical_amount": 100},
    "バター": {"calories": 745, "protein": 0.6, "fat": 81.0, "carbs": 0.2, "typical_amount": 10},
    # 豆類
    "豆腐": {"calories": 72, "protein": 6.6, "fat": 4.2, "carbs": 1.6, "typical_amount": 150},
    "納豆": {"calories": 200, "protein": 16.5, "fat": 10.0, "carbs": 12.1, "typical_amount": 50},
    "大豆": {"calories": 417, "protein": 33.8, "fat": 19.7, "carbs": 28.2, "typical_amount": 30},
    "厚揚げ": {"calories": 150, "protein": 10.7, "fat": 11.3, "carbs": 0.9, "typical_amount": 100},
    # 野菜類
    "キャベツ": {"calories": 23, "protein": 1.3, "fat": 0.2, "carbs": 5.2, "typical_amount": 80},
    "レタス": {"calories": 12, "protein": 0.6, "fat": 0.1, "carbs": 2.8, "typical_amount": 50},
    "トマト": {"calories": 19, "protein": 0.7, "fat": 0.1, "carbs": 4.7, "typical_amount": 100},
    "玉ねぎ": {"calories": 37, "protein": 1.0, "fat": 0.1, "carbs": 8.8, "typical_amount": 100},
    "たまねぎ": {"calories": 37, "protein": 1.0, "fat": 0.1, "carbs": 8.8, "typical_amount": 100},
    "にんじん": {"calories": 37, "protein": 0.6, "fat": 0.1, "carbs": 9.1, "typical_amount": 50},
    "じゃがいも": {"calories": 76, "protein": 1.6, "fat": 0.1, "carbs": 17.6, "typical_amount": 100},
    "ブロッコリー": {"calories": 33, "protein": 4.3, "fat": 0.5, "carbs": 5.2, "typical_amount": 80},
    "ほうれん草": {"calories": 20, "protein": 2.2, "fat": 0.4, "carbs": 3.1, "typical_amount": 80},
    "もやし": {"calories": 14, "protein": 1.7, "fat": 0.1, "carbs": 2.6, "typical_amount": 100},
    "なす": {"calories": 22, "protein": 1.1, "fat": 0.1, "carbs": 5.1, "typical_amount": 80},
    "ピーマン": {"calories": 22, "protein": 0.9, "fat": 0.2, "carbs": 5.1, "typical_amount": 30},
    "きのこ": {"calories": 18, "protein": 2.7, "fat": 0.4, "carbs": 3.1, "typical_amount": 50},
    "しめじ": {"calories": 18, "protein": 2.7, "fat": 0.4, "carbs": 3.1, "typical_amount": 50},
    "えのき": {"calories": 22, "protein": 2.7, "fat": 0.2, "carbs": 3.7, "typical_amount": 50},
    "しいたけ": {"calories": 18, "protein": 3.0, "fat": 0.4, "carbs": 4.9, "typical_amount": 30},
    "大根": {"calories": 18, "protein": 0.4, "fat": 0.1, "carbs": 4.1, "typical_amount": 100},
    "白菜": {"calories": 14, "protein": 0.8, "fat": 0.1, "carbs": 3.2, "typical_amount": 100},
    "ねぎ": {"calories": 28, "protein": 1.4, "fat": 0.1, "carbs": 7.2, "typical_amount": 30},
    "にんにく": {"calories": 134, "protein": 6.0, "fat": 0.9, "carbs": 26.3, "typical_amount": 5},
    "しょうが": {"calories": 30, "protein": 0.9, "fat": 0.3, "carbs": 6.6, "typical_amount": 5},
    "アボカド": {"calories": 187, "protein": 2.5, "fat": 18.7, "carbs": 6.2, "typical_amount": 70},
    # 主食
    "ご飯": {"calories": 168, "protein": 2.5, "fat": 0.3, "carbs": 37.1, "typical_amount": 150},
    "米": {"calories": 168, "protein": 2.5, "fat": 0.3, "carbs": 37.1, "typical_amount": 150},
    "白米": {"calories": 168, "protein": 2.5, "fat": 0.3, "carbs": 37.1, "typical_amount": 150},
    "パスタ": {"calories": 149, "protein": 5.2, "fat": 0.9, "carbs": 28.4, "typical_amount": 100},
    "うどん": {"calories": 105, "protein": 2.6, "fat": 0.4, "carbs": 21.6, "typical_amount": 200},
    "そば": {"calories": 132, "protein": 4.8, "fat": 1.0, "carbs": 26.0, "typical_amount": 180},
    "パン": {"calories": 264, "protein": 9.3, "fat": 4.4, "carbs": 46.7, "typical_amount": 60},
    "食パン": {"calories": 264, "protein": 9.3, "fat": 4.4, "carbs": 46.7, "typical_amount": 60},
    # 調味料・油
    "油": {"calories": 921, "protein": 0, "fat": 100, "carbs": 0, "typical_amount": 10},
    "サラダ油": {"calories": 921, "protein": 0, "fat": 100, "carbs": 0, "typical_amount": 10},
    "オリーブオイル": {"calories": 921, "protein": 0, "fat": 100, "carbs": 0, "typical_amount": 10},
    "ごま油": {"calories": 921, "protein": 0, "fat": 100, "carbs": 0, "typical_amount": 5},
    "マヨネーズ": {"calories": 703, "protein": 1.5, "fat": 75.3, "carbs": 3.6, "typical_amount": 15},
    "砂糖": {"calories": 384, "protein": 0, "fat": 0, "carbs": 99.2, "typical_amount": 10},
    "みりん": {"calories": 241, "protein": 0.3, "fat": 0, "carbs": 43.2, "typical_amount": 15},
}


def estimate_nutrition_from_materials(materials: list[str]) -> dict:
    """材料リストからカロリー・PFCを概算する

    Args:
        materials: 材料名のリスト（例: ["鶏むね肉 200g", "玉ねぎ 1個", "醤油 大さじ2"]）

    Returns:
        概算栄養情報
        {
            "estimated_calories": 概算カロリー,
            "estimated_protein": 概算タンパク質,
            "estimated_fat": 概算脂質,
            "estimated_carbs": 概算炭水化物,
            "matched_ingredients": マッチした食材リスト,
            "is_estimate": True（概算であることを示す）
        }
    """
    total_calories = 0
    total_protein = 0.0
    total_fat = 0.0
    total_carbs = 0.0
    matched_ingredients = []

    for material in materials:
        material_lower = material.lower()

        # データベースから一致する食材を検索
        for ingredient_key, nutrition in INGREDIENT_NUTRITION_DB.items():
            if ingredient_key in material_lower or ingredient_key in material:
                # 典型的な量（typical_amount）で計算
                typical = nutrition["typical_amount"]
                factor = typical / 100  # 100gあたりの値から換算

                cal = int(nutrition["calories"] * factor)
                prot = round(nutrition["protein"] * factor, 1)
                fat = round(nutrition["fat"] * factor, 1)
                carbs = round(nutrition["carbs"] * factor, 1)

                total_calories += cal
                total_protein += prot
                total_fat += fat
                total_carbs += carbs

                matched_ingredients.append({
                    "name": ingredient_key,
                    "original": material,
                    "calories": cal,
                    "protein": prot,
                    "fat": fat,
                    "carbs": carbs,
                })
                break  # 1つの材料につき1回だけマッチ

    return {
        "estimated_calories": total_calories,
        "estimated_protein": round(total_protein, 1),
        "estimated_fat": round(total_fat, 1),
        "estimated_carbs": round(total_carbs, 1),
        "matched_ingredients": matched_ingredients,
        "is_estimate": True,
        "note": "材料から概算した推定値です。実際の値とは異なる場合があります。",
    }
