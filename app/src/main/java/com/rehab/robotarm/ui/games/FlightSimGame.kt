package com.rehab.robotarm.ui.games

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.rehab.robotarm.viewmodel.GameTarget
import com.rehab.robotarm.viewmodel.Position2D
import kotlin.math.sin

/**
 * 飞行模拟游戏
 * 特点：
 * - 控制飞机高度避开障碍物
 * - 障碍物从右往左移动
 * - 需要平滑控制，避免抖动
 * - 连续游戏，无尽模式
 */
@Composable
fun FlightSimGame(
    targets: List<GameTarget>,
    currentPosition: Position2D,
    score: Int,
    timeRemaining: Int
) {
    var altitude by remember { mutableStateOf(0.25f) }
    var speed by remember { mutableStateOf(1f) }
    var distance by remember { mutableStateOf(0f) }

    // 根据Y坐标计算高度
    LaunchedEffect(currentPosition) {
        altitude = currentPosition.y
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

            // 速度显示
            Card(colors = CardDefaults.cardColors(containerColor = Color.White)) {
                Column(
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "速度",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                    Text(
                        text = "${String.format("%.1f", speed)}x",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
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

                // 背景云朵
                for (i in 0..5) {
                    val cloudX = (i * 200f + distance * 50f) % width
                    val cloudY = 100f + i * 80f
                    drawCircle(
                        color = Color.White.copy(alpha = 0.3f),
                        radius = 40f,
                        center = Offset(cloudX, cloudY)
                    )
                    drawCircle(
                        color = Color.White.copy(alpha = 0.3f),
                        radius = 30f,
                        center = Offset(cloudX + 30f, cloudY)
                    )
                    drawCircle(
                        color = Color.White.copy(alpha = 0.3f),
                        radius = 35f,
                        center = Offset(cloudX + 15f, cloudY - 20f)
                    )
                }

                // 绘制障碍物（管道）
                targets.forEach { target ->
                    if (target.position != null) {
                        val obstacleX = width - (distance * 100f - target.id * 300f) % (width + 300f)

                        if (obstacleX > -100f && obstacleX < width + 100f) {
                            val gapY = height - (target.position.y / 0.5f) * height
                            val gapSize = 200f

                            // 上方管道
                            drawRect(
                                color = Color(0xFF4CAF50),
                                topLeft = Offset(obstacleX - 40f, 0f),
                                size = Size(80f, gapY - gapSize / 2)
                            )
                            drawRect(
                                color = Color(0xFF388E3C),
                                topLeft = Offset(obstacleX - 50f, gapY - gapSize / 2 - 30f),
                                size = Size(100f, 30f)
                            )

                            // 下方管道
                            drawRect(
                                color = Color(0xFF4CAF50),
                                topLeft = Offset(obstacleX - 40f, gapY + gapSize / 2),
                                size = Size(80f, height - (gapY + gapSize / 2))
                            )
                            drawRect(
                                color = Color(0xFF388E3C),
                                topLeft = Offset(obstacleX - 50f, gapY + gapSize / 2),
                                size = Size(100f, 30f)
                            )
                        }
                    }
                }

                // 绘制飞机
                val planeX = 200f
                val planeY = height - (altitude / 0.5f) * height

                // 飞机机身
                val planePath = Path().apply {
                    moveTo(planeX, planeY)
                    lineTo(planeX + 60f, planeY)
                    lineTo(planeX + 70f, planeY - 10f)
                    lineTo(planeX + 60f, planeY - 20f)
                    lineTo(planeX, planeY - 20f)
                    close()
                }
                drawPath(
                    path = planePath,
                    color = Color(0xFF2196F3)
                )

                // 飞机机翼
                drawRect(
                    color = Color(0xFF1976D2),
                    topLeft = Offset(planeX + 20f, planeY - 30f),
                    size = Size(30f, 10f)
                )
                drawRect(
                    color = Color(0xFF1976D2),
                    topLeft = Offset(planeX + 20f, planeY - 10f),
                    size = Size(30f, 10f)
                )

                // 飞机窗户
                drawCircle(
                    color = Color.White.copy(alpha = 0.7f),
                    radius = 6f,
                    center = Offset(planeX + 30f, planeY - 10f)
                )

                // 尾翼
                val tailPath = Path().apply {
                    moveTo(planeX, planeY - 10f)
                    lineTo(planeX - 15f, planeY - 25f)
                    lineTo(planeX, planeY - 20f)
                    close()
                }
                drawPath(
                    path = tailPath,
                    color = Color(0xFFFF5722)
                )

                // 高度指示线
                drawLine(
                    color = Color.Yellow.copy(alpha = 0.3f),
                    start = Offset(0f, planeY),
                    end = Offset(width, planeY),
                    strokeWidth = 2f
                )
            }
        }

        // 高度和位置显示
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
                Text("飞行高度", fontSize = 14.sp, color = Color.Gray)
                Text(
                    text = "${String.format("%.2f", altitude)}m",
                    fontSize = 36.sp,
                    fontWeight = FontWeight.Bold,
                    color = when {
                        altitude < 0.1f -> Color.Red
                        altitude > 0.4f -> Color.Red
                        else -> Color(0xFF1A237E)
                    }
                )
                Spacer(modifier = Modifier.height(8.dp))
                LinearProgressIndicator(
                    progress = altitude / 0.5f,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp),
                    color = when {
                        altitude < 0.1f -> Color.Red
                        altitude > 0.4f -> Color.Red
                        else -> Color.Green
                    }
                )
            }
        }
    }
}
