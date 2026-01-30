-- CreateTable
CREATE TABLE "exercise_logs" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "exercise_name" TEXT NOT NULL,
    "sets" JSONB NOT NULL,
    "category" TEXT,
    "muscle_group" TEXT,
    "total_sets" INTEGER NOT NULL,
    "total_reps" INTEGER,
    "total_duration" INTEGER,
    "total_distance" DOUBLE PRECISION,
    "total_volume" DOUBLE PRECISION,
    "note" TEXT,
    "recorded_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "exercise_logs_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "exercise_logs_user_id_recorded_at_idx" ON "exercise_logs"("user_id", "recorded_at" DESC);

-- CreateIndex
CREATE INDEX "exercise_logs_user_id_exercise_name_recorded_at_idx" ON "exercise_logs"("user_id", "exercise_name", "recorded_at" DESC);

-- AddForeignKey
ALTER TABLE "exercise_logs" ADD CONSTRAINT "exercise_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "user_sessions"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;
