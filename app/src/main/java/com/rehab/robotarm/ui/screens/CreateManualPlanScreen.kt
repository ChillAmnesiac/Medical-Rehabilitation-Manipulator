package com.rehab.robotarm.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.rehab.robotarm.viewmodel.TrainingPlanViewModel

/**
 * 手动创建训练计划界面
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateManualPlanScreen(
    navController: NavController,
    patientId: String
) {
    var planName by remember { mutableStateOf("") }
    var planDescription by remember { mutableStateOf("") }
    var totalWeeks by remember { mutableStateOf(4) }
    var goals by remember { mutableStateOf("") }
    var currentStep by remember { mutableStateOf(0) } // 0: 基本信息, 1: 周计划
    var weekPlans by remember { mutableStateOf<List<WeekPlanInput>>(emptyList()) }
    var showSuccessDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("手动创建训练计划") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, "返回")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // 步骤指示器
            LinearProgressIndicator(
                progress = { (currentStep + 1) / 2f },
                modifier = Modifier.fillMaxWidth()
            )

            if (currentStep == 0) {
                // 第一步：基本信息
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        Text(
                            "第1步：填写基本信息",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    item {
                        OutlinedTextField(
                            value = planName,
                            onValueChange = { planName = it },
                            label = { Text("计划名称") },
                            placeholder = { Text("例如：肩关节康复4周计划") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true
                        )
                    }

                    item {
                        OutlinedTextField(
                            value = planDescription,
                            onValueChange = { planDescription = it },
                            label = { Text("计划描述") },
                            placeholder = { Text("简要描述训练计划的目标和内容") },
                            modifier = Modifier.fillMaxWidth(),
                            minLines = 3
                        )
                    }

                    item {
                        Text(
                            "训练周期：${totalWeeks}周",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Slider(
                            value = totalWeeks.toFloat(),
                            onValueChange = { totalWeeks = it.toInt() },
                            valueRange = 1f..12f,
                            steps = 10,
                            modifier = Modifier.fillMaxWidth()
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("1周", style = MaterialTheme.typography.bodySmall)
                            Text("6周", style = MaterialTheme.typography.bodySmall)
                            Text("12周", style = MaterialTheme.typography.bodySmall)
                        }
                    }

                    item {
                        OutlinedTextField(
                            value = goals,
                            onValueChange = { goals = it },
                            label = { Text("训练目标") },
                            placeholder = { Text("每行一个目标，例如：\n提高肩关节活动度\n增强肌肉力量") },
                            modifier = Modifier.fillMaxWidth(),
                            minLines = 4
                        )
                    }

                    item {
                        Card(
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.secondaryContainer
                            )
                        ) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(16.dp)
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        Icons.Default.Info,
                                        contentDescription = null,
                                        tint = MaterialTheme.colorScheme.secondary
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        "提示",
                                        style = MaterialTheme.typography.titleMedium,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    "下一步将为每周设置具体的训练内容，包括训练频率、时长和动作。",
                                    style = MaterialTheme.typography.bodyMedium
                                )
                            }
                        }
                    }
                }

                // 底部按钮
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = { navController.navigateUp() },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("取消")
                    }

                    Button(
                        onClick = {
                            // 初始化周计划
                            weekPlans = List(totalWeeks) { weekNum ->
                                WeekPlanInput(
                                    weekNumber = weekNum + 1,
                                    frequency = 3,
                                    duration = 30,
                                    exercises = ""
                                )
                            }
                            currentStep = 1
                        },
                        modifier = Modifier.weight(1f),
                        enabled = planName.isNotBlank() && planDescription.isNotBlank() && goals.isNotBlank()
                    ) {
                        Text("下一步")
                        Spacer(modifier = Modifier.width(4.dp))
                        Icon(Icons.Default.ArrowForward, contentDescription = null)
                    }
                }
            } else {
                // 第二步：周计划
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        Text(
                            "第2步：设置周计划",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    itemsIndexed(weekPlans) { index, weekPlan ->
                        WeekPlanInputCard(
                            weekPlan = weekPlan,
                            onUpdate = { updated ->
                                weekPlans = weekPlans.toMutableList().apply {
                                    set(index, updated)
                                }
                            }
                        )
                    }
                }

                // 底部按钮
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = { currentStep = 0 },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.ArrowBack, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("上一步")
                    }

                    Button(
                        onClick = {
                            // 保存计划（简化版，直接显示成功）
                            showSuccessDialog = true
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.Save, contentDescription = null)
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("保存计划")
                    }
                }
            }

            // 成功对话框
            if (showSuccessDialog) {
                AlertDialog(
                    onDismissRequest = { },
                    title = { Text("保存成功") },
                    text = { Text("训练计划已保存！") },
                    confirmButton = {
                        TextButton(onClick = {
                            showSuccessDialog = false
                            navController.navigateUp()
                        }) {
                            Text("确定")
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun WeekPlanInputCard(
    weekPlan: WeekPlanInput,
    onUpdate: (WeekPlanInput) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    "第${weekPlan.weekNumber}周",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                IconButton(onClick = { expanded = !expanded }) {
                    Icon(
                        if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                        contentDescription = if (expanded) "收起" else "展开"
                    )
                }
            }

            if (expanded) {
                Spacer(modifier = Modifier.height(12.dp))

                Text("每周训练次数：${weekPlan.frequency}次")
                Slider(
                    value = weekPlan.frequency.toFloat(),
                    onValueChange = { onUpdate(weekPlan.copy(frequency = it.toInt())) },
                    valueRange = 1f..7f,
                    steps = 5
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text("每次训练时长：${weekPlan.duration}分钟")
                Slider(
                    value = weekPlan.duration.toFloat(),
                    onValueChange = { onUpdate(weekPlan.copy(duration = it.toInt())) },
                    valueRange = 10f..60f,
                    steps = 9
                )

                Spacer(modifier = Modifier.height(8.dp))

                OutlinedTextField(
                    value = weekPlan.exercises,
                    onValueChange = { onUpdate(weekPlan.copy(exercises = it)) },
                    label = { Text("训练动作") },
                    placeholder = { Text("每行一个动作，例如：\n肩关节前屈 0-60° x10次\n肩关节外展 0-45° x10次") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 3
                )
            } else {
                Text(
                    "${weekPlan.frequency}次/周 · ${weekPlan.duration}分钟/次",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

data class WeekPlanInput(
    val weekNumber: Int,
    val frequency: Int,
    val duration: Int,
    val exercises: String
)
