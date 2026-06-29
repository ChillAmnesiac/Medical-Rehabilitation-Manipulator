# Project Progress

## 2026-06-27

Completed:

- Added `scripts/collect_stereo_dataset.py` on `NanoPi_ROSNode` for stereo USB camera dataset capture.
- Added `docs/VLA_STEREO_DATASET_GUIDE.md` covering camera placement, capture commands, labels, phone-photo use, and the next training path.
- Dataset script writes left/right JPEGs plus `meta/frames.jsonl`, records the 0.06 m baseline, and creates per-session labeling guidance.
- Updated the script to run on both NanoPi/Linux and Windows PCs, including `--list-cameras` probing and selectable OpenCV backends.
- Configured the current Windows PC defaults for the external stereo pair: camera index `2` as left, `3` as right, both flipped `hv`, output root `D:/vla_dataset`.
- Added `scripts/start_windows_stereo_capture.ps1` as the one-command Windows preview/capture launcher.
- Added automatic backend fallback for Windows camera opening: DirectShow, MSMF, then OpenCV `CAP_ANY`.
- Changed the Windows default backend to `CAP_ANY` and moved session creation after the first successful stereo frame so failed camera opens do not create empty dataset sessions.
- Added `--mode mono` as the default capture path because the current Windows setup reads external camera index `2` but not index `3`.
- Set the Windows mono default backend to DirectShow after `camera=2 + backend=dshow` saved a verified frame.
- Updated mono camera orientation to `flip-left=none` after a four-way flip probe showed the raw frame is already upright.
- Added initial `src/rehab_vla_orchestrator` dry-run mode/action-plan package and then reviewed GitHub history to bound it as a temporary thin adapter rather than a new product spine.
- Added `docs/REHAB_ARM_CLOSED_LOOP_ARCHITECTURE.md` and `docs/GITHUB_HISTORY_REVIEW_2026_06_29.md`.
- Added `docs/ADDITIVE_CLOSED_LOOP_INTEGRATION_PLAN.md` to enforce add-only integration and prevent replacing existing branch functions.

Validated:

- Python syntax check passed locally with `python -m py_compile scripts/collect_stereo_dataset.py`.
- CLI help passed locally with `python scripts/collect_stereo_dataset.py --help`.
- Windows camera probe identified indexes `2` and `3` as the external pair; `0` is the integrated camera and `1` is a virtual/placeholder feed.
- Single-camera probe verified `index=2 + dshow` saved `D:/vla_dataset_test/mono_one_shot_dshow/images/mono/mono_000001.jpg`. Index `3` opens but currently returns no frames through OpenCV/MSMF.
- Git history review found `product-main` already owns the intended spine: `vla_system -> rehab_task_manager -> safety_supervisor -> /can_tx`.
- Orchestrator smoke test passed locally with fetch, visual-servo, training, EMG-assist, and chat-only cases.

Decisions:

- Data capture stays separate from the existing C++ WebSocket camera stream.
- This task does not touch XiaoZhi/L, CAN, M33/M55, or any real motion path.
- Future real-time detection should move performance-sensitive loops to C++ after the dataset and model target are stable.
- Closed-loop extensions must align with `product-main`; do not create a second motion authority around `rehab_task_manager` or `safety_supervisor`.
- Current temporary orchestrator package is not a replacement for existing features; it is only additive scaffolding for the current branch.

Next step:

- Run the script on NanoPi with the actual two USB camera device IDs and collect the first target/end-effector dataset.

## 2026-06-29

Completed:

- Installed and used AnyLabeling/X-AnyLabeling as the newer local annotation tool after LabelImg crashed on rectangle creation.
- Confirmed current AnyLabeling annotations are JSON project files, not YOLO TXT yet.
- Added `scripts/prepare_yolo_dataset.py` to convert AnyLabeling rectangle JSON annotations into YOLO train/val folders and `data.yaml`.
- Added `docs/VLA_YOLO_DATASET_PIPELINE.md` with the JSON-to-YOLO workflow and class-id mapping.
- Reconnected to NanoPi at `192.168.3.36` (`NanoPi-M5`) with `pi/pi` and checked V-side status without touching L, CAN commands, or motion.

Validated:

- Current labeled files under `D:/vla_dataset/20260627_213112/images/mono` are AnyLabeling JSON with rectangle shapes and labels such as `end_effector`.
- NanoPi SSH works on `192.168.3.36`; OpenCV 4.6.0 is installed.
- NanoPi currently exposes `/dev/video-camera0 -> /dev/video22` and `/dev/video-camera1 -> /dev/video31`, but direct OpenCV reads did not return frames.
- Historical NanoPi VLA upload logs and stereo frames exist under `/home/pi/rehab_arm_vla_logs` and `/home/pi/rehab_arm_stereo_frames`, produced by `/home/pi/nanopi_stereo_vla_upload_loop.sh`.

Decisions:

- Continue annotation/training from the PC mono dataset while the user labels.
- Keep NanoPi camera recovery as a separate V-side hardware/software task; do not disturb the active ROS CAN bridge or L/XiaoZhi path.

Next step:

- After the user finishes labeling, run `scripts/prepare_yolo_dataset.py` on the completed AnyLabeling JSON set, inspect `conversion_report.json`, then start YOLO training.

