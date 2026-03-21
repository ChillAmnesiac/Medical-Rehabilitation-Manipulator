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

    // 关节角度数据
    val shoulderAngle: Float,
    val elbowAngle: Float,
    val wristAngle: Float = 0f,
    val lateralPosition: Float,

    // 扭矩/力传感器数据
    val shoulderTorque: Float = 0f,
    val elbowTorque: Float = 0f,
    val wristTorque: Float = 0f,
    val shoulderForce: Float = 0f,
    val elbowForce: Float = 0f,

    // EMG肌电信号
    val emgCh1: Float,
    val emgCh2: Float,

    // 六轴IMU数据
    val imuAccelX: Float = 0f,
    val imuAccelY: Float = 0f,
    val imuAccelZ: Float = 0f,
    val imuGyroX: Float = 0f,
    val imuGyroY: Float = 0f,
    val imuGyroZ: Float = 0f,

    // 生理传感器数据
    val heartRate: Int,
    val spo2: Int = 0,

    // 温度传感器数据
    val shoulderTemp: Float = 0f,
    val elbowTemp: Float = 0f,
    val lateralTemp: Float = 0f
)
