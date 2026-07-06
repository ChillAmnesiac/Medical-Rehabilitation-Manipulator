import importlib.util
import json
import sys
import zipfile
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("verify_rehab_mobile_apk_webview_assets.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_rehab_mobile_apk_webview_assets", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_android_www(android_www_dir: Path) -> None:
    files = {
        "home.html": "<html><body>home 问康复师</body></html>\n",
        "profile.html": "<html><body>我的康复档案 手机号</body></html>\n",
        "device.html": "<html><body>绑定设备 打开康复设备电源</body></html>\n",
        "ai-plan.html": "<html><body>问康复师</body></html>\n",
        "mobile-bridge.js": "fetch('/api/rehab-arm/app/v1/agent/messages', { method: 'POST' });\n",
        "assets/style.css": "body { color: #123; }\n",
    }
    for rel_path, content in files.items():
        path = android_www_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _write_apk(apk_path: Path, files: dict[str, bytes | str]) -> None:
    apk_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(apk_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("classes.dex", b"dex\n")
        for rel_path, content in files.items():
            data = content.encode("utf-8") if isinstance(content, str) else content
            bundle.writestr(f"assets/public/{rel_path}", data)


def _android_www_files(android_www_dir: Path) -> dict[str, bytes]:
    return {
        path.relative_to(android_www_dir).as_posix(): path.read_bytes()
        for path in android_www_dir.rglob("*")
        if path.is_file()
    }


def test_apk_webview_assets_pass_when_assets_public_matches_android_www(tmp_path):
    module = _load_module()
    android_www_dir = tmp_path / "android" / "www"
    apk_path = tmp_path / "app-debug.apk"
    _write_android_www(android_www_dir)
    _write_apk(apk_path, _android_www_files(android_www_dir))

    payload = module.verify_apk_webview_assets(apk_path, android_www_dir, "assets/public")

    assert payload["schema"] == "rehab-mobile-apk-webview-assets-verification/v1"
    assert payload["summary"]["overall"] == "PASS"
    assert payload["summary"]["failed"] == 0
    assert payload["summary"]["android_file_count"] == 6
    assert payload["summary"]["apk_webview_file_count"] == 6


def test_apk_webview_assets_fail_on_missing_changed_and_extra_files(tmp_path):
    module = _load_module()
    android_www_dir = tmp_path / "android" / "www"
    apk_path = tmp_path / "app-debug.apk"
    _write_android_www(android_www_dir)
    apk_files = _android_www_files(android_www_dir)
    apk_files.pop("mobile-bridge.js")
    apk_files["device.html"] = "<html><body>old debug M33</body></html>\n"
    apk_files["bluetooth-debug.html"] = "<html><body>developer debug page</body></html>\n"
    _write_apk(apk_path, apk_files)

    payload = module.verify_apk_webview_assets(apk_path, android_www_dir, "assets/public")

    assert payload["summary"]["overall"] == "FAIL"
    parity = next(result for result in payload["results"] if result["gate"] == "APK-WEBVIEW-FILE-PARITY")
    assert parity["status"] == "FAIL"
    assert parity["detail"]["missing_files"] == ["mobile-bridge.js"]
    assert parity["detail"]["changed_files"] == ["device.html"]
    assert parity["detail"]["extra_files"] == ["bluetooth-debug.html"]


def test_cli_writes_report_and_returns_nonzero_on_stale_apk(tmp_path):
    module = _load_module()
    android_www_dir = tmp_path / "android" / "www"
    apk_path = tmp_path / "app-debug.apk"
    output_path = tmp_path / "apk-webview-report.json"
    _write_android_www(android_www_dir)
    apk_files = _android_www_files(android_www_dir)
    apk_files["home.html"] = "<html><body>old home</body></html>\n"
    _write_apk(apk_path, apk_files)

    exit_code = module.main(
        [
            "--apk",
            str(apk_path),
            "--android-www-dir",
            str(android_www_dir),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 1
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["summary"]["overall"] == "FAIL"
    assert report["results"][2]["detail"]["changed_files"] == ["home.html"]
