package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.RobotViewModel
import kotlinx.coroutines.delay

/**
 * 动作回放界面 - 记忆模式子模块1
 * 回放已保存的记忆动作，支持单次回放、循环回放和速度调节
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ActionReplayScreen(
    navController: NavController,
    viewModel: RobotViewModel = viewModel()
) {
    val memoryActions by viewModel.memoryActions.collectAsState()
    var selectedAction by remember { mutableStateOf<com.rehab.robotarm.data.model.MemoryAction?>(null) }
    var isPlaying by remember { mutableStateOf(false) }
    var currentProgress by remember { mutableStateOf(0f) }
    var playbackSpeed by remember { mutableStateOf(1f) }
    var repeatCount by remember { mutableStateOf(1) }
    var currentRepeat by remember { mutableStateOf(0) }
    var mirrorMode by remember { mutableStateOf(false) }

    // 回放进度 - 支持循环回放
    LaunchedEffect(isPlaying) {
        if (isPlaying && selectedAction != null) {
            currentRepeat = 0
            while (isPlaying && currentRepeat < repeatCount) {
                val duration = selectedAction!!.duration
                val step = 0.01f / playbackSpeed
                currentProgress = 0f
                while (isPlaying && currentProgress < 1f) {
                    delay((duration * step).toLong())
                    currentProgress += step
                }
                if (currentProgress >= 1f) {
                    currentRepeat++
                    if (currentRepeat < repeatCount) {
                        delay(1000) // 每次重复之间休息1秒
                    }
                }
            }
            if (currentRepeat >= repeatCount) {
                isPlaying = false
                currentProgress = 0f
                currentRepeat = 0
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("动作回放") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, "返回")
                    }
                }
            )
        }
    ) { padding ->
        if (selectedAction == null) {
            // 动作列表
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                item {
                    Text(
                        text = "已保存的动作",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                }

                if (memoryActions.isEmpty()) {
                    item {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surfaceVariant
                            )
                        ) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(32.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Icon(
                                    Icons.Default.FolderOff,
                                    contentDescription = null,
                                    modifier = Modifier.size(64.dp),
                                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                                Spacer(modifier = Modifier.height(16.dp))
                                Text(
                                    "暂无保存的动作",
                                    style = MaterialTheme.typography.titleMedium
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    "在主动模式下录制动作后可在此回放",
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }
                } else {
                    items(memoryActions) { action ->
                        MemoryActionListCard(
                            action = action,
                            onClick = { selectedAction = action }
                        )
                    }
                }
            }
        } else {
            // 回放控制界面
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 动作信息
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
                                text = selectedAction!!.name,
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = selectedAction!!.description,
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        IconButton(onClick = {
                            selectedAction = null
                            isPlaying = false
                            currentProgress = 0f
                        }) {
                            Icon(Icons.Default.Close, "关闭")
                        }
                    }
                }

                // 回放进度
                Card {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "回放进度",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "${(currentProgress * 100).toInt()}%",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        LinearProgressIndicator(
                            progress = { currentProgress },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(8.dp),
                        )

                        Spacer(modifier = Modifier.height(8.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                "0:00",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Text(
                                "${selectedAction!!.duration / 1000}秒",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                // 轨迹可视化
                Card {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Text(
                            text = "动作轨迹",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(8.dp))

                        Canvas(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(200.dp)
                        ) {
                            val width = size.width
                            val height = size.height

                            // 绘制坐标轴
                            drawLine(
                                color = Color.Gray,
                                start = Offset(0f, height / 2),
                                end = Offset(width, height / 2),
                                strokeWidth = 2f
                            )
                            drawLine(
                                color = Color.Gray,
                                start = Offset(width / 2, 0f),
                                end = Offset(width / 2, height),
                                strokeWidth = 2f
                            )

                            // 绘制轨迹
                            if (selectedAction!!.keyframes.size > 1) {
                                val path = Path()
                                val firstFrame = selectedAction!!.keyframes.first()
                                path.moveTo(
                                    (firstFrame.shoulderAngle / 180f) * width,
                                    height - (firstFrame.elbowAngle / 180f) * height
                                )

                                selectedAction!!.keyframes.forEach { frame ->
                                    path.lineTo(
                                        (frame.shoulderAngle / 180f) * width,
                                        height - (frame.elbowAngle / 180f) * height
                                    )
                                }

                                drawPath(
                                    path = path,
                                    color = Color(0xFF2196F3),
                                    style = Stroke(width = 3f)
                                )

                                // 绘制当前位置
                                val currentIndex = (currentProgress * (selectedAction!!.keyframes.size - 1)).toInt()
                                if (currentIndex < selectedAction!!.keyframes.size) {
                                    val currentFrame = selectedAction!!.keyframes[currentIndex]
                                    drawCircle(
                                        color = Color(0xFFFF5722),
                                        radius = 10f,
                                        center = Offset(
                                            (currentFrame.shoulderAngle / 180f) * width,
                                            height - (currentFrame.elbowAngle / 180f) * height
                                        )
                                    )
                                }
                            }
                        }
                    }
                }

                // 回放速度控制
                Card {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "回放速度",
                                style = MaterialTheme.typography.titleMedium
                            )
                            Text(
                                text = "${playbackSpeed}x",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        Slider(
                            value = playbackSpeed,
                            onValueChange = { playbackSpeed = it },
                            valueRange = 0.5f..2f,
                            steps = 2,
                            enabled = !isPlaying
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("0.5x", style = MaterialTheme.typography.bodySmall)
                            Text("1x", style = MaterialTheme.typography.bodySmall)
                            Text("1.5x", style = MaterialTheme.typography.bodySmall)
                            Text("2x", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                }

                // 循环回放设置
                Card {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "重复次数",
                                style = MaterialTheme.typography.titleMedium
                            )
                            Text(
                                text = if (isPlaying) "${currentRepeat + 1}/$repeatCount" else "$repeatCount 次",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        Slider(
                            value = repeatCount.toFloat(),
                            onValueChange = { repeatCount = it.toInt() },
                            valueRange = 1f..10f,
                            steps = 8,
                            enabled = !isPlaying
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("1次", style = MaterialTheme.typography.bodySmall)
                            Text("5次", style = MaterialTheme.typography.bodySmall)
                            Text("10次", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                }

                // 镜像模式开关
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
                                text = "镜像模式",
                                style = MaterialTheme.typography.titleMedium
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "左右对称训练（角度镜像）",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Switch(
                            checked = mirrorMode,
                            onCheckedChange = { mirrorMode = it },
                            enabled = !isPlaying
                        )
                    }
                }

                Spacer(modifier = Modifier.weight(1f))

                // 控制按钮
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    if (!isPlaying) {
                        Button(
                            onClick = {
                                isPlaying = true
                                if (currentProgress >= 1f) {
                                    currentProgress = 0f
                                }
                            },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFF4CAF50)
                            )
                        ) {
                            Icon(Icons.Default.PlayArrow, contentDescription = null)
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("播放")
                        }
                    } else {
                        Button(
                            onClick = { isPlaying = false },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFFFC107)
                            )
                        ) {
                            Icon(Icons.Default.Pause, contentDescription = null)
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("暂停")
                        }
                    }

                    OutlinedButton(
                        onClick = {
                            isPlaying = false
                            currentProgress = 0f
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.Replay, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("重播")
                    }
                }
            }
        }
    }
}

@Composable
fun MemoryActionListCard(
    action: com.rehab.robotarm.data.model.MemoryAction,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth()
    ) {
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
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = action.description,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    AssistChip(
                        onClick = { },
                        label = { Text("${action.duration / 1000}秒") },
                        leadingIcon = {
                            Icon(
                                Icons.Default.Timer,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    )
                    AssistChip(
                        onClick = { },
                        label = { Text("${action.keyframes.size}帧") },
                        leadingIcon = {
                            Icon(
                                Icons.Default.VideoLibrary,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    )
                }
            }

            Icon(
                Icons.Default.PlayCircle,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}
