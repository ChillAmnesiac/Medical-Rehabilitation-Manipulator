# PSoC6 设备端通信协议规范

本文档定义了Android App与PSoC6机械臂设备之间的蓝牙通信协议。

## 通信方式

- **传输协议**: 蓝牙经典 (Bluetooth Classic)
- **UUID**: `00001101-0000-1000-8000-00805F9B34FB` (SPP标准UUID)
- **数据格式**: JSON字符串
- **编码**: UTF-8
- **波特率**: 115200 (建议)

## 数据包格式

所有数据包都是JSON格式，以换行符 `\n` 结尾。

### 1. 传感器数据上报 (设备 → App)

**频率**: 建议10-50Hz

**格式**:
```json
{
  "type": "sensor",
  "shoulder_angle": 45.5,
  "elbow_angle": 30.2,
  "lateral_pos": 50.0,
  "shoulder_force": 12.5,
  "elbow_force": 8.3,
  "shoulder_accel_x": 0.5,
  "shoulder_accel_y": 0.2,
  "shoulder_accel_z": 9.8,
  "elbow_accel_x": 0.3,
  "elbow_accel_y": 0.1,
  "elbow_accel_z": 9.7,
  "shoulder_temp": 28.5,
  "elbow_temp": 27.8,
  "lateral_temp": 26.5
}
```

**字段说明**:

| 字段 | 类型 | 单位 | 范围 | 说明 |
|------|------|------|------|------|
| type | string | - | "sensor" | 数据包类型标识 |
| shoulder_angle | float | 度(°) | 0-180 | 肩关节角度 |
| elbow_angle | float | 度(°) | 0-180 | 肘关节角度 |
| lateral_pos | float | % | 0-100 | 推杆位置百分比 |
| shoulder_force | float | N | 0-100 | 肩关节力传感器 |
| elbow_force | float | N | 0-100 | 肘关节力传感器 |
| shoulder_accel_x | float | m/s² | -20~20 | 肩关节X轴加速度 |
| shoulder_accel_y | float | m/s² | -20~20 | 肩关节Y轴加速度 |
| shoulder_accel_z | float | m/s² | -20~20 | 肩关节Z轴加速度 |
| elbow_accel_x | float | m/s² | -20~20 | 肘关节X轴加速度 |
| elbow_accel_y | float | m/s² | -20~20 | 肘关节Y轴加速度 |
| elbow_accel_z | float | m/s² | -20~20 | 肘关节Z轴加速度 |
| shoulder_temp | float | °C | 0-100 | 肩关节电机温度 |
| elbow_temp | float | °C | 0-100 | 肘关节电机温度 |
| lateral_temp | float | °C | 0-100 | 推杆电机温度 |

### 2. 模式切换命令 (App → 设备)

**格式**:
```json
{
  "type": "mode",
  "mode": "active"
}
```

**字段说明**:

| 字段 | 类型 | 可选值 | 说明 |
|------|------|--------|------|
| type | string | "mode" | 命令类型 |
| mode | string | "active", "passive", "memory" | 目标模式 |

**模式说明**:
- `active`: 主动模式 - 电机不使能，患者自由运动
- `passive`: 被动模式 - 电机使能，接受App控制
- `memory`: 记忆模式 - 执行预设动作序列

**设备响应**:
```json
{
  "type": "mode_ack",
  "success": true,
  "mode": "active"
}
```

### 3. 控制命令 (App → 设备，仅被动模式)

**格式**:
```json
{
  "type": "control",
  "shoulder_angle": 45.0,
  "elbow_angle": 30.0,
  "lateral_pos": 50.0
}
```

**字段说明**:

| 字段 | 类型 | 单位 | 范围 | 必填 | 说明 |
|------|------|------|------|------|------|
| type | string | - | "control" | 是 | 命令类型 |
| shoulder_angle | float | 度(°) | 0-180 | 否 | 目标肩关节角度 |
| elbow_angle | float | 度(°) | 0-180 | 否 | 目标肘关节角度 |
| lateral_pos | float | % | 0-100 | 否 | 目标推杆位置 |

**注意**:
- 字段可选，只发送需要控制的关节
- 设备端必须实现限位保护
- 建议实现平滑插值，避免突变

**设备响应**:
```json
{
  "type": "control_ack",
  "success": true
}
```

### 4. 记忆动作上传 (App → 设备)

