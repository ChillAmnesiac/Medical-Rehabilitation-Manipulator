#!/usr/bin/env python3
"""Verify Android WebView assets mirror the accepted rehab mobile web frontend."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA = "rehab-mobile-webview-mirror-verification/v1"
DEFAULT_WEB_DIR = Path("apps/web/public/rehab-arm-mobile")
DEFAULT_ANDROID_WWW_DIR = Path("apps/mobile/rehab-arm-android/www")
REQUIRED_PAGES = ("home.html", "profile.html", "device.html", "ai-plan.html")


@dataclass
class Result:
    gate: str
    level: str
    status: str
    summary: str
    detail: Any = None


def _result(gate: str, ok: bool, summary: str, detail: Any = None) -> Result:
    return Result(
        gate=gate,
        level="L1",
        status="PASS" if ok else "FAIL",
        summary=summary,
        detail=detail,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_map(root: Path) -> dict[str, dict[str, Any]]:
    if not root.exists() or not root.is_dir():
        return {}
    files: dict[str, dict[str, Any]] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel_path = path.relative_to(root).as_posix()
        files[rel_path] = {
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
    return files


def _check_directories(web_dir: Path, android_www_dir: Path) -> Result:
    web_ok = web_dir.exists() and web_dir.is_dir()
    android_ok = android_www_dir.exists() and android_www_dir.is_dir()
    return _result(
        "WEBVIEW-MIRROR-DIRECTORIES",
        web_ok and android_ok,
        "Web frontend source and Android WebView mirror directories exist.",
        {
            "web_dir": str(web_dir),
            "web_dir_exists": web_ok,
            "android_www_dir": str(android_www_dir),
            "android_www_dir_exists": android_ok,
        },
    )


def _check_required_pages(
    web_files: dict[str, dict[str, Any]],
    android_files: dict[str, dict[str, Any]],
) -> Result:
    missing_web_pages = [page for page in REQUIRED_PAGES if page not in web_files]
    missing_android_pages = [page for page in REQUIRED_PAGES if page not in android_files]
    mismatched_required_pages = [
        page
        for page in REQUIRED_PAGES
        if page in web_files
        and page in android_files
        and web_files[page]["sha256"] != android_files[page]["sha256"]
    ]
    ok = not missing_web_pages and not missing_android_pages and not mismatched_required_pages
    return _result(
        "WEBVIEW-MIRROR-REQUIRED-PAGES",
        ok,
        "Required mobile pages are present and byte-identical in the Android WebView mirror.",
        {
            "required_pages": list(REQUIRED_PAGES),
            "missing_web_pages": missing_web_pages,
            "missing_android_pages": missing_android_pages,
            "mismatched_required_pages": mismatched_required_pages,
        },
    )


def _check_file_parity(
    web_files: dict[str, dict[str, Any]],
    android_files: dict[str, dict[str, Any]],
) -> Result:
    web_names = set(web_files)
    android_names = set(android_files)
    missing_files = sorted(web_names - android_names)
    extra_files = sorted(android_names - web_names)
    changed_files = sorted(
        name
        for name in web_names & android_names
        if web_files[name]["sha256"] != android_files[name]["sha256"]
    )
    ok = not missing_files and not extra_files and not changed_files
    return _result(
        "WEBVIEW-MIRROR-FILE-PARITY",
        ok,
        "Every accepted web frontend file is mirrored into Android www without stale extras.",
        {
            "missing_files": missing_files,
            "extra_files": extra_files,
            "changed_files": changed_files,
        },
    )


def verify_webview_mirror(web_dir: Path, android_www_dir: Path) -> dict[str, Any]:
    web_dir = Path(web_dir)
    android_www_dir = Path(android_www_dir)
    web_files = _file_map(web_dir)
    android_files = _file_map(android_www_dir)
    results = [
        _check_directories(web_dir, android_www_dir),
        _check_required_pages(web_files, android_files),
        _check_file_parity(web_files, android_files),
    ]
    failed = [result for result in results if result.status == "FAIL"]
    return {
        "schema": SCHEMA,
        "target": {
            "web_dir": str(web_dir),
            "android_www_dir": str(android_www_dir),
            "required_pages": list(REQUIRED_PAGES),
        },
        "summary": {
            "overall": "FAIL" if failed else "PASS",
            "failed": len(failed),
            "total": len(results),
            "web_file_count": len(web_files),
            "android_file_count": len(android_files),
        },
        "results": [result.__dict__ for result in results],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web-dir", type=Path, default=DEFAULT_WEB_DIR)
    parser.add_argument("--android-www-dir", type=Path, default=DEFAULT_ANDROID_WWW_DIR)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = verify_webview_mirror(args.web_dir, args.android_www_dir)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
