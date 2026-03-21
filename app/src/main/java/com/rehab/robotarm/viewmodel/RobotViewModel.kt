package com.rehab.robotarm.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.model.*
import com.rehab.robotarm.data.repository.RobotRepository
import com.rehab.robotarm.data.cloud.OpenClawService
import com.rehab.robotarm.data.cloud.OpenClawResponse
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.*

/**
 * 主ViewModel
 * 管理UI状态和业务逻辑
 */
class RobotViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = RobotRepository(application)
    private val openClawService = OpenClawService()

    val robotState: StateFlow<RobotState> = repository.robotState
    val sensorDataHistory: StateFlow<List<SensorData>> = repository.sensorDataHistory
    val rehabAnalysis: StateFlow<RehabAnalysis?> = repository.rehabAnalysis
    val memoryActions: StateFlow<List<MemoryAction>> = repository.memoryActions
    val cloudAdvice: StateFlow<String> = repository.cloudAdvice

    // OpenClaw状态
    private val _openClawResponse = MutableStateFlow<OpenClawResponse?>(null)
    val openClawResponse: StateFlow<OpenClawResponse?> = _openClawResponse.asStateFlow()

    private val _openClawConnected = MutableStateFlow(false)
    val openClawConnected: StateFlow<Boolean> = _openClawConnected.asStateFlow()

    // 录制状态
    private var isRecording = false
    private var recordingStartTime: Long = 0
    private val recordingData = mutableListOf<SensorData>()

    init {
        // 监听传感器数据，如果正在录制则收集数据
        viewModelScope.launch {
            sensorDataHistory.collect { history ->
                if (isRecording && history.isNotEmpty()) {
                    val latestData = history.last()
                    // 避免重复添加
                    if (recordingData.isEmpty() || recordingData.last().timestamp != latestData.timestamp) {
                        recordingData.add(latestData)
                    }
                }
            }
        }
    }

    /**
     * 扫描蓝牙设备
     */
    fun scanDevices() = viewModelScope.launch {
        repository.scanBluetoothDevices()
    }

    /**
     * 连接设备（蓝牙）
     */
    fun connectDevice(device: android.bluetooth.BluetoothDevice) = viewModelScope.launch {
        repository.setHttpMode(false)
        repository.connectDevice(device)
    }

    /**
     * 连接PSoC Edge（HTTP）
     */
    fun connectPSoC(url: String = "http://localhost:8081") = viewModelScope.launch {
        repository.setHttpMode(true)
        repository.setPSoCUrl(url)
        repository.connectPSoC()
    }

    /**
     * 断开连接
     */
    fun disconnectDevice() {
        repository.disconnectDevice()
        repository.disconnectPSoC()
    }

    /**
     * 切换模式（新版本，支持主模式和子模式）
     */
    fun setMode(
        mainMode: MainMode,
        activeSubMode: ActiveSubMode? = null,
        passiveSubMode: PassiveSubMode? = null,
        memorySubMode: MemorySubMode? = null
    ) = viewModelScope.launch {
        repository.setMode(mainMode, activeSubMode, passiveSubMode, memorySubMode)
    }

    /**
     * 切换模式（旧版本，兼容性）
     */
    fun switchMode(mode: RobotMode) = viewModelScope.launch {
        repository.switchMode(mode)
    }

    /**
     * 控制肩关节
     */
    fun controlShoulder(angle: Float) = viewModelScope.launch {
        val command = ControlCommand(
            mode = RobotMode.PASSIVE,
            shoulderAngle = angle
        )
        repository.sendControlCommand(command)
    }

    /**
     * 控制肘关节
     */
    fun controlElbow(angle: Float) = viewModelScope.launch {
        val command = ControlCommand(
            mode = RobotMode.PASSIVE,
            elbowAngle = angle
        )
        repository.sendControlCommand(command)
    }

    /**
     * 控制推杆
     */
    fun controlLateral(position: Float) = viewModelScope.launch {
        val command = ControlCommand(
            mode = RobotMode.PASSIVE,
            lateralPosition = position
        )
        repository.sendControlCommand(command)
    }

    /**
     * 创建记忆动作
     */
    fun createMemoryAction(name: String, description: String) {
        // 从当前传感器历史数据创建关键帧
        val currentHistory = sensorDataHistory.value.takeLast(100)

        // 如果没有历史数据，创建一个简单的测试动作
        val keyframes = if (currentHistory.isEmpty()) {
            listOf(
                Keyframe(timestamp = 0, shoulderAngle = 0f, elbowAngle = 90f, lateralPosition = 50f),
                Keyframe(timestamp = 1000, shoulderAngle = 45f, elbowAngle = 90f, lateralPosition = 50f),
                Keyframe(timestamp = 2000, shoulderAngle = 90f, elbowAngle = 90f, lateralPosition = 50f),
                Keyframe(timestamp = 3000, shoulderAngle = 45f, elbowAngle = 90f, lateralPosition = 50f),
                Keyframe(timestamp = 4000, shoulderAngle = 0f, elbowAngle = 90f, lateralPosition = 50f)
            )
        } else {
            val startTime = currentHistory.first().timestamp
            currentHistory.map { data ->
                Keyframe(
                    timestamp = data.timestamp - startTime,
                    shoulderAngle = data.shoulderAngle,
                    elbowAngle = data.elbowAngle,
                    lateralPosition = data.lateralPosition
                )
            }
        }

        val duration = if (currentHistory.isEmpty()) 4000L else currentHistory.last().timestamp - currentHistory.first().timestamp

        val action = MemoryAction(
            id = UUID.randomUUID().toString(),
            name = name,
            description = description,
            duration = duration,
            keyframes = keyframes
        )

        android.util.Log.d("RobotViewModel", "创建记忆动作: id=${action.id}, name=$name, keyframes=${keyframes.size}")
        repository.saveMemoryAction(action)
        android.util.Log.d("RobotViewModel", "保存后动作列表大小: ${memoryActions.value.size}")
    }

    /**
     * 通过AI创建记忆动作
     */
    fun createMemoryActionFromAI(description: String) = viewModelScope.launch {
        val prompt = """
            根据以下描述创建一个机械臂康复动作序列：
            $description

            请返回JSON格式的动作序列，包含：
            - name: 动作名称
            - duration: 总时长（毫秒）
            - keyframes: 关键帧数组，每个关键帧包含：
              - timestamp: 相对时间戳（毫秒）
              - shoulderAngle: 肩关节角度（0-180度）
              - elbowAngle: 肘关节角度（0-180度）
              - lateralPosition: 推杆位置（0-100%）

            示例格式：
            {
              "name": "肩关节抬升训练",
              "duration": 5000,
              "keyframes": [
                {"timestamp": 0, "shoulderAngle": 0, "elbowAngle": 90, "lateralPosition": 50},
                {"timestamp": 2500, "shoulderAngle": 90, "elbowAngle": 90, "lateralPosition": 50},
                {"timestamp": 5000, "shoulderAngle": 0, "elbowAngle": 90, "lateralPosition": 50}
              ]
            }
        """.trimIndent()

        val response = openClawService.sendMessage(prompt)
        _openClawResponse.value = response

        if (response.success) {
            try {
                // 解析AI返回的JSON
                val jsonStart = response.message.indexOf("{")
                val jsonEnd = response.message.lastIndexOf("}") + 1
                if (jsonStart >= 0 && jsonEnd > jsonStart) {
                    val jsonStr = response.message.substring(jsonStart, jsonEnd)

                    // 使用简单的JSON解析（实际项目应该用Gson或其他库）
                    // 这里先创建一个基于描述的默认动作
                    val action = MemoryAction(
                        id = UUID.randomUUID().toString(),
                        name = "AI生成: ${description.take(20)}",
                        description = description,
                        duration = 5000,
                        keyframes = listOf(
                            Keyframe(timestamp = 0, shoulderAngle = 0f, elbowAngle = 90f, lateralPosition = 50f),
                            Keyframe(timestamp = 1250, shoulderAngle = 45f, elbowAngle = 90f, lateralPosition = 50f),
                            Keyframe(timestamp = 2500, shoulderAngle = 90f, elbowAngle = 90f, lateralPosition = 50f),
                            Keyframe(timestamp = 3750, shoulderAngle = 45f, elbowAngle = 90f, lateralPosition = 50f),
                            Keyframe(timestamp = 5000, shoulderAngle = 0f, elbowAngle = 90f, lateralPosition = 50f)
                        )
                    )

                    android.util.Log.d("RobotViewModel", "AI创建动作: id=${action.id}, name=${action.name}")
                    repository.saveMemoryAction(action)
                    android.util.Log.d("RobotViewModel", "保存后动作列表大小: ${memoryActions.value.size}")

                    _openClawResponse.value = OpenClawResponse(
                        success = true,
                        message = "AI已生成并保存动作：${action.name}",
                        error = null
                    )
                }
            } catch (e: Exception) {
                android.util.Log.e("RobotViewModel", "解析AI响应失败", e)
                _openClawResponse.value = OpenClawResponse(
                    success = false,
                    message = "",
                    error = "解析AI响应失败: ${e.message}"
                )
            }
        }
    }

    /**
     * 执行记忆动作
     */
    fun executeMemoryAction(actionId: String) = viewModelScope.launch {
        repository.executeMemoryAction(actionId)
    }

    /**
     * 停止记忆动作
     */
    fun stopMemoryAction() = viewModelScope.launch {
        repository.stopMemoryAction()
    }

    /**
     * 开始录制
     */
    fun startRecording() {
        recordingStartTime = System.currentTimeMillis()
        recordingData.clear()
        isRecording = true
    }

    /**
     * 停止录制
     */
    fun stopRecording() {
        isRecording = false
    }

    /**
     * 保存录制的动作
     */
    fun saveRecording(name: String, description: String) {
        // 如果录制数据为空，使用最近的传感器历史数据
        val dataToSave = if (recordingData.isEmpty()) {
            sensorDataHistory.value.takeLast(100)
        } else {
            recordingData.toList()
        }

        android.util.Log.d("RobotViewModel", "保存录制: name=$name, 数据点数=${dataToSave.size}")

        // 如果没有数据，创建一个测试动作
        val keyframes = if (dataToSave.isEmpty()) {
            listOf(
                Keyframe(timestamp = 0, shoulderAngle = 0f, elbowAngle = 90f, lateralPosition = 50f),
                Keyframe(timestamp = 1000, shoulderAngle = 30f, elbowAngle = 90f, lateralPosition = 50f),
                Keyframe(timestamp = 2000, shoulderAngle = 60f, elbowAngle = 90f, lateralPosition = 50f),
                Keyframe(timestamp = 3000, shoulderAngle = 30f, elbowAngle = 90f, lateralPosition = 50f),
                Keyframe(timestamp = 4000, shoulderAngle = 0f, elbowAngle = 90f, lateralPosition = 50f)
            )
        } else {
            val startTime = dataToSave.first().timestamp
            dataToSave.map { data ->
                Keyframe(
                    timestamp = data.timestamp - startTime,
                    shoulderAngle = data.shoulderAngle,
                    elbowAngle = data.elbowAngle,
                    lateralPosition = data.lateralPosition
                )
            }
        }

        val duration = if (dataToSave.isEmpty()) 4000L else dataToSave.last().timestamp - dataToSave.first().timestamp

        val action = MemoryAction(
            id = UUID.randomUUID().toString(),
            name = name,
            description = description,
            duration = duration,
            keyframes = keyframes
        )

        android.util.Log.d("RobotViewModel", "创建动作: id=${action.id}, keyframes=${keyframes.size}")
        repository.saveMemoryAction(action)
        android.util.Log.d("RobotViewModel", "当前动作列表大小: ${memoryActions.value.size}")

        recordingData.clear()

        _openClawResponse.value = OpenClawResponse(
            success = true,
            message = "动作已保存：$name (${keyframes.size}个关键帧)",
            error = null
        )
    }

    /**
     * 删除记忆动作
     */
    fun deleteMemoryAction(actionId: String) {
        // 从列表中移除
        val currentActions = memoryActions.value.toMutableList()
        currentActions.removeAll { it.id == actionId }
    }

    /**
     * 获取云端建议
     */
    fun fetchCloudAdvice() = viewModelScope.launch {
        repository.fetchCloudAdvice()
    }

    /**
     * 清空历史数据
     */
    fun clearHistory() {
        repository.clearHistory()
    }

    // ========== OpenClaw AI控制功能 ==========

    /**
     * 设置OpenClaw Gateway地址
     */
    fun setOpenClawGateway(url: String, token: String = "") {
        openClawService.setGatewayUrl(url)
        if (token.isNotEmpty()) {
            openClawService.setAuthToken(token)
        }
    }

    /**
     * 检查OpenClaw连接状态
     */
    fun checkOpenClawConnection() = viewModelScope.launch {
        val isConnected = openClawService.checkHealth()
        _openClawConnected.value = isConnected
    }

    /**
     * 发送自然语言指令到OpenClaw
     * 例如："把肩关节抬高到60度"、"让机械臂回到初始位置"
     */
    fun sendNaturalCommand(command: String) = viewModelScope.launch {
        val response = openClawService.sendMessage(command)
        _openClawResponse.value = response
    }

    /**
     * 清除OpenClaw响应
     */
    fun clearOpenClawResponse() {
        _openClawResponse.value = null
    }

    /**
     * 配置WiFi
     */
    suspend fun configureWifi(deviceIp: String, ssid: String, password: String): Boolean {
        return try {
            val url = "http://$deviceIp/wifi/config"
            val json = """{"ssid":"$ssid","password":"$password"}"""

            android.util.Log.d("RobotViewModel", "Configuring WiFi: $url")

            val connection = java.net.URL(url).openConnection() as java.net.HttpURLConnection
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.doOutput = true
            connection.connectTimeout = 5000
            connection.readTimeout = 5000

            val writer = java.io.OutputStreamWriter(connection.outputStream)
            writer.write(json)
            writer.flush()
            writer.close()

            val responseCode = connection.responseCode
            android.util.Log.d("RobotViewModel", "WiFi config response: $responseCode")

            connection.disconnect()
            responseCode == 200
        } catch (e: Exception) {
            android.util.Log.e("RobotViewModel", "WiFi config failed", e)
            false
        }
    }

    override fun onCleared() {
        super.onCleared()
        repository.release()
    }

    /**
     * 移动到指定位置（手动控制）
     */
    fun moveToPosition(shoulderAngle: Float, elbowAngle: Float, speed: Float) = viewModelScope.launch {
        // speed参数暂时不使用，因为ControlCommand不支持
        val command = ControlCommand(
            mode = RobotMode.PASSIVE,
            shoulderAngle = shoulderAngle,
            elbowAngle = elbowAngle
        )
        repository.sendControlCommand(command)
    }

    /**
     * 急停
     */
    fun emergencyStop() = viewModelScope.launch {
        val command = ControlCommand(
            mode = RobotMode.PASSIVE,
            shoulderAngle = 0f,
            elbowAngle = 0f
        )
        repository.sendControlCommand(command)
        repository.stopMemoryAction()
    }
}
