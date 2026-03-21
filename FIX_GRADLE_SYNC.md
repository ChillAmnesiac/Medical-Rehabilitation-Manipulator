# 修复Gradle同步失败问题

## 问题诊断

Android Studio已成功启动，但Gradle同步失败，错误信息：
```
Could not install Gradle distribution from 'https://services.gradle.org/distributions/gradle-8.2-bin.zip'.
Reason: java.net.SocketTimeoutException: Connect timed out
```

这是网络连接问题，无法下载Gradle。

## 解决方案

### 方案1：使用国内镜像（推荐）

1. **修改gradle-wrapper.properties**

在Android Studio中打开：
```
gradle/wrapper/gradle-wrapper.properties
```

将：
```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.2-bin.zip
```

改为（使用腾讯云镜像）：
```properties
distributionUrl=https\://mirrors.cloud.tencent.com/gradle/gradle-8.2-bin.zip
```

或使用阿里云镜像：
```properties
distributionUrl=https\://mirrors.aliyun.com/macports/distfiles/gradle/gradle-8.2-bin.zip
```

2. **点击"Sync Now"重新同步**

### 方案2：手动下载Gradle

1. **下载Gradle 8.2**
   ```bash
   cd /tmp
   wget https://mirrors.cloud.tencent.com/gradle/gradle-8.2-bin.zip
   # 或使用浏览器下载
   ```

2. **放到Gradle缓存目录**
   ```bash
   mkdir -p ~/.gradle/wrapper/dists/gradle-8.2-bin/
   # 将下载的zip文件复制到该目录
   ```

3. **在Android Studio中重新同步**

### 方案3：配置代理（如果有代理）

在 `gradle.properties` 中添加：
```properties
systemProp.http.proxyHost=your-proxy-host
systemProp.http.proxyPort=your-proxy-port
systemProp.https.proxyHost=your-proxy-host
systemProp.https.proxyPort=your-proxy-port
```

### 方案4：使用本地Gradle（最快）

1. **检查是否已安装Gradle**
   ```bash
   gradle --version
   ```

2. **在Android Studio中配置**
   - File → Settings → Build, Execution, Deployment → Gradle
   - 选择 "Use local gradle distribution"
   - 指定Gradle路径（如 `/usr/share/gradle`）

## 快速修复脚本

我已经为你准备了一个快速修复脚本：

```bash
cd /home/wen/RehabRobotArm
./fix_gradle.sh
```

## 修复后的步骤

1. 等待Gradle同步完成（可能需要几分钟）
2. 同步成功后，点击顶部的Run按钮
3. 选择模拟器或创建新模拟器
4. 运行应用

## 如果仍然失败

### 检查网络连接
```bash
ping mirrors.cloud.tencent.com
curl -I https://mirrors.cloud.tencent.com/gradle/gradle-8.2-bin.zip
```

### 清理并重试
```bash
cd /home/wen/RehabRobotArm
./gradlew clean
# 然后在Android Studio中重新同步
```

### 查看详细日志
在Android Studio底部：
- 点击 "Build" 标签查看构建日志
- 点击 "Sync" 标签查看同步详情

## 临时解决方案：使用较低版本的Gradle

如果上述方法都不行，可以降级Gradle版本：

在 `gradle/wrapper/gradle-wrapper.properties` 中改为：
```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.0-bin.zip
```

并在 `build.gradle.kts` 中修改：
```kotlin
plugins {
    id("com.android.application") version "8.0.0" apply false
    // ...
}
```

## 注意事项

- 修改配置文件后，一定要点击 "Sync Now" 或 "Sync Project with Gradle Files"
- 首次同步会下载很多依赖，请耐心等待
- 确保有足够的磁盘空间（建议至少5GB）
