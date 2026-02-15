from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 日本標準時（JST = UTC+9）
# Python 3.9+ の標準ライブラリ zoneinfo を使用（pytz は非推奨）
JST = ZoneInfo("Asia/Tokyo")


def get_jst_now() -> datetime:
    """JST の現在時刻を取得する。

    Returns:
        timezone-aware な JST の現在時刻
    """
    return datetime.now(JST)


def get_today_range_jst() -> tuple[datetime, datetime]:
    """JST の「今日」の範囲を取得する。

    Returns:
        (今日の0:00 JST, 明日の0:00 JST) のタプル
    """
    now = get_jst_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    return today_start, tomorrow_start


def parse_date_jst(date_str: str) -> datetime:
    """日付文字列を JST の datetime に変換する。

    Args:
        date_str: "YYYY-MM-DD" 形式の日付文字列

    Returns:
        JST の 0:00 に設定された timezone-aware datetime

    Raises:
        ValueError: 日付形式が不正な場合
    """
    naive = datetime.strptime(date_str, "%Y-%m-%d")
    return naive.replace(tzinfo=JST)


def get_current_datetime() -> dict:
    """現在の日時を取得します（日本時間）。"""
    now = get_jst_now()
    return {
        "status": "success",
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": "Asia/Tokyo (JST)",
        "weekday": now.strftime("%A"),
        "weekday_jp": ["月", "火", "水", "木", "金", "土", "日"][now.weekday()],
    }
