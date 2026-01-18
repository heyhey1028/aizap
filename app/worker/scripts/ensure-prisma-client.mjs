import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const clientPackageJsonPath = require.resolve('@prisma/client/package.json');
const clientDirLink = path.dirname(clientPackageJsonPath);
const clientDirReal = path.dirname(fs.realpathSync(clientPackageJsonPath));
const scopeDir = path.dirname(clientDirReal);
const nodeModulesDir = path.basename(scopeDir).startsWith('@')
  ? path.dirname(scopeDir)
  : scopeDir;
const prismaDir = path.join(nodeModulesDir, '.prisma');
const linkPath = path.join(clientDirLink, '.prisma');

if (!fs.existsSync(prismaDir)) {
  throw new Error('Prisma クライアントの生成結果が見つかりません。');
}

if (!fs.existsSync(linkPath)) {
  fs.symlinkSync(prismaDir, linkPath, 'dir');
}
