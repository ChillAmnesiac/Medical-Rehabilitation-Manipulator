package com.rehab.robotarm.data.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.rehab.robotarm.data.database.dao.*
import com.rehab.robotarm.data.database.entity.*

@Database(
    entities = [
        User::class,
        UserProfile::class,
        Patient::class,
        TrainingSession::class,
        TrainingRecord::class,
        LeaderboardEntry::class,
        Achievement::class,
        TrainingPlan::class,
        WeekPlan::class,
        Exercise::class,
        SensorRecord::class,
        RehabAssessment::class
    ],
    version = 3,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun userProfileDao(): UserProfileDao
    abstract fun patientDao(): PatientDao
    abstract fun trainingSessionDao(): TrainingSessionDao
    abstract fun trainingRecordDao(): TrainingRecordDao
    abstract fun leaderboardDao(): LeaderboardDao
    abstract fun achievementDao(): AchievementDao
    abstract fun trainingPlanDao(): TrainingPlanDao
    abstract fun sensorRecordDao(): SensorRecordDao
    abstract fun rehabAssessmentDao(): RehabAssessmentDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "rehab_robot_database"
                )
                    .fallbackToDestructiveMigration()
                    .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
