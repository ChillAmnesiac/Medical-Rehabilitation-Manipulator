package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.RobotViewModel
import com.rehab.robotarm.ui.components.Arm3DView
import kotlinx.coroutines.delay

/**
 * 标准训练界面 - 主动模式
 * 患者主动运动，系统记录和评估
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StandardTrainingScreen(
    navController: NavController,
    viewModel: RobotViewModel = viewModel()
) {
    val robotState by viewModel.robotState.collectAsState()
    var isTraining by remember { mutableStateOf(false) }
    var isRecording by remember { mutableStateOf(false) }
    var trainingDuration by remember { mutableStateOf(0) }
    var movementCount by remember { mutableStateOf(0) }
    val trajectoryPoints = remember { mutableStateListOf<Offset>() }
    var showSaveDialog by remember { mutableStateOf(false) }
    var actionName by remember { mutableStateOf("") }
    var actionDescription by remember { mutableStateOf("") }

    // 训练计时器
    LaunchedEffect(isTraining) {
        if (isTraining) {
            while (isTraining) {
                delay(1000)
                trainingDuration++
            }
        }
    }

    // 记录运动轨迹
    LaunchedEffect(robotState.sensorData) {
        if (isTraining) {
            val point = Offset(
                robotState.sensorData.shoulderAngle,
                robotState.sensorData.elbowAngle
            )
            trajectoryPoints.add(point)
            if (trajectoryPoints.size > 100) {
                trajectoryPoints.removeAt(0)
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("标准训练") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, "返回")
                    }
                },
                actions = {
                    // 录制按钮
                    if (isTraining) {
                        IconButton(
                            onClick = {
                                if (isRecording) {
                                    viewModel.stopRecording()
                                    isRecording = false
                                    showSaveDialog = true
                                } else {
                                    viewModel.startRecording()
                                    isRecording = true
                                }
                            }
                        ) {
                            Icon(
                                if (isRecording) Icons.Default.Stop else Icons.Default.FiberManualRecord,
                                contentDescription = if (isRecording) "停止录制" else "开始录制",
                                tint = if (isRecording) Color.Red else MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 训练状态卡片
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = if (isTraining) Color(0xFF4CAF50).copy(alpha = 0.2f) else MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = if (isTraining) "训练中..." else "准备开始",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                            if (isRecording) {
                                Text(
                                    text = "● 正在录制",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = Color.Red,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        Icon(
                            if (isTraining) Icons.Default.FitnessCenter else Icons.Default.PlayArrow,
                            contentDescription = null,
                            tint = if (isTraining) Color(0xFF4CAF50) else MaterialTheme.colorScheme.primary
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "训练时长: ${trainingDuration / 60}分${trainingDuration % 60}秒",
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Text(
                        text = "运动次数: $movementCount",
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
            }

            // 实时传感器数据
            Card {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "实时数据",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        SensorDataItem(
                            label = "肩关节",
                            value = "${robotState.sensorData.shoulderAngle.toInt()}°",
                            icon = Icons.Default.RotateRight
                        )
                        SensorDataItem(
                            label = "肘关节",
                            value = "${robotState.sensorData.elbowAngle.toInt()}°",
                            icon = Icons.Default.RotateLeft
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        SensorDataItem(
                            label = "力矩",
                            value = "${String.format("%.1f", robotState.sensorData.shoulderTorque)}Nm",
                            icon = Icons.Default.Speed
                        )
                        SensorDataItem(
                            label = "速度",
                            value = "${String.format("%.1f", robotState.sensorData.shoulderAngle)}°/s",
                            icon = Icons.Default.TrendingUp
                        )
                    }
                }
            }

            // 3D手臂模型
            Card {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "3D运动轨迹",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Arm3DView(
                        shoulderAngle = robotState.sensorData.motor1Angle,
                        elbowAngle = robotState.sensorData.motor2Angle,
                        lateralAngle = robotState.sensorData.imuAngleX,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(300.dp)
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "拖动旋转视角",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // 运动范围评估
            Card {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "运动范围评估",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    RangeIndicator(
                        label = "肩关节活动度",
                        current = robotState.sensorData.shoulderAngle,
                        min = 0f,
                        max = 180f,
                        optimal = 90f
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    RangeIndicator(
                        label = "肘关节活动度",
                        current = robotState.sensorData.elbowAngle,
                        min = 0f,
                        max = 180f,
                        optimal = 90f
                    )
                }
            }

            // 控制按钮
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (!isTraining) {
                    Button(
                        onClick = {
                            isTraining = true
                            trainingDuration = 0
                            movementCount = 0
                            trajectoryPoints.clear()
                        },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF4CAF50)
                        )
                    ) {
                        Icon(Icons.Default.PlayArrow, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("开始训练")
                    }
                } else {
                    Button(
                        onClick = {
                            isTraining = false
                            // 保存训练数据
                        },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.error
                        )
                    ) {
                        Icon(Icons.Default.Stop, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("结束训练")
                    }
                }

                OutlinedButton(
                    onClick = {
                        trajectoryPoints.clear()
                        movementCount = 0
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = null)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("重置")
                }
            }
        }
    }

    // 保存动作对话框
    if (showSaveDialog) {
        AlertDialog(
            onDismissRequest = {
                showSaveDialog = false
                actionName = ""
                actionDescription = ""
            },
            title = { Text("保存录制的动作") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(
                        value = actionName,
                        onValueChange = { actionName = it },
                        label = { Text("动作名称") },
                        placeholder = { Text("例如：肩关节抬升训练") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                    OutlinedTextField(
                        value = actionDescription,
                        onValueChange = { actionDescription = it },
                        label = { Text("动作描述") },
                        placeholder = { Text("例如：适合肩关节康复初期") },
                        maxLines = 3,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (actionName.isNotBlank()) {
                            viewModel.saveRecording(
                                name = actionName,
                                description = actionDescription.ifBlank { "标准训练录制" }
                            )
                            showSaveDialog = false
                            actionName = ""
                            actionDescription = ""
                        }
                    },
                    enabled = actionName.isNotBlank()
                ) {
                    Text("保存")
                }
            },
            dismissButton = {
                TextButton(onClick = {
                    showSaveDialog = false
                    actionName = ""
                    actionDescription = ""
                }) {
                    Text("取消")
                }
            }
        )
    }
}

@Composable
fun SensorDataItem(
    label: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(32.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun RangeIndicator(
    label: String,
    current: Float,
    min: Float,
    max: Float,
    optimal: Float
) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(text = label, style = MaterialTheme.typography.bodyMedium)
            Text(
                text = "${current.toInt()}°",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(4.dp))

        LinearProgressIndicator(
            progress = { (current - min) / (max - min) },
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp),
            color = when {
                current < optimal * 0.5f -> Color(0xFFFF5722)
                current < optimal * 0.8f -> Color(0xFFFFC107)
                else -> Color(0xFF4CAF50)
            },
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = "${min.toInt()}°",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = "${max.toInt()}°",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

