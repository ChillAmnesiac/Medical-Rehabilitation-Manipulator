#!/bin/bash
# Apply NanoPi M5 SPI3 MCP2518FD kernel patch.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_FILE="${SCRIPT_DIR}/../kernel-patches/0001-arm64-dts-enable-MCP2518FD-CAN-on-NanoPi-M5-SPI3.patch"

if [ $# -lt 1 ]; then
    echo "Usage: $0 /path/to/friendlywrt24-rk3576/kernel"
    exit 1
fi

KERNEL_DIR="$1"

if [ ! -d "${KERNEL_DIR}/.git" ]; then
    echo "error: ${KERNEL_DIR} is not a git kernel tree"
    exit 1
fi

if [ ! -f "${PATCH_FILE}" ]; then
    echo "error: patch not found: ${PATCH_FILE}"
    exit 1
fi

cd "${KERNEL_DIR}"

echo "Applying NanoPi M5 SPI3 MCP2518FD patch..."
git am "${PATCH_FILE}"

echo ""
echo "Patch applied. Build-check DTB with:"
echo "  export PATH=/home/cal/friendlywrt24-rk3576/.local-toolchain/11.3-aarch64/bin:\$PATH"
echo "  make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- rockchip/rk3576-nanopi5-rev01.dtb"
