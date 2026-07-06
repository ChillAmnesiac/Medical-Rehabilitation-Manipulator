#!/usr/bin/env python3
"""Objective-level L1 audit for the rehab mobile app.

This script turns the combined release gate into a user-goal checklist:
login, home next step, phone/device binding, Ask Therapist safety, profile
quality, APK delivery, cloud model readiness, and browser QA evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qa_rehab_mobile_l1_release  # noqa: E402


BROWSER_EVIDENCE_FILES = {
    "home_first_screen": "l1-home-390.png",
    "ask_therapist_chat": "l1-ask-therapist-chat-390.png",
    "unsafe_agent_refusal": "l1-unsafe-agent-refusal-390.png",
    "device_binding_wizard": "l1-device-binding-wizard-390.png",
    "profile_phone_medical": "l1-profile-phone-medical-390.png",
}

EXPECTED_BROWSER_SCREENSHOT_DIMENSIONS = {"width": 390, "height": 844}
MIN_BROWSER_SCREENSHOT_BYTES = 1024
REQUIRED_BROWSER_METRICS_PAGES = ["ai-plan", "device", "home", "profile"]
DEFAULT_BROWSER_METRICS_JSON = Path(
    "docs/qa/rehab-mobile-20260706/browser-metrics-clean-candidate-live-strict-20260707.json"
)


@dataclass
class Requirement:
    requirement: str
    status: str
    summary: str
    evidence: dict[str, Any]


def _gate_status(payload: dict[str, Any], gate: str) -> str | None:
    sections = (payload.get("api") or {}, payload.get("frontend") or {})
    for section in sections:
        for result in section.get("results") or []:
            if isinstance(result, dict) and result.get("gate") == gate:
                status = result.get("status")
                return status if isinstance(status, str) else None
    return None


def _requirement(name: str, ok: bool, summary: str, evidence: dict[str, Any]) -> Requirement:
    return Requirement(name, "PASS" if ok else "FAIL", summary, evidence)


def _all_gates_pass(payload: dict[str, Any], gates: list[str]) -> bool:
    return all(_gate_status(payload, gate) == "PASS" for gate in gates)


def _jpeg_dimensions(data: bytes) -> dict[str, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    offset = 2
    sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset + 3 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            return None
        marker = data[offset]
        offset += 1
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[offset : offset + 2], "big")
        if segment_length < 2 or offset + segment_length > len(data):
            return None
        if marker in sof_markers:
            if segment_length < 7:
                return None
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            return {"width": width, "height": height}
        offset += segment_length
    return None


def _image_dimensions(path: Path) -> dict[str, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    header = data[:24]
    if len(header) < 24 or not header.startswith(b"\x89PNG\r\n\x1a\n") or header[12:16] != b"IHDR":
        return _jpeg_dimensions(data)
    return {"width": int.from_bytes(header[16:20], "big"), "height": int.from_bytes(header[20:24], "big")}


def browser_metrics_status(metrics_path: Path) -> tuple[bool, dict[str, Any]]:
    detail: dict[str, Any] = {"path": str(metrics_path)}
    if not metrics_path.exists():
        return False, {**detail, "status": "MISSING"}
    try:
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, {**detail, "status": "INVALID", "error": str(exc)}

    summary = payload.get("summary") if isinstance(payload, dict) else {}
    gate_status = None
    checked_pages: list[str] = []
    declared_missing_pages: list[str] = []
    if isinstance(payload, dict):
        for result in payload.get("results") or []:
            if isinstance(result, dict) and result.get("gate") == "L1-BROWSER-METRICS-001":
                raw_status = result.get("status")
                gate_status = raw_status if isinstance(raw_status, str) else None
                result_detail = result.get("detail")
                if isinstance(result_detail, dict):
                    raw_pages = result_detail.get("checked_pages")
                    if isinstance(raw_pages, list):
                        checked_pages = [str(page) for page in raw_pages]
                    raw_missing_pages = result_detail.get("missing_pages")
                    if isinstance(raw_missing_pages, list):
                        declared_missing_pages = [str(page) for page in raw_missing_pages]
                break

    status = gate_status or (summary.get("overall") if isinstance(summary, dict) else None) or "MISSING_GATE"
    normalized_checked_pages = {page.replace(".html", "").strip().lower() for page in checked_pages}
    missing_pages = [page for page in REQUIRED_BROWSER_METRICS_PAGES if page not in normalized_checked_pages]
    missing_pages = sorted(set(missing_pages + declared_missing_pages))
    ok = (
        status == "PASS"
        and isinstance(summary, dict)
        and summary.get("overall") == "PASS"
        and not missing_pages
    )
    return ok, {
        **detail,
        "status": status if not missing_pages else "FAIL",
        "summary": summary if isinstance(summary, dict) else {},
        "checked_pages": checked_pages,
        "required_pages": REQUIRED_BROWSER_METRICS_PAGES,
        "missing_pages": missing_pages,
    }


def browser_evidence_status(screenshot_dir: Path, browser_metrics_json: Path | None = None) -> tuple[bool, dict[str, Any]]:
    files = list(screenshot_dir.glob("*.png")) if screenshot_dir.exists() else []
    lower_files = {path.name.lower(): path for path in files}
    missing = []
    matched: dict[str, str] = {}
    invalid_dimensions: dict[str, dict[str, Any]] = {}
    invalid_files: dict[str, dict[str, Any]] = {}
    for key, expected_name in BROWSER_EVIDENCE_FILES.items():
        match_name = expected_name.lower() if expected_name.lower() in lower_files else None
        if match_name:
            matched[key] = match_name
            path = lower_files[match_name]
            size = path.stat().st_size if path.exists() else 0
            if size < MIN_BROWSER_SCREENSHOT_BYTES:
                invalid_files[key] = {
                    "file": match_name,
                    "actual_bytes": size,
                    "minimum_bytes": MIN_BROWSER_SCREENSHOT_BYTES,
                }
            dimensions = _image_dimensions(path)
            if dimensions != EXPECTED_BROWSER_SCREENSHOT_DIMENSIONS:
                invalid_dimensions[key] = {
                    "file": match_name,
                    "actual": dimensions,
                    "expected": EXPECTED_BROWSER_SCREENSHOT_DIMENSIONS,
                }
        else:
            missing.append(key)
    metrics_path = browser_metrics_json or DEFAULT_BROWSER_METRICS_JSON
    metrics_ok, metrics_detail = browser_metrics_status(metrics_path)
    return not missing and not invalid_dimensions and not invalid_files and metrics_ok, {
        "screenshot_dir": str(screenshot_dir),
        "matched": matched,
        "missing": missing,
        "invalid_dimensions": invalid_dimensions,
        "invalid_files": invalid_files,
        "expected_dimensions": EXPECTED_BROWSER_SCREENSHOT_DIMENSIONS,
        "minimum_screenshot_bytes": MIN_BROWSER_SCREENSHOT_BYTES,
        "browser_metrics": metrics_detail,
    }


def audit_objective(
    release_payload: dict[str, Any],
    screenshot_dir: Path,
    browser_metrics_json: Path | None = None,
) -> dict[str, Any]:
    browser_ok, browser_detail = browser_evidence_status(screenshot_dir, browser_metrics_json)
    summary = release_payload.get("summary") or {}
    requirements = [
        _requirement(
            "cloud_deployment",
            _all_gates_pass(release_payload, ["P0-CLOUD-001", "P1-DEPLOY-META-001"]),
            "Cloud API is healthy and exposes traceable deployment metadata.",
            {"required_gates": ["P0-CLOUD-001", "P1-DEPLOY-META-001"]},
        ),
        _requirement(
            "login",
            _gate_status(release_payload, "P0-AUTH-001") == "PASS",
            "Staging user can log in and receive a bearer token.",
            {"required_gates": ["P0-AUTH-001"]},
        ),
        _requirement(
            "home_next_step",
            _gate_status(release_payload, "L1-HOME-STATIC-001") == "PASS",
            "Home shows a clear next action and no normal-screen debug terms.",
            {"required_gates": ["L1-HOME-STATIC-001"]},
        ),
        _requirement(
            "phone_binding",
            _all_gates_pass(
                release_payload,
                ["P0-PHONE-001", "P0-PHONE-FLOW-001", "L1-PROFILE-STATIC-001", "L1-FRONTEND-INTEGRATION-001"],
            ),
            "Phone is bound in API and the profile UI exposes the phone verification path.",
            {
                "required_gates": [
                    "P0-PHONE-001",
                    "P0-PHONE-FLOW-001",
                    "L1-PROFILE-STATIC-001",
                    "L1-FRONTEND-INTEGRATION-001",
                ]
            },
        ),
        _requirement(
            "device_binding",
            _all_gates_pass(
                release_payload,
                ["P0-DEVICE-FLOW-001", "P0-DEVICE-CONFLICT-001", "L1-DEVICE-STATIC-001", "L1-FRONTEND-INTEGRATION-001"],
            ),
            "Device binding and already-bound conflict work in API and the device UI shows a patient wizard.",
            {
                "required_gates": [
                    "P0-DEVICE-FLOW-001",
                    "P0-DEVICE-CONFLICT-001",
                    "L1-DEVICE-STATIC-001",
                    "L1-FRONTEND-INTEGRATION-001",
                ]
            },
        ),
        _requirement(
            "ask_therapist_safety",
            _all_gates_pass(
                release_payload,
                ["P0-AGENT-001", "P0-AGENT-002", "L1-AGENT-STATIC-001", "L1-FRONTEND-INTEGRATION-001"],
            ),
            "Ask Therapist answers safe questions, refuses unsafe control, and is reachable in the UI.",
            {
                "required_gates": [
                    "P0-AGENT-001",
                    "P0-AGENT-002",
                    "L1-AGENT-STATIC-001",
                    "L1-FRONTEND-INTEGRATION-001",
                ]
            },
        ),
        _requirement(
            "agent_cloud_model",
            _all_gates_pass(release_payload, ["P1-AGENT-CONFIG-001", "P1-AGENT-MODEL-001"]),
            "Agent is backed by a configured cloud model, not only safe fallback rules.",
            {"required_gates": ["P1-AGENT-CONFIG-001", "P1-AGENT-MODEL-001"]},
        ),
        _requirement(
            "profile_no_fake_debug",
            _gate_status(release_payload, "L1-PROFILE-STATIC-001") == "PASS",
            "Profile does not show fake patient data or engineering debug fields.",
            {"required_gates": ["L1-PROFILE-STATIC-001"]},
        ),
        _requirement(
            "apk_delivery",
            _gate_status(release_payload, "P0-APK-001") == "PASS",
            "Installable APK is reachable and has a valid APK content type.",
            {"required_gates": ["P0-APK-001"]},
        ),
        _requirement(
            "browser_qa_evidence",
            browser_ok,
            "Browser QA screenshots cover home, Ask Therapist, unsafe refusal, device wizard, and profile.",
            browser_detail,
        ),
        _requirement(
            "combined_l1_release",
            summary.get("overall") == "PASS" and not summary.get("blocking_gates"),
            "Combined L1 release gate is green with no blockers.",
            {"release_summary": summary},
        ),
    ]
    failed = [item.requirement for item in requirements if item.status != "PASS"]
    return {
        "summary": {
            "overall": "PASS" if not failed else "FAIL",
            "failed": len(failed),
            "total": len(requirements),
            "blocking_requirements": failed,
        },
        "requirements": [item.__dict__ for item in requirements],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshots-dir", type=Path, default=Path("docs/qa/rehab-mobile-20260706/screenshots"))
    parser.add_argument("--browser-metrics-json", type=Path, default=DEFAULT_BROWSER_METRICS_JSON)
    parser.add_argument("--api-base", default=os.getenv("REHAB_QA_API_BASE", "http://106.55.62.122:8011"))
    parser.add_argument("--web-base", default=os.getenv("REHAB_QA_WEB_BASE", "http://106.55.62.122:3001/rehab-arm-mobile"))
    parser.add_argument("--web-origin", default=os.getenv("REHAB_QA_WEB_ORIGIN", "http://106.55.62.122:3001"))
    parser.add_argument(
        "--apk-url",
        default=os.getenv(
            "REHAB_QA_APK_URL",
            "http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk",
        ),
    )
    parser.add_argument("--email", default=os.getenv("REHAB_QA_EMAIL"))
    parser.add_argument("--password", default=os.getenv("REHAB_QA_PASSWORD"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    release_args = qa_rehab_mobile_l1_release.parse_args(
        [
            "--api-base",
            args.api_base,
            "--web-base",
            args.web_base,
            "--web-origin",
            args.web_origin,
            "--apk-url",
            args.apk_url,
            "--timeout",
            str(args.timeout),
        ]
        + (["--email", args.email] if args.email else [])
        + (["--password", args.password] if args.password else [])
    )
    _, release_payload = qa_rehab_mobile_l1_release.run(release_args)
    payload = audit_objective(release_payload, args.screenshots_dir, args.browser_metrics_json)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
