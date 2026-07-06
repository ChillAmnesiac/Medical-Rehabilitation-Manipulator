#!/usr/bin/env python3
"""Verify a prepared rehab mobile frontend release before cloud deployment."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA = "rehab-mobile-frontend-release/v1"
REQUIRED_PAGES = ("home.html", "profile.html", "device.html", "ai-plan.html")
REQUIRED_BROWSER_SCREENSHOTS = (
    "l1-home-390.png",
    "l1-ask-therapist-chat-390.png",
    "l1-unsafe-agent-refusal-390.png",
    "l1-device-binding-wizard-390.png",
    "l1-profile-phone-medical-390.png",
)
REQUIRED_BROWSER_METRICS_REPORT = "browser-metrics-l1-390x844.json"
REQUIRED_BROWSER_METRICS_GATE_OUTPUT = "browser-metrics-gate.json"
REQUIRED_BROWSER_METRICS_PAGES = ["ai-plan", "device", "home", "profile"]


@dataclass
class Result:
    gate: str
    level: str
    status: str
    summary: str
    detail: Any = None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_manifest_path(manifest_path: Path, raw_path: Any) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return manifest_path.parent / path


def _result(gate: str, ok: bool, summary: str, detail: Any = None) -> Result:
    return Result(
        gate=gate,
        level="L1",
        status="PASS" if ok else "FAIL",
        summary=summary,
        detail=detail,
    )


def _check_schema(manifest: dict[str, Any]) -> Result:
    schema = manifest.get("schema")
    ok = schema == SCHEMA
    return _result(
        "FRONTEND-RELEASE-SCHEMA",
        ok,
        "Release manifest uses the expected rehab mobile frontend schema.",
        {"expected_schema": SCHEMA, "actual_schema": schema},
    )


def _check_zip_integrity(manifest_path: Path, manifest: dict[str, Any]) -> Result:
    artifact = manifest.get("artifact") if isinstance(manifest.get("artifact"), dict) else {}
    zip_path = _resolve_manifest_path(manifest_path, artifact.get("zip_path"))
    expected_sha = artifact.get("zip_sha256")
    detail: dict[str, Any] = {
        "zip_path": str(zip_path) if zip_path else None,
        "expected_sha256": expected_sha,
    }
    ok = False
    if zip_path and zip_path.is_file() and isinstance(expected_sha, str) and len(expected_sha) == 64:
        actual_sha = _sha256(zip_path)
        detail["actual_sha256"] = actual_sha
        detail["bytes"] = zip_path.stat().st_size
        ok = actual_sha == expected_sha and zip_path.stat().st_size > 0
    else:
        detail["reason"] = "zip_missing_or_manifest_hash_invalid"
    return _result(
        "FRONTEND-RELEASE-ZIP-INTEGRITY",
        ok,
        "Release zip exists and matches the manifest sha256.",
        detail,
    )


def _check_preflight(manifest_path: Path, manifest: dict[str, Any]) -> Result:
    manifest_summary = manifest.get("frontend_l1_preflight")
    if not isinstance(manifest_summary, dict):
        return _result(
            "FRONTEND-RELEASE-PREFLIGHT",
            False,
            "Local frontend L1 preflight passed before packaging.",
            {"reason": "frontend_l1_preflight_missing"},
        )

    report_path = _resolve_manifest_path(manifest_path, manifest_summary.get("report_path"))
    detail: dict[str, Any] = {
        "manifest_summary": manifest_summary,
        "report_path": str(report_path) if report_path else None,
    }
    report_summary: dict[str, Any] | None = None
    if report_path and report_path.is_file():
        report = _load_json(report_path)
        raw_report_summary = report.get("summary")
        if isinstance(raw_report_summary, dict):
            report_summary = raw_report_summary
            detail["report_summary"] = report_summary
    else:
        detail["reason"] = "preflight_report_missing"

    ok = (
        manifest_summary.get("overall") == "PASS"
        and manifest_summary.get("failed") == 0
        and report_summary is not None
        and report_summary.get("overall") == "PASS"
        and report_summary.get("failed") == 0
    )
    return _result(
        "FRONTEND-RELEASE-PREFLIGHT",
        ok,
        "Local frontend L1 preflight passed before packaging.",
        detail,
    )


def _check_pages(manifest: dict[str, Any]) -> Result:
    source = manifest.get("source") if isinstance(manifest.get("source"), dict) else {}
    required_pages = source.get("required_pages") if isinstance(source.get("required_pages"), list) else []
    missing_pages = source.get("missing_required_pages") if isinstance(source.get("missing_required_pages"), list) else []
    artifacts = source.get("required_page_artifacts")
    artifacts = artifacts if isinstance(artifacts, dict) else {}
    missing_artifacts = []
    invalid_artifacts = []
    for page in REQUIRED_PAGES:
        artifact = artifacts.get(page)
        if not isinstance(artifact, dict):
            missing_artifacts.append(page)
            continue
        sha = artifact.get("sha256")
        size = artifact.get("bytes")
        if not isinstance(sha, str) or len(sha) != 64 or not isinstance(size, int) or size <= 0:
            invalid_artifacts.append(page)

    ok = (
        set(required_pages) == set(REQUIRED_PAGES)
        and source.get("required_pages_present") is True
        and missing_pages == []
        and not missing_artifacts
        and not invalid_artifacts
    )
    return _result(
        "FRONTEND-RELEASE-PAGES",
        ok,
        "Release manifest accounts for every required mobile page artifact.",
        {
            "required_pages": required_pages,
            "expected_pages": list(REQUIRED_PAGES),
            "missing_required_pages": missing_pages,
            "missing_artifacts": missing_artifacts,
            "invalid_artifacts": invalid_artifacts,
        },
    )


def _check_deployment(manifest: dict[str, Any]) -> Result:
    deploy = manifest.get("deploy") if isinstance(manifest.get("deploy"), dict) else {}
    verification = manifest.get("verification") if isinstance(manifest.get("verification"), dict) else {}
    commands = deploy.get("commands") if isinstance(deploy.get("commands"), list) else []
    verification_commands = verification.get("powershell") if isinstance(verification.get("powershell"), list) else []
    joined_commands = "\n".join(str(command) for command in commands)
    joined_verification = "\n".join(str(command) for command in verification_commands)
    remote_web_root = deploy.get("remote_web_root")
    executor_command = deploy.get("executor_command")
    ok = (
        deploy.get("mode") == "manual_review_then_ssh"
        and isinstance(remote_web_root, str)
        and remote_web_root.endswith("/rehab-arm-mobile")
        and isinstance(executor_command, str)
        and "deploy_rehab_mobile_frontend_release.py --manifest" in executor_command
        and "scp " in joined_commands
        and "ssh " in joined_commands
        and "qa_rehab_mobile_l1_frontend.py" in joined_verification
        and "verify_rehab_mobile_webview_mirror.py" in joined_verification
        and "webview-mirror-verification.json" in joined_verification
        and "qa_rehab_mobile_l1_release.py" in joined_verification
        and "qa_rehab_mobile_l1_objective_audit.py" in joined_verification
        and "curl.exe -I -sS" in joined_verification
    )
    return _result(
        "FRONTEND-RELEASE-DEPLOYMENT",
        ok,
        "Release manifest includes cloud deploy and post-deploy verification commands.",
        {
            "mode": deploy.get("mode"),
            "remote_web_root": remote_web_root,
            "executor_command": executor_command,
            "command_count": len(commands),
            "verification_command_count": len(verification_commands),
        },
    )


def _check_browser_evidence(manifest: dict[str, Any]) -> Result:
    verification = manifest.get("verification") if isinstance(manifest.get("verification"), dict) else {}
    screenshots = verification.get("required_browser_screenshots")
    screenshots = screenshots if isinstance(screenshots, list) else []
    expected = set(REQUIRED_BROWSER_SCREENSHOTS)
    actual = set(str(name) for name in screenshots)
    ok = actual == expected
    return _result(
        "FRONTEND-RELEASE-BROWSER-EVIDENCE",
        ok,
        "Release manifest preserves the exact final browser QA screenshot requirements.",
        {
            "expected": list(REQUIRED_BROWSER_SCREENSHOTS),
            "actual": screenshots,
            "missing": sorted(expected - actual),
            "unexpected": sorted(actual - expected),
        },
    )


def _check_browser_metrics(manifest_path: Path, manifest: dict[str, Any]) -> Result:
    verification = manifest.get("verification") if isinstance(manifest.get("verification"), dict) else {}
    commands = verification.get("powershell") if isinstance(verification.get("powershell"), list) else []
    joined_commands = "\n".join(str(command) for command in commands)
    report = verification.get("required_browser_metrics_report")
    output = verification.get("browser_metrics_gate_output")
    output_path = _resolve_manifest_path(manifest_path, output)
    detail: dict[str, Any] = {
        "required_report": REQUIRED_BROWSER_METRICS_REPORT,
        "actual_report": report,
        "required_output": REQUIRED_BROWSER_METRICS_GATE_OUTPUT,
        "actual_output": output,
        "output_path": str(output_path) if output_path else None,
        "has_command": "qa_rehab_mobile_browser_metrics.py" in joined_commands,
    }
    gate_summary: dict[str, Any] | None = None
    gate_status = None
    checked_pages: list[str] = []
    declared_missing_pages: list[str] = []
    if output_path and output_path.is_file():
        gate_payload = _load_json(output_path)
        raw_summary = gate_payload.get("summary")
        if isinstance(raw_summary, dict):
            gate_summary = raw_summary
            detail["gate_summary"] = gate_summary
        for result in gate_payload.get("results") or []:
            if isinstance(result, dict) and result.get("gate") == "L1-BROWSER-METRICS-001":
                raw_status = result.get("status")
                gate_status = raw_status if isinstance(raw_status, str) else None
                detail["gate_status"] = gate_status
                result_detail = result.get("detail")
                if isinstance(result_detail, dict):
                    raw_checked_pages = result_detail.get("checked_pages")
                    if isinstance(raw_checked_pages, list):
                        checked_pages = [str(page) for page in raw_checked_pages]
                    raw_missing_pages = result_detail.get("missing_pages")
                    if isinstance(raw_missing_pages, list):
                        declared_missing_pages = [str(page) for page in raw_missing_pages]
                break
    else:
        detail["reason"] = "browser_metrics_gate_output_missing"

    normalized_checked_pages = {page.replace(".html", "").strip().lower() for page in checked_pages}
    missing_pages = [page for page in REQUIRED_BROWSER_METRICS_PAGES if page not in normalized_checked_pages]
    missing_pages = sorted(set(missing_pages + declared_missing_pages))
    detail["required_pages"] = REQUIRED_BROWSER_METRICS_PAGES
    detail["checked_pages"] = checked_pages
    detail["missing_pages"] = missing_pages

    ok = (
        report == REQUIRED_BROWSER_METRICS_REPORT
        and output == REQUIRED_BROWSER_METRICS_GATE_OUTPUT
        and "qa_rehab_mobile_browser_metrics.py" in joined_commands
        and f"--input artifacts/rehab-mobile-frontend-release/{REQUIRED_BROWSER_METRICS_REPORT}" in joined_commands
        and f"--output artifacts/rehab-mobile-frontend-release/{REQUIRED_BROWSER_METRICS_GATE_OUTPUT}" in joined_commands
        and gate_summary is not None
        and gate_summary.get("overall") == "PASS"
        and gate_summary.get("failed") == 0
        and gate_status == "PASS"
        and not missing_pages
    )
    return _result(
        "FRONTEND-RELEASE-BROWSER-METRICS",
        ok,
        "Release manifest requires a passing rendered browser metrics gate before L1 acceptance.",
        detail,
    )


def verify_release_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest_path = Path(manifest_path)
    manifest = _load_json(manifest_path)
    results = [
        _check_schema(manifest),
        _check_zip_integrity(manifest_path, manifest),
        _check_preflight(manifest_path, manifest),
        _check_pages(manifest),
        _check_deployment(manifest),
        _check_browser_evidence(manifest),
        _check_browser_metrics(manifest_path, manifest),
    ]
    failed = [result for result in results if result.status == "FAIL"]
    return {
        "summary": {
            "overall": "FAIL" if failed else "PASS",
            "failed": len(failed),
            "total": len(results),
            "manifest_path": str(manifest_path),
        },
        "results": [result.__dict__ for result in results],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("artifacts/rehab-mobile-frontend-release/rehab-mobile-frontend-release-manifest.json"),
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = verify_release_manifest(args.manifest)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
