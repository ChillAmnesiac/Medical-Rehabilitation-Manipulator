package com.rehab.robotarm.data.cloud

import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

/**
 * 云端AI服务
 * 调用豆包等云端大模型API获取康复建议
 */
class CloudAIService {

    private val client = OkHttpClient()
    private val gson = Gson()

    // 豆包API配置（需要替换为实际的API密钥和端点）
    private val API_KEY = "YOUR_DOUBAO_API_KEY"
    private val API_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    /**
     * 获取康复建议
     */
    suspend fun getRehabAdvice(
        smoothness: Float,
        rangeOfMotion: Float,
        strength: Float,
        overallScore: Float
    ): String = withContext(Dispatchers.IO) {
        try {
            val prompt = buildPrompt(smoothness, rangeOfMotion, strength, overallScore)
            val response = callCloudAPI(prompt)
            parseResponse(response)
        } catch (e: Exception) {
            e.printStackTrace()
            "无法连接到云端服务，请检查网络连接"
        }
    }

    /**
     * 构建提示词
     */
    private fun buildPrompt(
        smoothness: Float,
        rangeOfMotion: Float,
        strength: Float,
        overallScore: Float
    ): String {
        return """
            作为一名专业的康复医疗顾问，请根据以下患者的康复训练数据提供专业建议：

            - 运动平滑度：${smoothness.toInt()}分（满分100）
            - 运动范围：${rangeOfMotion.toInt()}分（满分100）
            - 力量评分：${strength.toInt()}分（满分100）
            - 综合评分：${overallScore.toInt()}分（满分100）

            请提供：
            1. 当前康复状态评估
            2. 具体的训练建议
            3. 注意事项

            请用简洁专业的语言回答，控制在200字以内。
        """.trimIndent()
    }

    /**
     * 调用云端API
     */
    private fun callCloudAPI(prompt: String): String {
        val requestBody = mapOf(
            "model" to "doubao-pro-32k",
            "messages" to listOf(
                mapOf(
                    "role" to "user",
                    "content" to prompt
                )
            ),
            "temperature" to 0.7,
            "max_tokens" to 500
        )

        val jsonBody = gson.toJson(requestBody)
        val body = jsonBody.toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url(API_ENDPOINT)
            .addHeader("Authorization", "Bearer $API_KEY")
            .addHeader("Content-Type", "application/json")
            .post(body)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response")
            return response.body?.string() ?: ""
        }
    }

    /**
     * 解析API响应
     */
    private fun parseResponse(response: String): String {
        return try {
            val responseMap = gson.fromJson(response, Map::class.java)
            val choices = responseMap["choices"] as? List<*>
            val firstChoice = choices?.firstOrNull() as? Map<*, *>
            val message = firstChoice?.get("message") as? Map<*, *>
            message?.get("content") as? String ?: "解析响应失败"
        } catch (e: Exception) {
            e.printStackTrace()
            "解析响应失败"
        }
    }

    /**
     * 获取模拟建议（用于测试）
     */
    fun getMockAdvice(overallScore: Float): String {
        return when {
            overallScore >= 80 -> """
                康复状态评估：优秀

                您的康复进展非常好，各项指标均达到良好水平。

                训练建议：
                1. 保持当前训练强度和频率
                2. 可以适当增加训练难度
                3. 注意动作标准性

                注意事项：
                - 避免过度训练
                - 保持良好的休息
                - 定期复查评估
            """.trimIndent()

            overallScore >= 60 -> """
                康复状态评估：良好

                您的康复进展稳定，但仍有提升空间。

                训练建议：
                1. 增加训练频率至每天2-3次
                2. 注重运动平滑度训练
                3. 逐步扩大运动范围

                注意事项：
                - 循序渐进，不要急于求成
                - 如有疼痛立即停止
                - 保持正确姿势
            """.trimIndent()

            else -> """
                康复状态评估：需要改进

                您的康复进展较慢，需要调整训练方案。

                训练建议：
                1. 从基础动作开始练习
                2. 增加辅助训练
                3. 建议咨询专业康复师

                注意事项：
                - 不要勉强做困难动作
                - 注意安全，防止二次损伤
                - 保持耐心和信心
            """.trimIndent()
        }
    }
}
