package com.rehab.robotarm.data.communication

import android.util.Log
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * PSoC Edge E84 HTTP API 管理器
 * 实现完整的 REST API 调用
 */
class PsocHttpManager(private var baseUrl: String = "http://192.168.1.100") {

    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .writeTimeout(10, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    companion object {
        private const val TAG = "PsocHttpManager"
    }

    /**
     * 设置 PSoC 设备地址
     */
    fun setBaseUrl(url: String) {
        baseUrl = url.trimEnd('/')
        Log.d(TAG, "Base URL set to: $baseUrl")
    }

    /**
     * 健康检查
     */
    suspend fun checkHealth(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/health")
                .get()
                .build()

            val response = client.newCall(request).execute()
            val success = response.isSuccessful
            response.close()

            Log.d(TAG, "Health check: $success")
            Result.success(success)
        } catch (e: Exception) {
            Log.e(TAG, "Health check failed", e)
            Result.failure(e)
        }
    }

    /**
     * 获取系统状态和传感器数据
     */
    suspend fun getStatus(): Result<Map<String, Any>> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/status")
                .get()
                .build()

            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val body = response.body?.string()
                response.close()

                if (body != null) {
                    val type = object : TypeToken<Map<String, Any>>() {}.type
                    val data: Map<String, Any> = gson.fromJson(body, type)
                    Log.d(TAG, "Status received: ${data.keys}")
                    Result.success(data)
                } else {
                    Result.failure(Exception("Empty response"))
                }
            } else {
                response.close()
                Result.failure(Exception("HTTP ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get status failed", e)
            Result.failure(e)
        }
    }

    /**
     * 切换控制模式
     */
    suspend fun setMode(mode: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val json = gson.toJson(mapOf("mode" to mode))
            val requestBody = json.toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/mode")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            val success = response.isSuccessful
            response.close()

            Log.d(TAG, "Set mode '$mode': $success")
            Result.success(success)
        } catch (e: Exception) {
            Log.e(TAG, "Set mode failed", e)
            Result.failure(e)
        }
    }

    /**
     * 发送控制指令（被动模式）
     */
    suspend fun sendControl(
        shoulderAngle: Float? = null,
        elbowAngle: Float? = null,
        lateralPos: Float? = null
    ): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val controlData = mutableMapOf<String, Any>("type" to "control")
            shoulderAngle?.let { controlData["shoulder_angle"] = it }
            elbowAngle?.let { controlData["elbow_angle"] = it }
            lateralPos?.let { controlData["lateral_pos"] = it }

            val json = gson.toJson(controlData)
            val requestBody = json.toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/control")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            val success = response.isSuccessful
            response.close()

            Log.d(TAG, "Send control: $success")
            Result.success(success)
        } catch (e: Exception) {
            Log.e(TAG, "Send control failed", e)
            Result.failure(e)
        }
    }

    /**
     * 执行记忆动作
     */
    suspend fun executeMemory(actionId: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val json = gson.toJson(mapOf("action_id" to actionId))
            val requestBody = json.toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/memory/execute")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            val success = response.isSuccessful
            response.close()

            Log.d(TAG, "Execute memory '$actionId': $success")
            Result.success(success)
        } catch (e: Exception) {
            Log.e(TAG, "Execute memory failed", e)
            Result.failure(e)
        }
    }

    /**
     * 停止记忆动作
     */
    suspend fun stopMemory(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val requestBody = "{}".toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/memory/stop")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            val success = response.isSuccessful
            response.close()

            Log.d(TAG, "Stop memory: $success")
            Result.success(success)
        } catch (e: Exception) {
            Log.e(TAG, "Stop memory failed", e)
            Result.failure(e)
        }
    }

    /**
     * 获取传感器数据
     */
    suspend fun getSensorData(): Result<Map<String, Any>> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/api/sensor/data")
                .get()
                .build()

            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val body = response.body?.string()
                response.close()

                if (body != null) {
                    val type = object : TypeToken<Map<String, Any>>() {}.type
                    val data: Map<String, Any> = gson.fromJson(body, type)
                    Result.success(data)
                } else {
                    Result.failure(Exception("Empty response"))
                }
            } else {
                response.close()
                Result.failure(Exception("HTTP ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get sensor data failed", e)
            Result.failure(e)
        }
    }

    /**
     * 开始训练
     */
    suspend fun startTraining(patientId: String, mode: String): Result<String> = withContext(Dispatchers.IO) {
        try {
            val json = gson.toJson(mapOf(
                "patient_id" to patientId,
                "mode" to mode
            ))
            val requestBody = json.toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/api/training/start")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val body = response.body?.string()
                response.close()

                if (body != null) {
                    val result: Map<String, Any> = gson.fromJson(body, object : TypeToken<Map<String, Any>>() {}.type)
                    val sessionId = result["session_id"] as? String
                    if (sessionId != null) {
                        Log.d(TAG, "Training started: $sessionId")
                        Result.success(sessionId)
                    } else {
                        Result.failure(Exception("No session ID returned"))
                    }
                } else {
                    Result.failure(Exception("Empty response"))
                }
            } else {
                response.close()
                Result.failure(Exception("HTTP ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Start training failed", e)
            Result.failure(e)
        }
    }

    /**
     * 获取统计数据
     */
    suspend fun getStats(): Result<Map<String, Any>> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/api/stats")
                .get()
                .build()

            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val body = response.body?.string()
                response.close()

                if (body != null) {
                    val type = object : TypeToken<Map<String, Any>>() {}.type
                    val data: Map<String, Any> = gson.fromJson(body, type)
                    Result.success(data)
                } else {
                    Result.failure(Exception("Empty response"))
                }
            } else {
                response.close()
                Result.failure(Exception("HTTP ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get stats failed", e)
            Result.failure(e)
        }
    }

    /**
     * 调用工具函数（OpenClaw 桥接）
     */
    suspend fun callTool(toolName: String, parameters: Map<String, Any>): Result<Map<String, Any>> = withContext(Dispatchers.IO) {
        try {
            val json = gson.toJson(mapOf(
                "tool" to toolName,
                "parameters" to parameters
            ))
            val requestBody = json.toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/api/command")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                val body = response.body?.string()
                response.close()

                if (body != null) {
                    val type = object : TypeToken<Map<String, Any>>() {}.type
                    val data: Map<String, Any> = gson.fromJson(body, type)
                    Log.d(TAG, "Tool '$toolName' called successfully")
                    Result.success(data)
                } else {
                    Result.failure(Exception("Empty response"))
                }
            } else {
                response.close()
                Result.failure(Exception("HTTP ${response.code}"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Call tool failed", e)
            Result.failure(e)
        }
    }

    /**
     * 移动关节（通过工具调用）
     */
    suspend fun moveJoint(jointId: Int, angle: Float, speed: Float = 30f): Result<Boolean> {
        val result = callTool("move_joint", mapOf(
            "joint_id" to jointId,
            "angle" to angle,
            "speed" to speed
        ))
        return result.map { it["success"] as? Boolean ?: false }
    }

    /**
     * 预测运动意图（AI 功能）
     */
    suspend fun predictMotion(emgData: List<Float>): Result<Map<String, Any>> {
        return callTool("predict_motion", mapOf("emg_data" to emgData))
    }

    /**
     * 获取康复分析
     */
    suspend fun getRehabAnalysis(sessionId: String): Result<Map<String, Any>> {
        return callTool("get_rehab_analysis", mapOf("session_id" to sessionId))
    }

    /**
     * 检测异常动作
     */
    suspend fun detectAnomaly(sensorData: Map<String, Any>): Result<Map<String, Any>> {
        return callTool("detect_anomaly", mapOf("sensor_data" to sensorData))
    }
}
