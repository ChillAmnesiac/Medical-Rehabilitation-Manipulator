from __future__ import annotations

import sys
import unittest
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))

from rehab_arm_control.cartesian_ik import solve_position_ik  # noqa: E402
from rehab_arm_control.medical_arm_kinematics import end_effector_position  # noqa: E402


class CartesianIkTests(unittest.TestCase):
    def test_ik_returns_zero_for_zero_pose_target(self) -> None:
        result = solve_position_ik((1.02, 0.0, 0.8), seed=[0.0] * 6)

        self.assertTrue(result.success)
        self.assertEqual(result.positions, [0.0] * 6)
        self.assertLessEqual(result.error_norm, 1e-6)

    def test_ik_reaches_a_nearby_reachable_target(self) -> None:
        target = end_effector_position([0.2, 0.35, 0.0, 0.4, 0.0, 0.0])

        result = solve_position_ik(target, seed=[0.0, 0.2, 0.0, 0.2, 0.0, 0.0])

        self.assertTrue(result.success, result)
        self.assertLess(result.error_norm, 0.01)

    def test_ik_reports_failure_for_far_unreachable_target(self) -> None:
        result = solve_position_ik((5.0, 5.0, 5.0), seed=[0.0] * 6, max_iterations=20)

        self.assertFalse(result.success)
        self.assertGreater(result.error_norm, 1.0)


if __name__ == '__main__':
    unittest.main()
