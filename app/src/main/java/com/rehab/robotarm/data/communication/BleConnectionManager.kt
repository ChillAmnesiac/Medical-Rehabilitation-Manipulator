package com.rehab.robotarm.data.communication

import android.annotation.SuppressLint
import android.bluetooth.*
import android.content.Context
import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.util.UUID

/**
 * BLE 连接管理器 - 使用原生 Android BLE API
 */
class BleConnectionManager(private val context: Context) {

    private var bluetoothGatt: BluetoothGatt? = null
    private var txCharacteristic: BluetoothGattCharacteristic? = null
    private var rxCharacteristic: BluetoothGattCharacteristic? = null

    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState

    private val _receivedData = MutableStateFlow<ByteArray?>(null)
    val receivedData: StateFlow<ByteArray?> = _receivedData

    // 数据缓冲区，用于拼接分块接收的数据
    private val dataBuffer = StringBuilder()

    enum class ConnectionState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        ERROR
    }

    private val gattCallback = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            when (newState) {
                BluetoothProfile.STATE_CONNECTED -> {
                    Log.d(TAG, "已连接到 GATT 服务器")
                    _connectionState.value = ConnectionState.CONNECTING
                    gatt.discoverServices()
                }
                BluetoothProfile.STATE_DISCONNECTED -> {
                    Log.d(TAG, "已断开 GATT 连接")
                    _connectionState.value = ConnectionState.DISCONNECTED
                }
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            if (status == BluetoothGatt.GATT_SUCCESS) {
                Log.d(TAG, "发现服务")
                val uartService = gatt.getService(UART_SERVICE_UUID)
                if (uartService != null) {
                    Log.d(TAG, "找到 UART 服务")
                    txCharacteristic = uartService.getCharacteristic(UART_TX_CHARACTERISTIC_UUID)
                    rxCharacteristic = uartService.getCharacteristic(UART_RX_CHARACTERISTIC_UUID)

                    // 启用 TX 特征的通知
                    txCharacteristic?.let { char ->
                        gatt.setCharacteristicNotification(char, true)
                        val descriptor = char.getDescriptor(CLIENT_CHARACTERISTIC_CONFIG_UUID)
                        descriptor?.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                        gatt.writeDescriptor(descriptor)
                    }

                    _connectionState.value = ConnectionState.CONNECTED
                    Log.d(TAG, "UART 服务已就绪")

                    // 发送 stream:on 命令
                    sendCommand("stream:on\n")
                } else {
                    Log.e(TAG, "未找到 UART 服务")
                    _connectionState.value = ConnectionState.ERROR
                    disconnect()
                }
            } else {
                Log.e(TAG, "服务发现失败: $status")
                _connectionState.value = ConnectionState.ERROR
            }
        }

        @Deprecated("Deprecated in Java")
        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic
        ) {
            if (characteristic.uuid == UART_TX_CHARACTERISTIC_UUID) {
                val data = characteristic.value
                val text = String(data)

                // 将接收到的数据添加到缓冲区
                dataBuffer.append(text)

                // 检查是否接收到完整的 JSON（以 } 结尾）
                val bufferContent = dataBuffer.toString()
                if (bufferContent.contains("}")) {
                    // 提取完整的 JSON
                    val endIndex = bufferContent.indexOf("}") + 1
                    val completeJson = bufferContent.substring(0, endIndex)

                    Log.d(TAG, "收到完整数据: $completeJson")
                    _receivedData.value = completeJson.toByteArray()

                    // 清空缓冲区，保留剩余数据
                    dataBuffer.clear()
                    if (endIndex < bufferContent.length) {
                        dataBuffer.append(bufferContent.substring(endIndex))
                    }
                }
            }
        }
    }

    @SuppressLint("MissingPermission")
    suspend fun connect(deviceAddress: String): Boolean {
        return try {
            Log.d(TAG, "开始连接: $deviceAddress")
            _connectionState.value = ConnectionState.CONNECTING

            val bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
            val device = bluetoothAdapter?.getRemoteDevice(deviceAddress)

            if (device == null) {
                Log.e(TAG, "设备不存在")
                _connectionState.value = ConnectionState.ERROR
                return false
            }

            bluetoothGatt = device.connectGatt(context, false, gattCallback)
            true
        } catch (e: Exception) {
            Log.e(TAG, "连接失败", e)
            _connectionState.value = ConnectionState.ERROR
            false
        }
    }

    @SuppressLint("MissingPermission")
    fun disconnect() {
        try {
            // 发送 stream:off 命令
            sendCommand("stream:off\n")
            Thread.sleep(100) // 等待命令发送完成

            dataBuffer.clear()  // 清空缓冲区
            bluetoothGatt?.disconnect()
            bluetoothGatt?.close()
            bluetoothGatt = null
            _connectionState.value = ConnectionState.DISCONNECTED
            Log.d(TAG, "已断开连接")
        } catch (e: Exception) {
            Log.e(TAG, "断开连接失败", e)
        }
    }

    @SuppressLint("MissingPermission")
    fun sendCommand(command: String) {
        try {
            rxCharacteristic?.let { char ->
                val data = command.toByteArray()
                // 分块发送（每次最多 20 字节）
                val chunkSize = 20
                for (i in data.indices step chunkSize) {
                    val chunk = data.copyOfRange(i, minOf(i + chunkSize, data.size))
                    char.value = chunk
                    bluetoothGatt?.writeCharacteristic(char)
                    Thread.sleep(10) // 短暂延迟确保数据发送完成
                }
                Log.d(TAG, "发送命令: $command")
            } ?: Log.e(TAG, "RX characteristic 为空")
        } catch (e: Exception) {
            Log.e(TAG, "发送命令失败", e)
        }
    }

    fun release() {
        disconnect()
    }

    companion object {
        private const val TAG = "BleConnectionManager"
        private val UART_SERVICE_UUID: UUID =
            UUID.fromString("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
        private val UART_TX_CHARACTERISTIC_UUID: UUID =
            UUID.fromString("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
        private val UART_RX_CHARACTERISTIC_UUID: UUID =
            UUID.fromString("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
        private val CLIENT_CHARACTERISTIC_CONFIG_UUID: UUID =
            UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")
    }
}
