package com.rehab.robotarm.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.rehab.robotarm.data.model.GameType
import com.rehab.robotarm.ui.screens.*
import com.rehab.robotarm.viewmodel.*

@Composable
fun AppNavigation(
    navController: NavHostController,
    authViewModel: AuthViewModel,
    patientViewModel: PatientViewModel,
    trainingViewModel: TrainingViewModel,
    leaderboardViewModel: LeaderboardViewModel,
    gameViewModel: GameViewModel,
    robotViewModel: RobotViewModel
) {
    NavHost(
        navController = navController,
        startDestination = "login"
    ) {
        // 认证相关
        composable("login") {
            LoginScreen(navController, authViewModel)
        }
        composable("register") {
            RegisterScreen(navController, authViewModel)
        }

        // 主界面
        composable("home") {
            HomeScreen(navController, authViewModel, robotViewModel)
        }

        // 模式选择
        composable("mode_selection") {
            ModeSelectionScreen(navController, robotViewModel)
        }

        // 患者管理
        composable("patient_list") {
            PatientListScreen(navController, patientViewModel)
        }
        composable("add_patient") {
            AddPatientScreen(navController, patientViewModel)
        }
        composable("patient_detail/{patientId}") { backStackEntry ->
            val patientId = backStackEntry.arguments?.getString("patientId") ?: ""
            PatientDetailScreen(navController, patientViewModel, trainingViewModel, patientId)
        }

        // 训练相关
        composable("training_history/{patientId}") { backStackEntry ->
            val patientId = backStackEntry.arguments?.getString("patientId") ?: ""
            TrainingHistoryScreen(patientId, trainingViewModel)
        }
        composable("robot_control") {
            RobotControlScreen(robotViewModel)
        }
        composable("mode_control") {
            ModeControlScreen(robotViewModel)
        }
        composable("sensor_data") {
            SensorDataScreen(robotViewModel)
        }
        composable("data_collection") {
            DataCollectionScreen(navController, robotViewModel)
        }
        composable("natural_control") {
            NaturalControlScreen(robotViewModel)
        }

        // 主动模式子模式
        composable("active_standard") {
            StandardTrainingScreen(navController, robotViewModel)
        }
        composable("active_ai_assist") {
            AIAssistTrainingScreen(navController, robotViewModel)
        }

        // 被动模式子模式
        composable("passive_manual") {
            ManualControlScreen(navController, robotViewModel)
        }
        composable("passive_auto_train") {
            AutoTrainScreen(navController, robotViewModel)
        }
        composable("passive_remote") {
            RemoteControlScreen(navController, robotViewModel)
        }

        // 记忆模式子模式
        composable("action_replay") {
            ActionReplayScreen(navController, robotViewModel)
        }
        composable("training_plan") {
            TrainingPlanSimpleScreen(navController)
        }
        composable("memory_assessment") {
            MemoryAssessmentScreen(navController, robotViewModel)
        }

        // 训练计划管理
        composable(
            "create_manual_plan/{patientId}",
            arguments = listOf(navArgument("patientId") { type = NavType.StringType })
        ) { backStackEntry ->
            val patientId = backStackEntry.arguments?.getString("patientId") ?: "default"
            CreateManualPlanScreen(navController, patientId)
        }

        // 兼容旧路由
        composable("memory_replay") {
            ActionReplayScreen(navController, robotViewModel)
        }
        composable("memory_plan") {
            TrainingPlanSimpleScreen(navController)
        }

        // 游戏化训练
        composable("game_selection") {
            GameSelectionScreen(navController, gameViewModel)
        }
        composable(
            "game_play/{gameType}",
            arguments = listOf(navArgument("gameType") { type = NavType.StringType })
        ) { backStackEntry ->
            val gameTypeStr = backStackEntry.arguments?.getString("gameType") ?: "FRUIT_NINJA"
            val gameType = GameType.valueOf(gameTypeStr)
            RehabGameScreen(navController, gameViewModel, gameType)
        }
        composable("rehab_game") {
            GameSelectionScreen(navController, gameViewModel)
        }

        // 排行榜
        composable("leaderboard") {
            LeaderboardScreen(leaderboardViewModel)
        }

        // 康复分析
        composable("rehab_analysis") {
            RehabAnalysisScreen(robotViewModel)
        }

        // WiFi配置
        composable("wifi_config") {
            WifiConfigScreen(robotViewModel)
        }

        // 蓝牙连接
        composable("bluetooth_connection") {
            BluetoothConnectionScreen(navController, robotViewModel)
        }

        // BLE 调试终端
        composable("ble_debug") {
            BleDebugScreen(navController, robotViewModel)
        }
    }
}
