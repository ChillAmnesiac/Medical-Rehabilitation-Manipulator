package com.rehab.robotarm.ui.screens

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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.RobotViewModel
import kotlinx.coroutines.launch

/**
 * AI辅助训练界面
 * 集成OpenClaw AI，提供智能训练指导
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AIAssistTrainingScreen(
    navController: NavController,
    viewModel: RobotViewModel = viewModel()
) {
    val robotState by viewModel.robotState.collectAsState()
    val openClawConnected by viewModel.openClawConnected.collectAsState()
    val openClawResponse by viewModel.openClawResponse.collectAsState()
    var userInput by remember { mutableStateOf("") }
    val messages = remember { mutableStateListOf<ChatMessage>() }
    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()
    var isLoading by remember { mutableStateOf(false) }
    var showSettingsDialog by remember { mutableStateOf(false) }
    var gatewayUrl by remember { mutableStateOf("http://localhost:8080") }

    // 检查OpenClaw连接状态
    LaunchedEffect(Unit) {
        viewModel.checkOpenClawConnection()
    }

    // 监听OpenClaw响应
    LaunchedEffect(openClawResponse) {
        openClawResponse?.let { response ->
            if (response.success) {
                messages.add(ChatMessage(response.message, false))
                isLoading = false
                listState.animateScrollToItem(messages.size - 1)
            } else if (response.error != null) {
                messages.add(ChatMessage("错误: ${response.error}", false))
                isLoading = false
                listState.animateScrollToItem(messages.size - 1)
            }
            viewModel.clearOpenClawResponse()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("AI辅助训练") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, "返回")
                    }
                },
                actions = {
                    // 设置按钮
                    IconButton(onClick = { showSettingsDialog = true }) {
                        Icon(Icons.Default.Settings, "设置")
                    }
                    // 连接状态指示器
                    Icon(
                        if (openClawConnected) Icons.Default.CloudDone else Icons.Default.CloudOff,
                        contentDescription = "连接状态",
                        tint = if (openClawConnected) Color(0xFF4CAF50) else Color(0xFFFF5722),
                        modifier = Modifier.padding(end = 16.dp)
                    )
                }
            )
        },
        bottomBar = {
            Surface(
                shadowElevation = 8.dp
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedTextField(
                        value = userInput,
                        onValueChange = { userInput = it },
                        modifier = Modifier.weight(1f),
                        placeholder = { Text("输入训练指令或问题...") },
                        enabled = openClawConnected && !isLoading,
                        maxLines = 3
                    )

                    IconButton(
                        onClick = {
                            if (userInput.isNotBlank()) {
                                val message = userInput
                                messages.add(ChatMessage(message, true))
                                userInput = ""
                                isLoading = true

                                scope.launch {
                                    // 滚动到底部
                                    listState.animateScrollToItem(messages.size - 1)

                                    // 调用OpenClaw API
                                    viewModel.sendNaturalCommand(message)
                                }
                            }
                        },
                        enabled = openClawConnected && !isLoading && userInput.isNotBlank()
                    ) {
                        Icon(Icons.Default.Send, "发送")
                    }
                }
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // 状态卡片
            if (!openClawConnected) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFFF5722).copy(alpha = 0.2f)
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
                            tint = Color(0xFFFF5722)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "OpenClaw未连接",
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "请在设置中配置OpenClaw服务地址",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                        TextButton(onClick = { showSettingsDialog = true }) {
                            Text("设置")
                        }
                    }
                }
            }

            // 实时传感器数据卡片
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("肩关节", style = MaterialTheme.typography.bodySmall)
                        Text(
                            "${robotState.sensorData.shoulderAngle.toInt()}°",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("肘关节", style = MaterialTheme.typography.bodySmall)
                        Text(
                            "${robotState.sensorData.elbowAngle.toInt()}°",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("力矩", style = MaterialTheme.typography.bodySmall)
                        Text(
                            "${String.format("%.1f", robotState.sensorData.shoulderTorque)}Nm",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            // 聊天消息列表
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .padding(horizontal = 16.dp),
                state = listState,
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (messages.isEmpty()) {
                    item {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 32.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Icon(
                                Icons.Default.Psychology,
                                contentDescription = null,
                                modifier = Modifier.size(64.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                "AI训练助手",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                "您可以用自然语言描述训练需求",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.height(16.dp))

                            // 快捷指令
                            Text(
                                "试试这些指令：",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            SuggestionChip(
                                onClick = { userInput = "制定一个肩关节康复训练计划" },
                                label = { Text("制定训练计划") }
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            SuggestionChip(
                                onClick = { userInput = "评估我的运动能力" },
                                label = { Text("评估运动能力") }
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            SuggestionChip(
                                onClick = { userInput = "推荐适合的训练动作" },
                                label = { Text("推荐训练动作") }
                            )
                        }
                    }
                }

                items(messages) { message ->
                    ChatMessageBubble(message)
                }

                if (isLoading) {
                    item {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(8.dp),
                            horizontalArrangement = Arrangement.Start
                        ) {
                            Card(
                                colors = CardDefaults.cardColors(
                                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                                )
                            ) {
                                Row(
                                    modifier = Modifier.padding(12.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    CircularProgressIndicator(
                                        modifier = Modifier.size(16.dp),
                                        strokeWidth = 2.dp
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("AI正在思考...")
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // OpenClaw设置对话框
    if (showSettingsDialog) {
        AlertDialog(
            onDismissRequest = { showSettingsDialog = false },
            title = { Text("OpenClaw设置") },
            text = {
                Column {
                    Text(
                        "配置OpenClaw服务地址",
                        style = MaterialTheme.typography.bodyMedium,
                        modifier = Modifier.padding(bottom = 12.dp)
                    )
                    OutlinedTextField(
                        value = gatewayUrl,
                        onValueChange = { gatewayUrl = it },
                        label = { Text("服务地址") },
                        placeholder = { Text("http://localhost:8080") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        "示例: http://your-server:8080",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.setOpenClawGateway(gatewayUrl)
                        viewModel.checkOpenClawConnection()
                        showSettingsDialog = false
                    }
                ) {
                    Text("保存")
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

data class ChatMessage(
    val content: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis()
)

@Composable
fun ChatMessageBubble(message: ChatMessage) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = if (message.isUser) Arrangement.End else Arrangement.Start
    ) {
        if (!message.isUser) {
            Icon(
                Icons.Default.SmartToy,
                contentDescription = null,
                modifier = Modifier
                    .size(32.dp)
                    .padding(end = 8.dp),
                tint = MaterialTheme.colorScheme.primary
            )
        }

        Card(
            colors = CardDefaults.cardColors(
                containerColor = if (message.isUser)
                    MaterialTheme.colorScheme.primary
                else
                    MaterialTheme.colorScheme.surfaceVariant
            ),
            modifier = Modifier.widthIn(max = 280.dp)
        ) {
            Text(
                text = message.content,
                modifier = Modifier.padding(12.dp),
                color = if (message.isUser)
                    MaterialTheme.colorScheme.onPrimary
                else
                    MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        if (message.isUser) {
            Icon(
                Icons.Default.Person,
                contentDescription = null,
                modifier = Modifier
                    .size(32.dp)
                    .padding(start = 8.dp),
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}
