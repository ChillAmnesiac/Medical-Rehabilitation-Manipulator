# 使用指南

## 当前状态

✅ Android Studio 已启动并正在打开项目
✅ 项目文件已全部创建完成

## 接下来的步骤

### 1. 等待Android Studio加载完成

Android Studio正在后台加载项目，请等待：
- Gradle同步完成
- 索引构建完成
- 依赖下载完成

这可能需要几分钟时间（首次打开会下载依赖）。

### 2. 配置Android模拟器

在Android Studio中：

**方法A：使用现有模拟器**
1. 点击顶部工具栏的设备选择器
2. 选择一个已有的模拟器
3. 点击运行按钮（绿色三角形）

**方法B：创建新模拟器**
1. Tools → Device Manager
2. 点击 "Create Device"
3. 选择设备类型（推荐：Pixel 6）
4. 选择系统镜像（推荐：API 34, Android 14）
5. 点击 Finish
6. 启动模拟器

### 3. 运行应用

1. 确保模拟器已启动
2. 点击 Run 按钮（或按 Shift+F10）
3. 应用会自动安装到模拟器

### 4. 测试功能

#### 无需真实设备的测试

应用内置了模拟数据，即使不连接真实设备也能看到：
- 机械臂3D动画（使用默认角度）
- 传感器数据显示（模拟数据）
- 康复分析图表（模拟评分）
- 模式切换功能

#### 使用Python模拟器测试蓝牙通信

如果想测试完整的蓝牙通信功能：

1. **在Linux主机上运行模拟器**：
   ```bash
   cd /home/wen/RehabRobotArm
   python3 device_simulator.py
   ```

2. **在Android模拟器中**：
   - 注意：Android模拟器默认不支持蓝牙
   - 需要使用真实Android设备进行蓝牙测试

3. **使用真实Android设备**：
   - 通过USB连接手机到电脑
   - 在手机上启用"开发者选项"和"USB调试"
   - Android Studio会自动识别设备
   - 运行应用到真实设备
   - 在手机蓝牙设置中搜索"RehabRobotArm"
   - 配对后打开应用即可自动连接

## 界面功能说明

### 界面1：机械臂控制
- 显示机械臂3D动画
- 关节颜色表示温度（蓝→绿→橙→红）
- 被动模式下可用滑块控制

### 界面2：传感器数据
- 实时显示所有传感器数值
- 角度、力、加速度、温度

### 界面3：康复分析
- 综合评分
- 运动平滑度、范围、力量
- 趋势图表
- AI建议

### 界面4：模式控制
- 切换三种模式
- 管理记忆动作

## 常见问题

### Q: Gradle同步失败
**A**: 
```bash
cd /home/wen/RehabRobotArm
./gradlew clean
./gradlew build
```

### Q: 依赖下载慢
**A**: 在 `gradle.properties` 中配置代理或使用国内镜像

### Q: 模拟器启动失败
**A**: 
- 检查是否安装了KVM
- 确保有足够的内存（建议4GB+）
- 尝试使用x86_64镜像

### Q: 应用闪退
**A**: 
- 检查Logcat日志
- 确认权限已授予
- 查看是否有编译错误

## 开发建议

### 修改代码后
1. 保存文件（Ctrl+S）
2. 点击 Run 按钮重新运行
3. 或使用 Apply Changes（闪电图标）快速更新

### 查看日志
1. 打开 Logcat 窗口（底部）
2. 过滤包名：com.rehab.robotarm
3. 查看运行时日志

### 调试
1. 在代码行号左侧点击设置断点
2. 点击 Debug 按钮（虫子图标）
3. 应用会在断点处暂停

## 项目文档

- **README.md** - 完整项目说明
- **QUICKSTART.md** - 快速开始指南  
- **ARCHITECTURE.md** - 架构设计文档
- **PROTOCOL.md** - 通信协议规范
- **FILE_LIST.md** - 文件清单

## 下一步开发

1. **配置云端API**：编辑 `CloudAIService.kt` 添加真实API密钥
2. **添加AI模型**：将 `.tflite` 文件放入 `assets/models/`
3. **自定义UI**：修改 `ui/screens/` 下的界面文件
4. **扩展功能**：参考 ARCHITECTURE.md 添加新功能

## 获取帮助

- 查看代码注释
- 阅读项目文档
- 检查Logcat日志
- 使用Android Studio的代码提示

祝开发顺利！🚀
