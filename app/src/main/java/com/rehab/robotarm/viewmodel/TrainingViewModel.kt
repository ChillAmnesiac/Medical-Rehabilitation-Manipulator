package com.rehab.robotarm.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.database.entity.TrainingSession
import com.rehab.robotarm.data.database.entity.TrainingRecord
import com.rehab.robotarm.data.repository.TrainingRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

class TrainingViewModel(
    private val trainingRepository: TrainingRepository
) : ViewModel() {

    private val _sessions = MutableStateFlow<List<TrainingSession>>(emptyList())
    val sessions: StateFlow<List<TrainingSession>> = _sessions

    private val _currentSession = MutableStateFlow<TrainingSession?>(null)
    val currentSession: StateFlow<TrainingSession?> = _currentSession

    private val _records = MutableStateFlow<List<TrainingRecord>>(emptyList())
    val records: StateFlow<List<TrainingRecord>> = _records

    private val _isTraining = MutableStateFlow(false)
    val isTraining: StateFlow<Boolean> = _isTraining

    fun loadSessions(patientId: String) {
        viewModelScope.launch {
            trainingRepository.getSessionsByPatient(patientId).collect { sessionList ->
                _sessions.value = sessionList
            }
        }
    }

    fun startTraining(patientId: String, mode: String) {
        viewModelScope.launch {
            val session = TrainingSession(
                id = UUID.randomUUID().toString(),
                patientId = patientId,
                startTime = System.currentTimeMillis(),
                mode = mode
            )
            trainingRepository.insertSession(session)
            _currentSession.value = session
            _isTraining.value = true
        }
    }

    fun stopTraining(
        overallScore: Float,
        painLevel: Int,
        fatigueLevel: Int,
        notes: String = ""
    ) {
        viewModelScope.launch {
            _currentSession.value?.let { session ->
                val endTime = System.currentTimeMillis()
                val updatedSession = session.copy(
                    endTime = endTime,
                    duration = (endTime - session.startTime) / 1000,
                    overallScore = overallScore,
                    painLevel = painLevel,
                    fatigueLevel = fatigueLevel,
                    notes = notes
                )
                trainingRepository.updateSession(updatedSession)
                _isTraining.value = false
                _currentSession.value = null
            }
        }
    }

    fun addRecord(record: TrainingRecord) {
        viewModelScope.launch {
            trainingRepository.insertRecord(record)
        }
    }

    fun loadRecords(sessionId: String) {
        viewModelScope.launch {
            trainingRepository.getRecordsBySession(sessionId).collect { recordList ->
                _records.value = recordList
            }
        }
    }

    suspend fun getAverageScore(patientId: String): Float {
        return trainingRepository.getAverageScore(patientId)
    }

    suspend fun getTotalSessionCount(patientId: String): Int {
        return trainingRepository.getTotalSessionCount(patientId)
    }
}
