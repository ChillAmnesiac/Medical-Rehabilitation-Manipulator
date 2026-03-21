package com.rehab.robotarm.data.database.dao

import androidx.room.*
import com.rehab.robotarm.data.database.entity.SensorRecord
import kotlinx.coroutines.flow.Flow

@Dao
interface SensorRecordDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(record: SensorRecord): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(records: List<SensorRecord>)

    @Query("SELECT * FROM sensor_records WHERE sessionId = :sessionId ORDER BY timestamp ASC")
    fun getRecordsBySession(sessionId: String): Flow<List<SensorRecord>>

    @Query("SELECT * FROM sensor_records WHERE sessionId = :sessionId ORDER BY timestamp ASC")
    suspend fun getRecordsBySessionSync(sessionId: String): List<SensorRecord>

    @Query("SELECT * FROM sensor_records WHERE sessionId = :sessionId ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getRecentRecords(sessionId: String, limit: Int = 100): List<SensorRecord>

    @Query("DELETE FROM sensor_records WHERE sessionId = :sessionId")
    suspend fun deleteBySession(sessionId: String)

    @Query("DELETE FROM sensor_records WHERE timestamp < :timestamp")
    suspend fun deleteOldRecords(timestamp: Long)

    @Query("SELECT COUNT(*) FROM sensor_records WHERE sessionId = :sessionId")
    suspend fun getRecordCount(sessionId: String): Int
}
