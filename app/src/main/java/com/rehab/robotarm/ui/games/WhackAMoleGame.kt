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
 * 打地鼠游戏
 * 特点：
 * - 地鼠随机出现在不同位置
 * - 快速移动手臂到地鼠位置
 * - 地鼠会自动消失
 * - 速度越快分数越高
 */
@Composable
fun WhackAMoleGame(
    targets: List<GameTarget>,
    currentPosition: Position2D,
    score: Int,
    timeRemaining: Int,
    onTargetHit: (Int) -> Unit
) {
    var combo by remember { mutableStateOf(0) }
    var lastHitTime by remember { mutableStateOf(0L) }

    Column(modifier = Modifier.fillMaxSize()) {
        // 顶部信息栏
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            GameInfoBar(score, timeRemaining)

            // 连击显示
            if (combo > 1) {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFFF6B6B)
                    )
                ) {
                    Text(
                        text = "连击 x$combo",
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

                // 绘制网格背景
                val gridSize = 5
                val cellWidth = width / gridSize
                val cellHeight = height / gridSize

                for (i in 0..gridSize) {
                    // 垂直线
                    drawLine(
                        color = Color.White.copy(alpha = 0.2f),
                        start = Offset(i * cellWidth, 0f),
                        end = Offset(i * cellWidth, height),
                        strokeWidth = 2f
                    )
                    // 水平线
                    drawLine(
                        color = Color.White.copy(alpha = 0.2f),
                        start = Offset(0f, i * cellHeight),
                        end = Offset(width, i * cellHeight),
                        strokeWidth = 2f
                    )
                }

                // 绘制地鼠洞
                targets.forEach { target ->
                    if (target.position != null) {
                        val screenX = (target.position.x / 0.6f) * width
                        val screenY = height - (target.position.y / 0.5f) * height

                        // 洞
                        drawCircle(
                            color = Color(0xFF8B4513),
                            radius = 70f,
                            center = Offset(screenX, screenY)
                        )
                        drawCircle(
                            color = Color(0xFF654321),
                            radius = 60f,
                            center = Offset(screenX, screenY)
                        )

                        if (!target.isHit) {
                            // 地鼠（未被打）
                            // 身体
                            drawCircle(
                                color = Color(0xFF8B6914),
                                radius = 50f,
                                center = Offset(screenX, screenY - 20f)
                            )
                            // 眼睛
                            drawCircle(
                                color = Color.Black,
                                radius = 8f,
                                center = Offset(screenX - 15f, screenY - 25f)
                            )
                            drawCircle(
                                color = Color.Black,
                                radius = 8f,
                                center = Offset(screenX + 15f, screenY - 25f)
                            )
                            // 鼻子
                            drawCircle(
                                color = Color(0xFFFF69B4),
                                radius = 6f,
                                center = Offset(screenX, screenY - 10f)
                            )
                        } else {
                            // 被打中的效果
                            drawCircle(
                                color = Color.Yellow,
                                radius = 80f,
                                center = Offset(screenX, screenY),
                                alpha = 0.5f
                            )
                            // 星星效果
                            for (i in 0..4) {
                                val angle = (i * 72f) * Math.PI / 180f
                                val x = screenX + 60f * kotlin.math.cos(angle).toFloat()
                                val y = screenY + 60f * kotlin.math.sin(angle).toFloat()
                                drawCircle(
                                    color = Color.Yellow,
                                    radius = 10f,
                                    center = Offset(x, y)
                                )
                            }
                        }
                    }
                }

                // 绘制锤子（当前位置）
                val currentX = (currentPosition.x / 0.6f) * width
                val currentY = height - (currentPosition.y / 0.5f) * height

                // 锤子柄
                drawLine(
                    color = Color(0xFF8B4513),
                    start = Offset(currentX, currentY),
                    end = Offset(currentX + 30f, currentY + 50f),
                    strokeWidth = 12f
                )
                // 锤子头
                drawCircle(
                    color = Color.Gray,
                    radius = 35f,
                    center = Offset(currentX, currentY)
                )
                drawCircle(
                    color = Color.DarkGray,
                    radius = 30f,
                    center = Offset(currentX, currentY)
                )
            }
        }

        // 当前位置显示
        PositionDisplay(currentPosition)
    }
}
