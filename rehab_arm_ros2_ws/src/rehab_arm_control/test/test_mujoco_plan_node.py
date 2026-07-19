from __future__ import annotations

import sys
import unittest
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))

from rehab_arm_control.medical_arm_kinematics import MEDICAL_ARM_JOINT_NAMES  # noqa: E402
from rehab_arm_control.mujoco_plan_node import (  # noqa: E402
    build_arg_parser,
    build_goal_positions,
    build_trajectory_message,
)


class MujocoPlanNodeTests(unittest.TestCase):
    def test_default_topic_is_shadow_simulation_topic(self) -> None:
        parser = build_arg_parser()

        args = parser.parse_args(['--joints', '0', '0.1', '0', '0.2', '0', '0'])

        self.assertEqual(args.topic, '/sim/medical_arm/joint_trajectory')

    def test_joint_goal_builds_medical_arm_trajectory_message(self) -> None:
        msg = build_trajectory_message([0.0] * 6, [0.0, 0.1, 0.0, 0.2, 0.0, 0.0], duration=2.0)

        self.assertEqual(msg.joint_names, list(MEDICAL_ARM_JOINT_NAMES))
        self.assertEqual(list(msg.points[-1].positions), [0.0, 0.1, 0.0, 0.2, 0.0, 0.0])

    def test_joint_goal_parser_returns_six_positions(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args(['--joints', '0', '0.1', '0', '0.2', '0', '0'])

        result = build_goal_positions(args, [0.0] * 6)

        self.assertEqual(result, [0.0, 0.1, 0.0, 0.2, 0.0, 0.0])

    def test_xyz_goal_uses_position_ik(self) -> None:
        parser = build_arg_parser()
        args = parser.parse_args(['--xyz', '1.02', '0', '0.8'])

        result = build_goal_positions(args, [0.0] * 6)

        self.assertEqual(result, [0.0] * 6)

    def test_package_installs_no_suffix_ros2_run_alias(self) -> None:
        package_dir = Path(__file__).resolve().parents[1]
        wrapper = package_dir / 'rehab_arm_control' / 'mujoco_plan_node'
        cmake = (package_dir / 'CMakeLists.txt').read_text(encoding='utf-8')

        self.assertTrue(wrapper.exists(), wrapper)
        self.assertIn('rehab_arm_control/mujoco_plan_node\n', cmake)


if __name__ == '__main__':
    unittest.main()
