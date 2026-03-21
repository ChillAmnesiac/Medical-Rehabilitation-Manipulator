package com.rehab.robotarm.data.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "training_sessions")
data class TrainingSession(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val patientId: String,
    val startTime: Long,
    val endTime: Long = 0,
    val duration: Long = 0,              // 秒
    val mode: String,                    // passive/active/assist/resist/memory/game
    val maxShoulderAngle: Float = 0f,
    val maxElbowAngle: Float = 0f,
    val maxAngle: Float = 0f,            // 最大关节角度（兼容字段）
    val minAngle: Float = 0f,            // 最小关节角度
    val targetAngle: Float = 0f,         // 目标角度
    val avgHeartRate: Int? = null,
    val maxHeartRate: Int = 0,
    val avgEmg: Float = 0f,
    val avgEmgCh1: Float = 0f,
    val avgEmgCh2: Float = 0f,
    val repetitions: Int = 0,
    val overallScore: Float = 0f,        // 0-100
    val painLevel: Int = 0,              // 0-10
    val fatigueLevel: Int = 0,           // 0-10
    val notes: String = "",
    val isSynced: Boolean = false
)

@Entity(tableName = "training_records")
data class TrainingRecord(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val sessionId: String,
    val timestamp: Long,
    val shoulderAngle: Float,
    val elbowAngle: Float,
    val wristAngle: Float,
    val emgCh1: Float,
    val emgCh2: Float,
    val heartRate: Int,
    val spo2: Int,
    val torqueX: Float,
    val torqueY: Float,
    val torqueZ: Float
)
