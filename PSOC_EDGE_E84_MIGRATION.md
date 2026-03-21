# PSoC Edge E84 迁移指南

本文档说明了Android App从PSoC62迁移到PSoC Edge E84的所有修改。

## 修改概述

根据《PSoC工程导读.md》和《开发计划文档.md》，本次更新主要适配PSoC Edge E84芯片的新功能和架构。

## 主要变更

### 1. 硬件平台升级

**从**: PSoC62 WITH CAPSENSE EVALUATION KIT
**到**: PSoC Edge E84 (Edgi-Talk开发板)

**新增特性**:
- Cortex-M33核心（主控）+ Cortex-M55核心（AI推理）
- Ethos-U55 NPU（AI加速）
- 双核通信机制（共享内存 + 邮箱）
- 更强大的AI推理能力

### 2. 传感器系统扩展

**新增传感器**（通过STM32C8T6传感器节点）:
- MSG肌电传感器 (EMG) - 2通道
- 心率传感器 (MAX30102)
- 六轴IMU传感器 (MPU6050)
  - 3轴加速度计
  - 3轴陀螺仪
- 血氧饱和度传感器

**数据模型更新** (`Models.kt`):
```kotlin
data class SensorData(
    // 新增字段
    val wristAngle: Float = 0f,              // 腕关节角度
    val wristTorque: Float = 0f,             // 腕关节扭矩
    val emgCh1: Float = 0f,                  // EMG通道1
    val emgCh2: Float = 0f,                  // EMG通道2
    val imuAccelX: Float = 0f,               // IMU加速度X
    val imuAccelY: Float = 0f,               // IMU加速度Y
    val imuAccelZ: Float = 0f,               // IMU加速度Z
    val imuGyroX: Float = 0f,                // IMU陀螺仪X
    val imuGyroY: Float = 0f,                // IMU陀螺仪Y
    val imuGyroZ: Float = 0f,                // IMU陀螺仪Z
    val heartRate: Int = 0,                  // 心率（bpm）
    val spo2: Int = 0,                       // 血氧饱和度（%）
    // ... 其他字段
)
```

### 3. 控制模式扩展

**从**: 3种模式（主动、被动、记忆）
**到**: 6种模式

**新增模式** (`Models.kt`):
```kotlin
enum class RobotMode {
    ACTIVE,      // 主动模式：患者主动运动
    PASSIVE,     // 被动模式：机械臂带动患者
    ASSIST,      // 助力模式：根据EMG提供辅助 ⭐新增
    RESIST,      // 阻力模式：提供可调阻力 ⭐新增
    MEMORY,      // 记忆模式：重复学习的轨迹
    GAME         // 游戏模式：互动训练 ⭐新增
}
```

### 4. 通信架构升级

**新增通信方式**:

#### 4.1 HTTP通信 (`HttpManager.kt`)
- 与PSoC Edge E84的HTTP服务器通信
- 支持WiFi连接
- 轮询传感器数据
- 发送控制命令

**主要API**:
```kotlin
class HttpManager {
    fun setPSoCUrl(url: String)
    suspend fun checkConnection(): Boolean
    suspend fun startPolling(intervalMs: Long = 100)
    suspend fun sendData(data: ByteArray): Boolean
}
```

#### 4.2 OpenClaw集成 (`OpenClawService.kt`)
- 连接到OpenClaw HTTP Bridge
- 发送自然语言指令
- 接收AI响应
- 调用PSoC Edge的71个工具函数

**主要API**:
```kotlin
class OpenClawService {
    fun setGatewayUrl(url: String)
    suspend fun sendMessage(message: String): OpenClawResponse
    suspend fun checkHealth(): Boolean
}
```

### 5. 新增用户界面

#### 5.1 自然语言控制界面 (`NaturalControlScreen.kt`)
- 自然语言指令输入
- 快捷指令按钮（机械臂专用）
- AI创建预设动作
- OpenClaw连接状态显示
- AI响应显示

**快捷指令示例**:
- "把肩关节抬高到60度"
- "切换到被动模式"
- "开始一组康复训练"
- "检查当前传感器数据"
- "切换到助力模式"
- "停止所有运动"

