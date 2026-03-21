package com.rehab.robotarm.data.database.dao

import androidx.room.*
import com.rehab.robotarm.data.database.entity.RehabAssessment
import kotlinx.coroutines.flow.Flow

@Dao
interface RehabAssessmentDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(assessment: RehabAssessment)

    @Query("SELECT * FROM rehab_assessments WHERE sessionId = :sessionId")
    suspend fun getBySession(sessionId: String): RehabAssessment?

    @Query("SELECT * FROM rehab_assessments WHERE sessionId = :sessionId")
    fun getBySessionFlow(sessionId: String): Flow<RehabAssessment?>

    @Query("SELECT * FROM rehab_assessments ORDER BY timestamp DESC LIMIT :limit")
    fun getRecentAssessments(limit: Int = 10): Flow<List<RehabAssessment>>

    @Query("SELECT * FROM rehab_assessments ORDER BY timestamp DESC")
    fun getAllAssessments(): Flow<List<RehabAssessment>>

    @Query("SELECT AVG(overallScore) FROM rehab_assessments WHERE timestamp >= :startTime")
    suspend fun getAverageScore(startTime: Long): Float?

    @Delete
    suspend fun delete(assessment: RehabAssessment)

    @Query("DELETE FROM rehab_assessments WHERE sessionId = :sessionId")
    suspend fun deleteBySession(sessionId: String)
}
