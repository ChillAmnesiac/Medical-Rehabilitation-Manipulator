package com.rehab.robotarm.data.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.UUID

@Entity(tableName = "patients")
data class Patient(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val name: String,
    val age: Int,
    val gender: String,
    val diagnosis: String,
    val affectedSide: String = "左侧",        // 患侧（左/右）
    val admissionDate: Long,
    val doctorId: String,
    val phoneNumber: String = "",
    val notes: String = "",
    val currentROM: Float = 0f,           // Range of Motion
    val strengthLevel: Int = 0,           // 0-10
    val latestScore: Float = 0f,
    val isActive: Boolean = true,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
