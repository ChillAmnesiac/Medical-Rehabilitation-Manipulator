package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import kotlinx.coroutines.delay

/**
 * 自动训练界面 - 被动模式
 * 执行预设的自动训练序列
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AutoTrainScreen(
    navController: NavController,
    viewModel: RobotViewModel = viewModel()
) {
    val robotState by viewModel.robotState.collectAsState()
    var selectedProgram by remember { mutableStateOf<TrainingProgram?>(null) }
    var isTraining by remember { mutableStateOf(false) }
    var currentRepetition by remember { mutableStateOf(0) }
    var totalRepetitions by remember { mutableStateOf(10) }
    var trainingSpeed by remember { mutableStateOf(50f) }

    val trainingPrograms = remember {
        listOf(
            TrainingProgram(
                id = 1,
                name = "肩关节屈伸训练",
                description = "改善肩关节活动度，增强肩部肌肉力量",
                duration = 300,
                difficulty = "简单"
            ),
            TrainingProgram(
                id = 2,
                name = "肘关节屈伸训练",
                description = "恢复肘关节功能，提高手臂灵活性",
                duration = 240,
                difficulty = "简单"
            ),
            TrainingProgram(
                id = 3,
                name = "全臂协调训练",
                description = "综合训练肩肘协调，提升整体运动能力",
                duration = 480,
                difficulty = "中等"
            ),
            TrainingProgram(
                id = 4,
                name = "力量强化训练",
                description = "增加阻力训练，强化肌肉力量",
                duration = 360,
                difficulty = "困难"
            )
        )
    }

    // 训练进度
    LaunchedEffect(isTraining) {
        if (isTraining && currentRepetition < totalRepetitions) {
            while (isTraining && currentRepetition < totalRepetitions) {
                delay(3000) // 每次重复3秒
                currentRepetition++
            }
            if (currentRepetition >= totalRepetitions) {
                isTraining = false
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("自动训练") },
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
        ) {
            if (selectedProgram == null) {
                // 训练程序选择
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    item {
                        Text(
                            text = "选择训练程序",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )
                    }

                    items(trainingPrograms) { program ->
                        TrainingProgramCard(
                            program = program,
                            onClick = { selectedProgram = program }
                        )
                    }
                }
            } else {
                // 训练执行界面
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // 当前程序信息
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = if (isTraining)
                                Color(0xFF4CAF50).copy(alpha = 0.2f)
                            else
                                MaterialTheme.colorScheme.surfaceVariant
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
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = selectedProgram!!.name,
                                        style = MaterialTheme.typography.titleLarge,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Text(
                                        text = selectedProgram!!.description,
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                                IconButton(
                                    onClick = {
                                        selectedProgram = null
                                        isTraining = false
                                        currentRepetition = 0
                                    }
                                ) {
                                    Icon(Icons.Default.Close, "关闭")
                                }
                            }
                        }
                    }

                    // 训练进度
                    Card {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Text(
                                text = "训练进度",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )

                            Spacer(modifier = Modifier.height(12.dp))

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text("重复次数")
                                Text(
                                    "$currentRepetition / $totalRepetitions",
                                    fontWeight = FontWeight.Bold
                                )
                            }

                            Spacer(modifier = Modifier.height(8.dp))

                            LinearProgressIndicator(
                                progress = { currentRepetition.toFloat() / totalRepetitions },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(8.dp),
                            )
                        }
                    }

                    // 训练参数
                    Card {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Text(
                                text = "训练参数",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )

                            Spacer(modifier = Modifier.height(12.dp))

                            // 重复次数设置
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text("重复次数")
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    IconButton(
                                        onClick = { if (totalRepetitions > 1) totalRepetitions-- },
                                        enabled = !isTraining
                                    ) {
                                        Icon(Icons.Default.Remove, "减少")
                                    }
                                    Text(
                                        "$totalRepetitions",
                                        style = MaterialTheme.typography.titleLarge,
                                        fontWeight = FontWeight.Bold
                                    )
                                    IconButton(
                                        onClick = { if (totalRepetitions < 50) totalRepetitions++ },
                                        enabled = !isTraining
                                    ) {
                                        Icon(Icons.Default.Add, "增加")
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(12.dp))

                            // 速度设置
                            Text("训练速度: ${trainingSpeed.toInt()}%")
                            Slider(
                                value = trainingSpeed,
                                onValueChange = { trainingSpeed = it },
                                valueRange = 20f..100f,
                                enabled = !isTraining
                            )
                        }
                    }

                    // 实时数据
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
                            }
                        }
                    }

                    Spacer(modifier = Modifier.weight(1f))

                    // 控制按钮
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        if (!isTraining) {
                            Button(
                                onClick = {
                                    isTraining = true
                                    currentRepetition = 0
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
                                onClick = { isTraining = false },
                                modifier = Modifier.weight(1f),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = MaterialTheme.colorScheme.error
                                )
                            ) {
                                Icon(Icons.Default.Stop, contentDescription = null)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("停止训练")
                            }
                        }

                        OutlinedButton(
                            onClick = {
                                currentRepetition = 0
                                isTraining = false
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
        }
    }
}

data class TrainingProgram(
    val id: Int,
    val name: String,
    val description: String,
    val duration: Int, // 秒
    val difficulty: String
)

@Composable
fun TrainingProgramCard(
    program: TrainingProgram,
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
                    text = program.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = program.description,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    AssistChip(
                        onClick = { },
                        label = { Text("${program.duration / 60}分钟") },
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
                        label = { Text(program.difficulty) },
                        leadingIcon = {
                            Icon(
                                Icons.Default.TrendingUp,
                                contentDescription = null,
                                modifier = Modifier.size(16.dp)
                            )
                        }
                    )
                }
            }

            Icon(
                Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
