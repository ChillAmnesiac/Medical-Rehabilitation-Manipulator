package com.rehab.robotarm.data.communication

import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
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

    // 发现的设备列表
    private val discoveredDevices = mutableSetOf<BluetoothDevice>()
    private var discoveryReceiver: BroadcastReceiver? = null

    // PSoC6设备的UUID（SPP标准UUID）
    private val DEVICE_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

    enum class ConnectionState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        ERROR
    }

    /**
     * 扫描可用的蓝牙设备（包括未配对的设备）
     */
    suspend fun scanDevices(): List<BluetoothDevice> = withContext(Dispatchers.IO) {
        discoveredDevices.clear()

        // 添加已配对的设备
        bluetoothAdapter?.bondedDevices?.let {
            discoveredDevices.addAll(it)
        }

        // 启动蓝牙发现
        try {
            // 如果正在扫描，先取消
            if (bluetoothAdapter?.isDiscovering == true) {
                bluetoothAdapter.cancelDiscovery()
            }

            // 注册广播接收器
            val filter = IntentFilter().apply {
                addAction(BluetoothDevice.ACTION_FOUND)
                addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)
            }

            discoveryReceiver = object : BroadcastReceiver() {
                override fun onReceive(context: Context, intent: Intent) {
                    when (intent.action) {
                        BluetoothDevice.ACTION_FOUND -> {
                            val device: BluetoothDevice? =
                                intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
                            device?.let { discoveredDevices.add(it) }
                        }
                    }
                }
            }

            context.registerReceiver(discoveryReceiver, filter)

            // 开始扫描
            bluetoothAdapter?.startDiscovery()

            // 等待扫描完成（最多12秒）
            delay(12000)

            // 取消扫描
            bluetoothAdapter?.cancelDiscovery()

            // 注销接收器
            try {
                context.unregisterReceiver(discoveryReceiver)
            } catch (e: Exception) {
                e.printStackTrace()
            }

        } catch (e: Exception) {
            e.printStackTrace()
        }

        discoveredDevices.toList()
    }

    /**
     * 连接到指定的蓝牙设备
     * 连接成功后自动发送 stream:on 命令启动数据流（M33协议要求）
     */
    suspend fun connect(device: BluetoothDevice): Boolean = withContext(Dispatchers.IO) {
        try {
            _connectionState.value = ConnectionState.CONNECTING
            android.util.Log.d("BluetoothManager", "Attempting to connect to ${device.name} (${device.address})")

            var connected = false
            var lastException: Exception? = null

            // 方法1: 标准 RFCOMM 连接
            try {
                bluetoothSocket = device.createRfcommSocketToServiceRecord(DEVICE_UUID)
                android.util.Log.d("BluetoothManager", "Created socket with standard method (UUID)")

                // 取消发现以提高连接速度
                bluetoothAdapter?.cancelDiscovery()

                bluetoothSocket?.connect()
                android.util.Log.d("BluetoothManager", "Socket connected successfully with standard method")
                connected = true
            } catch (e: Exception) {
                lastException = e
                android.util.Log.w("BluetoothManager", "Standard method failed: ${e.message}")

                // 关闭失败的 socket
                try {
                    bluetoothSocket?.close()
                } catch (e2: Exception) {
                    // 忽略
                }
                bluetoothSocket = null
            }

            // 方法2: 使用反射创建不安全连接，尝试多个通道
            if (!connected) {
                val channels = listOf(1, 2, 3, 4, 5) // 尝试常用的通道号

                for (channel in channels) {
                    try {
                        android.util.Log.d("BluetoothManager", "Trying reflection method with channel $channel")
                        val method = device.javaClass.getMethod("createRfcommSocket", Int::class.javaPrimitiveType)
                        bluetoothSocket = method.invoke(device, channel) as BluetoothSocket

                        // 取消发现
                        bluetoothAdapter?.cancelDiscovery()

                        bluetoothSocket?.connect()
                        android.util.Log.d("BluetoothManager", "Socket connected successfully with channel $channel")
                        connected = true
                        break
                    } catch (e: Exception) {
                        lastException = e
                        android.util.Log.w("BluetoothManager", "Channel $channel failed: ${e.message}")

                        // 关闭失败的 socket
                        try {
                            bluetoothSocket?.close()
                        } catch (e2: Exception) {
                            // 忽略
                        }
                        bluetoothSocket = null
                    }
                }
            }

            if (!connected) {
                throw lastException ?: IOException("All connection methods failed")
            }

            inputStream = bluetoothSocket?.inputStream
            outputStream = bluetoothSocket?.outputStream

            _connectionState.value = ConnectionState.CONNECTED

            // 启动数据接收线程
            startReceiving()

            // M33协议：连接成功后发送 stream:on 启动数据流
            kotlinx.coroutines.delay(500) // 等待设备准备好
            sendCommand("stream:on\n")
            android.util.Log.d("BluetoothManager", "Sent stream:on command to M33")

            true
        } catch (e: IOException) {
            android.util.Log.e("BluetoothManager", "Connection failed: ${e.message}", e)
            e.printStackTrace()
            _connectionState.value = ConnectionState.ERROR
            disconnect()
            false
        }
    }

    /**
     * 断开蓝牙连接
     * 断开前发送 stream:off 命令停止数据流（M33协议要求）
     */
    fun disconnect() {
        try {
            // M33协议：断开前发送 stream:off 停止数据流
            if (_connectionState.value == ConnectionState.CONNECTED) {
                try {
                    outputStream?.write("stream:off\n".toByteArray())
                    outputStream?.flush()
                    Thread.sleep(100) // 等待命令发送完成
                    android.util.Log.d("BluetoothManager", "Sent stream:off command to M33")
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }

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
