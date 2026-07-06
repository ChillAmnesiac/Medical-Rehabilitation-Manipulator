import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("qa_rehab_mobile_l1_objective_audit.py")


def _write_png_header(path, width, height):
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + (13).to_bytes(4, "big")
        + b"IHDR"
        + width.to_bytes(4, "big")
        + height.to_bytes(4, "big")
        + b"\x08\x02\x00\x00\x00"
        + b"\x00\x00\x00\x00"
    )


def _write_png_screenshot(path, width=390, height=844):
    _write_png_header(path, width, height)
    with path.open("ab") as handle:
        handle.write(b"\x00" * 4096)


def _write_jpeg_header(path, width, height):
    path.write_bytes(
        b"\xff\xd8"
        + b"\xff\xe0"
        + (16).to_bytes(2, "big")
        + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + b"\xff\xc0"
        + (17).to_bytes(2, "big")
        + b"\x08"
        + height.to_bytes(2, "big")
        + width.to_bytes(2, "big")
        + b"\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00"
    )


def _write_jpeg_screenshot(path, width=390, height=844):
    _write_jpeg_header(path, width, height)
    with path.open("ab") as handle:
        handle.write(b"\x00" * 4096)


def _write_browser_metrics_gate(path, status="PASS", checked_pages=None):
    pages = checked_pages or ["home", "profile", "device", "ai-plan"]
    path.write_text(
        json.dumps(
            {
                "summary": {"overall": status, "failed": 0 if status == "PASS" else 1, "total": 1},
                "results": [
                    {
                        "gate": "L1-BROWSER-METRICS-001",
                        "status": status,
                        "detail": {"checked_pages": pages, "missing_pages": []},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _load_module():
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_l1_objective_audit", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _release_payload(*, overall="PASS", frontend="PASS", blockers=None):
    blockers = blockers or []
    return {
        "summary": {
            "overall": overall,
            "api_overall": "PASS",
            "api_p0_failed": 0,
            "frontend_overall": frontend,
            "frontend_failed": 0 if frontend == "PASS" else 5,
            "apk_webview_assets_overall": "PASS",
            "apk_webview_assets_failed": 0,
            "blocking_gates": blockers,
        },
        "api": {
            "results": [
                {"gate": "P0-CLOUD-001", "status": "PASS"},
                {"gate": "P1-DEPLOY-META-001", "status": "PASS"},
                {"gate": "P0-AUTH-001", "status": "PASS"},
                {"gate": "P0-PATIENT-VIEW-001", "status": "PASS"},
                {"gate": "P0-PHONE-001", "status": "PASS"},
                {"gate": "P0-PHONE-FLOW-001", "status": "PASS"},
                {"gate": "P0-DEVICE-FLOW-001", "status": "PASS"},
                {"gate": "P0-DEVICE-CONFLICT-001", "status": "PASS"},
                {"gate": "P0-AGENT-001", "status": "PASS"},
                {"gate": "P0-AGENT-002", "status": "PASS"},
                {"gate": "P1-AGENT-CONFIG-001", "status": "PASS"},
                {"gate": "P1-AGENT-MODEL-001", "status": "PASS"},
                {"gate": "P0-APK-001", "status": "PASS"},
            ]
        },
        "frontend": {
            "results": [
                {"gate": "L1-HOME-STATIC-001", "status": frontend},
                {"gate": "L1-PROFILE-STATIC-001", "status": frontend},
                {"gate": "L1-DEVICE-STATIC-001", "status": frontend},
                {"gate": "L1-AGENT-STATIC-001", "status": frontend},
                {"gate": "L1-FRONTEND-INTEGRATION-001", "status": frontend},
            ]
        },
        "apk_webview_assets": {
            "summary": {"overall": "PASS", "failed": 0, "total": 3},
            "results": [
                {"gate": "APK-WEBVIEW-INPUTS", "status": "PASS"},
                {"gate": "APK-WEBVIEW-REQUIRED-PAGES", "status": "PASS"},
                {"gate": "APK-WEBVIEW-FILE-PARITY", "status": "PASS"},
            ],
        },
    }


def test_objective_audit_passes_when_release_and_browser_evidence_are_ready(tmp_path):
    module = _load_module()
    for name in (
        "l1-home-390.png",
        "l1-ask-therapist-chat-390.png",
        "l1-unsafe-agent-refusal-390.png",
        "l1-device-binding-wizard-390.png",
        "l1-profile-phone-medical-390.png",
    ):
        _write_png_screenshot(tmp_path / name, 390, 844)
    metrics_path = tmp_path / "browser-metrics-gate.json"
    _write_browser_metrics_gate(metrics_path, "PASS")

    payload = module.audit_objective(_release_payload(), tmp_path, metrics_path)

    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["failed"] == 0
    assert payload["summary"]["blocking_requirements"] == []


def test_objective_audit_fails_on_frontend_model_and_missing_browser_evidence(tmp_path):
    module = _load_module()
    release = _release_payload(
        overall="FAIL",
        frontend="FAIL",
        blockers=["frontend_l1_gate", "agent_cloud_model"],
    )
    for result in release["api"]["results"]:
        if result["gate"] in {"P1-AGENT-CONFIG-001", "P1-AGENT-MODEL-001"}:
            result["status"] = "WARN"

    payload = module.audit_objective(release, tmp_path)

    assert payload["summary"]["overall"] == "FAIL"
    blockers = payload["summary"]["blocking_requirements"]
    assert "home_next_step" in blockers
    assert "ask_therapist_safety" in blockers
    assert "agent_cloud_model" in blockers
    assert "browser_qa_evidence" in blockers


def test_objective_audit_requires_browser_metrics_gate_evidence(tmp_path):
    module = _load_module()
    for name in (
        "l1-home-390.png",
        "l1-ask-therapist-chat-390.png",
        "l1-unsafe-agent-refusal-390.png",
        "l1-device-binding-wizard-390.png",
        "l1-profile-phone-medical-390.png",
    ):
        _write_png_screenshot(tmp_path / name, 390, 844)

    payload = module.audit_objective(_release_payload(), tmp_path, tmp_path / "missing-browser-metrics.json")

    assert payload["summary"]["overall"] == "FAIL"
    assert "browser_qa_evidence" in payload["summary"]["blocking_requirements"]
    browser_evidence = next(
        item["evidence"] for item in payload["requirements"] if item["requirement"] == "browser_qa_evidence"
    )
    assert browser_evidence["browser_metrics"]["status"] == "MISSING"


def test_objective_audit_fails_when_browser_metrics_gate_fails(tmp_path):
    module = _load_module()
    for name in (
        "l1-home-390.png",
        "l1-ask-therapist-chat-390.png",
        "l1-unsafe-agent-refusal-390.png",
        "l1-device-binding-wizard-390.png",
        "l1-profile-phone-medical-390.png",
    ):
        _write_png_screenshot(tmp_path / name, 390, 844)
    metrics_path = tmp_path / "browser-metrics-gate.json"
    _write_browser_metrics_gate(metrics_path, "FAIL")

    payload = module.audit_objective(_release_payload(), tmp_path, metrics_path)

    assert payload["summary"]["overall"] == "FAIL"
    browser_evidence = next(
        item["evidence"] for item in payload["requirements"] if item["requirement"] == "browser_qa_evidence"
    )
    assert browser_evidence["browser_metrics"]["status"] == "FAIL"


def test_objective_audit_fails_when_browser_metrics_pass_but_pages_are_missing(tmp_path):
    module = _load_module()
    for name in (
        "l1-home-390.png",
        "l1-ask-therapist-chat-390.png",
        "l1-unsafe-agent-refusal-390.png",
        "l1-device-binding-wizard-390.png",
        "l1-profile-phone-medical-390.png",
    ):
        _write_png_screenshot(tmp_path / name, 390, 844)
    metrics_path = tmp_path / "browser-metrics-gate.json"
    _write_browser_metrics_gate(metrics_path, "PASS", checked_pages=["home"])

    payload = module.audit_objective(_release_payload(), tmp_path, metrics_path)

    assert payload["summary"]["overall"] == "FAIL"
    browser_evidence = next(
        item["evidence"] for item in payload["requirements"] if item["requirement"] == "browser_qa_evidence"
    )
    assert browser_evidence["browser_metrics"]["status"] == "FAIL"
    assert browser_evidence["browser_metrics"]["missing_pages"] == ["ai-plan", "device", "profile"]


def test_objective_audit_requires_apk_webview_asset_parity(tmp_path):
    module = _load_module()
    release = _release_payload(overall="FAIL", blockers=["apk_webview_assets"])
    release["summary"]["apk_webview_assets_overall"] = "FAIL"
    release["summary"]["apk_webview_assets_failed"] = 3
    release["apk_webview_assets"]["summary"] = {"overall": "FAIL", "failed": 3, "total": 3}
    for result in release["apk_webview_assets"]["results"]:
        result["status"] = "FAIL"
    for name in (
        "l1-home-390.png",
        "l1-ask-therapist-chat-390.png",
        "l1-unsafe-agent-refusal-390.png",
        "l1-device-binding-wizard-390.png",
        "l1-profile-phone-medical-390.png",
    ):
        _write_png_screenshot(tmp_path / name, 390, 844)
    metrics_path = tmp_path / "browser-metrics-gate.json"
    _write_browser_metrics_gate(metrics_path, "PASS")

    payload = module.audit_objective(release, tmp_path, metrics_path)

    assert payload["summary"]["overall"] == "FAIL"
    assert "apk_webview_assets" in payload["summary"]["blocking_requirements"]
    requirement = next(
        item for item in payload["requirements"] if item["requirement"] == "apk_webview_assets"
    )
    assert requirement["evidence"]["required_gates"] == [
        "APK-WEBVIEW-INPUTS",
        "APK-WEBVIEW-REQUIRED-PAGES",
        "APK-WEBVIEW-FILE-PARITY",
    ]


def test_browser_evidence_does_not_count_agent_page_as_device_wizard(tmp_path):
    module = _load_module()
    (tmp_path / "device-binding-agent-390.png").write_bytes(b"png")

    ok, detail = module.browser_evidence_status(tmp_path)

    assert not ok
    assert "device_binding_wizard" in detail["missing"]


def test_browser_evidence_does_not_count_current_failure_screenshots_as_l1_evidence(tmp_path):
    module = _load_module()
    for name in (
        "current-fail-home-390x844.png",
        "current-fail-profile-phone-390x844.png",
        "current-fail-device-wizard-390x844.png",
        "current-fail-ask-therapist-chat-390x844.png",
        "current-fail-unsafe-refusal-390x844.png",
    ):
        _write_png_header(tmp_path / name, 390, 844)

    ok, detail = module.browser_evidence_status(tmp_path)

    assert not ok
    assert sorted(detail["missing"]) == [
        "ask_therapist_chat",
        "device_binding_wizard",
        "home_first_screen",
        "profile_phone_medical",
        "unsafe_agent_refusal",
    ]


def test_browser_evidence_requires_mobile_viewport_png_dimensions(tmp_path):
    module = _load_module()
    for name in (
        "l1-home-390.png",
        "l1-ask-therapist-chat-390.png",
        "l1-unsafe-agent-refusal-390.png",
        "l1-device-binding-wizard-390.png",
        "l1-profile-phone-medical-390.png",
    ):
        _write_png_screenshot(tmp_path / name, 430, 932)

    ok, detail = module.browser_evidence_status(tmp_path)

    assert not ok
    assert detail["missing"] == []
    assert sorted(detail["invalid_dimensions"]) == [
        "ask_therapist_chat",
        "device_binding_wizard",
        "home_first_screen",
        "profile_phone_medical",
        "unsafe_agent_refusal",
    ]
    assert detail["expected_dimensions"] == {"width": 390, "height": 844}


def test_browser_evidence_rejects_header_only_placeholder_screenshots(tmp_path):
    module = _load_module()
    for name in (
        "l1-home-390.png",
        "l1-ask-therapist-chat-390.png",
        "l1-unsafe-agent-refusal-390.png",
        "l1-device-binding-wizard-390.png",
        "l1-profile-phone-medical-390.png",
    ):
        _write_png_header(tmp_path / name, 390, 844)
    metrics_path = tmp_path / "browser-metrics-gate.json"
    _write_browser_metrics_gate(metrics_path, "PASS")

    ok, detail = module.browser_evidence_status(tmp_path, metrics_path)

    assert not ok
    assert sorted(detail["invalid_files"]) == [
        "ask_therapist_chat",
        "device_binding_wizard",
        "home_first_screen",
        "profile_phone_medical",
        "unsafe_agent_refusal",
    ]
    assert detail["minimum_screenshot_bytes"] == 1024


def test_browser_evidence_accepts_browser_jpeg_screenshots_with_png_extension(tmp_path):
    module = _load_module()
    for name in (
        "l1-home-390.png",
        "l1-ask-therapist-chat-390.png",
        "l1-unsafe-agent-refusal-390.png",
        "l1-device-binding-wizard-390.png",
        "l1-profile-phone-medical-390.png",
    ):
        _write_jpeg_screenshot(tmp_path / name, 390, 844)
    metrics_path = tmp_path / "browser-metrics-gate.json"
    _write_browser_metrics_gate(metrics_path, "PASS")

    ok, detail = module.browser_evidence_status(tmp_path, metrics_path)

    assert ok
    assert detail["missing"] == []
    assert detail["invalid_dimensions"] == {}
