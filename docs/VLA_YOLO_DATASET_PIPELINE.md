# VLA YOLO Dataset Pipeline

当前标注工具 AnyLabeling 会先保存 `.json` 工程标注文件。训练 YOLO 前，需要把这些 `.json` 转成 YOLO `.txt`。

## 类别顺序

YOLO 类别 id 固定如下：

| id | class |
|---:|---|
| 0 | `target_cup` |
| 1 | `target_bottle` |
| 2 | `end_effector` |
| 3 | `gripper_tip` |

标注时类别名必须完全一致。

## 转换命令

标完一批后运行：

```powershell
cd D:\medical-rehab-manipulator-product
python scripts\prepare_yolo_dataset.py `
  --images D:\vla_dataset\20260627_213112\images\mono `
  --out D:\vla_dataset\20260627_213112\yolo `
  --val-ratio 0.2
```

输出结构：

```text
D:\vla_dataset\20260627_213112\yolo\
  data.yaml
  conversion_report.json
  images\train\
  images\val\
  labels\train\
  labels\val\
```

如果需要把没有标注框的图片也作为负样本加入训练：

```powershell
python scripts\prepare_yolo_dataset.py `
  --images D:\vla_dataset\20260627_213112\images\mono `
  --out D:\vla_dataset\20260627_213112\yolo_with_negatives `
  --val-ratio 0.2 `
  --include-unlabeled-images
```

## 训练前检查

- `conversion_report.json` 里的 `boxes_written` 不能为 0。
- `skipped_unknown_label` 应该为 0，否则说明类别名打错。
- `labels/train/*.txt` 每行应为 5 列：`class_id x_center y_center width height`。
- 坐标都是 0 到 1 之间的小数，这才是 YOLO 格式。

## NanoPi 当前 V 状态

- 当前 NanoPi: `192.168.3.36`, host `NanoPi-M5`.
- 历史 C++ 双目 VLA 上传链路位置: `/home/pi/nanopi_stereo_vla_upload_loop.sh`.
- 历史链路使用 `/dev/video45` 和 `/dev/video47`，并已经在 `/home/pi/rehab_arm_stereo_frames` 产生过左右图。
- 当前上电状态下，系统只看到 `/dev/video-camera0 -> /dev/video22` 和 `/dev/video-camera1 -> /dev/video31`，OpenCV 暂时读不到实时帧。
- 当前继续以 PC 单摄数据标注/训练为主，NanoPi 摄像头恢复后再回到边缘部署。

## 当前末端模型数据集

本轮标注只包含：

| id | class |
|---:|---|
| 0 | `end_effector` |
| 1 | `gripper_tip` |

转换命令：

```powershell
python scripts\prepare_yolo_dataset.py `
  --images D:\vla_dataset\20260627_213112\images\mono `
  --out D:\vla_dataset\20260627_213112\yolo_end_effector_v1_with_negatives `
  --classes end_effector,gripper_tip `
  --val-ratio 0.2 `
  --include-unlabeled-images
```

瓶子/水杯先继续使用已有通用 COCO/YOLOX 检测器，例如 `bottle` 类；不要混入本轮末端专用模型。

已验证烟测模型：

```text
D:\vla_dataset\20260627_213112\runs\end_effector_smoke\weights\best.pt
```

1 epoch CPU smoke 指标：

```text
precision=0.68089
recall=0.654
mAP50=0.74162
mAP50-95=0.32407
```

这只是链路烟测，预测图里仍有重复框和低置信度框。正式模型需要更长训练，并在导出 ONNX 后接入 C++/NanoPi 推理。

## v1 正式末端模型

正式 CPU 训练命令：

```powershell
D:\tools\yolo-train-venv\Scripts\yolo.exe detect train `
  model=yolov8n.pt `
  data=D:\vla_dataset\20260627_213112\yolo_end_effector_v1_with_negatives\data.yaml `
  epochs=10 imgsz=416 batch=8 device=cpu workers=0 `
  project=D:\vla_dataset\20260627_213112\runs `
  name=end_effector_v1_cpu_416_e10 `
  exist_ok=True
```

产物：

```text
D:\vla_dataset\20260627_213112\runs\end_effector_v1_cpu_416_e10\weights\best.pt
D:\vla_dataset\20260627_213112\runs\end_effector_v1_cpu_416_e10\weights\best.onnx
```

最终指标：

```text
all: precision=0.957, recall=0.937, mAP50=0.970, mAP50-95=0.556
end_effector: mAP50=0.984
gripper_tip: mAP50=0.957
```

导出 ONNX：

```powershell
D:\tools\yolo-train-venv\Scripts\yolo.exe export `
  model=D:\vla_dataset\20260627_213112\runs\end_effector_v1_cpu_416_e10\weights\best.pt `
  format=onnx imgsz=416 simplify=True opset=12
```

保存真实预测图和标签：

```powershell
D:\tools\yolo-train-venv\Scripts\yolo.exe predict `
  model=D:\vla_dataset\20260627_213112\runs\end_effector_v1_cpu_416_e10\weights\best.pt `
  source=D:\vla_dataset\20260627_213112\images\mono `
  imgsz=416 conf=0.35 save=True save_txt=True save_conf=True `
  project=D:\vla_dataset\20260627_213112\runs `
  name=end_effector_v1_predict_pt_416_conf035 `
  exist_ok=True
```

预测图目录：

```text
D:\vla_dataset\20260627_213112\runs\end_effector_v1_predict_pt_416_conf035
```

## VLA 视觉观测 JSON

目标物例如 `bottle` 先来自通用检测器，末端/夹爪来自本模型。两者合并后才形成 VLA 的 V 观测：

```powershell
python scripts\build_vla_visual_observation.py `
  --labels D:\vla_dataset\20260627_213112\runs\end_effector_v1_predict_pt_416_conf035\labels\mono_000003.txt `
  --frame-size 640x480 `
  --frame-id mono_000003 `
  --target-label bottle `
  --target-bbox 360,180,80,180,0.88 `
  --out D:\vla_dataset\20260627_213112\runs\end_effector_v1_predict_pt_416_conf035\mono_000003_vla_observation.json
```

输出重点字段：

```json
{
  "schema_version": "rehab_vla_visual_observation_v1",
  "control_boundary": "dry_run_not_motion_permission",
  "target_object": {"label": "bottle", "center_px": [400.0, 270.0]},
  "gripper_tip": {"label": "gripper_tip", "center_px": [209.96, 138.98]},
  "pixel_servo_hint": {"dx_px": 190.04, "dy_px": 131.02}
}
```

这一步仍然只是 dry-run 观测，不允许直接控制电机。
