package com.rehab.robotarm.data.model

/**
 * 主模式（三种）
 */
enum class MainMode {
    ACTIVE,      // 主动模式：患者主导运动
    PASSIVE,     // 被动模式：系统主导运动
    MEMORY       // 记忆模式：执行预设动作
}

/**
 * 主动模式子模式
 */
enum class ActiveSubMode {
    STANDARD,    // 标准主动模式
    AI_ASSIST,   // AI助力模式
    GAME         // 游戏化训练模式
}

/**
 * 被动模式子模式
 */
enum class PassiveSubMode {
    MANUAL,      // 手动控制模式
    AUTO_TRAIN,  // 自动训练模式
    REMOTE       // 远程控制模式
}

/**
 * 记忆模式子模式
 */
enum class MemorySubMode {
    REPLAY,      // 动作回放模式
    PLAN,        // 训练计划模式
    ASSESSMENT   // 评估测试模式
}

/**
 * 游戏类型
 */
enum class GameType {
    FRUIT_NINJA,     // 水果忍者：移动手臂"切"目标
    WHACK_A_MOLE,    // 打地鼠：快速移动到目标位置
    RHYTHM_MASTER,   // 节奏大师：跟随音乐节奏运动
    FLIGHT_SIM       // 飞行模拟：控制飞机飞行
}

/**
 * 机械臂运动模式（兼容旧代码）
 */
enum class RobotMode {
    ACTIVE,      // 主动模式：患者主动运动
    PASSIVE,     // 被动模式：机械臂带动患者
    ASSIST,      // 助力模式：根据EMG提供辅助
    RESIST,      // 阻力模式：提供可调阻力
    MEMORY,      // 记忆模式：重复学习的轨迹
    GAME         // 游戏模式：互动训练
}

/**
 * 关节类型
 */
enum class JointType {
    SHOULDER,    // 肩关节
    ELBOW,       // 肘关节
    LATERAL      // 推杆电机（横向张开）
}

/**
 * 传感器数据
 * 实际硬件配置：
 * - 1个EMG肌电传感器（单通道）
 * - 1个心率传感器
 * - 1个IMU（肩膀处）：3轴角度 + 3轴加速度
 * - 2个伺服电机：角度1、角度2、阻尼1、阻尼2、温度1、温度2
 * - 电机1：肩关节（纵向运动）
 * - 电机2：肘关节（纵向运动）
 * - 推杆电机：横向张开（无角度测量，通过IMU获取）
 */
data class SensorData(
    val timestamp: Long = System.currentTimeMillis(),

    // EMG肌电传感器（单通道）
    val emgCh1: Float = 0f,                  // EMG肌电信号

    // 心率传感器
    val heartRate: Int = 0,                  // 心率（bpm）

    // IMU传感器（肩膀处）- 3轴角度
    val imuAngleX: Float = 0f,               // IMU角度X（横向张开角度）
    val imuAngleY: Float = 0f,               // IMU角度Y
    val imuAngleZ: Float = 0f,               // IMU角度Z

    // IMU传感器（肩膀处）- 3轴加速度
    val imuAccelX: Float = 0f,               // IMU加速度X
    val imuAccelY: Float = 0f,               // IMU加速度Y
    val imuAccelZ: Float = 0f,               // IMU加速度Z

    // 伺服电机1（肩关节 - 纵向运动）
    val motor1Angle: Float = 0f,             // 电机1角度（肩关节角度）
    val motor1Damping: Float = 0f,           // 电机1阻尼
    val motor1Temp: Float = 25f,             // 电机1温度

    // 伺服电机2（肘关节 - 纵向运动）
    val motor2Angle: Float = 0f,             // 电机2角度（肘关节角度）
    val motor2Damping: Float = 0f,           // 电机2阻尼
    val motor2Temp: Float = 25f,             // 电机2温度

    // 兼容字段（映射到实际传感器）
    val shoulderAngle: Float = motor1Angle,  // 肩关节角度 = 电机1角度
    val elbowAngle: Float = motor2Angle,     // 肘关节角度 = 电机2角度
    val lateralPosition: Float = imuAngleX,  // 横向位置 = IMU角度X
    val shoulderTemp: Float = motor1Temp,    // 肩关节温度 = 电机1温度
    val elbowTemp: Float = motor2Temp,       // 肘关节温度 = 电机2温度

    // 保留字段（未使用）
    val emgCh2: Float = 0f,                  // EMG通道2（未使用）
    val spo2: Int = 0,                       // 血氧（未使用）
    val shoulderAccelX: Float = imuAccelX,   // 肩关节加速度X = IMU加速度X
    val shoulderAccelY: Float = imuAccelY,   // 肩关节加速度Y = IMU加速度Y
    val shoulderAccelZ: Float = imuAccelZ,   // 肩关节加速度Z = IMU加速度Z
    val elbowAccelX: Float = 0f,             // 肘关节加速度X（未使用）
    val elbowAccelY: Float = 0f,             // 肘关节加速度Y（未使用）
    val elbowAccelZ: Float = 0f,             // 肘关节加速度Z（未使用）
    val shoulderTorque: Float = motor1Damping, // 肩关节扭矩 = 电机1阻尼
    val elbowTorque: Float = motor2Damping,    // 肘关节扭矩 = 电机2阻尼
    val shoulderForce: Float = 0f,           // 肩关节力（未使用）
    val elbowForce: Float = 0f,              // 肘关节力（未使用）
    val temperature: Float = (motor1Temp + motor2Temp) / 2, // 平均温度
    val lateralTemp: Float = 25f             // 推杆温度（未使用）
)

