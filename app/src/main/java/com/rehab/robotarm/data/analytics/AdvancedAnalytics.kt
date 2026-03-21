package com.rehab.robotarm.data.analytics

import com.rehab.robotarm.data.database.entity.Patient
import com.rehab.robotarm.data.database.entity.TrainingSession
import com.rehab.robotarm.data.database.entity.TrainingRecord
import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.sqrt

/**
 * 高级数据分析引擎
 * 提供康复时间预测、异常检测、同龄对比等功能
 */
class AdvancedAnalytics {

    /**
     * 康复进度预测
     * 使用线性回归预测达到目标分数所需时间
     */
    suspend fun predictRecoveryTime(
        patientId: String,
        history: List<TrainingSession>,
        targetScore: Float = 80f
    ): PredictionResult {
        if (history.size < 3) {
            return PredictionResult(
                estimatedDays = -1,
                confidence = 0f,
                recommendation = "训练数据不足，需要至少3次训练记录"
            )
        }

        // 准备数据
        val sessions = history.sortedBy { it.startTime }
        val x = sessions.mapIndexed { index, _ -> index.toDouble() }
        val y = sessions.map { it.overallScore.toDouble() }

        // 线性回归
        val regression = linearRegression(x, y)
        val slope = regression.first
        val intercept = regression.second

        // 预测达到目标分数需要的训练次数
        val currentScore = y.lastOrNull() ?: 0.0
        if (slope <= 0) {
            return PredictionResult(
                estimatedDays = -1,
                confidence = 0f,
                recommendation = "训练进度未见改善，建议调整训练方案"
            )
        }

        val sessionsNeeded = ((targetScore - intercept) / slope).toInt()
        val remainingSessions = (sessionsNeeded - sessions.size).coerceAtLeast(0)

        // 计算平均训练间隔（天）
        val avgInterval = if (sessions.size > 1) {
            val intervals = sessions.zipWithNext { a, b ->
                (b.startTime - a.startTime) / (1000 * 60 * 60 * 24)
            }
            intervals.average()
        } else {
            3.0 // 默认3天一次
        }

        val estimatedDays = (remainingSessions * avgInterval).toInt()

        // 计算置信度（基于R²）
        val confidence = calculateRSquared(x, y, slope, intercept)

        val recommendation = when {
            estimatedDays <= 30 -> "预计1个月内可达到目标，保持当前训练强度"
            estimatedDays <= 90 -> "预计3个月内可达到目标，建议增加训练频率"
            else -> "预计需要较长时间，建议咨询医生调整训练方案"
        }

        return PredictionResult(
            estimatedDays = estimatedDays,
            confidence = confidence.toFloat(),
            recommendation = recommendation,
            currentScore = currentScore.toFloat(),
            targetScore = targetScore,
            improvementRate = slope.toFloat()
        )
    }

    /**
     * 异常检测
     * 检测训练过程中的异常情况
     */
    fun detectAnomalies(
        sensorData: List<TrainingRecord>,
        session: TrainingSession
    ): List<Anomaly> {
        val anomalies = mutableListOf<Anomaly>()

        sensorData.forEach { record ->
            // 心率异常检测
            if (record.heartRate > 120 || record.heartRate < 50) {
                anomalies.add(
                    Anomaly(
                        type = AnomalyType.HEART_RATE,
                        severity = if (record.heartRate > 140 || record.heartRate < 40)
                            Severity.HIGH else Severity.MEDIUM,
                        value = record.heartRate.toFloat(),
                        timestamp = record.timestamp,
                        description = "心率异常: ${record.heartRate} bpm"
                    )
                )
            }

            // 血氧异常检测
            if (record.spo2 < 90) {
                anomalies.add(
                    Anomaly(
                        type = AnomalyType.SPO2,
                        severity = if (record.spo2 < 85) Severity.HIGH else Severity.MEDIUM,
                        value = record.spo2.toFloat(),
                        timestamp = record.timestamp,
                        description = "血氧偏低: ${record.spo2}%"
                    )
                )
            }

            // EMG信号异常检测（突然下降可能表示疲劳）
            if (record.emgCh1 < 0.1f && record.emgCh2 < 0.1f) {
                anomalies.add(
                    Anomaly(
                        type = AnomalyType.FATIGUE,
                        severity = Severity.LOW,
                        value = (record.emgCh1 + record.emgCh2) / 2,
                        timestamp = record.timestamp,
                        description = "肌肉活动减弱，可能疲劳"
                    )
                )
            }

            // 扭矩异常检测（过大可能导致损伤）
            val totalTorque = sqrt(
                record.torqueX.pow(2) + record.torqueY.pow(2) + record.torqueZ.pow(2)
            )
            if (totalTorque > 50f) {
                anomalies.add(
                    Anomaly(
                        type = AnomalyType.EXCESSIVE_FORCE,
                        severity = Severity.HIGH,
                        value = totalTorque,
                        timestamp = record.timestamp,
                        description = "扭矩过大: ${totalTorque.toInt()} Nm"
                    )
                )
            }
        }

        // 检测运动异常（突然停止、抖动等）
        detectMotionAnomalies(sensorData, anomalies)

        return anomalies
    }

