# 项目架构说明

## 整体架构

本项目采用 **MVVM (Model-View-ViewModel)** 架构模式，结合 Jetpack Compose 构建现代化的Android应用。

```
┌─────────────────────────────────────────────────────────┐
│                        UI Layer                          │
│  (Jetpack Compose Screens + Navigation)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   ViewModel Layer                        │
│              (RobotViewModel)                            │
│         - 管理UI状态                                      │
│         - 处理用户交互                                    │
│         - 协调数据流                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Repository Layer                        │
│              (RobotRepository)                           │
│         - 统一数据管理                                    │
│         - 协调多个数据源                                  │
└────────┬───────────┬───────────┬────────────┬───────────┘
         │           │           │            │
         ▼           ▼           ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
    │蓝牙通信│  │AI推理  │  │云端API │  │协议解析│
    └────────┘  └────────┘  └────────┘  └────────┘
```

## 数据流向

### 1. 传感器数据流（设备 → App）

```
PSoC6设备
    │
    │ (蓝牙传输JSON数据)
    ▼
BluetoothManager
    │
    │ (接收ByteArray)
    ▼
ProtocolParser
    │
    │ (解析为SensorData)
    ▼
RobotRepository
    │
    ├─→ 更新robotState
    ├─→ 添加到sensorDataHistory
    └─→ 触发AI分析
         │
         ▼
    AIInferenceEngine
         │
         │ (生成RehabAnalysis)
         ▼
    RobotRepository
         │
         ▼
    RobotViewModel
         │
         ▼
    UI (自动更新)
```

### 2. 控制命令流（App → 设备）

```
UI (用户操作)
    │
    ▼
RobotViewModel
    │
    ▼
RobotRepository
    │
    ▼
ProtocolParser
    │
    │ (构建JSON命令)
    ▼
BluetoothManager
    │
    │ (发送ByteArray)
    ▼
PSoC6设备
```

## 核心组件说明

### 1. 数据模型层 (data/model/)

**Models.kt** 定义了所有数据结构：
- `RobotMode`: 运动模式枚举（主动/被动/记忆）
- `SensorData`: 传感器数据（角度、力、加速度、温度）
- `RobotState`: 机械臂状态
- `MemoryAction`: 记忆动作
- `RehabAnalysis`: 康复分析结果
- `ControlCommand`: 控制命令

### 2. 通信层 (data/communication/)

**BluetoothManager.kt**
- 管理蓝牙连接生命周期
- 扫描和连接设备
- 发送和接收数据
- 连接状态管理

**ProtocolParser.kt**
- JSON协议解析
- 传感器数据解析
- 控制命令构建
- 记忆动作序列化

### 3. AI层 (data/ai/ & data/cloud/)

**AIInferenceEngine.kt**
- TensorFlow Lite模型加载
- 本地推理执行
- 康复指标计算
- 模拟推理（无模型时）

**CloudAIService.kt**
- 云端API调用
- 豆包大模型集成
- 康复建议生成

### 4. 仓库层 (data/repository/)

**RobotRepository.kt**
- 统一数据管理中心
- 协调所有数据源
- 管理数据流
- 业务逻辑处理

### 5. ViewModel层 (viewmodel/)

**RobotViewModel.kt**
- UI状态管理
- 用户交互处理
- 生命周期管理
- 协程调度

### 6. UI层 (ui/)

**四个主要界面**：
- `RobotControlScreen`: 3D机械臂控制
- `SensorDataScreen`: 传感器数据显示
- `RehabAnalysisScreen`: 康复分析图表
- `ModeControlScreen`: 模式切换和记忆动作管理

**导航**：
- `AppNavigation`: 底部导航栏管理

**主题**：
- `Color.kt`: 颜色定义（包含温度映射颜色）
- `Theme.kt`: Material Design 3主题
- `Type.kt`: 字体配置

## 关键技术点

### 1. 响应式编程

使用 Kotlin Flow 实现响应式数据流：

```kotlin
// Repository中暴露StateFlow
val robotState: StateFlow<RobotState>

// ViewModel中收集
val robotState by viewModel.robotState.collectAsState()

// UI自动更新
Text("温度: ${robotState.sensorData.shoulderTemp}°C")
```

### 2. 协程管理

所有异步操作使用协程：

```kotlin
viewModelScope.launch {
    repository.connectDevice(device)
}
```

### 3. 温度颜色映射

根据电机温度动态改变关节颜色：

```kotlin
fun getTemperatureColor(temp: Float): Color {
    return when {
        temp < 20 -> TempCold      // 蓝色
        temp < 35 -> TempNormal    // 绿色
        temp < 50 -> TempWarm      // 橙色
        else -> TempHot            // 红色
    }
}
```

### 4. AI推理触发

每收集50条数据自动触发一次AI分析：

```kotlin
if (_sensorDataHistory.value.size % 50 == 0) {
    performAIAnalysis()
}
```

## 扩展指南

### 添加新传感器

1. 在 `SensorData` 中添加字段
2. 在 `ProtocolParser.parseSensorData()` 中解析
3. 在 `SensorDataScreen` 中显示
4. 在 `AIInferenceEngine.prepareInputData()` 中使用

### 添加新控制命令

1. 在 `ControlCommand` 中添加参数
2. 在 `ProtocolParser.buildControlCommand()` 中构建
3. 在 `RobotViewModel` 中添加控制方法
4. 在 UI 中调用

### 自定义AI模型

1. 训练模型（输入：传感器序列，输出：康复指标）
2. 转换为 `.tflite` 格式
3. 放入 `assets/models/` 目录
4. 调整 `AIInferenceEngine` 的输入输出处理

## 性能优化建议

1. **数据历史限制**: 只保留最近1000条数据
2. **AI推理频率**: 每50条数据执行一次
3. **UI更新**: 使用 StateFlow 避免过度重组
4. **蓝牙缓冲**: 使用独立线程接收数据
5. **图表渲染**: 只显示最近50个数据点

## 测试建议

1. **单元测试**: 测试 ProtocolParser 的解析逻辑
2. **集成测试**: 测试 Repository 的数据流
3. **UI测试**: 使用 Compose Testing 测试界面
4. **蓝牙测试**: 使用模拟设备测试通信

## 常见问题

### Q: 如何修改蓝牙UUID？
A: 在 `BluetoothManager.kt` 中修改 `DEVICE_UUID` 常量

### Q: 如何更换云端API？
A: 在 `CloudAIService.kt` 中修改 `API_ENDPOINT` 和请求格式

### Q: 如何调整AI推理频率？
A: 在 `RobotRepository.addSensorDataToHistory()` 中修改 `% 50` 的值

### Q: 如何添加数据持久化？
A: 使用 Room 数据库或 DataStore 替代内存存储