#### 5.2 WiFi配置界面 (`WifiConfigScreen.kt`)
- 配置PSoC Edge连接到家庭WiFi
- 设备IP地址设置
- WiFi SSID和密码输入
- 配置状态显示
- 故障排查帮助

**配置流程**:
1. 连接到PSoC Edge的配置热点 "RehabArm-Config"
2. 输入家庭WiFi信息
3. 点击"配置WiFi"按钮
4. 设备自动重启并连接到家庭WiFi

### 6. 协议解析器更新

**文件**: `ProtocolParser.kt`

**更新内容**:
- 支持6种控制模式的解析
- 支持新增传感器数据的解析
- 兼容PSoC Edge E84的JSON格式
- 支持HTTP和蓝牙双通道

**新增解析字段**:
```kotlin
// EMG传感器
emgCh1 = (dataMap["emg_ch1"] as? Double)?.toFloat() ?: 0f
emgCh2 = (dataMap["emg_ch2"] as? Double)?.toFloat() ?: 0f

// 六轴IMU
imuAccelX = (dataMap["imu_accel_x"] as? Double)?.toFloat() ?: 0f
imuGyroX = (dataMap["imu_gyro_x"] as? Double)?.toFloat() ?: 0f
// ...

// 生理传感器
heartRate = (dataMap["heart_rate"] as? Double)?.toInt() ?: 0
spo2 = (dataMap["spo2"] as? Double)?.toInt() ?: 0
```

### 7. 新增数据模型

**文件**: `Models.kt`

**新增类**:
```kotlin
// WiFi配置信息
data class WiFiConfig(
    val ssid: String,
    val password: String,
    val psocIpAddress: String = "192.168.4.1",
    val psocPort: Int = 8081
)

// 系统状态
data class SystemStatus(
    val mode: RobotMode = RobotMode.ACTIVE,
    val isEmergencyStop: Boolean = false,
    val isSafetyOk: Boolean = true,
    val errorCode: Int = 0,
    val m55Status: String = "running",
    val aiEngineStatus: String = "ready"
)

// 训练会话数据
data class TrainingSession(
    val id: String,
    val patientId: String = "",
    val startTime: Long,
    val endTime: Long = 0,
    val mode: RobotMode,
    val duration: Long = 0,
    val sensorDataList: List<SensorData> = emptyList(),
    val rehabAnalysis: RehabAnalysis? = null
)

// OpenClaw工具调用
data class OpenClawToolRequest(
    val toolName: String,
    val parameters: Map<String, Any> = emptyMap()
)

data class OpenClawToolResponse(
    val success: Boolean,
    val result: Any?,
    val error: String? = null
)
```

## PSoC Edge E84 HTTP API端点

根据PSoC工程文档，以下是可用的HTTP API端点：

### 基础端点
- `GET /health` - 健康检查
- `GET /status` - 获取系统状态和传感器数据

### 控制端点
- `POST /mode` - 切换控制模式
- `POST /control` - 发送控制指令
- `POST /memory/execute` - 执行记忆动作
- `POST /memory/stop` - 停止记忆动作

### 传感器端点
- `GET /api/sensor/data` - 获取传感器数据
- `POST /api/sensor/calibrate` - 传感器校准

### 训练端点
- `POST /api/training/start` - 开始训练
- `POST /api/training/stop` - 停止训练
- `GET /api/stats` - 获取统计数据

### OpenClaw工具端点（71个工具）
根据PSoC工程文档，PSoC Edge E84提供了71个OpenClaw工具，分为8大类：

1. **基础控制工具** (8个): 关节运动、模式切换、训练控制
2. **传感器工具** (6个): 数据获取、校准、滤波
3. **统计分析工具** (8个): 训练记录、进度追踪、报告生成
4. **数据管理工具** (6个): 存储、导出、同步
5. **AI推理工具** (5个): 运动预测、康复评估、参数推荐
6. **高级技能工具** (14个): 智能路径规划、疼痛预测、虚拟康复师
7. **安全系统工具** (8个): 急停、故障检测、碰撞检测
8. **自适应模型工具** (18个): EMG校准、疲劳预测、难度调整

## 三者互通架构

### 通信流程

#### 场景1: 简单实时控制（蓝牙直连）
```
用户点击"抬起肩关节"
  → App通过蓝牙发送指令
  → PSoC执行
  → 实时反馈
```

