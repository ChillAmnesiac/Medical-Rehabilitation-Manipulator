package com.rehab.robotarm.data.repository

import com.rehab.robotarm.data.database.dao.PatientDao
import com.rehab.robotarm.data.database.entity.Patient
import kotlinx.coroutines.flow.Flow

class PatientRepository(private val patientDao: PatientDao) {

    fun getAllPatients(): Flow<List<Patient>> {
        return patientDao.getAllPatients()
    }

    suspend fun getPatientById(patientId: String): Patient? {
        return patientDao.getPatientById(patientId)
    }

    fun getPatientByIdFlow(patientId: String): Flow<Patient?> {
        return patientDao.getPatientByIdFlow(patientId)
    }

    fun getPatientsByDoctor(doctorId: String): Flow<List<Patient>> {
        return patientDao.getPatientsByDoctor(doctorId)
    }

    suspend fun insertPatient(patient: Patient) {
        patientDao.insertPatient(patient)
    }

    suspend fun updatePatient(patient: Patient) {
        val updated = patient.copy(updatedAt = System.currentTimeMillis())
        patientDao.updatePatient(updated)
    }

    suspend fun deactivatePatient(patientId: String) {
        patientDao.deactivatePatient(patientId)
    }

    suspend fun getActivePatientCount(): Int {
        return patientDao.getActivePatientCount()
    }
}