## 2026-06-29 CAN Check

Completed:

- Checked NanoPi CAN status on `192.168.3.36` with focus on whether motor/node 3 can be observed.
- Used read-only status/log commands plus `candump`; no motor control frames were intentionally sent.

Validated:

- `can0` exists on MCP2518FD/SPI and is configured at `1000000` bitrate.
- `can0` state was `ERROR-PASSIVE` with `berr-counter tx 128 rx 0`.
- SocketCAN counters showed `RX packets=0` and rapidly increasing `TX errors` over 1M.
- `candump can0` failed with `read: Network is down` after the interface fell from `ERROR-PASSIVE` toward stopped/down.
- ROS topics `/rehab_arm/safety_state` and `/rehab_arm/model_state` were not published.
- Bridge journal reported repeated `safety limited: no PSoC status` and `OSError: [Errno 105] No buffer space available`.

Decision:

- Current CAN bus is not healthy enough to prove 3号电机 connectivity. Since there is no RX traffic at all, the issue is below motor-3 protocol level: physical bus, termination/power/common ground, bitrate/protocol mismatch, transceiver state, or the bad motor dragging the bus.

Next step:

- With motor 3 powered as the target condition, verify physical voltages, termination, and whether any independent CAN observer sees frames before attempting any 3号电机 command.

## 2026-06-29 End-Effector Dataset And Smoke Training

Completed:

- Confirmed the completed annotation batch only targets `end_effector` and `gripper_tip`.
- Converted AnyLabeling JSON annotations into YOLO datasets:
  - `D:/vla_dataset/20260627_213112/yolo_end_effector_v1`
  - `D:/vla_dataset/20260627_213112/yolo_end_effector_v1_with_negatives`
- Installed YOLO training environment at `D:/tools/yolo-train-venv`.
- Ran a 1-epoch CPU smoke training for the end-effector model.

Validated:

- Source images: `1212`.
- JSON annotations: `1143`.
- YOLO images/labels written with negatives: `1212`.
- Valid boxes written: `2216`.
- Class counts from raw JSON: `end_effector=1139`, `gripper_tip=1077`.
- Found 13 accidental `d` labels; they were skipped during conversion and source JSON was not modified.
- Smoke training produced weights at `D:/vla_dataset/20260627_213112/runs/end_effector_smoke/weights/best.pt`.
- Smoke metrics after 1 epoch: precision `0.68089`, recall `0.654`, mAP50 `0.74162`, mAP50-95 `0.32407`.

Decisions:

- Bottle/cup detection will continue using the previous general COCO/YOLOX detector for now.
- The new custom detector is scoped to `end_effector` and `gripper_tip` only.

Next step:

- Run longer training for the two-class end-effector detector, then export to ONNX for C++/NanoPi inference.

## 2026-06-30 End-Effector Detector V1 And Visual Observation Contract

Completed:

- Ran formal CPU training for the two-class `end_effector` / `gripper_tip` detector.
- Exported the trained detector to ONNX for the future C++/NanoPi inference path.
- Ran full-dataset prediction to save real detector boxes and YOLO TXT outputs.
- Added `scripts/build_vla_visual_observation.py` to convert detector labels plus an optional target bbox into a dry-run VLA visual observation JSON.
- Added unit tests for YOLO label parsing, pixel-space conversion, and pixel-servo hint generation.
- Added `docs/USER_MANUAL.md` with the current V-side dataset, training, export, prediction, and observation commands.

Validated:

- Formal weights:
  - `D:/vla_dataset/20260627_213112/runs/end_effector_v1_cpu_416_e10/weights/best.pt`
  - `D:/vla_dataset/20260627_213112/runs/end_effector_v1_cpu_416_e10/weights/best.onnx`
- Final v1 metrics: precision `0.957`, recall `0.937`, mAP50 `0.970`, mAP50-95 `0.556`.
- Per-class mAP50: `end_effector=0.984`, `gripper_tip=0.957`.
- PyTorch full-dataset prediction saved to `D:/vla_dataset/20260627_213112/runs/end_effector_v1_predict_pt_416_conf035`; 1164 label files were produced from 1212 images.
- ONNX single-image prediction on `mono_000003.jpg` detected both `end_effector` and `gripper_tip`.
- Observation example saved to `D:/vla_dataset/20260627_213112/runs/end_effector_v1_predict_pt_416_conf035/mono_000003_vla_observation.json`.
- `python -m unittest tests.test_build_vla_visual_observation` passed.
- `python -m py_compile scripts/build_vla_visual_observation.py` passed.

Decisions:

- Keep the custom model scoped to `end_effector` and `gripper_tip`.
- Keep bottle/cup detection as a separate general detector input for now.
- The visual observation contract is dry-run only and may feed display/orchestrator logic; it must not bypass `vla_system`, `rehab_task_manager`, `safety_supervisor`, or M33 safety authority.
- Performance-sensitive live inference should move to C++/ONNX/OpenCV DNN or ONNX Runtime after this offline contract is stable.

Next step:

- Build the C++ edge inference prototype that consumes camera frames and emits the same `rehab_vla_visual_observation_v1` JSON without replacing the existing `camera_client`.
