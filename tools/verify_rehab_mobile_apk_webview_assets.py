#!/usr/bin/env python3
"""Verify a rehab mobile APK contains the accepted Android WebView assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA = "rehab-mobile-apk-webview-assets-verification/v1"
DEFAULT_APK = Path("apps/web/public/downloads/rehab-arm/lingdong-rehab-arm-debug.apk")
DEFAULT_ANDROID_WWW_DIR = Path("apps/mobile/rehab-arm-android/www")
DEFAULT_ASSET_PREFIX = "assets/public"
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


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _android_file_map(root: Path) -> dict[str, dict[str, Any]]:
    if not root.exists() or not root.is_dir():
        return {}
    files: dict[str, dict[str, Any]] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel_path = path.relative_to(root).as_posix()
        files[rel_path] = {
            "bytes": path.stat().st_size,
            "sha256": _sha256_path(path),
        }
    return files


def _normalized_prefix(asset_prefix: str) -> str:
    return asset_prefix.strip("/").replace("\\", "/")


def _apk_webview_file_map(apk_path: Path, asset_prefix: str) -> dict[str, dict[str, Any]]:
    if not apk_path.is_file():
        return {}
    prefix = _normalized_prefix(asset_prefix)
    prefix_with_slash = f"{prefix}/"
    files: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(apk_path) as apk:
        for info in apk.infolist():
            name = info.filename.replace("\\", "/")
            if info.is_dir() or not name.startswith(prefix_with_slash):
                continue
            rel_path = name[len(prefix_with_slash) :]
            if not rel_path:
                continue
            data = apk.read(info)
            files[rel_path] = {
                "bytes": len(data),
                "sha256": _sha256_bytes(data),
                "apk_entry": name,
            }
    return files


def _check_inputs(apk_path: Path, android_www_dir: Path, asset_prefix: str) -> Result:
    apk_ok = apk_path.is_file()
    android_ok = android_www_dir.exists() and android_www_dir.is_dir()
    prefix_ok = bool(_normalized_prefix(asset_prefix))
    return _result(
        "APK-WEBVIEW-INPUTS",
        apk_ok and android_ok and prefix_ok,
        "APK file, Android WebView source directory, and APK asset prefix are available.",
        {
            "apk": str(apk_path),
            "apk_exists": apk_ok,
            "android_www_dir": str(android_www_dir),
            "android_www_dir_exists": android_ok,
            "asset_prefix": asset_prefix,
            "asset_prefix_valid": prefix_ok,
        },
    )


def _check_required_pages(
    android_files: dict[str, dict[str, Any]],
    apk_files: dict[str, dict[str, Any]],
) -> Result:
    missing_android_pages = [page for page in REQUIRED_PAGES if page not in android_files]
    missing_apk_pages = [page for page in REQUIRED_PAGES if page not in apk_files]
    changed_required_pages = [
        page
        for page in REQUIRED_PAGES
        if page in android_files and page in apk_files and android_files[page]["sha256"] != apk_files[page]["sha256"]
    ]
    ok = not missing_android_pages and not missing_apk_pages and not changed_required_pages
    return _result(
        "APK-WEBVIEW-REQUIRED-PAGES",
        ok,
        "Required L1 mobile pages are present and byte-identical inside the APK WebView assets.",
        {
            "required_pages": list(REQUIRED_PAGES),
            "missing_android_pages": missing_android_pages,
            "missing_apk_pages": missing_apk_pages,
            "changed_required_pages": changed_required_pages,
        },
    )


def _check_file_parity(
    android_files: dict[str, dict[str, Any]],
    apk_files: dict[str, dict[str, Any]],
) -> Result:
    android_names = set(android_files)
    apk_names = set(apk_files)
    missing_files = sorted(android_names - apk_names)
    extra_files = sorted(apk_names - android_names)
    changed_files = sorted(
        name
        for name in android_names & apk_names
        if android_files[name]["sha256"] != apk_files[name]["sha256"]
    )
    ok = not missing_files and not extra_files and not changed_files
    return _result(
        "APK-WEBVIEW-FILE-PARITY",
        ok,
        "Every Android WebView asset is present in the APK without stale extras or changed bytes.",
        {
            "missing_files": missing_files,
            "extra_files": extra_files,
            "changed_files": changed_files,
        },
    )


def verify_apk_webview_assets(apk: Path, android_www_dir: Path, asset_prefix: str = DEFAULT_ASSET_PREFIX) -> dict[str, Any]:
    apk = Path(apk)
    android_www_dir = Path(android_www_dir)
    android_files = _android_file_map(android_www_dir)
    apk_files = _apk_webview_file_map(apk, asset_prefix)
    results = [
        _check_inputs(apk, android_www_dir, asset_prefix),
        _check_required_pages(android_files, apk_files),
        _check_file_parity(android_files, apk_files),
    ]
    failed = [result for result in results if result.status == "FAIL"]
    return {
        "schema": SCHEMA,
        "target": {
            "apk": str(apk),
            "android_www_dir": str(android_www_dir),
            "asset_prefix": _normalized_prefix(asset_prefix),
            "required_pages": list(REQUIRED_PAGES),
        },
        "summary": {
            "overall": "FAIL" if failed else "PASS",
            "failed": len(failed),
            "total": len(results),
            "android_file_count": len(android_files),
            "apk_webview_file_count": len(apk_files),
        },
        "results": [result.__dict__ for result in results],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, default=DEFAULT_APK)
    parser.add_argument("--android-www-dir", type=Path, default=DEFAULT_ANDROID_WWW_DIR)
    parser.add_argument("--asset-prefix", default=DEFAULT_ASSET_PREFIX)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = verify_apk_webview_assets(args.apk, args.android_www_dir, args.asset_prefix)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (OSError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
