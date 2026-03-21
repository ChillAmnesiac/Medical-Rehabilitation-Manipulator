package com.rehab.robotarm.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.rehab.robotarm.ui.screens.*

sealed class Screen(val route: String, val title: String, val icon: androidx.compose.ui.graphics.vector.ImageVector) {
    object RobotControl : Screen("robot_control", "机械臂控制", Icons.Default.Settings)
    object SensorData : Screen("sensor_data", "传感器数据", Icons.Default.Info)
    object RehabAnalysis : Screen("rehab_analysis", "康复分析", Icons.Default.DateRange)
    object ModeControl : Screen("mode_control", "模式控制", Icons.Default.Build)
    object NaturalControl : Screen("natural_control", "AI控制", Icons.Default.Star)
    object WifiConfig : Screen("wifi_config", "WiFi配置", Icons.Default.Wifi)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    val items = listOf(
        Screen.RobotControl,
        Screen.NaturalControl,
        Screen.SensorData,
        Screen.RehabAnalysis,
        Screen.ModeControl
    )

    var showMenu by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("康复机械臂控制系统") },
                actions = {
                    IconButton(onClick = { showMenu = !showMenu }) {
                        Icon(Icons.Default.MoreVert, contentDescription = "更多")
                    }
                    DropdownMenu(
                        expanded = showMenu,
                        onDismissRequest = { showMenu = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("WiFi配置") },
                            onClick = {
                                showMenu = false
                                navController.navigate(Screen.WifiConfig.route)
                            },
                            leadingIcon = {
                                Icon(Icons.Default.Wifi, contentDescription = null)
                            }
                        )
                    }
                }
            )
        },
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination

                items.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = screen.title) },
                        label = { Text(screen.title) },
                        selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.RobotControl.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.RobotControl.route) { RobotControlScreen() }
            composable(Screen.NaturalControl.route) { NaturalControlScreen() }
            composable(Screen.SensorData.route) { SensorDataScreen() }
            composable(Screen.RehabAnalysis.route) { RehabAnalysisScreen() }
            composable(Screen.ModeControl.route) { ModeControlScreen() }
            composable(Screen.WifiConfig.route) { WifiConfigScreen() }
        }
    }
}
