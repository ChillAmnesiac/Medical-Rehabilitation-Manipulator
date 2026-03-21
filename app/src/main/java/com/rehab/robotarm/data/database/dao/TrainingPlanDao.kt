package com.rehab.robotarm.data.database.dao

import androidx.room.*
import com.rehab.robotarm.data.database.entity.TrainingPlan
import com.rehab.robotarm.data.database.entity.WeekPlan
import com.rehab.robotarm.data.database.entity.Exercise
import kotlinx.coroutines.flow.Flow

@Dao
interface TrainingPlanDao {
    @Query("SELECT * FROM training_plans WHERE patientId = :patientId AND isActive = 1")
    fun getActivePlan(patientId: String): Flow<TrainingPlan?>

    @Query("SELECT * FROM training_plans WHERE id = :planId")
    suspend fun getPlanById(planId: String): TrainingPlan?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPlan(plan: TrainingPlan)

    @Update
    suspend fun updatePlan(plan: TrainingPlan)

    @Query("UPDATE training_plans SET isActive = 0 WHERE patientId = :patientId")
    suspend fun deactivateAllPlans(patientId: String)

    @Query("SELECT * FROM week_plans WHERE planId = :planId ORDER BY weekNumber ASC")
    fun getWeekPlans(planId: String): Flow<List<WeekPlan>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertWeekPlan(weekPlan: WeekPlan)

    @Query("SELECT * FROM exercises WHERE weekPlanId = :weekPlanId")
    fun getExercises(weekPlanId: String): Flow<List<Exercise>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExercise(exercise: Exercise)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertExercises(exercises: List<Exercise>)
}
