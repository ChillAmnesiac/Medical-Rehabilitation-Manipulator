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
import com.rehab.robotarm.viewmodel.AuthViewModel
import com.rehab.robotarm.viewmodel.RobotViewModel
import com.rehab.robotarm.ui.components.ModeStatusBar

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    navController: NavController,
    authViewModel: AuthViewModel,
    robotViewModel: RobotViewModel
) {
    val currentUser by authViewModel.currentUser.collectAsState()
    val robotState by robotViewModel.robotState.collectAsState()
    val isConnected = robotState.isConnected

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("康复机械臂训练系统") },
                actions = {
                    // 蓝牙连接按钮
                    IconButton(onClick = { navController.navigate("bluetooth_connection") }) {
                        Icon(
                            imageVector = if (isConnected) Icons.Default.Bluetooth else Icons.Default.BluetoothDisabled,
                            contentDescription = "蓝牙连接",
                            tint = if (isConnected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
                        )
                    }
                    IconButton(onClick = { authViewModel.logout(); navController.navigate("login") }) {
                        Icon(Icons.Default.Logout, contentDescription = "登出")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // 模式状态栏
            ModeStatusBar(
                mainMode = robotState.mainMode,
                activeSubMode = robotState.activeSubMode,
                passiveSubMode = robotState.passiveSubMode,
                memorySubMode = robotState.memorySubMode,
                isConnected = isConnected,
                modifier = Modifier.padding(16.dp)
            )

            // 欢迎卡片
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "欢迎回来, ${currentUser?.username ?: "用户"}",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "角色: ${getRoleText(currentUser?.role ?: "")}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }

            // 紧急停止按钮（仅在连接时显示）
            if (isConnected) {
                Button(
                    onClick = { robotViewModel.emergencyStop() },
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .height(64.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = null,
                        modifier = Modifier.size(32.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "紧急停止",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
            }

            // 功能网格
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                contentPadding = PaddingValues(16.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(getMenuItems(currentUser?.role ?: "patient")) { item ->
                    MenuCard(
                        icon = item.icon,
                        title = item.title,
                        onClick = { navController.navigate(item.route) }
                    )
                }
            }
        }
    }
}

@Composable
fun MenuCard(
    icon: ImageVector,
    title: String,
    onClick: () -> Unit
) {
    Card(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .height(120.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

data class MenuItem(
    val icon: ImageVector,
    val title: String,
    val route: String
)

fun getMenuItems(role: String): List<MenuItem> {
    val commonItems = listOf(
        MenuItem(Icons.Default.Settings, "模式选择", "mode_selection"),
        MenuItem(Icons.Default.Sensors, "传感器数据", "sensor_data"),
        MenuItem(Icons.Default.Storage, "数据采集", "data_collection"),
        MenuItem(Icons.Default.BugReport, "BLE 调试", "ble_debug"),
        MenuItem(Icons.Default.Leaderboard, "排行榜", "leaderboard")
    )

    return when (role) {
        "doctor", "therapist" -> commonItems + listOf(
            MenuItem(Icons.Default.People, "患者管理", "patient_list"),
            MenuItem(Icons.Default.Wifi, "系统设置", "wifi_config")
        )
        else -> commonItems
    }
}

fun getRoleText(role: String): String {
    return when (role) {
        "patient" -> "患者"
        "doctor" -> "医生"
        "therapist" -> "治疗师"
        "family" -> "家属"
        else -> role
    }
}
