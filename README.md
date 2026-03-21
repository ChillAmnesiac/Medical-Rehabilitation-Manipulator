# 康复机械臂 Android App

这是一个用于控制和监控医疗康复机械臂的Android应用程序。

## 项目概述

### 硬件配置
- **主控板**: 英飞凌 PSoC Edge E84 (Edgi-Talk开发板)
  - Cortex-M33核心（主控制核）- 运行RT-Thread RTOS
  - Cortex-M55核心（AI推理核）- 配备Ethos-U55 NPU
  - 双核通信：通过共享内存和邮箱机制
- **电机系统**:
  - 2个伺服电机（SimpleFOC24v-GD32驱动器，CAN总线连接）
    - 肩关节伺服电机（纵向抬升）
    - 肘关节伺服电机（纵向抬升）
  - 1个推杆电机（肩关节横向张开）
- **传感器节点** (STM32C8T6 - 独立CAN节点):
  - MSG肌电传感器 (EMG) - 2通道
  - 心率传感器 (MAX30102)
  - 六轴IMU传感器 (MPU6050: 3轴加速度 + 3轴陀螺仪)
- **电机内置传感器**:
  - 角度传感器（每个关节）
  - 阻尼/扭矩传感器（每个关节）
  - 温度传感器（每个电机）
- **通讯**: CAN总线连接所有电机和传感器节点（500kbps）

### 应用功能

#### 主要界面

1. **机械臂控制界面** (`RobotControlScreen`)
   - 实时显示机械臂3D动画
   - 关节颜色根据电机温度实时变化（蓝色→绿色→橙色→红色）
   - 被动模式下可通过滑块控制机械臂运动
   - 显示连接状态（蓝牙/WiFi）

2. **传感器数据界面** (`SensorDataScreen`)
   - 实时显示所有传感器数值
   - 角度传感器（肩关节、肘关节、腕关节、推杆位置）
   - 扭矩/力传感器数据
   - EMG肌电信号（2通道）
   - 六轴IMU数据（加速度 + 陀螺仪）
   - 生理传感器（心率、血氧）
   - 温度传感器数据
   - 数据时间戳

3. **康复分析界面** (`RehabAnalysisScreen`)
   - 显示AI推理得出的康复效果
   - 综合评分（0-100分）
   - 详细指标：运动平滑度、运动范围、力量评分
   - 运动趋势折线图
   - 本地AI建议
   - 云端AI建议（豆包大模型）

4. **模式控制界面** (`ModeControlScreen`)
   - 六种运动模式切换（适配PSoC Edge E84）：
     - **主动模式**: 患者主动运动，系统记录数据
     - **被动模式**: 机械臂带动患者运动
     - **助力模式**: 根据EMG信号提供辅助力
     - **阻力模式**: 提供可调阻力训练
     - **记忆模式**: 重复学习的轨迹
     - **游戏模式**: 互动训练
   - 记忆动作管理（添加、执行、删除）
   - 模式详细说明

5. **自然语言控制界面** (`NaturalControlScreen`)
   - 通过OpenClaw AI控制机械臂
   - 自然语言指令输入
   - 快捷指令按钮
   - AI创建预设动作
   - OpenClaw Gateway连接状态
   - AI响应显示

6. **WiFi配置界面** (`WifiConfigScreen`)
   - 配置PSoC Edge连接到家庭WiFi
   - 设备IP地址设置
   - WiFi SSID和密码输入
   - 配置状态显示
   - 故障排查帮助

### 技术架构

#### 技术栈
- **语言**: Kotlin
- **UI框架**: Jetpack Compose + Material Design 3
- **架构**: MVVM (Model-View-ViewModel)
- **通信**:
  - 蓝牙 SPP (实时控制和数据流)
  - HTTP/WiFi (与PSoC Edge E84通信)
  - OpenClaw HTTP Bridge (AI自然语言控制)
- **AI推理**: TensorFlow Lite (本地推理)
- **云端API**: OkHttp + Retrofit
- **异步处理**: Kotlin Coroutines + Flow

