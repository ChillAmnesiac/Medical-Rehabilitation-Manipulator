package com.rehab.robotarm.data.communication

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.content.Context
import android.util.Log
import com.rehab.robotarm.data.model.SensorData
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withContext
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.*

/**
 * 蓝牙SPP通信管理器
 * 实现PSoC Edge E84的二进制帧协议
 *
 * 帧格式: [Header(1B)] [Type(1B)] [Length(2B)] [Data(N)] [Checksum(1B)]
 */
class BluetoothSppManager(private val context: Context) {

    private val bluetoothAdapter: BluetoothAdapter? = BluetoothAdapter.getDefaultAdapter()
    private var bluetoothSocket: BluetoothSocket? = null
    private var inputStream: InputStream? = null
    private var outputStream: OutputStream? = null
    private var receiveThread: Thread? = null
    private var isReceiving = false

    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState

    private val _sensorData = MutableStateFlow<SensorData?>(null)
    val sensorData: StateFlow<SensorData?> = _sensorData

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage

    // SPP UUID
    private val SPP_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

    // 协议常量
    private companion object {
        const val HEADER = 0xAA.toByte()
        const val TAG = "BluetoothSPP"

        // 命令类型
        const val CMD_MOVE_JOINT = 0x01.toByte()
        const val CMD_SET_MODE = 0x02.toByte()
        const val CMD_GET_SENSOR = 0x03.toByte()
        const val CMD_START_RECORD = 0x04.toByte()
        const val CMD_STOP_RECORD = 0x05.toByte()
        const val CMD_EMERGENCY_STOP = 0x06.toByte()
        const val CMD_EXECUTE_MEMORY = 0x07.toByte()

        // 数据类型
        const val DATA_SENSOR = 0x10.toByte()
        const val DATA_STATUS = 0x11.toByte()
        const val DATA_ALERT = 0x12.toByte()
    }

