# 康复外骨骼机械臂系统

这是 `Medical-Rehabilitation-Manipulator` 仓库的 GitHub 默认入口。

平台协作入口：

- [PLATFORM_DEVELOPMENT_ENTRY.md](./PLATFORM_DEVELOPMENT_ENTRY.md)
- [PLATFORM_TASK_BOARD.md](./PLATFORM_TASK_BOARD.md)

**当前主线不是早期 OpenClaw/App 直控方案，也不是单个电机 demo。** 本项目现在按医疗康复外骨骼机械臂的安全架构推进：AI、App、服务器、仿真和 NanoPi 都只能提出请求、建议或候选轨迹；真实运动必须经过 Infineon PSoC Edge E84 的 M33 安全裁决。

```text
正式运动主线:

传感/电机反馈
  -> M33 安全汇总
  -> NanoPi ROS2/上传网关
  -> Linux MuJoCo shadow / 服务器 VLA
  -> 高层任务或候选轨迹
  -> NanoPi
  -> M33 最终安全裁决
  -> 电机

唯一正式运动入口:

JointTrajectory -> NanoPi -> M33 -> 电机
```

## 当前权威入口

请优先看 `feature/rehab-arm-ros2-architecture` 分支中的当前架构文档：

- [`docs/CURRENT_PROJECT_BRIEFING.md`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/blob/feature/rehab-arm-ros2-architecture/docs/CURRENT_PROJECT_BRIEFING.md)
- [`docs/REHAB_ARM_SYSTEM_ARCHITECTURE.md`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/blob/feature/rehab-arm-ros2-architecture/docs/REHAB_ARM_SYSTEM_ARCHITECTURE.md)
- [`docs/COMMAND_CENTER_APP_PROTOCOL_V1.md`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/blob/feature/rehab-arm-ros2-architecture/docs/COMMAND_CENTER_APP_PROTOCOL_V1.md)
- [`docs/PATIENT_DEVICE_PROFILE_PROTOCOL_V1.md`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/blob/feature/rehab-arm-ros2-architecture/docs/PATIENT_DEVICE_PROFILE_PROTOCOL_V1.md)
- [`docs/PSOC_CAN_PROTOCOL_V1.md`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/blob/feature/rehab-arm-ros2-architecture/docs/PSOC_CAN_PROTOCOL_V1.md)

如果旧文档、旧 README、demo 代码或早期草案与这些文档冲突，以 `feature/rehab-arm-ros2-architecture` 的当前架构为准。

## 分支导览

| 分支 | 当前用途 | 备注 |
|---|---|---|
| [`feature/rehab-arm-ros2-architecture`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/feature/rehab-arm-ros2-architecture) | ROS2、NanoPi、MuJoCo、系统架构、安全 gate、协议文档主线 | 当前讲解和后续协作基准 |
| [`M33`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/M33) | Infineon M33 固件、安全状态机、CAN、电机控制、BLE、M55 IPC | M33 是最终安全裁决者 |
| [`M55`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/M55) | Infineon M55 Wi-Fi、LVGL、语音/XiaoZhi、小模型、M33 IPC | 只输出建议和语音/模型结果，不直接控制电机 |
| [`nanopi-sdk`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/nanopi-sdk) | NanoPi M5 Linux/CAN 底层 bring-up、MCP2518FD/SocketCAN | 底层驱动和硬件调试资料 |
| [`C8T6`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/C8T6) | STM32F103C8T6 传感采集板 | EMG、心率、IMU 等 CAN 传感节点 |
| [`APP`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/APP) | Android App、BLE、界面、传感数据显示 | UI/近端交互参考；不能绕过 M33 直控电机 |
| [`ai`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/ai) | VLA 任务理解原型 | 输出结构化任务，不是真机控制器 |
| [`ROS_VLA_WebSocket`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/ROS_VLA_WebSocket) | 早期 ROS/VLA WebSocket 通信原型 | 历史旁线，不能当当前真机主线 |
| [`NanoPi_ROSNode`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/NanoPi_ROSNode) | 早期 NanoPi ROS2/OpenClaw/HTTP bridge | 可参考，当前主线看 feature 分支 |
| [`PCB`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/PCB) | PCB/结构相关资料 | 资料分支 |

