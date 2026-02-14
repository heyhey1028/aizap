"""共通モデル設定

すべてのエージェントで使用するモデルと thinking 設定を一元管理する。
変更時はここを修正するだけで全エージェントに反映される。
"""

from google.adk.planners import BuiltInPlanner
from google.genai import types

DEFAULT_MODEL = "gemini-2.5-flash"

# thinking_budget でモデルの思考量を制御（Gemini 2.5 系は thinkingBudget を使用）
DEFAULT_PLANNER = BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_budget=2048,
    )
)
