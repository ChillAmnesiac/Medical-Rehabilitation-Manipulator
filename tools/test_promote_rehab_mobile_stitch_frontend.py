import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("promote_rehab_mobile_stitch_frontend.py")
FRONTEND_GATE_PATH = Path(__file__).with_name("qa_rehab_mobile_l1_frontend.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("promote_rehab_mobile_stitch_frontend", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_frontend_gate_module():
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_l1_frontend", FRONTEND_GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_l1_ready_stitch_source(source_dir: Path) -> None:
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
    (source_dir / "assets" / "style.css").write_text("body { color: #123; }\n", encoding="utf-8")


def _write_failing_stitch_source(source_dir: Path) -> None:
    source_dir.mkdir(parents=True)
    for page in ("home.html", "profile.html", "device.html", "ai-plan.html"):
        (source_dir / page).write_text(
            f"<html><body>{page} M33 setup_required mockData</body></html>\n",
            encoding="utf-8",
        )


def test_execute_rejects_failing_stitch_source_without_replacing_targets(tmp_path):
    module = _load_module()
    stitch_source = tmp_path / "stitch"
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    output_dir = tmp_path / "promotion"
    _write_failing_stitch_source(stitch_source)
    web_dir.mkdir(parents=True)
    android_dir.mkdir(parents=True)
    (web_dir / "home.html").write_text("existing live web\n", encoding="utf-8")
    (android_dir / "home.html").write_text("existing live android\n", encoding="utf-8")

    exit_code, payload = module.run(
        [
            "--stitch-source-dir",
            str(stitch_source),
            "--web-dir",
            str(web_dir),
            "--android-www-dir",
            str(android_dir),
            "--output-dir",
            str(output_dir),
            "--execute",
        ]
    )

    assert exit_code == 2
    assert payload["schema"] == "rehab-mobile-stitch-frontend-promotion/v1"
    assert payload["summary"]["overall"] == "FAIL"
    assert payload["summary"]["copied"] is False
    assert (web_dir / "home.html").read_text(encoding="utf-8") == "existing live web\n"
    assert (android_dir / "home.html").read_text(encoding="utf-8") == "existing live android\n"
    preflight = json.loads((output_dir / "stitch-frontend-l1-preflight.json").read_text(encoding="utf-8"))
    assert preflight["summary"]["overall"] == "FAIL"


def test_dry_run_accepts_l1_ready_stitch_source_without_copying(tmp_path):
    module = _load_module()
    stitch_source = tmp_path / "stitch"
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    output_dir = tmp_path / "promotion"
    _write_l1_ready_stitch_source(stitch_source)
    web_dir.mkdir(parents=True)
    android_dir.mkdir(parents=True)
    (web_dir / "home.html").write_text("existing live web\n", encoding="utf-8")
    (android_dir / "home.html").write_text("existing live android\n", encoding="utf-8")

    exit_code, payload = module.run(
        [
            "--stitch-source-dir",
            str(stitch_source),
            "--web-dir",
            str(web_dir),
            "--android-www-dir",
            str(android_dir),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["dry_run"] is True
    assert payload["summary"]["copied"] is False
    assert payload["frontend_l1_preflight"]["overall"] == "PASS"
    assert payload["plan"]["files_to_promote"] == [
        "ai-plan.html",
        "assets/style.css",
        "device.html",
        "home.html",
        "mobile-bridge.js",
        "profile.html",
    ]
    assert (web_dir / "home.html").read_text(encoding="utf-8") == "existing live web\n"
    assert (android_dir / "home.html").read_text(encoding="utf-8") == "existing live android\n"
    saved = json.loads((output_dir / "stitch-frontend-promotion.json").read_text(encoding="utf-8"))
    assert saved["summary"]["overall"] == "PASS"


def test_dry_run_rejects_l1_ready_source_with_qa_reports_mixed_in(tmp_path):
    module = _load_module()
    stitch_source = tmp_path / "stitch"
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    output_dir = tmp_path / "promotion"
    _write_l1_ready_stitch_source(stitch_source)
    (stitch_source / "frontend-l1-source-gate-v3.json").write_text(
        '{"summary": {"overall": "PASS"}}\n',
        encoding="utf-8",
    )

    exit_code, payload = module.run(
        [
            "--stitch-source-dir",
            str(stitch_source),
            "--web-dir",
            str(web_dir),
            "--android-www-dir",
            str(android_dir),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 2
    assert payload["summary"]["overall"] == "FAIL"
    assert payload["summary"]["copied"] is False
    assert payload["frontend_l1_preflight"]["overall"] == "PASS"
    assert payload["package_cleanliness"]["status"] == "FAIL"
    assert payload["package_cleanliness"]["unexpected_files"] == ["frontend-l1-source-gate-v3.json"]
    saved = json.loads((output_dir / "stitch-frontend-promotion.json").read_text(encoding="utf-8"))
    assert saved["package_cleanliness"]["unexpected_files"] == ["frontend-l1-source-gate-v3.json"]


def test_dry_run_rejects_l1_ready_source_with_debug_routes_mixed_in(tmp_path):
    module = _load_module()
    stitch_source = tmp_path / "stitch"
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    output_dir = tmp_path / "promotion"
    _write_l1_ready_stitch_source(stitch_source)
    (stitch_source / "bluetooth-debug.html").write_text(
        "<html><body>developer bluetooth debug route</body></html>\n",
        encoding="utf-8",
    )
    (stitch_source / "emg.html").write_text(
        "<html><body>developer EMG debug route</body></html>\n",
        encoding="utf-8",
    )

    exit_code, payload = module.run(
        [
            "--stitch-source-dir",
            str(stitch_source),
            "--web-dir",
            str(web_dir),
            "--android-www-dir",
            str(android_dir),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 2
    assert payload["summary"]["overall"] == "FAIL"
    assert payload["summary"]["copied"] is False
    assert payload["frontend_l1_preflight"]["overall"] == "PASS"
    assert payload["package_cleanliness"]["status"] == "FAIL"
    assert payload["package_cleanliness"]["unexpected_files"] == ["bluetooth-debug.html", "emg.html"]
    saved = json.loads((output_dir / "stitch-frontend-promotion.json").read_text(encoding="utf-8"))
    assert saved["package_cleanliness"]["unexpected_files"] == ["bluetooth-debug.html", "emg.html"]


def test_execute_promotes_l1_ready_source_and_verifies_android_mirror(tmp_path):
    module = _load_module()
    stitch_source = tmp_path / "stitch"
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    output_dir = tmp_path / "promotion"
    _write_l1_ready_stitch_source(stitch_source)
    web_dir.mkdir(parents=True)
    android_dir.mkdir(parents=True)
    (web_dir / "home.html").write_text("old web home\n", encoding="utf-8")
    (web_dir / "legacy-debug.html").write_text("M33 debug panel\n", encoding="utf-8")
    (android_dir / "home.html").write_text("old android home\n", encoding="utf-8")
    (android_dir / "legacy-debug.html").write_text("M33 debug panel\n", encoding="utf-8")

    exit_code, payload = module.run(
        [
            "--stitch-source-dir",
            str(stitch_source),
            "--web-dir",
            str(web_dir),
            "--android-www-dir",
            str(android_dir),
            "--output-dir",
            str(output_dir),
            "--execute",
        ]
    )

    assert exit_code == 0
    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["dry_run"] is False
    assert payload["summary"]["copied"] is True
    assert payload["webview_mirror"]["overall"] == "PASS"
    assert (web_dir / "legacy-debug.html").exists() is False
    assert (android_dir / "legacy-debug.html").exists() is False
    for rel_path in payload["plan"]["files_to_promote"]:
        assert (web_dir / rel_path).read_bytes() == (stitch_source / rel_path).read_bytes()
        assert (android_dir / rel_path).read_bytes() == (stitch_source / rel_path).read_bytes()
    mirror_report = json.loads((output_dir / "webview-mirror-verification.json").read_text(encoding="utf-8"))
    assert mirror_report["summary"]["overall"] == "PASS"


def test_execute_rejects_output_dir_inside_replace_target_before_writing(tmp_path):
    module = _load_module()
    stitch_source = tmp_path / "stitch"
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    output_dir = web_dir / "promotion"
    _write_l1_ready_stitch_source(stitch_source)
    web_dir.mkdir(parents=True)
    android_dir.mkdir(parents=True)
    (web_dir / "home.html").write_text("existing live web\n", encoding="utf-8")

    exit_code, payload = module.run(
        [
            "--stitch-source-dir",
            str(stitch_source),
            "--web-dir",
            str(web_dir),
            "--android-www-dir",
            str(android_dir),
            "--output-dir",
            str(output_dir),
            "--execute",
        ]
    )

    assert exit_code == 2
    assert payload["summary"]["overall"] == "FAIL"
    assert payload["summary"]["copied"] is False
    assert payload["summary"]["error"] == "output_dir_inside_replace_target"
    assert output_dir.exists() is False
    assert (web_dir / "home.html").read_text(encoding="utf-8") == "existing live web\n"
