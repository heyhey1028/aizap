-- CreateTable
CREATE TABLE "habits" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "goal_id" TEXT,
    "habit_type" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "description" TEXT,
    "routine_id" TEXT,
    "routine_name" TEXT,
    "order_in_routine" INTEGER,
    "exercise_name" TEXT,
    "category" TEXT,
    "muscle_group" TEXT,
    "target_sets" INTEGER,
    "target_reps" INTEGER,
    "target_duration" INTEGER,
    "target_distance" DOUBLE PRECISION,
    "target_weight" DOUBLE PRECISION,
    "meal_type" TEXT,
    "target_calories" INTEGER,
    "target_protein_g" DOUBLE PRECISION,
    "target_carbs_g" DOUBLE PRECISION,
    "target_fat_g" DOUBLE PRECISION,
    "meal_guidelines" TEXT,
    "frequency" TEXT NOT NULL,
    "days_of_week" JSONB,
    "time_of_day" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "start_date" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "end_date" TIMESTAMP(3),
    "notes" TEXT,
    "priority" INTEGER,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "habits_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "habits_user_id_habit_type_is_active_idx" ON "habits"("user_id", "habit_type", "is_active");

-- CreateIndex
CREATE INDEX "habits_user_id_routine_id_idx" ON "habits"("user_id", "routine_id");

-- CreateIndex
CREATE INDEX "habits_user_id_start_date_idx" ON "habits"("user_id", "start_date");

-- CreateIndex
CREATE INDEX "habits_goal_id_idx" ON "habits"("goal_id");

-- AddForeignKey
ALTER TABLE "habits" ADD CONSTRAINT "habits_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "user_sessions"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "habits" ADD CONSTRAINT "habits_goal_id_fkey" FOREIGN KEY ("goal_id") REFERENCES "goals"("id") ON DELETE SET NULL ON UPDATE CASCADE;
