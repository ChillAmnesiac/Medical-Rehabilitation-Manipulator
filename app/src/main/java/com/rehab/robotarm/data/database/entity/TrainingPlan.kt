package com.rehab.robotarm.data.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "training_plans")
data class TrainingPlan(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val patientId: String,
    val name: String,
    val description: String,
    val totalWeeks: Int,
    val goals: String,              // JSON array
    val createdAt: Long = System.currentTimeMillis(),
    val isActive: Boolean = true
)

@Entity(tableName = "week_plans")
data class WeekPlan(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val planId: String,
    val weekNumber: Int,
    val frequency: Int,             // 每周次数
    val duration: Int,              // 每次时长(分钟)
    val exercises: String           // JSON array of Exercise
)

@Entity(tableName = "exercises")
data class Exercise(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val weekPlanId: String,
    val name: String,
    val targetAngle: Float,
    val repetitions: Int,
    val restTime: Int,              // 秒
    val difficulty: String,         // easy/medium/hard
    val instructions: String = ""
)
