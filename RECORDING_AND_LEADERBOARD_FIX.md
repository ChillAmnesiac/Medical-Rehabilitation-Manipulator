# 录制功能和排行榜修复说明

## 修复日期
2026-03-14

## 问题描述

1. **标准主动模式缺少录制功能**：用户无法在标准训练模式下录制动作并保存到记忆模式
2. **排行榜加载不出来**：排行榜界面一直显示加载中，无法显示数据

## 解决方案

### 1. 标准训练模式添加录制功能

#### 修改文件：`StandardTrainingScreen.kt`

**新增功能：**
- 在顶部工具栏添加录制按钮（仅在训练中显示）
- 录制状态指示器（红色圆点显示"正在录制"）
- 保存动作对话框，允许用户输入动作名称和描述
- 集成 RobotViewModel 的录制功能

**使用流程：**
1. 点击"开始训练"按钮开始训练
2. 点击顶部工具栏的录制按钮（圆点图标）开始录制
3. 再次点击录制按钮停止录制
4. 在弹出的对话框中输入动作名称和描述
5. 点击"保存"将动作保存到记忆模式
6. 保存的动作可在"记忆模式 > 动作回放"中查看和播放

**技术实现：**
- 使用 `viewModel.startRecording()` 开始录制
- 使用 `viewModel.stopRecording()` 停止录制
- 使用 `viewModel.saveRecording(name, description)` 保存录制的动作
- 录制的数据会自动转换为关键帧格式存储

### 2. 排行榜加载问题修复

#### 修改文件：`LeaderboardViewModel.kt`

**问题原因：**
- 使用 `collect` 收集 Flow 数据时，协程会一直挂起等待新数据
- `finally` 块中的 `_isLoading.value = false` 永远不会执行
- 数据库初始为空，导致没有数据显示

**解决方案：**
1. **修复协程挂起问题**：将 `collect` 放在独立的子协程中，不阻塞主协程
2. **添加演示数据**：当数据库为空时，自动初始化5个演示用户数据
3. **添加默认用户排名**：当没有登录用户时，显示一个演示排名

**新增功能：**
- `initializeDemoData()` 方法：自动创建演示排行榜数据
- 演示用户包括：康复达人、训练之星、坚持不懈、努力向上、康复新星
- 默认显示"我"的排名为第12名（演示数据）

**技术细节：**
```kotlin
// 启动独立协程收集数据流
launch {
    leaderboardRepository.getLeaderboard(category, 100).collect { entries ->
        _leaderboard.value = entries
        if (entries.isEmpty()) {
            initializeDemoData(category)
        }
    }
}

// 主协程继续执行，不会被阻塞
_isLoading.value = false
```

## 测试建议

### 录制功能测试
1. 进入"主动模式 > 标准训练"
2. 点击"开始训练"
3. 点击顶部录制按钮，进行一些手臂动作
4. 再次点击录制按钮停止
5. 输入动作名称（如"测试动作1"）和描述
6. 点击保存
7. 进入"记忆模式 > 动作回放"查看是否有保存的动作
8. 点击动作进行回放测试

### 排行榜测试
1. 进入排行榜界面
2. 检查是否显示5个演示用户
3. 检查"我的排名"卡片是否显示
4. 切换不同标签（全球、本周、本月、好友）
5. 确认每个标签都能正常加载数据

## 注意事项

1. **录制数据存储**：录制的动作存储在内存中（RobotRepository），应用重启后会丢失。如需持久化，需要添加数据库存储。

2. **排行榜数据**：当前使用演示数据，实际部署时需要：
   - 连接真实的用户系统
   - 实现云端排行榜同步
   - 添加真实的用户认证

3. **录制质量**：录制的关键帧数量取决于传感器数据更新频率，建议：
   - 录制时长控制在5-30秒
   - 确保设备已连接并正常发送传感器数据
   - 录制前先测试设备连接状态

## 相关文件

- `app/src/main/java/com/rehab/robotarm/ui/screens/StandardTrainingScreen.kt`
- `app/src/main/java/com/rehab/robotarm/viewmodel/LeaderboardViewModel.kt`
- `app/src/main/java/com/rehab/robotarm/viewmodel/RobotViewModel.kt`
- `app/src/main/java/com/rehab/robotarm/ui/screens/ActionReplayScreen.kt`
