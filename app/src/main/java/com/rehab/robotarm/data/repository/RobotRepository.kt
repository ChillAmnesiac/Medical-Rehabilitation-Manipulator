package com.rehab.robotarm.data.repository

import android.content.Context
import com.rehab.robotarm.data.ai.AIInferenceEngine
import com.rehab.robotarm.data.cloud.CloudAIService
import com.rehab.robotarm.data.communication.BluetoothManager
import com.rehab.robotarm.data.communication.HttpManager
import com.rehab.robotarm.data.communication.ProtocolParser
import com.rehab.robotarm.data.model.*
import kotlinx.coroutines.flow.*

/**
 * 数据仓库
 * 统一管理所有数据源和业务逻辑
 */
class RobotRepository(context: Context) {

    private val bluetoothManager = BluetoothManager(context)
    private val httpManager = HttpManager()
    private val protocolParser = ProtocolParser()
    private val aiEngine = AIInferenceEngine(context)
    private val cloudService = CloudAIService()

    // 通信模式：true=HTTP, false=Bluetooth
    private var useHttpMode = true

    private val _robotState = MutableStateFlow(RobotState())
    val robotState: StateFlow<RobotState> = _robotState

    private val _sensorDataHistory = MutableStateFlow<List<SensorData>>(emptyList())
    val sensorDataHistory: StateFlow<List<SensorData>> = _sensorDataHistory

    private val _rehabAnalysis = MutableStateFlow<RehabAnalysis?>(null)
    val rehabAnalysis: StateFlow<RehabAnalysis?> = _rehabAnalysis

    private val _memoryActions = MutableStateFlow<List<MemoryAction>>(emptyList())
    val memoryActions: StateFlow<List<MemoryAction>> = _memoryActions

    private val _cloudAdvice = MutableStateFlow<String>("")
    val cloudAdvice: StateFlow<String> = _cloudAdvice

    init {
        // 初始化AI引擎
        aiEngine.initialize()

        // 监听蓝牙连接状态
        bluetoothManager.connectionState.onEach { state ->
            if (!useHttpMode) {
                _robotState.update { it.copy(isConnected = state == BluetoothManager.ConnectionState.CONNECTED) }
            }
        }.launchIn(kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Default))

