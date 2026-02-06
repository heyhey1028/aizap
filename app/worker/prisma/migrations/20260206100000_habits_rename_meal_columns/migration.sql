-- AlterTable: habits の食事関連カラム名を Prisma スキーマに合わせる
-- 初期マイグレーションで作成された target_protein_g, target_carbs_g, target_fat_g を
-- target_proteins, target_carbohydrates, target_fats にリネームし、型を INTEGER に統一

ALTER TABLE "habits" RENAME COLUMN "target_protein_g" TO "target_proteins";
ALTER TABLE "habits" ALTER COLUMN "target_proteins" TYPE INTEGER USING ROUND("target_proteins")::INTEGER;

ALTER TABLE "habits" RENAME COLUMN "target_carbs_g" TO "target_carbohydrates";
ALTER TABLE "habits" ALTER COLUMN "target_carbohydrates" TYPE INTEGER USING ROUND("target_carbohydrates")::INTEGER;

ALTER TABLE "habits" RENAME COLUMN "target_fat_g" TO "target_fats";
ALTER TABLE "habits" ALTER COLUMN "target_fats" TYPE INTEGER USING ROUND("target_fats")::INTEGER;
