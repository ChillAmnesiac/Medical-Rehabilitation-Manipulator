# Rehab Arm Closed-Loop Architecture

This project has several loops. They must stay separated by responsibility so the demo grows without becoming a pile of one-off scripts.

## Safety Boundary

All loops below are dry-run or advisory until M33 safety arbitration explicitly allows motion. The formal motion path remains:

```text
JointTrajectory candidate -> NanoPi -> M33 safety gate -> motor
```

NanoPi, cloud VLA, XiaoZhi, App, and M55 can propose context, intent, or candidate plans. They do not authorize motion by themselves.

## Loops

### 1. Language Intent Loop

Owner: XiaoZhi/L path and platform language adapter.

Input examples:

- "我口渴了"
- "帮我拿水杯"
- "开始今天的训练"
- "开启助力"
- normal chat

Output:

```text
LanguageIntent -> mode + target_label + confidence
```

Modes:

- `chat`
- `fetch_object`
- `training`
- `assistive_emg`
- `vision_servo`
- `safety_review`

Boundary:

- L is shared by all modes.
- This package classifies intent but does not replace XiaoZhi.
- Chat mode must not create robot action.

### 2. VLA Fetch Object Loop

Owner: VLA orchestrator plus vision detector.

Goal:

```text
language target -> target detection -> end-effector detection -> dry-run visual servo hint
```

Required visual facts:

- `target_cup` or `target_bottle`
- `end_effector`
- optional `gripper_tip`

State flow:

```text
waiting_for_target
  -> waiting_for_end_effector
  -> visual_servo_adjust
  -> visual_servo_aligned
  -> operator_review
  -> M33_required_for_motion
```

First implementation:

- PC/AnyLabeling dataset trains a mono detector.
- NanoPi C++ path should run detector/inference when the model is ready.
- Until calibration exists, servo hints are pixel-space only.

### 3. Vision Servo Loop

Owner: edge vision runtime, preferably C++ for realtime paths.

Input:

- target bbox center
- end-effector or gripper-tip bbox center
- frame size
- optional stereo/calibrated depth

Output:

```json
{
  "type": "pixel_servo_hint",
  "dx_px": 70,
  "dy_px": 20,
  "metric_depth_available": false
}
```

Boundary:

- Pixel servo hints are not motor commands.
- Camera-to-arm calibration is required before metric arm coordinates.
- Hand-eye calibration is required before true arm-frame control.

### 4. Training Loop

Owner: training library, App/platform, and later training AI.

Flow:

```text
language training intent
  -> training goal selection
  -> assistive policy
  -> EMG/IMU/joint feedback
  -> training summary
  -> next-session recommendation
```

Current scaffold:

- `TrainingGoal` contract exists.
- Training library content is still to be filled.

### 5. EMG Assistive Loop

Owner: C8T6 sensors, M55 intent inference, M33 safety gate, platform display.

Flow:

```text
4-channel EMG
  -> M55 intended motion
  -> M33 safety arbitration
  -> assistive hint / limited assist candidate
  -> platform visualization
```

Boundary:

- EMG confidence alone is not motion permission.
- M33 remains the final arbiter.

### 6. Demo Observability Loop

Owner: platform and logs.

The competition demo should show:

- real camera keyframes or video frames
- real detection boxes
- VLA mode and action-plan state
- visual servo delta
- M55 EMG intent and muscle activity
- M33 safety state
- MuJoCo/shadow state when available

No fake boxes. If a signal is missing, the UI should show a clear waiting/blocked state.

## Existing Product Spine

Before adding new nodes, use the `product-main` history as the architectural baseline. That branch already established this product integration spine:

```text
/speech/text
  -> vla_system / vla_bridge
  -> /task/resolved
  -> rehab_task_manager
  -> /rehab/task_intent
  -> /safety/command_request
  -> safety_supervisor
  -> /safety/command_approved
  -> /can_tx
```

Existing packages from `product-main`:

- `vla_system`: task parsing, grounding, phase prediction, confirmation.
- `vla_bridge`: ROS bridge around `vla_system`.
- `rehab_task_manager`: converts resolved tasks and app requests into safety requests.
- `safety_supervisor`: validates confirmation, limits, emergency stop, and publishes approved commands.
- `mock_hardware_bridge`: simulation/telemetry bridge for testing before hardware.

This means closed-loop work must extend that spine rather than create a parallel motion authority.

## Implementation Boundary

Current additive package:

```text
src/rehab_vla_orchestrator/
```

Purpose:

- Provide a thin multi-mode action-plan adapter while the current branch lacks the `product-main` packages.
- Own fallback mode classification for demo/testing only.
- Own dry-run action-plan contracts for visual servo, training, and EMG assist displays.
- Publish action plans to `/rehab_arm/vla/action_plan`.
- Keep real motion out of scope.

Non-goals:

- Do not replace `vla_system`.
- Do not replace `rehab_task_manager`.
- Do not replace `safety_supervisor`.
- Do not publish to `/can_tx`.

Merge direction:

- When this branch is reconciled with `product-main`, move useful mode/action-plan contracts into `rehab_task_manager` or `vla_system`.
- Keep C++ visual detection/runtime close to `camera_client` or a dedicated edge vision package.
- Keep all real command approval inside `safety_supervisor` and M33.

Performance plan:

- Python orchestrator is acceptable for mode/state planning.
- C++ should own detector runtime, frame processing, and future visual-servo realtime loops.
- The current `camera_client` C++ package remains the right place to extend edge vision transport/inference after the first YOLO model exists.

## Current Temporary Contract Topics

Input:

```text
/rehab_arm/language_intent_text  std_msgs/String
```

Output:

```text
/rehab_arm/vla/action_plan       std_msgs/String(JSON)
```

The JSON schema is `rehab_vla_action_plan_v1`.

These topics are temporary scaffolding for current-branch development. Product integration should eventually map them onto the `product-main` contract:

```text
/speech/text
/task/resolved
/rehab/task_intent
/safety/command_request
/safety/events
```
