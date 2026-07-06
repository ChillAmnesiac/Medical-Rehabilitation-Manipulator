import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("qa_rehab_mobile_l1_objective_audit.py")


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
        (tmp_path / name).write_bytes(b"png")

    payload = module.audit_objective(_release_payload(), tmp_path)

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


def test_browser_evidence_does_not_count_agent_page_as_device_wizard(tmp_path):
    module = _load_module()
    (tmp_path / "device-binding-agent-390.png").write_bytes(b"png")

    ok, detail = module.browser_evidence_status(tmp_path)

    assert not ok
    assert "device_binding_wizard" in detail["missing"]