#### 场景2: 自然语言控制（OpenClaw桥接）
```
用户说"帮我做一组康复训练"
  → App发送到OpenClaw (HTTP)
  → OpenClaw理解意图，生成训练计划
  → OpenClaw调用PSoC工具 (HTTP桥接)
    - set_mode("memory")
    - execute_memory(training_plan_id)
  → PSoC执行训练
  → 传感器数据通过蓝牙实时返回App显示
  → 训练结束后，OpenClaw生成康复评估
  → 评估结果返回App
```

#### 场景3: AI辅助训练（三者协同）
```
1. 用户在App启动"AI助力模式"
2. App通过蓝牙设置PSoC为助力模式
3. 患者开始运动，PSoC采集EMG信号
4. M55核心实时AI推理，预测运动意图
5. PSoC根据预测调整电机助力
6. 传感器数据通过蓝牙流式传输到App显示
7. 训练结束，App请求OpenClaw生成康复评估
8. OpenClaw调用PSoC获取历史数据
9. OpenClaw生成评估报告返回App
10. App保存到数据库并生成PDF
```

## 使用建议

### 开发环境
- Android Studio Hedgehog (2023.1.1) 或更高版本
- Android SDK 26 (Android 8.0) 或更高
- Kotlin 1.9.20
- Gradle 8.2.0

### 测试流程

1. **蓝牙连接测试**
   - 配对PSoC Edge E84设备
   - 测试实时数据接收
   - 测试控制指令发送

2. **WiFi连接测试**
   - 配置PSoC Edge连接到WiFi
   - 测试HTTP API调用
   - 测试数据轮询

3. **OpenClaw集成测试**
   - 启动OpenClaw HTTP Bridge
   - 配置Bridge地址
   - 测试自然语言指令
   - 测试工具调用

4. **传感器数据测试**
   - 验证所有传感器数据正确显示
   - 测试EMG信号采集
   - 测试心率和血氧数据
   - 测试IMU数据

5. **控制模式测试**
   - 测试6种控制模式切换
   - 测试助力模式（EMG控制）
   - 测试阻力模式
   - 测试游戏模式

## 兼容性说明

- 保留了对旧PSoC62设备的兼容性
- 协议解析器支持两种格式
- 可通过配置选择蓝牙或HTTP通信
- 新增功能在旧设备上会优雅降级

## 后续开发建议

根据开发计划文档，以下功能可以继续扩展：

1. **AI语音助手** - 集成Whisper + TTS
2. **3D可视化** - 使用OpenGL ES实现真实3D模型
3. **游戏化训练** - 水果忍者、打地鼠等游戏
4. **社交系统** - 排行榜、好友挑战
5. **AR训练** - 使用ARCore实现增强现实训练
6. **智能训练计划** - AI生成个性化训练计划
7. **远程医生监控** - 医生端Web Dashboard
8. **数据分析** - 康复时间预测、异常检测
9. **多语言支持** - 国际化
10. **离线模式** - 本地缓存和自动同步
11. **用户登录系统** - 多用户管理

## 文档更新

以下文档已更新以反映PSoC Edge E84的变化：

- ✅ `README.md` - 项目概述和使用说明
- ✅ `Models.kt` - 数据模型定义
- ✅ `ProtocolParser.kt` - 协议解析器
- ✅ `HttpManager.kt` - HTTP通信管理
- ✅ `OpenClawService.kt` - OpenClaw服务
- ✅ `NaturalControlScreen.kt` - 自然语言控制界面
- ✅ `WifiConfigScreen.kt` - WiFi配置界面

## 总结

本次迁移成功将Android App适配到PSoC Edge E84平台，主要改进包括：

1. ✅ 支持更多传感器（EMG、心率、血氧、IMU）
2. ✅ 扩展到6种控制模式
3. ✅ 新增HTTP/WiFi通信
4. ✅ 集成OpenClaw AI控制
5. ✅ 新增自然语言控制界面
6. ✅ 新增WiFi配置界面
7. ✅ 实现三者互通架构
8. ✅ 更新所有相关文档

App现在可以充分利用PSoC Edge E84的强大功能，为康复训练提供更智能、更个性化的解决方案。
