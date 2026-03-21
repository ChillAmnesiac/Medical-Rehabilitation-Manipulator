# 游戏与运动学逆解集成指南

## 概述

游戏系统现在支持基于2D/3D坐标的控制，可以直接使用机械臂运动学逆解计算出的末端位置来玩游戏。

## 坐标系统

### 工作空间定义
- **X轴**: 0 - 0.6米（前后方向）
- **Y轴**: 0 - 0.5米（左右方向）
- **Z轴**: 0 - 0.4米（上下方向，用于3D游戏）

### 坐标原点
- 原点位于机械臂基座位置
- X轴正方向：向前
- Y轴正方向：向右
- Z轴正方向：向上

## 使用方法

### 方法1：直接传入坐标（推荐）

```kotlin
// 在你的控制代码中
val gameViewModel: GameViewModel = viewModel()

// 从运动学逆解获得末端位置
val endEffectorX = 0.35f  // 米
val endEffectorY = 0.25f  // 米

// 更新游戏中的手臂位置
gameViewModel.updateArmPosition(endEffectorX, endEffectorY)
```

### 方法2：从传感器数据自动计算

```kotlin
// 使用内置的运动学正解
val sensorData = SensorData(
    shoulderAngle = 45f,  // 肩关节角度
    elbowAngle = 30f      // 肘关节角度
)

// 自动计算末端位置并更新游戏
// l1: 大臂长度（默认0.3米）
// l2: 小臂长度（默认0.25米）
gameViewModel.updateFromSensorData(
    sensorData = sensorData,
    l1 = 0.3f,
    l2 = 0.25f
)
```

### 方法3：3D坐标（用于高级游戏）

```kotlin
// 3D坐标控制
val x = 0.35f
val y = 0.25f
val z = 0.20f  // 高度

gameViewModel.updateArmPosition3D(x, y, z)
```

## 运动学正解示例

### 2连杆平面机械臂

```kotlin
/**
 * 2连杆平面机械臂正解
 * @param theta1 肩关节角度（度）
 * @param theta2 肘关节角度（度）
 * @param l1 大臂长度（米）
 * @param l2 小臂长度（米）
 * @return Pair(x, y) 末端位置
 */
fun forwardKinematics2Link(
    theta1: Float,
    theta2: Float,
    l1: Float = 0.3f,
    l2: Float = 0.25f
): Pair<Float, Float> {
    val theta1Rad = Math.toRadians(theta1.toDouble())
    val theta2Rad = Math.toRadians(theta2.toDouble())

    val x = (l1 * cos(theta1Rad) + l2 * cos(theta1Rad + theta2Rad)).toFloat()
    val y = (l1 * sin(theta1Rad) + l2 * sin(theta1Rad + theta2Rad)).toFloat()

    return Pair(x, y)
}
```

### 3连杆空间机械臂

```kotlin
/**
 * 3连杆空间机械臂正解
 * @param theta1 基座旋转角度（度）
 * @param theta2 肩关节角度（度）
 * @param theta3 肘关节角度（度）
 * @param l1 第一段长度
 * @param l2 第二段长度
 * @param l3 第三段长度
 * @return Triple(x, y, z) 末端位置
 */
fun forwardKinematics3Link(
    theta1: Float,
    theta2: Float,
    theta3: Float,
    l1: Float = 0.2f,
    l2: Float = 0.25f,
    l3: Float = 0.15f
): Triple<Float, Float, Float> {
    val t1 = Math.toRadians(theta1.toDouble())
    val t2 = Math.toRadians(theta2.toDouble())
    val t3 = Math.toRadians(theta3.toDouble())

    // 计算末端位置
    val r = l1 * cos(t2) + l2 * cos(t2 + t3)
    val x = (r * cos(t1)).toFloat()
    val y = (r * sin(t1)).toFloat()
    val z = (l1 * sin(t2) + l2 * sin(t2 + t3)).toFloat()

    return Triple(x, y, z)
}
```

## 游戏类型与坐标使用

### 1. 水果忍者 (FRUIT_NINJA)
- **坐标系**: 2D (X, Y)
- **玩法**: 移动手臂末端到水果位置"切"水果
- **碰撞检测**: 半径5厘米
- **目标生成**: 随机分布在工作空间内

```kotlin
// 示例：实时更新
viewModelScope.launch {
    while (gameState == GameState.Playing) {
        val (x, y) = forwardKinematics2Link(
            theta1 = sensorData.shoulderAngle,
            theta2 = sensorData.elbowAngle
        )
        gameViewModel.updateArmPosition(x, y)
        delay(50) // 20Hz更新频率
    }
}
```

