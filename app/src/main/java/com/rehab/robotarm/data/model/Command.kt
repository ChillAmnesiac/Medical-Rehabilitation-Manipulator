package com.rehab.robotarm.data.model

// 指令类型
enum class CommandType {
    REALTIME_CONTROL,    // 实时控制（蓝牙）
    NATURAL_LANGUAGE,    // 自然语言（OpenClaw）
    COMPLEX_TASK,        // 复杂任务（OpenClaw）
    HTTP_API             // HTTP API
}

// 指令对象
data class Command(
    val type: CommandType,
    val action: String = "",
    val params: Map<String, Any> = emptyMap(),
    val text: String? = null
)

// 响应对象
data class Response(
    val success: Boolean,
    val message: String = "",
    val data: Map<String, Any> = emptyMap()
)
