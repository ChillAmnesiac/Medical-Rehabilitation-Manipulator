#!/usr/bin/env python3
"""
Infineon WebSocket客户端示例
用于发送语音识别结果（cJSON格式）到WebSocket服务器
"""

import asyncio
import websockets
import json

# WebSocket服务器地址
WS_SERVER = "ws://YOUR_SERVER_IP:8080"

class InfineonWebSocketClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.ws = None

    async def connect(self):
        """连接到WebSocket服务器"""
        try:
            self.ws = await websockets.connect(self.server_url)
            print(f"Connected to {self.server_url}")

            # 注册为Infineon客户端
            await self.ws.send(json.dumps({
                "type": "register",
                "role": "infineon"
            }))

            response = await self.ws.recv()
            print(f"Registration response: {response}")

        except Exception as e:
            print(f"Connection error: {e}")
            raise

    async def send_voice_command(self, text, confidence=1.0, raw_json=None):
        """
        发送语音识别结果

        参数:
        text: 识别的文字内容
        confidence: 置信度 (0.0-1.0)
        raw_json: 原始cJSON数据（可选）
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            message = {
                "type": "infineon_voice",
                "text": text,
                "confidence": confidence,
                "raw": raw_json
            }

            await self.ws.send(json.dumps(message))
            print(f"Voice command sent: {text} (confidence: {confidence})")

        except Exception as e:
            print(f"Error sending voice command: {e}")

    async def send_cjson_result(self, cjson_data):
        """
        发送原始cJSON格式的语音识别结果

        参数:
        cjson_data: dict格式的cJSON数据
        示例: {
            "command": "move forward",
            "confidence": 0.95,
            "language": "en-US",
            "timestamp": 1234567890
        }
        """
        if self.ws is None:
            print("Not connected")
            return

        try:
            # 提取关键信息
            text = cjson_data.get("command", "")
            confidence = cjson_data.get("confidence", 1.0)

            message = {
                "type": "infineon_voice",
                "text": text,
                "confidence": confidence,
                "raw": cjson_data  # 保存完整的cJSON数据
            }

            await self.ws.send(json.dumps(message))
            print(f"cJSON result sent: {text}")

        except Exception as e:
            print(f"Error sending cJSON result: {e}")

    async def close(self):
        """关闭连接"""
        if self.ws:
            await self.ws.close()
            print("Connection closed")


# 使用示例
async def main():
    client = InfineonWebSocketClient(WS_SERVER)

    try:
        await client.connect()

        # 示例1: 发送简单的语音指令
        await client.send_voice_command("向前移动", confidence=0.95)
        await asyncio.sleep(2)

        await client.send_voice_command("抓取物体", confidence=0.88)
        await asyncio.sleep(2)

        # 示例2: 发送完整的cJSON数据
        cjson_result = {
            "command": "rotate left 90 degrees",
            "confidence": 0.92,
            "language": "en-US",
            "timestamp": 1234567890,
            "alternatives": [
                {"text": "rotate left 90 degrees", "confidence": 0.92},
                {"text": "rotate left 19 degrees", "confidence": 0.15}
            ],
            "audio_duration": 2.5,
            "processing_time": 0.3
        }
        await client.send_cjson_result(cjson_result)
        await asyncio.sleep(2)

        # 示例3: 中文语音指令
        chinese_result = {
            "command": "停止运动",
            "confidence": 0.98,
            "language": "zh-CN",
            "timestamp": 1234567891
        }
        await client.send_cjson_result(chinese_result)

        # 保持连接
        await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
