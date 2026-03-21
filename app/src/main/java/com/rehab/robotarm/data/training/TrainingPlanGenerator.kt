package com.rehab.robotarm.data.training

import com.rehab.robotarm.data.cloud.OpenClawService
import com.rehab.robotarm.data.database.entity.*
import com.rehab.robotarm.data.repository.TrainingRepository
import com.rehab.robotarm.data.repository.PatientRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.UUID

/**
 * 智能训练计划生成器
 * 基于OpenClaw AI生成个性化训练计划
 */
class TrainingPlanGenerator(
    private val openClawService: OpenClawService,
    private val trainingRepository: TrainingRepository,
    private val patientRepository: PatientRepository
) {

    /**
     * 生成个性化训练计划
     */
    suspend fun generatePlan(
        patient: Patient,
        durationWeeks: Int = 4,
        targetScore: Float = 80f
    ): Result<TrainingPlan> = withContext(Dispatchers.IO) {
        try {
            // 1. 分析历史数据
            val history = trainingRepository.getSessionsInRange(
                patientId = patient.id,
                startTime = System.currentTimeMillis() - (90L * 24 * 60 * 60 * 1000), // 最近90天
                endTime = System.currentTimeMillis()
            )

            val analysis = analyzeHistory(history)

            // 2. 构建OpenClaw提示词
            val prompt = buildPrompt(patient, analysis, durationWeeks, targetScore)

            // 3. 调用OpenClaw生成计划
            val response = openClawService.sendMessage(prompt)

            if (response.success) {
                // 4. 解析响应并创建训练计划
                val plan = parseTrainingPlan(response.message, patient.id, durationWeeks)
                Result.success(plan)
            } else {
                // 如果OpenClaw不可用，使用基于规则的生成
                val plan = generateRuleBasedPlan(patient, analysis, durationWeeks, targetScore)
                Result.success(plan)
            }
        } catch (e: Exception) {
            // 降级到基于规则的生成
            val analysis = HistoryAnalysis()
            val plan = generateRuleBasedPlan(patient, analysis, durationWeeks, targetScore)
            Result.success(plan)
        }
    }

    /**
     * 分析历史训练数据
     */
    private fun analyzeHistory(history: List<TrainingSession>): HistoryAnalysis {
        if (history.isEmpty()) {
            return HistoryAnalysis()
        }

        val avgScore = history.map { it.overallScore }.average().toFloat()
        val avgDuration = history.map { it.duration }.average().toFloat()
        val avgHeartRate = history.mapNotNull { it.avgHeartRate }.average().toInt()
        val maxAngle = history.maxOfOrNull { it.maxShoulderAngle } ?: 0f
        val avgPainLevel = history.mapNotNull { it.painLevel }.average().toFloat()
        val avgFatigueLevel = history.mapNotNull { it.fatigueLevel }.average().toFloat()

        // 计算进步趋势
        val recentSessions = history.takeLast(5)
        val recentAvgScore = recentSessions.map { it.overallScore }.average().toFloat()
        val improvementTrend = if (history.size >= 5) {
            recentAvgScore - avgScore
        } else {
            0f
        }

        return HistoryAnalysis(
            totalSessions = history.size,
            averageScore = avgScore,
            averageDuration = avgDuration,
            averageHeartRate = avgHeartRate,
            maxAngleAchieved = maxAngle,
            averagePainLevel = avgPainLevel,
            averageFatigueLevel = avgFatigueLevel,
            improvementTrend = improvementTrend
        )
    }

    /**
     * 构建OpenClaw提示词
     */
    private fun buildPrompt(
        patient: Patient,
        analysis: HistoryAnalysis,
        weeks: Int,
        targetScore: Float
    ): String {
        return """
            请为以下患者生成一个为期${weeks}周的康复训练计划：

            患者信息:
            - 年龄: ${patient.age}岁
            - 性别: ${patient.gender}
            - 诊断: ${patient.diagnosis}
            - 当前ROM: ${patient.currentROM}°
            - 力量水平: ${patient.strengthLevel}/10

            历史训练数据:
            - 总训练次数: ${analysis.totalSessions}
            - 平均分数: ${analysis.averageScore.toInt()}
            - 平均训练时长: ${(analysis.averageDuration / 60).toInt()}分钟
            - 最大角度: ${analysis.maxAngleAchieved.toInt()}°
            - 平均疼痛等级: ${analysis.averagePainLevel.toInt()}/10
            - 进步趋势: ${if (analysis.improvementTrend > 0) "上升" else "平稳"}

            目标:
            - 目标分数: ${targetScore.toInt()}
            - 训练周期: ${weeks}周

            请生成包含以下内容的训练计划:
            1. 每周训练频率（建议3-5次/周）
            2. 每次训练时长（建议20-40分钟）
            3. 具体训练动作和参数（角度、重复次数、休息时间）
            4. 难度递进策略
            5. 进度评估标准
            6. 注意事项和安全提示

            请以JSON格式返回，包含weeks数组，每个week包含exercises数组。
        """.trimIndent()
    }

    /**
     * 解析OpenClaw返回的训练计划
     */
    private fun parseTrainingPlan(
        response: String,
        patientId: String,
        weeks: Int
    ): TrainingPlan {
        // TODO: 实现JSON解析
        // 这里简化处理，实际应该解析OpenClaw返回的JSON
        return generateRuleBasedPlan(
            Patient(
                id = patientId,
                name = "",
                age = 0,
                gender = "",
                diagnosis = "",
                admissionDate = 0,
                doctorId = ""
            ),
            HistoryAnalysis(),
            weeks,
            80f
        )
    }

    /**
     * 基于规则生成训练计划（降级方案）
     */
    private fun generateRuleBasedPlan(
        patient: Patient,
        analysis: HistoryAnalysis,
        weeks: Int,
        targetScore: Float
    ): TrainingPlan {
        val planId = UUID.randomUUID().toString()

        // 创建训练计划
        val plan = TrainingPlan(
            id = planId,
            patientId = patient.id,
            name = "${weeks}周康复训练计划",
            description = "根据患者情况自动生成的个性化训练计划",
            totalWeeks = weeks,
            goals = buildGoals(patient, targetScore)
        )

        // 生成每周计划
        val weekPlans = mutableListOf<WeekPlan>()
        for (weekNum in 1..weeks) {
            val weekPlan = generateWeekPlan(planId, weekNum, weeks, patient, analysis)
            weekPlans.add(weekPlan)
        }

        return plan
    }

    /**
     * 生成周计划
     */
    private fun generateWeekPlan(
        planId: String,
        weekNumber: Int,
        totalWeeks: Int,
        patient: Patient,
        analysis: HistoryAnalysis
    ): WeekPlan {
        val weekPlanId = UUID.randomUUID().toString()

        // 根据周数递进难度
        val difficultyFactor = weekNumber.toFloat() / totalWeeks
        val baseFrequency = 3
        val frequency = (baseFrequency + (difficultyFactor * 2).toInt()).coerceIn(3, 5)
        val baseDuration = 20
        val duration = (baseDuration + (difficultyFactor * 20).toInt()).coerceIn(20, 40)

        // 生成训练动作
        val exercises = generateExercises(weekPlanId, weekNumber, patient, analysis, difficultyFactor)

        return WeekPlan(
            id = weekPlanId,
            planId = planId,
            weekNumber = weekNumber,
            frequency = frequency,
            duration = duration,
            exercises = exercisesToJson(exercises)
        )
    }

    /**
     * 生成训练动作
     */
    private fun generateExercises(
        weekPlanId: String,
        weekNumber: Int,
        patient: Patient,
        analysis: HistoryAnalysis,
        difficultyFactor: Float
    ): List<Exercise> {
        val exercises = mutableListOf<Exercise>()

        // 1. 肩关节前屈训练
        exercises.add(
            Exercise(
                id = UUID.randomUUID().toString(),
                weekPlanId = weekPlanId,
                name = "肩关节前屈训练",
                targetAngle = (60f + difficultyFactor * 60f).coerceIn(60f, 120f),
                repetitions = (8 + (difficultyFactor * 7).toInt()).coerceIn(8, 15),
                restTime = 30,
                difficulty = getDifficulty(difficultyFactor),
                instructions = "缓慢抬起手臂至目标角度，保持2秒后缓慢放下"
            )
        )

        // 2. 肩关节外展训练
        exercises.add(
            Exercise(
                id = UUID.randomUUID().toString(),
                weekPlanId = weekPlanId,
                name = "肩关节外展训练",
                targetAngle = (50f + difficultyFactor * 50f).coerceIn(50f, 100f),
                repetitions = (8 + (difficultyFactor * 7).toInt()).coerceIn(8, 15),
                restTime = 30,
                difficulty = getDifficulty(difficultyFactor),
                instructions = "向侧面抬起手臂至目标角度，保持2秒后缓慢放下"
            )
        )

        // 3. 肘关节屈伸训练
        exercises.add(
            Exercise(
                id = UUID.randomUUID().toString(),
                weekPlanId = weekPlanId,
                name = "肘关节屈伸训练",
                targetAngle = (90f + difficultyFactor * 45f).coerceIn(90f, 135f),
                repetitions = (10 + (difficultyFactor * 10).toInt()).coerceIn(10, 20),
                restTime = 20,
                difficulty = getDifficulty(difficultyFactor),
                instructions = "弯曲肘关节至目标角度，保持1秒后伸直"
            )
        )

        // 4. 协调性训练
        if (weekNumber >= 2) {
            exercises.add(
                Exercise(
                    id = UUID.randomUUID().toString(),
                    weekPlanId = weekPlanId,
                    name = "肩肘协调训练",
                    targetAngle = (70f + difficultyFactor * 40f).coerceIn(70f, 110f),
                    repetitions = (6 + (difficultyFactor * 6).toInt()).coerceIn(6, 12),
                    restTime = 40,
                    difficulty = getDifficulty(difficultyFactor),
                    instructions = "同时进行肩关节和肘关节运动，保持动作流畅"
                )
            )
        }

        // 5. 阻力训练（后期）
        if (weekNumber >= 3) {
            exercises.add(
                Exercise(
                    id = UUID.randomUUID().toString(),
                    weekPlanId = weekPlanId,
                    name = "阻力对抗训练",
                    targetAngle = (60f + difficultyFactor * 50f).coerceIn(60f, 110f),
                    repetitions = (5 + (difficultyFactor * 5).toInt()).coerceIn(5, 10),
                    restTime = 60,
                    difficulty = "hard",
                    instructions = "在机械臂提供的阻力下完成运动，增强肌肉力量"
                )
            )
        }

        return exercises
    }

    /**
     * 构建训练目标
     */
    private fun buildGoals(patient: Patient, targetScore: Float): String {
        val goals = listOf(
            "提高关节活动度至${(patient.currentROM + 30).toInt()}°",
            "增强肌肉力量至${(patient.strengthLevel + 3).coerceAtMost(10)}级",
            "达到训练分数${targetScore.toInt()}分",
            "减少疼痛和不适感",
            "提高日常生活自理能力"
        )
        return goals.joinToString(",")
    }

    /**
     * 获取难度等级
     */
    private fun getDifficulty(factor: Float): String {
        return when {
            factor < 0.33f -> "easy"
            factor < 0.67f -> "medium"
            else -> "hard"
        }
    }

    /**
     * 动作列表转JSON
     */
    private fun exercisesToJson(exercises: List<Exercise>): String {
        // 简化版，实际应该使用Gson
        return exercises.joinToString(",") { it.name }
    }
}

/**
 * 历史分析结果
 */
data class HistoryAnalysis(
    val totalSessions: Int = 0,
    val averageScore: Float = 0f,
    val averageDuration: Float = 0f,
    val averageHeartRate: Int = 0,
    val maxAngleAchieved: Float = 0f,
    val averagePainLevel: Float = 0f,
    val averageFatigueLevel: Float = 0f,
    val improvementTrend: Float = 0f
)
