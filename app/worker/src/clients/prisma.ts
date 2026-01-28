/**
 * Prisma クライアント
 *
 * 接続先は DATABASE_URL を使用する。
 */
import prismaModule from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { getDatabaseUrl } from '@/config/env.js';

// Prisma v7 では型定義上 PrismaClient が名前付きエクスポートとして見えないため、
// ランタイムのデフォルトエクスポートから安全に取得する。
// 型は InstanceType 経由で緩めに扱う。
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const { PrismaClient } = prismaModule as any;

type PrismaClientType = InstanceType<typeof PrismaClient>;

let prismaClient: PrismaClientType | null = null;

/**
 * Prisma クライアントを取得する。
 *
 * @returns Prisma クライアント
 */
export function getPrismaClient(): PrismaClientType {
  if (!prismaClient) {
    const adapter = new PrismaPg({ connectionString: getDatabaseUrl() });
    prismaClient = new PrismaClient({ adapter });
  }
  return prismaClient;
}
