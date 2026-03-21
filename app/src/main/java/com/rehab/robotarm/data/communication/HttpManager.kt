package com.rehab.robotarm.data.communication

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

/**
 * HTTP通信管理器
 * 用于与PSoC Edge设备通过HTTP/WiFi通信
 */
class HttpManager {

    enum class ConnectionState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        ERROR
    }

    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState

    private val _receivedData = MutableStateFlow<ByteArray?>(null)
    val receivedData: StateFlow<ByteArray?> = _receivedData

    private var psocUrl = "http://localhost:8081"  // PSoC Edge HTTP服务器地址
    private var isPolling = false

    /**
     * 设置PSoC Edge服务器地址
     */
    fun setPSoCUrl(url: String) {
        psocUrl = url.trimEnd('/')
    }

    /**
     * 检查连接状态
     */
    suspend fun checkConnection(): Boolean = withContext(Dispatchers.IO) {
        try {
            _connectionState.value = ConnectionState.CONNECTING
            android.util.Log.d("HttpManager", "Connecting to: $psocUrl/health")

            val url = URL("$psocUrl/health")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000

            android.util.Log.d("HttpManager", "Waiting for response...")
            val responseCode = connection.responseCode
            android.util.Log.d("HttpManager", "Response code: $responseCode")

            val isConnected = responseCode == 200

            _connectionState.value = if (isConnected) {
                ConnectionState.CONNECTED
            } else {
                ConnectionState.ERROR
            }

            connection.disconnect()
            android.util.Log.d("HttpManager", "Connection result: $isConnected")
            isConnected
        } catch (e: Exception) {
            android.util.Log.e("HttpManager", "Connection failed: ${e.message}", e)
            e.printStackTrace()
            _connectionState.value = ConnectionState.ERROR
            false
        }
    }

    /**
     * 开始轮询传感器数据
     */
    suspend fun startPolling(intervalMs: Long = 100) {
        isPolling = true
        android.util.Log.d("HttpManager", "Starting polling with interval ${intervalMs}ms")
        withContext(Dispatchers.IO) {
            while (isPolling) {
                try {
                    val data = fetchSensorData()
                    if (data != null) {
                        android.util.Log.d("HttpManager", "Received data: ${String(data).take(100)}")
                        _receivedData.value = data
                    } else {
                        android.util.Log.w("HttpManager", "fetchSensorData returned null")
                    }
                    kotlinx.coroutines.delay(intervalMs)
                } catch (e: Exception) {
                    android.util.Log.e("HttpManager", "Polling error: ${e.message}", e)
                    e.printStackTrace()
                    kotlinx.coroutines.delay(1000) // 错误时延长间隔
                }
            }
        }
        android.util.Log.d("HttpManager", "Polling stopped")
    }

    /**
     * 停止轮询
     */
    fun stopPolling() {
        isPolling = false
    }

    /**
     * 获取传感器数据
     */
    private suspend fun fetchSensorData(): ByteArray? = withContext(Dispatchers.IO) {
        try {
            val url = URL("$psocUrl/status")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 2000
            connection.readTimeout = 2000

            if (connection.responseCode == 200) {
                val reader = BufferedReader(InputStreamReader(connection.inputStream))
                val response = reader.readText()
                reader.close()
                connection.disconnect()
                response.toByteArray()
            } else {
                connection.disconnect()
                null
            }
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    /**
     * 发送数据到PSoC Edge
     */
    suspend fun sendData(data: ByteArray): Boolean = withContext(Dispatchers.IO) {
        try {
            val jsonString = String(data)
            android.util.Log.d("HttpManager", "Sending data: $jsonString")
            val jsonMap = com.google.gson.Gson().fromJson(jsonString, Map::class.java)
            val type = jsonMap["type"] as? String

            val endpoint = when (type) {
                "mode" -> "/mode"
                "control" -> "/control"
                "memory", "execute_memory" -> "/memory/execute"
                "stop_memory" -> "/memory/stop"
                else -> {
                    // 如果没有type字段，检查是否有mode字段（直接模式切换）
                    if (jsonMap.containsKey("mode")) {
                        "/mode"
                    } else {
                        android.util.Log.e("HttpManager", "Unknown command type")
                        return@withContext false
                    }
                }
            }

            android.util.Log.d("HttpManager", "Sending to endpoint: $endpoint")
            val url = URL("$psocUrl$endpoint")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.doOutput = true
            connection.connectTimeout = 3000
            connection.readTimeout = 3000

            val writer = OutputStreamWriter(connection.outputStream)
            writer.write(jsonString)
            writer.flush()
            writer.close()

            val responseCode = connection.responseCode
            android.util.Log.d("HttpManager", "Response code: $responseCode")
            connection.disconnect()

            responseCode == 200
        } catch (e: Exception) {
            android.util.Log.e("HttpManager", "Send data failed: ${e.message}", e)
            e.printStackTrace()
            false
        }
    }

    /**
     * 断开连接
     */
    fun disconnect() {
        stopPolling()
        _connectionState.value = ConnectionState.DISCONNECTED
    }

    /**
     * 发送命令
     */
    suspend fun sendCommand(command: com.rehab.robotarm.data.model.Command): Result<com.rehab.robotarm.data.model.Response> {
        return try {
            val jsonData = com.google.gson.Gson().toJson(command).toByteArray()
            val success = sendData(jsonData)
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
     * 获取设备状态
     */
    suspend fun getStatus(): Result<Map<String, Any>> {
        return try {
            val data = fetchSensorData()
            if (data != null) {
                val jsonString = String(data)
                val statusMap = com.google.gson.Gson().fromJson(jsonString, Map::class.java) as Map<String, Any>
                Result.success(statusMap)
            } else {
                Result.failure(Exception("Failed to get status"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
