package com.rehab.robotarm.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.database.entity.Patient
import com.rehab.robotarm.data.repository.PatientRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

class PatientViewModel(
    private val patientRepository: PatientRepository
) : ViewModel() {

    private val _patients = MutableStateFlow<List<Patient>>(emptyList())
    val patients: StateFlow<List<Patient>> = _patients

    private val _selectedPatient = MutableStateFlow<Patient?>(null)
    val selectedPatient: StateFlow<Patient?> = _selectedPatient

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    init {
        loadPatients()
    }

    fun loadPatients() {
        viewModelScope.launch {
            _isLoading.value = true
            patientRepository.getAllPatients().collect { patientList ->
                _patients.value = patientList
                _isLoading.value = false
            }
        }
    }

    fun selectPatient(patientId: String) {
        viewModelScope.launch {
            patientRepository.getPatientByIdFlow(patientId).collect { patient ->
                _selectedPatient.value = patient
            }
        }
    }

    fun addPatient(
        name: String,
        age: Int,
        gender: String,
        diagnosis: String,
        doctorId: String,
        notes: String = ""
    ) {
        viewModelScope.launch {
            val patient = Patient(
                id = UUID.randomUUID().toString(),
                name = name,
                age = age,
                gender = gender,
                diagnosis = diagnosis,
                admissionDate = System.currentTimeMillis(),
                doctorId = doctorId,
                notes = notes
            )
            patientRepository.insertPatient(patient)
        }
    }

    fun updatePatient(patient: Patient) {
        viewModelScope.launch {
            patientRepository.updatePatient(patient)
        }
    }

    fun deactivatePatient(patientId: String) {
        viewModelScope.launch {
            patientRepository.deactivatePatient(patientId)
        }
    }
}
