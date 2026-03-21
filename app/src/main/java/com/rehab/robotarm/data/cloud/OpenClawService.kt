package com.rehab.robotarm.data.cloud

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * OpenClaw服务 (通过HTTP Bridge)
 * 连接到OpenClaw HTTP Bridge，发送消息并接收响应
 */
class OpenClawService {
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(10, TimeUnit.SECONDS)
        .build()

    private var bridgeUrl: String = "http://localhost:8080"
    private val TAG = "OpenClawService"

    /**
     * 设置Bridge地址
     */
    fun setGatewayUrl(url: String) {
        bridgeUrl = url.trimEnd('/')
        Log.i(TAG, "OpenClaw Bridge设置为: $bridgeUrl")
    }

    fun setBaseUrl(url: String) {
        setGatewayUrl(url)
    }

    fun setAuthToken(token: String) {
        // HTTP Bridge不需要token
    }

    /**
     * 发送消息到OpenClaw
     */
    suspend fun sendMessage(message: String): OpenClawResponse = withContext(Dispatchers.IO) {
        try {
            Log.i(TAG, "发送消息: $message")

            val json = JSONObject().apply {
                put("message", message)
            }

            val requestBody = json.toString()
                .toRequestBody("application/json".toMediaType())

            val request = Request.Builder()
                .url("$bridgeUrl/message")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()

            if (response.isSuccessful) {
                val responseBody = response.body?.string() ?: ""
                Log.d(TAG, "收到响应: $responseBody")

                val jsonResponse = JSONObject(responseBody)
                val success = jsonResponse.optBoolean("success", false)
                val aiMessage = jsonResponse.optString("message", "")
                val error = jsonResponse.optString("error", null)

                OpenClawResponse(
                    success = success,
                    message = aiMessage,
                    error = error
                )
            } else {
                Log.e(TAG, "请求失败: ${response.code}")
                OpenClawResponse(
                    success = false,
                    message = "",
                    error = "HTTP错误: ${response.code}"
                )
            }
        } catch (e: IOException) {
            Log.e(TAG, "网络错误", e)
            OpenClawResponse(
                success = false,
                message = "",
                error = "网络连接失败: ${e.message}"
            )
        } catch (e: Exception) {
            Log.e(TAG, "未知错误", e)
            OpenClawResponse(
                success = false,
                message = "",
                error = "错误: ${e.message}"
            )
        }
    }

    /**
     * 检查Bridge健康状态
     */
    suspend fun checkHealth(): Boolean = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$bridgeUrl/health")
                .get()
                .build()

            val response = client.newCall(request).execute()
            val isHealthy = response.isSuccessful

            if (isHealthy) {
                Log.i(TAG, "OpenClaw Bridge在线")
            } else {
                Log.w(TAG, "OpenClaw Bridge离线")
            }

            isHealthy
        } catch (e: Exception) {
            Log.e(TAG, "无法连接OpenClaw Bridge", e)
            false
        }
    }

    fun disconnect() {
        // HTTP不需要断开连接
    }

    /**
     * 发送自然语言指令
     */
    suspend fun sendNaturalLanguage(text: String): Result<com.rehab.robotarm.data.model.Response> {
        return try {
            val response = sendMessage(text)
            if (response.success) {
                Result.success(
                    com.rehab.robotarm.data.model.Response(
                        success = true,
                        message = response.message,
                        data = emptyMap()
                    )
                )
            } else {
                Result.failure(Exception(response.error ?: "Unknown error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 执行复杂任务
     */
    suspend fun executeTask(command: com.rehab.robotarm.data.model.Command): Result<com.rehab.robotarm.data.model.Response> {
        return try {
            val response = sendMessage(command.text ?: "")
            if (response.success) {
                Result.success(
                    com.rehab.robotarm.data.model.Response(
                        success = true,
                        message = response.message,
                        data = emptyMap()
                    )
                )
            } else {
                Result.failure(Exception(response.error ?: "Unknown error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * 获取康复分析
     */
    suspend fun getRehabAnalysis(sessionId: String): Result<String> {
        return try {
            val response = sendMessage("分析训练会话: $sessionId")
            if (response.success) {
                Result.success(response.message)
            } else {
                Result.failure(Exception(response.error ?: "Unknown error"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

/**
 * OpenClaw响应数据类
 */
data class OpenClawResponse(
    val success: Boolean,
    val message: String,
    val error: String?
)
