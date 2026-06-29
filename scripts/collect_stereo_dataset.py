#!/usr/bin/env python3
"""
Stereo dataset capture tool for VLA target/end-effector detection.

Use this on NanoPi or a Windows PC after the two USB cameras are fixed. It
captures left/right pairs plus JSONL metadata that can be used for labeling and
later training.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2


DEFAULT_CLASSES = [
    "target_cup",
    "target_bottle",
    "end_effector",
    "gripper_tip",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture synchronized-ish stereo image pairs for VLA labeling."
    )
    parser.add_argument("--mode", default="mono", choices=["mono", "stereo"], help="Capture one camera or stereo pair.")
    parser.add_argument("--camera", default="2", help="Mono camera index or /dev/video path.")
    parser.add_argument("--left", default="2", help="Left camera index or /dev/video path.")
    parser.add_argument("--right", default="3", help="Right camera index or /dev/video path.")
    parser.add_argument("--out", default="D:/vla_dataset", help="Dataset root directory.")
    parser.add_argument("--session", default=None, help="Session name. Defaults to timestamp.")
    parser.add_argument("--width", type=int, default=640, help="Capture width.")
    parser.add_argument("--height", type=int, default=480, help="Capture height.")
    parser.add_argument("--fps", type=int, default=15, help="Requested camera FPS.")
    parser.add_argument(
        "--backend",
        default="dshow",
        choices=["auto", "any", "v4l2", "dshow", "msmf"],
        help="OpenCV camera backend. Windows usually works best with dshow or msmf.",
    )
    parser.add_argument("--list-cameras", action="store_true", help="Probe camera indexes 0..9 and exit.")
    parser.add_argument("--baseline-m", type=float, default=0.06, help="Stereo baseline in meters.")
    parser.add_argument("--interval-ms", type=int, default=500, help="Auto burst interval.")
    parser.add_argument("--count", type=int, default=0, help="Auto burst frame-pair count. 0 means manual.")
    parser.add_argument("--note", default="", help="Operator/session note written into metadata.")
    parser.add_argument("--headless", action="store_true", help="No preview window; capture by count.")
    parser.add_argument("--flip-left", default="none", choices=["none", "h", "v", "hv"], help="Flip left frame.")
    parser.add_argument("--flip-right", default="hv", choices=["none", "h", "v", "hv"], help="Flip right frame.")
    return parser.parse_args()


def camera_source(value: str) -> int | str:
    return int(value) if value.isdigit() else value


def backend_id(name: str) -> int:
    if name == "any":
        return cv2.CAP_ANY
    if name == "v4l2":
        return cv2.CAP_V4L2
    if name == "dshow":
        return cv2.CAP_DSHOW
    if name == "msmf":
        return cv2.CAP_MSMF
    if platform.system().lower().startswith("win"):
        return cv2.CAP_DSHOW
    if platform.system().lower() == "linux":
        return cv2.CAP_V4L2
    return cv2.CAP_ANY


def backend_candidates(name: str) -> list[str]:
    if name != "auto":
        return [name]
    if platform.system().lower().startswith("win"):
        return ["dshow", "msmf", "any"]
    if platform.system().lower() == "linux":
        return ["v4l2", "any"]
    return ["any"]


def open_camera(source: int | str, width: int, height: int, fps: int, backend: str) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(source, backend_id(backend))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera: {source}")

    if backend in {"v4l2", "dshow"}:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def open_camera_pair(args: argparse.Namespace) -> tuple[cv2.VideoCapture, cv2.VideoCapture, str]:
    left_source = camera_source(args.left)
    right_source = camera_source(args.right)
    last_error = ""
    for backend in backend_candidates(args.backend):
        left_cap = None
        right_cap = None
        try:
            left_cap = open_camera(left_source, args.width, args.height, args.fps, backend)
            right_cap = open_camera(right_source, args.width, args.height, args.fps, backend)
            print(f"[camera] opened left={args.left} right={args.right} backend={backend}")
            return left_cap, right_cap, backend
        except Exception as exc:
            last_error = f"{backend}: {exc}"
            if left_cap is not None:
                left_cap.release()
            if right_cap is not None:
                right_cap.release()
            print(f"[camera] backend {backend} failed: {exc}")
            time.sleep(0.5)
    raise RuntimeError(f"Cannot open stereo cameras left={args.left} right={args.right}. Last error: {last_error}")


def list_cameras(backend: str) -> None:
    print(f"[probe] backend={backend} platform={platform.system()}")
    for index in range(10):
        cap = cv2.VideoCapture(index, backend_id(backend))
        ok = cap.isOpened()
        if ok:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            grabbed, frame = cap.read()
            shape = f"{frame.shape[1]}x{frame.shape[0]}" if grabbed and frame is not None else "opened/no-frame"
            print(f"[camera] index={index} {shape}")
        cap.release()


def flip_frame(frame: Any, mode: str) -> Any:
    if mode == "h":
        return cv2.flip(frame, 1)
    if mode == "v":
        return cv2.flip(frame, 0)
    if mode == "hv":
        return cv2.flip(frame, -1)
    return frame


def read_pair(
    left_cap: cv2.VideoCapture,
    right_cap: cv2.VideoCapture,
    left_flip: str,
    right_flip: str,
) -> tuple[Any, Any]:
    # grab/retrieve keeps the two frames closer in time than sequential read().
    left_cap.grab()
    right_cap.grab()
    ok_left, left_frame = left_cap.retrieve()
    ok_right, right_frame = right_cap.retrieve()
    if not ok_left or left_frame is None:
        raise RuntimeError("Failed to read left camera frame")
    if not ok_right or right_frame is None:
        raise RuntimeError("Failed to read right camera frame")
    return flip_frame(left_frame, left_flip), flip_frame(right_frame, right_flip)


def warmup_pair(
    left_cap: cv2.VideoCapture,
    right_cap: cv2.VideoCapture,
    left_flip: str,
    right_flip: str,
) -> tuple[Any, Any]:
    last_pair = None
    last_error = None
    for _ in range(20):
        try:
            last_pair = read_pair(left_cap, right_cap, left_flip, right_flip)
            if last_pair[0].size and last_pair[1].size:
                return last_pair
        except RuntimeError as exc:
            last_error = exc
        time.sleep(0.05)
    if last_pair is not None:
        return last_pair
    raise RuntimeError(f"Stereo cameras opened but did not return frames: {last_error}")


def write_labeling_readme(session_dir: Path, args: argparse.Namespace) -> None:
    text = f"""# VLA Stereo Labeling Session

