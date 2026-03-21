package com.rehab.robotarm.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.database.entity.LeaderboardEntry
import com.rehab.robotarm.data.repository.LeaderboardRepository
import com.rehab.robotarm.data.repository.UserRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class LeaderboardViewModel(
    private val leaderboardRepository: LeaderboardRepository,
    private val userRepository: UserRepository
) : ViewModel() {

    private val _leaderboard = MutableStateFlow<List<LeaderboardEntry>>(emptyList())
    val leaderboard: StateFlow<List<LeaderboardEntry>> = _leaderboard

    private val _myRank = MutableStateFlow<LeaderboardEntry?>(null)
    val myRank: StateFlow<LeaderboardEntry?> = _myRank

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    // 加载排行榜
    fun loadLeaderboard(category: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                // 启动一个新的协程来收集数据流
                launch {
                    leaderboardRepository.getLeaderboard(category, 100).collect { entries ->
                        _leaderboard.value = entries

                        // 如果数据为空，添加一些测试数据
                        if (entries.isEmpty()) {
                            initializeDemoData(category)
                        }
                    }
                }

                // 获取我的排名
                val currentUser = userRepository.getCurrentUser()
                if (currentUser != null) {
                    val myEntry = leaderboardRepository.getUserRank(currentUser.id, category)
                    _myRank.value = myEntry
                } else {
                    // 如果没有登录用户，创建一个演示排名
                    _myRank.value = LeaderboardEntry(
                        userId = "current_user",
                        username = "我",
                        score = 3200,
                        level = 10,
                        totalSessions = 45,
                        totalDuration = 15000,
                        maxAngle = 145f,
                        bestGameScore = 3500,
                        achievements = 8,
                        rank = 12,
                        category = category
                    )
                }
            } catch (e: Exception) {
                // 处理错误 - 设置空列表避免崩溃
                _leaderboard.value = emptyList()
                _myRank.value = null
            } finally {
                _isLoading.value = false
            }
        }
    }

    // 初始化演示数据
    private fun initializeDemoData(category: String) {
        viewModelScope.launch {
            try {
                val demoEntries = listOf(
                    LeaderboardEntry(
                        userId = "demo1",
                        username = "康复达人",
                        score = 9500,
                        level = 25,
                        totalSessions = 150,
                        totalDuration = 45000,
                        maxAngle = 175f,
                        bestGameScore = 8500,
                        achievements = 28,
                        rank = 1,
                        category = category
                    ),
                    LeaderboardEntry(
                        userId = "demo2",
                        username = "训练之星",
                        score = 8800,
                        level = 22,
                        totalSessions = 130,
                        totalDuration = 38000,
                        maxAngle = 170f,
                        bestGameScore = 7800,
                        achievements = 24,
                        rank = 2,
                        category = category
                    ),
                    LeaderboardEntry(
                        userId = "demo3",
                        username = "坚持不懈",
                        score = 7600,
                        level = 19,
                        totalSessions = 110,
                        totalDuration = 32000,
                        maxAngle = 165f,
                        bestGameScore = 6900,
                        achievements = 20,
                        rank = 3,
                        category = category
                    ),
                    LeaderboardEntry(
                        userId = "demo4",
                        username = "努力向上",
                        score = 6500,
                        level = 16,
                        totalSessions = 95,
                        totalDuration = 28000,
                        maxAngle = 160f,
                        bestGameScore = 6200,
                        achievements = 18,
                        rank = 4,
                        category = category
                    ),
                    LeaderboardEntry(
                        userId = "demo5",
                        username = "康复新星",
                        score = 5400,
                        level = 14,
                        totalSessions = 80,
                        totalDuration = 24000,
                        maxAngle = 155f,
                        bestGameScore = 5500,
                        achievements = 15,
                        rank = 5,
                        category = category
                    )
                )

                demoEntries.forEach { entry ->
                    leaderboardRepository.uploadScore(entry)
                }
            } catch (e: Exception) {
                // 忽略错误
            }
        }
    }

    // 更新我的分数
    fun updateMyScore(userId: String) {
        viewModelScope.launch {
            try {
                val profile = userRepository.getProfile(userId) ?: return@launch

                // 计算综合分数
                val score = calculateScore(
                    profile.totalTrainingSessions,
                    profile.totalTrainingTime,
                    profile.level,
                    profile.experience
                )

                val entry = LeaderboardEntry(
                    userId = userId,
                    username = profile.displayName,
                    avatarUrl = null,
                    score = score,
                    level = profile.level,
                    totalSessions = profile.totalTrainingSessions,
                    totalDuration = profile.totalTrainingTime,
                    maxAngle = 0f,
                    bestGameScore = 0,
                    achievements = 0,
                    rank = 0,
                    category = "global"
                )

                leaderboardRepository.uploadScore(entry)
            } catch (e: Exception) {
                // 处理错误
            }
        }
    }

    private fun calculateScore(sessions: Int, time: Long, level: Int, exp: Int): Int {
        return (sessions * 10) + (time / 3600).toInt() + (level * 100) + (exp / 10)
    }

    fun showUserProfile(userId: String) {
        // TODO: 导航到用户资料页面
    }
}
