#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Sequence

from rehab_arm_control.cartesian_ik import IKResult, solve_position_ik
from rehab_arm_control.joint_trajectory_planner import (
    plan_joint_trajectory,
    to_joint_trajectory,
)
from rehab_arm_control.medical_arm_kinematics import (
    MEDICAL_ARM_JOINT_NAMES,
    end_effector_position,
)


DEFAULT_SHADOW_TOPIC = '/sim/medical_arm/joint_trajectory'


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Plan a 6DOF medical arm target and publish it to the MuJoCo shadow trajectory topic.',
    )
    goal_group = parser.add_mutually_exclusive_group(required=True)
    goal_group.add_argument(
        '--joints',
        nargs=6,
        type=float,
        metavar=('Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
        help='Target joint positions in radians, ordered as the medical_arm_6dof joint contract.',
    )
    goal_group.add_argument(
        '--xyz',
        nargs=3,
        type=float,
        metavar=('X', 'Y', 'Z'),
        help='Target end-effector position in the MuJoCo world frame, meters.',
    )
    parser.add_argument(
        '--start',
        nargs=6,
        type=float,
        default=[0.0] * 6,
        metavar=('Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
        help='Start joint positions in radians. Defaults to the zero calibration pose.',
    )
    parser.add_argument(
        '--seed',
        nargs=6,
        type=float,
        metavar=('Q0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
        help='IK seed joint positions in radians. Defaults to --start.',
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=None,
        help='Trajectory duration in seconds. Omit to compute a conservative velocity-limited duration.',
    )
    parser.add_argument('--sample-period', type=float, default=0.1, help='Trajectory sampling period in seconds.')
    parser.add_argument(
        '--max-velocity-scale',
        type=float,
        default=1.0,
        help='Scale applied to the medical_arm_6dof velocity limits when duration is automatic.',
    )
    parser.add_argument('--topic', default=DEFAULT_SHADOW_TOPIC, help='JointTrajectory topic to publish.')
    parser.add_argument('--publish-repeat', type=int, default=3, help='Number of publish attempts before exit.')
    parser.add_argument('--spin-delay', type=float, default=0.1, help='Seconds to spin after each publish.')
    return parser


def build_goal_positions(args: argparse.Namespace, start_positions: Sequence[float]) -> list[float]:
    if args.joints is not None:
        return [float(value) for value in args.joints]

    seed = args.seed if args.seed is not None else start_positions
    result = solve_position_ik(args.xyz, seed=seed)
    if not result.success:
        raise RuntimeError(
            'IK failed for target '
            f'{tuple(args.xyz)}; best_error={result.error_norm:.4f}m, best_positions={result.positions}'
        )
    return result.positions


def build_trajectory_message(
    start_positions: Sequence[float],
    goal_positions: Sequence[float],
    *,
    duration: float | None = None,
    sample_period: float = 0.1,
    max_velocity_scale: float = 1.0,
):
    plan = plan_joint_trajectory(
        start_positions,
        goal_positions,
        duration=duration,
        sample_period=sample_period,
        max_velocity_scale=max_velocity_scale,
    )
    return to_joint_trajectory(plan)


def _ik_result_for_log(args: argparse.Namespace, start_positions: Sequence[float]) -> IKResult | None:
    if args.xyz is None:
        return None
    seed = args.seed if args.seed is not None else start_positions
    return solve_position_ik(args.xyz, seed=seed)


def publish_message(args: argparse.Namespace, message, goal_positions: Sequence[float]) -> None:
    import rclpy

    rclpy.init()
    node = rclpy.create_node('medical_arm_mujoco_plan_publisher')
    try:
        publisher = node.create_publisher(type(message), args.topic, 10)
        if hasattr(message, 'header'):
            message.header.stamp = node.get_clock().now().to_msg()
        final_xyz = end_effector_position(goal_positions)
        node.get_logger().info(
            f'Publishing {len(message.points)} trajectory points to {args.topic}; '
            f'goal_joints={[round(value, 4) for value in goal_positions]}; '
            f'goal_xyz={[round(value, 4) for value in final_xyz]}'
        )
        for _ in range(max(1, int(args.publish_repeat))):
            publisher.publish(message)
            rclpy.spin_once(node, timeout_sec=max(0.0, float(args.spin_delay)))
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    start_positions = [float(value) for value in args.start]
    goal_positions = build_goal_positions(args, start_positions)
    message = build_trajectory_message(
        start_positions,
        goal_positions,
        duration=args.duration,
        sample_period=args.sample_period,
        max_velocity_scale=args.max_velocity_scale,
    )
    publish_message(args, message, goal_positions)


if __name__ == '__main__':
    main()