## 安全边界

本项目面向会穿戴在人身上的康复外骨骼机械臂，安全优先级高于演示效果和 AI 能力。

不可违背的原则：

- 默认不动。上电、重启、通信中断、传感异常、轨迹异常或程序异常时，不得继续驱动电机。
- M33 是最终安全责任核心。NanoPi、Linux 工作站、App、VLA、OpenClaw、服务器和 M55 都不能绕过 M33 直接控制电机。
- VLA、语音、M55 小模型和 App 只能产生任务目标、候选轨迹、状态、建议或人工确认请求。
- 急停、限位、限速、限流、heartbeat timeout 和电机故障必须能在 M33 本地独立触发。
- 人在设备内时，不允许使用 NanoPi 直发 CANSimple/private 电机帧做运动控制。
- 新功能进入真机前必须经过仿真、空载台架、低能量受限动作，再进入穿戴测试。

## 系统分层

```text
高层任务层:
  VLA / OpenClaw / App 高层 AI 请求

总控台与研发平台层:
  总服务器 / 多设备管理 / 数据资产 / 模型管理 / 实验追踪 / 远程协作

规划与仿真层:
  Linux 工作站 ROS2 / URDF / MuJoCo / RViz / rosbag / 数据标注

机器人主控与桥接层:
  NanoPi ROS2 / PSoC CAN Bridge / 状态汇总 / 摄像头和服务器上传

实时控制与安全层:
  Infineon M33 / 安全状态机 / 限位 / 急停 / 电机控制

边缘 AI 与信号处理层:
  Infineon M55 / EMG 意图预测 / 疲劳检测 / 语音采集 / XiaoZhi relay

传感与执行层:
  C8T6 传感节点 / 电机驱动 / 编码器 / 限位开关 / 急停硬件
```

## 当前已验证的主线能力

截至 2026-06-10，当前主线可准确描述为：

- `M33/M55/CAN/NanoPi ROS2/无线 MuJoCo shadow` 的基础链路已分层打通。
- M33 状态帧 `0x322`、电机槽位帧 `0x330~0x334`、M55 结果帧 `0x323` 已在 NanoPi CAN 上验证。
- M33 数据进入 M55 小模型，再经 M33 `0x323` 到 NanoPi `/rehab_arm/model_state` 的闭环已通过 `req_snap` 验证。
- MuJoCo 6DOF hardware shadow 已能跟随 NanoPi 上来的真实/占位 joint 状态。
- M55 Wi-Fi、LVGL、XiaoZhi token 配置和语音/WebSocket 适配正在沿官方 local voice/XiaoZhi 路线推进。
- M55 LVGL 触屏 WiFi 配网页已完成扫描、选网、密码输入、保存/连接的可用里程碑；下一步是 WiFi 获得 IP 后联调小智/服务器连接。

当前不能夸大的内容：

- 完整 6DOF 真机闭环控制还没有完成。
- 真实 4 路 EMG 小模型还没有完成产品级训练和验证。
- VLA 还不能安全控制真机，只能产生高层任务或 dry-run 候选。
- 7 号 EL05 是外部台架调试电机，不是正式机械臂关节。
- App、服务器、M55 confidence、语音文本或 VLA 输出都不是运动许可。

## 主线和旁线分类

后续开发、AI 协作和文档更新必须先判断入口属于哪一类：

