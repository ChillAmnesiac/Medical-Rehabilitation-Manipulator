package com.rehab.robotarm.data.communication

import com.google.gson.Gson
import com.rehab.robotarm.data.model.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * 协议解析器
 * 负责解析从PSoC Edge E84设备接收的数据和构建发送命令
 */
class ProtocolParser {

    private val gson = Gson()

    private val _sensorData = MutableStateFlow(SensorData())
    val sensorData: StateFlow<SensorData> = _sensorData

    /**
     * 解析接收到的传感器数据
     * 支持两种格式：
     * 1. PSoC Edge格式: {"timestamp":123,"mode":"ACTIVE","shoulder_angle":45.5,...}
     * 2. 旧格式: {"type":"sensor","shoulder_angle":45.5,...}
     */
    fun parse(data: ByteArray): SensorData {
        return parseSensorData(data) ?: SensorData()
    }

    fun parseSensorData(data: ByteArray): SensorData? {
        return try {
            val jsonString = String(data)
            android.util.Log.d("ProtocolParser", "Parsing JSON: $jsonString")
            val dataMap = gson.fromJson(jsonString, Map::class.java)

            // 支持PSoC Edge格式（无type字段）或旧格式（有type字段）
            if (dataMap["type"] == "sensor" || dataMap.containsKey("shoulder_angle")) {
                val sensorData = SensorData(
                    timestamp = (dataMap["timestamp"] as? Double)?.toLong() ?: System.currentTimeMillis(),
                    // 角度传感器
                    shoulderAngle = (dataMap["shoulder_angle"] as? Double)?.toFloat() ?: 0f,
                    elbowAngle = (dataMap["elbow_angle"] as? Double)?.toFloat() ?: 0f,
                    wristAngle = (dataMap["wrist_angle"] as? Double)?.toFloat() ?: 0f,
                    lateralPosition = (dataMap["lateral_position"] as? Double)?.toFloat() ?: 0f,
                    // 扭矩传感器
                    shoulderTorque = (dataMap["shoulder_torque"] as? Double)?.toFloat() ?: 0f,
                    elbowTorque = (dataMap["elbow_torque"] as? Double)?.toFloat() ?: 0f,
                    wristTorque = (dataMap["wrist_torque"] as? Double)?.toFloat() ?: 0f,
                    // 力传感器
                    shoulderForce = (dataMap["shoulder_force"] as? Double)?.toFloat() ?: 0f,
                    elbowForce = (dataMap["elbow_force"] as? Double)?.toFloat() ?: 0f,
                    // EMG肌电传感器
                    emgCh1 = (dataMap["emg_ch1"] as? Double)?.toFloat() ?: 0f,
                    emgCh2 = (dataMap["emg_ch2"] as? Double)?.toFloat() ?: 0f,
                    // 六轴IMU传感器（MPU6050）
                    imuAccelX = (dataMap["imu_accel_x"] as? Double)?.toFloat() ?: 0f,
                    imuAccelY = (dataMap["imu_accel_y"] as? Double)?.toFloat() ?: 0f,
                    imuAccelZ = (dataMap["imu_accel_z"] as? Double)?.toFloat() ?: 0f,
                    imuGyroX = (dataMap["imu_gyro_x"] as? Double)?.toFloat() ?: 0f,
                    imuGyroY = (dataMap["imu_gyro_y"] as? Double)?.toFloat() ?: 0f,
                    imuGyroZ = (dataMap["imu_gyro_z"] as? Double)?.toFloat() ?: 0f,
                    // 关节加速度传感器（兼容）
                    shoulderAccelX = (dataMap["shoulder_accel_x"] as? Double)?.toFloat() ?: 0f,
                    shoulderAccelY = (dataMap["shoulder_accel_y"] as? Double)?.toFloat() ?: 0f,
                    shoulderAccelZ = (dataMap["shoulder_accel_z"] as? Double)?.toFloat() ?: 0f,
                    elbowAccelX = (dataMap["elbow_accel_x"] as? Double)?.toFloat() ?: 0f,
                    elbowAccelY = (dataMap["elbow_accel_y"] as? Double)?.toFloat() ?: 0f,
                    elbowAccelZ = (dataMap["elbow_accel_z"] as? Double)?.toFloat() ?: 0f,
                    // 生理传感器（MAX30102）
                    heartRate = (dataMap["heart_rate"] as? Double)?.toInt() ?: 0,
                    spo2 = (dataMap["spo2"] as? Double)?.toInt() ?: 0,
                    // 温度传感器
                    temperature = (dataMap["temperature"] as? Double)?.toFloat() ?: 25f,
                    shoulderTemp = (dataMap["shoulder_temp"] as? Double)?.toFloat() ?: 25f,
                    elbowTemp = (dataMap["elbow_temp"] as? Double)?.toFloat() ?: 25f,
                    lateralTemp = (dataMap["lateral_temp"] as? Double)?.toFloat() ?: 25f
                )
                android.util.Log.d("ProtocolParser", "Parsed sensor data: shoulder=${sensorData.shoulderAngle}, elbow=${sensorData.elbowAngle}")
                _sensorData.value = sensorData
                sensorData
            } else {
                android.util.Log.w("ProtocolParser", "Data format not recognized")
                null
            }
        } catch (e: Exception) {
            android.util.Log.e("ProtocolParser", "Parse error: ${e.message}", e)
            e.printStackTrace()
            null
        }
    }

    /**
     * 构建模式切换命令（适配PSoC Edge E84的6种模式）
     */
    fun buildModeCommand(mode: RobotMode): ByteArray {
        val command = mapOf(
            "mode" to when(mode) {
                RobotMode.ACTIVE -> "ACTIVE"
                RobotMode.PASSIVE -> "PASSIVE"
                RobotMode.ASSIST -> "ASSIST"
                RobotMode.RESIST -> "RESIST"
                RobotMode.MEMORY -> "MEMORY"
                RobotMode.GAME -> "GAME"
            }
        )
        android.util.Log.d("ProtocolParser", "Building mode command: ${gson.toJson(command)}")
        return gson.toJson(command).toByteArray()
    }

    /**
     * 构建控制命令（被动模式）
     */
    fun buildControlCommand(command: ControlCommand): ByteArray {
        val cmdMap = mutableMapOf<String, Any>(
            "type" to "control"
        )

        command.shoulderAngle?.let { cmdMap["shoulder_angle"] = it }
        command.elbowAngle?.let { cmdMap["elbow_angle"] = it }
        command.lateralPosition?.let { cmdMap["lateral_pos"] = it }

        return gson.toJson(cmdMap).toByteArray()
    }

    /**
     * 构建记忆动作命令
     */
    fun buildMemoryCommand(action: MemoryAction): ByteArray {
        val command = mapOf(
            "type" to "memory",
            "action_id" to action.id,
            "keyframes" to action.keyframes.map { keyframe ->
                mapOf(
                    "time" to keyframe.timestamp,
                    "shoulder" to keyframe.shoulderAngle,
                    "elbow" to keyframe.elbowAngle,
                    "lateral" to keyframe.lateralPosition
                )
            }
        )
        return gson.toJson(command).toByteArray()
    }

    /**
     * 构建执行记忆动作命令
     */
    fun buildExecuteMemoryCommand(actionId: String): ByteArray {
        val command = mapOf(
            "type" to "execute_memory",
            "action_id" to actionId
        )
        return gson.toJson(command).toByteArray()
    }
}
