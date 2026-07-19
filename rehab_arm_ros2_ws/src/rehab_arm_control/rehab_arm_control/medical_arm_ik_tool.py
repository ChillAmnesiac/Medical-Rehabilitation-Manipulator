#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from typing import Sequence

from rehab_arm_control.cartesian_ik import solve_position_ik
from rehab_arm_control.joint_trajectory_planner import duration_message
from rehab_arm_control.medical_arm_kinematics import (
    MEDICAL_ARM_JOINT_NAMES,
    end_effector_position,
)


DEFAULT_TOPIC = '/arm_controller/joint_trajectory'
MAX_CURRENT_MA = 3000
HARDWARE_JOINT_NAMES = (
    'elbow_lift_joint',
    'shoulder_abduction_joint',
    'upper_arm_rotation_joint',
)
HARDWARE_LIMITS = {
    'elbow_lift_joint': (0.0, 1.8),
    'shoulder_abduction_joint': (0.0, math.radians(150.0)),
    'upper_arm_rotation_joint': (-1.2, 1.2),
}


class _FallbackJointTrajectoryPoint:
    def __init__(self) -> None:
        self.positions: list[float] = []
        self.velocities: list[float] = []
        self.effort: list[float] = []
        self.time_from_start = duration_message(0.0)


class _FallbackJointTrajectory:
    def __init__(self) -> None:
        self.joint_names: list[str] = []
        self.points: list[_FallbackJointTrajectoryPoint] = []


def rpm_to_velocity_rad_s(rpm: int | float) -> float:
    return abs(float(rpm)) * 2.0 * math.pi / 60.0


def hardware_seed_to_medical_positions(
    *,
    motor4_rad: float = 0.0,
    motor5_rad: float = 0.0,
    motor6_rad: float = 0.0,
    jian_hengxiang_rad: float = 0.0,
    wrist_flex_rad: float = 0.0,
    wrist_dev_rad: float = 0.0,
) -> list[float]:
    return [
        float(jian_hengxiang_rad),
        float(motor4_rad),
        float(motor6_rad),
        float(motor5_rad),
        float(wrist_flex_rad),
        float(wrist_dev_rad),
    ]


def medical_positions_to_hardware_positions(medical_positions: Sequence[float]) -> list[float]:
    if len(medical_positions) != len(MEDICAL_ARM_JOINT_NAMES):
        raise ValueError(f'expected {len(MEDICAL_ARM_JOINT_NAMES)} medical arm joints')
    return [
        float(medical_positions[1]),
        float(medical_positions[3]),
        float(medical_positions[2]),
    ]


def validate_hardware_positions(hardware_positions: Sequence[float]) -> dict[str, object]:
    if len(hardware_positions) != len(HARDWARE_JOINT_NAMES):
        raise ValueError(f'expected {len(HARDWARE_JOINT_NAMES)} hardware joints')
    issues: list[str] = []
    for name, value in zip(HARDWARE_JOINT_NAMES, hardware_positions):
        low, high = HARDWARE_LIMITS[name]
        if value < low or value > high:
            issues.append(f'{name} {value:.4f} rad outside [{low:.4f}, {high:.4f}]')
    return {'ok': not issues, 'issues': issues}


def _round_list(values: Sequence[float], digits: int = 6) -> list[float]:
    return [round(float(value), digits) for value in values]


def build_hardware_ik_payload(
    target_xyz: Sequence[float],
    *,
    seed_motor4_deg: float = 0.0,
    seed_motor5_deg: float = 0.0,
    seed_motor6_deg: float = 0.0,
    current_ma: int = MAX_CURRENT_MA,
    rpm: int = 3,
    duration: float = 3.0,
) -> dict[str, object]:
    seed = hardware_seed_to_medical_positions(
        motor4_rad=math.radians(seed_motor4_deg),
        motor5_rad=math.radians(seed_motor5_deg),
        motor6_rad=math.radians(seed_motor6_deg),
    )
    ik_result = solve_position_ik(target_xyz, seed=seed)
    hardware_positions = medical_positions_to_hardware_positions(ik_result.positions)
    limit_result = validate_hardware_positions(hardware_positions)
    final_xyz = end_effector_position(ik_result.positions)
    return {
        'schema_version': 'medical_arm_hardware_ik_v1',
        'default_mode': 'dry_run_no_ros_publish',
        'ik_success': ik_result.success,
        'ik_error_norm_m': round(ik_result.error_norm, 6),
        'target_xyz_m': _round_list(target_xyz),
        'solved_xyz_m': _round_list(final_xyz),
        'medical_arm_joint_order': list(MEDICAL_ARM_JOINT_NAMES),
        'medical_arm_joint_radians': _round_list(ik_result.positions),
        'hardware_joint_names': list(HARDWARE_JOINT_NAMES),
        'hardware_joint_radians': _round_list(hardware_positions),
        'hardware_joint_degrees': _round_list([math.degrees(value) for value in hardware_positions], 3),
        'hardware_limit_ok': bool(limit_result['ok']),
        'hardware_limit_issues': list(limit_result['issues']),
        'trajectory_topic': DEFAULT_TOPIC,
        'current_ma': int(current_ma),
        'current_a': round(int(current_ma) / 1000.0, 3),
        'rpm': int(rpm),
        'duration_sec': float(duration),
        'publish_requires': ['--publish', '--confirm-onsite'],
    }


