-- CreateTable
CREATE TABLE "diet_logs" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "meal_type" TEXT NOT NULL,
    "calories" DOUBLE PRECISION NOT NULL,
    "proteins" DOUBLE PRECISION NOT NULL,
    "fats" DOUBLE PRECISION NOT NULL,
    "carbohydrates" DOUBLE PRECISION NOT NULL,
    "sodium" DOUBLE PRECISION,
    "fiber" DOUBLE PRECISION,
    "sugar" DOUBLE PRECISION,
    "estimation_source" TEXT NOT NULL,
    "is_user_corrected" BOOLEAN NOT NULL DEFAULT false,
    "image_url" TEXT,
    "note" TEXT,
    "recorded_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "diet_logs_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "diet_logs_user_id_recorded_at_idx" ON "diet_logs"("user_id", "recorded_at" DESC);

-- CreateIndex
CREATE INDEX "diet_logs_user_id_meal_type_recorded_at_idx" ON "diet_logs"("user_id", "meal_type", "recorded_at" DESC);

-- AddForeignKey
ALTER TABLE "diet_logs" ADD CONSTRAINT "diet_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "user_sessions"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;