    enum class ConnectionState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        ERROR
    }

    enum class RobotMode(val value: Byte) {
        ACTIVE(0x01),
        PASSIVE(0x02),
        ASSIST(0x03),
        RESIST(0x04),
        MEMORY(0x05),
        GAME(0x06)
    }

    /**
     * 扫描已配对的蓝牙设备
     */
    suspend fun scanDevices(): List<BluetoothDevice> = withContext(Dispatchers.IO) {
        try {
            bluetoothAdapter?.bondedDevices?.toList() ?: emptyList()
        } catch (e: SecurityException) {
            Log.e(TAG, "Permission denied for scanning devices", e)
            emptyList()
        }
    }

    /**
     * 连接到指定的蓝牙设备
     */
    suspend fun connect(device: BluetoothDevice): Boolean = withContext(Dispatchers.IO) {
        try {
            _connectionState.value = ConnectionState.CONNECTING
            Log.d(TAG, "Connecting to device: ${device.name}")

            bluetoothSocket = device.createRfcommSocketToServiceRecord(SPP_UUID)
            bluetoothSocket?.connect()

            inputStream = bluetoothSocket?.inputStream
            outputStream = bluetoothSocket?.outputStream

            _connectionState.value = ConnectionState.CONNECTED
            Log.d(TAG, "Connected successfully")

            // 启动数据接收线程
            startReceiving()

            true
        } catch (e: IOException) {
            Log.e(TAG, "Connection failed", e)
            _connectionState.value = ConnectionState.ERROR
            _errorMessage.value = "连接失败: ${e.message}"
            disconnect()
            false
        } catch (e: SecurityException) {
            Log.e(TAG, "Permission denied", e)
            _connectionState.value = ConnectionState.ERROR
            _errorMessage.value = "权限不足"
            false
        }
    }

    /**
     * 断开蓝牙连接
     */
    fun disconnect() {
        isReceiving = false
        receiveThread?.interrupt()

        try {
            inputStream?.close()
            outputStream?.close()
            bluetoothSocket?.close()
        } catch (e: IOException) {
            Log.e(TAG, "Error closing connection", e)
        } finally {
            inputStream = null
            outputStream = null
            bluetoothSocket = null
            _connectionState.value = ConnectionState.DISCONNECTED
            Log.d(TAG, "Disconnected")
        }
    }

    /**
     * 移动关节
     * @param jointId 关节ID (0=肩关节, 1=肘关节, 2=推杆)
     * @param angle 目标角度
     * @param speed 运动速度 (度/秒)
     */
    suspend fun moveJoint(jointId: Int, angle: Float, speed: Float = 30f): Boolean {
        val data = ByteBuffer.allocate(9)
            .order(ByteOrder.LITTLE_ENDIAN)
            .put(jointId.toByte())
            .putFloat(angle)
            .putFloat(speed)
            .array()

        return sendFrame(CMD_MOVE_JOINT, data)
    }

    /**
     * 设置工作模式
     */
    suspend fun setMode(mode: RobotMode): Boolean {
        val data = byteArrayOf(mode.value)
        return sendFrame(CMD_SET_MODE, data)
    }

    /**
     * 获取传感器数据
     */
    suspend fun getSensorData(): Boolean {
        return sendFrame(CMD_GET_SENSOR, byteArrayOf())
    }

    /**
     * 开始录制动作
     */
    suspend fun startRecording(): Boolean {
        return sendFrame(CMD_START_RECORD, byteArrayOf())
    }

    /**
     * 停止录制动作
     */
    suspend fun stopRecording(): Boolean {
        return sendFrame(CMD_STOP_RECORD, byteArrayOf())
    }

    /**
     * 紧急停止
     */
    suspend fun emergencyStop(): Boolean {
        return sendFrame(CMD_EMERGENCY_STOP, byteArrayOf())
    }

    /**
     * 执行记忆动作
     * @param memoryId 记忆动作ID
     */
    suspend fun executeMemory(memoryId: String): Boolean {
        val data = memoryId.toByteArray()
        return sendFrame(CMD_EXECUTE_MEMORY, data)
    }

    /**
     * 发送数据帧
     * 帧格式: [Header(1B)] [Type(1B)] [Length(2B)] [Data(N)] [Checksum(1B)]
     */
    private suspend fun sendFrame(type: Byte, data: ByteArray): Boolean = withContext(Dispatchers.IO) {
        try {
            if (_connectionState.value != ConnectionState.CONNECTED) {
                Log.w(TAG, "Not connected")
                return@withContext false
            }

            val length = data.size.toShort()
            val frame = ByteBuffer.allocate(5 + data.size)
                .put(HEADER)
                .put(type)
                .putShort(length)
                .put(data)

            // 计算校验和
            val checksum = calculateChecksum(frame.array(), 0, 4 + data.size)
            frame.put(checksum)

            outputStream?.write(frame.array())
            outputStream?.flush()

            Log.d(TAG, "Sent frame: type=0x${type.toString(16)}, length=$length")
            true
        } catch (e: IOException) {
            Log.e(TAG, "Failed to send frame", e)
            _connectionState.value = ConnectionState.ERROR
            false
        }
    }

    /**
     * 启动数据接收线程
     */
    private fun startReceiving() {
        isReceiving = true
        receiveThread = Thread {
            val buffer = ByteArray(1024)
            var bufferPos = 0

            while (isReceiving && _connectionState.value == ConnectionState.CONNECTED) {
                try {
                    val available = inputStream?.available() ?: 0
                    if (available > 0) {
                        val bytes = inputStream?.read(buffer, bufferPos, buffer.size - bufferPos) ?: -1
                        if (bytes > 0) {
                            bufferPos += bytes

                            // 尝试解析帧
                            while (bufferPos >= 5) {
                                val frameSize = parseFrame(buffer, bufferPos)
                                if (frameSize > 0) {
                                    // 移除已处理的数据
                                    System.arraycopy(buffer, frameSize, buffer, 0, bufferPos - frameSize)
                                    bufferPos -= frameSize
                                } else {
                                    break
                                }
                            }
                        }
                    } else {
                        Thread.sleep(10)
                    }
                } catch (e: IOException) {
                    Log.e(TAG, "Error receiving data", e)
                    _connectionState.value = ConnectionState.ERROR
                    break
                } catch (e: InterruptedException) {
                    break
                }
            }
        }
        receiveThread?.start()
    }

    /**
     * 解析数据帧
     * @return 帧大小，如果解析失败返回0
     */
    private fun parseFrame(buffer: ByteArray, bufferSize: Int): Int {
        if (bufferSize < 5) return 0

        // 检查帧头
        if (buffer[0] != HEADER) {
            Log.w(TAG, "Invalid header")
            return 1 // 跳过一个字节
        }

        val type = buffer[1]
        val length = ByteBuffer.wrap(buffer, 2, 2).order(ByteOrder.LITTLE_ENDIAN).short.toInt()

        val frameSize = 5 + length
        if (bufferSize < frameSize) {
            return 0 // 数据不完整
        }

        // 验证校验和
        val receivedChecksum = buffer[frameSize - 1]
        val calculatedChecksum = calculateChecksum(buffer, 0, frameSize - 1)

        if (receivedChecksum != calculatedChecksum) {
            Log.w(TAG, "Checksum mismatch")
            return frameSize // 跳过这个帧
        }

        // 提取数据
        val data = buffer.copyOfRange(4, 4 + length)

        // 处理不同类型的数据
        when (type) {
            DATA_SENSOR -> parseSensorData(data)
            DATA_STATUS -> parseStatusData(data)
            DATA_ALERT -> parseAlertData(data)
            else -> Log.w(TAG, "Unknown data type: 0x${type.toString(16)}")
        }

        return frameSize
    }

    /**
     * 解析传感器数据
     */
    private fun parseSensorData(data: ByteArray) {
        try {
            val buffer = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)

            val sensorData = SensorData(
                timestamp = buffer.long,
                emgCh1 = buffer.float,
                heartRate = buffer.int,
                imuAngleX = buffer.float,
                imuAngleY = buffer.float,
                imuAngleZ = buffer.float,
                imuAccelX = buffer.float,
                imuAccelY = buffer.float,
                imuAccelZ = buffer.float,
                motor1Angle = buffer.float,
                motor1Damping = buffer.float,
                motor1Temp = buffer.float,
                motor2Angle = buffer.float,
                motor2Damping = buffer.float,
                motor2Temp = buffer.float
            )

            _sensorData.value = sensorData
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing sensor data", e)
        }
    }

    /**
     * 解析状态数据
     */
    private fun parseStatusData(data: ByteArray) {
        // 实现状态数据解析
        Log.d(TAG, "Received status data")
    }

    /**
     * 解析告警数据
     */
    private fun parseAlertData(data: ByteArray) {
        val message = String(data)
        Log.w(TAG, "Alert: $message")
        _errorMessage.value = message
    }

    /**
     * 计算校验和 (简单的异或校验)
     */
    private fun calculateChecksum(data: ByteArray, offset: Int, length: Int): Byte {
        var checksum: Byte = 0
        for (i in offset until offset + length) {
            checksum = (checksum.toInt() xor data[i].toInt()).toByte()
        }
        return checksum
    }

    /**
     * 检查蓝牙是否可用
     */
    fun isBluetoothAvailable(): Boolean {
        return bluetoothAdapter != null && bluetoothAdapter.isEnabled
    }

    /**
     * 检查是否已连接
     */
    fun isConnected(): Boolean {
        return _connectionState.value == ConnectionState.CONNECTED
    }
}
