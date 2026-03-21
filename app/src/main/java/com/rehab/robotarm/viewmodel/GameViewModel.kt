package com.rehab.robotarm.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.model.GameType
import com.rehab.robotarm.data.model.SensorData
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.sqrt
import kotlin.random.Random

class GameViewModel : ViewModel() {

    private val _targets = MutableStateFlow<List<GameTarget>>(emptyList())
    val targets: StateFlow<List<GameTarget>> = _targets

    private val _score = MutableStateFlow(0)
    val score: StateFlow<Int> = _score

    private val _gameState = MutableStateFlow<GameState>(GameState.Idle)
    val gameState: StateFlow<GameState> = _gameState

    private val _currentAngle = MutableStateFlow(0f)
    val currentAngle: StateFlow<Float> = _currentAngle

    private val _timeRemaining = MutableStateFlow(60)
    val timeRemaining: StateFlow<Int> = _timeRemaining

    private val _currentGameType = MutableStateFlow<GameType?>(null)
    val currentGameType: StateFlow<GameType?> = _currentGameType

    // 新增：当前手臂末端位置（从运动学逆解获得）
    private val _currentPosition = MutableStateFlow(Position2D(0f, 0f))
    val currentPosition: StateFlow<Position2D> = _currentPosition

    // 新增：3D位置支持
    private val _currentPosition3D = MutableStateFlow(Position3D(0f, 0f, 0f))
    val currentPosition3D: StateFlow<Position3D> = _currentPosition3D

    fun selectGameType(gameType: GameType) {
        _currentGameType.value = gameType
    }

    fun startGame(difficulty: String = "medium", gameType: GameType = GameType.FRUIT_NINJA) {
        viewModelScope.launch {
            _currentGameType.value = gameType
            _gameState.value = GameState.Playing
            _score.value = 0
            _timeRemaining.value = 60
            generateTargets(difficulty, gameType)
        }
    }

    fun pauseGame() {
        _gameState.value = GameState.Paused
    }

    fun resumeGame() {
        _gameState.value = GameState.Playing
    }

    fun stopGame() {
        _gameState.value = GameState.Finished
    }

    /**
     * 更新传感器数据（旧版本，基于角度）
     */
    fun updateSensorData(sensorData: SensorData) {
        _currentAngle.value = sensorData.shoulderAngle
        checkHits(sensorData.shoulderAngle)
    }

    /**
     * 更新手臂末端位置（新版本，基于坐标）
     * @param x X坐标（单位：米或厘米）
     * @param y Y坐标
     */
    fun updateArmPosition(x: Float, y: Float) {
        _currentPosition.value = Position2D(x, y)
        checkHitsByPosition(x, y)
    }

    /**
     * 更新手臂末端3D位置
     * @param x X坐标
     * @param y Y坐标
     * @param z Z坐标（高度）
     */
    fun updateArmPosition3D(x: Float, y: Float, z: Float) {
        _currentPosition3D.value = Position3D(x, y, z)
        checkHitsByPosition3D(x, y, z)
    }

    /**
     * 从传感器数据计算末端位置（运动学正解）
     * 这里提供一个简化的2连杆正解示例
     */
    fun updateFromSensorData(sensorData: SensorData, l1: Float = 0.3f, l2: Float = 0.25f) {
        val theta1 = Math.toRadians(sensorData.shoulderAngle.toDouble())
        val theta2 = Math.toRadians(sensorData.elbowAngle.toDouble())

        // 2连杆正解
        val x = (l1 * kotlin.math.cos(theta1) + l2 * kotlin.math.cos(theta1 + theta2)).toFloat()
        val y = (l1 * kotlin.math.sin(theta1) + l2 * kotlin.math.sin(theta1 + theta2)).toFloat()

        updateArmPosition(x, y)
        _currentAngle.value = sensorData.shoulderAngle
    }

