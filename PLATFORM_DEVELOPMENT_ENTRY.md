# AI Platform Development Entry

This branch is the AI collaboration platform entry branch for the Medical
Rehabilitation Manipulator project.

It does not implement ROS 2, firmware, app, or hardware control directly. Its
purpose is to make the existing GitHub repository understandable and assignable
to platform workstations, NPCs, and development threads without losing the
existing branch assets.

## Current Project Intent

The product is a complete medical rehabilitation manipulator prototype:

- hardware structure, PCB, motors, sensors, CAN/serial communication, power, and
  emergency stop;
- firmware for M33, M55, and optional C8T6 boards;
- NanoPi or Linux edge runtime, later including ROS 2;
- VLA/AI task understanding and rehabilitation assistance;
- Android app or web UI for patient workflow, training, debugging, data review,
  and reports;
- safety, data recording, and rehabilitation workflow validation.

The current priority is not to build a fake closed loop. The priority is to
organize the repository so the platform can develop the real project branch by
branch.

## Branch Inventory

| Branch | Current Role | Platform Treatment |
| --- | --- | --- |
| `main` | Historical PSoC Edge E84 product plan and README. | Keep as legacy overview. Do not treat as latest implementation truth. |
| `M33` | PSoC M33 / RT-Thread control, CAN, Bluetooth, safety, sensor/control manager assets. | Firmware workstation source for real-time control and safety. |
| `M55` | PSoC M55 / voice, WiFi, OpenClaw, AI/audio assets. | Firmware/AI edge workstation source. Validate whether M55 remains in current hardware plan. |
| `C8T6` | STM32F1 sensor collection, CAN, MAX/IMU/ADC assets. | Sensor-node workstation source only if STM32F1 is still used. |
| `NanoPi_ROSNode` | ROS 2 Jazzy workspace, camera client, HTTP bridge, OpenClaw bridge docs. | Future ROS/edge workstation base. Do not force ROS before user is ready. |
| `ai` | VLA task understanding prototype with schemas, tests, ROS bridge draft. | AI/VLA workstation source for task parsing and structured intent. |
| `APP` | Android rehabilitation app assets and many generated build files. | App workstation source; must be cleaned before serious development. |
| `PCB` | Hardware zip artifacts. | Hardware documentation source. Keep separate from software source. |
| `ROS_VLA_WebSocket` | Early WebSocket demo. | Legacy reference only; do not use as main runtime. |
| `nanopi-sdk` | NanoPi SDK branch. | Board support reference. Use only when NanoPi system work needs it. |
| `wake-word-model` | Wake word model branch. | Voice/AI asset reference. |

## Platform Workstations

Use these platform workstations instead of treating every branch as one mixed
project:

1. Product architecture workstation
   - Owns current architecture docs, branch map, hardware decisions, and product
     milestones.
   - Must keep this branch updated when plans change.

2. Hardware and PCB workstation
   - Starts from `PCB` and user-provided hardware truth.
   - Produces pin maps, power map, CAN topology, motor/sensor list, and safety
     checklist.

3. M33 firmware workstation
   - Starts from `M33`.
   - Owns real-time control, CAN, Bluetooth, safety state machine, and actuator
     command protocol.

4. M55 / voice / local AI workstation
   - Starts from `M55` and `wake-word-model`.
   - Owns voice, WiFi, local inference feasibility, and OpenClaw interface only
     if the hardware plan still uses M55.
   - 2026-06-13: M55 WiFi scan and LVGL touch provisioning reached a usable
     milestone. This is now the prerequisite for XiaoZhi/server connectivity
     bring-up; keep branch-specific firmware work on `M55`.

5. Sensor node workstation
   - Starts from `C8T6` only after confirming STM32F1 remains in the design.
   - Owns EMG, IMU, heart-rate, and CAN sensor frame definition.

6. Edge / ROS workstation
   - Starts from `NanoPi_ROSNode`.
   - Owns ROS 2 only after the user confirms ROS work begins.
   - Until then, it should document interfaces and avoid fake hardware loops.

7. VLA / AI workstation
   - Starts from `ai`.
   - Owns task understanding, schemas, dataset needs, and safety-bound intent
     output.

8. App workstation
   - Starts from `APP`.
   - Owns patient workflow, training UI, data visualization, reports, and
     communication adapters.

## Development Rules

- Do not collapse all branches into one code tree before hardware and runtime
  decisions are confirmed.
- Do not implement simulated ROS or hardware closed loops unless the user asks
  for that milestone.
- Do not trust old docs as current truth. When a decision changes, update this
  entry branch first.
- Keep branch-specific work in the matching branch until there is a clear
  integration milestone.
- All platform tasks should reference the source branch, expected output, test
  method, and user-visible acceptance criteria.
- Safety work is mandatory before any real actuator command path is considered
  complete.
- VLA/AI must produce intent or advice first; it must not directly own motor
  control.

## Immediate Platform Milestones

1. Confirm current hardware truth.
   - Which boards are actually used?
   - Which motors and sensors are physically available?
   - Which communication links are real: CAN, serial, BLE, WiFi, USB?

2. Clean branch inventory.
   - Mark each branch as active, reference-only, or archived.
   - Remove or ignore generated build output in `APP` before assigning app work.

3. Produce interface contracts before implementation.
   - Firmware command protocol.
   - Sensor telemetry frames.
   - App communication API.
   - Future ROS topic/API contract.
   - VLA structured task schema.

4. Assign platform threads.
   - Threads 1-2: hardware and firmware audit.
   - Threads 3-4: app and product workflow audit.
   - Thread 5: VLA/schema audit.
   - Thread 6: integration documentation and GitHub branch hygiene.

5. Only after the above, start implementation milestones in the matching source
   branch.

## What This Branch Should Contain

- Current architecture and branch decisions.
- Platform task board for NPC/workstation assignment.
- Handoff notes for each source branch.
- Integration plans and acceptance checklists.

It should not contain large copied source trees from other branches unless the
user decides to create a unified monorepo branch later.
