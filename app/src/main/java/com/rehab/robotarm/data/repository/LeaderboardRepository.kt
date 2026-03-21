package com.rehab.robotarm.data.repository

import com.rehab.robotarm.data.database.dao.LeaderboardDao
import com.rehab.robotarm.data.database.dao.AchievementDao
import com.rehab.robotarm.data.database.entity.LeaderboardEntry
import com.rehab.robotarm.data.database.entity.Achievement
import kotlinx.coroutines.flow.Flow

class LeaderboardRepository(
    private val leaderboardDao: LeaderboardDao,
    private val achievementDao: AchievementDao
) {
    fun getLeaderboard(category: String, limit: Int = 100): Flow<List<LeaderboardEntry>> {
        return leaderboardDao.getLeaderboard(category, limit)
    }

    suspend fun getUserRank(userId: String, category: String): LeaderboardEntry? {
        return leaderboardDao.getUserRank(userId, category)
    }

    suspend fun uploadScore(entry: LeaderboardEntry) {
        leaderboardDao.insertEntry(entry)
    }

    suspend fun fetchLeaderboard(category: String, limit: Int): List<LeaderboardEntry> {
        // TODO: 从云端获取数据
        // 目前返回本地数据
        return emptyList()
    }

    suspend fun clearCategory(category: String) {
        leaderboardDao.clearCategory(category)
    }

    fun getAchievementsByUser(userId: String): Flow<List<Achievement>> {
        return achievementDao.getAchievementsByUser(userId)
    }

    suspend fun getAchievementCount(userId: String): Int {
        return achievementDao.getAchievementCount(userId)
    }

    suspend fun unlockAchievement(achievement: Achievement) {
        achievementDao.insertAchievement(achievement)
    }
}
