package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rehab.robotarm.viewmodel.RobotViewModel
import com.rehab.robotarm.ui.components.ModeStatusBar

/**
 * 界面二：传感器数据显示界面
 * 实时显示各种传感器数值
 */
@Composable
fun SensorDataScreen(viewModel: RobotViewModel = viewModel()) {
    val robotState by viewModel.robotState.collectAsState()
    val sensorData = robotState.sensorData

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text(
                text = "传感器数据",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(bottom = 8.dp)
            )
        }

        // 模式状态栏
        item {
            ModeStatusBar(
                mainMode = robotState.mainMode,
                activeSubMode = robotState.activeSubMode,
                passiveSubMode = robotState.passiveSubMode,
                memorySubMode = robotState.memorySubMode,
                isConnected = robotState.isConnected
            )
        }

        // 连接提示
        if (!robotState.isConnected) {
            item {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Text(
                        text = "未连接设备，请先连接机械臂以查看实时数据",
                        modifier = Modifier.padding(16.dp),
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                }
            }
        }

        // 电机角度
        item {
            SensorCard(title = "电机角度") {
                SensorDataRow("电机1（肩关节）", String.format("%.1f°", sensorData.motor1Angle))
                SensorDataRow("电机2（肘关节）", String.format("%.1f°", sensorData.motor2Angle))
            }
        }

        // IMU角度（肩膀处）
        item {
            SensorCard(title = "IMU角度（肩膀处）") {
                SensorDataRow("X轴（横向张开）", String.format("%.1f°", sensorData.imuAngleX))
                SensorDataRow("Y轴", String.format("%.1f°", sensorData.imuAngleY))
                SensorDataRow("Z轴", String.format("%.1f°", sensorData.imuAngleZ))
            }
        }

        // IMU加速度（肩膀处）
        item {
            SensorCard(title = "IMU加速度（肩膀处）") {
                SensorDataRow("X轴", String.format("%.2f m/s²", sensorData.imuAccelX))
                SensorDataRow("Y轴", String.format("%.2f m/s²", sensorData.imuAccelY))
                SensorDataRow("Z轴", String.format("%.2f m/s²", sensorData.imuAccelZ))
            }
        }

        // 电机阻尼
        item {
            SensorCard(title = "电机阻尼") {
                SensorDataRow("电机1阻尼", String.format("%.2f", sensorData.motor1Damping))
                SensorDataRow("电机2阻尼", String.format("%.2f", sensorData.motor2Damping))
            }
        }

        // EMG肌电信号
        item {
            SensorCard(title = "EMG肌电信号") {
                SensorDataRow("EMG通道", String.format("%.1f μV", sensorData.emgCh1))
            }
        }

        // 心率传感器
        item {
            SensorCard(title = "心率传感器") {
                SensorDataRow("心率", "${sensorData.heartRate} bpm")
            }
        }

        // 电机温度
        item {
            SensorCard(title = "电机温度") {
                SensorDataRow("电机1温度", String.format("%.1f°C", sensorData.motor1Temp))
                SensorDataRow("电机2温度", String.format("%.1f°C", sensorData.motor2Temp))
                SensorDataRow("平均温度", String.format("%.1f°C", sensorData.temperature))
            }
        }

        // 时间戳
        item {
            Card {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "数据时间戳",
                        style = MaterialTheme.typography.titleSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS")
                            .format(java.util.Date(sensorData.timestamp)),
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
}

@Composable
fun SensorCard(
    title: String,
    content: @Composable ColumnScope.() -> Unit
) {
    Card {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(bottom = 12.dp)
            )
            content()
        }
    }
}

@Composable
fun SensorDataRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}
