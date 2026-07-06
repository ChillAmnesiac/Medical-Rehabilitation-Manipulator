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
                    "gate": "P1-PHONE-SMS-001",
                    "status": "WARN",
                    "summary": "Phone verification is using debug_sms.",
                    "detail": {
                        "mode": "debug_sms",
                        "configured": False,
                        "exposes_debug_code": True,
                        "reason": "debug_code_enabled",
                    },
                },
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
        frontend_source_commit="eaa08a40cdd3e1e62827809111f2323e7f92556f",
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
    assert packet["summary"]["ops_warnings"] == ["phone_sms_delivery"]
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
    assert packet["required_artifacts"]["stitch_prompt"].endswith(
        "rehab-mobile-l1-stitch-execution-v4-20260706.md"
    )
    assert packet["required_artifacts"]["frontend_release_tool"].endswith(
        "prepare_rehab_mobile_frontend_release.py"
    )
    assert packet["required_artifacts"]["frontend_release_verifier"].endswith(
        "verify_rehab_mobile_frontend_release.py"
    )
    assert packet["required_artifacts"]["webview_mirror_verifier"].endswith(
        "verify_rehab_mobile_webview_mirror.py"
    )
    assert packet["required_artifacts"]["browser_metrics_gate"].endswith(
        "qa_rehab_mobile_browser_metrics.py"
    )
    assert packet["required_artifacts"]["frontend_release_deployer"].endswith(
        "deploy_rehab_mobile_frontend_release.py"
    )
    assert packet["required_artifacts"]["api_fixture"].endswith("rehab-mobile-l1-api-fixture-20260706.json")
    assert packet["target"]["frontend_branch"] == "app/rehab-arm-mobile-stitch"
    assert packet["target"]["frontend_source_commit"] == "eaa08a40cdd3e1e62827809111f2323e7f92556f"
    assert packet["target"]["frontend_edit_scope"] == "apps/web/public/rehab-arm-mobile/"
    assert packet["target"]["android_webview_mirror_scope"] == "apps/mobile/rehab-arm-android/www/"
    assert packet["target"]["apk_webview_mirror_required"] is True
    assert packet["target"]["required_frontend_pages"] == ["home.html", "profile.html", "device.html", "ai-plan.html"]
    assert "Mirror the accepted web frontend files" in packet["stitch_rules"][-1]
    assert packet["required_artifacts"]["sms_delivery_runbook"].endswith(
        "rehab-mobile-sms-delivery-runbook-20260706.md"
    )
    assert packet["required_artifacts"]["sms_provider_smoke_tool"].endswith("smoke_rehab_sms_provider.py")
    assert packet["required_artifacts"]["sms_delivery_config_tool"].endswith("configure_rehab_sms_delivery.py")
    assert "qa_rehab_mobile_l1_release.py" in "\n".join(packet["verification_commands"]["powershell"])
    assert "qa_rehab_mobile_browser_metrics.py" in "\n".join(packet["verification_commands"]["powershell"])
    assert "browser-metrics-l1-390x844.json" in "\n".join(packet["verification_commands"]["powershell"])
    commands = packet["verification_commands"]["powershell"]
    metrics_index = next(index for index, command in enumerate(commands) if "qa_rehab_mobile_browser_metrics.py" in command)
    objective_index = next(index for index, command in enumerate(commands) if "qa_rehab_mobile_l1_objective_audit.py" in command)
    assert metrics_index < objective_index
    assert "--browser-metrics-json artifacts\\rehab-mobile-frontend-release\\browser-metrics-gate.json" in commands[
        objective_index
    ]
    assert "smoke_rehab_model_provider.py" in packet["non_stitch_actions"][0]["preflight_command"]
    assert "configure_rehab_model_relay.py" in packet["non_stitch_actions"][0]["configure_command"]
    sms_actions = [action for action in packet["non_stitch_actions"] if action["blocker"] == "phone_sms_delivery"]
    assert len(sms_actions) == 1
    assert "smoke_rehab_sms_provider.py" in sms_actions[0]["preflight_command"]
    assert "configure_rehab_sms_delivery.py" in sms_actions[0]["configure_command"]
    assert packet["ops_readiness_warnings"][0]["gate"] == "P1-PHONE-SMS-001"
    rendered = json.dumps(packet, ensure_ascii=False)
    forbidden_email = "".join(["3245056131", "@", "qq.com"])
    forbidden_password_command = "REHAB_QA_PASSWORD='" + "".join(["12", "34"]) + "'"
    assert forbidden_email not in rendered
    assert forbidden_password_command not in rendered


def test_repair_packet_includes_current_fail_browser_evidence(tmp_path):
    module = _load_module()
    for name in (
        "current-fail-home-clip-390x844.png",
        "current-fail-ai-plan-clip-390x844.png",
        "current-fail-device-clip2-390x844.png",
        "current-fail-profile-clip2-390x844.png",
    ):
        _write_jpeg_header(tmp_path / name, 390, 844)

    packet = module.build_repair_packet(
        _release_payload(),
        _objective_payload(),
        generated_at="2026-07-06T12:00:00Z",
        current_fail_dir=tmp_path,
    )

    assert [item["screen"] for item in packet["current_fail_evidence"]] == [
        "home",
        "ai-plan",
        "device",
        "profile",
    ]
    assert packet["current_fail_evidence"][0]["dimensions"] == {"width": 390, "height": 844}
    assert packet["current_fail_evidence"][0]["purpose"] == "Documents current deployed frontend failure only."
    assert packet["current_fail_evidence"][0]["counts_for_l1_success"] is False


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
            "--frontend-source-commit",
            "eaa08a40cdd3e1e62827809111f2323e7f92556f",
        ]
    )

    assert exit_code == 0
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    assert packet["generated_at"] == "2026-07-06T12:00:00Z"
    assert packet["target"]["frontend_source_commit"] == "eaa08a40cdd3e1e62827809111f2323e7f92556f"
    assert packet["frontend_failures"][0]["page_url"] == "http://example.test/home.html"
    assert packet["browser_qa_required"][0]["name"] == "home_first_screen"


def test_cli_accepts_utf16_saved_gate_payloads(tmp_path):
    module = _load_module()
    release_path = tmp_path / "release-utf16.json"
    objective_path = tmp_path / "objective-utf16.json"
    output_path = tmp_path / "repair-packet.json"
    release_path.write_text(json.dumps(_release_payload()), encoding="utf-16")
    objective_path.write_text(json.dumps(_objective_payload()), encoding="utf-16")

    exit_code = module.main(
        [
            "--release-json",
            str(release_path),
            "--objective-json",
            str(objective_path),
            "--output",
            str(output_path),
            "--generated-at",
            "2026-07-07T03:31:02+08:00",
        ]
    )

    assert exit_code == 0
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    assert packet["summary"]["overall"] == "FAIL"
