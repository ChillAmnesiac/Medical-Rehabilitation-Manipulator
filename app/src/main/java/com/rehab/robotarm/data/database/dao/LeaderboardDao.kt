package com.rehab.robotarm.data.database.dao

import androidx.room.*
import com.rehab.robotarm.data.database.entity.LeaderboardEntry
import com.rehab.robotarm.data.database.entity.Achievement
import kotlinx.coroutines.flow.Flow

@Dao
interface LeaderboardDao {
    @Query("SELECT * FROM leaderboard_entries WHERE category = :category ORDER BY rank ASC LIMIT :limit")
    fun getLeaderboard(category: String, limit: Int): Flow<List<LeaderboardEntry>>

    @Query("SELECT * FROM leaderboard_entries WHERE userId = :userId AND category = :category")
    suspend fun getUserRank(userId: String, category: String): LeaderboardEntry?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertEntry(entry: LeaderboardEntry)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertEntries(entries: List<LeaderboardEntry>)

    @Query("DELETE FROM leaderboard_entries WHERE category = :category")
    suspend fun clearCategory(category: String)

    @Query("SELECT * FROM leaderboard_entries WHERE category = :category ORDER BY score DESC LIMIT 1")
    suspend fun getTopPlayer(category: String): LeaderboardEntry?
}

@Dao
interface AchievementDao {
    @Query("SELECT * FROM achievements WHERE userId = :userId ORDER BY unlockedAt DESC")
    fun getAchievementsByUser(userId: String): Flow<List<Achievement>>

    @Query("SELECT COUNT(*) FROM achievements WHERE userId = :userId")
    suspend fun getAchievementCount(userId: String): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAchievement(achievement: Achievement)

    @Query("SELECT * FROM achievements WHERE userId = :userId AND category = :category")
    fun getAchievementsByCategory(userId: String, category: String): Flow<List<Achievement>>
}
