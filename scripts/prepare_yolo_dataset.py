#!/usr/bin/env python3
"""
Convert AnyLabeling/LabelMe rectangle JSON files into a YOLO dataset.

This does not modify source images or source JSON annotations. It creates:

  <out>/images/train|val
  <out>/labels/train|val
  <out>/data.yaml
  <out>/conversion_report.json
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CLASSES = ["target_cup", "target_bottle", "end_effector", "gripper_tip"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


@dataclass
class ConvertStats:
    images_seen: int = 0
    json_seen: int = 0
    images_written: int = 0
    labels_written: int = 0
    boxes_written: int = 0
    skipped_no_json: int = 0
    skipped_empty_json: int = 0
    skipped_unknown_label: int = 0
    skipped_bad_shape: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare YOLO dataset from AnyLabeling JSON annotations.")
    parser.add_argument("--images", required=True, help="Directory containing images and AnyLabeling JSON files.")
    parser.add_argument("--out", required=True, help="Output YOLO dataset directory.")
    parser.add_argument("--classes", default=",".join(DEFAULT_CLASSES), help="Comma-separated class names in YOLO id order.")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Validation split ratio.")
    parser.add_argument("--seed", type=int, default=20260629, help="Deterministic split seed.")
    parser.add_argument(
        "--include-unlabeled-images",
        action="store_true",
        help="Include images without JSON or boxes as negative samples with empty label files.",
    )
    return parser.parse_args()


def load_classes(value: str) -> list[str]:
    classes = [item.strip() for item in value.split(",") if item.strip()]
    if not classes:
        raise SystemExit("At least one class is required")
    if len(set(classes)) != len(classes):
        raise SystemExit(f"Duplicate classes are not allowed: {classes}")
    return classes


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def rectangle_to_yolo(points: list[list[float]], width: int, height: int) -> tuple[float, float, float, float] | None:
    if len(points) < 2 or width <= 0 or height <= 0:
        return None

    xs = [float(point[0]) for point in points[:2]]
    ys = [float(point[1]) for point in points[:2]]
    x1 = clamp(min(xs), 0.0, float(width))
    x2 = clamp(max(xs), 0.0, float(width))
    y1 = clamp(min(ys), 0.0, float(height))
    y2 = clamp(max(ys), 0.0, float(height))
    box_w = x2 - x1
    box_h = y2 - y1
    if box_w <= 1.0 or box_h <= 1.0:
        return None

    x_center = (x1 + x2) / 2.0 / width
    y_center = (y1 + y2) / 2.0 / height
    norm_w = box_w / width
    norm_h = box_h / height
    return x_center, y_center, norm_w, norm_h


def convert_annotation(json_path: Path, classes: list[str], stats: ConvertStats) -> list[str]:
    data: dict[str, Any] = json.loads(json_path.read_text(encoding="utf-8"))
    width = int(data.get("imageWidth") or 0)
    height = int(data.get("imageHeight") or 0)
    class_to_id = {name: index for index, name in enumerate(classes)}
    lines: list[str] = []

    for shape in data.get("shapes", []):
        if shape.get("shape_type") != "rectangle":
            stats.skipped_bad_shape += 1
            continue
        label = str(shape.get("label", "")).strip()
        if label not in class_to_id:
            stats.skipped_unknown_label += 1
            continue
        converted = rectangle_to_yolo(shape.get("points") or [], width, height)
        if converted is None:
            stats.skipped_bad_shape += 1
            continue
        x_center, y_center, box_w, box_h = converted
        lines.append(
            f"{class_to_id[label]} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}"
        )
    return lines


def image_files(root: Path) -> list[Path]:
    return sorted(path for path in root.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)


def write_data_yaml(out_dir: Path, classes: list[str]) -> None:
    names = ", ".join(f"'{name}'" for name in classes)
    text = (
        f"path: {out_dir.as_posix()}\n"
        "train: images/train\n"
        "val: images/val\n\n"
        f"nc: {len(classes)}\n"
        f"names: [{names}]\n"
    )
    (out_dir / "data.yaml").write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    images_dir = Path(args.images)
    out_dir = Path(args.out)
    classes = load_classes(args.classes)
    if not images_dir.is_dir():
        raise SystemExit(f"Missing images directory: {images_dir}")
    if not 0.0 <= args.val_ratio < 1.0:
        raise SystemExit("--val-ratio must be in [0, 1)")

    stats = ConvertStats()
    images = image_files(images_dir)
    stats.images_seen = len(images)

    annotated_items: list[tuple[Path, list[str]]] = []
    for image_path in images:
        json_path = image_path.with_suffix(".json")
        if not json_path.exists():
            stats.skipped_no_json += 1
            if args.include_unlabeled_images:
                annotated_items.append((image_path, []))
            continue
        stats.json_seen += 1
        lines = convert_annotation(json_path, classes, stats)
        if not lines:
            stats.skipped_empty_json += 1
            if not args.include_unlabeled_images:
                continue
        annotated_items.append((image_path, lines))

    rng = random.Random(args.seed)
    rng.shuffle(annotated_items)
    val_count = int(round(len(annotated_items) * args.val_ratio))
    val_items = set(path for path, _ in annotated_items[:val_count])

    for split in ["train", "val"]:
        (out_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (out_dir / "labels" / split).mkdir(parents=True, exist_ok=True)

    for image_path, lines in annotated_items:
        split = "val" if image_path in val_items else "train"
        target_image = out_dir / "images" / split / image_path.name
        target_label = out_dir / "labels" / split / f"{image_path.stem}.txt"
        shutil.copy2(image_path, target_image)
        target_label.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        stats.images_written += 1
        stats.labels_written += 1
        stats.boxes_written += len(lines)

    write_data_yaml(out_dir, classes)
    report = {
        "source_images": str(images_dir),
        "output": str(out_dir),
        "classes": classes,
        "val_ratio": args.val_ratio,
        "stats": stats.__dict__,
    }
    (out_dir / "conversion_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
