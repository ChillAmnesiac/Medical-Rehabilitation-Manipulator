package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.RobotViewModel
import com.rehab.robotarm.ui.components.Arm3DView
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * 手动控制界面 - 被动模式
 * 通过滑块手动控制机械臂各关节
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ManualControlScreen(
    navController: NavController,
    viewModel: RobotViewModel = viewModel()
) {
    val robotState by viewModel.robotState.collectAsState()
    var targetShoulderAngle by remember { mutableStateOf(90f) }
    var targetElbowAngle by remember { mutableStateOf(90f) }
    var targetLateralPosition by remember { mutableStateOf(50f) }
    var speed by remember { mutableStateOf(50f) }
    var isMoving by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("手动控制") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, "返回")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 安全提示
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFFFC107).copy(alpha = 0.2f)
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = null,
                        tint = Color(0xFFFFC107)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "请确保患者处于安全位置，随时准备按下急停按钮",
                        style = MaterialTheme.typography.bodyMedium
                    )
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
                        text = "3D实时预览",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Arm3DView(
                        shoulderAngle = robotState.sensorData.motor1Angle,
                        elbowAngle = robotState.sensorData.motor2Angle,
                        lateralAngle = robotState.sensorData.imuAngleX,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(300.dp)
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("肩关节", style = MaterialTheme.typography.bodySmall)
                            Text(
                                "${robotState.sensorData.motor1Angle.toInt()}°",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }

                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("肘关节", style = MaterialTheme.typography.bodySmall)
                            Text(
                                "${robotState.sensorData.motor2Angle.toInt()}°",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }

                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("横向张开", style = MaterialTheme.typography.bodySmall)
                            Text(
                                "${robotState.sensorData.imuAngleX.toInt()}°",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "拖动旋转视角",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // 当前状态
            Card {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "当前位置",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                Icons.Default.RotateRight,
                                contentDescription = null,
                                modifier = Modifier.size(32.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Text("肩关节", style = MaterialTheme.typography.bodySmall)
                            Text(
                                "${robotState.sensorData.shoulderAngle.toInt()}°",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                Icons.Default.RotateLeft,
                                contentDescription = null,
                                modifier = Modifier.size(32.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Text("肘关节", style = MaterialTheme.typography.bodySmall)
                            Text(
                                "${robotState.sensorData.elbowAngle.toInt()}°",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }

            // 肩关节控制
            Card {
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
                        Text(
                            text = "肩关节目标角度",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "${targetShoulderAngle.toInt()}°",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Slider(
                        value = targetShoulderAngle,
                        onValueChange = { targetShoulderAngle = it },
                        valueRange = 0f..180f,
                        enabled = !isMoving
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("0°", style = MaterialTheme.typography.bodySmall)
                        Text("90°", style = MaterialTheme.typography.bodySmall)
                        Text("180°", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }

            // 肘关节控制
            Card {
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
                        Text(
                            text = "肘关节目标角度",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "${targetElbowAngle.toInt()}°",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Slider(
                        value = targetElbowAngle,
                        onValueChange = { targetElbowAngle = it },
                        valueRange = 0f..180f,
                        enabled = !isMoving
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("0°", style = MaterialTheme.typography.bodySmall)
                        Text("90°", style = MaterialTheme.typography.bodySmall)
                        Text("180°", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }

            // 推杆控制（横向位置）
            Card {
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
                        Text(
                            text = "横向位置",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "${targetLateralPosition.toInt()}mm",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Slider(
                        value = targetLateralPosition,
                        onValueChange = { targetLateralPosition = it },
                        valueRange = 0f..100f,
                        enabled = !isMoving
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("内收", style = MaterialTheme.typography.bodySmall)
                        Text("中间", style = MaterialTheme.typography.bodySmall)
                        Text("外展", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }

            // 速度控制
            Card {
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
                        Text(
                            text = "运动速度",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "${speed.toInt()}%",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Slider(
                        value = speed,
                        onValueChange = { speed = it },
                        valueRange = 10f..100f,
                        enabled = !isMoving
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("慢", style = MaterialTheme.typography.bodySmall)
                        Text("中", style = MaterialTheme.typography.bodySmall)
                        Text("快", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            // 控制按钮
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = {
                        isMoving = true
                        // 发送关节控制命令
                        viewModel.controlShoulder(targetShoulderAngle)
                        viewModel.controlElbow(targetElbowAngle)
                        viewModel.controlLateral(targetLateralPosition)
                        // 延迟后重置状态
                        GlobalScope.launch {
                            delay(2000)
                            isMoving = false
                        }
                    },
                    modifier = Modifier.weight(1f),
                    enabled = !isMoving,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF4CAF50)
                    )
                ) {
                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("执行")
                }

                OutlinedButton(
                    onClick = {
                        targetShoulderAngle = 90f
                        targetElbowAngle = 90f
                        targetLateralPosition = 50f
                        speed = 50f
                    },
                    modifier = Modifier.weight(1f),
                    enabled = !isMoving
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = null)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("重置")
                }
            }

            // 急停按钮
            Button(
                onClick = {
                    isMoving = false
                    viewModel.emergencyStop()
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(64.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFFFF5722)
                )
            ) {
                Icon(
                    Icons.Default.PanTool,
                    contentDescription = null,
                    modifier = Modifier.size(32.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    "急停",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}
