#!/bin/bash
# 配置 CAN 接口

set -e

CAN_INTERFACE="can0"
BITRATE="${1:-1000000}"

echo "=== NanoPi M5 CAN 接口配置脚本 ==="
echo "接口: ${CAN_INTERFACE}"
echo "波特率: ${BITRATE} bps"

if [ "$EUID" -ne 0 ]; then
    echo "错误: 请使用 sudo 运行此脚本"
    exit 1
fi

if ! ip link show ${CAN_INTERFACE} &> /dev/null; then
    echo "错误: 未找到 ${CAN_INTERFACE} 接口"
    echo "请检查设备树是否加载: dmesg | grep -i mcp2518"
    exit 1
fi

echo "✓ 找到 ${CAN_INTERFACE} 接口"

ip link set ${CAN_INTERFACE} down 2>/dev/null || true
ip link set ${CAN_INTERFACE} type can bitrate ${BITRATE}
ip link set ${CAN_INTERFACE} up

echo ""
echo "=== CAN 接口状态 ==="
ip -details link show ${CAN_INTERFACE}

echo ""
echo "=== 配置完成 ==="
echo "测试命令: candump ${CAN_INTERFACE}"
