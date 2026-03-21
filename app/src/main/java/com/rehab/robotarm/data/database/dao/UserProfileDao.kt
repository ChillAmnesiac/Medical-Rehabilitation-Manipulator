package com.rehab.robotarm.data.database.dao

import androidx.room.*
import com.rehab.robotarm.data.database.entity.UserProfile
import kotlinx.coroutines.flow.Flow

@Dao
interface UserProfileDao {
    @Query("SELECT * FROM user_profiles WHERE userId = :userId")
    suspend fun getProfile(userId: String): UserProfile?

    @Query("SELECT * FROM user_profiles WHERE userId = :userId")
    fun getProfileFlow(userId: String): Flow<UserProfile?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun createProfile(profile: UserProfile)

    @Update
    suspend fun updateProfile(profile: UserProfile)

    @Query("UPDATE user_profiles SET level = :level, experience = :experience WHERE userId = :userId")
    suspend fun updateLevelAndExp(userId: String, level: Int, experience: Int)

    @Query("UPDATE user_profiles SET totalTrainingSessions = totalTrainingSessions + 1, totalTrainingTime = totalTrainingTime + :duration WHERE userId = :userId")
    suspend fun incrementTrainingStats(userId: String, duration: Long)
}
