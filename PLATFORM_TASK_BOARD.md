# Platform Task Board

This file is the first task board for assigning work through the AI
collaboration platform. It is intentionally branch-oriented.

## P0: Repository And Product Truth

| ID | Workstation | Source Branch | Task | Output |
| --- | --- | --- | --- | --- |
| P0-001 | Product architecture | `main`, all branch READMEs | Build the current branch inventory and mark active/reference/archive status. | Updated `PLATFORM_DEVELOPMENT_ENTRY.md`. |
| P0-002 | Hardware and PCB | `PCB`, `main` | Confirm actual hardware list and unknowns. | `docs/hardware-current-truth.md`. |
| P0-003 | Firmware M33 | `M33` | Audit real-time control, CAN, Bluetooth, and safety code. | `docs/m33-firmware-audit.md`. |
| P0-004 | Firmware M55 | `M55`, `wake-word-model` | Audit voice, WiFi, OpenClaw, and local AI feasibility. | `docs/m55-ai-voice-audit.md`. |
| P0-005 | Sensor node | `C8T6` | Decide if STM32F1 sensor node is active. Audit sensor/CAN code if active. | `docs/c8t6-sensor-node-audit.md`. |
| P0-006 | App | `APP` | Audit app source versus generated build output and identify cleanup plan. | `docs/app-branch-cleanup-plan.md`. |
| P0-007 | Edge/ROS | `NanoPi_ROSNode` | Audit ROS2 assets without implementing ROS work yet. | `docs/nanopi-ros-audit.md`. |
| P0-008 | VLA/AI | `ai` | Audit schemas, tests, and VLA task boundary. | `docs/vla-ai-audit.md`. |

## P1: Contracts Before Code

| ID | Workstation | Depends On | Task | Output |
| --- | --- | --- | --- | --- |
| P1-001 | Product architecture | P0-002, P0-003 | Define actuator command protocol. | `docs/contracts/actuator-command-protocol.md`. |
| P1-002 | Product architecture | P0-002, P0-005 | Define telemetry frame format. | `docs/contracts/telemetry-frame-format.md`. |
| P1-003 | App + Firmware | P0-006, P0-003 | Define app-to-device API/channel decision. | `docs/contracts/app-device-api.md`. |
| P1-004 | VLA/AI + Safety | P0-008 | Define VLA intent output and forbidden direct-control boundary. | `docs/contracts/vla-intent-schema.md`. |
| P1-005 | Edge/ROS | P0-007, P1-001, P1-002 | Draft future ROS topic/API mapping. | `docs/contracts/future-ros-interface.md`. |

## P2: Implementation Starts After Contracts

Implementation tasks should be created only after P0 and the relevant P1
contract are accepted by the user.

Examples:

- M33 CAN telemetry read path.
- App source cleanup and build recovery.
- Sensor node read-only telemetry.
- VLA schema tests.
- NanoPi ROS2 build recovery.

Do not start fake integration loops to make the task board look complete.
