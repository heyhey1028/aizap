/**
 * Prisma クライアント
 *
 * 接続先は DATABASE_URL を使用する。
 */
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { getDatabaseUrl } from '@/config/env.js';

let prismaClient: PrismaClient | null = null;

/**
 * Prisma クライアントを取得する。
 *
 * @returns Prisma クライアント
 */
export function getPrismaClient(): PrismaClient {
  if (!prismaClient) {
    const adapter = new PrismaPg({ connectionString: getDatabaseUrl() });
    prismaClient = new PrismaClient({ adapter });
  }
  return prismaClient;
}
