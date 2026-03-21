package com.rehab.robotarm.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.cloud.OpenClawService
import com.rehab.robotarm.data.database.entity.TrainingPlan
import com.rehab.robotarm.data.database.entity.WeekPlan
import com.rehab.robotarm.data.database.entity.Exercise
import com.rehab.robotarm.data.repository.PatientRepository
import com.rehab.robotarm.data.repository.TrainingRepository
import com.rehab.robotarm.data.training.TrainingPlanGenerator
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class TrainingPlanViewModel(
    private val patientRepository: PatientRepository,
    private val trainingRepository: TrainingRepository,
    private val openClawService: OpenClawService
) : ViewModel() {

    private val planGenerator = TrainingPlanGenerator(
        openClawService,
        trainingRepository,
        patientRepository
    )

    private val _currentPlan = MutableStateFlow<TrainingPlan?>(null)
    val currentPlan: StateFlow<TrainingPlan?> = _currentPlan

    private val _weekPlans = MutableStateFlow<List<WeekPlan>>(emptyList())
    val weekPlans: StateFlow<List<WeekPlan>> = _weekPlans

    private val _isGenerating = MutableStateFlow(false)
    val isGenerating: StateFlow<Boolean> = _isGenerating

    private val _generationError = MutableStateFlow<String?>(null)
    val generationError: StateFlow<String?> = _generationError

    private val _isSaving = MutableStateFlow(false)
    val isSaving: StateFlow<Boolean> = _isSaving

    /**
     * 生成训练计划
     */
    fun generatePlan(
        patientId: String,
        durationWeeks: Int = 4,
        targetScore: Float = 80f
    ) {
        viewModelScope.launch {
            _isGenerating.value = true
            _generationError.value = null

            try {
                val patient = patientRepository.getPatientById(patientId)
                if (patient == null) {
                    _generationError.value = "患者不存在"
                    return@launch
                }

                val result = planGenerator.generatePlan(patient, durationWeeks, targetScore)

                if (result.isSuccess) {
                    val plan = result.getOrNull()!!
                    _currentPlan.value = plan
                    // 保存到数据库
                    savePlanToDatabase(plan)
                } else {
                    _generationError.value = result.exceptionOrNull()?.message ?: "生成失败"
                }
            } catch (e: Exception) {
                _generationError.value = e.message ?: "未知错误"
            } finally {
                _isGenerating.value = false
            }
        }
    }

    /**
     * 手动创建训练计划
     */
    fun createManualPlan(
        patientId: String,
        name: String,
        description: String,
        totalWeeks: Int,
        goals: String
    ) {
        viewModelScope.launch {
            _isSaving.value = true
            _generationError.value = null

            try {
                val plan = TrainingPlan(
                    patientId = patientId,
                    name = name,
                    description = description,
                    totalWeeks = totalWeeks,
                    goals = goals,
                    isActive = true
                )

                _currentPlan.value = plan
                savePlanToDatabase(plan)
            } catch (e: Exception) {
                _generationError.value = e.message ?: "保存失败"
            } finally {
                _isSaving.value = false
            }
        }
    }

    /**
     * 添加周计划
     */
    fun addWeekPlan(
        planId: String,
        weekNumber: Int,
        frequency: Int,
        duration: Int,
        exercises: String
    ) {
        viewModelScope.launch {
            try {
                val weekPlan = WeekPlan(
                    planId = planId,
                    weekNumber = weekNumber,
                    frequency = frequency,
                    duration = duration,
                    exercises = exercises
                )
                trainingRepository.insertWeekPlan(weekPlan)
                loadWeekPlans(planId)
            } catch (e: Exception) {
                _generationError.value = "添加周计划失败: ${e.message}"
            }
        }
    }

    /**
     * 保存计划到数据库
     */
    private suspend fun savePlanToDatabase(plan: TrainingPlan) {
        try {
            // 先停用该患者的其他计划
            trainingRepository.deactivateAllPlans(plan.patientId)
            // 保存新计划
            trainingRepository.insertPlan(plan)
        } catch (e: Exception) {
            _generationError.value = "保存失败: ${e.message}"
        }
    }

    /**
     * 加载训练计划
     */
    fun loadPlan(patientId: String) {
        viewModelScope.launch {
            try {
                trainingRepository.getActivePlan(patientId).collect { plan ->
                    _currentPlan.value = plan
                    plan?.let { loadWeekPlans(it.id) }
                }
            } catch (e: Exception) {
                _generationError.value = "加载失败: ${e.message}"
            }
        }
    }

    /**
     * 加载周计划
     */
    private fun loadWeekPlans(planId: String) {
        viewModelScope.launch {
            try {
                trainingRepository.getWeekPlans(planId).collect { plans ->
                    _weekPlans.value = plans
                }
            } catch (e: Exception) {
                _generationError.value = "加载周计划失败: ${e.message}"
            }
        }
    }
}
