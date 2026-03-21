package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material.icons.filled.FiberManualRecord
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rehab.robotarm.data.model.RobotMode
import com.rehab.robotarm.ui.theme.MedicalBlue
import com.rehab.robotarm.ui.theme.MedicalGreen
import com.rehab.robotarm.ui.theme.MedicalOrange
import com.rehab.robotarm.ui.theme.MedicalRed
import com.rehab.robotarm.viewmodel.RobotViewModel

/**
 * 界面四：模式控制界面
 * 显示和切换机械臂模式，管理记忆动作
 */
@Composable
fun ModeControlScreen(viewModel: RobotViewModel = viewModel()) {
    val robotState by viewModel.robotState.collectAsState()
    val memoryActions by viewModel.memoryActions.collectAsState()
    var showAddDialog by remember { mutableStateOf(false) }
    var isExecutingAction by remember { mutableStateOf(false) }
    var isRecording by remember { mutableStateOf(false) }
    var showSaveRecordingDialog by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "模式控制",
                style = MaterialTheme.typography.headlineMedium
            )
        }

        // 当前模式显示
        item {
            CurrentModeCard(robotState.mode)
        }

        // 模式切换按钮
        item {
            ModeSwitchButtons(
                currentMode = robotState.mode,
                onModeChange = { mode -> viewModel.switchMode(mode) }
            )
        }

        // 模式说明
        item {
            ModeDescriptionCard()
        }

        // 主动模式录制功能
        if (robotState.mode == RobotMode.ACTIVE) {
            item {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = if (isRecording) MedicalRed.copy(alpha = 0.2f) else MedicalGreen.copy(alpha = 0.1f)
                    )
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Text(
                            text = "动作录制",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = if (isRecording) "正在录制患者的主动运动..." else "在主动模式下录制患者的运动轨迹",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            if (!isRecording) {
                                Button(
                                    onClick = {
                                        isRecording = true
                                        viewModel.startRecording()
                                    },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = MedicalRed
                                    )
                                ) {
                                    Icon(Icons.Default.FiberManualRecord, contentDescription = null)
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text("开始录制")
                                }
                            } else {
                                Button(
                                    onClick = {
                                        isRecording = false
                                        viewModel.stopRecording()
                                        showSaveRecordingDialog = true
                                    },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = MaterialTheme.colorScheme.error
                                    )
                                ) {
                                    Icon(Icons.Default.Stop, contentDescription = null)
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text("结束录制")
                                }
                            }
                        }
                    }
                }
            }
        }

        // 记忆模式管理（仅在记忆模式下显示）
        if (robotState.mode == RobotMode.MEMORY) {
            // 全局控制按钮
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = {
                            isExecutingAction = true
                            // 这里应该执行当前选中的动作
                        },
                        modifier = Modifier.weight(1f),
                        enabled = !isExecutingAction && memoryActions.isNotEmpty(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MedicalGreen
                        )
                    ) {
                        Icon(Icons.Default.PlayArrow, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("开始执行")
                    }

                    Button(
                        onClick = {
                            isExecutingAction = false
                            viewModel.stopMemoryAction()
                        },
                        modifier = Modifier.weight(1f),
                        enabled = isExecutingAction,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.error
                        )
                    ) {
                        Icon(Icons.Default.Stop, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("停止执行")
                    }
                }
            }

            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "记忆动作列表",
                        style = MaterialTheme.typography.titleLarge
                    )
                    IconButton(onClick = { showAddDialog = true }) {
                        Icon(Icons.Default.Add, contentDescription = "添加动作")
                    }
                }
            }

            items(memoryActions) { action ->
                MemoryActionCard(
                    action = action,
                    onExecute = {
                        isExecutingAction = true
                        viewModel.executeMemoryAction(action.id)
                    },
                    onDelete = { viewModel.deleteMemoryAction(action.id) }
                )
            }
        }
    }

    // 添加记忆动作对话框
    if (showAddDialog) {
        AddMemoryActionDialog(
            onDismiss = { showAddDialog = false },
            onConfirm = { name, description ->
                viewModel.createMemoryAction(name, description)
                showAddDialog = false
            }
        )
    }

    // 保存录制对话框
    if (showSaveRecordingDialog) {
        SaveRecordingDialog(
            onDismiss = { showSaveRecordingDialog = false },
            onConfirm = { name, description ->
                viewModel.saveRecording(name, description)
                showSaveRecordingDialog = false
            }
        )
    }
}

