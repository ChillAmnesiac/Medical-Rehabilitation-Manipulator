#!/bin/bash

echo "=================================="
echo "康复机械臂项目 - 快速启动脚本"
echo "=================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

echo "✓ Python3已安装"

# 检查pybluez是否安装
if ! python3 -c "import bluetooth" 2>/dev/null; then
    echo "⚠ pybluez未安装"
    echo "正在尝试安装pybluez..."
    pip3 install pybluez 2>/dev/null || pip install pybluez 2>/dev/null

    if ! python3 -c "import bluetooth" 2>/dev/null; then
        echo "❌ pybluez安装失败"
        echo ""
        echo "请手动安装："
        echo "  sudo apt-get install libbluetooth-dev"
        echo "  pip3 install pybluez"
        echo ""
        echo "或者使用模拟数据模式（无需蓝牙）"
        exit 1
    fi
fi

echo "✓ pybluez已安装"
echo ""
echo "=================================="
echo "选择运行模式："
echo "=================================="
echo "1. 启动蓝牙设备模拟器（需要蓝牙硬件）"
echo "2. 查看项目信息"
echo "3. 打开Android Studio"
echo "4. 退出"
echo ""
read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "正在启动蓝牙设备模拟器..."
        echo "请在Android设备上搜索并连接'RehabRobotArm'"
        echo ""
        python3 device_simulator.py
        ;;
    2)
        echo ""
        echo "项目信息："
        echo "- 项目路径: $(pwd)"
        echo "- 包名: com.rehab.robotarm"
        echo "- 最小SDK: 26 (Android 8.0)"
        echo "- 目标SDK: 34 (Android 14)"
        echo ""
        echo "主要文件："
        echo "- README.md - 项目说明"
        echo "- QUICKSTART.md - 快速开始"
        echo "- ARCHITECTURE.md - 架构文档"
        echo "- PROTOCOL.md - 通信协议"
        echo ""
        ;;
    3)
        echo ""
        echo "正在启动Android Studio..."
        /home/wen/android-studio/bin/studio.sh . &
        echo "Android Studio已启动"
        ;;
    4)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