        // 监听HTTP连接状态
        httpManager.connectionState.onEach { state ->
            if (useHttpMode) {
                _robotState.update { it.copy(isConnected = state == HttpManager.ConnectionState.CONNECTED) }
            }
        }.launchIn(kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Default))

        // 监听蓝牙接收到的数据
        bluetoothManager.receivedData.onEach { data ->
            if (!useHttpMode) {
                data?.let {
                    val sensorData = protocolParser.parseSensorData(it)
                    sensorData?.let { sensor ->
                        _robotState.update { state -> state.copy(sensorData = sensor) }
                        addSensorDataToHistory(sensor)
                    }
                }
            }
        }.launchIn(kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Default))

        // 监听HTTP接收到的数据
        httpManager.receivedData.onEach { data ->
            if (useHttpMode) {
                android.util.Log.d("RobotRepository", "Received HTTP data: ${data?.size ?: 0} bytes")
                data?.let {
                    val sensorData = protocolParser.parseSensorData(it)
                    sensorData?.let { sensor ->
                        android.util.Log.d("RobotRepository", "Updated sensor data: shoulder=${sensor.shoulderAngle}")

                        // 同时解析mode字段并更新状态
                        try {
                            val jsonString = String(it)
                            val dataMap = com.google.gson.Gson().fromJson(jsonString, Map::class.java)
                            val modeStr = dataMap["mode"] as? String
                            val mode = when(modeStr?.uppercase()) {
                                "ACTIVE" -> RobotMode.ACTIVE
                                "PASSIVE" -> RobotMode.PASSIVE
                                "MEMORY" -> RobotMode.MEMORY
                                else -> null
                            }

                            _robotState.update { state ->
                                state.copy(
                                    sensorData = sensor,
                                    mode = mode ?: state.mode  // 如果解析失败，保持原有模式
                                )
                            }
                        } catch (e: Exception) {
                            // 如果解析mode失败，只更新传感器数据
                            _robotState.update { state -> state.copy(sensorData = sensor) }
                        }

                        addSensorDataToHistory(sensor)
                    }
                }
            }
        }.launchIn(kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Default))
    }

    /**
     * 设置通信模式
     */
    fun setHttpMode(enabled: Boolean) {
        useHttpMode = enabled
    }

    /**
     * 设置PSoC Edge HTTP地址
     */
    fun setPSoCUrl(url: String) {
        httpManager.setPSoCUrl(url)
    }

    /**
     * 连接PSoC Edge (HTTP模式)
     */
    suspend fun connectPSoC(): Boolean {
        val success = httpManager.checkConnection()
        if (success) {
            httpManager.startPolling(100) // 100ms轮询间隔
        }
        return success
    }

    /**
     * 断开PSoC Edge连接
     */
    fun disconnectPSoC() {
        httpManager.disconnect()
    }

    /**
     * 扫描蓝牙设备
     */
    suspend fun scanBluetoothDevices() = bluetoothManager.scanDevices()

    /**
     * 连接设备
     */
    suspend fun connectDevice(device: android.bluetooth.BluetoothDevice) =
        bluetoothManager.connect(device)

    /**
     * 断开连接
     */
    fun disconnectDevice() = bluetoothManager.disconnect()

    /**
     * 切换模式（新版本，支持主模式和子模式）
     */
    suspend fun setMode(
        mainMode: MainMode,
        activeSubMode: ActiveSubMode? = null,
        passiveSubMode: PassiveSubMode? = null,
        memorySubMode: MemorySubMode? = null
    ): Boolean {
        android.util.Log.d("RobotRepository", "Setting mode: main=$mainMode, active=$activeSubMode, passive=$passiveSubMode, memory=$memorySubMode")

        // 更新UI状态
        _robotState.update {
            it.copy(
                mainMode = mainMode,
                activeSubMode = activeSubMode ?: it.activeSubMode,
                passiveSubMode = passiveSubMode ?: it.passiveSubMode,
                memorySubMode = memorySubMode ?: it.memorySubMode,
                mode = when(mainMode) {
                    MainMode.ACTIVE -> RobotMode.ACTIVE
                    MainMode.PASSIVE -> RobotMode.PASSIVE
                    MainMode.MEMORY -> RobotMode.MEMORY
                }
            )
        }

        // 如果已连接，则发送命令到设备
        if (_robotState.value.isConnected) {
            val mode = when(mainMode) {
                MainMode.ACTIVE -> RobotMode.ACTIVE
                MainMode.PASSIVE -> RobotMode.PASSIVE
                MainMode.MEMORY -> RobotMode.MEMORY
            }
            val command = protocolParser.buildModeCommand(mode)
            val success = if (useHttpMode) {
                httpManager.sendData(command)
            } else {
                bluetoothManager.sendData(command)
            }
            android.util.Log.d("RobotRepository", "Mode switch command sent: $success")
            return success
        }
        return true
    }

    /**
     * 切换模式（旧版本，兼容性）
     */
    suspend fun switchMode(mode: RobotMode): Boolean {
        android.util.Log.d("RobotRepository", "Switching mode to: $mode, useHttpMode=$useHttpMode, isConnected=${_robotState.value.isConnected}")

        // 先更新UI状态（即使未连接也允许切换）
        _robotState.update { it.copy(mode = mode) }

        // 如果已连接，则发送命令到设备
        if (_robotState.value.isConnected) {
            val command = protocolParser.buildModeCommand(mode)
            android.util.Log.d("RobotRepository", "Mode command built: ${String(command)}")
            val success = if (useHttpMode) {
                httpManager.sendData(command)
            } else {
                bluetoothManager.sendData(command)
            }
            android.util.Log.d("RobotRepository", "Mode switch command sent: $success")
            return success
        } else {
            android.util.Log.d("RobotRepository", "Not connected, only updating UI")
            return true
        }
    }

    /**
     * 发送控制命令（被动模式）
     */
    suspend fun sendControlCommand(command: ControlCommand): Boolean {
        val data = protocolParser.buildControlCommand(command)
        return if (useHttpMode) {
            httpManager.sendData(data)
        } else {
            bluetoothManager.sendData(data)
        }
    }

    /**
     * 保存记忆动作
     */
    fun saveMemoryAction(action: MemoryAction) {
        _memoryActions.update { it + action }
    }

    /**
     * 执行记忆动作
     */
    suspend fun executeMemoryAction(actionId: String): Boolean {
        val action = _memoryActions.value.find { it.id == actionId } ?: return false
        val command = protocolParser.buildMemoryCommand(action)
        val success = if (useHttpMode) {
            httpManager.sendData(command)
        } else {
            bluetoothManager.sendData(command)
        }
        if (success) {
            _robotState.update { it.copy(currentMemoryAction = actionId) }
        }
        return success
    }

    /**
     * 停止记忆动作
     */
    suspend fun stopMemoryAction(): Boolean {
        val stopCommand = """{"type":"stop_memory"}""".toByteArray()
        val success = if (useHttpMode) {
            httpManager.sendData(stopCommand)
        } else {
            bluetoothManager.sendData(stopCommand)
        }
        if (success) {
            _robotState.update { it.copy(currentMemoryAction = null) }
        }
        return success
    }

    /**
     * 添加传感器数据到历史记录
     */
    private fun addSensorDataToHistory(data: SensorData) {
        _sensorDataHistory.update { history ->
            (history + data).takeLast(1000) // 保留最近1000条数据
        }

        // 每收集50条数据进行一次AI分析
        if (_sensorDataHistory.value.size % 50 == 0) {
            performAIAnalysis()
        }
    }

    /**
     * 执行AI分析
     */
    private fun performAIAnalysis() {
        val analysis = aiEngine.analyzeRehabProgress(_sensorDataHistory.value)
        _rehabAnalysis.value = analysis
    }

    /**
     * 获取云端建议
     */
    suspend fun fetchCloudAdvice() {
        val analysis = _rehabAnalysis.value ?: return

        // 优先使用真实API，失败则使用模拟数据
        val advice = try {
            cloudService.getRehabAdvice(
                analysis.smoothness,
                analysis.rangeOfMotion,
                analysis.strength,
                analysis.overallScore
            )
        } catch (e: Exception) {
            cloudService.getMockAdvice(analysis.overallScore)
        }

        _cloudAdvice.value = advice
    }

    /**
     * 清空历史数据
     */
    fun clearHistory() {
        _sensorDataHistory.value = emptyList()
        _rehabAnalysis.value = null
    }

    /**
     * 释放资源
     */
    fun release() {
        aiEngine.release()
        bluetoothManager.disconnect()
        httpManager.disconnect()
    }
}
