#!/bin/bash

# 启动WebSocket服务器和Cloudflare隧道

echo "================================"
echo "🚀 启动 ROS-VLA WebSocket 服务器"
echo "================================"

# 启动WebSocket服务器（后台运行）
node server.js &
SERVER_PID=$!

echo "✅ WebSocket服务器已启动 (PID: $SERVER_PID)"
echo ""

# 等待服务器启动
sleep 2

# 启动Cloudflare隧道
echo "🌐 启动 Cloudflare 隧道..."
echo "================================"
./cloudflared tunnel --url http://localhost:8080

# 清理：当隧道停止时，也停止服务器
kill $SERVER_PID 2>/dev/null
echo ""
echo "服务器已停止"
