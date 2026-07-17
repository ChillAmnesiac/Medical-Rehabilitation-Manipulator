# M33 助力模式反馈准备修复与实机复盘

日期：2026-07-17

## 1. 现场现象

M33 能接受 `rehab assist 5`，但进入后不输出助力。首次受限烟测把 `assist_max` 临时降到 0.2 A，结果为：

```text
rehab assist ret=0
rehab status mode=assist fresh=0 detail=9 assist=0 last=-116
```

`detail=9` 是 `CONTROL_STATUS_DETAIL_MOTOR_FAULT`，`last=-116` 是 `-RT_ETIMEOUT`。安全 STOP 成功，测试没有产生电流。

## 2. 根因

助力 worker 在调用 `control_motor_current_control()` 前，要求目标电机存在 100 ms 内的新鲜反馈。私有协议电机上电后未必主动上报，而 `control_motor_set_active_report()` 原来只由 Shell 或特定命令调用。

这形成了启动依赖死锁：

```text
未开启主动上报
  -> 反馈缓存过期
  -> rehab worker 拒绝进入电流控制
  -> control_motor_current_control() 中的电机 enable 永远不会执行
```

现场执行 `cmd_motor_report 5 1` 后，`rx_total` 快速增长，电机反馈时间戳持续更新；再次执行助力烟测即可达到 `fresh=1 detail=0 assist=1`，证明算法和限流路径本身可工作。

## 3. 修复

提交：`092e05670 fix(rehab): prepare motor feedback before assist`

单关节活动模式进入前现在会：

1. 调用 `control_motor_set_active_report(m33_joint_id, RT_TRUE)`。
2. 最多等待 300 ms。
3. 只有检测到 100 ms 内的新鲜反馈，才提交 ACTIVE、ASSIST 或 RESIST 状态转换。
4. 上报请求失败或等待超时则返回错误，保持原模式，不下发电流。

该等待发生在取得 `actuation_lock` 之前，不会在等待 CAN 首帧时长期占用执行锁。

## 4. 自动验证

测试遵循先失败、后实现的顺序：

```powershell
rtk python tools/test_rehab_service_actuation_static.py
```

结果：4 项通过。完整 SCons 构建通过，生成新的 `build/rtthread.hex`。构建仍有工程原有的 CAN、BLE 和 main 警告，本次新增代码没有产生新警告。

`tools/test_rehab_mode_static.py` 当前被工作区已有 `main.c` 配置差异阻断：测试要求 `M33_XIAOZHI_MINIMAL_FRAMEWORK 1`，当前文件没有该宏。本次没有修改这部分用户代码。

## 5. 复位后实机验证

新镜像通过 verified flash 流程完成编程、原始地址校验和 XIP 地址校验。复位会清除之前手动开启的主动上报，因此烧录后没有执行 `cmd_motor_report 5 1`，直接运行 0.2 A 助力烟测。

关键结果：

```text
rehab assist ret=0
rehab status mode=assist fresh=1 detail=0 assist=1 limit_x1000=200 last=0
MOTOR[5]: mode=2 fault=0x00
rehab stop ret=0
rehab status mode=passive detail=0 last=0
```

本次关节基本静止，扭矩和速度在策略触发阈值附近，因此观测电流为 0 A；它证明反馈准备和模式进入已恢复，但不能替代操作者手动施力时的助力方向、幅值和连续运行测试。STOP 后运行参数已恢复为 `assist_max=1.0 A`。

## 6. 剩余范围

本提交只修复 `rehab_service_enter_mode_on_m33()` 的单关节入口。NanoPi/CAN 使用多关节 mask 时走 `rehab_service_set_mode_mask()`，仍需以独立小提交加入逐关节反馈准备和全失败回滚，避免扩大本次改动范围。
