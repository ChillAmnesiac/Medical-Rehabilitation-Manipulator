package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rehab.robotarm.ui.theme.MedicalBlue
import com.rehab.robotarm.ui.theme.MedicalGreen
import com.rehab.robotarm.ui.theme.MedicalOrange
import com.rehab.robotarm.viewmodel.RobotViewModel

/**
 * 界面三：康复分析界面
 * 显示AI推理得出的康复效果图表
 */
@Composable
fun RehabAnalysisScreen(viewModel: RobotViewModel = viewModel()) {
    val rehabAnalysis by viewModel.rehabAnalysis.collectAsState()
    val cloudAdvice by viewModel.cloudAdvice.collectAsState()
    val sensorHistory by viewModel.sensorDataHistory.collectAsState()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "康复分析",
                style = MaterialTheme.typography.headlineMedium
            )
        }

        // 综合评分卡片
        item {
            rehabAnalysis?.let { analysis ->
                OverallScoreCard(analysis.overallScore)
            }
        }

        // 详细指标
        item {
            rehabAnalysis?.let { analysis ->
                DetailedMetricsCard(
                    smoothness = analysis.smoothness,
                    rangeOfMotion = analysis.rangeOfMotion,
                    strength = analysis.strength
                )
            }
        }

        // 趋势图表
        item {
            TrendChartCard(sensorHistory)
        }

        // AI建议
        item {
            rehabAnalysis?.let { analysis ->
                RecommendationCard(analysis.recommendation)
            }
        }

        // 云端建议
        item {
            if (cloudAdvice.isNotEmpty()) {
                CloudAdviceCard(cloudAdvice)
            }
        }

        // 刷新按钮
        item {
            Button(
                onClick = { viewModel.fetchCloudAdvice() },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("获取云端AI建议")
            }
        }
    }
}

@Composable
fun OverallScoreCard(score: Float) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = when {
                score >= 80 -> MedicalGreen.copy(alpha = 0.2f)
                score >= 60 -> MedicalOrange.copy(alpha = 0.2f)
                else -> Color.Red.copy(alpha = 0.2f)
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
                text = "综合评分",
                style = MaterialTheme.typography.titleLarge
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "${score.toInt()}",
                style = MaterialTheme.typography.displayLarge,
                color = MaterialTheme.colorScheme.primary
            )
            Text(
                text = "分",
                style = MaterialTheme.typography.titleMedium
            )
        }
    }
}

@Composable
fun DetailedMetricsCard(
    smoothness: Float,
    rangeOfMotion: Float,
    strength: Float
) {
    Card {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "详细指标",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            MetricProgressBar("运动平滑度", smoothness, MedicalBlue)
            Spacer(modifier = Modifier.height(12.dp))
            MetricProgressBar("运动范围", rangeOfMotion, MedicalGreen)
            Spacer(modifier = Modifier.height(12.dp))
            MetricProgressBar("力量评分", strength, MedicalOrange)
        }
    }
}

@Composable
fun MetricProgressBar(label: String, value: Float, color: Color) {
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(label, style = MaterialTheme.typography.bodyMedium)
            Text("${value.toInt()}/100", style = MaterialTheme.typography.bodyMedium)
        }
        Spacer(modifier = Modifier.height(4.dp))
        LinearProgressIndicator(
            progress = value / 100f,
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp),
            color = color
        )
    }
}

@Composable
fun TrendChartCard(sensorHistory: List<com.rehab.robotarm.data.model.SensorData>) {
    Card {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "运动趋势",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(bottom = 8.dp)
            )

            if (sensorHistory.isEmpty()) {
                Text(
                    text = "暂无数据",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(vertical = 32.dp)
                )
            } else {
                SimpleLineChart(
                    data = sensorHistory.takeLast(50).map { it.shoulderAngle },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                )
            }
        }
    }
}

@Composable
fun SimpleLineChart(data: List<Float>, modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        if (data.size < 2) return@Canvas

        val width = size.width
        val height = size.height
        val maxValue = data.maxOrNull() ?: 1f
        val minValue = data.minOrNull() ?: 0f
        val range = maxValue - minValue

        val path = Path()
        val stepX = width / (data.size - 1)

        data.forEachIndexed { index, value ->
            val x = index * stepX
            val y = height - ((value - minValue) / range * height * 0.8f + height * 0.1f)

            if (index == 0) {
                path.moveTo(x, y)
            } else {
                path.lineTo(x, y)
            }
        }

        drawPath(
            path = path,
            color = MedicalBlue,
            style = Stroke(width = 4f)
        )
    }
}

@Composable
fun RecommendationCard(recommendation: String) {
    Card {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "本地AI建议",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            Text(
                text = recommendation,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}

@Composable
fun CloudAdviceCard(advice: String) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = MedicalBlue.copy(alpha = 0.1f)
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "云端AI建议",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            Text(
                text = advice,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}
