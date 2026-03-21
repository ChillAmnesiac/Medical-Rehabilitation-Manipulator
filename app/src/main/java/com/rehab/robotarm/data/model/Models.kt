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
 * 传感器数据（适配PSoC Edge E84 + STM32C8T6传感器节点）
 */
data class SensorData(
    val timestamp: Long = System.currentTimeMillis(),
    // 角度传感器
    val shoulderAngle: Float = 0f,           // 肩关节角度
    val elbowAngle: Float = 0f,              // 肘关节角度
    val wristAngle: Float = 0f,              // 腕关节角度
    val lateralPosition: Float = 0f,         // 推杆位置
    // 扭矩传感器
    val shoulderTorque: Float = 0f,          // 肩关节扭矩
    val elbowTorque: Float = 0f,             // 肘关节扭矩
    val wristTorque: Float = 0f,             // 腕关节扭矩
    // 力传感器
    val shoulderForce: Float = 0f,           // 肩关节力传感器
    val elbowForce: Float = 0f,              // 肘关节力传感器
    // EMG肌电传感器（MSG传感器，2通道）
    val emgCh1: Float = 0f,                  // EMG通道1（肌电信号）
    val emgCh2: Float = 0f,                  // EMG通道2（肌电信号）
    // 六轴IMU传感器（MPU6050: 3轴加速度 + 3轴陀螺仪）
    val imuAccelX: Float = 0f,               // IMU加速度X
    val imuAccelY: Float = 0f,               // IMU加速度Y
    val imuAccelZ: Float = 0f,               // IMU加速度Z
    val imuGyroX: Float = 0f,                // IMU陀螺仪X
    val imuGyroY: Float = 0f,                // IMU陀螺仪Y
    val imuGyroZ: Float = 0f,                // IMU陀螺仪Z
    // 关节加速度传感器（保留兼容）
    val shoulderAccelX: Float = 0f,          // 肩关节加速度X
    val shoulderAccelY: Float = 0f,          // 肩关节加速度Y
    val shoulderAccelZ: Float = 0f,          // 肩关节加速度Z
    val elbowAccelX: Float = 0f,             // 肘关节加速度X
    val elbowAccelY: Float = 0f,             // 肘关节加速度Y
    val elbowAccelZ: Float = 0f,             // 肘关节加速度Z
    // 生理传感器（MAX30102）
    val heartRate: Int = 0,                  // 心率（bpm）
    val spo2: Int = 0,                       // 血氧饱和度（%）
    // 温度传感器
    val temperature: Float = 25f,            // 整体温度
    val shoulderTemp: Float = 25f,           // 肩关节温度
    val elbowTemp: Float = 25f,              // 肘关节温度
    val lateralTemp: Float = 25f             // 推杆电机温度
)

/**
 * 机械臂状态
 */
data class RobotState(
    val mode: RobotMode = RobotMode.ACTIVE,
    val mainMode: MainMode = MainMode.ACTIVE,
    val activeSubMode: ActiveSubMode = ActiveSubMode.STANDARD,
    val passiveSubMode: PassiveSubMode = PassiveSubMode.MANUAL,
    val memorySubMode: MemorySubMode = MemorySubMode.REPLAY,
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
