import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("qa_rehab_mobile_l1_frontend.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_l1_frontend", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_local_frontend(source_dir: Path, module) -> None:
    source_dir.mkdir()
    (source_dir / "mobile-bridge.js").write_text(
        """
        localStorage.setItem('access_token', token);
        fetch('/api/auth/session');
        fetch('/api/rehab-arm/app/v1/me', { headers: { Authorization: `Bearer ${token}` } });
        const home = response.data.patient_view.home;
        const profile = response.data.patient_view.profile;
        const device = response.data.patient_view.device;
        const agent = response.data.patient_view.agent;
        fetch('/api/rehab-arm/app/v1/account/phone-verifications', { method: 'POST' });
        fetch(`/api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm`, { method: 'POST' });
        if (error.code === 'PHONE_CODE_RESEND_TOO_SOON') showRetry(error.retry_after);
        if (error.code === 'PHONE_SMS_NOT_CONFIGURED') showSmsUnavailable();
        if (error.code === 'PHONE_SMS_DELIVERY_FAILED') showSmsFailed();
        fetch('/api/rehab-arm/app/v1/devices/bind', { method: 'POST' });
        if (error.code === 'DEVICE_ALREADY_BOUND') showAlreadyBound();
        fetch('/api/rehab-arm/app/v1/agent/messages', { method: 'POST' });
        if (error.code === 'UNSAFE_MOTION_REQUEST') showSafeRefusal();
        renderModelStatus(response.data.model_status);
        document.querySelectorAll('[data-nav-target]').forEach((control) => {
          control.addEventListener('click', () => {
            window.location.href = control.getAttribute('data-nav-target');
          });
        });
        """,
        encoding="utf-8",
    )
    for page, config in module.PAGE_GATES.items():
        body = " ".join(config["required_terms"])
        if page == "home.html":
            body += """
            <button class="primary-action" data-nav-target="ai-plan.html">Review therapist suggestion</button>
            <button class="ask-therapist-action" data-nav-target="ai-plan.html">Ask therapist</button>
            """
        if page == "ai-plan.html":
            body += '<button aria-label="闂悍澶嶅笀">闂悍澶嶅笀</button>'
        (source_dir / page).write_text(
            f'<html><body>{body}<script src="mobile-bridge.js"></script></body></html>',
            encoding="utf-8",
        )


def test_run_checks_local_source_dir_with_same_l1_rules(tmp_path):
    module = _load_module()
    source_dir = tmp_path / "rehab-arm-mobile"
    _write_local_frontend(source_dir, module)

    exit_code, payload = module.run(module.parse_args(["--source-dir", str(source_dir)]))

    assert exit_code == 0
    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["source_dir"] == str(source_dir)
    assert payload["summary"]["web_base"] is None
    integration = next(result for result in payload["results"] if result["gate"] == "L1-FRONTEND-INTEGRATION-001")
    assert integration["status"] == "PASS"


def test_run_local_source_dir_reports_missing_required_page(tmp_path):
    module = _load_module()
    source_dir = tmp_path / "rehab-arm-mobile"
    source_dir.mkdir()
    (source_dir / "home.html").write_text("<html>home</html>", encoding="utf-8")

    exit_code, payload = module.run(module.parse_args(["--source-dir", str(source_dir)]))

    assert exit_code == 1
    assert payload["summary"]["overall"] == "FAIL"
    missing = [result for result in payload["results"] if result["detail"].get("reason") == "local_file_missing"]
    assert {result["detail"]["path"] for result in missing} == {
        str(source_dir / "profile.html"),
        str(source_dir / "device.html"),
        str(source_dir / "ai-plan.html"),
    }


def test_cli_writes_frontend_gate_payload_to_output_file(tmp_path):
    module = _load_module()
    source_dir = tmp_path / "rehab-arm-mobile"
    output_path = tmp_path / "frontend-l1-preflight.json"
    _write_local_frontend(source_dir, module)

    exit_code = module.main(["--source-dir", str(source_dir), "--output", str(output_path)])

    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["source_dir"] == str(source_dir)
    integration = next(result for result in payload["results"] if result["gate"] == "L1-FRONTEND-INTEGRATION-001")
    assert integration["status"] == "PASS"
