#!/usr/bin/env python3
"""
PSoC6设备模拟器
用于测试Android App，无需真实硬件
"""

import bluetooth
import json
import time
import random
import math
import threading

class RobotArmSimulator:
    def __init__(self):
        self.mode = "active"  # active, passive, memory
        self.shoulder_angle = 45.0
        self.elbow_angle = 30.0
        self.lateral_pos = 50.0
        self.running = True

    def get_sensor_data(self):
        """生成模拟传感器数据"""
        # 添加一些随机波动
        shoulder_noise = random.uniform(-0.5, 0.5)
        elbow_noise = random.uniform(-0.5, 0.5)

        return {
            "type": "sensor",
            "shoulder_angle": self.shoulder_angle + shoulder_noise,
            "elbow_angle": self.elbow_angle + elbow_noise,
            "lateral_pos": self.lateral_pos,
            "shoulder_force": random.uniform(10, 15),
            "elbow_force": random.uniform(8, 12),
            "shoulder_accel_x": random.uniform(-0.5, 0.5),
            "shoulder_accel_y": random.uniform(-0.5, 0.5),
            "shoulder_accel_z": random.uniform(9.5, 10.2),
            "elbow_accel_x": random.uniform(-0.5, 0.5),
            "elbow_accel_y": random.uniform(-0.5, 0.5),
            "elbow_accel_z": random.uniform(9.5, 10.2),
            "shoulder_temp": random.uniform(27, 32),
            "elbow_temp": random.uniform(26, 31),
            "lateral_temp": random.uniform(25, 30)
        }

    def handle_mode_command(self, data):
        """处理模式切换命令"""
        mode = data.get("mode")
        if mode in ["active", "passive", "memory"]:
            self.mode = mode
            print(f"Mode changed to: {mode}")
            return {"type": "mode_ack", "success": True, "mode": mode}
        return {"type": "error", "code": 1001, "message": "Invalid mode"}

    def handle_control_command(self, data):
        """处理控制命令"""
        if self.mode != "passive":
            return {"type": "error", "code": 1003, "message": "Not in passive mode"}

        if "shoulder_angle" in data:
            self.shoulder_angle = max(0, min(180, data["shoulder_angle"]))
        if "elbow_angle" in data:
            self.elbow_angle = max(0, min(180, data["elbow_angle"]))
        if "lateral_pos" in data:
            self.lateral_pos = max(0, min(100, data["lateral_pos"]))

        print(f"Control: shoulder={self.shoulder_angle:.1f}, elbow={self.elbow_angle:.1f}, lateral={self.lateral_pos:.1f}")
        return {"type": "control_ack", "success": True}

    def handle_memory_command(self, data):
        """处理记忆动作上传"""
        action_id = data.get("action_id")
        keyframes = data.get("keyframes", [])
        print(f"Memory action uploaded: {action_id}, {len(keyframes)} keyframes")
        return {"type": "memory_ack", "success": True, "action_id": action_id}

    def handle_execute_memory(self, data):
        """处理执行记忆动作"""
        action_id = data.get("action_id")
        print(f"Executing memory action: {action_id}")
        return {"type": "execute_ack", "success": True, "action_id": action_id}

    def handle_stop_command(self):
        """处理停止命令"""
        print("Emergency stop!")
        return {"type": "stop_ack", "success": True}

    def process_command(self, json_str):
        """处理接收到的命令"""
        try:
            data = json.loads(json_str)
            cmd_type = data.get("type")

            if cmd_type == "mode":
                return self.handle_mode_command(data)
            elif cmd_type == "control":
                return self.handle_control_command(data)
            elif cmd_type == "memory":
                return self.handle_memory_command(data)
            elif cmd_type == "execute_memory":
                return self.handle_execute_memory(data)
            elif cmd_type == "stop":
                return self.handle_stop_command()
            else:
                return {"type": "error", "code": 1001, "message": "Unknown command"}
        except json.JSONDecodeError:
            return {"type": "error", "code": 1001, "message": "Invalid JSON"}

def run_simulator():
    """运行蓝牙模拟器"""
    simulator = RobotArmSimulator()

    # 创建蓝牙服务器
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    uuid = "00001101-0000-1000-8000-00805F9B34FB"

    bluetooth.advertise_service(
        server_sock, "RehabRobotArm",
        service_id=uuid,
        service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )

    print("=" * 50)
    print("PSoC6 Robot Arm Simulator")
    print("=" * 50)
    print(f"Waiting for connection on RFCOMM channel {port}")
    print("UUID:", uuid)
    print("\nPlease pair and connect from Android app...")

    client_sock, client_info = server_sock.accept()
    print(f"\n✓ Connected to {client_info}")
    print("\nSimulator running. Press Ctrl+C to stop.\n")

    # 接收命令的线程
    def receive_commands():
        buffer = ""
        while simulator.running:
            try:
                data = client_sock.recv(1024).decode('utf-8')
                if not data:
                    break

                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        print(f"← Received: {line[:80]}...")
                        response = simulator.process_command(line)
                        response_str = json.dumps(response) + "\n"
                        client_sock.send(response_str.encode('utf-8'))
                        print(f"→ Sent: {response_str[:80]}...")
            except Exception as e:
                print(f"Error receiving: {e}")
                break

    recv_thread = threading.Thread(target=receive_commands, daemon=True)
    recv_thread.start()

    # 主循环：发送传感器数据
    try:
        while simulator.running:
            sensor_data = simulator.get_sensor_data()
            data_str = json.dumps(sensor_data) + "\n"

            try:
                client_sock.send(data_str.encode('utf-8'))
                time.sleep(0.1)  # 10Hz
            except Exception as e:
                print(f"Error sending: {e}")
                break

    except KeyboardInterrupt:
        print("\n\nShutting down simulator...")
    finally:
        simulator.running = False
        client_sock.close()
        server_sock.close()
        print("Simulator stopped.")

if __name__ == "__main__":
    try:
        run_simulator()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have pybluez installed:")
        print("  pip install pybluez")
