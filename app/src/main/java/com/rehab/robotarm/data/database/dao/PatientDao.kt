package com.rehab.robotarm.data.database.dao

import androidx.room.*
import com.rehab.robotarm.data.database.entity.Patient
import kotlinx.coroutines.flow.Flow

@Dao
interface PatientDao {
    @Query("SELECT * FROM patients WHERE isActive = 1 ORDER BY updatedAt DESC")
    fun getAllPatients(): Flow<List<Patient>>

    @Query("SELECT * FROM patients WHERE id = :patientId")
    suspend fun getPatientById(patientId: String): Patient?

    @Query("SELECT * FROM patients WHERE id = :patientId")
    fun getPatientByIdFlow(patientId: String): Flow<Patient?>

    @Query("SELECT * FROM patients WHERE doctorId = :doctorId AND isActive = 1")
    fun getPatientsByDoctor(doctorId: String): Flow<List<Patient>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPatient(patient: Patient)

    @Update
    suspend fun updatePatient(patient: Patient)

    @Query("UPDATE patients SET isActive = 0 WHERE id = :patientId")
    suspend fun deactivatePatient(patientId: String)

    @Delete
    suspend fun deletePatient(patient: Patient)

    @Query("SELECT COUNT(*) FROM patients WHERE isActive = 1")
    suspend fun getActivePatientCount(): Int
}