def build_hardware_trajectory_message(
    hardware_positions: Sequence[float],
    *,
    current_ma: int = MAX_CURRENT_MA,
    rpm: int = 3,
    duration: float = 3.0,
):
    if current_ma < 0 or current_ma > MAX_CURRENT_MA:
        raise ValueError(f'current_ma must be in [0, {MAX_CURRENT_MA}]')
    if rpm <= 0:
        raise ValueError('rpm must be positive')
    if duration <= 0.0:
        raise ValueError('duration must be positive')
    limit_result = validate_hardware_positions(hardware_positions)
    if not limit_result['ok']:
        raise ValueError('; '.join(limit_result['issues']))

    try:
        from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
    except Exception:
        message = _FallbackJointTrajectory()
        point = _FallbackJointTrajectoryPoint()
    else:
        message = JointTrajectory()
        point = JointTrajectoryPoint()

    message.joint_names = list(HARDWARE_JOINT_NAMES)
    point.positions = [float(value) for value in hardware_positions]
    point.velocities = [rpm_to_velocity_rad_s(rpm)] * len(HARDWARE_JOINT_NAMES)
    point.effort = [float(current_ma) / 1000.0] * len(HARDWARE_JOINT_NAMES)
    point.time_from_start = duration_message(duration)
    message.points = [point]
    return message


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Solve xyz inverse kinematics for mounted motor 4/5/6 and optionally publish to hardware.',
    )
    parser.add_argument('--xyz', nargs=3, type=float, required=True, metavar=('X', 'Y', 'Z'))
    parser.add_argument('--seed-motor4-deg', type=float, default=0.0)
    parser.add_argument('--seed-motor5-deg', type=float, default=0.0)
    parser.add_argument('--seed-motor6-deg', type=float, default=0.0)
    parser.add_argument('--current-ma', type=int, default=MAX_CURRENT_MA)
    parser.add_argument('--rpm', type=int, default=3)
    parser.add_argument('--duration', type=float, default=3.0)
    parser.add_argument('--topic', default=DEFAULT_TOPIC)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--confirm-onsite', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    return parser


def publish_message(topic: str, message) -> None:
    import rclpy

    rclpy.init()
    node = rclpy.create_node('medical_arm_hardware_ik_publisher')
    try:
        publisher = node.create_publisher(type(message), topic, 10)
        if hasattr(message, 'header'):
            message.header.stamp = node.get_clock().now().to_msg()
        for _ in range(4):
            rclpy.spin_once(node, timeout_sec=0.05)
        publisher.publish(message)
        rclpy.spin_once(node, timeout_sec=0.2)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    payload = build_hardware_ik_payload(
        args.xyz,
        seed_motor4_deg=args.seed_motor4_deg,
        seed_motor5_deg=args.seed_motor5_deg,
        seed_motor6_deg=args.seed_motor6_deg,
        current_ma=args.current_ma,
        rpm=args.rpm,
        duration=args.duration,
    )

    returncode = 0
    if args.publish:
        if not args.confirm_onsite:
            payload['error'] = '--publish requires --confirm-onsite'
            returncode = 2
        elif not payload['ik_success']:
            payload['error'] = 'IK did not converge; refusing to publish'
            returncode = 2
        elif not payload['hardware_limit_ok']:
            payload['error'] = 'IK solution violates hardware limits; refusing to publish'
            returncode = 2
        else:
            message = build_hardware_trajectory_message(
                payload['hardware_joint_radians'],  # type: ignore[arg-type]
                current_ma=args.current_ma,
                rpm=args.rpm,
                duration=args.duration,
            )
            publish_message(args.topic, message)
            payload['published'] = True
            payload['trajectory_topic'] = args.topic

    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=args.pretty))
    return returncode


if __name__ == '__main__':
    raise SystemExit(main())
