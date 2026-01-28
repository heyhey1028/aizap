/*
  Warnings:

  - The primary key for the `user_sessions` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - Added the required column `display_name` to the `user_sessions` table without a default value. This is not possible if the table is not empty.
  - Added the required column `goal` to the `user_sessions` table without a default value. This is not possible if the table is not empty.
  - The required column `id` was added to the `user_sessions` table with a prisma-level default value. This is not possible if the table is not empty. Please add this column as optional, then populate it before making it required.
  - Added the required column `secret_salt` to the `user_sessions` table without a default value. This is not possible if the table is not empty.
  - Added the required column `secret_value` to the `user_sessions` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "user_sessions" DROP CONSTRAINT "user_sessions_pkey",
ADD COLUMN     "display_name" TEXT NOT NULL,
ADD COLUMN     "goal" TEXT NOT NULL,
ADD COLUMN     "id" TEXT NOT NULL,
ADD COLUMN     "secret_salt" TEXT NOT NULL,
ADD COLUMN     "secret_value" TEXT NOT NULL,
ADD CONSTRAINT "user_sessions_pkey" PRIMARY KEY ("id");
