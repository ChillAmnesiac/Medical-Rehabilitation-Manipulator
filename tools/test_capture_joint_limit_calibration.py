import importlib.util
import math
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("capture_joint_limit_calibration.py")


def load_module():
    spec = importlib.util.spec_from_file_location("capture_joint_limit_calibration", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class JointLimitCalibrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_parse_feedback_and_drop_duplicate_tick(self):
        text = (
            "MOTOR[4]: id=4 proto=0 mode=0 fault=0x00 pos_mrad=-12437 "
            "vel_mrad_s=-3094 tor_mNm=0 temp_dC=300 tick=100\n"
            "MOTOR[4]: id=4 proto=0 mode=0 fault=0x00 pos_mrad=-12437 "
            "vel_mrad_s=-3094 tor_mNm=0 temp_dC=300 tick=100\n"
            "MOTOR[4]: id=4 proto=0 mode=0 fault=0x00 pos_mrad=12440 "
            "vel_mrad_s=-2521 tor_mNm=0 temp_dC=300 tick=101\n"
        )

        samples = self.module.parse_fresh_feedback(text, joint=4)

        self.assertEqual([sample.tick for sample in samples], [100, 101])
        self.assertAlmostEqual(samples[0].raw_rad, -12.437)
        self.assertAlmostEqual(samples[1].raw_rad, 12.440)

    def test_unwrap_uses_private_protocol_position_span(self):
        raw = [-12.000, -12.437, 12.440, 12.000]

        unwrapped = self.module.unwrap_positions(raw, period_rad=25.14)

        self.assertAlmostEqual(unwrapped[0], -12.000, places=3)
        self.assertAlmostEqual(unwrapped[2], -12.700, places=3)
        self.assertAlmostEqual(unwrapped[3], -13.140, places=3)

    def test_summary_accepts_repeatable_round_trip(self):
        summary = self.module.build_limit_summary(
            lower_start_rad=-2.000,
            upper_rad=-12.500,
            lower_return_rad=-2.020,
            gear_ratio=7.1844,
            repeat_tolerance_motor_rad=0.10,
        )

        self.assertAlmostEqual(summary["motor_travel_rad"], 10.50, places=2)
        self.assertAlmostEqual(
            summary["joint_travel_deg"],
            math.degrees(10.50 / 7.1844),
            places=2,
        )
        self.assertTrue(summary["repeatable"])

    def test_summary_marks_nonrepeatable_lower_limit_invalid(self):
        summary = self.module.build_limit_summary(
            lower_start_rad=-2.000,
            upper_rad=-12.500,
            lower_return_rad=-1.500,
            gear_ratio=7.1844,
            repeat_tolerance_motor_rad=0.10,
        )

        self.assertFalse(summary["repeatable"])
        self.assertAlmostEqual(summary["lower_repeat_error_motor_rad"], 0.50)
        self.assertIn("lower-limit repeat error", summary["validation_error"])


if __name__ == "__main__":
    unittest.main()
