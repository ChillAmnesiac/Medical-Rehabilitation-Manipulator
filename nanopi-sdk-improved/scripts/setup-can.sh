#!/bin/bash
# Configure a NanoPi CAN interface.
#
# Defaults:
# - Prefer an already-present USB-CAN SLCAN service interface can_usb0.
# - Fall back to SPI MCP2518FD can0.
# - Do not auto-start unverified CH340/SLCAN adapters unless
#   ALLOW_UNVERIFIED_SLCAN=1 is set.

set -e

BITRATE="${1:-${CAN_BITRATE:-1000000}}"
CAN_INTERFACE="${CAN_INTERFACE:-}"

echo "=== NanoPi M5 CAN 接口配置脚本 ==="
echo "波特率: ${BITRATE} bps"

if [ "$EUID" -ne 0 ]; then
    echo "错误: 请使用 sudo 运行此脚本"
    exit 1
fi

if [ -z "$CAN_INTERFACE" ]; then
    if ip link show can_usb0 &> /dev/null; then
        CAN_INTERFACE="can_usb0"
    elif ip link show can0 &> /dev/null; then
        CAN_INTERFACE="can0"
    elif [ "${ALLOW_UNVERIFIED_SLCAN:-0}" = "1" ] && systemctl list-unit-files usbcan-slcan.service &> /dev/null; then
        echo "未发现 CAN 接口，尝试启动 usbcan-slcan.service..."
        systemctl restart usbcan-slcan.service || true
        sleep 1
        if ip link show can_usb0 &> /dev/null; then
            CAN_INTERFACE="can_usb0"
        fi
    elif systemctl list-unit-files usbcan-slcan.service &> /dev/null; then
        echo "检测到 usbcan-slcan.service，但当前 CH340 适配器未验证，默认不自动启动。"
        echo "如需实验性启用: ALLOW_UNVERIFIED_SLCAN=1 sudo -E $0 ${BITRATE}"
    fi
fi

if [ -z "$CAN_INTERFACE" ] || ! ip link show "$CAN_INTERFACE" &> /dev/null; then
    echo "错误: 未找到 CAN 接口"
    echo "排查:"
    echo "  USB-CAN: systemctl status usbcan-slcan.service; lsusb; ls -l /dev/ttyUSB*"
    echo "  SPI-CAN: dmesg | grep -iE 'mcp251|spi|can'"
    exit 1
fi

echo "接口: ${CAN_INTERFACE}"
echo "✓ 找到 ${CAN_INTERFACE} 接口"

ip link set "$CAN_INTERFACE" down 2>/dev/null || true

case "$CAN_INTERFACE" in
    can_usb0)
        # SLCAN adapters are configured by slcand, not by ip link bitrate.
        echo "警告: can_usb0 只表示 slcand 创建了 SocketCAN 接口。"
        echo "      对 CH340 适配器必须先用 diagnose-usbcan.sh 验证真实收发。"
        ip link set "$CAN_INTERFACE" up
        ;;
    *)
        ip link set "$CAN_INTERFACE" type can bitrate "$BITRATE" restart-ms 100 berr-reporting on
        ip link set "$CAN_INTERFACE" up
        ;;
esac

echo ""
echo "=== CAN 接口状态 ==="
ip -details -statistics link show "$CAN_INTERFACE"

echo ""
echo "=== 配置完成 ==="
echo "测试命令: candump ${CAN_INTERFACE}"
