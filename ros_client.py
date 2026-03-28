#!/usr/bin/env python3
"""
ROS WebSocket客户端示例
在NanoPi上运行，发送图像、语音、电机和传感器数据到WebSocket服务器
"""

import asyncio
import websockets
import json
import base64
from datetime import datetime

# WebSocket服务器地址（替换为你的公网IP或域名）
WS_SERVER = "ws://YOUR_SERVER_IP:8080"

class ROSWebSocketClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.ws = None

    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.ws = await websockets.connect(self.server_url)
            print(f"Connected to {self.server_url}")

            # 注册为ROS客户端
            await self.ws.send(json.dumps({
                "type": "register",
                "role": "ros"
            }))

            response = await self.ws.recv()
            print(f"Registration response: {response}")

        except Exception as e:
            print(f"Connection error: {e}")
            raise

    async def send_image(self, image_data):
        """
        发送图像数据
        image_data: base64编码的图像字符串，或者图像文件路径
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            # 如果是文件路径，读取并编码
            if isinstance(image_data, str) and image_data.endswith(('.jpg', '.png', '.jpeg')):
                with open(image_data, 'rb') as f:
                    image_bytes = f.read()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    image_data = f"data:image/jpeg;base64,{image_base64}"

            message = {
                "type": "ros_data",
                "dataType": "image",
                "payload": image_data
            }

            await self.ws.send(json.dumps(message))
            print("Image sent")

        except Exception as e:
            print(f"Error sending image: {e}")

    async def send_audio(self, audio_data):
        """
        发送语音数据
        audio_data: base64编码的音频字符串，或者音频文件路径
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            # 如果是文件路径，读取并编码
            if isinstance(audio_data, str) and audio_data.endswith(('.wav', '.mp3', '.ogg')):
                with open(audio_data, 'rb') as f:
                    audio_bytes = f.read()
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                    audio_data = f"data:audio/wav;base64,{audio_base64}"

            message = {
                "type": "ros_data",
                "dataType": "audio",
                "payload": audio_data
            }

            await self.ws.send(json.dumps(message))
            print("Audio sent")

        except Exception as e:
            print(f"Error sending audio: {e}")

    async def send_motor_data(self, motors):
        """
        发送电机数据
        motors: 电机数据列表，每个电机包含 position, velocity, current
        示例: [
            {"position": 45.5, "velocity": 1.2, "current": 0.5},
            {"position": 90.0, "velocity": 0.8, "current": 0.3},
            ...
        ]
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            message = {
                "type": "ros_data",
                "dataType": "motors",
                "payload": motors
            }

            await self.ws.send(json.dumps(message))
            print(f"Motor data sent: {len(motors)} motors")

        except Exception as e:
            print(f"Error sending motor data: {e}")

    async def send_sensor_data(self, sensors):
        """
        发送传感器数据
        sensors: 传感器数据列表
        示例: [
            {"name": "温度", "value": 25.5, "unit": "°C"},
            {"name": "湿度", "value": 60, "unit": "%"},
            {"name": "距离", "value": 150, "unit": "cm"}
        ]
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            message = {
                "type": "ros_data",
                "dataType": "sensors",
                "payload": sensors
            }

            await self.ws.send(json.dumps(message))
            print(f"Sensor data sent: {len(sensors)} sensors")

        except Exception as e:
            print(f"Error sending sensor data: {e}")

    async def send_motor_status(self, motor_status):
        """
        发送电机详细状态
        motor_status: 电机状态字典
        示例: {
            "1": {"temperature": 45.5, "runtime": 120.5, "error_code": 0},
            "2": {"temperature": 52.3, "runtime": 118.2, "error_code": 0},
            "3": {"temperature": 48.1, "runtime": 119.8, "error_code": 0}
        }
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            message = {
                "type": "ros_data",
                "dataType": "motor_status",
                "payload": motor_status
            }

            await self.ws.send(json.dumps(message))
            print(f"Motor status sent: {len(motor_status)} motors")

        except Exception as e:
            print(f"Error sending motor status: {e}")

    async def send_system_status(self, system_status):
        """
        发送系统状态
        system_status: 系统状态字典
        示例: {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 35.5,
            "network_rx": 1024,
            "network_tx": 512
        }
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            message = {
                "type": "ros_data",
                "dataType": "system_status",
                "payload": system_status
            }

            await self.ws.send(json.dumps(message))
            print("System status sent")

        except Exception as e:
            print(f"Error sending system status: {e}")

    async def receive_commands(self):
        """接收来自VLA的指令和Infineon的语音指令"""
        try:
            async for message in self.ws:
                data = json.loads(message)

                if data.get("type") == "vla_command":
                    command = data.get("command")
                    print(f"Received VLA command: {command}")
                    # 在这里处理VLA发来的指令
                    # 例如：控制机器人移动、执行动作等

                elif data.get("type") == "voice_command":
                    text = data.get("text")
                    confidence = data.get("confidence")
                    print(f"Received voice command: {text} (confidence: {confidence})")
                    # 在这里处理语音指令
                    # 例如：解析语音指令并执行相应动作

        except Exception as e:
            print(f"Error receiving commands: {e}")

    async def close(self):
        """关闭连接"""
        if self.ws:
            await self.ws.close()
            print("Connection closed")


# 使用示例
async def main():
    client = ROSWebSocketClient(WS_SERVER)

    try:
        await client.connect()

        # 创建接收指令的任务
        receive_task = asyncio.create_task(client.receive_commands())

        # 模拟发送数据
        while True:
            # 发送电机数据（5个电机）
            motor_data = [
                {"position": 45.5, "velocity": 1.2, "current": 0.5},
                {"position": 90.0, "velocity": 0.8, "current": 0.3},
                {"position": 30.2, "velocity": 1.5, "current": 0.6},
                {"position": 60.8, "velocity": 0.9, "current": 0.4},
                {"position": 120.5, "velocity": 1.1, "current": 0.55}
            ]
            await client.send_motor_data(motor_data)

            # 发送电机详细状态
            motor_status = {
                "1": {"temperature": 45.5, "runtime": 120.5, "error_code": 0},
                "2": {"temperature": 52.3, "runtime": 118.2, "error_code": 0},
                "3": {"temperature": 48.1, "runtime": 119.8, "error_code": 0},
                "4": {"temperature": 43.2, "runtime": 121.3, "error_code": 0},
                "5": {"temperature": 50.8, "runtime": 117.9, "error_code": 0}
            }
            await client.send_motor_status(motor_status)

            # 发送传感器数据
            sensor_data = [
                {"name": "温度", "value": 25.5, "unit": "°C"},
                {"name": "湿度", "value": 60, "unit": "%"},
                {"name": "距离", "value": 150, "unit": "cm"},
                {"name": "电压", "value": 12.5, "unit": "V"}
            ]
            await client.send_sensor_data(sensor_data)

            # 发送系统状态
            system_status = {
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "disk_usage": 35.5,
                "network_rx": 1024,
                "network_tx": 512
            }
            await client.send_system_status(system_status)

            # 如果有图像，发送图像
            # await client.send_image("/path/to/image.jpg")

            # 如果有语音，发送语音
            # await client.send_audio("/path/to/audio.wav")

            await asyncio.sleep(1)  # 每秒发送一次

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
