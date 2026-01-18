FROM node:22-slim AS base

# pnpm をインストール
RUN corepack enable && corepack prepare pnpm@latest --activate

FROM base AS deps

WORKDIR /app

# 依存関係ファイルをコピー
COPY package.json pnpm-lock.yaml* ./

# 依存関係をインストール
RUN PRISMA_GENERATE_SKIP_POSTINSTALL=1 pnpm install --frozen-lockfile

FROM base AS builder

WORKDIR /app

# 依存関係をコピー
COPY --from=deps /app/node_modules ./node_modules
COPY package.json tsconfig.json prisma.config.ts ./
COPY prisma ./prisma
COPY scripts ./scripts
COPY src ./src

# Prisma クライアントを生成（DATABASE_URL は必須）
RUN DATABASE_URL="postgresql://postgres:postgres@localhost:5432/aizap?schema=public" pnpm prisma:generate

# ビルド
RUN pnpm build

FROM base AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=8080

# 実行に必要なファイルのみをコピー
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/prisma.config.ts ./prisma.config.ts
COPY package.json ./

EXPOSE 8080

# 起動コマンド
CMD ["node", "dist/index.js"]
