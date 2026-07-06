import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("verify_rehab_mobile_webview_mirror.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_rehab_mobile_webview_mirror", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_matching_sources(web_dir: Path, android_dir: Path) -> None:
    web_dir.mkdir(parents=True)
    android_dir.mkdir(parents=True)
    files = {
        "home.html": "<html><body>home 问康复师</body></html>\n",
        "profile.html": "<html><body>我的康复档案 手机号 验证码</body></html>\n",
        "device.html": "<html><body>绑定设备 打开康复设备电源</body></html>\n",
        "ai-plan.html": "<html><body>问康复师</body></html>\n",
        "mobile-bridge.js": "export const apiBase = window.REHAB_API_BASE;\n",
        "assets/app.css": "body { color: #123; }\n",
    }
    for rel_path, content in files.items():
        web_path = web_dir / rel_path
        android_path = android_dir / rel_path
        web_path.parent.mkdir(parents=True, exist_ok=True)
        android_path.parent.mkdir(parents=True, exist_ok=True)
        web_path.write_text(content, encoding="utf-8")
        android_path.write_text(content, encoding="utf-8")


def test_webview_mirror_passes_when_android_www_matches_web_source(tmp_path):
    module = _load_module()
    web_dir = tmp_path / "apps" / "web" / "public" / "rehab-arm-mobile"
    android_dir = tmp_path / "apps" / "mobile" / "rehab-arm-android" / "www"
    _write_matching_sources(web_dir, android_dir)

    payload = module.verify_webview_mirror(web_dir, android_dir)

    assert payload["schema"] == "rehab-mobile-webview-mirror-verification/v1"
    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["failed"] == 0
    assert payload["summary"]["web_file_count"] == 6
    assert payload["summary"]["android_file_count"] == 6
    assert {result["gate"] for result in payload["results"]} == {
        "WEBVIEW-MIRROR-DIRECTORIES",
        "WEBVIEW-MIRROR-REQUIRED-PAGES",
        "WEBVIEW-MIRROR-FILE-PARITY",
    }


def test_webview_mirror_fails_when_required_page_differs(tmp_path):
    module = _load_module()
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    _write_matching_sources(web_dir, android_dir)
    (android_dir / "device.html").write_text(
        "<html><body>legacy debug M33 Gatekeeper</body></html>\n",
        encoding="utf-8",
    )

    payload = module.verify_webview_mirror(web_dir, android_dir)

    assert payload["summary"]["overall"] == "FAIL"
    page_gate = next(result for result in payload["results"] if result["gate"] == "WEBVIEW-MIRROR-REQUIRED-PAGES")
    assert page_gate["status"] == "FAIL"
    assert page_gate["detail"]["mismatched_required_pages"] == ["device.html"]
    parity_gate = next(result for result in payload["results"] if result["gate"] == "WEBVIEW-MIRROR-FILE-PARITY")
    assert parity_gate["detail"]["changed_files"] == ["device.html"]


def test_webview_mirror_fails_on_missing_and_extra_stale_files(tmp_path):
    module = _load_module()
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    _write_matching_sources(web_dir, android_dir)
    (android_dir / "mobile-bridge.js").unlink()
    (android_dir / "bluetooth-debug.html").write_text("legacy debug page\n", encoding="utf-8")

    payload = module.verify_webview_mirror(web_dir, android_dir)

    assert payload["summary"]["overall"] == "FAIL"
    parity_gate = next(result for result in payload["results"] if result["gate"] == "WEBVIEW-MIRROR-FILE-PARITY")
    assert parity_gate["status"] == "FAIL"
    assert parity_gate["detail"]["missing_files"] == ["mobile-bridge.js"]
    assert parity_gate["detail"]["extra_files"] == ["bluetooth-debug.html"]


def test_cli_writes_report_and_returns_nonzero_when_mirror_is_stale(tmp_path):
    module = _load_module()
    web_dir = tmp_path / "web"
    android_dir = tmp_path / "android" / "www"
    output_path = tmp_path / "mirror-report.json"
    _write_matching_sources(web_dir, android_dir)
    (android_dir / "ai-plan.html").write_text("old agent page\n", encoding="utf-8")

    exit_code = module.main(
        [
            "--web-dir",
            str(web_dir),
            "--android-www-dir",
            str(android_dir),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 1
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["summary"]["overall"] == "FAIL"
    assert "ai-plan.html" in report["results"][1]["detail"]["mismatched_required_pages"]
