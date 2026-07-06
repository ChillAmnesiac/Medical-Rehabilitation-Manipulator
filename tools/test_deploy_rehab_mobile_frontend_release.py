import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("deploy_rehab_mobile_frontend_release.py")
PREPARE_MODULE_PATH = Path(__file__).with_name("prepare_rehab_mobile_frontend_release.py")
FRONTEND_GATE_PATH = Path(__file__).with_name("qa_rehab_mobile_l1_frontend.py")


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_deploy_module():
    return _load_module(MODULE_PATH, "deploy_rehab_mobile_frontend_release")


def _write_l1_ready_frontend(source_dir: Path) -> None:
    gate_module = _load_module(FRONTEND_GATE_PATH, "qa_rehab_mobile_l1_frontend")
    source_dir.mkdir(parents=True)
    for page, config in gate_module.PAGE_GATES.items():
        body = " ".join(config["required_terms"])
        if page == "ai-plan.html":
            label = config["required_terms"][0]
            body += f'<button aria-label="{label}">{label}</button>'
        (source_dir / page).write_text(
            f'<html><body>{body}<script src="mobile-bridge.js"></script></body></html>\n',
            encoding="utf-8",
        )
    (source_dir / "mobile-bridge.js").write_text(
        """
        localStorage.setItem('access_token', token);
        fetch('/api/auth/session');
        fetch('/api/rehab-arm/app/v1/me', { headers: { Authorization: `Bearer ${token}` } });
        const home = response.data.patient_view.home;
        const profile = response.data.patient_view.profile;
        const device = response.data.patient_view.device;
        const agent = response.data.patient_view.agent;
        fetch('/api/rehab-arm/app/v1/account/phone-verifications');
        fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`);
        if (error.code === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(error.retry_after);
        if (error.code === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
        if (error.code === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
        fetch('/api/rehab-arm/app/v1/devices/bind');
        if (error.code === 'DEVICE_ALREADY_BOUND') showAlreadyBound();
        fetch('/api/rehab-arm/app/v1/agent/messages');
        if (error.code === 'UNSAFE_MOTION_REQUEST') showSafeRefusal();
        renderModelStatus(response.data.model_status);
        """,
        encoding="utf-8",
    )


def _write_browser_metrics_gate(output_dir: Path, *, status: str = "PASS") -> None:
    failed = 0 if status == "PASS" else 1
    payload = {
        "summary": {"overall": status, "failed": failed, "total": 1},
        "results": [
            {
                "gate": "L1-BROWSER-METRICS-001",
                "level": "L1",
                "status": status,
                "summary": "Rendered mobile browser QA covers all L1 pages and has no touch/layout blockers.",
                "detail": {
                    "checked_pages": ["home", "profile", "device", "ai-plan"],
                    "missing_pages": [],
                    "fake_hits": [],
                    "touch_issues": [] if status == "PASS" else [{"page": "ai-plan", "width": 40, "height": 40}],
                    "input_issues": [],
                    "overflow_issues": [],
                    "vertical_text_issues": [],
                },
            }
        ],
    }
    (output_dir / "browser-metrics-gate.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _build_manifest(tmp_path: Path) -> Path:
    prepare = _load_module(PREPARE_MODULE_PATH, "prepare_rehab_mobile_frontend_release")
    source_dir = tmp_path / "rehab-arm-mobile"
    output_dir = tmp_path / "release"
    _write_l1_ready_frontend(source_dir)
    manifest = prepare.build_release_bundle(
        source_dir=source_dir,
        output_dir=output_dir,
        generated_at="2026-07-06T16:00:00Z",
    )
    _write_browser_metrics_gate(output_dir)
    return Path(manifest["artifact"]["manifest_path"])


def test_plan_deployment_verifies_manifest_and_preserves_post_checks(tmp_path):
    module = _load_deploy_module()
    manifest_path = _build_manifest(tmp_path)

    plan = module.plan_deployment(manifest_path)

    assert plan["manifest_verification"]["overall"] == "PASS"
    assert plan["remote_web_root"].endswith("/rehab-arm-mobile")
    assert any(command.startswith("scp ") for command in plan["deploy_commands"])
    assert any(command.startswith("ssh ") for command in plan["deploy_commands"])
    assert "qa_rehab_mobile_browser_metrics.py" in "\n".join(plan["post_deploy_verification"]["commands"])
    assert "qa_rehab_mobile_l1_release.py" in "\n".join(plan["post_deploy_verification"]["commands"])
    assert "qa_rehab_mobile_l1_objective_audit.py" in "\n".join(plan["post_deploy_verification"]["commands"])
    assert "curl.exe -I -sS" in "\n".join(plan["post_deploy_verification"]["commands"])


def test_dry_run_does_not_execute_deploy_commands(tmp_path):
    module = _load_deploy_module()
    manifest_path = _build_manifest(tmp_path)
    calls = []

    exit_code, summary = module.run(["--manifest", str(manifest_path)], command_runner=calls.append)

    assert exit_code == 0
    assert summary["dry_run"] is True
    assert summary["executed"] == []
    assert calls == []
    assert summary["manifest_verification"]["overall"] == "PASS"


def test_execute_runs_deploy_commands_and_requested_post_verify(tmp_path):
    module = _load_deploy_module()
    manifest_path = _build_manifest(tmp_path)
    calls = []

    exit_code, summary = module.run(
        ["--manifest", str(manifest_path), "--execute", "--run-post-verify"],
        command_runner=calls.append,
    )

    assert exit_code == 0
    assert summary["dry_run"] is False
    assert len(calls) == 3
    assert calls[0].startswith("scp ")
    assert calls[1].startswith("ssh ")
    assert calls[2].startswith("powershell")
    assert "-EncodedCommand " in calls[2]
    assert "qa_rehab_mobile_l1_release.py" not in calls[2]
    assert summary["executed"] == calls


def test_execute_requires_post_deploy_verification(tmp_path):
    module = _load_deploy_module()
    manifest_path = _build_manifest(tmp_path)
    calls = []

    exit_code, summary = module.run(
        ["--manifest", str(manifest_path), "--execute"],
        command_runner=calls.append,
    )

    assert exit_code == 2
    assert summary["error"] == "post_deploy_verification_required"
    assert summary["executed"] == []
    assert calls == []


def test_failed_manifest_blocks_deployment(tmp_path):
    module = _load_deploy_module()
    manifest_path = _build_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["verification"]["required_browser_screenshots"] = []
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    calls = []

    exit_code, summary = module.run(
        ["--manifest", str(manifest_path), "--execute"],
        command_runner=calls.append,
    )

    assert exit_code == 2
    assert summary["manifest_verification"]["overall"] == "FAIL"
    assert summary["executed"] == []
    assert calls == []


def test_missing_browser_metrics_gate_output_blocks_deployment(tmp_path):
    module = _load_deploy_module()
    manifest_path = _build_manifest(tmp_path)
    (manifest_path.parent / "browser-metrics-gate.json").unlink()
    calls = []

    exit_code, summary = module.run(
        ["--manifest", str(manifest_path), "--execute"],
        command_runner=calls.append,
    )

    assert exit_code == 2
    assert summary["manifest_verification"]["overall"] == "FAIL"
    assert summary["executed"] == []
    assert calls == []


def test_rejects_unsafe_remote_web_root(tmp_path):
    module = _load_deploy_module()
    manifest_path = _build_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["deploy"]["remote_web_root"] = "/"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    exit_code, summary = module.run(["--manifest", str(manifest_path)], command_runner=lambda command: None)

    assert exit_code == 2
    assert summary["error"] == "unsafe_remote_web_root"
