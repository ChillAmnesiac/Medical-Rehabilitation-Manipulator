package com.rehab.robotarm.data.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val username: String,
    val password: String,           // 加密存储
    val email: String,
    val phoneNumber: String? = null,
    val role: String,               // patient/doctor/therapist/family
    val avatarUrl: String? = null,
    val createdAt: Long = System.currentTimeMillis(),
    val lastLoginAt: Long = 0,
    val isActive: Boolean = true
)

@Entity(tableName = "user_profiles")
data class UserProfile(
    @PrimaryKey val userId: String,
    val displayName: String,
    val age: Int,
    val gender: String,
    val diagnosis: String? = null,         // 仅患者
    val hospitalId: String? = null,        // 所属医院
    val doctorId: String? = null,          // 主治医生
    val level: Int = 1,                    // 用户等级
    val experience: Int = 0,               // 经验值
    val totalTrainingSessions: Int = 0,
    val totalTrainingTime: Long = 0,
    val achievements: String = "[]"        // JSON数组
)
