package com.rehab.robotarm

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.rememberNavController
import com.rehab.robotarm.data.database.AppDatabase
import com.rehab.robotarm.data.repository.*
import com.rehab.robotarm.data.communication.*
import com.rehab.robotarm.data.cloud.OpenClawService
import com.rehab.robotarm.ui.navigation.AppNavigation
import com.rehab.robotarm.ui.theme.RehabRobotArmTheme
import com.rehab.robotarm.viewmodel.*

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // 初始化数据库
        val database = AppDatabase.getDatabase(applicationContext)

        // 初始化Repositories
        val userRepository = UserRepository(
            database.userDao(),
            database.userProfileDao()
        )
        val patientRepository = PatientRepository(database.patientDao())
        val trainingRepository = TrainingRepository(
            database.trainingSessionDao(),
            database.trainingRecordDao(),
            database.trainingPlanDao()
        )
        val leaderboardRepository = LeaderboardRepository(
            database.leaderboardDao(),
            database.achievementDao()
        )

        // 初始化通信管理器
        val communicationManager = CommunicationManager(applicationContext)

        setContent {
            RehabRobotArmTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()

                    // 创建ViewModels
                    val authViewModel = AuthViewModel(userRepository)
                    val patientViewModel = PatientViewModel(patientRepository)
                    val trainingViewModel = TrainingViewModel(trainingRepository)
                    val leaderboardViewModel = LeaderboardViewModel(
                        leaderboardRepository,
                        userRepository
                    )
                    val gameViewModel = GameViewModel()
                    val robotViewModel = RobotViewModel(application)

                    AppNavigation(
                        navController = navController,
                        authViewModel = authViewModel,
                        patientViewModel = patientViewModel,
                        trainingViewModel = trainingViewModel,
                        leaderboardViewModel = leaderboardViewModel,
                        gameViewModel = gameViewModel,
                        robotViewModel = robotViewModel
                    )
                }
            }
        }
    }
}
