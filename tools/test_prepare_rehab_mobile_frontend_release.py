import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("prepare_rehab_mobile_frontend_release.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("prepare_rehab_mobile_frontend_release", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_frontend(source_dir: Path) -> None:
    gate_module = _load_frontend_gate_module()
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
        """,
        encoding="utf-8",
    )
    (source_dir / "assets").mkdir()
    (source_dir / "assets" / "style.css").write_text("body { color: #111; }\n", encoding="utf-8")


def _load_frontend_gate_module():
    gate_path = Path(__file__).with_name("qa_rehab_mobile_l1_frontend.py")
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_l1_frontend", gate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_release_bundle_validates_pages_and_manifest(tmp_path):
    module = _load_module()
    source_dir = tmp_path / "rehab-arm-mobile"
    output_dir = tmp_path / "release"
    _write_frontend(source_dir)

    manifest = module.build_release_bundle(
        source_dir=source_dir,
        output_dir=output_dir,
        generated_at="2026-07-06T14:00:00Z",
        api_base="http://106.55.62.122:8011",
        web_base="http://106.55.62.122:3001/rehab-arm-mobile",
        apk_url="http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk",
        remote_web_root="/home/ubuntu/apps/ai-collab/apps/web/public/rehab-arm-mobile",
    )

    artifact_path = Path(manifest["artifact"]["zip_path"])
    manifest_path = Path(manifest["artifact"]["manifest_path"])
    preflight_path = Path(manifest["frontend_l1_preflight"]["report_path"])
    assert artifact_path.exists()
    assert manifest_path.exists()
    assert preflight_path.exists()
    assert manifest["schema"] == "rehab-mobile-frontend-release/v1"
    assert manifest["source"]["required_pages_present"] is True
    assert manifest["source"]["missing_required_pages"] == []
    assert set(manifest["source"]["required_pages"]) == {"home.html", "profile.html", "device.html", "ai-plan.html"}
    assert manifest["artifact"]["file_count"] == 6
    assert manifest["artifact"]["zip_sha256"] == hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    assert manifest["frontend_l1_preflight"]["overall"] == "PASS"
    assert manifest["frontend_l1_preflight"]["failed"] == 0
    assert json.loads(preflight_path.read_text(encoding="utf-8"))["summary"]["overall"] == "PASS"
    assert manifest["deploy"]["remote_web_root"].endswith("/rehab-arm-mobile")
    assert "deploy_rehab_mobile_frontend_release.py" in manifest["deploy"]["executor_command"]
    assert "verify_rehab_mobile_frontend_release.py" in "\n".join(manifest["verification"]["powershell"])
    assert "verify_rehab_mobile_webview_mirror.py" in "\n".join(manifest["verification"]["powershell"])
    assert "webview-mirror-verification.json" in "\n".join(manifest["verification"]["powershell"])
    assert manifest["verification"]["required_browser_metrics_report"] == "browser-metrics-l1-390x844.json"
    assert "qa_rehab_mobile_browser_metrics.py" in "\n".join(manifest["verification"]["powershell"])
    assert "browser-metrics-l1-390x844.json" in "\n".join(manifest["verification"]["powershell"])
    assert "browser-metrics-gate.json" in "\n".join(manifest["verification"]["powershell"])
    verifier_index = next(
        index
        for index, command in enumerate(manifest["verification"]["powershell"])
        if "verify_rehab_mobile_frontend_release.py" in command
    )
    metrics_index = next(
        index
        for index, command in enumerate(manifest["verification"]["powershell"])
        if "qa_rehab_mobile_browser_metrics.py" in command
    )
    assert metrics_index < verifier_index
    assert "qa_rehab_mobile_l1_release.py" in "\n".join(manifest["verification"]["powershell"])
    assert "scp" in "\n".join(manifest["deploy"]["commands"])
    verification_script = "\n".join(manifest["verification"]["powershell"])
    forbidden_email = "".join(["3245056131", "@", "qq.com"])
    forbidden_password = "REHAB_QA_PASSWORD='" + "".join(["12", "34"]) + "'"
    assert forbidden_email not in verification_script
    assert forbidden_password not in verification_script
    assert "$env:REHAB_QA_EMAIL" not in verification_script
    assert "$env:REHAB_QA_PASSWORD" not in verification_script

    with zipfile.ZipFile(artifact_path) as bundle:
        assert sorted(bundle.namelist()) == [
            "ai-plan.html",
            "assets/style.css",
            "device.html",
            "home.html",
            "mobile-bridge.js",
            "profile.html",
        ]

    saved_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert saved_manifest["artifact"]["zip_sha256"] == manifest["artifact"]["zip_sha256"]


def test_build_release_bundle_rejects_missing_required_pages(tmp_path):
    module = _load_module()
    source_dir = tmp_path / "rehab-arm-mobile"
    source_dir.mkdir()
    (source_dir / "home.html").write_text("<html>home</html>", encoding="utf-8")

    try:
        module.build_release_bundle(
            source_dir=source_dir,
            output_dir=tmp_path / "release",
            generated_at="2026-07-06T14:00:00Z",
        )
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing pages to raise ValueError")

    assert "profile.html" in message
    assert "device.html" in message
    assert "ai-plan.html" in message


def test_build_release_bundle_rejects_frontend_that_fails_l1_preflight(tmp_path):
    module = _load_module()
    source_dir = tmp_path / "rehab-arm-mobile"
    source_dir.mkdir()
    for page in ("home.html", "profile.html", "device.html", "ai-plan.html"):
        (source_dir / page).write_text(f"<html><body>{page} M33 setup_required</body></html>", encoding="utf-8")

    output_dir = tmp_path / "release"
    try:
        module.build_release_bundle(
            source_dir=source_dir,
            output_dir=output_dir,
            generated_at="2026-07-06T14:00:00Z",
        )
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected failing L1 preflight to raise ValueError")

    assert "frontend L1 local preflight failed" in message
    failure_report = output_dir / "frontend-l1-preflight.json"
    assert failure_report.exists()
    payload = json.loads(failure_report.read_text(encoding="utf-8"))
    assert payload["summary"]["overall"] == "FAIL"


def test_cli_writes_release_manifest(tmp_path):
    module = _load_module()
    source_dir = tmp_path / "rehab-arm-mobile"
    output_dir = tmp_path / "release"
    _write_frontend(source_dir)

    exit_code = module.main(
        [
            "--source-dir",
            str(source_dir),
            "--output-dir",
            str(output_dir),
            "--generated-at",
            "2026-07-06T14:00:00Z",
        ]
    )

    assert exit_code == 0
    manifest_path = output_dir / "rehab-mobile-frontend-release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["source"]["path"] == str(source_dir)
    assert Path(manifest["artifact"]["zip_path"]).exists()
