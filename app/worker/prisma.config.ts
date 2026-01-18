import { defineConfig } from 'prisma/config';

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    path: 'prisma/migrations',
  },
  datasource: {
    // prisma generate は DB 接続不要なため、ビルド時は未設定でも動作させる。
    // migrate dev / deploy は DATABASE_URL が必須（未設定だと失敗する）。
    url: process.env.DATABASE_URL ?? '',
  },
});
