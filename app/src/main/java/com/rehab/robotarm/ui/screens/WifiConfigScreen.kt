package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rehab.robotarm.ui.theme.MedicalBlue
import com.rehab.robotarm.ui.theme.MedicalGreen
import com.rehab.robotarm.viewmodel.RobotViewModel
import kotlinx.coroutines.launch

/**
 * WiFi配置界面
 * 用于配置PSoC Edge连接到家庭WiFi网络
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WifiConfigScreen(viewModel: RobotViewModel = viewModel()) {
    var deviceIp by remember { mutableStateOf("192.168.4.1") }
    var wifiSsid by remember { mutableStateOf("") }
    var wifiPassword by remember { mutableStateOf("") }
    var isConfiguring by remember { mutableStateOf(false) }
    var configResult by remember { mutableStateOf<String?>(null) }
    var showInstructions by remember { mutableStateOf(true) }

    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // 标题
        Text(
            text = "WiFi配置",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // 配置说明卡片
        if (showInstructions) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MedicalBlue.copy(alpha = 0.1f)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(bottom = 8.dp)
                    ) {
                        Icon(
                            Icons.Default.Wifi,
                            contentDescription = null,
                            tint = MedicalBlue
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            "配置步骤",
                            style = MaterialTheme.typography.titleMedium,
                            color = MedicalBlue
                        )
                    }

                    Text(
                        "1. 确保PSoC Edge设备已上电\n" +
                        "2. 在手机WiFi设置中连接到 \"RehabArm-Config\"\n" +
                        "3. WiFi密码: 12345678\n" +
                        "4. 返回此界面，输入您的家庭WiFi信息\n" +
                        "5. 点击\"配置WiFi\"按钮",
                        style = MaterialTheme.typography.bodyMedium,
                        modifier = Modifier.padding(vertical = 8.dp)
                    )

                    TextButton(
                        onClick = { showInstructions = false },
                        modifier = Modifier.align(Alignment.End)
                    ) {
                        Text("我知道了")
                    }
                }
            }
        }

        // 设备IP地址
        OutlinedTextField(
            value = deviceIp,
            onValueChange = { deviceIp = it },
            label = { Text("设备IP地址") },
            placeholder = { Text("192.168.4.1") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            singleLine = true
        )

        // WiFi SSID
        OutlinedTextField(
            value = wifiSsid,
            onValueChange = { wifiSsid = it },
            label = { Text("WiFi名称 (SSID)") },
            placeholder = { Text("输入您的WiFi名称") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 12.dp),
            singleLine = true,
            enabled = !isConfiguring
        )

        // WiFi密码
        OutlinedTextField(
            value = wifiPassword,
            onValueChange = { wifiPassword = it },
            label = { Text("WiFi密码") },
            placeholder = { Text("输入WiFi密码") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            singleLine = true,
            enabled = !isConfiguring
        )

        // 配置按钮
        Button(
            onClick = {
                scope.launch {
                    isConfiguring = true
                    configResult = null

                    try {
                        val result = viewModel.configureWifi(deviceIp, wifiSsid, wifiPassword)
                        configResult = if (result) {
                            "配置成功！设备正在连接到WiFi..."
                        } else {
                            "配置失败，请检查设备连接和WiFi信息"
                        }
                    } catch (e: Exception) {
                        configResult = "配置出错: ${e.message}"
                    } finally {
                        isConfiguring = false
                    }
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            enabled = !isConfiguring && wifiSsid.isNotBlank() && wifiPassword.isNotBlank(),
            colors = ButtonDefaults.buttonColors(
                containerColor = MedicalBlue
            )
        ) {
            if (isConfiguring) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("配置中...")
            } else {
                Text("配置WiFi")
            }
        }

        // 配置结果
        configResult?.let { result ->
            Spacer(modifier = Modifier.height(16.dp))
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (result.contains("成功")) {
                        MedicalGreen.copy(alpha = 0.2f)
                    } else {
                        MaterialTheme.colorScheme.errorContainer
                    }
                )
            ) {
                Text(
                    text = result,
                    modifier = Modifier.padding(16.dp),
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // 帮助信息
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    "故障排查",
                    style = MaterialTheme.typography.titleSmall,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
                Text(
                    "• 确保手机已连接到 RehabArm-Config 网络\n" +
                    "• 设备IP通常为 192.168.4.1\n" +
                    "• 确保输入的WiFi信息正确\n" +
                    "• 配置成功后，设备会自动重启并连接到您的WiFi",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
