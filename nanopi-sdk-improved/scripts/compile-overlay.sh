#!/bin/bash
# 编译设备树覆盖文件

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OVERLAY_DIR="${SCRIPT_DIR}/../overlays"
OUTPUT_DIR="${SCRIPT_DIR}/../output"

echo "=== NanoPi M5 SPI4 MCP2518FD 设备树编译脚本 ==="

# 检查 dtc 是否安装
if ! command -v dtc &> /dev/null; then
    echo "错误: 未找到 dtc 工具"
    echo "请安装: sudo apt-get install device-tree-compiler"
    exit 1
fi

# 创建输出目录
mkdir -p "${OUTPUT_DIR}"

# 编译设备树覆盖
echo "正在编译设备树覆盖..."
dtc -@ -I dts -O dtb -o "${OUTPUT_DIR}/rk3588-spi4-mcp2518fd.dtbo" \
    "${OVERLAY_DIR}/rk3588-spi4-mcp2518fd.dts"

if [ $? -eq 0 ]; then
    echo "✓ 编译成功: ${OUTPUT_DIR}/rk3588-spi4-mcp2518fd.dtbo"
    ls -lh "${OUTPUT_DIR}/rk3588-spi4-mcp2518fd.dtbo"
else
    echo "✗ 编译失败"
    exit 1
fi

echo ""
echo "下一步:"
echo "1. 运行 sudo ./install-overlay.sh 安装设备树覆盖"
echo "2. 重启系统"
echo "3. 运行 ./setup-can.sh 配置 CAN 接口"
