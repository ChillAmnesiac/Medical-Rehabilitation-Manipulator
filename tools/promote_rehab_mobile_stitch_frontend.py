#!/usr/bin/env python3
"""Promote a verified Stitch frontend export into web and Android WebView assets."""

from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
import sys
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qa_rehab_mobile_l1_frontend  # noqa: E402
import verify_rehab_mobile_webview_mirror  # noqa: E402


SCHEMA = "rehab-mobile-stitch-frontend-promotion/v1"
DEFAULT_WEB_DIR = Path("apps/web/public/rehab-arm-mobile")
DEFAULT_ANDROID_WWW_DIR = Path("apps/mobile/rehab-arm-android/www")
DEFAULT_OUTPUT_DIR = Path("artifacts/rehab-mobile-stitch-promotion")
PREFLIGHT_REPORT = "stitch-frontend-l1-preflight.json"
PROMOTION_REPORT = "stitch-frontend-promotion.json"
MIRROR_REPORT = "webview-mirror-verification.json"
FORBIDDEN_PROMOTION_FILE_PATTERNS = (
    "frontend-l1-*.json",
    "browser-qa*.json",
    "browser-metrics*.json",
    "stitch-frontend-*.json",
    "webview-mirror-verification.json",
    "rehab-mobile-frontend-release-manifest.json",
)


def _source_files(source_dir: Path) -> list[str]:
    return sorted(path.relative_to(source_dir).as_posix() for path in source_dir.rglob("*") if path.is_file())


def check_package_cleanliness(source_dir: Path) -> dict[str, Any]:
    files = _source_files(source_dir) if source_dir.is_dir() else []
    unexpected_files = [
        rel_path
        for rel_path in files
        if any(fnmatch.fnmatch(Path(rel_path).name, pattern) for pattern in FORBIDDEN_PROMOTION_FILE_PATTERNS)
    ]
    return {
        "status": "PASS" if not unexpected_files else "FAIL",
        "unexpected_files": unexpected_files,
        "forbidden_patterns": list(FORBIDDEN_PROMOTION_FILE_PATTERNS),
    }


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _validate_copy_targets(source_dir: Path, output_dir: Path, targets: list[Path]) -> None:
    source = source_dir.resolve()
    output = output_dir.resolve()
    for target in targets:
        resolved = target.resolve()
        if resolved == Path(resolved.anchor):
            raise ValueError("unsafe_replace_target_root")
        if resolved == source or _is_relative_to(resolved, source):
            raise ValueError("target_inside_stitch_source")
        if _is_relative_to(source, resolved):
            raise ValueError("stitch_source_inside_replace_target")
        if resolved == output or _is_relative_to(output, resolved):
            raise ValueError("output_dir_inside_replace_target")


def _replace_dir_contents(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for child in target_dir.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    for rel_path in _source_files(source_dir):
        source_path = source_dir / rel_path
        target_path = target_dir / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)


def run_frontend_l1_preflight(source_dir: Path, report_path: Path, timeout: int) -> dict[str, Any]:
    args = qa_rehab_mobile_l1_frontend.parse_args(
        ["--source-dir", str(source_dir), "--timeout", str(timeout)]
    )
    _, payload = qa_rehab_mobile_l1_frontend.run(args)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = dict(payload.get("summary") or {})
    summary["report_path"] = str(report_path)
    return summary


def _base_payload(
    args: argparse.Namespace,
    preflight_summary: dict[str, Any],
    package_cleanliness: dict[str, Any],
) -> dict[str, Any]:
    copied = False
    overall = (
        "PASS"
        if preflight_summary.get("overall") == "PASS" and package_cleanliness.get("status") == "PASS"
        else "FAIL"
    )
    return {
        "schema": SCHEMA,
        "summary": {
            "overall": overall,
            "dry_run": not args.execute,
            "copied": copied,
        },
        "source": {"stitch_source_dir": str(args.stitch_source_dir)},
        "targets": {
            "web_dir": str(args.web_dir),
            "android_www_dir": str(args.android_www_dir),
        },
        "plan": {
            "files_to_promote": _source_files(args.stitch_source_dir) if args.stitch_source_dir.is_dir() else [],
            "replace_targets": [str(args.web_dir), str(args.android_www_dir)],
        },
        "frontend_l1_preflight": preflight_summary,
        "package_cleanliness": package_cleanliness,
    }


def _early_error_payload(args: argparse.Namespace, error: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "summary": {
            "overall": "FAIL",
            "dry_run": not args.execute,
            "copied": False,
            "error": error,
        },
        "source": {"stitch_source_dir": str(args.stitch_source_dir)},
        "targets": {
            "web_dir": str(args.web_dir),
            "android_www_dir": str(args.android_www_dir),
        },
        "plan": {
            "files_to_promote": _source_files(args.stitch_source_dir) if args.stitch_source_dir.is_dir() else [],
            "replace_targets": [str(args.web_dir), str(args.android_www_dir)],
        },
    }


def run(argv: list[str]) -> tuple[int, dict[str, Any]]:
    args = parse_args(argv)
    if args.execute:
        try:
            _validate_copy_targets(args.stitch_source_dir, args.output_dir, [args.web_dir, args.android_www_dir])
        except ValueError as exc:
            return 2, _early_error_payload(args, str(exc))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    preflight_summary = run_frontend_l1_preflight(
        args.stitch_source_dir,
        args.output_dir / PREFLIGHT_REPORT,
        args.timeout,
    )
    package_cleanliness = check_package_cleanliness(args.stitch_source_dir)
    payload = _base_payload(args, preflight_summary, package_cleanliness)
    if preflight_summary.get("overall") != "PASS" or package_cleanliness.get("status") != "PASS":
        report_path = args.output_dir / PROMOTION_REPORT
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 2, payload
    if not args.execute:
        report_path = args.output_dir / PROMOTION_REPORT
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0, payload

    _replace_dir_contents(args.stitch_source_dir, args.web_dir)
    _replace_dir_contents(args.stitch_source_dir, args.android_www_dir)
    mirror_report = verify_rehab_mobile_webview_mirror.verify_webview_mirror(
        args.web_dir,
        args.android_www_dir,
    )
    mirror_path = args.output_dir / MIRROR_REPORT
    mirror_path.write_text(json.dumps(mirror_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mirror_summary = dict(mirror_report.get("summary") or {})
    mirror_summary["report_path"] = str(mirror_path)
    payload["webview_mirror"] = mirror_summary
    payload["summary"]["copied"] = True
    payload["summary"]["overall"] = "PASS" if mirror_summary.get("overall") == "PASS" else "FAIL"
    report_path = args.output_dir / PROMOTION_REPORT
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return (0 if payload["summary"]["overall"] == "PASS" else 2), payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stitch-source-dir", type=Path, required=True)
    parser.add_argument("--web-dir", type=Path, default=DEFAULT_WEB_DIR)
    parser.add_argument("--android-www-dir", type=Path, default=DEFAULT_ANDROID_WWW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    exit_code, payload = run(argv)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
