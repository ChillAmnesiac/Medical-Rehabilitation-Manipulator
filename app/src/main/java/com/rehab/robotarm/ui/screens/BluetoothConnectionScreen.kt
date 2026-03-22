package com.rehab.robotarm.ui.screens

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.RobotViewModel
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BluetoothConnectionScreen(
    navController: NavController,
    robotViewModel: RobotViewModel
) {
    val context = LocalContext.current
    val robotState by robotViewModel.robotState.collectAsState()
    val scope = rememberCoroutineScope()
    var isScanning by remember { mutableStateOf(false) }
    var availableDevices by remember { mutableStateOf<List<android.bluetooth.BluetoothDevice>>(emptyList()) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var permissionsGranted by remember { mutableStateOf(false) }
    var showManualInput by remember { mutableStateOf(false) }
    var manualMacAddress by remember { mutableStateOf("") }

    // 权限请求
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        permissionsGranted = allGranted
        if (!allGranted) {
            errorMessage = "需要蓝牙权限才能扫描设备"
        }
    }

    // 检查并请求权限
    LaunchedEffect(Unit) {
        val permissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            arrayOf(
                Manifest.permission.BLUETOOTH_SCAN,
                Manifest.permission.BLUETOOTH_CONNECT,
                Manifest.permission.ACCESS_FINE_LOCATION
            )
        } else {
            arrayOf(
                Manifest.permission.BLUETOOTH,
                Manifest.permission.BLUETOOTH_ADMIN,
                Manifest.permission.ACCESS_FINE_LOCATION
            )
        }
        permissionLauncher.launch(permissions)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("蓝牙连接") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            // 连接状态卡片
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = if (robotState.isConnected)
                        MaterialTheme.colorScheme.primaryContainer
                    else
                        MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = if (robotState.isConnected) Icons.Default.Bluetooth else Icons.Default.BluetoothDisabled,
                        contentDescription = null,
                        modifier = Modifier.size(48.dp),
                        tint = if (robotState.isConnected)
                            MaterialTheme.colorScheme.primary
                        else
                            MaterialTheme.colorScheme.error
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Text(
                            text = if (robotState.isConnected) "已连接" else "未连接",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        if (robotState.isConnected) {
                            Text(
                                text = "设备: OpenClaw-NUS",
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                    Spacer(modifier = Modifier.weight(1f))
                    if (robotState.isConnected) {
                        IconButton(
                            onClick = {
                                scope.launch {
                                    robotViewModel.disconnectBluetooth()
                                }
                            }
                        ) {
                            Icon(Icons.Default.Close, contentDescription = "断开连接")
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // 扫描按钮
            if (!robotState.isConnected) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = {
                            if (!permissionsGranted) {
                                errorMessage = "请先授予蓝牙权限"
                                return@Button
                            }
                            scope.launch {
                                isScanning = true
                                errorMessage = null
                                try {
                                    val devices = robotViewModel.scanBluetoothDevices()
                                    availableDevices = devices
                                    if (devices.isEmpty()) {
                                        errorMessage = "未找到设备，请尝试手动输入 MAC 地址"
                                    }
                                } catch (e: Exception) {
                                    errorMessage = "扫描失败: ${e.message}"
                                } finally {
                                    isScanning = false
                                }
                            }
                        },
                        modifier = Modifier.weight(1f),
                        enabled = !isScanning && permissionsGranted
                    ) {
                        if (isScanning) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                        Text(if (isScanning) "扫描中..." else "扫描设备")
                    }

                    OutlinedButton(
                        onClick = { showManualInput = !showManualInput },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("手动输入")
                    }
                }

                // 手动输入 MAC 地址
                if (showManualInput) {
                    Spacer(modifier = Modifier.height(8.dp))
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
                                text = "手动输入 MAC 地址",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            OutlinedTextField(
                                value = manualMacAddress,
                                onValueChange = { manualMacAddress = it.uppercase() },
                                label = { Text("MAC 地址") },
                                placeholder = { Text("例如: 00:11:22:33:44:55") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Button(
                                onClick = {
                                    if (manualMacAddress.matches(Regex("^([0-9A-F]{2}:){5}[0-9A-F]{2}$"))) {
                                        scope.launch {
                                            errorMessage = null
                                            try {
                                                val success = robotViewModel.connectBluetooth(manualMacAddress)
                                                if (success) {
                                                    navController.popBackStack()
                                                } else {
                                                    errorMessage = "连接失败，请检查 MAC 地址是否正确"
                                                }
                                            } catch (e: Exception) {
                                                errorMessage = "连接失败: ${e.message}"
                                            }
                                        }
                                    } else {
                                        errorMessage = "MAC 地址格式不正确，应为: 00:11:22:33:44:55"
                                    }
                                },
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Text("连接")
                            }
                        }
                    }
                }
            }

            // 错误信息
            errorMessage?.let { error ->
                Spacer(modifier = Modifier.height(8.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Text(
                        text = error,
                        modifier = Modifier.padding(16.dp),
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // 设备列表
            if (availableDevices.isNotEmpty()) {
                Text(
                    text = "可用设备",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))

                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(availableDevices) { device ->
                        Card(
                            onClick = {
                                scope.launch {
                                    errorMessage = null
                                    try {
                                        val success = robotViewModel.connectBluetooth(device.address)
                                        if (success) {
                                            navController.popBackStack()
                                        } else {
                                            errorMessage = "连接失败，请重试"
                                        }
                                    } catch (e: Exception) {
                                        errorMessage = "连接失败: ${e.message}"
                                    }
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(16.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Bluetooth,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.primary
                                )
                                Spacer(modifier = Modifier.width(16.dp))
                                Column {
                                    Text(
                                        text = device.name ?: "未知设备",
                                        style = MaterialTheme.typography.titleMedium,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Text(
                                        text = device.address,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        }
                    }
                }
            }

            // 使用说明
            if (!robotState.isConnected && availableDevices.isEmpty()) {
                Spacer(modifier = Modifier.height(24.dp))
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
                            text = "连接说明",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "1. 确保 M33 设备已开启蓝牙\n" +
                                    "2. 点击\"扫描设备\"按钮扫描附近的蓝牙设备\n" +
                                    "3. 或点击\"手动输入\"直接输入设备 MAC 地址\n" +
                                    "4. 设备名称: OpenClaw-NUS\n" +
                                    "5. 连接成功后会自动启动数据流",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
        }
    }
}

