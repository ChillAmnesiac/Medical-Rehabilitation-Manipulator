package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rehab.robotarm.viewmodel.RobotViewModel

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

        // 角度传感器
        item {
            SensorCard(title = "角度传感器") {
                SensorDataRow("肩关节角度", "${sensorData.shoulderAngle.toInt()}°")
                SensorDataRow("肘关节角度", "${sensorData.elbowAngle.toInt()}°")
                SensorDataRow("推杆位置", "${sensorData.lateralPosition.toInt()}%")
            }
        }

        // 力传感器
        item {
            SensorCard(title = "力/扭矩传感器") {
                SensorDataRow("肩关节扭矩", String.format("%.2f Nm", sensorData.shoulderTorque))
                SensorDataRow("肘关节扭矩", String.format("%.2f Nm", sensorData.elbowTorque))
                SensorDataRow("肩关节力", String.format("%.2f N", sensorData.shoulderForce))
                SensorDataRow("肘关节力", String.format("%.2f N", sensorData.elbowForce))
            }
        }

        // EMG肌电信号
        item {
            SensorCard(title = "EMG肌电信号") {
                SensorDataRow("通道1", String.format("%.1f μV", sensorData.emgCh1))
                SensorDataRow("通道2", String.format("%.1f μV", sensorData.emgCh2))
            }
        }

        // 加速度传感器 - 肩关节
        item {
            SensorCard(title = "肩关节加速度") {
                SensorDataRow("X轴", String.format("%.2f m/s²", sensorData.shoulderAccelX))
                SensorDataRow("Y轴", String.format("%.2f m/s²", sensorData.shoulderAccelY))
                SensorDataRow("Z轴", String.format("%.2f m/s²", sensorData.shoulderAccelZ))
            }
        }

        // 加速度传感器 - 肘关节
        item {
            SensorCard(title = "肘关节加速度") {
                SensorDataRow("X轴", String.format("%.2f m/s²", sensorData.elbowAccelX))
                SensorDataRow("Y轴", String.format("%.2f m/s²", sensorData.elbowAccelY))
                SensorDataRow("Z轴", String.format("%.2f m/s²", sensorData.elbowAccelZ))
            }
        }

        // 温度传感器
        item {
            SensorCard(title = "温度传感器") {
                SensorDataRow("整体温度", String.format("%.1f°C", sensorData.temperature))
                SensorDataRow("肩关节温度", String.format("%.1f°C", sensorData.shoulderTemp))
                SensorDataRow("肘关节温度", String.format("%.1f°C", sensorData.elbowTemp))
                SensorDataRow("推杆电机温度", String.format("%.1f°C", sensorData.lateralTemp))
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
