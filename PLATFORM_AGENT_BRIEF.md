# Platform Agent Brief

Use this brief when assigning an NPC or workstation to this GitHub project.

## Mission

Organize and develop the Medical Rehabilitation Manipulator as a complete
engineering product. Do not reduce it to a VLA demo, ROS demo, Android app, or
firmware-only project.

## Current Branch Rule

`platform-dev-organization` is the coordination branch. It contains task and
architecture truth for platform development.

Do not implement feature code in this branch unless the task is specifically
about coordination documents, task board, branch hygiene, or project planning.

## Source Branch Rules

- Firmware work starts from `M33`, `M55`, or `C8T6`.
- App work starts from `APP`.
- Future ROS work starts from `NanoPi_ROSNode`.
- VLA work starts from `ai`.
- Hardware documentation work starts from `PCB`.

Agents must name the source branch they inspected and the target branch they
intend to change before doing implementation work.

## Safety Rule

Any real actuator-control task must explicitly identify:

- safety owner;
- emergency stop behavior;
- command limits;
- telemetry evidence;
- user-visible acceptance test.

If those are missing, the agent should produce a contract or audit document
instead of writing motor-control code.

## First Assignments

Use `PLATFORM_TASK_BOARD.md` as the first queue. P0 audit tasks come before
implementation tasks.
