package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.rehab.robotarm.data.model.GameType
import com.rehab.robotarm.viewmodel.GameViewModel
import com.rehab.robotarm.viewmodel.GameState
import com.rehab.robotarm.ui.games.FruitNinjaGame as FruitNinjaGameImpl
import com.rehab.robotarm.ui.games.WhackAMoleGame as WhackAMoleGameImpl
import com.rehab.robotarm.ui.games.RhythmMasterGame as RhythmMasterGameImpl
import com.rehab.robotarm.ui.games.FlightSimGame as FlightSimGameImpl
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RehabGameScreen(
    navController: NavController,
    viewModel: GameViewModel,
    gameType: GameType
) {
    val targets by viewModel.targets.collectAsState()
    val score by viewModel.score.collectAsState()
    val gameState by viewModel.gameState.collectAsState()
    val currentAngle by viewModel.currentAngle.collectAsState()
    val currentPosition by viewModel.currentPosition.collectAsState()
    val timeRemaining by viewModel.timeRemaining.collectAsState()
    var showGameMenu by remember { mutableStateOf(false) }

    // 倒计时
    LaunchedEffect(gameState) {
        if (gameState is GameState.Playing) {
            while (timeRemaining > 0) {
                delay(1000)
                viewModel.decrementTime()
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(getGameTitle(gameType)) },
                navigationIcon = {
                    IconButton(onClick = { showGameMenu = true }) {
                        Icon(Icons.Default.Menu, contentDescription = "菜单")
                    }
                },
                actions = {
                    IconButton(onClick = { navController.navigate("game_selection") }) {
                        Icon(Icons.Default.SwapHoriz, contentDescription = "切换游戏")
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(Color(0xFF1A237E))
        ) {
            when (gameState) {
                is GameState.Idle -> {
                    GameStartScreen(
                        gameType = gameType,
                        onStart = { difficulty ->
                            viewModel.startGame(difficulty, gameType)
                        }
                    )
                }
                is GameState.Playing -> {
                    when (gameType) {
                        GameType.FRUIT_NINJA -> FruitNinjaGameImpl(
                            targets = targets,
                            currentPosition = currentPosition,
                            score = score,
                            timeRemaining = timeRemaining,
                            onTargetHit = { }
                        )
                        GameType.WHACK_A_MOLE -> WhackAMoleGameImpl(
                            targets = targets,
                            currentPosition = currentPosition,
                            score = score,
                            timeRemaining = timeRemaining,
                            onTargetHit = { }
                        )
                        GameType.RHYTHM_MASTER -> RhythmMasterGameImpl(
                            targets = targets,
                            currentPosition = currentPosition,
                            score = score,
                            timeRemaining = timeRemaining,
                            onTargetHit = { }
                        )
                        GameType.FLIGHT_SIM -> FlightSimGameImpl(
                            targets = targets,
                            currentPosition = currentPosition,
                            score = score,
                            timeRemaining = timeRemaining
                        )
                    }
                }
                is GameState.Finished -> {
                    GameFinishedScreen(
                        score = score,
                        onRestart = { viewModel.startGame(gameType = gameType) },
                        onChangeGame = { navController.navigate("game_selection") },
                        onExit = { navController.navigateUp() }
                    )
                }
                else -> {}
            }
        }

        // 游戏菜单
        if (showGameMenu) {
            GameMenuDialog(
                onDismiss = { showGameMenu = false },
                onPause = { viewModel.pauseGame() },
                onResume = { viewModel.resumeGame() },
                onRestart = { viewModel.startGame(gameType = gameType) },
                onChangeGame = {
                    showGameMenu = false
                    navController.navigate("game_selection")
                },
                onExit = { navController.navigateUp() }
            )
        }
    }
}

fun getGameTitle(gameType: GameType): String {
    return when (gameType) {
        GameType.FRUIT_NINJA -> "水果忍者"
        GameType.WHACK_A_MOLE -> "打地鼠"
        GameType.RHYTHM_MASTER -> "节奏大师"
        GameType.FLIGHT_SIM -> "飞行模拟"
    }
}

@Composable
fun GameStartScreen(
    gameType: GameType,
    onStart: (String) -> Unit
) {
    var selectedDifficulty by remember { mutableStateOf("medium") }

    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = when (gameType) {
                GameType.FRUIT_NINJA -> Icons.Default.Restaurant
                GameType.WHACK_A_MOLE -> Icons.Default.TouchApp
                GameType.RHYTHM_MASTER -> Icons.Default.MusicNote
                GameType.FLIGHT_SIM -> Icons.Default.Flight
            },
            contentDescription = null,
            modifier = Modifier.size(120.dp),
            tint = Color.White
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = getGameTitle(gameType),
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = getGameDescription(gameType),
            fontSize = 16.sp,
            color = Color.White.copy(alpha = 0.8f)
        )

        Spacer(modifier = Modifier.height(48.dp))

        Text("选择难度", color = Color.White, fontWeight = FontWeight.Bold)

        Spacer(modifier = Modifier.height(16.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            listOf("easy" to "简单", "medium" to "中等", "hard" to "困难").forEach { (difficulty, label) ->
                FilterChip(
                    selected = selectedDifficulty == difficulty,
                    onClick = { selectedDifficulty = difficulty },
                    label = { Text(label) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = Color.White,
                        selectedLabelColor = Color(0xFF1A237E)
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(48.dp))

        Button(
            onClick = { onStart(selectedDifficulty) },
            modifier = Modifier
                .width(200.dp)
                .height(56.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.White,
                contentColor = Color(0xFF1A237E)
            )
        ) {
            Text("开始游戏", fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun GamePlayingScreen(
    targets: List<com.rehab.robotarm.viewmodel.GameTarget>,
    currentAngle: Float,
    score: Int,
    timeRemaining: Int
) {
    Column(modifier = Modifier.fillMaxSize()) {
        // 顶部信息栏
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            // 分数
            Card(
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(Icons.Default.Star, contentDescription = null, tint = Color(0xFFFFD700))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "$score",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            // 倒计时
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = if (timeRemaining <= 10) Color(0xFFF44336) else Color.White
                )
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.Timer,
                        contentDescription = null,
                        tint = if (timeRemaining <= 10) Color.White else Color(0xFF1A237E)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "$timeRemaining",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = if (timeRemaining <= 10) Color.White else Color.Black
                    )
                }
            }
        }

        // 游戏区域
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
        ) {
            // 绘制目标（支持2D坐标）
            Canvas(modifier = Modifier.fillMaxSize()) {
                val width = size.width
                val height = size.height

                targets.forEach { target ->
                    // 如果有2D坐标，使用坐标绘制；否则使用角度
                    val (x, y) = if (target.position != null) {
                        // 将物理坐标映射到屏幕坐标
                        // 假设工作空间：X: 0-0.6米, Y: 0-0.5米
                        val screenX = (target.position.x / 0.6f) * width
                        val screenY = height - (target.position.y / 0.5f) * height // Y轴翻转
                        Pair(screenX, screenY)
                    } else {
                        // 使用角度（旧版本）
                        val screenX = (target.angle / 180f) * width
                        val screenY = height / 2
                        Pair(screenX, screenY)
                    }

                    drawCircle(
                        color = if (target.isHit) Color.Gray else Color.Yellow,
                        radius = 40f,
                        center = Offset(x, y)
                    )
                }

                // 绘制当前手臂位置指示器
                val (currentX, currentY) = if (targets.firstOrNull()?.position != null) {
                    // 使用2D坐标模式
                    // 这里需要从ViewModel获取当前位置，暂时用角度模拟
                    val screenX = (currentAngle / 180f) * width
                    val screenY = height / 2
                    Pair(screenX, screenY)
                } else {
                    // 使用角度模式
                    val screenX = (currentAngle / 180f) * width
                    val screenY = height / 2
                    Pair(screenX, screenY)
                }

                drawCircle(
                    color = Color.Red,
                    radius = 30f,
                    center = Offset(currentX, currentY)
                )
            }
        }

        // 当前角度显示
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text("当前角度", fontSize = 14.sp, color = Color.Gray)
                Text(
                    text = "${currentAngle.toInt()}°",
                    fontSize = 48.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1A237E)
                )
            }
        }
    }
}

