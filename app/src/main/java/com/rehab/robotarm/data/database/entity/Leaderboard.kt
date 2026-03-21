package com.rehab.robotarm.data.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "leaderboard_entries")
data class LeaderboardEntry(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val username: String,
    val avatarUrl: String? = null,
    val score: Int,                 // 综合分数
    val level: Int,                 // 等级
    val totalSessions: Int,         // 总训练次数
    val totalDuration: Long,        // 总时长(秒)
    val maxAngle: Float,            // 最大角度
    val bestGameScore: Int,         // 最高游戏分数
    val achievements: Int,          // 成就数量
    val rank: Int,                  // 排名
    val category: String,           // global/weekly/monthly/friends
    val timestamp: Long = System.currentTimeMillis()
)

@Entity(tableName = "achievements")
data class Achievement(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val name: String,
    val description: String,
    val iconUrl: String? = null,
    val unlockedAt: Long,
    val category: String,           // training/social/milestone
    val points: Int = 0
)