| 类型 | 含义 | 能否影响真实运动 |
|---|---|---|
| `mainline` | 正式真机链路，最终到 M33 安全裁决 | 可以，但必须经过 M33 |
| `shadow-sim` | MuJoCo/RViz/无线 ROS2 状态影子 | 不可以 |
| `dry-run` | 轨迹候选、仿真审核、operator review 前准备 | 不可以 |
| `bench-debug` | 台架电机、直发 CAN、诊断脚本 | 不可以用于穿戴场景 |
| `offline-demo` | 历史 demo、合成数据、topic smoke | 不可以 |
| `side-channel` | M55、BLE、服务器同步、语音/模型建议 | 不可以单独授权运动 |

任何包含 `demo`、`smoke`、`synthetic`、`bench`、`fallback` 的入口，默认不属于真机主线。

## 当前真实 CAN 和 ROS 边界

正式 NanoPi -> M33 桥接协议：

| ID/topic | 方向 | 作用 |
|---|---|---|
| CAN `0x320` | NanoPi -> M33 | 关节目标/轨迹片段请求 |
| CAN `0x321` | NanoPi -> M33 | NanoPi heartbeat |
| CAN `0x322` | M33 -> NanoPi | M33 状态、安全和 heartbeat 回复 |
| CAN `0x323` | M33 -> NanoPi | M55 模型/语音/建议结果摘要，只是建议 |
| CAN `0x330~0x334` | M33 -> NanoPi | 电机槽位/状态摘要 |
| CAN `0x7C2` | C8T6 -> M33 | 传感数据 |
| CAN `0x7C3` | C8T6 -> M33 | C8T6 健康状态 |
| `/joint_states` | NanoPi/仿真 | 输出端 joint 状态 |
| `/rehab_arm/model_state` | NanoPi | M55 编号结果语义化，只作上下文 |
| `/rehab_arm/safety_state` | NanoPi/M33 bridge | 安全状态展示和审核依据 |
| `/arm_controller/joint_trajectory` | planner/dry-run | 标准轨迹候选，进入 NanoPi/M33 gate |

## 被降级或不能再当主线的内容

- 旧 OpenClaw HTTP 直控 PSoC/电机方案不能作为正式运动路径。
- `ROS_VLA_WebSocket` 早期服务器不能证明 VLA 已经能控制真机。
- `ai` 分支当前是规则版任务理解原型，不是控制器。
- `demo_trajectory_node.py` 和 `vla_task_planner_node.py` 只能做 topic/demo 验证，不能当 6DOF 真机 planner。
- 旧 5 关节 demo 和新 6 关节 medical arm schema 不能直接混接。
- 7 号 EL05 只能作为外部台架调试电机，不进入患者 profile、VLA 真机决策或正式 6DOF 映射。
- CH340/SLCAN USB-CAN 路径未被证明真实收发，不能把本地 TX echo 当 CAN bus 验证通过。
- 旧 `wake_word_detector` 路线已降级为诊断/fallback；语音/wake 主线优先按 Infineon 官方 local voice / XiaoZhi 适配推进。

## 推荐阅读顺序

1. 当前总览：[`docs/CURRENT_PROJECT_BRIEFING.md`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/blob/feature/rehab-arm-ros2-architecture/docs/CURRENT_PROJECT_BRIEFING.md)
2. 系统架构：[`docs/REHAB_ARM_SYSTEM_ARCHITECTURE.md`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/blob/feature/rehab-arm-ros2-architecture/docs/REHAB_ARM_SYSTEM_ARCHITECTURE.md)
3. 服务器/App/VLA 协议：[`docs/COMMAND_CENTER_APP_PROTOCOL_V1.md`](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/blob/feature/rehab-arm-ros2-architecture/docs/COMMAND_CENTER_APP_PROTOCOL_V1.md)
4. M33 固件：[`M33` 分支](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/M33)
5. M55 固件：[`M55` 分支](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/M55)
6. NanoPi/CAN：[`nanopi-sdk` 分支](https://github.com/ChillAmnesiac/Medical-Rehabilitation-Manipulator/tree/nanopi-sdk)

后续如果发现旧 README、旧文档或旧 demo 与本 README 冲突，默认按本 README 和 `feature/rehab-arm-ros2-architecture` 分支处理。
