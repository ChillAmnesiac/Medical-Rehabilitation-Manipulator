#!/bin/bash

# 启动脚本
echo "正在启动 ROS-VLA WebSocket 服务器..."
echo "================================"

# 获取本机IP
IP=$(hostname -I | awk '{print $1}')

echo "服务器将在以下地址启动:"
echo "  本地访问: http://localhost:8080"
echo "  局域网访问: http://$IP:8080"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================"

# 启动服务器
node server.js
