#!/usr/bin/env python3
"""
VLA WebSocket客户端示例
用于VLA发送控制指令到ROS
"""

import asyncio
import websockets
import json

# WebSocket服务器地址（替换为你的公网IP或域名）
WS_SERVER = "ws://YOUR_SERVER_IP:8080"

class VLAWebSocketClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.ws = None

    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.ws = await websockets.connect(self.server_url)
            print(f"Connected to {self.server_url}")

            # 注册为VLA客户端
            await self.ws.send(json.dumps({
                "type": "register",
                "role": "vla"
            }))

            response = await self.ws.recv()
            print(f"Registration response: {response}")

        except Exception as e:
            print(f"Connection error: {e}")
            raise

    async def send_command(self, command):
        """
        发送控制指令到ROS
        command: 指令字典
        示例: {
            "action": "move",
            "params": {"x": 1.0, "y": 0.5, "theta": 0.0}
        }
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            message = {
                "type": "vla_command",
                "command": command
            }

            await self.ws.send(json.dumps(message))
            print(f"Command sent: {command}")

        except Exception as e:
            print(f"Error sending command: {e}")

    async def close(self):
        """关闭连接"""
        if self.ws:
            await self.ws.close()
            print("Connection closed")


# 使用示例
async def main():
    client = VLAWebSocketClient(WS_SERVER)

    try:
        await client.connect()

        # 示例：发送不同类型的指令
        commands = [
            {
                "action": "move_forward",
                "params": {"distance": 1.0, "speed": 0.5}
            },
            {
                "action": "rotate",
                "params": {"angle": 90, "direction": "left"}
            },
            {
                "action": "grasp",
                "params": {"force": 0.8}
            },
            {
                "action": "set_motor",
                "params": {"motor_id": 1, "position": 45.0}
            }
        ]

        for cmd in commands:
            await client.send_command(cmd)
            await asyncio.sleep(2)  # 每2秒发送一个指令

        # 保持连接
        await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
