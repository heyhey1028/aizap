from datetime import datetime

def get_current_datetime() -> dict:
  """現在の日時を取得します。"""
  now = datetime.now()
  return {
      "status": "success",
      "datetime": now.isoformat(),
      "date": now.strftime("%Y-%m-%d"),
      "time": now.strftime("%H:%M:%S"),
      "weekday": now.strftime("%A"),
      "weekday_jp": ["月", "火", "水", "木", "金", "土", "日"][now.weekday()],
  }

