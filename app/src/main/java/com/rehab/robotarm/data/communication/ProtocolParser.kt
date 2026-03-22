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
     * 新格式（实际硬件）:
     * {
     *   "emg": 123.4,           // EMG肌电信号（单通道）
     *   "hr": 75,               // 心率
     *   "imu_ax": 0.5,          // IMU角度X（横向张开角度）
     *   "imu_ay": 0.2,          // IMU角度Y
     *   "imu_az": 0.1,          // IMU角度Z
     *   "imu_gx": 1.2,          // IMU加速度X
     *   "imu_gy": 0.8,          // IMU加速度Y
     *   "imu_gz": 9.8,          // IMU加速度Z
     *   "m1_angle": 45.5,       // 电机1角度（肩关节）
     *   "m1_damping": 0.5,      // 电机1阻尼
     *   "m1_temp": 28.5,        // 电机1温度
     *   "m2_angle": 90.2,       // 电机2角度（肘关节）
     *   "m2_damping": 0.3,      // 电机2阻尼
     *   "m2_temp": 27.8         // 电机2温度
     * }
     *
     * 兼容旧格式（M33 ASCII）: {"s":1,"m":0,"sh":45.5,"el":30.2,...}
     */
    fun parseSensorData(data: ByteArray): SensorData? {
        return try {
            val jsonString = String(data).trim()
            android.util.Log.d("ProtocolParser", "Parsing JSON: $jsonString")
            val dataMap = gson.fromJson(jsonString, Map::class.java)

            // 安全地提取数值，处理可能的格式错误
            fun safeGetFloat(key: String): Float {
                return when (val value = dataMap[key]) {
                    is Double -> value.toFloat()
                    is Int -> value.toFloat()
                    is Long -> value.toFloat()
                    is String -> value.toFloatOrNull() ?: 0f
                    else -> 0f
                }
            }

            fun safeGetInt(key: String): Int {
                return when (val value = dataMap[key]) {
                    is Double -> value.toInt()
                    is Int -> value
                    is Long -> value.toInt()
                    is String -> value.toIntOrNull() ?: 0
                    else -> 0
                }
            }

            val sensorData = when {
                // 新格式：包含 emg, hr, imu_ax 等字段
                dataMap.containsKey("emg") || dataMap.containsKey("m1_angle") -> {
                    SensorData(
                        timestamp = System.currentTimeMillis(),
                        // EMG肌电传感器
                        emgCh1 = safeGetFloat("emg"),
                        // 心率传感器
                        heartRate = safeGetInt("hr").coerceIn(0, 200),
                        // IMU传感器 - 3轴角度
                        imuAngleX = safeGetFloat("imu_ax"),
                        imuAngleY = safeGetFloat("imu_ay"),
                        imuAngleZ = safeGetFloat("imu_az"),
                        // IMU传感器 - 3轴加速度
                        imuAccelX = safeGetFloat("imu_gx"),
                        imuAccelY = safeGetFloat("imu_gy"),
                        imuAccelZ = safeGetFloat("imu_gz"),
                        // 电机1（肩关节）
                        motor1Angle = safeGetFloat("m1_angle"),
                        motor1Damping = safeGetFloat("m1_damping"),
                        motor1Temp = safeGetFloat("m1_temp"),
                        // 电机2（肘关节）
                        motor2Angle = safeGetFloat("m2_angle"),
                        motor2Damping = safeGetFloat("m2_damping"),
                        motor2Temp = safeGetFloat("m2_temp")
                    )
                }
                // M33 ASCII格式（兼容）: {"s":1,"m":0,"sh":45.5,"el":30.2,...}
                dataMap.containsKey("sh") -> {
                    SensorData(
                        timestamp = System.currentTimeMillis(),
                        emgCh1 = safeGetFloat("e1"),
                        heartRate = safeGetInt("hr").coerceIn(0, 200),
                        motor1Angle = safeGetFloat("sh"),
                        motor2Angle = safeGetFloat("el"),
                        imuAngleX = safeGetFloat("la")
                    )
                }
                // PSoC Edge格式或旧格式（兼容）
                dataMap["type"] == "sensor" || dataMap.containsKey("shoulder_angle") -> {
                    SensorData(
                        timestamp = (dataMap["timestamp"] as? Double)?.toLong() ?: System.currentTimeMillis(),
                        motor1Angle = (dataMap["shoulder_angle"] as? Double)?.toFloat() ?: 0f,
                        motor2Angle = (dataMap["elbow_angle"] as? Double)?.toFloat() ?: 0f,
                        imuAngleX = (dataMap["lateral_position"] as? Double)?.toFloat() ?: 0f,
                        motor1Damping = (dataMap["shoulder_torque"] as? Double)?.toFloat() ?: 0f,
                        motor2Damping = (dataMap["elbow_torque"] as? Double)?.toFloat() ?: 0f,
                        emgCh1 = (dataMap["emg_ch1"] as? Double)?.toFloat() ?: 0f,
                        imuAccelX = (dataMap["imu_accel_x"] as? Double)?.toFloat() ?: 0f,
                        imuAccelY = (dataMap["imu_accel_y"] as? Double)?.toFloat() ?: 0f,
                        imuAccelZ = (dataMap["imu_accel_z"] as? Double)?.toFloat() ?: 0f,
                        heartRate = (dataMap["heart_rate"] as? Double)?.toInt() ?: 0,
                        motor1Temp = (dataMap["shoulder_temp"] as? Double)?.toFloat() ?: 25f,
                        motor2Temp = (dataMap["elbow_temp"] as? Double)?.toFloat() ?: 25f
                    )
                }
                else -> {
                    android.util.Log.w("ProtocolParser", "Data format not recognized")
                    return null
                }
            }

            android.util.Log.d("ProtocolParser", "Parsed sensor data: m1_angle=${sensorData.motor1Angle}, m2_angle=${sensorData.motor2Angle}, emg=${sensorData.emgCh1}")
            _sensorData.value = sensorData
            sensorData
        } catch (e: Exception) {
            android.util.Log.e("ProtocolParser", "Parse error: ${e.message}", e)
            e.printStackTrace()
            null
        }
    }

    /**
     * 构建模式切换命令（适配M33的ASCII文本协议）
     * M33格式: mode:passive\n, mode:active\n, mode:memory\n, mode:ai_assist\n
     */
    fun buildModeCommand(mode: RobotMode): ByteArray {
        val modeStr = when(mode) {
            RobotMode.ACTIVE -> "active"
            RobotMode.PASSIVE -> "passive"
            RobotMode.ASSIST -> "ai_assist"
            RobotMode.RESIST -> "passive"  // M33暂不支持阻力模式，映射到被动模式
            RobotMode.MEMORY -> "memory"
            RobotMode.GAME -> "passive"    // M33暂不支持游戏模式，映射到被动模式
        }
        val command = "mode:$modeStr\n"
        android.util.Log.d("ProtocolParser", "Building mode command: $command")
        return command.toByteArray()
    }

    /**
     * 构建关节移动命令（M33 ASCII格式）
     * M33格式: move:<关节ID>:<目标角度>\n
     * 关节ID: 0=肩关节纵向, 1=肘关节纵向, 2=肩关节横向
     */
    fun buildControlCommand(command: ControlCommand): ByteArray {
        val commands = mutableListOf<String>()

        command.shoulderAngle?.let {
            commands.add("move:0:$it\n")
        }
        command.elbowAngle?.let {
            commands.add("move:1:$it\n")
        }
        command.lateralPosition?.let {
            commands.add("move:2:$it\n")
        }

        val fullCommand = commands.joinToString("")
        android.util.Log.d("ProtocolParser", "Building control command: $fullCommand")
        return fullCommand.toByteArray()
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

    /**
     * 构建启动数据流命令（M33 ASCII格式）
     */
    fun buildStartStreamCommand(): ByteArray {
        return "stream:on\n".toByteArray()
    }

    /**
     * 构建停止数据流命令（M33 ASCII格式）
     */
    fun buildStopStreamCommand(): ByteArray {
        return "stream:off\n".toByteArray()
    }

    /**
     * 构建紧急停止命令（M33 ASCII格式）
     */
    fun buildEmergencyStopCommand(): ByteArray {
        return "stop\n".toByteArray()
    }

    /**
     * 构建心跳命令（M33 ASCII格式）
     */
    fun buildHeartbeatCommand(): ByteArray {
        return "heartbeat\n".toByteArray()
    }
}