fun getGameDescription(gameType: GameType): String {
    return when (gameType) {
        GameType.FRUIT_NINJA -> "移动手臂切水果获得分数"
        GameType.WHACK_A_MOLE -> "快速移动到目标位置"
        GameType.RHYTHM_MASTER -> "跟随节奏运动"
        GameType.FLIGHT_SIM -> "控制飞机平稳飞行"
    }
}

@Composable
fun GameMenuDialog(
    onDismiss: () -> Unit,
    onPause: () -> Unit,
    onResume: () -> Unit,
    onRestart: () -> Unit,
    onChangeGame: () -> Unit,
    onExit: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("游戏菜单") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                TextButton(
                    onClick = {
                        onResume()
                        onDismiss()
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("继续游戏")
                }
                TextButton(
                    onClick = {
                        onRestart()
                        onDismiss()
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.Replay, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("重新开始")
                }
                TextButton(
                    onClick = {
                        onChangeGame()
                        onDismiss()
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.SwapHoriz, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("切换游戏")
                }
                Divider()
                TextButton(
                    onClick = {
                        onExit()
                        onDismiss()
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Icon(Icons.Default.ExitToApp, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("退出游戏")
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("关闭")
            }
        }
    )
}


@Composable
fun GameFinishedScreen(
    score: Int,
    onRestart: () -> Unit,
    onChangeGame: () -> Unit,
    onExit: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.EmojiEvents,
            contentDescription = null,
            modifier = Modifier.size(120.dp),
            tint = Color(0xFFFFD700)
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "游戏结束!",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "最终得分",
            fontSize = 16.sp,
            color = Color.White.copy(alpha = 0.8f)
        )

        Text(
            text = "$score",
            fontSize = 64.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFFD700)
        )

        Spacer(modifier = Modifier.height(48.dp))

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Button(
                onClick = onRestart,
                modifier = Modifier
                    .width(200.dp)
                    .height(56.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.White,
                    contentColor = Color(0xFF1A237E)
                )
            ) {
                Icon(Icons.Default.Replay, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("再玩一次", fontWeight = FontWeight.Bold)
            }

            OutlinedButton(
                onClick = onChangeGame,
                modifier = Modifier
                    .width(200.dp)
                    .height(56.dp),
                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = Color.White
                )
            ) {
                Icon(Icons.Default.SwapHoriz, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("切换游戏", fontWeight = FontWeight.Bold)
            }

            TextButton(
                onClick = onExit,
                modifier = Modifier.width(200.dp)
            ) {
                Text("退出", color = Color.White)
            }
        }
    }
}
