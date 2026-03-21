package com.rehab.robotarm.data.communication

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withContext
import java.io.IOException
import java.io.InputStream
import java.io.OutputStream
import java.util.*

/**
 * 蓝牙通信管理器
 * 负责与PSoC6设备的蓝牙连接和数据传输
 */
class BluetoothManager(private val context: Context) {

    private val bluetoothAdapter: BluetoothAdapter? = BluetoothAdapter.getDefaultAdapter()
    private var bluetoothSocket: BluetoothSocket? = null
    private var inputStream: InputStream? = null
    private var outputStream: OutputStream? = null

    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState

    private val _receivedData = MutableStateFlow<ByteArray?>(null)
    val receivedData: StateFlow<ByteArray?> = _receivedData

    // PSoC6设备的UUID（需要根据实际设备修改）
    private val DEVICE_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

    enum class ConnectionState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        ERROR
    }

    /**
     * 扫描可用的蓝牙设备
     */
    suspend fun scanDevices(): List<BluetoothDevice> = withContext(Dispatchers.IO) {
        bluetoothAdapter?.bondedDevices?.toList() ?: emptyList()
    }

    /**
     * 连接到指定的蓝牙设备
     */
    suspend fun connect(device: BluetoothDevice): Boolean = withContext(Dispatchers.IO) {
        try {
            _connectionState.value = ConnectionState.CONNECTING

            bluetoothSocket = device.createRfcommSocketToServiceRecord(DEVICE_UUID)
            bluetoothSocket?.connect()

            inputStream = bluetoothSocket?.inputStream
            outputStream = bluetoothSocket?.outputStream

            _connectionState.value = ConnectionState.CONNECTED

            // 启动数据接收线程
            startReceiving()

            true
        } catch (e: IOException) {
            e.printStackTrace()
            _connectionState.value = ConnectionState.ERROR
            disconnect()
            false
        }
    }

    /**
     * 断开蓝牙连接
     */
    fun disconnect() {
        try {
            inputStream?.close()
            outputStream?.close()
            bluetoothSocket?.close()
        } catch (e: IOException) {
            e.printStackTrace()
        } finally {
            inputStream = null
            outputStream = null
            bluetoothSocket = null
            _connectionState.value = ConnectionState.DISCONNECTED
        }
    }

    /**
     * 发送数据到设备
     */
    suspend fun sendData(data: ByteArray): Boolean = withContext(Dispatchers.IO) {
        try {
            outputStream?.write(data)
            outputStream?.flush()
            true
        } catch (e: IOException) {
            e.printStackTrace()
            false
        }
    }

    /**
     * 发送控制命令
     */
    suspend fun sendCommand(command: String): Boolean {
        return sendData(command.toByteArray())
    }

    /**
     * 启动数据接收
     */
    private fun startReceiving() {
        Thread {
            val buffer = ByteArray(1024)
            while (connectionState.value == ConnectionState.CONNECTED) {
                try {
                    val bytes = inputStream?.read(buffer) ?: -1
                    if (bytes > 0) {
                        val data = buffer.copyOf(bytes)
                        _receivedData.value = data
                    }
                } catch (e: IOException) {
                    e.printStackTrace()
                    _connectionState.value = ConnectionState.ERROR
                    break
                }
            }
        }.start()
    }

    /**
     * 检查蓝牙是否可用
     */
    fun isBluetoothAvailable(): Boolean {
        return bluetoothAdapter != null && bluetoothAdapter.isEnabled
    }

    /**
     * 连接到指定地址的设备
     */
    suspend fun connect(deviceAddress: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val device = bluetoothAdapter?.getRemoteDevice(deviceAddress)
            if (device != null) {
                val success = connect(device)
                Result.success(success)
            } else {
                Result.failure(Exception("Device not found"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 发送命令
     */
    suspend fun sendCommand(command: com.rehab.robotarm.data.model.Command): Result<com.rehab.robotarm.data.model.Response> {
        return try {
            val success = sendCommand(command.text ?: "")
            if (success) {
                Result.success(
                    com.rehab.robotarm.data.model.Response(
                        success = true,
                        message = "Command sent",
                        data = emptyMap()
                    )
                )
            } else {
                Result.failure(Exception("Failed to send command"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 检查是否已连接
     */
    fun isConnected(): Boolean {
        return connectionState.value == ConnectionState.CONNECTED
    }

    /**
     * 开始监听数据
     */
    fun startListening(onData: (ByteArray) -> Unit) {
        // 已经在startReceiving中实现了接收逻辑
        // 这里可以添加回调支持
    }

    /**
     * 停止监听数据
     */
    fun stopListening() {
        // 停止接收数据
    }
}