#### 项目结构
```
app/src/main/java/com/rehab/robotarm/
├── MainActivity.kt                          # 主Activity
├── data/
│   ├── model/
│   │   └── Models.kt                       # 数据模型（RobotMode, SensorData, WiFiConfig等）
│   ├── communication/
│   │   ├── BluetoothManager.kt            # 蓝牙通信管理
│   │   ├── HttpManager.kt                 # HTTP通信管理（PSoC Edge）
│   │   └── ProtocolParser.kt              # 通信协议解析
│   ├── ai/
│   │   └── AIInferenceEngine.kt           # 本地AI推理引擎
│   ├── cloud/
│   │   ├── CloudAIService.kt              # 云端AI服务
│   │   └── OpenClawService.kt             # OpenClaw HTTP Bridge服务
│   └── repository/
│       └── RobotRepository.kt             # 数据仓库（统一数据管理）
├── ui/
│   ├── screens/
│   │   ├── RobotControlScreen.kt          # 界面1：机械臂控制
│   │   ├── SensorDataScreen.kt            # 界面2：传感器数据
│   │   ├── RehabAnalysisScreen.kt         # 界面3：康复分析
│   │   ├── ModeControlScreen.kt           # 界面4：模式控制
│   │   ├── NaturalControlScreen.kt        # 界面5：自然语言控制
│   │   └── WifiConfigScreen.kt            # 界面6：WiFi配置
│   ├── navigation/
│   │   └── AppNavigation.kt               # 导航管理
│   └── theme/
│       ├── Color.kt                        # 颜色定义
│       ├── Theme.kt                        # 主题配置
│       └── Type.kt                         # 字体配置
└── viewmodel/
    └── RobotViewModel.kt                   # 主ViewModel
```

### 通信架构

#### 三者互通设计

本系统采用三者互通架构，实现Android App、PSoC Edge E84和OpenClaw Gateway的协同工作：

```
┌─────────────────────────────────────────────────────────┐
│                    Android App (手机端)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 实时控制     │  │ 自然语言输入 │  │ 数据可视化   │  │
│  │ (蓝牙SPP)    │  │ (OpenClaw)   │  │ (蓝牙+HTTP)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────▲───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
    ①蓝牙SPP          ②HTTP(已有)        ③数据回传
    快速指令          自然语言            实时+评估
          │                  │                  │
          ↓                  ↓                  │
┌─────────────────┐   ┌──────────────────────────────┐
│  PSoC Edge E84  │   │    OpenClaw Gateway          │
│                 │   │                              │
│  ④HTTP工具调用  │◄──┤  - 理解自然语言              │
│  /api/command   │   │  - 生成训练计划              │
│  /api/sensors   │───┤  - 调用PSoC工具              │
│  /api/status    │   │  - 生成康复评估              │
│                 │   └──────────────────────────────┘
│  ⑤实时数据流    │
│  传感器→蓝牙    │
└─────────────────┘
```

**通讯方式说明**:

1. **蓝牙SPP (App ↔ PSoC)** - 实时控制通道
   - 用途：快速响应的实时控制和数据流
   - 优势：低延迟(~10ms)、无需网络、点对点连接
   - 数据流：
     - App → PSoC: 关节控制指令、模式切换、紧急停止
     - PSoC → App: 传感器数据流(100Hz)、状态更新、告警信息

2. **HTTP (App ↔ OpenClaw)** - 智能控制通道
   - 用途：自然语言控制、复杂指令、AI建议
   - 优势：App已有OpenClaw连接代码，无需改动
   - 数据流：
     - App → OpenClaw: 自然语言指令("抬起手臂到90度")
     - OpenClaw → App: 执行结果、AI康复建议

3. **HTTP桥接 (OpenClaw ↔ PSoC)** - 工具调用通道
   - 用途：OpenClaw调用PSoC的71个工具函数
   - 实现：PSoC提供HTTP REST API，OpenClaw通过工具调用
   - 数据流：
     - OpenClaw → PSoC: 工具调用(move_joint, set_mode等)
     - PSoC → OpenClaw: 执行结果、传感器数据

## 通信协议

### 数据格式
使用JSON格式进行数据传输

