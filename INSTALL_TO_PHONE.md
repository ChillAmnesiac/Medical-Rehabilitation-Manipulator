# 安装应用到真实手机

## 方法1：USB连接 + ADB安装（推荐）

### 步骤：

1. **在手机上启用开发者选项**
   - 进入"设置" → "关于手机"
   - 连续点击"版本号"7次
   - 返回设置，找到"开发者选项"

2. **启用USB调试**
   - 进入"开发者选项"
   - 打开"USB调试"开关

3. **USB连接手机到电脑**
   - 使用USB数据线连接
   - 手机上会弹出"允许USB调试"提示，点击"允许"

4. **检查连接**
   ```bash
   adb devices
   ```
   应该显示你的手机设备

5. **安装应用**
   ```bash
   cd /home/wen/RehabRobotArm
   adb install -r app/build/outputs/apk/debug/app-debug.apk
   ```

6. **启动应用**
   - 在手机上找到"康复机械臂"图标
   - 点击打开

## 方法2：复制APK文件到手机

### 步骤：

1. **找到APK文件**
   ```bash
   # APK位置
   /home/wen/RehabRobotArm/app/build/outputs/apk/debug/app-debug.apk
   ```

2. **通过USB传输**
   ```bash
   # 推送到手机下载目录
   adb push app/build/outputs/apk/debug/app-debug.apk /sdcard/Download/
   ```

3. **在手机上安装**
   - 打开"文件管理器"
   - 进入"Download"文件夹
   - 点击"app-debug.apk"
   - 点击"安装"
   - 如果提示"不允许安装未知来源"，需要在设置中允许

## 方法3：通过网络传输

### 使用Python HTTP服务器：

1. **启动HTTP服务器**
   ```bash
   cd /home/wen/RehabRobotArm/app/build/outputs/apk/debug/
   python3 -m http.server 8000
   ```

2. **查看电脑IP地址**
   ```bash
   ip addr show | grep "inet " | grep -v 127.0.0.1
   ```

3. **在手机浏览器中下载**
   - 确保手机和电脑在同一WiFi网络
   - 在手机浏览器输入：`http://电脑IP:8000/app-debug.apk`
   - 下载后点击安装

## 方法4：通过云盘或聊天工具

1. **上传APK到云盘**
   - 将APK上传到百度云盘、微云等
   - 在手机上下载

2. **通过微信/QQ发送**
   - 将APK发送到"文件传输助手"
   - 在手机上接收并安装

## 测试蓝牙功能

安装到真实手机后，可以测试完整的蓝牙功能：

### 使用Python模拟器：

1. **在电脑上运行模拟器**
   ```bash
   cd /home/wen/RehabRobotArm
   python3 device_simulator.py
   ```

2. **在手机上连接**
   - 打开手机蓝牙
   - 搜索"RehabRobotArm"设备
   - 配对连接
   - 打开应用，会自动连接

3. **查看实时数据**
   - 应用会显示"已连接"
   - 传感器数据会实时更新
   - 可以控制机械臂运动

## 注意事项

1. **权限授予**
   - 首次运行会请求蓝牙、位置、网络权限
   - 请全部允许

2. **安装未知来源**
   - 如果无法安装，需要在设置中允许"安装未知应用"
   - 路径：设置 → 安全 → 未知来源

3. **APK大小**
   - 文件大小约33MB
   - 确保手机有足够存储空间

4. **系统要求**
   - Android 8.0 (API 26) 或更高版本
   - 建议Android 10+以获得最佳体验

## 快速命令

```bash
# 检查手机连接
adb devices

# 安装到手机
adb install -r app/build/outputs/apk/debug/app-debug.apk

# 推送到手机
adb push app/build/outputs/apk/debug/app-debug.apk /sdcard/Download/

# 启动应用
adb shell am start -n com.rehab.robotarm/.MainActivity

# 查看日志
adb logcat | grep rehab.robotarm
```