    /**
     * 检测运动异常
     */
    private fun detectMotionAnomalies(
        sensorData: List<TrainingRecord>,
        anomalies: MutableList<Anomaly>
    ) {
        if (sensorData.size < 3) return

        for (i in 1 until sensorData.size - 1) {
            val prev = sensorData[i - 1]
            val curr = sensorData[i]
            val next = sensorData[i + 1]

            // 检测突然停止
            val prevSpeed = abs(curr.shoulderAngle - prev.shoulderAngle)
            val currSpeed = abs(next.shoulderAngle - curr.shoulderAngle)

            if (prevSpeed > 5f && currSpeed < 0.5f) {
                anomalies.add(
                    Anomaly(
                        type = AnomalyType.SUDDEN_STOP,
                        severity = Severity.MEDIUM,
                        value = currSpeed,
                        timestamp = curr.timestamp,
                        description = "运动突然停止"
                    )
                )
            }

            // 检测抖动（加速度变化过大）
            val accelChange = sqrt(
                (curr.shoulderAngle - prev.shoulderAngle).pow(2) +
                (next.shoulderAngle - curr.shoulderAngle).pow(2)
            )
            if (accelChange > 20f) {
                anomalies.add(
                    Anomaly(
                        type = AnomalyType.TREMOR,
                        severity = Severity.LOW,
                        value = accelChange,
                        timestamp = curr.timestamp,
                        description = "检测到运动抖动"
                    )
                )
            }
        }
    }

    /**
     * 同龄对比分析
     */
    fun compareWithPeers(
        patient: Patient,
        peerPatients: List<Patient>,
        peerSessions: Map<String, List<TrainingSession>>
    ): ComparisonResult {
        if (peerPatients.isEmpty()) {
            return ComparisonResult(
                patientScore = patient.latestScore,
                peerAverage = 0f,
                percentile = 0f,
                ranking = 0,
                totalPeers = 0,
                recommendation = "暂无同龄对比数据"
            )
        }

        // 计算同龄患者平均分数
        val peerScores = peerPatients.map { it.latestScore }
        val avgScore = peerScores.average().toFloat()
        val maxScore = peerScores.maxOrNull() ?: 0f
        val minScore = peerScores.minOrNull() ?: 0f

        // 计算百分位
        val betterThanCount = peerScores.count { it < patient.latestScore }
        val percentile = (betterThanCount.toFloat() / peerScores.size) * 100

        // 计算排名
        val sortedScores = (peerScores + patient.latestScore).sortedDescending()
        val ranking = sortedScores.indexOf(patient.latestScore) + 1

        // 生成建议
        val recommendation = when {
            percentile >= 75 -> "表现优秀，超过${percentile.toInt()}%的同龄患者"
            percentile >= 50 -> "表现良好，处于中上水平"
            percentile >= 25 -> "表现一般，建议增加训练强度"
            else -> "需要加强训练，建议咨询医生调整方案"
        }

        return ComparisonResult(
            patientScore = patient.latestScore,
            peerAverage = avgScore,
            peerMax = maxScore,
            peerMin = minScore,
            percentile = percentile,
            ranking = ranking,
            totalPeers = peerPatients.size,
            recommendation = recommendation
        )
    }

    /**
     * 训练效果评估
     */
    fun evaluateTrainingEffectiveness(
        sessions: List<TrainingSession>
    ): EffectivenessReport {
        if (sessions.isEmpty()) {
            return EffectivenessReport(
                overallEffectiveness = 0f,
                consistencyScore = 0f,
                improvementRate = 0f,
                recommendation = "暂无训练数据"
            )
        }

        val sortedSessions = sessions.sortedBy { it.startTime }

        // 计算一致性分数（训练频率的稳定性）
        val consistencyScore = calculateConsistency(sortedSessions)

        // 计算改善率
        val scores = sortedSessions.map { it.overallScore.toDouble() }
        val x = scores.indices.map { it.toDouble() }
        val regression = linearRegression(x, scores)
        val improvementRate = regression.first.toFloat()

        // 计算整体有效性
        val avgScore = scores.average().toFloat()
        val recentAvg = scores.takeLast(5).average().toFloat()
        val overallEffectiveness = ((recentAvg / avgScore) * 100).coerceIn(0f, 100f)

        val recommendation = when {
            improvementRate > 2f -> "训练效果显著，继续保持"
            improvementRate > 0.5f -> "训练效果良好，可适当增加难度"
            improvementRate > 0f -> "训练效果一般，建议调整训练方案"
            else -> "训练效果不佳，建议咨询医生"
        }

        return EffectivenessReport(
            overallEffectiveness = overallEffectiveness,
            consistencyScore = consistencyScore,
            improvementRate = improvementRate,
            averageScore = avgScore,
            recentAverageScore = recentAvg,
            totalSessions = sessions.size,
            recommendation = recommendation
        )
    }

