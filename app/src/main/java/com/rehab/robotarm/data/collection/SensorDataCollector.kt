package com.rehab.robotarm.data.collection

import android.content.Context
import com.rehab.robotarm.data.database.AppDatabase
import com.rehab.robotarm.data.database.entity.SensorRecord
import com.rehab.robotarm.data.model.SensorData
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import java.util.UUID

/**
 * 传感器数据采集器
 * 负责按指定速率采集和存储传感器数据
 */
class SensorDataCollector(context: Context) {

    private val database = AppDatabase.getDatabase(context)
    private val sensorRecordDao = database.sensorRecordDao()

    private var collectionJob: Job? = null
    private var currentSessionId: String? = null

    private val _isCollecting = MutableStateFlow(false)
    val isCollecting: StateFlow<Boolean> = _isCollecting.asStateFlow()

    private val _collectionRate = MutableStateFlow(100L) // 默认100ms采集一次
    val collectionRate: StateFlow<Long> = _collectionRate.asStateFlow()

    private val _recordCount = MutableStateFlow(0)
    val recordCount: StateFlow<Int> = _recordCount.asStateFlow()

    /**
     * 开始采集数据
     * @param sensorDataFlow 传感器数据流
     * @param sessionId 会话ID，如果为null则自动生成
     */
    fun startCollection(
        sensorDataFlow: StateFlow<SensorData>,
        sessionId: String? = null
    ) {
        if (_isCollecting.value) {
            android.util.Log.w(TAG, "Collection already in progress")
            return
        }

        currentSessionId = sessionId ?: UUID.randomUUID().toString()
        _isCollecting.value = true
        _recordCount.value = 0

        android.util.Log.d(TAG, "Starting data collection, sessionId=$currentSessionId, rate=${_collectionRate.value}ms")

        collectionJob = CoroutineScope(Dispatchers.IO).launch {
            while (isActive && _isCollecting.value) {
                try {
                    val sensorData = sensorDataFlow.value
                    val record = convertToSensorRecord(sensorData, currentSessionId!!)
                    sensorRecordDao.insert(record)
                    _recordCount.value++

                    if (_recordCount.value % 100 == 0) {
                        android.util.Log.d(TAG, "Collected ${_recordCount.value} records")
                    }
                } catch (e: Exception) {
                    android.util.Log.e(TAG, "Error collecting data", e)
                }

                delay(_collectionRate.value)
            }
        }
    }

    /**
     * 停止采集数据
     */
    fun stopCollection() {
        android.util.Log.d(TAG, "Stopping data collection, total records: ${_recordCount.value}")
        _isCollecting.value = false
        collectionJob?.cancel()
        collectionJob = null
    }

    /**
     * 设置采集速率
     * @param rateMs 采集间隔（毫秒）
     */
    fun setCollectionRate(rateMs: Long) {
        _collectionRate.value = rateMs.coerceIn(10L, 10000L) // 限制在10ms到10s之间
        android.util.Log.d(TAG, "Collection rate set to ${_collectionRate.value}ms")
    }

    /**
     * 导出指定会话的数据为JSON
     */
    suspend fun exportSessionToJson(sessionId: String): String {
        val records = sensorRecordDao.getRecordsBySessionSync(sessionId)
        return com.google.gson.GsonBuilder()
            .setPrettyPrinting()
            .create()
            .toJson(records)
    }

    /**
     * 获取当前会话ID
     */
    fun getCurrentSessionId(): String? = currentSessionId

    /**
     * 转换SensorData到SensorRecord
     */
    private fun convertToSensorRecord(data: SensorData, sessionId: String): SensorRecord {
        return SensorRecord(
            sessionId = sessionId,
            timestamp = data.timestamp,
            emgCh1 = data.emgCh1,
            heartRate = data.heartRate,
            imuAngleX = data.imuAngleX,
            imuAngleY = data.imuAngleY,
            imuAngleZ = data.imuAngleZ,
            imuAccelX = data.imuAccelX,
            imuAccelY = data.imuAccelY,
            imuAccelZ = data.imuAccelZ,
            motor1Angle = data.motor1Angle,
            motor1Damping = data.motor1Damping,
            motor1Temp = data.motor1Temp,
            motor2Angle = data.motor2Angle,
            motor2Damping = data.motor2Damping,
            motor2Temp = data.motor2Temp
        )
    }

    companion object {
        private const val TAG = "SensorDataCollector"
    }
}
