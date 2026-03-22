package com.rehab.robotarm.data.communication

import android.content.Context
import com.rehab.robotarm.data.cloud.OpenClawService
import com.rehab.robotarm.data.model.Command
import com.rehab.robotarm.data.model.CommandType
import com.rehab.robotarm.data.model.Response
import com.rehab.robotarm.data.model.SensorData
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow

/**
 * 通信管理器 - 智能路由
 * 根据指令类型自动选择最佳通信通道（蓝牙SPP或HTTP）
 */
class CommunicationManager(
    private val context: Context
) {
    private val openClawService = OpenClawService()
    private val bluetoothSppManager = BluetoothSppManager(context)
    private val psocHttpManager = PsocHttpManager()

    // 兼容旧代码
    private val bluetoothManager = BluetoothManager(context)
    private val httpManager = HttpManager()
    /**
     * 发送指令 - 智能路由
     * @param command 指令对象
     * @return 执行结果
     */
    suspend fun sendCommand(command: Command): Result<Response> {
        return when (command.type) {
            CommandType.REALTIME_CONTROL -> {
                // 简单实时控制 → 蓝牙直连（低延迟）
                bluetoothManager.sendCommand(command)
            }
            CommandType.NATURAL_LANGUAGE -> {
                // 自然语言 → OpenClaw处理
                openClawService.sendNaturalLanguage(command.text ?: "")
            }
            CommandType.COMPLEX_TASK -> {
                // 复杂任务 → OpenClaw + PSoC HTTP桥接
                openClawService.executeTask(command)
            }
            CommandType.HTTP_API -> {
                // 直接HTTP API调用
                httpManager.sendCommand(command)
            }
        }
    }

    /**
     * 启动实时传感器数据流（蓝牙）
     * @param onData 数据回调
     */
    fun startSensorDataStream(onData: (SensorData) -> Unit) {
        bluetoothManager.startListening { bytes ->
            val data = parseSensorData(bytes)
            onData(data)
        }
    }

    /**
     * 停止传感器数据流
     */
    fun stopSensorDataStream() {
        bluetoothManager.stopListening()
    }

    /**
     * 获取康复评估（OpenClaw）
     */
    suspend fun getRehabAssessment(sessionId: String): Result<String> {
        return openClawService.getRehabAnalysis(sessionId)
    }

    /**
     * 连接蓝牙设备
     */
    suspend fun connectBluetooth(deviceAddress: String): Result<Boolean> {
        return bluetoothManager.connect(deviceAddress)
    }

    /**
     * 断开蓝牙连接
     */
    fun disconnectBluetooth() {
        bluetoothManager.disconnect()
    }

    /**
     * 检查蓝牙连接状态
     */
    fun isBluetoothConnected(): Boolean {
        return bluetoothManager.isConnected()
    }

    /**
     * 解析传感器数据
     */
    private fun parseSensorData(bytes: ByteArray): SensorData {
        // 协议格式: [Header(2)] [Type(1)] [Data(N)] [Checksum(1)]
        // 参考 PROTOCOL.md
        return try {
            val parser = ProtocolParser()
            parser.parseSensorData(bytes) ?: SensorData()
        } catch (e: Exception) {
            SensorData() // 返回空数据
        }
    }

    /**
     * 获取设备状态
     */
    suspend fun getDeviceStatus(): Result<Map<String, Any>> {
        return httpManager.getStatus()
    }

    /**
     * 设置 PSoC HTTP 地址
     */
    fun setPsocUrl(url: String) {
        psocHttpManager.setBaseUrl(url)
        httpManager.setPSoCUrl(url)
    }

    /**
     * 设置 OpenClaw 地址
     */
    fun setOpenClawUrl(url: String) {
        openClawService.setBaseUrl(url)
    }

    /**
     * 获取蓝牙连接状态
     */
    val bluetoothConnectionState: StateFlow<BluetoothSppManager.ConnectionState>
        get() = bluetoothSppManager.connectionState

    /**
     * 获取实时传感器数据流
     */
    val sensorDataFlow: StateFlow<SensorData?>
        get() = bluetoothSppManager.sensorData

    /**
     * 移动关节（蓝牙SPP - 低延迟）
     */
    suspend fun moveJoint(jointId: Int, angle: Float, speed: Float = 30f): Boolean {
        return bluetoothSppManager.moveJoint(jointId, angle, speed)
    }

    /**
     * 设置工作模式（蓝牙SPP）
     */
    suspend fun setMode(mode: String): Boolean {
        val robotMode = when (mode.uppercase()) {
            "ACTIVE" -> BluetoothSppManager.RobotMode.ACTIVE
            "PASSIVE" -> BluetoothSppManager.RobotMode.PASSIVE
            "ASSIST" -> BluetoothSppManager.RobotMode.ASSIST
            "RESIST" -> BluetoothSppManager.RobotMode.RESIST
            "MEMORY" -> BluetoothSppManager.RobotMode.MEMORY
            "GAME" -> BluetoothSppManager.RobotMode.GAME
            else -> return false
        }
        return bluetoothSppManager.setMode(robotMode)
    }

    /**
     * 紧急停止
     */
    suspend fun emergencyStop(): Boolean {
        return bluetoothSppManager.emergencyStop()
    }

    /**
     * 执行记忆动作
     */
    suspend fun executeMemory(memoryId: String): Boolean {
        return bluetoothSppManager.executeMemory(memoryId)
    }

    /**
     * 检查 PSoC HTTP 连接
     */
    suspend fun checkPsocConnection(): Result<Boolean> {
        return psocHttpManager.checkHealth()
    }

    /**
     * 获取 PSoC 状态
     */
    suspend fun getPsocStatus(): Result<Map<String, Any>> {
        return psocHttpManager.getStatus()
    }

    /**
     * 开始训练会话
     */
    suspend fun startTraining(patientId: String, mode: String): Result<String> {
        return psocHttpManager.startTraining(patientId, mode)
    }

    /**
     * 获取康复分析（通过 PSoC）
     */
    suspend fun getRehabAnalysisFromPsoc(sessionId: String): Result<Map<String, Any>> {
        return psocHttpManager.getRehabAnalysis(sessionId)
    }

    /**
     * 断开所有连接
     */
    fun disconnectAll() {
        bluetoothSppManager.disconnect()
        bluetoothManager.disconnect()
        httpManager.disconnect()
    }
}
