package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
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
import com.rehab.robotarm.data.model.GameType
import com.rehab.robotarm.viewmodel.GameViewModel

/**
 * 游戏选择界面
 * 显示所有可用的游戏类型，可以随时切换
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GameSelectionScreen(
    navController: NavController,
    gameViewModel: GameViewModel
) {
    val currentGameType by gameViewModel.currentGameType.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("选择游戏") },
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
                .padding(16.dp)
        ) {
            Text(
                text = "游戏化康复训练",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "通过趣味游戏进行康复训练，让康复过程更有趣",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(24.dp))

            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(getGameList()) { game ->
                    GameCard(
                        game = game,
                        isSelected = currentGameType == game.type,
                        onClick = {
                            gameViewModel.selectGameType(game.type)
                            navController.navigate("game_play/${game.type.name}")
                        }
                    )
                }
            }
        }
    }
}

data class GameInfo(
    val type: GameType,
    val title: String,
    val description: String,
    val icon: ImageVector,
    val difficulty: String
)

fun getGameList(): List<GameInfo> {
    return listOf(
        GameInfo(
            type = GameType.FRUIT_NINJA,
            title = "水果忍者",
            description = "移动手臂切水果，训练快速反应和精准控制",
            icon = Icons.Default.Restaurant,
            difficulty = "简单"
        ),
        GameInfo(
            type = GameType.WHACK_A_MOLE,
            title = "打地鼠",
            description = "快速移动到目标位置，提高反应速度",
            icon = Icons.Default.TouchApp,
            difficulty = "中等"
        ),
        GameInfo(
            type = GameType.RHYTHM_MASTER,
            title = "节奏大师",
            description = "跟随音乐节奏运动，训练协调性",
            icon = Icons.Default.MusicNote,
            difficulty = "中等"
        ),
        GameInfo(
            type = GameType.FLIGHT_SIM,
            title = "飞行模拟",
            description = "控制飞机飞行，训练平滑运动控制",
            icon = Icons.Default.Flight,
            difficulty = "困难"
        )
    )
}

@Composable
fun GameCard(
    game: GameInfo,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(180.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected)
                MaterialTheme.colorScheme.primaryContainer
            else
                MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isSelected) 8.dp else 2.dp
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Icon(
                imageVector = game.icon,
                contentDescription = null,
                modifier = Modifier.size(56.dp),
                tint = if (isSelected)
                    MaterialTheme.colorScheme.primary
                else
                    MaterialTheme.colorScheme.onSurface
            )

            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = game.title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = game.description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = 2
                )
            }

            AssistChip(
                onClick = { },
                label = { Text(game.difficulty) },
                colors = AssistChipDefaults.assistChipColors(
                    containerColor = when (game.difficulty) {
                        "简单" -> MaterialTheme.colorScheme.tertiaryContainer
                        "中等" -> MaterialTheme.colorScheme.secondaryContainer
                        else -> MaterialTheme.colorScheme.errorContainer
                    }
                )
            )
        }
    }
}
