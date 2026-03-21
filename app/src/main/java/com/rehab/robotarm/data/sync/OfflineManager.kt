package com.rehab.robotarm.data.sync

import android.content.Context
import androidx.work.*
import com.rehab.robotarm.data.database.AppDatabase
import com.rehab.robotarm.data.repository.TrainingRepository
import java.util.concurrent.TimeUnit

/**
 * 离线数据同步管理器
 */
class OfflineManager(private val context: Context) {

    private val workManager = WorkManager.getInstance(context)

    /**
     * 调度自动同步任务
     */
    fun scheduleSync() {
        val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
            repeatInterval = 15,
            repeatIntervalTimeUnit = TimeUnit.MINUTES
        )
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .setRequiresBatteryNotLow(true)
                    .build()
            )
            .build()

        workManager.enqueueUniquePeriodicWork(
            "training_data_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            syncWork
        )
    }

    /**
     * 立即同步
     */
    fun syncNow() {
        val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .build()

        workManager.enqueue(syncWork)
    }

    /**
     * 取消同步
     */
    fun cancelSync() {
        workManager.cancelUniqueWork("training_data_sync")
    }
}

/**
 * 同步Worker
 */
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val database = AppDatabase.getDatabase(applicationContext)
            val trainingRepository = TrainingRepository(
                database.trainingSessionDao(),
                database.trainingRecordDao(),
                database.trainingPlanDao()
            )

            // 获取未同步的训练会话
            val pendingSessions = trainingRepository.getUnsyncedSessions()

            // 上传到云端
            pendingSessions.forEach { session ->
                try {
                    // TODO: 实现云端上传逻辑
                    // cloudApi.uploadSession(session)

                    // 标记为已同步
                    trainingRepository.markSynced(session.id)
                } catch (e: Exception) {
                    // 记录错误，继续处理下一个
                }
            }

            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
