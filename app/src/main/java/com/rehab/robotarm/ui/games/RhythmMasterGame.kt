package com.rehab.robotarm.ui.games

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.rehab.robotarm.viewmodel.GameTarget
import com.rehab.robotarm.viewmodel.Position2D
import kotlinx.coroutines.delay

/**
 * 节奏大师游戏
 * 特点：
 * - 音符从上往下落
 * - 按照节奏移动到目标位置
 * - 时机准确度影响分数
 * - 有判定区域和准确度提示
 */
@Composable
fun RhythmMasterGame(
    targets: List<GameTarget>,
    currentPosition: Position2D,
    score: Int,
    timeRemaining: Int,
    onTargetHit: (Int) -> Unit
) {
    var accuracy by remember { mutableStateOf("") }
    var showAccuracy by remember { mutableStateOf(false) }

    // 准确度提示淡出
    LaunchedEffect(showAccuracy) {
        if (showAccuracy) {
            delay(1000)
            showAccuracy = false
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        // 顶部信息栏
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            GameInfoBar(score, timeRemaining)

            // 准确度提示
            if (showAccuracy) {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = when (accuracy) {
                            "Perfect!" -> Color(0xFF4CAF50)
                            "Great!" -> Color(0xFF2196F3)
                            "Good" -> Color(0xFFFFC107)
                            else -> Color(0xFFFF5722)
                        }
                    )
                ) {
                    Text(
                        text = accuracy,
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
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
            Canvas(modifier = Modifier.fillMaxSize()) {
                val width = size.width
                val height = size.height

                // 绘制轨道
                val trackCount = 4
                val trackWidth = width / trackCount

                for (i in 0 until trackCount) {
                    val x = i * trackWidth + trackWidth / 2
                    // 轨道线
                    drawLine(
                        color = Color.White.copy(alpha = 0.3f),
                        start = Offset(x, 0f),
                        end = Offset(x, height),
                        strokeWidth = 2f
                    )
                }

                // 判定线（底部）
                val judgeLineY = height - 150f
                drawLine(
                    color = Color.Green,
                    start = Offset(0f, judgeLineY),
                    end = Offset(width, judgeLineY),
                    strokeWidth = 4f
                )

                // 判定区域
                drawRect(
                    color = Color.Green.copy(alpha = 0.2f),
                    topLeft = Offset(0f, judgeLineY - 50f),
                    size = androidx.compose.ui.geometry.Size(width, 100f)
                )

                // 绘制音符
                targets.forEach { target ->
                    if (target.position != null && !target.isHit) {
                        val screenX = (target.position.x / 0.6f) * width
                        // 音符从上往下落
                        val progress = (System.currentTimeMillis() - target.appearTime) / 3000f
                        val screenY = progress * height

                        if (screenY < height) {
                            // 音符外圈
                            drawCircle(
                                color = Color.Cyan,
                                radius = 50f,
                                center = Offset(screenX, screenY),
                                style = Stroke(width = 4f)
                            )
                            // 音符内圈
                            drawCircle(
                                color = Color.Cyan.copy(alpha = 0.5f),
                                radius = 40f,
                                center = Offset(screenX, screenY)
                            )

                            // 音符尾巴（轨迹）
                            for (j in 1..5) {
                                val tailY = screenY - j * 20f
                                if (tailY > 0) {
                                    drawCircle(
                                        color = Color.Cyan.copy(alpha = 0.3f / j),
                                        radius = 40f - j * 5f,
                                        center = Offset(screenX, tailY)
                                    )
                                }
                            }
                        }
                    }
                }

                // 绘制当前位置指示器
                val currentX = (currentPosition.x / 0.6f) * width
                val currentY = judgeLineY

                // 外圈动画
                drawCircle(
                    color = Color.Yellow,
                    radius = 60f,
                    center = Offset(currentX, currentY),
                    style = Stroke(width = 3f)
                )
                // 内圈
                drawCircle(
                    color = Color.Yellow,
                    radius = 45f,
                    center = Offset(currentX, currentY)
                )
                // 中心点
                drawCircle(
                    color = Color.White,
                    radius = 20f,
                    center = Offset(currentX, currentY)
                )
            }
        }

        // 当前位置显示
        PositionDisplay(currentPosition)
    }
}
