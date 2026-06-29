# Troubleshooting And Lessons

## 2026-06-27 - Stereo VLA dataset capture boundary

Environment:

- NanoPi ROS camera branch `NanoPi_ROSNode`.
- Two fixed USB cameras, temporary non-final mounting.

Lesson:

- Keep dataset capture separate from live WebSocket streaming and robot control. Capture needs metadata, repeated manual/auto shots, negative samples, and labeling guidance; live VLA inference can be optimized later.

Trick:

- Use OpenCV `grab()` on both cameras before `retrieve()` to reduce left/right timestamp skew without adding a complex synchronization layer.
- On Windows, avoid forcing V4L2. Use the script default auto backend or try `--backend msmf` if DirectShow opens slowly or gives black frames.
- On the current Windows PC, external USB stereo cameras appear as OpenCV indexes `2` and `3`; indexes `0` and `1` are not the stereo pair.
- Current status: `index=2` reads frames with DirectShow and can be used for mono detection training. `index=3` is enumerated but OpenCV reads fail, so keep mono capture as the working fallback until the second camera/USB path is fixed.
- Do not assume the USB camera needs `hv` flipping. The current Windows `index=2` image is correct with `flip-left=none`; stale preview windows can make orientation debugging confusing, so stop old capture processes before retesting.

## 2026-06-29 - Annotation format and NanoPi V-side status

Symptoms:

- LabelImg crashed when creating a rectangle on Windows.
- AnyLabeling successfully creates annotations but saves `.json` files beside images by default.
- NanoPi at `192.168.3.36` is reachable, but direct OpenCV reads from current `/dev/video-camera0`, `/dev/video-camera1`, `/dev/video22`, and `/dev/video31` returned no frames.

Environment:

- PC annotation dataset: `D:/vla_dataset/20260627_213112/images/mono`.
- Annotation tool: AnyLabeling `0.4.36`.
- NanoPi: `NanoPi-M5`, Linux `6.1.141`, OpenCV `4.6.0`.

Root cause:

- AnyLabeling JSON is an intermediate annotation format, not YOLO TXT. A conversion step is required before training.
- NanoPi historical stereo capture used `/dev/video45` and `/dev/video47`, but the current boot exposes different camera links and no directly readable frames from the tested nodes.

Fix:

- Use `scripts/prepare_yolo_dataset.py` to convert AnyLabeling rectangle JSON into YOLO labels and dataset folders after annotation is complete.
- Keep NanoPi camera recovery separate from annotation/training and avoid changing CAN/L pathways during V-side diagnosis.

Status:

- Annotation conversion path is ready.
- NanoPi camera runtime capture is unverified on the current boot and needs a focused follow-up.

## 2026-06-29 - CAN check shows no RX and error-passive/down

Symptoms:

- `ip -details -statistics link show can0` showed `state ERROR-PASSIVE`, `berr-counter tx 128 rx 0`, `RX packets=0`, and rapidly increasing `TX errors`.
- `candump -tz -L can0` returned `read: Network is down` after the interface degraded.
- ROS bridge repeatedly logged `safety limited: no PSoC status` and eventually `OSError: [Errno 105] No buffer space available`.
- `/rehab_arm/safety_state` and `/rehab_arm/model_state` were not published.

Environment:

- NanoPi-M5 at `192.168.3.36`.
- MCP2518FD SocketCAN device `can0`, bitrate `1000000`, `restart-ms 100`.
- Active bridge command used `enable_target_tx:=false`, but it still sends heartbeat/status frames.

Root cause:

- Not proven. Because `RX packets=0`, the current failure is not specifically a 3号电机 parsing/control issue. It is a bus/tool-layer failure: no valid received CAN frames are visible to NanoPi.

Likely causes to check:

- CANH/CANL reversed or shorted by the suspect motor.
- Missing common ground or incorrect termination.
- Motor 3 or another device holding the bus dominant/recessive abnormally.
- Bitrate/protocol mismatch.
- MCP2518FD/SPI signal integrity problem, supported by repeated kernel `CRC read error` messages.

Status:

- CAN is currently not healthy enough to verify motor 3. Stop at bus bring-up before any motion or protocol test.

Status:

- Script written and syntax-checked locally. NanoPi hardware run is still unverified.

## 2026-06-30 - VLA visual observation boundary

Environment:

- PC dataset: `D:/vla_dataset/20260627_213112`.
- YOLO environment: `D:/tools/yolo-train-venv`.
- Model: two-class `end_effector` / `gripper_tip` detector.

Lesson:

- Do not fake VLA boxes for demos. Save real detector prediction images and TXT labels, then convert them into a visual observation contract that the UI/orchestrator can display.
- Keep target-object detection and end-effector detection separate until the dataset covers both. The current custom detector should not be stretched to bottle/cup classes it was not trained on.
- The useful VLA display state is not just "object found"; it is target visible, end effector visible, gripper tip visible, and the pixel delta between target and tip.

Trick:

- Export `best.pt` to ONNX immediately after training and run at least one ONNX prediction before planning NanoPi deployment.
- Use `rehab_vla_visual_observation_v1` JSON as the stable bridge between Python training experiments and future C++ inference.

Status:

- PT and ONNX inference both work on the PC.
- Live NanoPi camera inference remains unverified and should be handled as a separate edge deployment task.
