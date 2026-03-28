# ROS-VLA WebSocket 通信服务器

实时WebSocket服务器，用于ROS和VLA之间的双向通信，支持图像、语音、电机、传感器数据传输和指令控制。

## 功能特性

- ✅ ROS数据实时上传（图像、语音、电机、传感器）
- ✅ VLA指令下发到ROS
- ✅ Infineon语音识别结果接收（支持cJSON格式）
- ✅ 电机详细状态监控（温度、运行时间、错误码）
- ✅ 系统状态监控（CPU、内存、网络）
- ✅ Web实时监控界面
- ✅ 语音播报功能
- ✅ 自动重连机制
- ✅ 多客户端支持

## 快速开始

### 1. 安装依赖

```bash
cd ros-vla-websocket
npm install
```

### 2. 启动服务器

```bash
npm start
```

服务器将在 `http://0.0.0.0:8080` 启动

### 3. 访问监控界面

浏览器打开: `http://YOUR_SERVER_IP:8080`

## 客户端使用

### ROS客户端（NanoPi）

1. 安装Python依赖:
```bash
pip3 install websockets
```

2. 修改 `ros_client.py` 中的服务器地址:
```python
WS_SERVER = "ws://YOUR_SERVER_IP:8080"
```

3. 运行客户端:
```bash
python3 ros_client.py
```

### VLA客户端

1. 安装Python依赖:
```bash
pip3 install websockets
```

2. 修改 `vla_client.py` 中的服务器地址:
```python
WS_SERVER = "ws://YOUR_SERVER_IP:8080"
```

3. 运行客户端:
```bash
python3 vla_client.py
```

### Infineon客户端

1. 安装Python依赖:
```bash
pip3 install websockets
```

2. 修改 `infineon_client.py` 中的服务器地址:
```python
WS_SERVER = "ws://YOUR_SERVER_IP:8080"
```

3. 运行客户端:
```bash
python3 infineon_client.py
```

3. 运行客户端:
```bash
python3 vla_client.py
```

## 数据格式

### ROS发送数据

**图像数据:**
```json
{
  "type": "ros_data",
  "dataType": "image",
  "payload": "data:image/jpeg;base64,..."
}
```

**电机数据:**
```json
{
  "type": "ros_data",
  "dataType": "motors",
  "payload": [
    {"position": 45.5, "velocity": 1.2, "current": 0.5},
    {"position": 90.0, "velocity": 0.8, "current": 0.3}
  ]
}
```

**传感器数据:**
```json
{
  "type": "ros_data",
  "dataType": "sensors",
  "payload": [
    {"name": "温度", "value": 25.5, "unit": "°C"},
    {"name": "湿度", "value": 60, "unit": "%"}
  ]
}
```

**电机详细状态:**
```json
{
  "type": "ros_data",
  "dataType": "motor_status",
  "payload": {
    "1": {"temperature": 45.5, "runtime": 120.5, "error_code": 0},
    "2": {"temperature": 52.3, "runtime": 118.2, "error_code": 0}
  }
}
```

**系统状态:**
```json
{
  "type": "ros_data",
  "dataType": "system_status",
  "payload": {
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "disk_usage": 35.5
  }
}
```

### Infineon发送语音识别结果

```json
{
  "type": "infineon_voice",
  "text": "向前移动",
  "confidence": 0.95,
  "raw": {
    "command": "向前移动",
    "confidence": 0.95,
    "language": "zh-CN",
    "timestamp": 1234567890
  }
}
```

### VLA发送指令

```json
{
  "type": "vla_command",
  "command": {
    "action": "move_forward",
    "params": {"distance": 1.0, "speed": 0.5}
  }
}
```

## 公网部署

### 方法1: 使用云服务器

1. 购买云服务器（阿里云、腾讯云等）
2. 开放8080端口
3. 上传代码并运行

### 方法2: 使用内网穿透

使用frp、ngrok等工具将本地服务映射到公网

**frp示例配置:**
```ini
[websocket]
type = tcp
local_ip = 127.0.0.1
local_port = 8080
remote_port = 8080
```

### 方法3: 使用Cloudflare Tunnel

免费且稳定的内网穿透方案

## 端口配置

修改端口可以通过环境变量:
```bash
PORT=3000 npm start
```

## 安全建议

1. 生产环境建议添加认证机制
2. 使用HTTPS/WSS加密传输
3. 限制客户端连接数
4. 添加数据大小限制

## 故障排查

**连接失败:**
- 检查防火墙设置
- 确认服务器IP和端口正确
- 查看服务器日志

**数据不显示:**
- 检查客户端是否正确注册
- 查看浏览器控制台错误
- 确认数据格式正确

## 许可证

MIT
