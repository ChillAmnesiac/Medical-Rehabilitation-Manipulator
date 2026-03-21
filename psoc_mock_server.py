#!/usr/bin/env python3
"""
PSoC Edge Mock HTTP Server
模拟PSoC Edge设备，生成测试传感器数据用于测试App连接
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import math
import threading

class PSoCState:
    """PSoC设备状态"""
    def __init__(self):
        self.mode = "ACTIVE"  # ACTIVE, PASSIVE, MEMORY
        self.shoulder_angle = 45.0
        self.elbow_angle = 90.0
        self.lateral_position = 50.0
        self.shoulder_torque = 0.0
        self.elbow_torque = 0.0
        self.emg_ch1 = 0.0
        self.emg_ch2 = 0.0
        self.temperature = 36.5
        self.is_executing = False
        self.start_time = time.time()

    def update_simulation(self):
        """更新模拟数据 - 生成正弦波运动"""
        t = time.time() - self.start_time

        if self.mode == "ACTIVE":
            # 主动模式：模拟患者自主运动
            self.shoulder_angle = 45 + 30 * math.sin(t * 0.5)
            self.elbow_angle = 90 + 20 * math.sin(t * 0.3)
            self.lateral_position = 50 + 10 * math.sin(t * 0.4)
            self.shoulder_torque = 2.0 + 1.0 * math.sin(t * 0.5)
            self.elbow_torque = 1.5 + 0.8 * math.sin(t * 0.3)
            self.emg_ch1 = abs(50 + 30 * math.sin(t * 2.0))
            self.emg_ch2 = abs(40 + 25 * math.sin(t * 2.5))

        elif self.mode == "PASSIVE":
            # 被动模式：保持设定位置
            pass  # 位置由外部控制命令设置

        elif self.mode == "MEMORY":
            # 记忆模式：执行预设动作
            if self.is_executing:
                self.shoulder_angle = 45 + 45 * math.sin(t * 0.8)
                self.elbow_angle = 90 + 30 * math.sin(t * 0.8)
                self.lateral_position = 50 + 15 * math.sin(t * 0.8)

        # 温度缓慢变化
        self.temperature = 36.5 + 0.5 * math.sin(t * 0.1)

state = PSoCState()

class PSoCHandler(BaseHTTPRequestHandler):
    """处理HTTP请求"""

    def do_GET(self):
        """处理GET请求 - 获取传感器数据"""
        if self.path == "/status":
            state.update_simulation()

            response = {
                "timestamp": int(time.time() * 1000),
                "mode": state.mode,
                "shoulder_angle": round(state.shoulder_angle, 2),
                "elbow_angle": round(state.elbow_angle, 2),
                "lateral_position": round(state.lateral_position, 2),
                "shoulder_torque": round(state.shoulder_torque, 2),
                "elbow_torque": round(state.elbow_torque, 2),
                "emg_ch1": round(state.emg_ch1, 2),
                "emg_ch2": round(state.emg_ch2, 2),
                "temperature": round(state.temperature, 2),
                "is_executing": state.is_executing
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        elif self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "device": "PSoC Edge Mock"}).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """处理POST请求 - 控制命令"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()

        try:
            data = json.loads(body)

            if self.path == "/mode":
                # 切换模式
                mode = data.get("mode", "ACTIVE")
                if mode in ["ACTIVE", "PASSIVE", "MEMORY"]:
                    state.mode = mode
                    response = {"success": True, "mode": state.mode}
                else:
                    response = {"success": False, "error": "Invalid mode"}

            elif self.path == "/control":
                # 被动模式控制
                if state.mode == "PASSIVE":
                    if "shoulder_angle" in data:
                        state.shoulder_angle = data["shoulder_angle"]
                    if "elbow_angle" in data:
                        state.elbow_angle = data["elbow_angle"]
                    if "lateral_position" in data:
                        state.lateral_position = data["lateral_position"]
                    response = {"success": True}
                else:
                    response = {"success": False, "error": "Not in PASSIVE mode"}

            elif self.path == "/memory/execute":
                # 执行记忆动作
                if state.mode == "MEMORY":
                    state.is_executing = True
                    state.start_time = time.time()
                    response = {"success": True, "message": "Executing memory action"}
                else:
                    response = {"success": False, "error": "Not in MEMORY mode"}

            elif self.path == "/memory/stop":
                # 停止记忆动作
                state.is_executing = False
                response = {"success": True, "message": "Stopped"}

            else:
                response = {"success": False, "error": "Unknown endpoint"}

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}")

def run_server(port=8081):
    """启动HTTP服务器"""
    server = HTTPServer(('0.0.0.0', port), PSoCHandler)
    print(f"PSoC Edge Mock Server 启动在端口 {port}")
    print(f"测试URL: http://localhost:{port}/status")
    print("按 Ctrl+C 停止服务器")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()

if __name__ == "__main__":
    run_server()
