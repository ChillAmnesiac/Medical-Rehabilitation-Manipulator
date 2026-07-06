import hashlib
import importlib.util
import json
import sys
from pathlib import Path


VERIFY_MODULE_PATH = Path(__file__).with_name("verify_rehab_mobile_frontend_release.py")
PREPARE_MODULE_PATH = Path(__file__).with_name("prepare_rehab_mobile_frontend_release.py")


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_l1_ready_frontend(source_dir: Path) -> None:
    gate_module = _load_module(Path(__file__).with_name("qa_rehab_mobile_l1_frontend.py"), "qa_rehab_mobile_l1_frontend")
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


def _write_browser_metrics_gate(output_dir: Path, *, status: str = "PASS", checked_pages=None) -> None:
    failed = 0 if status == "PASS" else 1
    pages = checked_pages or ["home", "profile", "device", "ai-plan"]
    missing_pages = [page for page in ["ai-plan", "device", "home", "profile"] if page not in pages]
    payload = {
        "summary": {"overall": status, "failed": failed, "total": 1},
        "results": [
            {
                "gate": "L1-BROWSER-METRICS-001",
                "level": "L1",
                "status": status,
                "summary": "Rendered mobile browser QA covers all L1 pages and has no touch/layout blockers.",
                "detail": {
                    "checked_pages": pages,
                    "missing_pages": missing_pages,
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
        generated_at="2026-07-06T15:00:00Z",
    )
    _write_browser_metrics_gate(output_dir)
    return Path(manifest["artifact"]["manifest_path"])


def test_verify_release_manifest_accepts_intact_stitch_bundle(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)

    payload = verify.verify_release_manifest(manifest_path)

    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["failed"] == 0
    assert payload["summary"]["manifest_path"] == str(manifest_path)
    assert {result["gate"] for result in payload["results"]} == {
        "FRONTEND-RELEASE-SCHEMA",
        "FRONTEND-RELEASE-ZIP-INTEGRITY",
        "FRONTEND-RELEASE-PREFLIGHT",
        "FRONTEND-RELEASE-PAGES",
        "FRONTEND-RELEASE-DEPLOYMENT",
        "FRONTEND-RELEASE-BROWSER-EVIDENCE",
        "FRONTEND-RELEASE-BROWSER-METRICS",
    }
    deployment = next(result for result in payload["results"] if result["gate"] == "FRONTEND-RELEASE-DEPLOYMENT")
    assert "tools\\deploy_rehab_mobile_frontend_release.py --manifest" in deployment["detail"]["executor_command"]
    assert str(manifest_path).replace("\\", "/") in deployment["detail"]["executor_command"].replace("\\", "/")


def test_verify_release_manifest_rejects_tampered_zip_hash(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    zip_path = Path(manifest["artifact"]["zip_path"])
    manifest["artifact"]["zip_sha256"] = hashlib.sha256(zip_path.read_bytes() + b"tampered").hexdigest()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = verify.verify_release_manifest(manifest_path)

    assert payload["summary"]["overall"] == "FAIL"
    failed_gates = {result["gate"] for result in payload["results"] if result["status"] == "FAIL"}
    assert failed_gates == {"FRONTEND-RELEASE-ZIP-INTEGRITY"}


def test_verify_release_manifest_rejects_failed_preflight(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report_path = Path(manifest["frontend_l1_preflight"]["report_path"])
    preflight = json.loads(report_path.read_text(encoding="utf-8"))
    preflight["summary"]["overall"] = "FAIL"
    preflight["summary"]["failed"] = 1
    report_path.write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = verify.verify_release_manifest(manifest_path)

    assert payload["summary"]["overall"] == "FAIL"
    failed_gates = {result["gate"] for result in payload["results"] if result["status"] == "FAIL"}
    assert failed_gates == {"FRONTEND-RELEASE-PREFLIGHT"}


def test_verify_release_manifest_rejects_missing_webview_mirror_command(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["verification"]["powershell"] = [
        command
        for command in manifest["verification"]["powershell"]
        if "verify_rehab_mobile_webview_mirror.py" not in command
    ]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = verify.verify_release_manifest(manifest_path)

    assert payload["summary"]["overall"] == "FAIL"
    failed_gates = {result["gate"] for result in payload["results"] if result["status"] == "FAIL"}
    assert failed_gates == {"FRONTEND-RELEASE-DEPLOYMENT"}


def test_verify_release_manifest_rejects_missing_browser_metrics_gate(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["verification"]["powershell"] = [
        command
        for command in manifest["verification"]["powershell"]
        if "qa_rehab_mobile_browser_metrics.py" not in command
    ]
    manifest["verification"].pop("required_browser_metrics_report", None)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = verify.verify_release_manifest(manifest_path)

    assert payload["summary"]["overall"] == "FAIL"
    failed_gates = {result["gate"] for result in payload["results"] if result["status"] == "FAIL"}
    assert failed_gates == {"FRONTEND-RELEASE-BROWSER-METRICS"}


def test_verify_release_manifest_rejects_missing_browser_metrics_gate_output(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)
    (manifest_path.parent / "browser-metrics-gate.json").unlink()

    payload = verify.verify_release_manifest(manifest_path)

    assert payload["summary"]["overall"] == "FAIL"
    failed_gates = {result["gate"] for result in payload["results"] if result["status"] == "FAIL"}
    assert failed_gates == {"FRONTEND-RELEASE-BROWSER-METRICS"}
    metrics = next(result for result in payload["results"] if result["gate"] == "FRONTEND-RELEASE-BROWSER-METRICS")
    assert metrics["detail"]["reason"] == "browser_metrics_gate_output_missing"


def test_verify_release_manifest_rejects_failed_browser_metrics_gate_output(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)
    _write_browser_metrics_gate(manifest_path.parent, status="FAIL")

    payload = verify.verify_release_manifest(manifest_path)

    assert payload["summary"]["overall"] == "FAIL"
    failed_gates = {result["gate"] for result in payload["results"] if result["status"] == "FAIL"}
    assert failed_gates == {"FRONTEND-RELEASE-BROWSER-METRICS"}
    metrics = next(result for result in payload["results"] if result["gate"] == "FRONTEND-RELEASE-BROWSER-METRICS")
    assert metrics["detail"]["gate_summary"]["overall"] == "FAIL"


def test_verify_release_manifest_rejects_pass_browser_metrics_with_missing_pages(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)
    _write_browser_metrics_gate(manifest_path.parent, status="PASS", checked_pages=["home"])

    payload = verify.verify_release_manifest(manifest_path)

    assert payload["summary"]["overall"] == "FAIL"
    failed_gates = {result["gate"] for result in payload["results"] if result["status"] == "FAIL"}
    assert failed_gates == {"FRONTEND-RELEASE-BROWSER-METRICS"}
    metrics = next(result for result in payload["results"] if result["gate"] == "FRONTEND-RELEASE-BROWSER-METRICS")
    assert metrics["detail"]["missing_pages"] == ["ai-plan", "device", "profile"]


def test_cli_writes_verification_report_and_returns_nonzero_on_failure(tmp_path):
    verify = _load_module(VERIFY_MODULE_PATH, "verify_rehab_mobile_frontend_release")
    manifest_path = _build_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["verification"]["required_browser_screenshots"] = []
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_path = tmp_path / "release-verification.json"

    exit_code = verify.main(["--manifest", str(manifest_path), "--output", str(output_path)])

    assert exit_code == 1
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["summary"]["overall"] == "FAIL"
    assert "FRONTEND-RELEASE-BROWSER-EVIDENCE" in {
        result["gate"] for result in report["results"] if result["status"] == "FAIL"
    }
