package com.rehab.robotarm.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.analytics.*
import com.rehab.robotarm.data.repository.PatientRepository
import com.rehab.robotarm.data.repository.TrainingRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class AnalyticsViewModel(
    private val patientRepository: PatientRepository,
    private val trainingRepository: TrainingRepository
) : ViewModel() {

    private val analytics = AdvancedAnalytics()

    private val _prediction = MutableStateFlow<PredictionResult?>(null)
    val prediction: StateFlow<PredictionResult?> = _prediction

    private val _anomalies = MutableStateFlow<List<Anomaly>>(emptyList())
    val anomalies: StateFlow<List<Anomaly>> = _anomalies

    private val _comparison = MutableStateFlow<ComparisonResult?>(null)
    val comparison: StateFlow<ComparisonResult?> = _comparison

    private val _effectiveness = MutableStateFlow<EffectivenessReport?>(null)
    val effectiveness: StateFlow<EffectivenessReport?> = _effectiveness

    private val _timeRecommendation = MutableStateFlow<TimeRecommendation?>(null)
    val timeRecommendation: StateFlow<TimeRecommendation?> = _timeRecommendation

    fun loadAnalytics(patientId: String) {
        viewModelScope.launch {
            // 加载训练历史
            trainingRepository.getSessionsByPatient(patientId).collect { sessions ->
                if (sessions.isNotEmpty()) {
                    // 康复时间预测
                    val predictionResult = analytics.predictRecoveryTime(
                        patientId = patientId,
                        history = sessions,
                        targetScore = 80f
                    )
                    _prediction.value = predictionResult

                    // 训练效果评估
                    val effectivenessReport = analytics.evaluateTrainingEffectiveness(sessions)
                    _effectiveness.value = effectivenessReport

                    // 最佳训练时间推荐
                    val timeRec = analytics.recommendBestTrainingTime(sessions)
                    _timeRecommendation.value = timeRec

                    // 异常检测（最近一次训练）
                    val latestSession = sessions.maxByOrNull { it.startTime }
                    latestSession?.let { session ->
                        trainingRepository.getRecordsBySession(session.id).collect { records ->
                            val detectedAnomalies = analytics.detectAnomalies(records, session)
                            _anomalies.value = detectedAnomalies
                        }
                    }
                }
            }

            // 同龄对比
            val patient = patientRepository.getPatientById(patientId)
            patient?.let { p ->
                // 获取同龄患者（简化版，实际应该从数据库查询）
                patientRepository.getAllPatients().collect { allPatients ->
                    val peers = allPatients.filter {
                        it.id != patientId &&
                        kotlin.math.abs(it.age - p.age) <= 5 &&
                        it.diagnosis == p.diagnosis
                    }

                    if (peers.isNotEmpty()) {
                        val comparisonResult = analytics.compareWithPeers(
                            patient = p,
                            peerPatients = peers,
                            peerSessions = emptyMap() // 简化版
                        )
                        _comparison.value = comparisonResult
                    }
                }
            }
        }
    }
}
