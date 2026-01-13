FROM python:3.12-slim

WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ポート設定
ENV PORT=8080
EXPOSE 8080

# 起動コマンド
CMD ["python", "main.py"]
