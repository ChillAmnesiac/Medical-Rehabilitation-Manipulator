package com.rehab.robotarm.data.database.entity

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(
    tableName = "rehab_assessments",
    foreignKeys = [
        ForeignKey(
            entity = TrainingSession::class,
            parentColumns = ["id"],
            childColumns = ["sessionId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("sessionId")]
)
data class RehabAssessment(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val sessionId: String,
    val smoothness: Float,           // 平滑度评分 (0-100)
    val rangeOfMotion: Float,        // 运动范围评分 (0-100)
    val strength: Float,             // 力量评分 (0-100)
    val overallScore: Float,         // 综合评分 (0-100)
    val recommendation: String,      // AI建议
    val cloudRecommendation: String? = null,  // 云端AI建议
    val timestamp: Long = System.currentTimeMillis()
)
