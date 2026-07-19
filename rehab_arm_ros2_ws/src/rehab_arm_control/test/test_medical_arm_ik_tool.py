from __future__ import annotations

import sys
import unittest
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))

from rehab_arm_control.medical_arm_ik_tool import (  # noqa: E402
    HARDWARE_JOINT_NAMES,
    build_arg_parser,
    build_hardware_ik_payload,
    build_hardware_trajectory_message,
    validate_hardware_positions,
)


class MedicalArmIkToolTests(unittest.TestCase):
    def test_zero_pose_target_maps_to_zero_hardware_joints(self) -> None:
        payload = build_hardware_ik_payload((1.02, 0.0, 0.8))

        self.assertTrue(payload['ik_success'])
        self.assertTrue(payload['hardware_limit_ok'])
        self.assertEqual(payload['hardware_joint_names'], list(HARDWARE_JOINT_NAMES))
        self.assertEqual(payload['hardware_joint_radians'], [0.0, 0.0, 0.0])

    def test_hardware_limits_reject_negative_motor4_angle(self) -> None:
        result = validate_hardware_positions([-0.1, 0.0, 0.0])

        self.assertFalse(result['ok'])
        self.assertIn('elbow_lift_joint', result['issues'][0])

    def test_trajectory_message_carries_current_hint_as_effort(self) -> None:
        msg = build_hardware_trajectory_message(
            [0.1, 0.2, 0.3],
            current_ma=3000,
            rpm=3,
            duration=2.0,
        )

        self.assertEqual(msg.joint_names, list(HARDWARE_JOINT_NAMES))
        self.assertEqual(list(msg.points[0].positions), [0.1, 0.2, 0.3])
        self.assertEqual(list(msg.points[0].effort), [3.0, 3.0, 3.0])
        self.assertEqual(msg.points[0].time_from_start.sec, 2)

    def test_parser_defaults_to_hardware_topic_and_3000ma(self) -> None:
        parser = build_arg_parser()

        args = parser.parse_args(['--xyz', '1.02', '0', '0.8'])

        self.assertEqual(args.topic, '/arm_controller/joint_trajectory')
        self.assertEqual(args.current_ma, 3000)


if __name__ == '__main__':
    unittest.main()