### 2. 打地鼠 (WHACK_A_MOLE)
- **坐标系**: 2D (X, Y)
- **玩法**: 快速移动到目标位置
- **特点**: 目标会随机出现和消失
- **评分**: 速度越快分数越高

### 3. 节奏大师 (RHYTHM_MASTER)
- **坐标系**: 2D (X, Y)
- **玩法**: 按照节奏移动到目标位置
- **特点**: 目标按时间序列出现
- **评分**: 时机准确度

### 4. 飞行模拟 (FLIGHT_SIM)
- **坐标系**: 可选2D或3D
- **玩法**: 控制飞机高度避开障碍
- **特点**: 连续控制，平滑运动

## 完整集成示例

```kotlin
@Composable
fun GameWithKinematics(
    robotViewModel: RobotViewModel,
    gameViewModel: GameViewModel
) {
    val sensorData by robotViewModel.robotState.collectAsState()
    val gameState by gameViewModel.gameState.collectAsState()

    // 实时更新游戏位置
    LaunchedEffect(sensorData, gameState) {
        if (gameState is GameState.Playing) {
            // 方法1：使用内置正解
            gameViewModel.updateFromSensorData(
                sensorData = sensorData.sensorData,
                l1 = 0.3f,  // 根据实际机械臂尺寸调整
                l2 = 0.25f
            )

            // 方法2：使用自定义运动学
            // val (x, y) = yourCustomForwardKinematics(sensorData)
            // gameViewModel.updateArmPosition(x, y)
        }
    }

    // 显示游戏界面
    RehabGameScreen(
        navController = navController,
        viewModel = gameViewModel,
        gameType = GameType.FRUIT_NINJA
    )
}
```

## 性能优化建议

### 1. 更新频率
- **推荐**: 20-50Hz (20-50ms间隔)
- **最低**: 10Hz (100ms间隔)
- **最高**: 100Hz (10ms间隔)

```kotlin
// 使用协程控制更新频率
viewModelScope.launch {
    while (isActive) {
        updateGamePosition()
        delay(50) // 20Hz
    }
}
```

### 2. 坐标平滑
```kotlin
// 使用低通滤波器平滑坐标
class PositionFilter(val alpha: Float = 0.3f) {
    private var lastX = 0f
    private var lastY = 0f

    fun filter(x: Float, y: Float): Pair<Float, Float> {
        lastX = alpha * x + (1 - alpha) * lastX
        lastY = alpha * y + (1 - alpha) * lastY
        return Pair(lastX, lastY)
    }
}
```

### 3. 碰撞检测优化
```kotlin
// 只检测未击中的目标
private fun checkHitsOptimized(x: Float, y: Float) {
    val activeTargets = _targets.value.filter { !it.isHit }
    // ... 检测逻辑
}
```

## 调试工具

### 显示当前坐标
```kotlin
@Composable
fun DebugOverlay(position: Position2D) {
    Text(
        text = "X: ${String.format("%.3f", position.x)}m\n" +
               "Y: ${String.format("%.3f", position.y)}m",
        modifier = Modifier.padding(16.dp),
        color = Color.White,
        style = MaterialTheme.typography.bodySmall
    )
}
```

### 显示工作空间边界
```kotlin
Canvas(modifier = Modifier.fillMaxSize()) {
    // 绘制工作空间边界
    drawRect(
        color = Color.White.copy(alpha = 0.3f),
        topLeft = Offset(0f, 0f),
        size = Size(size.width, size.height),
        style = Stroke(width = 2f)
    )
}
```

## 常见问题

### Q1: 坐标系不匹配怎么办？
A: 调整坐标映射函数中的比例系数：
```kotlin
val screenX = (target.position.x / YOUR_MAX_X) * width
val screenY = height - (target.position.y / YOUR_MAX_Y) * height
```

### Q2: 如何校准工作空间？
A: 记录机械臂的最大可达范围，更新工作空间定义。

### Q3: 游戏延迟太大？
A:
1. 提高更新频率
2. 减少坐标平滑滤波器的延迟
3. 优化运动学计算

### Q4: 碰撞检测不准确？
A: 调整碰撞半径：
```kotlin
val hitRadius = 0.05f // 增大或减小这个值
```

## 下一步扩展

1. **添加更多游戏类型**
   - 篮球投篮
   - 绘画游戏
   - 迷宫导航

2. **增强视觉效果**
   - 粒子效果
   - 轨迹显示
   - 碰撞动画

3. **多人游戏**
   - 协作模式
   - 竞技模式

4. **自适应难度**
   - 根据患者能力调整目标位置
   - 动态调整碰撞半径
