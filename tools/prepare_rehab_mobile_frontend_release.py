#!/usr/bin/env python3
"""Prepare a deployable frontend bundle after Stitch updates rehab mobile assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qa_rehab_mobile_l1_frontend  # noqa: E402


DEFAULT_SOURCE_DIR = Path("apps/web/public/rehab-arm-mobile")
DEFAULT_OUTPUT_DIR = Path("artifacts/rehab-mobile-frontend-release")
DEFAULT_API_BASE = "http://106.55.62.122:8011"
DEFAULT_WEB_BASE = "http://106.55.62.122:3001/rehab-arm-mobile"
DEFAULT_APK_URL = "http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk"
DEFAULT_REMOTE_WEB_ROOT = "/home/ubuntu/apps/ai-collab/apps/web/public/rehab-arm-mobile"
REQUIRED_PAGES = ("home.html", "profile.html", "device.html", "ai-plan.html")
FINAL_BROWSER_SCREENSHOTS = (
    "l1-home-390.png",
    "l1-ask-therapist-chat-390.png",
    "l1-unsafe-agent-refusal-390.png",
    "l1-device-binding-wizard-390.png",
    "l1-profile-phone-medical-390.png",
)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_files(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.rglob("*") if path.is_file())


def _validate_source(source_dir: Path) -> list[str]:
    if not source_dir.exists() or not source_dir.is_dir():
        raise ValueError(f"frontend source dir does not exist: {source_dir}")
    missing = [page for page in REQUIRED_PAGES if not (source_dir / page).is_file()]
    if missing:
        raise ValueError("missing required frontend pages: " + ", ".join(missing))
    return missing


def _write_zip(source_dir: Path, zip_path: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, path.relative_to(source_dir).as_posix())


def _deploy_commands(zip_path: Path, remote_web_root: str) -> list[str]:
    remote_parent = str(Path(remote_web_root).parent).replace("\\", "/")
    remote_name = Path(remote_web_root).name
    remote_zip = f"/tmp/{zip_path.name}"
    local_zip = zip_path.as_posix()
    return [
        f'scp "{local_zip}" ubuntu@106.55.62.122:{remote_zip}',
        (
            'ssh ubuntu@106.55.62.122 "set -e; '
            f'cd {remote_parent}; '
            f'test -d {remote_name}; '
            f'cp -a {remote_name} {remote_name}.backup-$(date -u +%Y%m%dT%H%M%SZ); '
            f'rm -rf {remote_name}/*; '
            f'unzip -o {remote_zip} -d {remote_name}"'
        ),
    ]


def _verification_commands(api_base: str, web_base: str, apk_url: str) -> list[str]:
    return [
        "$env:REHAB_QA_EMAIL='3245056131@qq.com'",
        "$env:REHAB_QA_PASSWORD='1234'",
        f"$env:REHAB_QA_API_BASE='{api_base}'",
        f"$env:REHAB_QA_WEB_BASE='{web_base}'",
        f"$env:REHAB_QA_APK_URL='{apk_url}'",
        ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe tools\\qa_rehab_mobile_l1_frontend.py --source-dir apps/web/public/rehab-arm-mobile",
        ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe tools\\qa_rehab_mobile_l1_release.py",
        ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe tools\\qa_rehab_mobile_l1_objective_audit.py",
        f"curl.exe -I -sS {apk_url}",
    ]


def run_frontend_l1_preflight(source_dir: Path, report_path: Path, timeout: int = 20) -> dict[str, Any]:
    args = qa_rehab_mobile_l1_frontend.parse_args(
        ["--source-dir", str(source_dir), "--timeout", str(timeout)]
    )
    _, payload = qa_rehab_mobile_l1_frontend.run(args)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = dict(payload.get("summary") or {})
    summary["report_path"] = str(report_path)
    return summary


def build_release_bundle(
    *,
    source_dir: Path,
    output_dir: Path,
    generated_at: str | None = None,
    api_base: str = DEFAULT_API_BASE,
    web_base: str = DEFAULT_WEB_BASE,
    apk_url: str = DEFAULT_APK_URL,
    remote_web_root: str = DEFAULT_REMOTE_WEB_ROOT,
) -> dict[str, Any]:
    generated_at = generated_at or _utc_now()
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    _validate_source(source_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    preflight_report_path = output_dir / "frontend-l1-preflight.json"
    preflight_summary = run_frontend_l1_preflight(source_dir, preflight_report_path)
    if preflight_summary.get("overall") != "PASS":
        failed = preflight_summary.get("failed")
        raise ValueError(f"frontend L1 local preflight failed: {failed} failing gates")

    zip_path = output_dir / "rehab-mobile-frontend-release.zip"
    manifest_path = output_dir / "rehab-mobile-frontend-release-manifest.json"
    files = _source_files(source_dir)
    _write_zip(source_dir, zip_path, files)

    required_pages = {
        page: {
            "bytes": (source_dir / page).stat().st_size,
            "sha256": _sha256(source_dir / page),
        }
        for page in REQUIRED_PAGES
    }
    manifest: dict[str, Any] = {
        "schema": "rehab-mobile-frontend-release/v1",
        "generated_at": generated_at,
        "source": {
            "path": str(source_dir),
            "required_pages": list(REQUIRED_PAGES),
            "required_pages_present": True,
            "missing_required_pages": [],
            "required_page_artifacts": required_pages,
        },
        "frontend_l1_preflight": preflight_summary,
        "artifact": {
            "zip_path": str(zip_path),
            "zip_sha256": _sha256(zip_path),
            "manifest_path": str(manifest_path),
            "file_count": len(files),
            "total_source_bytes": sum(path.stat().st_size for path in files),
        },
        "deploy": {
            "mode": "manual_review_then_ssh",
            "remote_web_root": remote_web_root,
            "commands": _deploy_commands(zip_path, remote_web_root),
        },
        "verification": {
            "powershell": _verification_commands(api_base, web_base, apk_url),
            "required_browser_screenshots": list(FINAL_BROWSER_SCREENSHOTS),
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--generated-at")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--web-base", default=DEFAULT_WEB_BASE)
    parser.add_argument("--apk-url", default=DEFAULT_APK_URL)
    parser.add_argument("--remote-web-root", default=DEFAULT_REMOTE_WEB_ROOT)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    manifest = build_release_bundle(
        source_dir=args.source_dir,
        output_dir=args.output_dir,
        generated_at=args.generated_at,
        api_base=args.api_base,
        web_base=args.web_base,
        apk_url=args.apk_url,
        remote_web_root=args.remote_web_root,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
