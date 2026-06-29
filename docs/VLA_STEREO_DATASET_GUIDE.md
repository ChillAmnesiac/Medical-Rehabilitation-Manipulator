# VLA 双目采集与标注指南

这一步只做视觉数据闭环：采集双目图像、人工标注目标和机械臂末端，后面再训练检测模型。它不连接 CAN，不控制电机，也不影响 XiaoZhi 的 L 链路。

## 摄像头摆放

- 两个 USB 摄像头固定在同一水平线上，镜头光轴尽量平行。
- 左右基线先按实测 `0.06 m` 记录，脚本默认就是 6 cm。
- 两个摄像头都要看到桌面目标和机械臂末端，目标最好出现在画面中间 60% 区域。
- 采集期间不要手持摄像头；只移动杯子、瓶子、末端和光照。

## Windows 电脑运行采集

你现在也可以把两个 USB 摄像头接到自己的 Windows 电脑上运行脚本。先安装依赖：

```powershell
pip install opencv-python
```

进入仓库：

```powershell
cd D:\medical-rehab-manipulator-product
```

先扫描摄像头编号：

```powershell
python scripts\collect_stereo_dataset.py --list-cameras
```

当前这台电脑已经识别到：

- `0`: 笔记本内置摄像头。
- `1`: 虚拟/占位摄像头画面。
- `2` 和 `3`: 外接双目摄像头。

当前 Windows 上 `index=2` 的外接摄像头可以稳定读取，`index=3` 能被系统枚举但 OpenCV 暂时读不到帧。先用单摄训练目标和末端检测，脚本已经默认配置成 `mode=mono`、`camera=2`、`DirectShow`、`none` 不翻转。直接运行即可：

```powershell
python scripts\collect_stereo_dataset.py
```

也可以运行一键脚本：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_windows_stereo_capture.ps1
```

窗口弹出后：

- `Space`: 保存当前左右图一对。
- `a`: 开关自动连拍。
- `q`: 退出。

如果打开慢或黑屏，可以换 Windows 后端：

```powershell
python scripts\collect_stereo_dataset.py --list-cameras --backend msmf
python scripts\collect_stereo_dataset.py --backend msmf
```

如果你重新插拔后编号变了，按扫描结果手动指定：

```powershell
python scripts\collect_stereo_dataset.py --mode mono --camera 2 --flip-left none --out D:\vla_dataset
```

后面右摄恢复后，再切回双目：

```powershell
python scripts\collect_stereo_dataset.py --mode stereo --left 2 --right 3 --flip-left hv --flip-right hv --out D:\vla_dataset
```

## NanoPi 运行采集

先确认设备号：

```bash
ls /dev/video*
v4l2-ctl --list-devices
```

在 NanoPi 仓库根目录运行：

```bash
python3 scripts/collect_stereo_dataset.py --left 0 --right 1 --out datasets/vla_stereo --baseline-m 0.06 --flip-left none --flip-right none
```

如果摄像头画面方向仍然反了，可以加翻转：

```bash
python3 scripts/collect_stereo_dataset.py --left 0 --right 1 --flip-left h --flip-right h
```

无显示器或 SSH 采集 60 组：

```bash
python3 scripts/collect_stereo_dataset.py --left 0 --right 1 --headless --count 60 --interval-ms 700
```

交互按键：

- `Space`: 保存当前左右图一对。
- `a`: 开关自动连拍。
- `q`: 退出。

输出目录示例：

```text
datasets/vla_stereo/20260627_153000/
  images/mono/mono_000001.jpg
  images/left/left_000001.jpg
  images/right/right_000001.jpg
  meta/frames.jsonl
  labels/README_LABELING.md
  phone_images/
```

`datasets/` 是采集产物目录，建议不要提交到 Git。需要给我训练时，可以打包对应 session。

## 标注类别

先只标 4 个类，越少越稳定：

| 类名 | 含义 |
|---|---|
| `target_cup` | 要拿的水杯 |
| `target_bottle` | 要拿的瓶子 |
| `end_effector` | 可见的机械臂末端整体 |
| `gripper_tip` | 真正接触目标的夹爪尖/末端点 |

左右图都要标，类别名必须一致。只框真实可见的像素，不要凭感觉补全被挡住的部分。

## 先拍什么最有价值

每个场景都尽量左右图同步保存：

- 目标和末端同时出现：至少 80 对。
- 只有水杯/瓶子：至少 40 对。
- 只有末端：至少 40 对。
- 什么目标都没有：至少 40 对。
- 目标在近、中、远三个距离，各拍一批。
- 目标在左、中、右位置，各拍一批。
- 加一些遮挡、桌面杂物、不同光照。

这对简易 VLA 很关键：模型不仅要知道“杯子在哪”，还要知道“末端在哪”，后面才能做视觉伺服式逼近。

## 手机照片怎么用

手机拍照可以补充泛化能力，但它没有双目几何。建议把手机照片放在同一 session 的 `phone_images/`，只用于训练检测类别外观，不用于深度或三维坐标验证。

手机补拍建议：

- 多拍不同水杯、瓶子、背景和光照。
- 末端特写也拍一些，尤其是夹爪尖。
- 不要只拍漂亮正面图，歪角度和半遮挡更有用。

## 下一步训练思路

1. 用 LabelImg、CVAT 或 Roboflow 标注左右图。
2. 导出 YOLO 格式。
3. 先训练轻量 YOLO 检测 `target_*` 和 `end_effector/gripper_tip`。
4. 双目未标定前，先用左右框中心差做粗略视差和视觉锁定演示。
5. 完成棋盘格标定后，再把像素坐标转成相机坐标系。
6. 完成手眼/坐标系标定后，再把相机坐标系转机械臂坐标系。

真机运动仍然必须保持 dry-run，直到 M33 安全裁决链路和低能量台架验证都完成。
