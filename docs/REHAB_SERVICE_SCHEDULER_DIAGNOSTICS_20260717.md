# rehab_svc 调度诊断实现与验证记录

日期：2026-07-17

## 目的

助力模式没有输出时，不能仅凭现象判断 `rehab_svc` 被饿死。本步骤只增加三个只读指标，不改变线程优先级、20 ms delay、模式状态机、电机协议或电流算法：

- `cycles`：worker 进入主循环的累计次数，`uint32_t` 自然回绕。
- `last_tick`：worker 最近一次进入主循环的 RT-Thread tick。
- `max_jitter_ms`：相邻两次循环间隔相对目标周期的最大绝对偏差。

## 实现边界

`rehab_worker_timing` 是不访问设备的纯计算模块。`rehab_service_worker()` 在每轮入口读取一次 `rt_tick_get()`，然后在原有 `s_rehab.lock` 下更新诊断并复制到 `rehab_service_status_t`。worker 内不打印日志；Shell 通过已有的 `rehab_service_get_status()` 快照输出。

tick 间隔使用无符号减法：

```c
elapsed_ticks = now - last_tick;
```

因此 32 位 tick 从 `UINT32_MAX` 回绕到零时仍能得到正确的小间隔。首轮只建立基线，最大 jitter 保持零。

## 自动验证

Host 测试覆盖：

1. 首轮建立基线。
2. 20 ms 正常周期。
3. 提前和延迟周期只保留历史最大 jitter。
4. 32 位 tick 回绕。

```powershell
rtk gcc -std=c11 -Wall -Wextra -Werror `
  -Itests\host -Iapplications\control `
  tests\host\rehab_worker_timing_test.c `
  applications\control\rehab_worker_timing.c `
  -o tmp\rehab_worker_timing_test.exe
rtk .\tmp\rehab_worker_timing_test.exe
```

结果：`rehab_worker_timing_test PASS`。

M33 完整构建命令：

```powershell
$env:RTT_EXEC_PATH='F:\RT-ThreadStudio\platform\env_released\env-new\tools\gnu_gcc\arm_gcc\mingw\bin'
rtk F:\RT-ThreadStudio\platform\env_released\env-new\.venv\Scripts\scons.exe -j8
```

结果：SCons exit code 0，生成 `build/rtthread.hex`，并完成 `0x08340400 -> 0x60340400` relocation。构建日志确认 `rehab_worker_timing.o` 被编译。

本次未烧录构建产物：

```text
rt-thread.elf       SHA-256 9FE3D602939810FA888DF59CCDEEA6400FDC3681CA13C3E49192F5E27166485B
build/rtthread.hex  SHA-256 8F9EAC589D8DB33032D7316AF5FAC8986E1455638FA04708249DB36955F82674
```

这些 hash 对应当时整个工作区构建状态，其中包含用户已有但未提交的其他源码修改；它们只用于后续板端故障与 ELF/HEX 精确对应，不代表工作区其他改动属于本提交。

工程仍存在本步骤之前已有的编译警告，例如 BLE API 隐式声明和 `control_layer.c` 未使用符号。本提交不顺手修改这些警告，避免扩大回归范围。

## 板端验证

本提交尚未烧录。烧录后先不要进入运动模式，连续执行：

```text
rehab status
rehab status
ps
free
```

预期：

- 第二次 `cycles` 大于第一次。
- `last_tick` 更新。
- `max_jitter_ms` 为历史最大值，因此只增不减；它不是当前周期 jitter。
- `rehab_sv` 栈占用没有明显增加。
- CAN、F103 和 M55 IPC 基线不变。

确认诊断正常后，才按空载台架步骤执行 `rehab assist 5`。本诊断提交本身不证明助力电流已经输出。
