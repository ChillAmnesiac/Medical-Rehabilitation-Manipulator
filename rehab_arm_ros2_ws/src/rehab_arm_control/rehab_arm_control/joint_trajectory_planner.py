from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from rehab_arm_control.medical_arm_kinematics import (
    JOINT_LIMITS,
    MEDICAL_ARM_JOINT_NAMES,
    clamp_to_limits,
)


@dataclass(frozen=True)
class TrajectoryPoint:
    positions: list[float]
    velocities: list[float]
    time_from_start: float


@dataclass(frozen=True)
class PlannedTrajectory:
    points: list[TrajectoryPoint]
    duration: float


class _FallbackDuration:
    def __init__(self) -> None:
        self.sec = 0
        self.nanosec = 0


class _FallbackJointTrajectoryPoint:
    def __init__(self) -> None:
        self.positions: list[float] = []
        self.velocities: list[float] = []
        self.time_from_start = _FallbackDuration()


class _FallbackJointTrajectory:
    def __init__(self) -> None:
        self.joint_names: list[str] = []
        self.points: list[_FallbackJointTrajectoryPoint] = []


def _validate_positions(name: str, positions: Sequence[float]) -> list[float]:
    if len(positions) != len(MEDICAL_ARM_JOINT_NAMES):
        raise ValueError(f'{name} must contain {len(MEDICAL_ARM_JOINT_NAMES)} joint positions')
    return [float(position) for position in positions]


def _smoothstep(alpha: float) -> float:
    return 10.0 * alpha ** 3 - 15.0 * alpha ** 4 + 6.0 * alpha ** 5


def _smoothstep_derivative(alpha: float) -> float:
    return 30.0 * alpha ** 2 * (1.0 - alpha) ** 2


def _automatic_duration(start: list[float], goal: list[float], max_velocity_scale: float) -> float:
    if max_velocity_scale <= 0.0:
        raise ValueError('max_velocity_scale must be positive')
    required = 0.0
    # Quintic smoothstep reaches 1.875x average velocity at alpha=0.5.
    peak_velocity_factor = 1.875
    for name, start_value, goal_value in zip(MEDICAL_ARM_JOINT_NAMES, start, goal):
        velocity_limit = JOINT_LIMITS[name].velocity * max_velocity_scale
        if velocity_limit <= 0.0:
            continue
        required = max(required, abs(goal_value - start_value) * peak_velocity_factor / velocity_limit)
    return max(required, 0.1)


def _sample_times(duration: float, sample_period: float) -> list[float]:
    if sample_period <= 0.0:
        raise ValueError('sample_period must be positive')
    if duration <= 0.0:
        raise ValueError('duration must be positive')

    count = max(1, int(math.ceil(duration / sample_period)))
    times = [round(min(index * sample_period, duration), 12) for index in range(count + 1)]
    if times[-1] != duration:
        times.append(duration)
    return times


def plan_joint_trajectory(
    start: Sequence[float],
    goal: Sequence[float],
    *,
    duration: float | None = None,
    sample_period: float = 0.1,
    max_velocity_scale: float = 1.0,
) -> PlannedTrajectory:
    start_values = clamp_to_limits(_validate_positions('start', start))
    goal_values = clamp_to_limits(_validate_positions('goal', goal))
    plan_duration = float(duration) if duration is not None else _automatic_duration(
        start_values,
        goal_values,
        max_velocity_scale,
    )
    times = _sample_times(plan_duration, sample_period)
    deltas = [goal_value - start_value for start_value, goal_value in zip(start_values, goal_values)]
    points: list[TrajectoryPoint] = []

    for time_from_start in times:
        alpha = time_from_start / plan_duration
        scale = _smoothstep(alpha)
        velocity_scale = _smoothstep_derivative(alpha) / plan_duration
        points.append(
            TrajectoryPoint(
                positions=[
                    start_value + delta * scale
                    for start_value, delta in zip(start_values, deltas)
                ],
                velocities=[delta * velocity_scale for delta in deltas],
                time_from_start=time_from_start,
            )
        )

    points[0].positions[:] = start_values
    points[0].velocities[:] = [0.0] * len(start_values)
    points[-1].positions[:] = goal_values
    points[-1].velocities[:] = [0.0] * len(start_values)
    return PlannedTrajectory(points=points, duration=plan_duration)


def duration_message(seconds: float):
    try:
        from builtin_interfaces.msg import Duration
    except Exception:
        msg = _FallbackDuration()
    else:
        msg = Duration()

    whole_seconds = int(seconds)
    msg.sec = whole_seconds
    msg.nanosec = int(round((seconds - whole_seconds) * 1_000_000_000))
    if msg.nanosec >= 1_000_000_000:
        msg.sec += 1
        msg.nanosec -= 1_000_000_000
    return msg


def to_joint_trajectory(
    plan: PlannedTrajectory,
    *,
    joint_names: Sequence[str] = MEDICAL_ARM_JOINT_NAMES,
):
    try:
        from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
    except Exception:
        trajectory = _FallbackJointTrajectory()
        point_type = _FallbackJointTrajectoryPoint
    else:
        trajectory = JointTrajectory()
        point_type = JointTrajectoryPoint

    trajectory.joint_names = list(joint_names)
    trajectory.points = []
    for planned_point in plan.points:
        point = point_type()
        point.positions = list(planned_point.positions)
        point.velocities = list(planned_point.velocities)
        point.time_from_start = duration_message(planned_point.time_from_start)
        trajectory.points.append(point)
    return trajectory
