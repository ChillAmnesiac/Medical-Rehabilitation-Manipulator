from __future__ import annotations

import sys
import unittest
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))

from rehab_arm_control.joint_trajectory_planner import (  # noqa: E402
    plan_joint_trajectory,
    to_joint_trajectory,
)
from rehab_arm_control.medical_arm_kinematics import MEDICAL_ARM_JOINT_NAMES  # noqa: E402


class JointTrajectoryPlannerTests(unittest.TestCase):
    def test_planner_starts_and_ends_at_requested_positions(self) -> None:
        goal = [0.2, 0.1, 0.0, 0.3, 0.0, 0.0]

        plan = plan_joint_trajectory([0.0] * 6, goal, duration=2.0, sample_period=0.5)

        self.assertEqual(plan.points[0].positions, [0.0] * 6)
        self.assertEqual(plan.points[-1].positions, goal)
        self.assertEqual(plan.points[0].time_from_start, 0.0)
        self.assertEqual(plan.points[-1].time_from_start, 2.0)

    def test_planner_respects_velocity_limits_when_duration_is_automatic(self) -> None:
        plan = plan_joint_trajectory([0.0] * 6, [0.0, 0.7, 0.0, 0.0, 0.0, 0.0], sample_period=0.2)

        self.assertGreaterEqual(plan.duration, 2.0)

    def test_planner_clamps_goal_to_joint_limits(self) -> None:
        plan = plan_joint_trajectory([0.0] * 6, [9.0, -9.0, 0.0, 9.0, 0.0, 0.0], duration=1.0)

        self.assertEqual(plan.points[-1].positions, [1.5708, -0.5236, 0.0, 2.3562, 0.0, 0.0])

    def test_to_joint_trajectory_uses_medical_arm_joint_names(self) -> None:
        plan = plan_joint_trajectory([0.0] * 6, [0.0, 0.1, 0.0, 0.2, 0.0, 0.0], duration=2.0)

        msg = to_joint_trajectory(plan)

        self.assertEqual(msg.joint_names, list(MEDICAL_ARM_JOINT_NAMES))
        self.assertEqual(list(msg.points[-1].positions), [0.0, 0.1, 0.0, 0.2, 0.0, 0.0])
        self.assertEqual(msg.points[-1].time_from_start.sec, 2)
        self.assertEqual(msg.points[-1].time_from_start.nanosec, 0)


if __name__ == '__main__':
    unittest.main()
