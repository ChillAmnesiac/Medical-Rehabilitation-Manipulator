# GitHub History Review - 2026-06-29

Purpose: prevent the closed-loop work from creating a second, messy architecture.

## Branches Reviewed

- `NanoPi_ROSNode`: current working branch; early ROS2 workspace with camera client and HTTP bridge.
- `product-main`: product integration spine.
- `origin/ai`: VLA rule-based system imported later into `product-main`.
- `origin/ROS_VLA_WebSocket`: legacy web socket prototype; reference only.
- `origin/M33`, `origin/M55`, `origin/C8T6`, `origin/nanopi-sdk`: firmware and board-specific assets.

## Key Finding

`product-main` already defines the product-level loop architecture:

```text
HTTP/app/speech
  -> /speech/text
  -> vla_system / vla_bridge
  -> /task/resolved
  -> rehab_task_manager
  -> /rehab/task_intent
  -> /safety/command_request
  -> safety_supervisor
  -> /safety/command_approved
  -> /can_tx
```

Therefore, new closed-loop work must extend this spine. It should not create a new authority path around `rehab_task_manager` or `safety_supervisor`.

## Current Additions Assessment

The new `src/rehab_vla_orchestrator` package is acceptable only as a temporary thin adapter on the current `NanoPi_ROSNode` branch, because this branch does not contain the `product-main` integration packages.

Keep it scoped to:

- mode classification fallback;
- dry-run action-plan JSON;
- visual-servo/training/EMG display hints;
- no CAN TX;
- no real motion approval.

When merging with `product-main`, fold these contracts into:

- `vla_system` for task/intent parsing and grounding;
- `rehab_task_manager` for product-level intent and action-plan shaping;
- `safety_supervisor` for command approval;
- C++ camera/vision package for realtime frame inference.

## Practical Next Step

Do not add more parallel orchestration packages. The next useful increment is:

1. finish/convert the labeled mono dataset to YOLO;
2. train first target/end-effector detector;
3. emit detector results as scene objects compatible with `vla_system`;
4. add visual-servo hints as dry-run display context;
5. later wire real motion only through `safety_supervisor` and M33.