#### 从设备接收的传感器数据（PSoC Edge E84格式）
```json
{
  "type": "sensor",
  "timestamp": 1234567890,
  "shoulder_angle": 45.5,
  "elbow_angle": 30.2,
  "wrist_angle": 15.0,
  "lateral_pos": 50.0,
  "shoulder_torque": 12.5,
  "elbow_torque": 8.3,
  "wrist_torque": 5.2,
  "shoulder_force": 10.0,
  "elbow_force": 7.5,
  "emg_ch1": 0.5,
  "emg_ch2": 0.3,
  "imu_accel_x": 0.5,
  "imu_accel_y": 0.2,
  "imu_accel_z": 9.8,
  "imu_gyro_x": 0.1,
  "imu_gyro_y": 0.05,
  "imu_gyro_z": 0.02,
  "heart_rate": 75,
  "spo2": 98,
  "shoulder_temp": 28.5,
  "elbow_temp": 27.8,
  "lateral_temp": 26.5
}
```

#### 发送到设备的命令

**模式切换命令（支持6种模式）**
```json
{
  "mode": "ACTIVE"  // "ACTIVE", "PASSIVE", "ASSIST", "RESIST", "MEMORY", "GAME"
}
```

**控制命令（被动模式）**
```json
{
  "type": "control",
  "shoulder_angle": 45.0,
  "elbow_angle": 30.0,
  "lateral_pos": 50.0
}
```

**记忆动作命令**
```json
{
  "type": "memory",
  "action_id": "uuid-string",
  "keyframes": [
    {
      "time": 0,
      "shoulder": 0.0,
      "elbow": 0.0,
      "lateral": 0.0
    },
    {
      "time": 1000,
      "shoulder": 45.0,
      "elbow": 30.0,
      "lateral": 50.0
    }
  ]
}
```

### PSoC Edge E84 HTTP API端点

- `GET /health` - 健康检查
- `GET /status` - 获取系统状态和传感器数据
- `POST /mode` - 切换控制模式
- `POST /control` - 发送控制指令
- `POST /memory/execute` - 执行记忆动作
- `POST /memory/stop` - 停止记忆动作
- `GET /api/sensor/data` - 获取传感器数据
- `POST /api/training/start` - 开始训练
- `GET /api/stats` - 获取统计数据

## AI功能

### 本地AI推理
- 使用TensorFlow Lite进行本地推理
- 分析传感器数据序列（最近100个数据点）
- 输出指标：
  - 运动平滑度（基于角度变化的抖动程度）
  - 运动范围（关节活动范围）
  - 力量评分（基于力传感器数据）
  - 综合评分
- 模型文件位置：`app/src/main/assets/models/rehab_model.tflite`

### 云端AI服务
- 集成豆包大模型API
- 根据康复评分生成专业建议
- 包含：康复状态评估、训练建议、注意事项
- 配置位置：`CloudAIService.kt` 中的 `API_KEY` 和 `API_ENDPOINT`

## 安装和使用

### 环境要求
- Android Studio Hedgehog (2023.1.1) 或更高版本
- Android SDK 26 (Android 8.0) 或更高
- Kotlin 1.9.20
- Gradle 8.2.0

### 构建步骤

1. **克隆或打开项目**
   ```bash
   cd RehabRobotArm
   ```

2. **在Android Studio中打开项目**
   - File → Open → 选择 `RehabRobotArm` 目录

3. **同步Gradle**
   - Android Studio会自动提示同步
   - 或手动点击 "Sync Project with Gradle Files"

4. **配置云端API（可选）**
   - 打开 `CloudAIService.kt`
   - 替换 `API_KEY` 为你的豆包API密钥
   - 如不配置，将使用模拟数据

5. **添加AI模型（可选）**
   - 将训练好的 `.tflite` 模型文件放入 `app/src/main/assets/models/`
   - 命名为 `rehab_model.tflite`
   - 如不添加，将使用模拟推理

6. **连接Android设备或启动模拟器**

7. **运行应用**
   - 点击 Run 按钮或按 Shift+F10

### 权限配置

应用需要以下权限（已在AndroidManifest.xml中配置）：
- 蓝牙权限（BLUETOOTH, BLUETOOTH_CONNECT, BLUETOOTH_SCAN）
- 位置权限（蓝牙扫描需要）
- 网络权限（云端API调用）
- 存储权限（保存数据和模型）

首次运行时需要手动授予权限。

## 使用流程

### 方式1：蓝牙连接（实时控制）

1. **连接设备**
   - 确保PSoC Edge E84设备蓝牙已开启
   - 在设置中配对设备
   - 应用会自动连接已配对的设备

