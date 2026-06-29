# Additive Closed-Loop Integration Plan

This document is the guardrail for future work: add capability without replacing existing functions.

## Non-Negotiable Rule

Do not remove or replace existing branch functions unless the user explicitly asks for a migration.

Additions must be one of:

- new data source;
- new topic;
- new adapter;
- new dry-run context;
- new UI/display evidence;
- new test or documentation;
- new model artifact path.

They must not bypass:

- XiaoZhi/L chain;
- `vla_system`;
- `rehab_task_manager`;
- `safety_supervisor`;
- M33 safety arbitration.

## Current Branch Reality

Current working branch: `NanoPi_ROSNode`.

Existing local functions:

- `camera_client`: C++ WebSocket image stream.
- `http_bridge`: Android/OpenClaw HTTP bridge.
- `start_camera.sh`, `start_http_bridge.sh`: existing entry scripts.

Historical product spine from `product-main`:

- `vla_system`
- `vla_bridge`
- `rehab_task_manager`
- `safety_supervisor`
- `mock_hardware_bridge`

Therefore, any new closed loop should be built as an additive layer that can later be folded into `product-main`.

## Additive Loop Map

### Visual Detection Loop

Add:

- labeled dataset under `D:/vla_dataset` outside Git;
- `scripts/prepare_yolo_dataset.py`;
- trained model artifact path;
- C++ inference executable later.

Do not replace:

- existing `camera_client` stream;
- existing NanoPi stereo upload loop;
- existing platform keyframe flow.

Target output:

```json
{
  "objects": [
    {
      "object_id": "cup_001",
      "class_name": "cup",
      "bbox": [x, y, w, h],
      "confidence": 0.82
    }
  ],
  "end_effector": {
    "bbox": [x, y, w, h],
    "gripper_tip": [x, y]
  }
}
```

Later integration point:

- `vla_system` scene objects for grounding;
- platform visual evidence cards;
- dry-run visual servo hint.

### VLA Fetch Loop

Add:

- target/end-effector observations;
- pixel-space servo hints;
- operator review state.

Do not replace:

- `vla_system` parsing/grounding;
- `rehab_task_manager` product intent shaping;
- `safety_supervisor` approval.

Temporary output:

```text
/rehab_arm/vla/action_plan
```

Future product mapping:

```text
scene objects -> vla_system -> /task/resolved -> rehab_task_manager
```

### Training Loop

Add:

- training goal library;
- training session state;
- display of current goal and progress;
- later AI summary.

Do not replace:

- app request path;
- safety supervisor;
- M33/M55 real-time roles.

Future product mapping:

```text
training request -> /rehab/task_intent -> /safety/command_request
```

### EMG Assistive Loop

Add:

- normalized EMG telemetry display;
- M55 intent context;
- assistive hint only.

Do not replace:

- M55 inference path;
- M33 safety gate;
- existing C8T6 firmware work.

Future product mapping:

```text
EMG/M55 context -> rehab_task_manager assist intent -> safety_supervisor -> M33
```

### Demo Observability Loop

Add:

- mode timeline;
- real detection frames;
- real logs;
- explicit missing-signal states.

Do not fake:

- detection boxes;
- motor status;
- M33 safety state;
- EMG confidence.

## C++ Placement Rule

Use C++ for:

- camera capture runtime;
- detector inference;
- future visual-servo frame loop;
- latency-sensitive NanoPi components.

Use Python for:

- dataset conversion;
- smoke tests;
- slow orchestration/dry-run planning;
- docs/tooling.

## Current Temporary Package

`src/rehab_vla_orchestrator` exists only because `NanoPi_ROSNode` does not contain the `product-main` packages.

Allowed use:

- smoke-test closed-loop modes;
- dry-run action plan JSON;
- demo scaffolding.

Not allowed:

- publishing to `/can_tx`;
- replacing `vla_bridge`;
- replacing `rehab_task_manager`;
- replacing `safety_supervisor`.

## Immediate Safe Next Steps

1. Finish annotation.
2. Convert AnyLabeling JSON to YOLO.
3. Train first detector.
4. Create a C++ or OpenCV edge inference prototype that emits target/end-effector observations.
5. Feed observations into `vla_system` scene objects or temporary dry-run action plan.
6. Only later, merge with `product-main` and keep motion behind `safety_supervisor` and M33.
