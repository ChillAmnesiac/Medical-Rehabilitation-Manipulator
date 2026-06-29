#!/usr/bin/env python3
"""
Build a dry-run VLA visual observation JSON from detector outputs.

This is an offline/additive bridge for the current V-side work. It accepts the
custom end-effector YOLO labels and an optional target bbox from a general
object detector. It does not command motion.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_CLASSES = ["end_effector", "gripper_tip"]


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    bbox_xywh_px: tuple[float, float, float, float]

    @property
    def center_px(self) -> tuple[float, float]:
        x, y, width, height = self.bbox_xywh_px
        return x + width / 2.0, y + height / 2.0


def parse_frame_size(value: str) -> tuple[int, int]:
    parts = [part.strip() for part in value.lower().replace("x", ",").split(",") if part.strip()]
    if len(parts) != 2:
        raise ValueError("frame size must be WIDTHxHEIGHT or WIDTH,HEIGHT")
    width, height = int(parts[0]), int(parts[1])
    if width <= 0 or height <= 0:
        raise ValueError("frame size must be positive")
    return width, height


def parse_target_bbox(value: str, label: str) -> Detection:
    parts = [float(part.strip()) for part in value.split(",") if part.strip()]
    if len(parts) not in {4, 5}:
        raise ValueError("target bbox must be x,y,w,h or x,y,w,h,confidence")
    confidence = parts[4] if len(parts) == 5 else 1.0
    return Detection(label=label, confidence=confidence, bbox_xywh_px=(parts[0], parts[1], parts[2], parts[3]))


def read_yolo_detections(
    label_path: Path,
    classes: list[str],
    frame_size_px: tuple[int, int],
) -> list[Detection]:
    width, height = frame_size_px
    detections: list[Detection] = []
    if not label_path.exists():
        return detections

    for line_number, raw_line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) not in {5, 6}:
            raise ValueError(f"{label_path}:{line_number} expected YOLO class xc yc w h [conf]")
        class_id = int(float(parts[0]))
        if class_id < 0 or class_id >= len(classes):
            raise ValueError(f"{label_path}:{line_number} class id {class_id} is outside class list")
        x_center, y_center, box_w, box_h = (float(value) for value in parts[1:5])
        confidence = float(parts[5]) if len(parts) == 6 else 1.0
        bbox_w = box_w * width
        bbox_h = box_h * height
        bbox_x = x_center * width - bbox_w / 2.0
        bbox_y = y_center * height - bbox_h / 2.0
        detections.append(
            Detection(
                label=classes[class_id],
                confidence=confidence,
                bbox_xywh_px=(bbox_x, bbox_y, bbox_w, bbox_h),
            )
        )
    return detections


def best_detection(detections: Iterable[Detection], label: str) -> Detection | None:
    candidates = [detection for detection in detections if detection.label == label]
    if not candidates:
        return None
    return max(candidates, key=lambda detection: detection.confidence)


def _round_tuple(values: tuple[float, ...], digits: int = 2) -> list[float]:
    return [round(value, digits) for value in values]


def _detection_json(detection: Detection | None) -> dict | None:
    if detection is None:
        return None
    return {
        "label": detection.label,
        "confidence": round(detection.confidence, 4),
        "bbox_xywh_px": _round_tuple(detection.bbox_xywh_px),
        "center_px": _round_tuple(detection.center_px),
    }


def build_visual_observation(
    detections: list[Detection],
    frame_size_px: tuple[int, int],
    target: Detection | None = None,
    frame_id: str = "",
) -> dict:
    end_effector = best_detection(detections, "end_effector")
    gripper_tip = best_detection(detections, "gripper_tip")
    servo_origin = gripper_tip or end_effector
    pixel_servo_hint = None

    if target is not None and servo_origin is not None:
        target_x, target_y = target.center_px
        origin_x, origin_y = servo_origin.center_px
        dx = target_x - origin_x
        dy = target_y - origin_y
        frame_w, frame_h = frame_size_px
        pixel_servo_hint = {
            "dx_px": round(dx, 2),
            "dy_px": round(dy, 2),
            "dx_norm": round(dx / max(frame_w, 1), 4),
            "dy_norm": round(dy / max(frame_h, 1), 4),
        }

    return {
        "schema_version": "rehab_vla_visual_observation_v1",
        "frame_id": frame_id,
        "frame_size_px": list(frame_size_px),
        "control_boundary": "dry_run_not_motion_permission",
        "target_object": _detection_json(target),
        "end_effector": _detection_json(end_effector),
        "gripper_tip": _detection_json(gripper_tip),
        "pixel_servo_hint": pixel_servo_hint,
        "metric_depth_available": False,
        "detections": [asdict(detection) for detection in detections],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build VLA visual observation JSON from YOLO detections.")
    parser.add_argument("--labels", required=True, help="YOLO detection .txt from the end-effector model.")
    parser.add_argument("--frame-size", default="640x480", help="Frame size as WIDTHxHEIGHT.")
    parser.add_argument("--classes", default=",".join(DEFAULT_CLASSES), help="Comma-separated class names.")
    parser.add_argument("--frame-id", default="", help="Optional frame/image id for traceability.")
    parser.add_argument("--target-label", default="bottle", help="Target object label from L grounding/general detector.")
    parser.add_argument("--target-bbox", default="", help="Optional target bbox: x,y,w,h[,confidence] in pixels.")
    parser.add_argument("--out", default="", help="Optional output JSON path. Prints to stdout when omitted.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    classes = [item.strip() for item in args.classes.split(",") if item.strip()]
    frame_size_px = parse_frame_size(args.frame_size)
    detections = read_yolo_detections(Path(args.labels), classes, frame_size_px)
    target = parse_target_bbox(args.target_bbox, args.target_label) if args.target_bbox else None
    observation = build_visual_observation(detections, frame_size_px, target=target, frame_id=args.frame_id)
    text = json.dumps(observation, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
