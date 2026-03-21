package com.rehab.robotarm.ui.games

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Timer
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.rehab.robotarm.viewmodel.GameTarget
import com.rehab.robotarm.viewmodel.Position2D
import kotlinx.coroutines.delay
import kotlin.math.cos
import kotlin.math.sin
import kotlin.random.Random

/**
 * 水果忍者游戏
 * 特点：
 * - 水果从下往上飞
 * - 移动手臂到水果位置"切"水果
 * - 有切割轨迹效果
 * - 水果会旋转和下落
 */
@Composable
fun FruitNinjaGame(
    targets: List<GameTarget>,
    currentPosition: Position2D,
    score: Int,
    timeRemaining: Int,
    onTargetHit: (Int) -> Unit
) {
    var slashPath by remember { mutableStateOf<List<Offset>>(emptyList()) }
    var lastPosition by remember { mutableStateOf(currentPosition) }

    // 记录切割轨迹
    LaunchedEffect(currentPosition) {
        if (slashPath.size > 20) {
            slashPath = slashPath.takeLast(20)
        }
        slashPath = slashPath + listOf(
            Offset(
                currentPosition.x * 1000f,
                currentPosition.y * 1000f
            )
        )

        // 轨迹淡出
        delay(100)
        if (slashPath.isNotEmpty()) {
            slashPath = slashPath.drop(1)
        }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        // 顶部信息栏
        GameInfoBar(score, timeRemaining)

        // 游戏区域
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
        ) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                val width = size.width
                val height = size.height

                // 绘制水果
                targets.forEach { target ->
                    if (target.position != null) {
                        val screenX = (target.position.x / 0.6f) * width
                        val screenY = height - (target.position.y / 0.5f) * height

                        // 水果颜色
                        val fruitColor = when (target.id % 5) {
                            0 -> Color(0xFFFF6B6B) // 红色（苹果）
                            1 -> Color(0xFFFFA500) // 橙色（橙子）
                            2 -> Color(0xFFFFFF00) // 黄色（香蕉）
                            3 -> Color(0xFF4CAF50) // 绿色（西瓜）
                            else -> Color(0xFF9C27B0) // 紫色（葡萄）
                        }

                        if (target.isHit) {
                            // 被切开的水果效果
                            drawCircle(
                                color = fruitColor.copy(alpha = 0.3f),
                                radius = 50f,
                                center = Offset(screenX - 20f, screenY)
                            )
                            drawCircle(
                                color = fruitColor.copy(alpha = 0.3f),
                                radius = 50f,
                                center = Offset(screenX + 20f, screenY)
                            )
                        } else {
                            // 完整的水果
                            drawCircle(
                                color = fruitColor,
                                radius = 60f,
                                center = Offset(screenX, screenY)
                            )
                            // 水果高光
                            drawCircle(
                                color = Color.White.copy(alpha = 0.3f),
                                radius = 20f,
                                center = Offset(screenX - 15f, screenY - 15f)
                            )
                        }
                    }
                }

                // 绘制切割轨迹
                if (slashPath.size > 1) {
                    val path = Path()
                    path.moveTo(slashPath.first().x, slashPath.first().y)
                    slashPath.forEach { point ->
                        path.lineTo(point.x, point.y)
                    }
                    drawPath(
                        path = path,
                        color = Color.White.copy(alpha = 0.6f),
                        style = Stroke(width = 8f)
                    )
                }

                // 绘制当前手臂位置（刀）
                val currentX = (currentPosition.x / 0.6f) * width
                val currentY = height - (currentPosition.y / 0.5f) * height

                // 刀的形状
                drawCircle(
                    color = Color.Red,
                    radius = 25f,
                    center = Offset(currentX, currentY)
                )
                drawCircle(
                    color = Color.White,
                    radius = 15f,
                    center = Offset(currentX, currentY)
                )
            }
        }

        // 当前位置显示
        PositionDisplay(currentPosition)
    }
}

@Composable
fun GameInfoBar(score: Int, timeRemaining: Int) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        // 分数
        Card(colors = CardDefaults.cardColors(containerColor = Color.White)) {
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
}

@Composable
fun PositionDisplay(position: Position2D) {
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
            Text("当前位置", fontSize = 14.sp, color = Color.Gray)
            Row(
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    text = "X: ${String.format("%.2f", position.x)}m",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1A237E)
                )
                Text(
                    text = "Y: ${String.format("%.2f", position.y)}m",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF1A237E)
                )
            }
        }
    }
}
