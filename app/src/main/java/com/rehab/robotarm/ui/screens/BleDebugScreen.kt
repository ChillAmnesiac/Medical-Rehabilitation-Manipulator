package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.RobotViewModel
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BleDebugScreen(
    navController: NavController,
    robotViewModel: RobotViewModel
) {
    val robotState by robotViewModel.robotState.collectAsState()
    val scope = rememberCoroutineScope()
    var logMessages by remember { mutableStateOf<List<LogMessage>>(emptyList()) }
    var commandText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()

    // 监听传感器数据变化，添加到日志
    LaunchedEffect(robotState.sensorData) {
        robotState.sensorData?.let { data ->
            val timestamp = java.text.SimpleDateFormat("HH:mm:ss.SSS", java.util.Locale.getDefault())
                .format(java.util.Date())
            logMessages = logMessages + LogMessage(
                timestamp = timestamp,
                direction = LogDirection.RX,
                data = "肩: ${data.shoulderAngle}° 肘: ${data.elbowAngle}° 侧移: ${data.lateralPosition}mm"
            )
            // 自动滚动到底部
            if (logMessages.size > 100) {
                logMessages = logMessages.takeLast(100)
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("BLE 调试终端") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                },
                actions = {
                    IconButton(onClick = { logMessages = emptyList() }) {
                        Icon(Icons.Default.Delete, contentDescription = "清空日志")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // 连接状态卡片
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (robotState.isConnected)
                        MaterialTheme.colorScheme.primaryContainer
                    else
                        MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = if (robotState.isConnected) Icons.Default.Bluetooth else Icons.Default.BluetoothDisabled,
                        contentDescription = null,
                        modifier = Modifier.size(32.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = if (robotState.isConnected) "已连接" else "未连接",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "OpenClaw-NUS",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }

            // 日志区域
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .padding(horizontal = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF1E1E1E)
                )
            ) {
                LazyColumn(
                    state = listState,
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(8.dp)
                ) {
                    items(logMessages) { log ->
                        LogMessageItem(log)
                    }
                }

                // 自动滚动到底部
                LaunchedEffect(logMessages.size) {
                    if (logMessages.isNotEmpty()) {
                        listState.animateScrollToItem(logMessages.size - 1)
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // 命令输入区域
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "发送命令",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        OutlinedTextField(
                            value = commandText,
                            onValueChange = { commandText = it },
                            modifier = Modifier.weight(1f),
                            placeholder = { Text("例如: stream:on") },
                            singleLine = true,
                            enabled = robotState.isConnected
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Button(
                            onClick = {
                                if (commandText.isNotEmpty()) {
                                    scope.launch {
                                        val timestamp = java.text.SimpleDateFormat("HH:mm:ss.SSS", java.util.Locale.getDefault())
                                            .format(java.util.Date())
                                        logMessages = logMessages + LogMessage(
                                            timestamp = timestamp,
                                            direction = LogDirection.TX,
                                            data = commandText
                                        )
                                        robotViewModel.sendBleCommand(commandText + "\n")
                                        commandText = ""
                                    }
                                }
                            },
                            enabled = robotState.isConnected && commandText.isNotEmpty()
                        ) {
                            Icon(Icons.Default.Send, contentDescription = "发送")
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // 快捷命令
                    Text(
                        text = "快捷命令",
                        style = MaterialTheme.typography.labelSmall
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        OutlinedButton(
                            onClick = {
                                scope.launch {
                                    val timestamp = java.text.SimpleDateFormat("HH:mm:ss.SSS", java.util.Locale.getDefault())
                                        .format(java.util.Date())
                                    logMessages = logMessages + LogMessage(
                                        timestamp = timestamp,
                                        direction = LogDirection.TX,
                                        data = "stream:on"
                                    )
                                    robotViewModel.sendBleCommand("stream:on\n")
                                }
                            },
                            enabled = robotState.isConnected,
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("启动流", fontSize = 12.sp)
                        }
                        OutlinedButton(
                            onClick = {
                                scope.launch {
                                    val timestamp = java.text.SimpleDateFormat("HH:mm:ss.SSS", java.util.Locale.getDefault())
                                        .format(java.util.Date())
                                    logMessages = logMessages + LogMessage(
                                        timestamp = timestamp,
                                        direction = LogDirection.TX,
                                        data = "stream:off"
                                    )
                                    robotViewModel.sendBleCommand("stream:off\n")
                                }
                            },
                            enabled = robotState.isConnected,
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("停止流", fontSize = 12.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun LogMessageItem(log: LogMessage) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 2.dp)
    ) {
        Text(
            text = log.timestamp,
            color = Color(0xFF808080),
            fontSize = 11.sp,
            fontFamily = FontFamily.Monospace
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = if (log.direction == LogDirection.TX) "TX:" else "RX:",
            color = if (log.direction == LogDirection.TX) Color(0xFF4CAF50) else Color(0xFF2196F3),
            fontSize = 11.sp,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.Bold
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = log.data,
            color = Color(0xFFE0E0E0),
            fontSize = 11.sp,
            fontFamily = FontFamily.Monospace
        )
    }
}

data class LogMessage(
    val timestamp: String,
    val direction: LogDirection,
    val data: String
)

enum class LogDirection {
    TX, RX
}
