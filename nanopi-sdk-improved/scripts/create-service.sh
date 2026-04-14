#!/bin/bash
set -e
SERVICE_NAME="can-setup"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$EUID" -ne 0 ]; then
    echo "错误: 请使用 sudo 运行此脚本"
    exit 1
fi
cat > ${SERVICE_FILE} << EOFSERVICE
[Unit]
Description=CAN Interface Setup for MCP2518FD
After=network.target
[Service]
Type=oneshot
ExecStart=${SCRIPT_DIR}/setup-can.sh 1000000
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
EOFSERVICE
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}.service
echo "✓ 服务已创建"
