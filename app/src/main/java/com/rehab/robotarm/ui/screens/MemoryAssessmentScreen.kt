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
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.RobotViewModel
import kotlinx.coroutines.delay

/**
 * 评估测试模式界面 - 记忆模式子模块3
 * 执行标准化评估动作，生成康复能力报告
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MemoryAssessmentScreen(
    navController: NavController,
    viewModel: RobotViewModel
) {
    var selectedTest by remember { mutableStateOf<AssessmentTest?>(null) }
    var isRunning by remember { mutableStateOf(false) }
    var currentProgress by remember { mutableStateOf(0f) }
    var testResult by remember { mutableStateOf<AssessmentResult?>(null) }

    // 模拟测试进度
    LaunchedEffect(isRunning) {
        if (isRunning) {
            while (currentProgress < 1f) {
                delay(100)
                currentProgress += 0.01f
            }
            // 测试完成，生成结果
            testResult = AssessmentResult(
                testName = selectedTest?.name ?: "",
                romScore = (60..95).random().toFloat(),
                strengthScore = (55..90).random().toFloat(),
                coordinationScore = (65..95).random().toFloat(),
                overallScore = (60..92).random().toFloat()
            )
            isRunning = false
            currentProgress = 0f
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("评估测试模式") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, "返回")
                    }
                }
            )
        }
    ) { padding ->
        if (selectedTest == null) {
            // 测试类型选择
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.primaryContainer
                        )
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Icon(
                                Icons.Default.Assessment,
                                contentDescription = null,
                                modifier = Modifier.size(48.dp),
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                "标准化康复评估",
                                style = MaterialTheme.typography.headlineSmall,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                "通过标准化动作测试，全面评估患者的康复能力，生成详细的评估报告",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        }
                    }
                }

                item {
                    Text(
                        "选择评估类型",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }

                items(getAssessmentTests()) { test ->
                    AssessmentTestCard(
                        test = test,
                        onClick = { selectedTest = test }
                    )
                }
            }
        } else if (isRunning) {
            // 测试进行中
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    "正在进行${selectedTest!!.name}",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(32.dp))

                CircularProgressIndicator(
                    progress = { currentProgress },
                    modifier = Modifier.size(120.dp),
                    strokeWidth = 8.dp
                )

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    "${(currentProgress * 100).toInt()}%",
                    style = MaterialTheme.typography.displayMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )

                Spacer(modifier = Modifier.height(24.dp))

                Text(
                    selectedTest!!.instruction,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Spacer(modifier = Modifier.height(48.dp))

                OutlinedButton(
                    onClick = {
                        isRunning = false
                        currentProgress = 0f
                        selectedTest = null
                    }
                ) {
                    Icon(Icons.Default.Stop, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("停止测试")
                }
            }
        } else if (testResult != null) {
            // 显示测试结果
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.secondaryContainer
                        )
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Icon(
                                Icons.Default.CheckCircle,
                                contentDescription = null,
                                modifier = Modifier.size(64.dp),
                                tint = Color(0xFF4CAF50)
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                "测试完成",
                                style = MaterialTheme.typography.headlineMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                testResult!!.testName,
                                style = MaterialTheme.typography.titleMedium
                            )
                        }
                    }
                }

                item {
                    Text(
                        "评估结果",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }

                item {
                    Card {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            AssessmentScoreItem("运动范围 (ROM)", testResult!!.romScore)
                            AssessmentScoreItem("力量评分", testResult!!.strengthScore)
                            AssessmentScoreItem("协调性", testResult!!.coordinationScore)

                            Divider()

                            AssessmentScoreItem(
                                "综合评分",
                                testResult!!.overallScore,
                                isOverall = true
                            )
                        }
                    }
                }

                item {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.tertiaryContainer
                        )
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    Icons.Default.Lightbulb,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.tertiary
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    "AI康复建议",
                                    style = MaterialTheme.typography.titleMedium,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                getRecommendation(testResult!!.overallScore),
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                }

                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        OutlinedButton(
                            onClick = {
                                testResult = null
                                selectedTest = null
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(Icons.Default.Replay, contentDescription = null)
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("重新测试")
                        }

                        Button(
                            onClick = {
                                // 保存报告
                                navController.navigateUp()
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Icon(Icons.Default.Save, contentDescription = null)
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("保存报告")
                        }
                    }
                }
            }
        } else {
            // 测试准备界面
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Text(
                            selectedTest!!.name,
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            selectedTest!!.description,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }

                Card {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp)
                    ) {
                        Text(
                            "测试说明",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            selectedTest!!.instruction,
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            InfoChipAssessment(Icons.Default.Timer, "${selectedTest!!.duration}分钟")
                            InfoChipAssessment(Icons.Default.FitnessCenter, "${selectedTest!!.exercises}个动作")
                        }
                    }
                }

                Spacer(modifier = Modifier.weight(1f))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = { selectedTest = null },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("取消")
                    }

                    Button(
                        onClick = { isRunning = true },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.PlayArrow, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("开始测试")
                    }
                }
            }
        }
    }
}

@Composable
fun AssessmentTestCard(
    test: AssessmentTest,
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
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                test.icon,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    test.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    test.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    AssistChip(
                        onClick = { },
                        label = { Text("${test.duration}分钟") },
                        leadingIcon = {
                            Icon(
                                Icons.Default.Timer,
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

@Composable
fun AssessmentScoreItem(label: String, score: Float, isOverall: Boolean = false) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                label,
                style = if (isOverall) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyLarge,
                fontWeight = if (isOverall) FontWeight.Bold else FontWeight.Normal
            )
            Text(
                String.format("%.1f", score),
                style = if (isOverall) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Bold,
                color = getMemoryAssessmentScoreColor(score)
            )
        }
        LinearProgressIndicator(
            progress = { score / 100f },
            modifier = Modifier.fillMaxWidth(),
            color = getMemoryAssessmentScoreColor(score)
        )
    }
}

@Composable
fun InfoChipAssessment(icon: androidx.compose.ui.graphics.vector.ImageVector, text: String) {
    Surface(
        color = MaterialTheme.colorScheme.secondaryContainer,
        shape = MaterialTheme.shapes.small
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                icon,
                contentDescription = null,
                modifier = Modifier.size(16.dp),
                tint = MaterialTheme.colorScheme.onSecondaryContainer
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text,
                style = MaterialTheme.typography.labelMedium
            )
        }
    }
}

fun getMemoryAssessmentScoreColor(score: Float): Color {
    return when {
        score >= 80 -> Color(0xFF4CAF50)
        score >= 60 -> Color(0xFFFFC107)
        score >= 40 -> Color(0xFFFF9800)
        else -> Color(0xFFF44336)
    }
}

fun getRecommendation(score: Float): String {
    return when {
        score >= 80 -> "康复效果良好！建议继续保持当前训练强度，可适当增加训练难度以进一步提升能力。"
        score >= 60 -> "康复进展正常。建议增加训练频率，重点加强力量和协调性训练。"
        score >= 40 -> "需要加强训练。建议在专业指导下进行针对性康复训练，注意循序渐进。"
        else -> "康复能力较弱。建议咨询医生，制定个性化康复方案，从基础训练开始。"
    }
}

data class AssessmentTest(
    val name: String,
    val description: String,
    val instruction: String,
    val duration: Int,
    val exercises: Int,
    val icon: androidx.compose.ui.graphics.vector.ImageVector
)

data class AssessmentResult(
    val testName: String,
    val romScore: Float,
    val strengthScore: Float,
    val coordinationScore: Float,
    val overallScore: Float
)

fun getAssessmentTests(): List<AssessmentTest> {
    return listOf(
        AssessmentTest(
            name = "ROM测试",
            description = "测量关节运动范围，评估患者的活动能力",
            instruction = "请尽可能抬高手臂，系统将记录您的最大运动角度",
            duration = 5,
            exercises = 3,
            icon = Icons.Default.OpenInFull
        ),
        AssessmentTest(
            name = "力量测试",
            description = "评估肌肉力量和耐力水平",
            instruction = "请对抗机械臂的阻力，尽力保持姿势",
            duration = 8,
            exercises = 5,
            icon = Icons.Default.FitnessCenter
        ),
        AssessmentTest(
            name = "协调性测试",
            description = "评估运动协调性和控制能力",
            instruction = "请跟随系统指示完成一系列精确动作",
            duration = 10,
            exercises = 8,
            icon = Icons.Default.Adjust
        ),
        AssessmentTest(
            name = "综合评估",
            description = "全面评估ROM、力量和协调性",
            instruction = "完整的康复能力评估，包含所有测试项目",
            duration = 20,
            exercises = 15,
            icon = Icons.Default.Assessment
        )
    )
}
