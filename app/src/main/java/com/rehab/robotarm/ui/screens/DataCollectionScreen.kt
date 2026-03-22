package com.rehab.robotarm.ui.screens

import android.content.Intent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.FileProvider
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.RobotViewModel
import kotlinx.coroutines.launch
import java.io.File

/**
 * 数据采集界面
 * 用于采集传感器数据并导出为JSON
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DataCollectionScreen(
    navController: NavController,
    viewModel: RobotViewModel
) {
    val robotState by viewModel.robotState.collectAsState()
    val isCollecting by viewModel.isCollectingData.collectAsState()
    val recordCount by viewModel.collectionRecordCount.collectAsState()
    val collectionRate by viewModel.collectionRate.collectAsState()

    var showRateDialog by remember { mutableStateOf(false) }
    var rateInput by remember { mutableStateOf(collectionRate.toString()) }

    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var showExportDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("传感器数据采集") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
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
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 连接状态卡片
            Card(
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
                        modifier = Modifier.size(32.dp)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = if (robotState.isConnected) "设备已连接" else "设备未连接",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = if (robotState.isConnected) "可以开始采集数据" else "请先连接设备",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }

            // 采集状态卡片
            Card {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "采集状态",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("状态:")
                        Text(
                            text = if (isCollecting) "采集中" else "已停止",
                            color = if (isCollecting) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("已采集记录:")
                        Text(
                            text = "$recordCount 条",
                            fontWeight = FontWeight.Bold
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("采集速率:")
                        TextButton(onClick = { showRateDialog = true }) {
                            Text("${collectionRate}ms / 条")
                            Icon(Icons.Default.Edit, contentDescription = null, modifier = Modifier.size(16.dp))
                        }
                    }

                    if (isCollecting) {
                        Spacer(modifier = Modifier.height(8.dp))
                        LinearProgressIndicator(
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }
            }

            // 控制按钮
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(
                    onClick = { viewModel.startDataCollection() },
                    modifier = Modifier.weight(1f),
                    enabled = robotState.isConnected && !isCollecting
                ) {
                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("开始采集")
                }

                Button(
                    onClick = { viewModel.stopDataCollection() },
                    modifier = Modifier.weight(1f),
                    enabled = isCollecting,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Icon(Icons.Default.Stop, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("停止采集")
                }
            }

            // 导出按钮
            Button(
                onClick = { showExportDialog = true },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isCollecting && recordCount > 0
            ) {
                Icon(Icons.Default.Download, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("导出数据为JSON")
            }

            // 当前传感器数据预览
            Card {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                ) {
                    Text(
                        text = "实时数据预览",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))

                    SensorDataRow("肩关节角度", "${robotState.sensorData.shoulderAngle.toInt()}°")
                    SensorDataRow("肘关节角度", "${robotState.sensorData.elbowAngle.toInt()}°")
                    SensorDataRow("推杆位置", "${robotState.sensorData.lateralPosition.toInt()}%")
                    SensorDataRow("EMG通道1", String.format("%.1f μV", robotState.sensorData.emgCh1))
                    SensorDataRow("EMG通道2", String.format("%.1f μV", robotState.sensorData.emgCh2))
                }
            }
        }
    }

    // 采集速率设置对话框
    if (showRateDialog) {
        AlertDialog(
            onDismissRequest = { showRateDialog = false },
            title = { Text("设置采集速率") },
            text = {
                Column {
                    Text("输入采集间隔（毫秒），范围: 10-10000")
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = rateInput,
                        onValueChange = { rateInput = it },
                        label = { Text("间隔 (ms)") },
                        singleLine = true
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        val rate = rateInput.toLongOrNull()
                        if (rate != null && rate in 10..10000) {
                            viewModel.setCollectionRate(rate)
                            showRateDialog = false
                        }
                    }
                ) {
                    Text("确定")
                }
            },
            dismissButton = {
                TextButton(onClick = { showRateDialog = false }) {
                    Text("取消")
                }
            }
        )
    }

    // 导出确认对话框
    if (showExportDialog) {
        AlertDialog(
            onDismissRequest = { showExportDialog = false },
            title = { Text("导出数据") },
            text = { Text("确定要导出 $recordCount 条记录为JSON文件吗？") },
            confirmButton = {
                TextButton(
                    onClick = {
                        scope.launch {
                            try {
                                val json = viewModel.exportCollectedData()
                                val file = File(context.cacheDir, "sensor_data_${System.currentTimeMillis()}.json")
                                file.writeText(json)

                                val uri = FileProvider.getUriForFile(
                                    context,
                                    "${context.packageName}.fileprovider",
                                    file
                                )

                                val shareIntent = Intent(Intent.ACTION_SEND).apply {
                                    type = "application/json"
                                    putExtra(Intent.EXTRA_STREAM, uri)
                                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                                }
                                context.startActivity(Intent.createChooser(shareIntent, "导出数据"))

                                showExportDialog = false
                            } catch (e: Exception) {
                                android.util.Log.e("DataCollection", "Export failed", e)
                            }
                        }
                    }
                ) {
                    Text("导出")
                }
            },
            dismissButton = {
                TextButton(onClick = { showExportDialog = false }) {
                    Text("取消")
                }
            }
        )
    }
}
