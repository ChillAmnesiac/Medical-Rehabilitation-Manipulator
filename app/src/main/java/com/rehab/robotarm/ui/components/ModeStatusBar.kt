package com.rehab.robotarm.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rehab.robotarm.data.model.*

/**
 * 模式状态栏组件 - 显示当前模式
 */
@Composable
fun ModeStatusBar(
    mainMode: MainMode,
    activeSubMode: ActiveSubMode?,
    passiveSubMode: PassiveSubMode?,
    memorySubMode: MemorySubMode?,
    isConnected: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = when (mainMode) {
                MainMode.ACTIVE -> Color(0xFF4CAF50).copy(alpha = 0.2f)
                MainMode.PASSIVE -> Color(0xFF2196F3).copy(alpha = 0.2f)
                MainMode.MEMORY -> Color(0xFFFF9800).copy(alpha = 0.2f)
            }
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 左侧：主模式
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = when (mainMode) {
                        MainMode.ACTIVE -> Icons.Default.DirectionsRun
                        MainMode.PASSIVE -> Icons.Default.TouchApp
                        MainMode.MEMORY -> Icons.Default.Memory
                    },
                    contentDescription = null,
                    tint = when (mainMode) {
                        MainMode.ACTIVE -> Color(0xFF4CAF50)
                        MainMode.PASSIVE -> Color(0xFF2196F3)
                        MainMode.MEMORY -> Color(0xFFFF9800)
                    },
                    modifier = Modifier.size(24.dp)
                )

                Column {
                    Text(
                        text = when (mainMode) {
                            MainMode.ACTIVE -> "主动模式"
                            MainMode.PASSIVE -> "被动模式"
                            MainMode.MEMORY -> "记忆模式"
                        },
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )

                    // 子模式
                    val subModeText = when (mainMode) {
                        MainMode.ACTIVE -> when (activeSubMode) {
                            ActiveSubMode.STANDARD -> "标准主动模式"
                            ActiveSubMode.AI_ASSIST -> "AI助力模式"
                            ActiveSubMode.GAME -> "游戏化训练"
                            null -> "未选择"
                        }
                        MainMode.PASSIVE -> when (passiveSubMode) {
                            PassiveSubMode.MANUAL -> "手动控制"
                            PassiveSubMode.AUTO_TRAIN -> "自动训练"
                            PassiveSubMode.REMOTE -> "远程控制"
                            null -> "未选择"
                        }
                        MainMode.MEMORY -> when (memorySubMode) {
                            MemorySubMode.REPLAY -> "动作回放"
                            MemorySubMode.PLAN -> "训练计划"
                            MemorySubMode.ASSESSMENT -> "评估测试"
                            null -> "未选择"
                        }
                    }

                    Text(
                        text = subModeText,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // 右侧：连接状态
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Icon(
                    imageVector = if (isConnected) Icons.Default.Bluetooth else Icons.Default.BluetoothDisabled,
                    contentDescription = null,
                    tint = if (isConnected) Color(0xFF4CAF50) else Color(0xFFF44336),
                    modifier = Modifier.size(20.dp)
                )
                Text(
                    text = if (isConnected) "已连接" else "未连接",
                    style = MaterialTheme.typography.bodySmall,
                    color = if (isConnected) Color(0xFF4CAF50) else Color(0xFFF44336)
                )
            }
        }
    }
}
