# User Manual

## VLA Vision Dataset And Model

Current custom detector classes:

```text
0 end_effector
1 gripper_tip
```

Bottle/cup detection is still handled by the existing general detector path for now.

Convert AnyLabeling JSON to YOLO:

```powershell
cd D:\medical-rehab-manipulator-product
python scripts\prepare_yolo_dataset.py `
  --images D:\vla_dataset\20260627_213112\images\mono `
  --out D:\vla_dataset\20260627_213112\yolo_end_effector_v1_with_negatives `
  --classes end_effector,gripper_tip `
  --val-ratio 0.2 `
  --include-unlabeled-images
```

Train on CPU:

```powershell
D:\tools\yolo-train-venv\Scripts\yolo.exe detect train `
  model=yolov8n.pt `
  data=D:\vla_dataset\20260627_213112\yolo_end_effector_v1_with_negatives\data.yaml `
  epochs=10 imgsz=416 batch=8 device=cpu workers=0 `
  project=D:\vla_dataset\20260627_213112\runs `
  name=end_effector_v1_cpu_416_e10 `
  exist_ok=True
```

Export ONNX for future C++/NanoPi inference:

```powershell
D:\tools\yolo-train-venv\Scripts\yolo.exe export `
  model=D:\vla_dataset\20260627_213112\runs\end_effector_v1_cpu_416_e10\weights\best.pt `
  format=onnx imgsz=416 simplify=True opset=12
```

Save real prediction images:

```powershell
D:\tools\yolo-train-venv\Scripts\yolo.exe predict `
  model=D:\vla_dataset\20260627_213112\runs\end_effector_v1_cpu_416_e10\weights\best.pt `
  source=D:\vla_dataset\20260627_213112\images\mono `
  imgsz=416 conf=0.35 save=True save_txt=True save_conf=True `
  project=D:\vla_dataset\20260627_213112\runs `
  name=end_effector_v1_predict_pt_416_conf035 `
  exist_ok=True
```

Build a dry-run VLA visual observation:

```powershell
python scripts\build_vla_visual_observation.py `
  --labels D:\vla_dataset\20260627_213112\runs\end_effector_v1_predict_pt_416_conf035\labels\mono_000003.txt `
  --frame-size 640x480 `
  --frame-id mono_000003 `
  --target-label bottle `
  --target-bbox 360,180,80,180,0.88 `
  --out D:\vla_dataset\20260627_213112\runs\end_effector_v1_predict_pt_416_conf035\mono_000003_vla_observation.json
```

Safety boundary:

- The visual observation JSON is display/planning context only.
- It must not bypass `vla_system`, `rehab_task_manager`, `safety_supervisor`, or M33.
- Real motion remains disabled until the M33 safety chain and low-energy bench tests are proven.