    private fun generateTargets(difficulty: String, gameType: GameType) {
        val targetCount = when (difficulty) {
            "easy" -> 5
            "medium" -> 8
            "hard" -> 12
            else -> 8
        }

        val newTargets = mutableListOf<GameTarget>()

        when (gameType) {
            GameType.FRUIT_NINJA, GameType.WHACK_A_MOLE -> {
                // 2D坐标游戏：在工作空间内随机生成目标
                for (i in 0 until targetCount) {
                    newTargets.add(
                        GameTarget(
                            id = i,
                            angle = Random.nextFloat() * 180f,
                            position = Position2D(
                                x = Random.nextFloat() * 0.5f + 0.1f, // 0.1-0.6米范围
                                y = Random.nextFloat() * 0.4f + 0.1f  // 0.1-0.5米范围
                            ),
                            score = Random.nextInt(10, 50),
                            isHit = false
                        )
                    )
                }
            }
            GameType.RHYTHM_MASTER -> {
                // 节奏游戏：按时间序列生成目标
                for (i in 0 until targetCount) {
                    newTargets.add(
                        GameTarget(
                            id = i,
                            angle = Random.nextFloat() * 180f,
                            position = Position2D(
                                x = Random.nextFloat() * 0.5f + 0.1f,
                                y = Random.nextFloat() * 0.4f + 0.1f
                            ),
                            score = 20,
                            isHit = false,
                            appearTime = i * 2000L // 每2秒出现一个
                        )
                    )
                }
            }
            GameType.FLIGHT_SIM -> {
                // 飞行游戏：生成障碍物
                for (i in 0 until targetCount) {
                    newTargets.add(
                        GameTarget(
                            id = i,
                            angle = Random.nextFloat() * 180f,
                            position = Position2D(
                                x = 0.3f + i * 0.05f,
                                y = Random.nextFloat() * 0.4f + 0.1f
                            ),
                            score = 10,
                            isHit = false
                        )
                    )
                }
            }
        }
        _targets.value = newTargets
    }

    /**
     * 基于角度检测碰撞（旧版本）
     */
    private fun checkHits(currentAngle: Float) {
        val updatedTargets = _targets.value.map { target ->
            if (!target.isHit && abs(currentAngle - target.angle) < 5f) {
                _score.value += target.score
                target.copy(isHit = true)
            } else {
                target
            }
        }
        _targets.value = updatedTargets

        // 检查是否所有目标都被击中
        if (updatedTargets.all { it.isHit }) {
            generateTargets("medium", _currentGameType.value ?: GameType.FRUIT_NINJA)
        }
    }

    /**
     * 基于2D坐标检测碰撞（新版本）
     */
    private fun checkHitsByPosition(x: Float, y: Float) {
        val hitRadius = 0.05f // 5厘米碰撞半径

        val updatedTargets = _targets.value.map { target ->
            if (!target.isHit && target.position != null) {
                val distance = sqrt(
                    (x - target.position.x) * (x - target.position.x) +
                    (y - target.position.y) * (y - target.position.y)
                )
                if (distance < hitRadius) {
                    _score.value += target.score
                    target.copy(isHit = true)
                } else {
                    target
                }
            } else {
                target
            }
        }
        _targets.value = updatedTargets

        // 检查是否所有目标都被击中
        if (updatedTargets.all { it.isHit }) {
            generateTargets("medium", _currentGameType.value ?: GameType.FRUIT_NINJA)
        }
    }

    /**
     * 基于3D坐标检测碰撞
     */
    private fun checkHitsByPosition3D(x: Float, y: Float, z: Float) {
        val hitRadius = 0.05f

        val updatedTargets = _targets.value.map { target ->
            if (!target.isHit && target.position3D != null) {
                val distance = sqrt(
                    (x - target.position3D.x) * (x - target.position3D.x) +
                    (y - target.position3D.y) * (y - target.position3D.y) +
                    (z - target.position3D.z) * (z - target.position3D.z)
                )
                if (distance < hitRadius) {
                    _score.value += target.score
                    target.copy(isHit = true)
                } else {
                    target
                }
            } else {
                target
            }
        }
        _targets.value = updatedTargets

        if (updatedTargets.all { it.isHit }) {
            generateTargets("medium", _currentGameType.value ?: GameType.FRUIT_NINJA)
        }
    }

    fun decrementTime() {
        if (_timeRemaining.value > 0) {
            _timeRemaining.value -= 1
        } else {
            stopGame()
        }
    }
}

/**
 * 2D位置
 */
data class Position2D(
    val x: Float,
    val y: Float
)

/**
 * 3D位置
 */
data class Position3D(
    val x: Float,
    val y: Float,
    val z: Float
)

/**
 * 游戏目标
 */
data class GameTarget(
    val id: Int,
    val angle: Float,                    // 角度（兼容旧版本）
    val position: Position2D? = null,    // 2D坐标位置
    val position3D: Position3D? = null,  // 3D坐标位置
    val score: Int,
    val isHit: Boolean = false,
    val appearTime: Long = 0L            // 出现时间（用于节奏游戏）
)

sealed class GameState {
    object Idle : GameState()
    object Playing : GameState()
    object Paused : GameState()
    object Finished : GameState()
}
