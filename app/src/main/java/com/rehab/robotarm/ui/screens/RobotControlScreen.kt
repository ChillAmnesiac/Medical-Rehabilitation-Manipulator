package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rehab.robotarm.ui.theme.*
import com.rehab.robotarm.viewmodel.RobotViewModel
import kotlin.math.cos
import kotlin.math.sin

/**
 * 界面一：机械臂3D控制界面
 * 显示机械臂动画，关节颜色代表温度，可控制运动
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RobotControlScreen(viewModel: RobotViewModel = viewModel()) {
    val robotState by viewModel.robotState.collectAsState()
    val sensorData = robotState.sensorData

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // 标题
        Text(
            text = "机械臂控制",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // 连接状态
        ConnectionStatusCard(isConnected = robotState.isConnected, viewModel = viewModel)

        Spacer(modifier = Modifier.height(16.dp))

        // 3D机械臂显示区域
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
        ) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                RobotArmVisualization(
                    shoulderAngle = sensorData.shoulderAngle,
                    elbowAngle = sensorData.elbowAngle,
                    lateralPosition = sensorData.lateralPosition,
                    shoulderTemp = sensorData.shoulderTemp,
                    elbowTemp = sensorData.elbowTemp
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 控制面板（仅在被动模式下可用，但始终显示）
        val isControlEnabled = robotState.mode == com.rehab.robotarm.data.model.RobotMode.PASSIVE
        android.util.Log.d("RobotControlScreen", "Current mode: ${robotState.mode}, isControlEnabled: $isControlEnabled")
        ControlPanel(
            viewModel = viewModel,
            isEnabled = isControlEnabled
        )

        // 温度图例
        TemperatureLegend()
    }
}

@Composable
fun ConnectionStatusCard(isConnected: Boolean, viewModel: RobotViewModel = viewModel()) {
    var showConnectionDialog by remember { mutableStateOf(false) }

    Card(
        colors = CardDefaults.cardColors(
            containerColor = if (isConnected) MedicalGreen.copy(alpha = 0.2f) else MedicalRed.copy(alpha = 0.2f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(12.dp)
                        .background(
                            if (isConnected) MedicalGreen else MedicalRed,
                            shape = MaterialTheme.shapes.small
                        )
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = if (isConnected) "已连接" else "未连接",
                    style = MaterialTheme.typography.bodyMedium
                )
            }

            if (!isConnected) {
                Button(
                    onClick = { showConnectionDialog = true },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MedicalBlue
                    )
                ) {
                    Text("连接PSoC")
                }
            }
        }
    }

    if (showConnectionDialog) {
        ConnectionDialog(
            onDismiss = { showConnectionDialog = false },
            onConnect = { url ->
                viewModel.connectPSoC(url)
                showConnectionDialog = false
            }
        )
    }
}

@Composable
fun ConnectionDialog(
    onDismiss: () -> Unit,
    onConnect: (String) -> Unit
) {
    var url by remember { mutableStateOf("http://192.168.5.217:8081") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("连接PSoC Edge") },
        text = {
            Column {
                Text(
                    "输入PSoC Edge HTTP服务器地址",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                OutlinedTextField(
                    value = url,
                    onValueChange = { url = it },
                    label = { Text("服务器地址") },
                    placeholder = { Text("http://localhost:8081") },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onConnect(url) },
                enabled = url.isNotBlank()
            ) {
                Text("连接")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}

@Composable
fun RobotArmVisualization(
    shoulderAngle: Float,
    elbowAngle: Float,
    lateralPosition: Float,
    shoulderTemp: Float,
    elbowTemp: Float
) {
    Canvas(modifier = Modifier.fillMaxSize()) {
        val centerX = size.width / 2
        val centerY = size.height / 2

        // 绘制阴影效果
        val shadowOffset = 8f

        // 基座底座（3D效果）
        drawCircle(
            color = Color(0xFF424242),
            radius = 50f,
            center = Offset(centerX, centerY + 120)
        )
        drawCircle(
            color = Color(0xFF616161),
            radius = 45f,
            center = Offset(centerX, centerY + 115)
        )
        drawCircle(
            color = Color(0xFF757575),
            radius = 35f,
            center = Offset(centerX, centerY + 110)
        )

        // 推杆（横向张开）- 根据lateralPosition调整
        val lateralOffset = lateralPosition * 2
        val baseX = centerX + lateralOffset

        // 绘制推杆导轨
        drawLine(
            color = Color(0xFF9E9E9E),
            start = Offset(centerX - 100, centerY + 100),
            end = Offset(centerX + 100, centerY + 100),
            strokeWidth = 8f
        )

        // 推杆滑块
        drawRoundRect(
            color = Color(0xFF757575),
            topLeft = Offset(baseX - 15, centerY + 90),
            size = androidx.compose.ui.geometry.Size(30f, 20f),
            cornerRadius = androidx.compose.ui.geometry.CornerRadius(4f, 4f)
        )

        // 肩关节
        val shoulderColor = getTemperatureColor(shoulderTemp)
        val upperArmLength = 150f
        val shoulderRad = Math.toRadians(shoulderAngle.toDouble())
        val shoulderEndX = baseX + (upperArmLength * cos(shoulderRad)).toFloat()
        val shoulderEndY = centerY + 100 - (upperArmLength * sin(shoulderRad)).toFloat()

        // 绘制上臂阴影
        drawLine(
            color = Color.Black.copy(alpha = 0.2f),
            start = Offset(baseX + shadowOffset, centerY + 100 + shadowOffset),
            end = Offset(shoulderEndX + shadowOffset, shoulderEndY + shadowOffset),
            strokeWidth = 24f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )

        // 绘制上臂（3D圆柱效果）
        drawLine(
            color = shoulderColor.copy(alpha = 0.7f),
            start = Offset(baseX, centerY + 100),
            end = Offset(shoulderEndX, shoulderEndY),
            strokeWidth = 28f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )
        drawLine(
            color = shoulderColor,
            start = Offset(baseX, centerY + 100),
            end = Offset(shoulderEndX, shoulderEndY),
            strokeWidth = 24f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )
        drawLine(
            color = Color.White.copy(alpha = 0.3f),
            start = Offset(baseX - 3, centerY + 100 - 3),
            end = Offset(shoulderEndX - 3, shoulderEndY - 3),
            strokeWidth = 8f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )

        // 肩关节球体（3D效果）
        drawCircle(
            color = Color.Black.copy(alpha = 0.2f),
            radius = 28f,
            center = Offset(baseX + shadowOffset, centerY + 100 + shadowOffset)
        )
        drawCircle(
            color = shoulderColor.copy(alpha = 0.8f),
            radius = 30f,
            center = Offset(baseX, centerY + 100)
        )
        drawCircle(
            color = shoulderColor,
            radius = 25f,
            center = Offset(baseX, centerY + 100)
        )
        drawCircle(
            color = Color.White.copy(alpha = 0.5f),
            radius = 12f,
            center = Offset(baseX - 5, centerY + 95)
        )

        // 肘关节
        val elbowColor = getTemperatureColor(elbowTemp)
        val forearmLength = 120f
        val elbowRad = Math.toRadians((shoulderAngle + elbowAngle).toDouble())
        val elbowEndX = shoulderEndX + (forearmLength * cos(elbowRad)).toFloat()
        val elbowEndY = shoulderEndY - (forearmLength * sin(elbowRad)).toFloat()

        // 绘制前臂阴影
        drawLine(
            color = Color.Black.copy(alpha = 0.2f),
            start = Offset(shoulderEndX + shadowOffset, shoulderEndY + shadowOffset),
            end = Offset(elbowEndX + shadowOffset, elbowEndY + shadowOffset),
            strokeWidth = 20f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )

        // 绘制前臂（3D圆柱效果）
        drawLine(
            color = elbowColor.copy(alpha = 0.7f),
            start = Offset(shoulderEndX, shoulderEndY),
            end = Offset(elbowEndX, elbowEndY),
            strokeWidth = 24f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )
        drawLine(
            color = elbowColor,
            start = Offset(shoulderEndX, shoulderEndY),
            end = Offset(elbowEndX, elbowEndY),
            strokeWidth = 20f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )
        drawLine(
            color = Color.White.copy(alpha = 0.3f),
            start = Offset(shoulderEndX - 2, shoulderEndY - 2),
            end = Offset(elbowEndX - 2, elbowEndY - 2),
            strokeWidth = 6f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )

        // 肘关节球体（3D效果）
        drawCircle(
            color = Color.Black.copy(alpha = 0.2f),
            radius = 23f,
            center = Offset(shoulderEndX + shadowOffset, shoulderEndY + shadowOffset)
        )
        drawCircle(
            color = elbowColor.copy(alpha = 0.8f),
            radius = 25f,
            center = Offset(shoulderEndX, shoulderEndY)
        )
        drawCircle(
            color = elbowColor,
            radius = 20f,
            center = Offset(shoulderEndX, shoulderEndY)
        )
        drawCircle(
            color = Color.White.copy(alpha = 0.5f),
            radius = 10f,
            center = Offset(shoulderEndX - 4, shoulderEndY - 4)
        )

        // 末端执行器（夹爪）
        val gripperColor = Color(0xFF37474F)

        // 夹爪阴影
        drawCircle(
            color = Color.Black.copy(alpha = 0.2f),
            radius = 20f,
            center = Offset(elbowEndX + shadowOffset, elbowEndY + shadowOffset)
        )

        // 夹爪主体
        drawCircle(
            color = gripperColor,
            radius = 22f,
            center = Offset(elbowEndX, elbowEndY)
        )
        drawCircle(
            color = Color(0xFF546E7A),
            radius = 18f,
            center = Offset(elbowEndX, elbowEndY)
        )

        // 夹爪细节
        drawLine(
            color = Color(0xFF263238),
            start = Offset(elbowEndX - 10, elbowEndY),
            end = Offset(elbowEndX - 20, elbowEndY - 5),
            strokeWidth = 4f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )
        drawLine(
            color = Color(0xFF263238),
            start = Offset(elbowEndX - 10, elbowEndY),
            end = Offset(elbowEndX - 20, elbowEndY + 5),
            strokeWidth = 4f,
            cap = androidx.compose.ui.graphics.StrokeCap.Round
        )

        // 高光
        drawCircle(
            color = Color.White.copy(alpha = 0.4f),
            radius = 8f,
            center = Offset(elbowEndX - 5, elbowEndY - 5)
        )
    }
}

@Composable
fun ControlPanel(viewModel: RobotViewModel, isEnabled: Boolean) {
    var shoulderAngle by remember { mutableStateOf(0f) }
    var elbowAngle by remember { mutableStateOf(0f) }
    var lateralPosition by remember { mutableStateOf(0f) }

    Card {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text("手动控制", style = MaterialTheme.typography.titleMedium)
            Text(
                if (isEnabled) "被动模式已启用" else "仅在被动模式下可用",
                style = MaterialTheme.typography.bodySmall,
                color = if (isEnabled) MedicalGreen else MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(16.dp))

            // 肩关节电机控制
            MotorControlSection(
                title = "肩关节电机",
                currentValue = shoulderAngle,
                unit = "°",
                range = 0f..180f,
                enabled = isEnabled,
                onValueChange = { shoulderAngle = it },
                onIncrease = {
                    shoulderAngle = (shoulderAngle + 5f).coerceAtMost(180f)
                    viewModel.controlShoulder(shoulderAngle)
                },
                onDecrease = {
                    shoulderAngle = (shoulderAngle - 5f).coerceAtLeast(0f)
                    viewModel.controlShoulder(shoulderAngle)
                },
                onSliderFinished = {
                    viewModel.controlShoulder(shoulderAngle)
                }
            )

            Spacer(modifier = Modifier.height(16.dp))

            // 肘关节电机控制
            MotorControlSection(
                title = "肘关节电机",
                currentValue = elbowAngle,
                unit = "°",
                range = 0f..180f,
                enabled = isEnabled,
                onValueChange = { elbowAngle = it },
                onIncrease = {
                    elbowAngle = (elbowAngle + 5f).coerceAtMost(180f)
                    viewModel.controlElbow(elbowAngle)
                },
                onDecrease = {
                    elbowAngle = (elbowAngle - 5f).coerceAtLeast(0f)
                    viewModel.controlElbow(elbowAngle)
                },
                onSliderFinished = {
                    viewModel.controlElbow(elbowAngle)
                }
            )

            Spacer(modifier = Modifier.height(16.dp))

            // 推杆电机控制
            MotorControlSection(
                title = "推杆电机",
                currentValue = lateralPosition,
                unit = "%",
                range = 0f..100f,
                enabled = isEnabled,
                onValueChange = { lateralPosition = it },
                onIncrease = {
                    lateralPosition = (lateralPosition + 5f).coerceAtMost(100f)
                    viewModel.controlLateral(lateralPosition)
                },
                onDecrease = {
                    lateralPosition = (lateralPosition - 5f).coerceAtLeast(0f)
                    viewModel.controlLateral(lateralPosition)
                },
                onSliderFinished = {
                    viewModel.controlLateral(lateralPosition)
                }
            )
        }
    }
}

@Composable
fun MotorControlSection(
    title: String,
    currentValue: Float,
    unit: String,
    range: ClosedFloatingPointRange<Float>,
    enabled: Boolean,
    onValueChange: (Float) -> Unit,
    onIncrease: () -> Unit,
    onDecrease: () -> Unit,
    onSliderFinished: () -> Unit
) {
    Column {
        Text(
            text = title,
            style = MaterialTheme.typography.titleSmall,
            color = if (enabled) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(8.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 减小按钮
            Button(
                onClick = onDecrease,
                modifier = Modifier.size(48.dp),
                contentPadding = PaddingValues(0.dp),
                enabled = enabled
            ) {
                Icon(Icons.Default.KeyboardArrowDown, contentDescription = "减小")
            }

            // 滑块和数值显示
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    "${currentValue.toInt()}$unit",
                    style = MaterialTheme.typography.bodyLarge,
                    modifier = Modifier.align(Alignment.CenterHorizontally)
                )
                Slider(
                    value = currentValue,
                    onValueChange = onValueChange,
                    valueRange = range,
                    onValueChangeFinished = onSliderFinished,
                    enabled = enabled
                )
            }

            // 增大按钮
            Button(
                onClick = onIncrease,
                modifier = Modifier.size(48.dp),
                contentPadding = PaddingValues(0.dp),
                enabled = enabled
            ) {
                Icon(Icons.Default.KeyboardArrowUp, contentDescription = "增大")
            }
        }
    }
}

@Composable
fun TemperatureLegend() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        LegendItem("低温", TempCold)
        LegendItem("正常", TempNormal)
        LegendItem("温暖", TempWarm)
        LegendItem("过热", TempHot)
    }
}

@Composable
fun LegendItem(label: String, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier = Modifier
                .size(16.dp)
                .background(color, shape = MaterialTheme.shapes.small)
        )
        Spacer(modifier = Modifier.width(4.dp))
        Text(label, style = MaterialTheme.typography.bodySmall)
    }
}

/**
 * 根据温度返回对应颜色
 */
fun getTemperatureColor(temp: Float): Color {
    return when {
        temp < 20 -> TempCold
        temp < 35 -> TempNormal
        temp < 50 -> TempWarm
        else -> TempHot
    }
}