@Composable
fun CurrentModeCard(mode: RobotMode) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = when (mode) {
                RobotMode.ACTIVE -> MedicalGreen.copy(alpha = 0.2f)
                RobotMode.PASSIVE -> MedicalBlue.copy(alpha = 0.2f)
                RobotMode.ASSIST -> MedicalGreen.copy(alpha = 0.3f)
                RobotMode.RESIST -> MedicalRed.copy(alpha = 0.2f)
                RobotMode.MEMORY -> MedicalOrange.copy(alpha = 0.2f)
                RobotMode.GAME -> MedicalBlue.copy(alpha = 0.3f)
            }
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "当前模式",
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = when (mode) {
                    RobotMode.ACTIVE -> "主动模式"
                    RobotMode.PASSIVE -> "被动模式"
                    RobotMode.ASSIST -> "助力模式"
                    RobotMode.RESIST -> "阻力模式"
                    RobotMode.MEMORY -> "记忆模式"
                    RobotMode.GAME -> "游戏模式"
                },
                style = MaterialTheme.typography.headlineLarge,
                color = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
fun ModeSwitchButtons(
    currentMode: RobotMode,
    onModeChange: (RobotMode) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        ModeButton(
            text = "主动模式",
            description = "电机不使能，患者主动运动",
            isSelected = currentMode == RobotMode.ACTIVE,
            onClick = { onModeChange(RobotMode.ACTIVE) }
        )

        ModeButton(
            text = "被动模式",
            description = "电机使能，由App控制运动",
            isSelected = currentMode == RobotMode.PASSIVE,
            onClick = { onModeChange(RobotMode.PASSIVE) }
        )

        ModeButton(
            text = "记忆模式",
            description = "执行预设的记忆动作",
            isSelected = currentMode == RobotMode.MEMORY,
            onClick = { onModeChange(RobotMode.MEMORY) }
        )
    }
}

@Composable
fun ModeButton(
    text: String,
    description: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        colors = ButtonDefaults.buttonColors(
            containerColor = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant,
            contentColor = if (isSelected) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(vertical = 8.dp),
            horizontalAlignment = Alignment.Start
        ) {
            Text(text = text, style = MaterialTheme.typography.titleMedium)
            Text(text = description, style = MaterialTheme.typography.bodySmall)
        }
    }
}

@Composable
fun ModeDescriptionCard() {
    Card {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "模式说明",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            ModeDescriptionItem(
                title = "主动模式",
                description = "电机不使能，患者可以自由移动手臂。系统记录运动数据用于评估患者的主动运动能力。适用于康复初期评估和主动训练。"
            )

            Spacer(modifier = Modifier.height(12.dp))

            ModeDescriptionItem(
                title = "被动模式",
                description = "电机使能，由App远程控制机械臂运动。系统会自动限位保护，防止伤害患者。适用于被动康复训练。"
            )

            Spacer(modifier = Modifier.height(12.dp))

            ModeDescriptionItem(
                title = "记忆模式",
                description = "执行预先设定的康复动作序列。可以通过主动模式录制动作，或在App中手动规划动作路径。适用于重复性康复训练。"
            )
        }
    }
}

@Composable
fun ModeDescriptionItem(title: String, description: String) {
    Column {
        Text(
            text = title,
            style = MaterialTheme.typography.titleSmall,
            color = MaterialTheme.colorScheme.secondary
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = description,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun MemoryActionCard(
    action: com.rehab.robotarm.data.model.MemoryAction,
    onExecute: () -> Unit,
    onDelete: () -> Unit
) {
    Card {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = action.name,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = action.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "时长: ${action.duration / 1000}秒 | ${action.keyframes.size}个关键帧",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Row {
                IconButton(onClick = onExecute) {
                    Icon(
                        Icons.Default.PlayArrow,
                        contentDescription = "执行",
                        tint = MedicalGreen
                    )
                }
                IconButton(onClick = onDelete) {
                    Icon(
                        Icons.Default.Delete,
                        contentDescription = "删除",
                        tint = MaterialTheme.colorScheme.error
                    )
                }
            }
        }
    }
}

@Composable
fun AddMemoryActionDialog(
    onDismiss: () -> Unit,
    onConfirm: (String, String) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("添加记忆动作") },
        text = {
            Column {
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("动作名称") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = description,
                    onValueChange = { description = it },
                    label = { Text("动作描述") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 3
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onConfirm(name, description) },
                enabled = name.isNotBlank()
            ) {
                Text("确定")
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
fun SaveRecordingDialog(
    onDismiss: () -> Unit,
    onConfirm: (String, String) -> Unit
) {
    var name by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("保存录制动作") },
        text = {
            Column {
                Text(
                    "录制完成！请为这个动作命名并添加描述。",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                OutlinedTextField(
                    value = name,
                    onValueChange = { name = it },
                    label = { Text("动作名称") },
                    placeholder = { Text("例如：肩关节抬升训练") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = description,
                    onValueChange = { description = it },
                    label = { Text("动作描述") },
                    placeholder = { Text("例如：患者主动抬起手臂至90度") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 3
                )
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onConfirm(name, description) },
                enabled = name.isNotBlank()
            ) {
                Icon(Icons.Default.Save, contentDescription = null)
                Spacer(modifier = Modifier.width(4.dp))
                Text("保存")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("取消")
            }
        }
    )
}
