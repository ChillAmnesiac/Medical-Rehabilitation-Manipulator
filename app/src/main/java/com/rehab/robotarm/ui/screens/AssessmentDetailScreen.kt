package com.rehab.robotarm.ui.screens

import android.content.Context
import android.widget.Toast
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rehab.robotarm.data.database.entity.RehabAssessment
import com.rehab.robotarm.viewmodel.AssessmentViewModel
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AssessmentDetailScreen(
    patientId: String,
    onNavigateBack: () -> Unit,
    viewModel: AssessmentViewModel = viewModel()
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    val assessments by viewModel.getAssessmentsByPatient(patientId).collectAsState(initial = emptyList())
    val patient by viewModel.getPatient(patientId).collectAsState(initial = null)
    val sessions by viewModel.getSessionsByPatient(patientId).collectAsState(initial = emptyList())

    var showExportDialog by remember { mutableStateOf(false) }
    var isExporting by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("康复评估详情") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, "返回")
                    }
                },
                actions = {
                    IconButton(
                        onClick = { showExportDialog = true },
                        enabled = assessments.isNotEmpty() && patient != null
                    ) {
                        Icon(Icons.Default.PictureAsPdf, "导出PDF")
                    }
                }
            )
        }
    ) { padding ->
        if (assessments.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        Icons.Default.Assessment,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("暂无评估数据", style = MaterialTheme.typography.titleMedium)
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 统计卡片
                item {
                    AssessmentStatisticsCard(assessments)
                }

                // 最新评估
                item {
                    Text(
                        "最新评估",
                        style = MaterialTheme.typography.titleLarge,
                        modifier = Modifier.padding(vertical = 8.dp)
                    )
                }

                item {
                    AssessmentCard(assessments.first(), isLatest = true)
                }

                // 历史评估
                if (assessments.size > 1) {
                    item {
                        Text(
                            "历史评估",
                            style = MaterialTheme.typography.titleLarge,
                            modifier = Modifier.padding(vertical = 8.dp)
                        )
                    }

                    items(assessments.drop(1)) { assessment ->
                        AssessmentCard(assessment, isLatest = false)
                    }
                }
            }
        }
    }

    // 导出对话框
    if (showExportDialog) {
        AlertDialog(
            onDismissRequest = { showExportDialog = false },
            title = { Text("导出PDF报告") },
            text = {
                if (isExporting) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        CircularProgressIndicator(modifier = Modifier.size(24.dp))
                        Text("正在生成PDF...")
                    }
                } else {
                    Text("确定要导出康复评估报告吗？报告将保存到下载文件夹。")
                }
            },
            confirmButton = {
                if (!isExporting) {
                    TextButton(
                        onClick = {
                            scope.launch {
                                isExporting = true
                                val result = viewModel.exportPdfReport(
                                    context,
                                    patient!!,
                                    sessions,
                                    assessments
                                )
                                isExporting = false
                                showExportDialog = false

                                if (result.isSuccess) {
                                    Toast.makeText(
                                        context,
                                        "PDF已保存到: ${result.getOrNull()?.absolutePath}",
                                        Toast.LENGTH_LONG
                                    ).show()
                                } else {
                                    Toast.makeText(
                                        context,
                                        "导出失败: ${result.exceptionOrNull()?.message}",
                                        Toast.LENGTH_SHORT
                                    ).show()
                                }
                            }
                        }
                    ) {
                        Text("确定")
                    }
                }
            },
            dismissButton = {
                if (!isExporting) {
                    TextButton(onClick = { showExportDialog = false }) {
                        Text("取消")
                    }
                }
            }
        )
    }
}

@Composable
fun AssessmentStatisticsCard(assessments: List<RehabAssessment>) {
    val avgSmooth = assessments.map { it.smoothness }.average()
    val avgROM = assessments.map { it.rangeOfMotion }.average()
    val avgStrength = assessments.map { it.strength }.average()
    val avgOverall = assessments.map { it.overallScore }.average()

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                "平均评分统计",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StatItem("平滑度", avgSmooth)
                StatItem("运动范围", avgROM)
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StatItem("力量", avgStrength)
                StatItem("综合", avgOverall)
            }
        }
    }
}

@Composable
fun StatItem(label: String, value: Double) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            String.format("%.1f", value),
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
fun AssessmentCard(assessment: RehabAssessment, isLatest: Boolean) {
    val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = if (isLatest) {
            CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.secondaryContainer
            )
        } else {
            CardDefaults.cardColors()
        }
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    dateFormat.format(Date(assessment.timestamp)),
                    style = MaterialTheme.typography.titleSmall
                )
                if (isLatest) {
                    AssistChip(
                        onClick = { },
                        label = { Text("最新") },
                        leadingIcon = { Icon(Icons.Default.Star, null, modifier = Modifier.size(16.dp)) }
                    )
                }
            }

            Divider()

            // 评分项
            ScoreRow("运动平滑度", assessment.smoothness)
            ScoreRow("运动范围", assessment.rangeOfMotion)
            ScoreRow("力量评分", assessment.strength)

            Divider()

            ScoreRow("综合评分", assessment.overallScore, isOverall = true)

            // AI建议
            if (assessment.recommendation.isNotEmpty()) {
                Divider()
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Default.Lightbulb,
                            contentDescription = null,
                            modifier = Modifier.size(16.dp),
                            tint = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            "AI建议",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    Text(
                        assessment.recommendation,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
fun ScoreRow(label: String, score: Float, isOverall: Boolean = false) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            label,
            style = if (isOverall) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyMedium
        )
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            LinearProgressIndicator(
                progress = score / 100f,
                modifier = Modifier.width(100.dp),
                color = getAssessmentScoreColor(score)
            )
            Text(
                String.format("%.1f", score),
                style = if (isOverall) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyMedium,
                color = getAssessmentScoreColor(score)
            )
        }
    }
}

fun getAssessmentScoreColor(score: Float): Color {
    return when {
        score >= 80 -> Color(0xFF4CAF50) // 绿色
        score >= 60 -> Color(0xFFFFC107) // 黄色
        score >= 40 -> Color(0xFFFF9800) // 橙色
        else -> Color(0xFFF44336) // 红色
    }
}
