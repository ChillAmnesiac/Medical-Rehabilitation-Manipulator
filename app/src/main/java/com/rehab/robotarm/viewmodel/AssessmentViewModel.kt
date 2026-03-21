package com.rehab.robotarm.viewmodel

import android.app.Application
import android.os.Environment
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.database.AppDatabase
import com.rehab.robotarm.data.database.entity.Patient
import com.rehab.robotarm.data.database.entity.RehabAssessment
import com.rehab.robotarm.data.database.entity.TrainingSession
import com.rehab.robotarm.data.export.PdfExporter
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

class AssessmentViewModel(application: Application) : AndroidViewModel(application) {
    private val database = AppDatabase.getDatabase(application)
    private val assessmentDao = database.rehabAssessmentDao()
    private val patientDao = database.patientDao()
    private val sessionDao = database.trainingSessionDao()
    private val pdfExporter = PdfExporter(application)

    fun getAssessmentsByPatient(patientId: String): Flow<List<RehabAssessment>> {
        // 需要通过 session 关联查询
        return assessmentDao.getAllAssessments()
    }

    fun getPatient(patientId: String): Flow<Patient?> {
        return patientDao.getPatientByIdFlow(patientId)
    }

    fun getSessionsByPatient(patientId: String) = sessionDao.getSessionsByPatient(patientId)

    suspend fun exportPdfReport(
        context: android.content.Context,
        patient: Patient,
        sessions: List<TrainingSession>,
        assessments: List<RehabAssessment>
    ): Result<File> = withContext(Dispatchers.IO) {
        try {
            val dateFormat = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault())
            val fileName = "康复报告_${patient.name}_${dateFormat.format(Date())}.pdf"

            val outputDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            if (!outputDir.exists()) {
                outputDir.mkdirs()
            }

            val outputFile = File(outputDir, fileName)
            pdfExporter.generateRehabReport(patient, sessions, assessments, outputFile)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun createAssessment(assessment: RehabAssessment) {
        viewModelScope.launch(Dispatchers.IO) {
            assessmentDao.insert(assessment)
        }
    }

    suspend fun getAverageScore(startTime: Long): Float? {
        return assessmentDao.getAverageScore(startTime)
    }
}
