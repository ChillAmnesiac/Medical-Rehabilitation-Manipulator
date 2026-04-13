#!/bin/bash
# 动态加载 SPI4 设备树覆盖脚本

echo "尝试通过 configfs 加载设备树覆盖..."

# 检查 configfs 是否支持设备树覆盖
if [ ! -d /sys/kernel/config/device-tree ]; then
    echo "错误: 系统不支持通过 configfs 加载设备树覆盖"
    echo ""
    echo "替代方案:"
    echo "1. 将 spi4-mcp2518fd.dtbo 复制到 /lib/firmware/"
    echo "2. 重新编译内核设备树并重启"
    echo "3. 使用 FriendlyElec 提供的工具"
    exit 1
fi

# 创建覆盖目录
sudo mkdir -p /sys/kernel/config/device-tree/overlays/spi4-mcp2518fd

# 加载覆盖
sudo sh -c "cat spi4-mcp2518fd.dtbo > /sys/kernel/config/device-tree/overlays/spi4-mcp2518fd/dtbo"

echo "设备树覆盖已加载"
