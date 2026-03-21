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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rehab.robotarm.data.database.entity.TrainingSession
import com.rehab.robotarm.viewmodel.TrainingViewModel
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrainingHistoryScreen(
    patientId: String,
    viewModel: TrainingViewModel
) {
    val sessions by viewModel.sessions.collectAsState()

    LaunchedEffect(patientId) {
        viewModel.loadSessions(patientId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("训练历史") }
            )
        }
    ) { padding ->
        if (sessions.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        Icons.Default.FitnessCenter,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("暂无训练记录", style = MaterialTheme.typography.titleMedium)
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(sessions) { session ->
                    TrainingSessionCard(session)
                }
            }
        }
    }
}

@Composable
fun TrainingSessionCard(session: TrainingSession) {
    val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())

    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
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
                Text(
                    text = getModeText(session.mode),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${session.overallScore.toInt()}分",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    color = getScoreColor(session.overallScore)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = dateFormat.format(Date(session.startTime)),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                InfoChip(
                    icon = Icons.Default.Timer,
                    text = "${session.duration / 60}分钟"
                )
                InfoChip(
                    icon = Icons.Default.Repeat,
                    text = "${session.repetitions}次"
                )
                InfoChip(
                    icon = Icons.Default.FavoriteBorder,
                    text = "${session.avgHeartRate}bpm"
                )
            }

            if (session.notes.isNotBlank()) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "备注: ${session.notes}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
fun InfoChip(icon: androidx.compose.ui.graphics.vector.ImageVector, text: String) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(16.dp),
            tint = MaterialTheme.colorScheme.primary
        )
        Text(
            text = text,
            style = MaterialTheme.typography.bodySmall
        )
    }
}

fun getModeText(mode: String): String {
    return when (mode) {
        "passive" -> "被动模式"
        "active" -> "主动模式"
        "assist" -> "助力模式"
        "resist" -> "阻力模式"
        "memory" -> "记忆模式"
        "game" -> "游戏模式"
        else -> mode
    }
}

fun getScoreColor(score: Float): androidx.compose.ui.graphics.Color {
    return when {
        score >= 80 -> androidx.compose.ui.graphics.Color(0xFF4CAF50) // 绿色
        score >= 60 -> androidx.compose.ui.graphics.Color(0xFFFFC107) // 黄色
        else -> androidx.compose.ui.graphics.Color(0xFFF44336) // 红色
    }
}