**格式**:
```json
{
  "type": "memory",
  "action_id": "uuid-string",
  "keyframes": [
    {
      "time": 0,
      "shoulder": 0.0,
      "elbow": 0.0,
      "lateral": 0.0
    },
    {
      "time": 1000,
      "shoulder": 45.0,
      "elbow": 30.0,
      "lateral": 50.0
    },
    {
      "time": 2000,
      "shoulder": 90.0,
      "elbow": 60.0,
      "lateral": 80.0
    }
  ]
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 命令类型 "memory" |
| action_id | string | 动作唯一标识符 |
| keyframes | array | 关键帧数组 |
| keyframes[].time | int | 相对时间戳(毫秒) |
| keyframes[].shoulder | float | 肩关节角度(度) |
| keyframes[].elbow | float | 肘关节角度(度) |
| keyframes[].lateral | float | 推杆位置(%) |

**设备响应**:
```json
{
  "type": "memory_ack",
  "success": true,
  "action_id": "uuid-string"
}
```

### 5. 执行记忆动作 (App → 设备)

**格式**:
```json
{
  "type": "execute_memory",
  "action_id": "uuid-string"
}
```

**设备响应**:
```json
{
  "type": "execute_ack",
  "success": true,
  "action_id": "uuid-string"
}
```

### 6. 停止命令 (App → 设备)

**格式**:
```json
{
  "type": "stop"
}
```

**说明**: 立即停止所有运动

**设备响应**:
```json
{
  "type": "stop_ack",
  "success": true
}
```

### 7. 错误响应 (设备 → App)

**格式**:
```json
{
  "type": "error",
  "code": 1001,
  "message": "Invalid command"
}
```

**错误码**:

| 错误码 | 说明 |
|--------|------|
| 1001 | 无效命令 |
| 1002 | 参数超出范围 |
| 1003 | 当前模式不支持该操作 |
| 1004 | 电机故障 |
| 1005 | 温度过高 |
| 1006 | 限位触发 |
| 1007 | 记忆动作不存在 |

## 实现建议

### PSoC6设备端

1. **JSON解析**: 使用轻量级JSON库（如cJSON）
2. **缓冲区**: 建议1024字节接收缓冲区
3. **数据上报**: 使用定时器定期发送传感器数据
4. **命令处理**: 使用状态机处理不同模式
5. **安全保护**:
   - 硬件限位开关
   - 软件限位检查
   - 温度监控和保护
   - 力传感器过载保护

### 示例代码片段 (PSoC6 C语言)

```c
// 发送传感器数据
void send_sensor_data() {
    char json_buffer[512];
    sprintf(json_buffer,
        "{\"type\":\"sensor\","
        "\"shoulder_angle\":%.2f,"
        "\"elbow_angle\":%.2f,"
        "\"lateral_pos\":%.2f,"
        "\"shoulder_force\":%.2f,"
        "\"elbow_force\":%.2f,"
        "\"shoulder_accel_x\":%.2f,"
        "\"shoulder_accel_y\":%.2f,"
        "\"shoulder_accel_z\":%.2f,"
        "\"elbow_accel_x\":%.2f,"
        "\"elbow_accel_y\":%.2f,"
        "\"elbow_accel_z\":%.2f,"
        "\"shoulder_temp\":%.1f,"
        "\"elbow_temp\":%.1f,"
        "\"lateral_temp\":%.1f}\n",
        get_shoulder_angle(),
        get_elbow_angle(),
        get_lateral_position(),
        get_shoulder_force(),
        get_elbow_force(),
        get_shoulder_accel_x(),
        get_shoulder_accel_y(),
        get_shoulder_accel_z(),
        get_elbow_accel_x(),
        get_elbow_accel_y(),
        get_elbow_accel_z(),
        get_shoulder_temp(),
        get_elbow_temp(),
        get_lateral_temp()
    );

    bluetooth_send(json_buffer, strlen(json_buffer));
}

// 处理接收到的命令
void process_command(const char* json_str) {
    cJSON* root = cJSON_Parse(json_str);
    if (root == NULL) return;

    cJSON* type = cJSON_GetObjectItem(root, "type");
    if (type == NULL) {
        cJSON_Delete(root);
        return;
    }

    if (strcmp(type->valuestring, "mode") == 0) {
        cJSON* mode = cJSON_GetObjectItem(root, "mode");
        if (mode != NULL) {
            handle_mode_change(mode->valuestring);
        }
    } else if (strcmp(type->valuestring, "control") == 0) {
        handle_control_command(root);
    } else if (strcmp(type->valuestring, "memory") == 0) {
        handle_memory_upload(root);
    } else if (strcmp(type->valuestring, "execute_memory") == 0) {
        handle_memory_execute(root);
    } else if (strcmp(type->valuestring, "stop") == 0) {
        emergency_stop();
    }

    cJSON_Delete(root);
}
```

## 测试工具

可以使用以下工具测试协议：

1. **串口调试助手**: 测试JSON格式
2. **蓝牙串口APP**: 测试蓝牙通信
3. **Python脚本**: 模拟设备端

### Python模拟设备示例

```python
import bluetooth
import json
import time
import random

def simulate_device():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]
    uuid = "00001101-0000-1000-8000-00805F9B34FB"

    bluetooth.advertise_service(server_sock, "RehabRobotArm",
                                service_id=uuid,
                                service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])

    print("Waiting for connection on RFCOMM channel", port)
    client_sock, client_info = server_sock.accept()
    print("Accepted connection from", client_info)

    try:
        while True:
            # 发送模拟传感器数据
            sensor_data = {
                "type": "sensor",
                "shoulder_angle": random.uniform(0, 180),
                "elbow_angle": random.uniform(0, 180),
                "lateral_pos": random.uniform(0, 100),
                "shoulder_force": random.uniform(0, 50),
                "elbow_force": random.uniform(0, 50),
                "shoulder_accel_x": random.uniform(-2, 2),
                "shoulder_accel_y": random.uniform(-2, 2),
                "shoulder_accel_z": random.uniform(8, 11),
                "elbow_accel_x": random.uniform(-2, 2),
                "elbow_accel_y": random.uniform(-2, 2),
                "elbow_accel_z": random.uniform(8, 11),
                "shoulder_temp": random.uniform(25, 35),
                "elbow_temp": random.uniform(25, 35),
                "lateral_temp": random.uniform(25, 35)
            }

            client_sock.send(json.dumps(sensor_data) + "\n")
            time.sleep(0.1)  # 10Hz

    except Exception as e:
        print("Error:", e)
    finally:
        client_sock.close()
        server_sock.close()

if __name__ == "__main__":
    simulate_device()
```

## 版本历史

- v1.0 (2024-03): 初始版本
