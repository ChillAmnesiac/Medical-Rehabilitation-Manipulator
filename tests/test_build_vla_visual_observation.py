from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.build_vla_visual_observation import (
    Detection,
    build_visual_observation,
    parse_frame_size,
    read_yolo_detections,
)


class VisualObservationTest(unittest.TestCase):
    def test_reads_yolo_detections_in_pixel_space(self) -> None:
        with TemporaryDirectory() as temp_dir:
            label_path = Path(temp_dir) / "frame.txt"
            label_path.write_text("1 0.5 0.25 0.2 0.1 0.75\n", encoding="utf-8")

            detections = read_yolo_detections(label_path, ["end_effector", "gripper_tip"], (640, 480))

        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0].label, "gripper_tip")
        self.assertAlmostEqual(detections[0].confidence, 0.75)
        self.assertEqual(tuple(round(value, 2) for value in detections[0].bbox_xywh_px), (256.0, 96.0, 128.0, 48.0))

    def test_builds_dry_run_pixel_servo_hint_when_target_and_tip_exist(self) -> None:
        target = Detection(label="bottle", confidence=0.9, bbox_xywh_px=(300.0, 200.0, 80.0, 100.0))
        tip = Detection(label="gripper_tip", confidence=0.8, bbox_xywh_px=(220.0, 180.0, 40.0, 40.0))

        observation = build_visual_observation([tip], (640, 480), target=target, frame_id="mono_000003")

        self.assertEqual(observation["control_boundary"], "dry_run_not_motion_permission")
        self.assertEqual(observation["target_object"]["center_px"], [340.0, 250.0])
        self.assertEqual(observation["gripper_tip"]["center_px"], [240.0, 200.0])
        self.assertEqual(observation["pixel_servo_hint"]["dx_px"], 100.0)
        self.assertEqual(observation["pixel_servo_hint"]["dy_px"], 50.0)

    def test_parse_frame_size_accepts_common_formats(self) -> None:
        self.assertEqual(parse_frame_size("640x480"), (640, 480))
        self.assertEqual(parse_frame_size("640,480"), (640, 480))


if __name__ == "__main__":
    unittest.main()
