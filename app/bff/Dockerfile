FROM node:22-slim AS base

# pnpm をインストール
RUN corepack enable && corepack prepare pnpm@latest --activate

FROM base AS deps

WORKDIR /app

# 依存関係ファイルをコピー
COPY package.json pnpm-lock.yaml* ./

# 依存関係をインストール
RUN pnpm install --frozen-lockfile

FROM base AS builder

WORKDIR /app

# 依存関係をコピー
COPY --from=deps /app/node_modules ./node_modules
COPY package.json tsconfig.json ./
COPY src ./src

# ビルド
RUN pnpm build

FROM base AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=8080

# 実行に必要なファイルのみをコピー
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./

EXPOSE 8080

# 起動コマンド
CMD ["node", "dist/index.js"]