    /**
     * 最佳训练时间推荐
     */
    fun recommendBestTrainingTime(sessions: List<TrainingSession>): TimeRecommendation {
        if (sessions.size < 5) {
            return TimeRecommendation(
                recommendedHour = 9,
                recommendedDayOfWeek = listOf(1, 3, 5),
                reason = "建议上午9点训练，每周一、三、五"
            )
        }

        // 按小时统计平均分数
        val hourScores = sessions.groupBy { session ->
            val hour = java.util.Calendar.getInstance().apply {
                timeInMillis = session.startTime
            }.get(java.util.Calendar.HOUR_OF_DAY)
            hour
        }.mapValues { (_, sessions) ->
            sessions.map { it.overallScore }.average().toFloat()
        }

        val bestHour = hourScores.maxByOrNull { it.value }?.key ?: 9

        // 按星期统计
        val dayScores = sessions.groupBy { session ->
            val day = java.util.Calendar.getInstance().apply {
                timeInMillis = session.startTime
            }.get(java.util.Calendar.DAY_OF_WEEK)
            day
        }.mapValues { (_, sessions) ->
            sessions.map { it.overallScore }.average().toFloat()
        }

        val bestDays = dayScores.entries
            .sortedByDescending { it.value }
            .take(3)
            .map { it.key }

        return TimeRecommendation(
            recommendedHour = bestHour,
            recommendedDayOfWeek = bestDays,
            reason = "根据历史数据，您在${bestHour}点训练效果最好"
        )
    }

    // ========== 辅助函数 ==========

    /**
     * 线性回归
     * 返回 (斜率, 截距)
     */
    private fun linearRegression(x: List<Double>, y: List<Double>): Pair<Double, Double> {
        val n = x.size
        val sumX = x.sum()
        val sumY = y.sum()
        val sumXY = x.zip(y).sumOf { it.first * it.second }
        val sumX2 = x.sumOf { it * it }

        val slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
        val intercept = (sumY - slope * sumX) / n

        return Pair(slope, intercept)
    }

    /**
     * 计算R²（决定系数）
     */
    private fun calculateRSquared(
        x: List<Double>,
        y: List<Double>,
        slope: Double,
        intercept: Double
    ): Double {
        val yMean = y.average()
        val ssTot = y.sumOf { (it - yMean).pow(2) }
        val ssRes = x.zip(y).sumOf { (xi, yi) ->
            val predicted = slope * xi + intercept
            (yi - predicted).pow(2)
        }
        return 1 - (ssRes / ssTot)
    }

    /**
     * 计算训练一致性分数
     */
    private fun calculateConsistency(sessions: List<TrainingSession>): Float {
        if (sessions.size < 2) return 100f

        val intervals = sessions.zipWithNext { a, b ->
            (b.startTime - a.startTime) / (1000 * 60 * 60 * 24) // 天数
        }

        val avgInterval = intervals.average()
        val variance = intervals.map { (it - avgInterval).pow(2) }.average()
        val stdDev = sqrt(variance)

        // 标准差越小，一致性越高
        val consistencyScore = (100 - (stdDev / avgInterval * 100)).coerceIn(0.0, 100.0)

        return consistencyScore.toFloat()
    }
}

// ========== 数据类 ==========

data class PredictionResult(
    val estimatedDays: Int,
    val confidence: Float,
    val recommendation: String,
    val currentScore: Float = 0f,
    val targetScore: Float = 80f,
    val improvementRate: Float = 0f
)

data class Anomaly(
    val type: AnomalyType,
    val severity: Severity,
    val value: Float,
    val timestamp: Long,
    val description: String
)

enum class AnomalyType {
    HEART_RATE,
    SPO2,
    FATIGUE,
    EXCESSIVE_FORCE,
    SUDDEN_STOP,
    TREMOR
}

enum class Severity {
    LOW, MEDIUM, HIGH
}

data class ComparisonResult(
    val patientScore: Float,
    val peerAverage: Float,
    val peerMax: Float = 0f,
    val peerMin: Float = 0f,
    val percentile: Float,
    val ranking: Int,
    val totalPeers: Int,
    val recommendation: String
)

data class EffectivenessReport(
    val overallEffectiveness: Float,
    val consistencyScore: Float,
    val improvementRate: Float,
    val averageScore: Float = 0f,
    val recentAverageScore: Float = 0f,
    val totalSessions: Int = 0,
    val recommendation: String
)

data class TimeRecommendation(
    val recommendedHour: Int,
    val recommendedDayOfWeek: List<Int>,
    val reason: String
)
