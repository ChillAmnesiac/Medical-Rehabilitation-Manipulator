#!/bin/bash

echo "=================================="
echo "Gradle同步问题自动修复脚本"
echo "=================================="
echo ""

# 备份原文件
echo "1. 备份原配置文件..."
cp gradle/wrapper/gradle-wrapper.properties gradle/wrapper/gradle-wrapper.properties.bak

# 修改为使用国内镜像
echo "2. 修改Gradle下载源为腾讯云镜像..."
cat > gradle/wrapper/gradle-wrapper.properties << 'EOF'
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://mirrors.cloud.tencent.com/gradle/gradle-8.2-bin.zip
networkTimeout=10000
validateDistributionUrl=true
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

echo "✓ 配置文件已更新"
echo ""

# 添加Maven镜像
echo "3. 配置Maven仓库镜像..."
cat >> gradle.properties << 'EOF'

# Maven镜像配置
systemProp.maven.repo.central=https://maven.aliyun.com/repository/central
systemProp.maven.repo.google=https://maven.aliyun.com/repository/google
systemProp.maven.repo.jcenter=https://maven.aliyun.com/repository/public
EOF

echo "✓ Maven镜像已配置"
echo ""

echo "=================================="
echo "修复完成！"
echo "=================================="
echo ""
echo "下一步操作："
echo "1. 在Android Studio中点击 File → Sync Project with Gradle Files"
echo "2. 或点击顶部的 'Sync Now' 按钮"
echo "3. 等待同步完成（可能需要几分钟）"
echo ""
echo "如果仍然失败，请查看 FIX_GRADLE_SYNC.md 文档"