2. **选择模式**
   - 进入"模式控制"界面
   - 选择合适的运动模式（主动/被动/助力/阻力/记忆/游戏）

3. **开始训练**
   - **主动模式**: 患者自由移动手臂，系统记录数据
   - **被动模式**: 使用滑块控制机械臂运动
   - **助力模式**: 系统根据EMG信号提供辅助力
   - **阻力模式**: 系统提供可调阻力
   - **记忆模式**: 选择并执行预设动作
   - **游戏模式**: 进行互动训练

4. **查看数据**
   - "传感器数据"界面查看实时数据
   - "康复分析"界面查看AI评估结果

### 方式2：WiFi连接（OpenClaw AI控制）

1. **配置WiFi**
   - 进入"WiFi配置"界面
   - 连接到PSoC Edge的配置热点 "RehabArm-Config"
   - 输入家庭WiFi信息并配置

2. **连接PSoC Edge**
   - 配置成功后，PSoC Edge会连接到家庭WiFi
   - 在App中输入PSoC Edge的IP地址
   - 点击连接

3. **配置OpenClaw Gateway**
   - 进入"自然语言控制"界面
   - 点击设置按钮
   - 输入OpenClaw HTTP Bridge地址（如 http://192.168.1.100:8080）
   - 检测连接状态

4. **使用自然语言控制**
   - 输入自然语言指令，如："把肩关节抬高到60度"
   - 或使用快捷指令按钮
   - AI会理解指令并控制机械臂执行

5. **AI创建预设动作**
   - 用自然语言描述动作序列
   - AI会自动生成记忆动作
   - 可在"模式控制"界面执行

### 方式3：混合模式（推荐）

1. 使用蓝牙接收实时传感器数据（高频率，低延迟）
2. 使用OpenClaw进行复杂的AI控制和康复评估
3. 获取最佳的用户体验

## 开发说明

### 添加新功能

1. **添加新的传感器数据**
   - 在 `Models.kt` 的 `SensorData` 中添加字段
   - 在 `ProtocolParser.kt` 中更新解析逻辑
   - 在 `SensorDataScreen.kt` 中添加显示

2. **修改通信协议**
   - 更新 `ProtocolParser.kt` 中的解析和构建方法
   - 确保与PSoC6设备端协议一致

3. **自定义AI模型**
   - 训练TensorFlow模型并转换为 `.tflite` 格式
   - 更新 `AIInferenceEngine.kt` 中的输入输出处理
   - 调整 `inputSize` 和 `featureSize` 参数

### 调试技巧

1. **蓝牙连接问题**
   - 检查设备是否已配对
   - 确认UUID是否正确（`BluetoothManager.kt` 中的 `DEVICE_UUID`）
   - 查看Logcat中的蓝牙日志

2. **数据解析问题**
   - 在 `ProtocolParser.kt` 中添加日志输出
   - 验证JSON格式是否正确

3. **AI推理问题**
   - 确认模型文件存在
   - 检查输入数据格式和维度
   - 查看异常堆栈信息

## 注意事项

1. **安全限位**
   - 被动模式下，设备端应实现硬件限位保护
   - App端的角度范围限制为0-180度

2. **数据存储**
   - 传感器历史数据保留最近1000条
   - 记忆动作存储在内存中，重启后丢失
   - 如需持久化，可使用DataStore或数据库

3. **性能优化**
   - AI推理每收集50条数据执行一次
   - 可根据需要调整频率

4. **网络请求**
   - 云端API调用需要网络连接
   - 建议添加超时和重试机制

## 后续改进建议

1. **数据持久化**
   - 使用Room数据库存储历史数据
   - 保存记忆动作到本地

2. **3D渲染增强**
   - 使用OpenGL ES或Rajawali 3D实现真实3D模型
   - 添加手势控制（旋转、缩放）

3. **图表优化**
   - 集成专业图表库（如MPAndroidChart）
   - 支持多种图表类型（折线图、柱状图、雷达图）

4. **用户管理**
   - 添加患者信息管理
   - 多用户数据隔离
   - 康复进度追踪

5. **导出功能**
   - 导出康复报告（PDF）
   - 数据导出（CSV/Excel）

6. **离线模式**
   - 本地缓存云端建议
   - 离线数据同步

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请联系开发团队。
