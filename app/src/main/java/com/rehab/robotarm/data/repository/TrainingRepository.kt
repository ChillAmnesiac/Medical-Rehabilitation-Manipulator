package com.rehab.robotarm.data.repository

import com.rehab.robotarm.data.database.dao.TrainingSessionDao
import com.rehab.robotarm.data.database.dao.TrainingRecordDao
import com.rehab.robotarm.data.database.dao.TrainingPlanDao
import com.rehab.robotarm.data.database.entity.TrainingSession
import com.rehab.robotarm.data.database.entity.TrainingRecord
import com.rehab.robotarm.data.database.entity.TrainingPlan
import com.rehab.robotarm.data.database.entity.WeekPlan
import com.rehab.robotarm.data.database.entity.Exercise
import kotlinx.coroutines.flow.Flow

class TrainingRepository(
    private val sessionDao: TrainingSessionDao,
    private val recordDao: TrainingRecordDao,
    private val planDao: TrainingPlanDao
) {
    fun getSessionsByPatient(patientId: String): Flow<List<TrainingSession>> {
        return sessionDao.getSessionsByPatient(patientId)
    }

    suspend fun getSessionById(sessionId: String): TrainingSession? {
        return sessionDao.getSessionById(sessionId)
    }

    suspend fun getSessionsInRange(patientId: String, startTime: Long, endTime: Long): List<TrainingSession> {
        return sessionDao.getSessionsInRange(patientId, startTime, endTime)
    }

    suspend fun insertSession(session: TrainingSession): Long {
        return sessionDao.insertSession(session)
    }

    suspend fun updateSession(session: TrainingSession) {
        sessionDao.updateSession(session)
    }

    suspend fun deleteSession(session: TrainingSession) {
        sessionDao.deleteSession(session)
    }

    suspend fun getUnsyncedSessions(): List<TrainingSession> {
        return sessionDao.getUnsyncedSessions()
    }

    suspend fun markSynced(sessionId: String) {
        sessionDao.markSynced(sessionId)
    }

    suspend fun getAverageScore(patientId: String): Float {
        return sessionDao.getAverageScore(patientId) ?: 0f
    }

    suspend fun getTotalSessionCount(patientId: String): Int {
        return sessionDao.getTotalSessionCount(patientId)
    }

    fun getRecordsBySession(sessionId: String): Flow<List<TrainingRecord>> {
        return recordDao.getRecordsBySession(sessionId)
    }

    suspend fun insertRecord(record: TrainingRecord) {
        recordDao.insertRecord(record)
    }

    suspend fun insertRecords(records: List<TrainingRecord>) {
        recordDao.insertRecords(records)
    }

    // 训练计划相关
    fun getActivePlan(patientId: String): Flow<TrainingPlan?> {
        return planDao.getActivePlan(patientId)
    }

    suspend fun getPlanById(planId: String): TrainingPlan? {
        return planDao.getPlanById(planId)
    }

    suspend fun insertPlan(plan: TrainingPlan) {
        planDao.insertPlan(plan)
    }

    suspend fun updatePlan(plan: TrainingPlan) {
        planDao.updatePlan(plan)
    }

    suspend fun deactivateAllPlans(patientId: String) {
        planDao.deactivateAllPlans(patientId)
    }

    fun getWeekPlans(planId: String): Flow<List<WeekPlan>> {
        return planDao.getWeekPlans(planId)
    }

    suspend fun insertWeekPlan(weekPlan: WeekPlan) {
        planDao.insertWeekPlan(weekPlan)
    }

    fun getExercises(weekPlanId: String): Flow<List<Exercise>> {
        return planDao.getExercises(weekPlanId)
    }

    suspend fun insertExercise(exercise: Exercise) {
        planDao.insertExercise(exercise)
    }

    suspend fun insertExercises(exercises: List<Exercise>) {
        planDao.insertExercises(exercises)
    }
}
