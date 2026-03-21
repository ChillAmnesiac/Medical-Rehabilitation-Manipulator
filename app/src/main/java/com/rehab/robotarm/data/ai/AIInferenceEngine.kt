package com.rehab.robotarm.data.ai

import android.content.Context
import com.rehab.robotarm.data.model.RehabAnalysis
import com.rehab.robotarm.data.model.SensorData
import org.tensorflow.lite.Interpreter
import java.io.FileInputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel

/**
 * AI推理引擎
 * 使用TensorFlow Lite进行本地AI推理
 * 分析传感器数据，评估康复效果
 */
class AIInferenceEngine(private val context: Context) {

    private var interpreter: Interpreter? = null
    private val inputSize = 100  // 输入序列长度
    private val featureSize = 12 // 特征数量

    /**
     * 初始化AI模型
     * 注意：需要将训练好的.tflite模型文件放在assets/models/目录下
     */
    fun initialize() {
        try {
            val modelFile = loadModelFile("models/rehab_model.tflite")
            interpreter = Interpreter(modelFile)
        } catch (e: Exception) {
            e.printStackTrace()
            // 如果模型文件不存在，使用模拟推理
        }
    }

    /**
     * 加载模型文件
     */
    private fun loadModelFile(modelPath: String): MappedByteBuffer {
        val fileDescriptor = context.assets.openFd(modelPath)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        val startOffset = fileDescriptor.startOffset
        val declaredLength = fileDescriptor.declaredLength
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
    }

    /**
     * 分析传感器数据序列，生成康复评估
     */
    fun analyzeRehabProgress(sensorDataList: List<SensorData>): RehabAnalysis {
        if (interpreter == null) {
            // 如果模型未加载，返回模拟数据
            return generateMockAnalysis(sensorDataList)
        }

        try {
            // 准备输入数据
            val inputBuffer = prepareInputData(sensorDataList)

            // 准备输出缓冲区
            val outputBuffer = ByteBuffer.allocateDirect(4 * 4) // 4个float输出
            outputBuffer.order(ByteOrder.nativeOrder())

            // 执行推理
            interpreter?.run(inputBuffer, outputBuffer)

            // 解析输出
            outputBuffer.rewind()
            val smoothness = outputBuffer.float * 100
            val rangeOfMotion = outputBuffer.float * 100
            val strength = outputBuffer.float * 100
            val overallScore = (smoothness + rangeOfMotion + strength) / 3

            return RehabAnalysis(
                timestamp = System.currentTimeMillis(),
                smoothness = smoothness,
                rangeOfMotion = rangeOfMotion,
                strength = strength,
                overallScore = overallScore,
                recommendation = generateRecommendation(smoothness, rangeOfMotion, strength)
            )
        } catch (e: Exception) {
            e.printStackTrace()
            return generateMockAnalysis(sensorDataList)
        }
    }

    /**
     * 准备输入数据
     */
    private fun prepareInputData(sensorDataList: List<SensorData>): ByteBuffer {
        val inputBuffer = ByteBuffer.allocateDirect(4 * inputSize * featureSize)
        inputBuffer.order(ByteOrder.nativeOrder())

        // 取最近的inputSize个数据点
        val dataToUse = sensorDataList.takeLast(inputSize)

        // 填充数据
        for (i in 0 until inputSize) {
            val data = if (i < dataToUse.size) dataToUse[i] else SensorData()

            // 归一化并添加特征
            inputBuffer.putFloat(data.shoulderAngle / 180f)
            inputBuffer.putFloat(data.elbowAngle / 180f)
            inputBuffer.putFloat(data.lateralPosition / 100f)
            inputBuffer.putFloat(data.shoulderForce / 100f)
            inputBuffer.putFloat(data.elbowForce / 100f)
            inputBuffer.putFloat(data.shoulderAccelX / 10f)
            inputBuffer.putFloat(data.shoulderAccelY / 10f)
            inputBuffer.putFloat(data.shoulderAccelZ / 10f)
            inputBuffer.putFloat(data.elbowAccelX / 10f)
            inputBuffer.putFloat(data.elbowAccelY / 10f)
            inputBuffer.putFloat(data.elbowAccelZ / 10f)
            inputBuffer.putFloat((data.shoulderTemp + data.elbowTemp) / 100f)
        }

        inputBuffer.rewind()
        return inputBuffer
    }

    /**
     * 生成模拟分析数据（用于演示）
     */
    private fun generateMockAnalysis(sensorDataList: List<SensorData>): RehabAnalysis {
        if (sensorDataList.isEmpty()) {
            return RehabAnalysis()
        }

        // 计算运动平滑度（基于角度变化）
        val smoothness = calculateSmoothness(sensorDataList)

        // 计算运动范围
        val rangeOfMotion = calculateRangeOfMotion(sensorDataList)

        // 计算力量评分
        val strength = calculateStrength(sensorDataList)

        val overallScore = (smoothness + rangeOfMotion + strength) / 3

        return RehabAnalysis(
            timestamp = System.currentTimeMillis(),
            smoothness = smoothness,
            rangeOfMotion = rangeOfMotion,
            strength = strength,
            overallScore = overallScore,
            recommendation = generateRecommendation(smoothness, rangeOfMotion, strength)
        )
    }

    /**
     * 计算运动平滑度
     */
    private fun calculateSmoothness(data: List<SensorData>): Float {
        if (data.size < 2) return 50f

        var totalJerk = 0f
        for (i in 1 until data.size) {
            val angleDiff = Math.abs(data[i].shoulderAngle - data[i-1].shoulderAngle) +
                           Math.abs(data[i].elbowAngle - data[i-1].elbowAngle)
            totalJerk += angleDiff
        }

        val avgJerk = totalJerk / (data.size - 1)
        return (100 - avgJerk.coerceIn(0f, 100f)).coerceIn(0f, 100f)
    }

    /**
     * 计算运动范围
     */
    private fun calculateRangeOfMotion(data: List<SensorData>): Float {
        if (data.isEmpty()) return 0f

        val shoulderRange = data.maxOf { it.shoulderAngle } - data.minOf { it.shoulderAngle }
        val elbowRange = data.maxOf { it.elbowAngle } - data.minOf { it.elbowAngle }

        return ((shoulderRange + elbowRange) / 3.6f).coerceIn(0f, 100f)
    }

    /**
     * 计算力量评分
     */
    private fun calculateStrength(data: List<SensorData>): Float {
        if (data.isEmpty()) return 0f

        val avgForce = data.map { it.shoulderForce + it.elbowForce }.average().toFloat()
        return (avgForce * 2).coerceIn(0f, 100f)
    }

    /**
     * 生成康复建议
     */
    private fun generateRecommendation(smoothness: Float, rangeOfMotion: Float, strength: Float): String {
        return when {
            smoothness < 50 -> "建议：增加运动控制训练，提高动作平滑度"
            rangeOfMotion < 50 -> "建议：扩大运动范围，进行拉伸训练"
            strength < 50 -> "建议：增强力量训练，提高肌肉力量"
            else -> "康复进展良好，继续保持当前训练强度"
        }
    }

    /**
     * 释放资源
     */
    fun release() {
        interpreter?.close()
        interpreter = null
    }
}
