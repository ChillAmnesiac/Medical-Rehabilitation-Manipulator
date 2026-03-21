package com.rehab.robotarm.data.database.dao

import androidx.room.*
import com.rehab.robotarm.data.database.entity.TrainingSession
import com.rehab.robotarm.data.database.entity.TrainingRecord
import kotlinx.coroutines.flow.Flow

@Dao
interface TrainingSessionDao {
    @Query("SELECT * FROM training_sessions WHERE patientId = :patientId ORDER BY startTime DESC")
    fun getSessionsByPatient(patientId: String): Flow<List<TrainingSession>>

    @Query("SELECT * FROM training_sessions WHERE id = :sessionId")
    suspend fun getSessionById(sessionId: String): TrainingSession?

    @Query("SELECT * FROM training_sessions WHERE patientId = :patientId AND startTime >= :startTime AND startTime <= :endTime")
    suspend fun getSessionsInRange(patientId: String, startTime: Long, endTime: Long): List<TrainingSession>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertSession(session: TrainingSession): Long

    @Update
    suspend fun updateSession(session: TrainingSession)

    @Delete
    suspend fun deleteSession(session: TrainingSession)

    @Query("SELECT * FROM training_sessions WHERE isSynced = 0")
    suspend fun getUnsyncedSessions(): List<TrainingSession>

    @Query("UPDATE training_sessions SET isSynced = 1 WHERE id = :sessionId")
    suspend fun markSynced(sessionId: String)

    @Query("SELECT AVG(overallScore) FROM training_sessions WHERE patientId = :patientId")
    suspend fun getAverageScore(patientId: String): Float?

    @Query("SELECT COUNT(*) FROM training_sessions WHERE patientId = :patientId")
    suspend fun getTotalSessionCount(patientId: String): Int
}

@Dao
interface TrainingRecordDao {
    @Query("SELECT * FROM training_records WHERE sessionId = :sessionId ORDER BY timestamp ASC")
    fun getRecordsBySession(sessionId: String): Flow<List<TrainingRecord>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRecord(record: TrainingRecord)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRecords(records: List<TrainingRecord>)

    @Query("DELETE FROM training_records WHERE sessionId = :sessionId")
    suspend fun deleteRecordsBySession(sessionId: String)
}
