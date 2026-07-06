import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("export_rehab_mobile_stitch_prompt.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("export_rehab_mobile_stitch_prompt", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _packet():
    return {
        "schema": "rehab-mobile-stitch-repair-packet/v1",
        "generated_at": "2026-07-06T13:30:00Z",
        "target": {
            "api_base": "http://106.55.62.122:8011",
            "web_base": "http://106.55.62.122:3001/rehab-arm-mobile",
            "frontend_edit_scope": "apps/web/public/rehab-arm-mobile/",
        },
        "summary": {
            "stitch_blockers": ["home_next_step", "phone_binding"],
            "non_stitch_blockers": ["agent_cloud_model"],
        },
        "required_artifacts": {
            "api_fixture": "docs/stitch/rehab-mobile-l1-api-fixture-20260706.json",
            "stitch_runbook": "docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md",
            "frontend_release_tool": "tools/prepare_rehab_mobile_frontend_release.py",
        },
        "frontend_failures": [
            {
                "gate": "L1-HOME-STATIC-001",
                "summary": "Home still exposes technical terms.",
                "must_add": ["问康复师"],
                "must_remove": ["M33", "M55"],
                "visible_text_sample": "setup_required M33",
            }
        ],
        "integration_gaps": ["patient_view_home", "agent_messages"],
        "browser_evidence_current": {
            "missing": ["home_first_screen", "ask_therapist_chat"],
            "expected_dimensions": {"width": 390, "height": 844},
        },
        "current_fail_evidence": [
            {
                "screen": "home",
                "file": "docs/qa/current-fail-home-clip-390x844.png",
                "dimensions": {"width": 390, "height": 844},
                "counts_for_l1_success": False,
            }
        ],
        "browser_qa_required": [
            {
                "name": "home_first_screen",
                "expected_filename": "l1-home-390.png",
                "viewport": "390x844",
                "must_show": ["one clear next action"],
            }
        ],
        "verification_commands": {
            "powershell": [
                ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe tools\\qa_rehab_mobile_l1_release.py",
                ".\\cloud\\rehab-platform\\.venv\\Scripts\\python.exe tools\\qa_rehab_mobile_l1_objective_audit.py",
            ]
        },
    }


def test_render_prompt_includes_repair_packet_evidence_and_acceptance_commands():
    module = _load_module()

    prompt = module.render_prompt(_packet(), generated_at="2026-07-06T13:30:00Z")

    assert "Stitch Execution Prompt V4" in prompt
    assert "apps/web/public/rehab-arm-mobile/" in prompt
    assert "Do not change backend code" in prompt
    assert "docs/stitch/rehab-mobile-l1-api-fixture-20260706.json" in prompt
    assert "Do not hard-code fixture values" in prompt
    assert "docs/qa/current-fail-home-clip-390x844.png" in prompt
    assert "counts_for_l1_success = false" in prompt
    assert "L1-HOME-STATIC-001" in prompt
    assert "patient_view_home" in prompt
    assert "agent_messages" in prompt
    assert "agent_cloud_model" in prompt
    assert "qa_rehab_mobile_l1_release.py" in prompt
    assert "qa_rehab_mobile_l1_objective_audit.py" in prompt
    assert "prepare_rehab_mobile_frontend_release.py" in prompt
    assert "verify_rehab_mobile_frontend_release.py" in prompt
    assert "--source-dir apps/web/public/rehab-arm-mobile" in prompt
    assert "qa_rehab_mobile_l1_frontend.py --source-dir" in prompt
    assert "--output artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json" in prompt


def test_cli_writes_prompt_from_repair_packet(tmp_path):
    module = _load_module()
    packet_path = tmp_path / "repair-packet.json"
    output_path = tmp_path / "prompt.md"
    packet_path.write_text(json.dumps(_packet()), encoding="utf-8")

    exit_code = module.main(
        [
            "--repair-packet",
            str(packet_path),
            "--output",
            str(output_path),
            "--generated-at",
            "2026-07-06T13:30:00Z",
        ]
    )

    assert exit_code == 0
    prompt = output_path.read_text(encoding="utf-8")
    assert "Stitch Execution Prompt V4" in prompt
    assert "docs/qa/current-fail-home-clip-390x844.png" in prompt
    assert "prepare_rehab_mobile_frontend_release.py" in prompt
    assert "verify_rehab_mobile_frontend_release.py" in prompt
    assert "qa_rehab_mobile_l1_frontend.py --source-dir" in prompt
    assert "frontend-l1-preflight.json" in prompt
