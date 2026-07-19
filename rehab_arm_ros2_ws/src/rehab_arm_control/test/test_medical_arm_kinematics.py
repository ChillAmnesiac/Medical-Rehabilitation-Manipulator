from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))

from rehab_arm_control.medical_arm_kinematics import (  # noqa: E402
    MEDICAL_ARM_JOINT_NAMES,
    clamp_to_limits,
    end_effector_position,
    forward_kinematics,
    numerical_position_jacobian,
)


def assert_close_tuple(
    test_case: unittest.TestCase,
    actual: tuple[float, ...],
    expected: tuple[float, ...],
    tolerance: float = 1e-6,
) -> None:
    test_case.assertEqual(len(actual), len(expected))
    for actual_value, expected_value in zip(actual, expected):
        test_case.assertAlmostEqual(actual_value, expected_value, delta=tolerance)


class MedicalArmKinematicsTests(unittest.TestCase):
    def test_joint_contract_matches_medical_arm_shadow_model(self) -> None:
        self.assertEqual(
            MEDICAL_ARM_JOINT_NAMES,
            (
                'jian_hengxiang_joint',
                'jian_zongxiang_joint',
                'jian_xuanzhuan_joint',
                'zhou_zongxiang_joint',
                'wanbu_zongxiang_joint',
                'wanbu_hengxiang_joint',
            ),
        )

    def test_zero_pose_matches_mjcf_chain_length_and_base_height(self) -> None:
        pose = forward_kinematics([0.0] * 6)

        self.assertEqual(pose.position, (1.02, 0.0, 0.8))
        self.assertEqual(end_effector_position([0.0] * 6), pose.position)

    def test_base_yaw_rotates_end_effector_into_y_axis(self) -> None:
        pose = forward_kinematics([math.pi / 2, 0.0, 0.0, 0.0, 0.0, 0.0])

        assert_close_tuple(self, pose.position, (0.0, 1.02, 0.8))

    def test_shoulder_pitch_moves_end_effector_down_in_model_z(self) -> None:
        zero = forward_kinematics([0.0] * 6).position
        pitched = forward_kinematics([0.0, 0.5, 0.0, 0.0, 0.0, 0.0]).position

        self.assertLess(pitched[2], zero[2])
        self.assertLess(pitched[0], zero[0])

    def test_clamp_to_limits_uses_medical_arm_limits(self) -> None:
        positions = clamp_to_limits([9.0, -9.0, 0.0, 9.0, 0.0, 0.0])

        self.assertEqual(positions, [1.5708, -0.5236, 0.0, 2.3562, 0.0, 0.0])

    def test_numerical_jacobian_has_xyz_rows_and_one_column_per_joint(self) -> None:
        jacobian = numerical_position_jacobian([0.0, 0.2, 0.0, 0.3, 0.0, 0.0])

        self.assertEqual(len(jacobian), 3)
        self.assertTrue(all(len(row) == 6 for row in jacobian))


if __name__ == '__main__':
    unittest.main()