/**
 * 机械臂状态
 */
data class RobotState(
    val mode: RobotMode = RobotMode.ACTIVE,
    val mainMode: MainMode = MainMode.ACTIVE,
    val activeSubMode: ActiveSubMode? = ActiveSubMode.STANDARD,
    val passiveSubMode: PassiveSubMode? = null,
    val memorySubMode: MemorySubMode? = null,
    val currentGameType: GameType? = null,
    val isConnected: Boolean = false,
    val sensorData: SensorData = SensorData(),
    val currentMemoryAction: String? = null
)

/**
 * 记忆动作
 */
data class MemoryAction(
    val id: String,
    val name: String,
    val description: String,
    val duration: Long,                      // 动作持续时间（毫秒）
    val keyframes: List<Keyframe>            // 关键帧列表
)

/**
 * 动作关键帧
 */
data class Keyframe(
    val timestamp: Long,                     // 相对时间戳
    val shoulderAngle: Float,
    val elbowAngle: Float,
    val lateralPosition: Float
)

/**
 * 康复分析结果
 */
data class RehabAnalysis(
    val timestamp: Long = System.currentTimeMillis(),
    val smoothness: Float = 0f,              // 运动平滑度 (0-100)
    val rangeOfMotion: Float = 0f,           // 运动范围 (0-100)
    val strength: Float = 0f,                // 力量评分 (0-100)
    val overallScore: Float = 0f,            // 总体康复评分 (0-100)
    val recommendation: String = ""          // AI建议
)

/**
 * 控制命令
 */
data class ControlCommand(
    val mode: RobotMode,
    val shoulderAngle: Float? = null,
    val elbowAngle: Float? = null,
    val lateralPosition: Float? = null,
    val memoryActionId: String? = null
)

/**
 * WiFi配置信息
 */
data class WiFiConfig(
    val ssid: String,
    val password: String,
    val psocIpAddress: String = "192.168.4.1",  // PSoC Edge默认IP
    val psocPort: Int = 8081                     // HTTP服务器端口
)

/**
 * 系统状态（来自PSoC Edge E84）
 */
data class SystemStatus(
    val timestamp: Long = System.currentTimeMillis(),
    val mode: RobotMode = RobotMode.ACTIVE,
    val isEmergencyStop: Boolean = false,
    val isSafetyOk: Boolean = true,
    val errorCode: Int = 0,
    val errorMessage: String = "",
    val m55Status: String = "running",           // M55核心状态
    val aiEngineStatus: String = "ready"         // AI引擎状态
)

/**
 * 训练会话数据
 */
data class TrainingSession(
    val id: String,
    val patientId: String = "",
    val startTime: Long = System.currentTimeMillis(),
    val endTime: Long = 0,
    val mode: RobotMode = RobotMode.ACTIVE,
    val duration: Long = 0,                      // 训练时长（毫秒）
    val sensorDataList: List<SensorData> = emptyList(),
    val rehabAnalysis: RehabAnalysis? = null
)

/**
 * OpenClaw工具调用请求
 */
data class OpenClawToolRequest(
    val toolName: String,
    val parameters: Map<String, Any> = emptyMap()
)

/**
 * OpenClaw工具调用响应
 */
data class OpenClawToolResponse(
    val success: Boolean,
    val result: Any?,
    val error: String? = null
)
