import argparse
import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("export_rehab_mobile_l1_evidence.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("export_rehab_mobile_l1_evidence", MODULE_PATH)
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
            "api_p0_failed": 0,
            "frontend_overall": "FAIL",
            "frontend_failed": 5,
            "blocking_gates": ["frontend_l1_gate", "agent_cloud_model"],
        },
        "api": {"summary": {"overall": "PASS", "p0_failed": 0}},
        "frontend": {"summary": {"overall": "FAIL", "failed": 5}},
    }


def _objective_payload():
    return {
        "summary": {
            "overall": "FAIL",
            "failed": 8,
            "total": 11,
            "blocking_requirements": ["home_next_step", "browser_qa_evidence", "combined_l1_release"],
        },
        "requirements": [
            {
                "requirement": "browser_qa_evidence",
                "status": "FAIL",
                "summary": "Browser QA screenshots are incomplete.",
                "evidence": {
                    "screenshot_dir": "docs/qa/rehab-mobile-20260706/screenshots",
                    "matched": {},
                    "missing": ["home_first_screen", "ask_therapist_chat"],
                    "invalid_dimensions": {},
                    "expected_dimensions": {"width": 390, "height": 844},
                },
            }
        ],
    }


def test_build_evidence_includes_l1_gates_browser_apk_health_and_git():
    module = _load_module()
    args = argparse.Namespace(
        api_base="http://api.example",
        web_base="http://web.example/rehab-arm-mobile",
        web_origin="http://web.example",
        apk_url="http://web.example/app.apk",
        screenshots_dir=Path("docs/qa/rehab-mobile-20260706/screenshots"),
        timeout=3,
        email="3245056131@qq.com",
        password="1234",
    )

    evidence = module.build_evidence(
        args,
        generated_at="2026-07-06T16:00:00Z",
        release_runner=lambda _args: (1, _release_payload()),
        objective_runner=lambda _release_payload, _screenshots_dir: _objective_payload(),
        health_getter=lambda _api_base, _timeout: {
            "status": 200,
            "body": {"data": {"deployment": {"build_sha": "d2f81c92", "app_env": "staging"}}},
        },
        apk_head_getter=lambda _url, _timeout: {
            "status": 200,
            "content_length": 4198462,
            "content_type": "application/vnd.android.package-archive",
            "headers": {"Content-Length": "4198462"},
        },
        git_getter=lambda: {"branch": "codex/rehab-mobile-backend-qa-20260706", "head": "abc5678"},
    )

    assert evidence["schema"] == "rehab-mobile-l1-evidence/v1"
    assert evidence["generated_at"] == "2026-07-06T16:00:00Z"
    assert evidence["summary"]["overall"] == "FAIL"
    assert evidence["summary"]["release_overall"] == "FAIL"
    assert evidence["summary"]["objective_overall"] == "FAIL"
    assert evidence["summary"]["release_blocking_gates"] == ["frontend_l1_gate", "agent_cloud_model"]
    assert evidence["release"]["exit_code"] == 1
    assert evidence["objective"]["summary"]["failed"] == 8
    assert evidence["browser_evidence"]["missing"] == ["home_first_screen", "ask_therapist_chat"]
    assert evidence["apk_head"]["status"] == 200
    assert evidence["apk_head"]["content_length"] == 4198462
    assert evidence["health"]["body"]["data"]["deployment"]["build_sha"] == "d2f81c92"
    assert evidence["git"]["branch"] == "codex/rehab-mobile-backend-qa-20260706"
    assert evidence["required_artifacts"]["scorecard"].endswith("APP_COMPLETION_SCORECARD.md")
    assert evidence["required_artifacts"]["l1_evidence_exporter"].endswith("export_rehab_mobile_l1_evidence.py")
    assert evidence["required_artifacts"]["webview_mirror_verifier"].endswith(
        "verify_rehab_mobile_webview_mirror.py"
    )
    assert evidence["required_artifacts"]["l1_evidence_default_output"].endswith("rehab-mobile-l1-evidence.json")
    assert "1234" not in json.dumps(evidence, ensure_ascii=False)


def test_main_writes_evidence_and_only_fails_l1_when_requested(tmp_path, monkeypatch):
    module = _load_module()
    output_path = tmp_path / "evidence.json"
    calls = {"release": 0, "health": 0, "apk": 0, "git": 0}

    def fake_release(_args):
        calls["release"] += 1
        return 1, _release_payload()

    def fake_health(_api_base, _timeout):
        calls["health"] += 1
        return {"status": 200, "body": {"data": {"deployment": {"build_sha": "d2f81c92"}}}}

    def fake_apk(_url, _timeout):
        calls["apk"] += 1
        return {
            "status": 200,
            "content_length": 4198462,
            "content_type": "application/vnd.android.package-archive",
        }

    def fake_git():
        calls["git"] += 1
        return {"branch": "codex/test", "head": "abc1234"}

    monkeypatch.setattr(module, "_run_release_gate", fake_release)
    monkeypatch.setattr(
        module.qa_rehab_mobile_l1_objective_audit,
        "audit_objective",
        lambda _release_payload, _screenshots_dir: _objective_payload(),
    )
    monkeypatch.setattr(
        module,
        "fetch_health",
        fake_health,
    )
    monkeypatch.setattr(
        module,
        "head_apk",
        fake_apk,
    )
    monkeypatch.setattr(module, "git_info", fake_git)

    exit_code = module.main(["--output", str(output_path), "--generated-at", "2026-07-06T16:00:00Z"])

    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["overall"] == "FAIL"
    assert payload["release"]["exit_code"] == 1

    fail_code = module.main(
        [
            "--output",
            str(output_path),
            "--generated-at",
            "2026-07-06T16:00:00Z",
            "--fail-on-l1-fail",
        ]
    )

    assert fail_code == 1
    assert calls == {"release": 2, "health": 2, "apk": 2, "git": 2}
