package com.rehab.robotarm.data.repository

import com.rehab.robotarm.data.database.dao.*
import com.rehab.robotarm.data.database.entity.*
import kotlinx.coroutines.flow.Flow
import java.security.MessageDigest

class UserRepository(
    private val userDao: UserDao,
    private val userProfileDao: UserProfileDao
) {
    suspend fun login(username: String, password: String): User? {
        val hashedPassword = hashPassword(password)
        return userDao.login(username, hashedPassword)
    }

    suspend fun register(user: User) {
        val hashedUser = user.copy(password = hashPassword(user.password))
        userDao.register(hashedUser)
    }

    suspend fun findByEmail(email: String): User? {
        return userDao.findByEmail(email)
    }

    suspend fun getUserById(userId: String): User? {
        return userDao.getUserById(userId)
    }

    suspend fun updateLastLogin(userId: String, timestamp: Long) {
        userDao.updateLastLogin(userId, timestamp)
    }

    suspend fun getProfile(userId: String): UserProfile? {
        return userProfileDao.getProfile(userId)
    }

    fun getProfileFlow(userId: String): Flow<UserProfile?> {
        return userProfileDao.getProfileFlow(userId)
    }

    suspend fun createProfile(profile: UserProfile) {
        userProfileDao.createProfile(profile)
    }

    suspend fun updateProfile(profile: UserProfile) {
        userProfileDao.updateProfile(profile)
    }

    suspend fun incrementTrainingStats(userId: String, duration: Long) {
        userProfileDao.incrementTrainingStats(userId, duration)
    }

    // 获取当前用户（需要配合AuthViewModel使用）
    suspend fun getCurrentUser(): User? {
        // 这里应该从SharedPreferences或其他地方获取当前登录用户ID
        // 暂时返回null，实际使用时需要配合AuthViewModel
        return null
    }

    private fun hashPassword(password: String): String {
        val md = MessageDigest.getInstance("SHA-256")
        val hash = md.digest(password.toByteArray())
        return hash.joinToString("") { "%02x".format(it) }
    }
}
