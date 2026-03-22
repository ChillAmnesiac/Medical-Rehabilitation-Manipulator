package com.rehab.robotarm.data.database.entity

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "sensor_records",
    foreignKeys = [
        ForeignKey(
            entity = TrainingSession::class,
            parentColumns = ["id"],
            childColumns = ["sessionId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("sessionId"), Index("timestamp")]
)
data class SensorRecord(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val sessionId: String,
    val timestamp: Long = System.currentTimeMillis(),

    // EMG肌电传感器（单通道）
    val emgCh1: Float,

    // 心率传感器
    val heartRate: Int,

    // IMU传感器（肩膀处）- 3轴角度
    val imuAngleX: Float,
    val imuAngleY: Float,
    val imuAngleZ: Float,

    // IMU传感器（肩膀处）- 3轴加速度
    val imuAccelX: Float,
    val imuAccelY: Float,
    val imuAccelZ: Float,

    // 伺服电机1（肩关节 - 纵向运动）
    val motor1Angle: Float,
    val motor1Damping: Float,
    val motor1Temp: Float,

    // 伺服电机2（肘关节 - 纵向运动）
    val motor2Angle: Float,
    val motor2Damping: Float,
    val motor2Temp: Float
)
