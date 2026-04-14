#!/bin/bash
# 安装设备树覆盖到系统

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/../output"
DTBO_FILE="rk3588-spi4-mcp2518fd.dtbo"

echo "=== NanoPi M5 SPI4 MCP2518FD 设备树安装脚本 ==="

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "错误: 请使用 sudo 运行此脚本"
    exit 1
fi

# 检查 dtbo 文件是否存在
if [ ! -f "${OUTPUT_DIR}/${DTBO_FILE}" ]; then
    echo "错误: 未找到 ${DTBO_FILE}"
    echo "请先运行 ./compile-overlay.sh 编译设备树"
    exit 1
fi

# 方法1: 尝试复制到 /boot/overlays
if [ -d /boot/overlays ]; then
    echo "方法1: 安装到 /boot/overlays/"
    cp "${OUTPUT_DIR}/${DTBO_FILE}" /boot/overlays/
    echo "✓ 已复制到 /boot/overlays/${DTBO_FILE}"
fi

# 方法2: 复制到 /lib/firmware
echo ""
echo "方法2: 安装到 /lib/firmware/"
mkdir -p /lib/firmware
cp "${OUTPUT_DIR}/${DTBO_FILE}" /lib/firmware/
echo "✓ 已复制到 /lib/firmware/${DTBO_FILE}"

# 方法3: FriendlyElec 特定配置
if [ -d /boot/dtb/rockchip/overlay ]; then
    echo ""
    echo "方法3: 安装到 FriendlyElec overlay 目录"
    cp "${OUTPUT_DIR}/${DTBO_FILE}" /boot/dtb/rockchip/overlay/
    echo "✓ 已复制到 /boot/dtb/rockchip/overlay/${DTBO_FILE}"
fi

echo ""
echo "=== 安装完成，请重启系统 ==="
