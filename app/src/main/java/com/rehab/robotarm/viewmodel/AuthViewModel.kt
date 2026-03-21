package com.rehab.robotarm.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rehab.robotarm.data.database.entity.User
import com.rehab.robotarm.data.database.entity.UserProfile
import com.rehab.robotarm.data.repository.UserRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.util.UUID

class AuthViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState: StateFlow<LoginState> = _loginState

    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser

    // 登录
    fun login(username: String, password: String) {
        viewModelScope.launch {
            _loginState.value = LoginState.Loading

            try {
                val user = userRepository.login(username, password)

                if (user != null && user.isActive) {
                    userRepository.updateLastLogin(user.id, System.currentTimeMillis())
                    _currentUser.value = user
                    _loginState.value = LoginState.Success(user)
                } else {
                    _loginState.value = LoginState.Error("用户名或密码错误")
                }
            } catch (e: Exception) {
                _loginState.value = LoginState.Error(e.message ?: "登录失败")
            }
        }
    }

    // 注册
    fun register(
        username: String,
        password: String,
        email: String,
        role: String
    ) {
        viewModelScope.launch {
            _loginState.value = LoginState.Loading

            try {
                val existing = userRepository.findByEmail(email)
                if (existing != null) {
                    _loginState.value = LoginState.Error("邮箱已被注册")
                    return@launch
                }

                val user = User(
                    id = UUID.randomUUID().toString(),
                    username = username,
                    password = password,
                    email = email,
                    role = role
                )

                userRepository.register(user)

                val profile = UserProfile(
                    userId = user.id,
                    displayName = username,
                    age = 0,
                    gender = ""
                )
                userRepository.createProfile(profile)

                _currentUser.value = user
                _loginState.value = LoginState.Success(user)
            } catch (e: Exception) {
                _loginState.value = LoginState.Error(e.message ?: "注册失败")
            }
        }
    }

    // 指纹登录
    fun loginWithBiometric(onSuccess: () -> Unit, onError: (String) -> Unit) {
        // 生物识别认证成功后调用
        viewModelScope.launch {
            try {
                // 从本地存储获取上次登录的用户
                // TODO: 实现本地存储逻辑
                onSuccess()
            } catch (e: Exception) {
                onError(e.message ?: "指纹登录失败")
            }
        }
    }

    // 微信登录
    fun loginWithWechat() {
        // TODO: 实现微信登录
        _loginState.value = LoginState.Error("微信登录功能开发中")
    }

    // QQ登录
    fun loginWithQQ() {
        // TODO: 实现QQ登录
        _loginState.value = LoginState.Error("QQ登录功能开发中")
    }

    // 登出
    fun logout() {
        _currentUser.value = null
        _loginState.value = LoginState.Idle
    }

    fun resetLoginState() {
        _loginState.value = LoginState.Idle
    }
}

sealed class LoginState {
    object Idle : LoginState()
    object Loading : LoginState()
    data class Success(val user: User) : LoginState()
    data class Error(val message: String) : LoginState()
}