Session: `{session_dir.name}`
Baseline: `{args.baseline_m}` m

## Label Classes

- `target_cup`: cup to fetch, including handle if visible.
- `target_bottle`: bottle to fetch.
- `end_effector`: whole visible gripper/end-effector assembly.
- `gripper_tip`: the contact tip or fingertip area when it is visible enough.

## Labeling Rules

- Label left and right images with the same class names.
- Draw boxes only around real visible pixels. Do not invent occluded parts.
- Prefer one tight box per object. If the gripper has two fingers, use
  `end_effector` for the whole end and optional `gripper_tip` for the useful tip.
- Keep negative samples. Frames with only the target, only the end-effector, or
  neither are useful for reducing false detections.
- Mark blurred or partially blocked objects if a human can still identify them.

## Minimum Useful Dataset

- 80+ stereo pairs with target and end-effector both visible.
- 40+ target-only pairs.
- 40+ end-effector-only pairs.
- 40+ negative/background pairs.
- Cover near/mid/far distances, left/right image areas, table clutter, and lighting changes.

## Phone Photos

Phone photos can supplement class appearance, but keep them in a separate
`phone_images/` folder because they do not have stereo geometry. They are useful
for generic cup/bottle/end-effector detection, not depth.
"""
    (session_dir / "labels" / "README_LABELING.md").write_text(text, encoding="utf-8")


def create_session(args: argparse.Namespace) -> tuple[Path, Path]:
    session_name = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Path(args.out) / session_name
    for child in ["images/mono", "images/left", "images/right", "meta", "labels", "phone_images"]:
        (session_dir / child).mkdir(parents=True, exist_ok=True)
    write_labeling_readme(session_dir, args)
    return session_dir, session_dir / "meta" / "frames.jsonl"


def save_pair(
    session_dir: Path,
    meta_path: Path,
    index: int,
    left_frame: Any,
    right_frame: Any,
    args: argparse.Namespace,
) -> None:
    timestamp = datetime.now().isoformat(timespec="milliseconds")
    stem = f"{index:06d}"
    left_rel = f"images/left/left_{stem}.jpg"
    right_rel = f"images/right/right_{stem}.jpg"
    left_path = session_dir / left_rel
    right_path = session_dir / right_rel

    cv2.imwrite(str(left_path), left_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    cv2.imwrite(str(right_path), right_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])

    record = {
        "frame_pair_id": stem,
        "timestamp": timestamp,
        "left_image": left_rel,
        "right_image": right_rel,
        "left_camera": args.left,
        "right_camera": args.right,
        "resolution": {"width": int(left_frame.shape[1]), "height": int(left_frame.shape[0])},
        "baseline_m": args.baseline_m,
        "classes": DEFAULT_CLASSES,
        "operator_note": args.note,
        "capture_host": platform.node(),
        "dry_run_motion": True,
    }
    with meta_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_mono(
    session_dir: Path,
    meta_path: Path,
    index: int,
    frame: Any,
    args: argparse.Namespace,
) -> None:
    timestamp = datetime.now().isoformat(timespec="milliseconds")
    stem = f"{index:06d}"
    image_rel = f"images/mono/mono_{stem}.jpg"
    image_path = session_dir / image_rel

    cv2.imwrite(str(image_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])

    record = {
        "frame_id": stem,
        "timestamp": timestamp,
        "image": image_rel,
        "camera": args.camera,
        "resolution": {"width": int(frame.shape[1]), "height": int(frame.shape[0])},
        "classes": DEFAULT_CLASSES,
        "operator_note": args.note,
        "capture_host": platform.node(),
        "capture_mode": "mono",
        "dry_run_motion": True,
    }
    with meta_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def draw_mono_preview(frame: Any, index: int, auto_mode: bool) -> Any:
    preview = frame.copy()
    cv2.putText(preview, "MONO CAM", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 220, 40), 2)
    status = f"frames={index}  space:save  a:auto  q:quit"
    if auto_mode:
        status += "  AUTO"
    cv2.putText(preview, status, (12, preview.shape[0] - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 2)
    return preview


def draw_preview(left_frame: Any, right_frame: Any, index: int, auto_mode: bool) -> Any:
    left = left_frame.copy()
    right = right_frame.copy()
    cv2.putText(left, "LEFT", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 220, 40), 2)
    cv2.putText(right, "RIGHT", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 220, 40), 2)
    stereo = cv2.hconcat([left, right])
    status = f"pairs={index}  space:save  a:auto  q:quit"
    if auto_mode:
        status += "  AUTO"
    cv2.putText(stereo, status, (12, stereo.shape[0] - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 2)
    return stereo


def run_mono(args: argparse.Namespace) -> int:
    cap = open_camera(camera_source(args.camera), args.width, args.height, args.fps, args.backend)
    first_frame = None
    for _ in range(20):
        ok, frame = cap.read()
        if ok and frame is not None:
            first_frame = flip_frame(frame, args.flip_left)
            break
        time.sleep(0.05)
    if first_frame is None:
        cap.release()
        raise RuntimeError(f"Mono camera {args.camera} opened but did not return frames")

    session_dir, meta_path = create_session(args)
    print(f"[dataset] session: {session_dir}")
    print(f"[dataset] metadata: {meta_path}")
    print("[control] space=save frame, a=toggle auto, q=quit")
    print(f"[preview] mono realtime window is on. camera={args.camera}, flip={args.flip_left}, backend={args.backend}")

    frame_index = 0
    auto_mode = args.count > 0
    last_auto_capture = 0.0
    first_preview = True

    try:
        while True:
            if first_preview:
                frame = first_frame
                first_preview = False
            else:
                ok, raw = cap.read()
                if not ok or raw is None:
                    raise RuntimeError("Failed to read mono camera frame")
                frame = flip_frame(raw, args.flip_left)
            now = time.monotonic()

            should_save = False
            if args.count > 0:
                should_save = frame_index < args.count and (now - last_auto_capture) * 1000 >= args.interval_ms
            elif auto_mode:
                should_save = (now - last_auto_capture) * 1000 >= args.interval_ms

            if should_save:
                frame_index += 1
                save_mono(session_dir, meta_path, frame_index, frame, args)
                last_auto_capture = now
                print(f"[saved] frame {frame_index:06d}")
                if args.count > 0 and frame_index >= args.count:
                    break

            if args.headless:
                time.sleep(0.01)
                continue

            cv2.imshow("vla-mono-capture", draw_mono_preview(frame, frame_index, auto_mode))
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                frame_index += 1
                save_mono(session_dir, meta_path, frame_index, frame, args)
                print(f"[saved] frame {frame_index:06d}")
            if key == ord("a"):
                auto_mode = not auto_mode
                print(f"[auto] {'on' if auto_mode else 'off'}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

    print(f"[done] saved {frame_index} mono frames in {session_dir}")
    return 0


def run_stereo(args: argparse.Namespace) -> int:
    left_cap, right_cap, active_backend = open_camera_pair(args)
    first_left, first_right = warmup_pair(left_cap, right_cap, args.flip_left, args.flip_right)
    session_dir, meta_path = create_session(args)
    print(f"[dataset] session: {session_dir}")
    print(f"[dataset] metadata: {meta_path}")
    print("[control] space=save pair, a=toggle auto, q=quit")
    print(f"[preview] realtime window is on. left flip={args.flip_left}, right flip={args.flip_right}, backend={active_backend}")

    pair_index = 0
    auto_mode = args.count > 0
    last_auto_capture = 0.0
    first_preview = True

    try:
        while True:
            if first_preview:
                left_frame, right_frame = first_left, first_right
                first_preview = False
            else:
                left_frame, right_frame = read_pair(left_cap, right_cap, args.flip_left, args.flip_right)
            now = time.monotonic()

            should_save = False
            if args.count > 0:
                should_save = pair_index < args.count and (now - last_auto_capture) * 1000 >= args.interval_ms
            elif auto_mode:
                should_save = (now - last_auto_capture) * 1000 >= args.interval_ms

            if should_save:
                pair_index += 1
                save_pair(session_dir, meta_path, pair_index, left_frame, right_frame, args)
                last_auto_capture = now
                print(f"[saved] pair {pair_index:06d}")
                if args.count > 0 and pair_index >= args.count:
                    break

            if args.headless:
                time.sleep(0.01)
                continue

            cv2.imshow("vla-stereo-capture", draw_preview(left_frame, right_frame, pair_index, auto_mode))
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                pair_index += 1
                save_pair(session_dir, meta_path, pair_index, left_frame, right_frame, args)
                print(f"[saved] pair {pair_index:06d}")
            if key == ord("a"):
                auto_mode = not auto_mode
                print(f"[auto] {'on' if auto_mode else 'off'}")
    finally:
        left_cap.release()
        right_cap.release()
        cv2.destroyAllWindows()

    print(f"[done] saved {pair_index} stereo pairs in {session_dir}")
    return 0


def main() -> int:
    args = parse_args()
    if args.list_cameras:
        list_cameras(args.backend)
        return 0
    if args.headless and args.count <= 0:
        raise SystemExit("--headless needs --count > 0")

    if args.mode == "mono":
        return run_mono(args)
    return run_stereo(args)


if __name__ == "__main__":
    raise SystemExit(main())
