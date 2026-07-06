import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("export_rehab_mobile_stitch_repair_packet.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("export_rehab_mobile_stitch_repair_packet", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _release_payload():
    return {
        "summary": {
            "overall": "FAIL",
            "api_overall": "PASS",
            "frontend_overall": "FAIL",
            "blocking_gates": ["frontend_l1_gate", "agent_cloud_model"],
        },
        "frontend": {
            "results": [
                {
                    "gate": "L1-HOME-STATIC-001",
                    "status": "FAIL",
                    "summary": "Home still exposes technical terms.",
                    "detail": {
                        "url": "http://example.test/home.html",
                        "missing_terms": ["问康复师"],
                        "forbidden_hits": ["M33", "RoboRehab Controller"],
                        "text_prefix": "RoboRehab Controller M33 ACTIVE",
                    },
                },
                {
                    "gate": "L1-FRONTEND-INTEGRATION-001",
                    "status": "FAIL",
                    "summary": "Frontend source is missing API wiring.",
                    "detail": {
                        "missing_requirements": [
                            "patient_view_home",
                            "phone_verification_start",
                            "agent_messages",
                        ],
                        "checked_pages": ["home.html", "profile.html", "ai-plan.html"],
                    },
                },
            ]
        },
        "api": {
            "results": [
                {
                    "gate": "P1-AGENT-MODEL-001",
                    "status": "WARN",
                    "summary": "Agent is using safe fallback rules.",
                    "detail": {"mode": "fallback_rule_based", "reason": "external_model_not_configured"},
                }
            ]
        },
    }


def _objective_payload():
    return {
        "summary": {
            "overall": "FAIL",
            "blocking_requirements": [
                "home_next_step",
                "phone_binding",
                "ask_therapist_safety",
                "agent_cloud_model",
                "browser_qa_evidence",
                "combined_l1_release",
            ],
        },
        "requirements": [
            {
                "requirement": "home_next_step",
                "status": "FAIL",
                "summary": "Home shows a clear next action and no normal-screen debug terms.",
                "evidence": {"required_gates": ["L1-HOME-STATIC-001"]},
            },
            {
                "requirement": "agent_cloud_model",
                "status": "FAIL",
                "summary": "Agent is backed by a configured cloud model.",
                "evidence": {"required_gates": ["P1-AGENT-MODEL-001"]},
            },
            {
                "requirement": "browser_qa_evidence",
                "status": "FAIL",
                "summary": "Browser QA screenshots are incomplete.",
                "evidence": {
                    "matched": {"home_first_screen": "device-binding-home-390.png"},
                    "missing": ["ask_therapist_chat", "unsafe_agent_refusal"],
                    "invalid_dimensions": {
                        "home_first_screen": {
                            "file": "device-binding-home-390.png",
                            "actual": {"width": 375, "height": 812},
                            "expected": {"width": 390, "height": 844},
                        }
                    },
                    "expected_dimensions": {"width": 390, "height": 844},
                },
            },
        ],
    }


def test_repair_packet_extracts_stitch_and_non_stitch_blockers():
    module = _load_module()

    packet = module.build_repair_packet(
        _release_payload(),
        _objective_payload(),
        generated_at="2026-07-06T12:00:00Z",
    )

    assert packet["summary"]["overall"] == "FAIL"
    assert packet["summary"]["stitch_blockers"] == [
        "home_next_step",
        "phone_binding",
        "ask_therapist_safety",
        "browser_qa_evidence",
        "frontend_l1_gate",
    ]
    assert packet["summary"]["non_stitch_blockers"] == ["agent_cloud_model"]
    assert packet["summary"]["meta_blockers"] == ["combined_l1_release"]
    assert packet["frontend_failures"][0]["gate"] == "L1-HOME-STATIC-001"
    assert packet["frontend_failures"][0]["must_remove"] == ["M33", "RoboRehab Controller"]
    assert packet["integration_gaps"] == [
        "patient_view_home",
        "phone_verification_start",
        "agent_messages",
    ]
    assert packet["browser_evidence_current"]["missing"] == ["ask_therapist_chat", "unsafe_agent_refusal"]
    assert packet["browser_evidence_current"]["invalid_dimensions"]["home_first_screen"]["actual"] == {
        "width": 375,
        "height": 812,
    }
    assert packet["required_artifacts"]["api_fixture"].endswith("rehab-mobile-l1-api-fixture-20260706.json")
    assert "qa_rehab_mobile_l1_release.py" in "\n".join(packet["verification_commands"]["powershell"])
    assert "configure_rehab_model_relay.py" in packet["non_stitch_actions"][0]["command"]


def test_cli_writes_repair_packet_from_saved_gate_payloads(tmp_path):
    module = _load_module()
    release_path = tmp_path / "release.json"
    objective_path = tmp_path / "objective.json"
    output_path = tmp_path / "repair-packet.json"
    release_path.write_text(json.dumps(_release_payload()), encoding="utf-8")
    objective_path.write_text(json.dumps(_objective_payload()), encoding="utf-8")

    exit_code = module.main(
        [
            "--release-json",
            str(release_path),
            "--objective-json",
            str(objective_path),
            "--output",
            str(output_path),
            "--generated-at",
            "2026-07-06T12:00:00Z",
        ]
    )

    assert exit_code == 0
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    assert packet["generated_at"] == "2026-07-06T12:00:00Z"
    assert packet["frontend_failures"][0]["page_url"] == "http://example.test/home.html"
    assert packet["browser_qa_required"][0]["name"] == "home_first_screen"
