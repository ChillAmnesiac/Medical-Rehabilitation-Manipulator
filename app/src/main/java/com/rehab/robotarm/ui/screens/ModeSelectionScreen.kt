package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.rehab.robotarm.data.model.*
import com.rehab.robotarm.viewmodel.RobotViewModel

/**
 * 统一的模式选择界面
 * 三级结构：主模式 -> 子模式 -> 具体训练
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ModeSelectionScreen(
    navController: NavController,
    viewModel: RobotViewModel
) {
    val robotState by viewModel.robotState.collectAsState()
    var selectedMainMode by remember { mutableStateOf(robotState.mainMode) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("选择训练模式") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 主模式选择
            Text(
                text = "选择主模式",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                MainModeCard(
                    title = "主动模式",
                    icon = Icons.Default.DirectionsRun,
                    description = "患者主导运动",
                    isSelected = selectedMainMode == MainMode.ACTIVE,
                    onClick = { selectedMainMode = MainMode.ACTIVE },
                    modifier = Modifier.weight(1f)
                )
                MainModeCard(
                    title = "被动模式",
                    icon = Icons.Default.Accessibility,
                    description = "系统主导运动",
                    isSelected = selectedMainMode == MainMode.PASSIVE,
                    onClick = { selectedMainMode = MainMode.PASSIVE },
                    modifier = Modifier.weight(1f)
                )
                MainModeCard(
                    title = "记忆模式",
                    icon = Icons.Default.Replay,
                    description = "执行预设动作",
                    isSelected = selectedMainMode == MainMode.MEMORY,
                    onClick = { selectedMainMode = MainMode.MEMORY },
                    modifier = Modifier.weight(1f)
                )
            }

            Divider()

            // 子模式选择
            Text(
                text = "选择子模式",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )

            when (selectedMainMode) {
                MainMode.ACTIVE -> ActiveSubModeSelection(navController, viewModel)
                MainMode.PASSIVE -> PassiveSubModeSelection(navController, viewModel)
                MainMode.MEMORY -> MemorySubModeSelection(navController, viewModel)
            }
        }
    }
}

@Composable
fun MainModeCard(
    title: String,
    icon: ImageVector,
    description: String,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onClick,
        modifier = modifier.height(140.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected)
                MaterialTheme.colorScheme.primaryContainer
            else
                MaterialTheme.colorScheme.surfaceVariant
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isSelected) 8.dp else 2.dp
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(40.dp),
                tint = if (isSelected)
                    MaterialTheme.colorScheme.primary
                else
                    MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = description,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun ActiveSubModeSelection(navController: NavController, viewModel: RobotViewModel) {
    val robotState by viewModel.robotState.collectAsState()

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        SubModeCard(
            title = "标准主动模式",
            icon = Icons.Default.FitnessCenter,
            description = "电机不使能，患者自由运动，记录运动数据评估能力",
            onClick = {
                navController.navigate("active_standard")
            },
            isActive = robotState.mainMode == MainMode.ACTIVE && robotState.activeSubMode == ActiveSubMode.STANDARD,
            onActivate = {
                viewModel.setMode(MainMode.ACTIVE, ActiveSubMode.STANDARD)
            }
        )

        SubModeCard(
            title = "AI助力模式",
            icon = Icons.Default.Psychology,
            description = "AI实时分析EMG信号，预测运动意图并提供智能助力",
            onClick = {
                navController.navigate("active_ai_assist")
            },
            isActive = robotState.mainMode == MainMode.ACTIVE && robotState.activeSubMode == ActiveSubMode.AI_ASSIST,
            onActivate = {
                viewModel.setMode(MainMode.ACTIVE, ActiveSubMode.AI_ASSIST)
            }
        )

        SubModeCard(
            title = "游戏化训练模式",
            icon = Icons.Default.SportsEsports,
            description = "通过趣味游戏进行康复训练，提高患者积极性",
            onClick = {
                navController.navigate("game_selection")
            },
            isActive = robotState.mainMode == MainMode.ACTIVE && robotState.activeSubMode == ActiveSubMode.GAME,
            onActivate = {
                viewModel.setMode(MainMode.ACTIVE, ActiveSubMode.GAME)
            }
        )
    }
}

@Composable
fun PassiveSubModeSelection(navController: NavController, viewModel: RobotViewModel) {
    val robotState by viewModel.robotState.collectAsState()

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        SubModeCard(
            title = "手动控制模式",
            icon = Icons.Default.TouchApp,
            description = "通过App手动控制机械臂运动，实时调整角度和速度",
            onClick = {
                navController.navigate("robot_control")
            },
            isActive = robotState.mainMode == MainMode.PASSIVE && robotState.passiveSubMode == PassiveSubMode.MANUAL,
            onActivate = {
                viewModel.setMode(MainMode.PASSIVE, passiveSubMode = PassiveSubMode.MANUAL)
            }
        )

        SubModeCard(
            title = "自动训练模式",
            icon = Icons.Default.AutoMode,
            description = "系统自动执行预设的训练方案，无需人工干预",
            onClick = {
                navController.navigate("passive_auto_train")
            },
            isActive = robotState.mainMode == MainMode.PASSIVE && robotState.passiveSubMode == PassiveSubMode.AUTO_TRAIN,
            onActivate = {
                viewModel.setMode(MainMode.PASSIVE, passiveSubMode = PassiveSubMode.AUTO_TRAIN)
            }
        )

        SubModeCard(
            title = "远程控制模式",
            icon = Icons.Default.Cloud,
            description = "医生通过远程连接实时控制和监督训练过程",
            onClick = {
                navController.navigate("passive_remote")
            },
            isActive = robotState.mainMode == MainMode.PASSIVE && robotState.passiveSubMode == PassiveSubMode.REMOTE,
            onActivate = {
                viewModel.setMode(MainMode.PASSIVE, passiveSubMode = PassiveSubMode.REMOTE)
            }
        )
    }
}

@Composable
fun MemorySubModeSelection(navController: NavController, viewModel: RobotViewModel) {
    val robotState by viewModel.robotState.collectAsState()

    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        SubModeCard(
            title = "动作回放模式",
            icon = Icons.Default.Replay,
            description = "回放之前录制的康复动作，支持单次回放、循环回放和速度调节",
            onClick = {
                navController.navigate("action_replay")
            },
            isActive = robotState.mainMode == MainMode.MEMORY && robotState.memorySubMode == MemorySubMode.REPLAY,
            onActivate = {
                viewModel.setMode(MainMode.MEMORY, memorySubMode = MemorySubMode.REPLAY)
            }
        )

        SubModeCard(
            title = "训练计划模式",
            icon = Icons.Default.CalendarMonth,
            description = "执行每日计划、周计划或AI生成的个性化训练计划",
            onClick = {
                navController.navigate("training_plan")
            },
            isActive = robotState.mainMode == MainMode.MEMORY && robotState.memorySubMode == MemorySubMode.PLAN,
            onActivate = {
                viewModel.setMode(MainMode.MEMORY, memorySubMode = MemorySubMode.PLAN)
            }
        )

        SubModeCard(
            title = "评估测试模式",
            icon = Icons.Default.Assessment,
            description = "执行ROM测试、力量测试和协调性测试，生成康复能力报告",
            onClick = {
                navController.navigate("memory_assessment")
            },
            isActive = robotState.mainMode == MainMode.MEMORY && robotState.memorySubMode == MemorySubMode.ASSESSMENT,
            onActivate = {
                viewModel.setMode(MainMode.MEMORY, memorySubMode = MemorySubMode.ASSESSMENT)
            }
        )
    }
}

@Composable
fun SubModeCard(
    title: String,
    icon: ImageVector,
    description: String,
    onClick: () -> Unit,
    isActive: Boolean = false,
    onActivate: (() -> Unit)? = null
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isActive)
                MaterialTheme.colorScheme.primaryContainer
            else
                MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(48.dp),
                    tint = if (isActive)
                        MaterialTheme.colorScheme.primary
                    else
                        MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.width(16.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = title,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        if (isActive) {
                            Spacer(modifier = Modifier.width(8.dp))
                            Surface(
                                color = MaterialTheme.colorScheme.primary,
                                shape = MaterialTheme.shapes.small
                            ) {
                                Text(
                                    text = "当前模式",
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onPrimary
                                )
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = description,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // 按钮行
            Spacer(modifier = Modifier.height(12.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // 开启模式按钮
                if (onActivate != null) {
                    Button(
                        onClick = onActivate,
                        modifier = Modifier.weight(1f),
                        enabled = !isActive
                    ) {
                        Icon(
                            imageVector = if (isActive) Icons.Default.Check else Icons.Default.PlayArrow,
                            contentDescription = null,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(if (isActive) "已开启" else "开启模式")
                    }
                }

                // 查看详情按钮
                OutlinedButton(
                    onClick = onClick,
                    modifier = Modifier.weight(1f)
                ) {
                    Text("查看详情")
                    Spacer(modifier = Modifier.width(4.dp))
                    Icon(
                        imageVector = Icons.Default.ChevronRight,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}
