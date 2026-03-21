package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rehab.robotarm.ui.theme.MedicalBlue
import com.rehab.robotarm.ui.theme.MedicalGreen
import com.rehab.robotarm.ui.theme.MedicalRed
import com.rehab.robotarm.viewmodel.RobotViewModel

/**
 * 自然语言控制界面
 * 通过OpenClaw AI控制机械臂
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NaturalControlScreen(viewModel: RobotViewModel = viewModel()) {
    val openClawConnected by viewModel.openClawConnected.collectAsState()
    val openClawResponse by viewModel.openClawResponse.collectAsState()

    var commandText by remember { mutableStateOf("") }
    var showSettingsDialog by remember { mutableStateOf(false) }
    var gatewayUrl by remember { mutableStateOf("http://localhost:8080") }
    var authToken by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        // 标题栏
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "AI语音控制",
                style = MaterialTheme.typography.headlineMedium
            )

            IconButton(onClick = { showSettingsDialog = true }) {
                Icon(Icons.Default.Settings, contentDescription = "设置")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // OpenClaw连接状态
        OpenClawStatusCard(
            isConnected = openClawConnected,
            gatewayUrl = gatewayUrl,
            onCheckConnection = { viewModel.checkOpenClawConnection() }
        )

        Spacer(modifier = Modifier.height(16.dp))

        // 说明卡片
        Card(
            colors = CardDefaults.cardColors(
                containerColor = MedicalBlue.copy(alpha = 0.1f)
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "💡 使用说明",
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "用自然语言控制机械臂，AI会理解你的意图并执行相应动作。",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 指令输入区
        Card {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "输入指令",
                    style = MaterialTheme.typography.titleMedium
                )

                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = commandText,
                    onValueChange = { commandText = it },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("例如：把肩关节抬高到60度") },
                    minLines = 3,
                    maxLines = 5
                )

                Spacer(modifier = Modifier.height(12.dp))

                Button(
                    onClick = {
                        if (commandText.isNotBlank()) {
                            viewModel.sendNaturalCommand(commandText)
                            commandText = ""
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = openClawConnected && commandText.isNotBlank()
                ) {
                    Icon(Icons.Default.Send, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("发送指令")
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // 快捷指令
        Text(
            text = "快捷指令",
            style = MaterialTheme.typography.titleMedium
        )

        Spacer(modifier = Modifier.height(8.dp))

        QuickCommandButtons(
            onCommandClick = { command ->
                commandText = command
                viewModel.sendNaturalCommand(command)
            },
            enabled = openClawConnected
        )

        Spacer(modifier = Modifier.height(16.dp))

        // AI创建预设动作
        Card {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "AI创建预设动作",
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "用自然语言描述动作，AI会帮你创建预设动作序列",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(12.dp))

                var actionDescription by remember { mutableStateOf("") }

                OutlinedTextField(
                    value = actionDescription,
                    onValueChange = { actionDescription = it },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("例如：肩关节从0度抬到90度，保持3秒，然后回到0度") },
                    minLines = 2
                )

                Spacer(modifier = Modifier.height(12.dp))

                Button(
                    onClick = {
                        if (actionDescription.isNotBlank()) {
                            viewModel.createMemoryActionFromAI(actionDescription)
                            actionDescription = ""
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = openClawConnected && actionDescription.isNotBlank()
                ) {
                    Text("让AI创建动作")
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // AI响应显示
        if (openClawResponse != null) {
            AIResponseCard(
                response = openClawResponse!!,
                onDismiss = { viewModel.clearOpenClawResponse() }
            )
        }
    }

    // 设置对话框
    if (showSettingsDialog) {
        AlertDialog(
            onDismissRequest = { showSettingsDialog = false },
            title = { Text("OpenClaw Bridge设置") },
            text = {
                Column {
                    Text("请输入OpenClaw HTTP Bridge地址")
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = gatewayUrl,
                        onValueChange = { gatewayUrl = it },
                        label = { Text("Bridge URL") },
                        placeholder = { Text("http://192.168.5.217:8080") },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    viewModel.setOpenClawGateway(gatewayUrl, authToken)
                    viewModel.checkOpenClawConnection()
                    showSettingsDialog = false
                }) {
                    Text("确定")
                }
            },
            dismissButton = {
                TextButton(onClick = { showSettingsDialog = false }) {
                    Text("取消")
                }
            }
        )
    }
}

@Composable
fun OpenClawStatusCard(
    isConnected: Boolean,
    gatewayUrl: String,
    onCheckConnection: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = if (isConnected)
                MedicalGreen.copy(alpha = 0.2f)
            else
                MedicalRed.copy(alpha = 0.2f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
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
                        text = if (isConnected) "Gateway已连接" else "Gateway未连接",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }

                TextButton(onClick = onCheckConnection) {
                    Text("检测")
                }
            }

            Text(
                text = gatewayUrl,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun QuickCommandButtons(
    onCommandClick: (String) -> Unit,
    enabled: Boolean
) {
    val commands = listOf(
        "把肩关节抬高到60度",
        "切换到被动模式",
        "开始一组康复训练",
        "检查当前传感器数据",
        "切换到助力模式",
        "停止所有运动"
    )

    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        commands.chunked(2).forEach { rowCommands ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                rowCommands.forEach { command ->
                    OutlinedButton(
                        onClick = { onCommandClick(command) },
                        modifier = Modifier.weight(1f),
                        enabled = enabled
                    ) {
                        Text(
                            text = command,
                            style = MaterialTheme.typography.bodySmall,
                            maxLines = 2
                        )
                    }
                }
                // 如果是奇数个，填充空白
                if (rowCommands.size == 1) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
fun AIResponseCard(
    response: com.rehab.robotarm.data.cloud.OpenClawResponse,
    onDismiss: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = if (response.success)
                MedicalGreen.copy(alpha = 0.1f)
            else
                MedicalRed.copy(alpha = 0.1f)
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = if (response.success) "✓ AI响应" else "✗ 执行失败",
                    style = MaterialTheme.typography.titleMedium,
                    color = if (response.success) MedicalGreen else MedicalRed
                )

                TextButton(onClick = onDismiss) {
                    Text("关闭")
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            if (response.success) {
                Text(
                    text = response.message,
                    style = MaterialTheme.typography.bodyMedium
                )
            } else {
                Text(
                    text = response.error ?: "未知错误",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MedicalRed
                )
            }
        }
    }
}
