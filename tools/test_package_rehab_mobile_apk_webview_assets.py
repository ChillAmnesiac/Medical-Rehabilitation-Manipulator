import importlib.util
import sys
import zipfile
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("package_rehab_mobile_apk_webview_assets.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("package_rehab_mobile_apk_webview_assets", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_template_apk(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as apk:
        apk.writestr("classes.dex", b"dex\n")
        apk.writestr("AndroidManifest.xml", b"manifest\n")
        apk.writestr("resources.arsc", b"resources\n")
        apk.writestr("META-INF/CERT.SF", b"old signature\n")
        apk.writestr("META-INF/CERT.RSA", b"old signature\n")
        apk.writestr("assets/public/home.html", b"old home\n")
        apk.writestr("assets/public/bluetooth-debug.html", b"debug\n")
        apk.writestr("assets/other/native-config.json", b"keep me\n")


def _write_android_www(root: Path) -> None:
    files = {
        "home.html": "<html>accepted home</html>\n",
        "profile.html": "<html>accepted profile</html>\n",
        "device.html": "<html>accepted device</html>\n",
        "ai-plan.html": "<html>accepted therapist</html>\n",
        "assets/style.css": "body { color: #234; }\n",
    }
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))


def _zip_names(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as apk:
        return sorted(name for name in apk.namelist() if not name.endswith("/"))


def _read_zip(path: Path, name: str) -> bytes:
    with zipfile.ZipFile(path) as apk:
        return apk.read(name)


def test_replace_webview_assets_removes_stale_files_and_old_signatures(tmp_path):
    module = _load_module()
    template_apk = tmp_path / "template.apk"
    android_www_dir = tmp_path / "android-www"
    unsigned_apk = tmp_path / "rebundled.apk"
    _write_template_apk(template_apk)
    _write_android_www(android_www_dir)

    report = module.replace_webview_assets(
        template_apk=template_apk,
        android_www_dir=android_www_dir,
        output_apk=unsigned_apk,
        asset_prefix="assets/public",
    )

    assert report["summary"]["overall"] == "PASS"
    assert report["summary"]["added_webview_files"] == 5
    assert report["summary"]["removed_template_webview_files"] == 2
    assert report["summary"]["removed_signature_files"] == 2
    assert "assets/public/bluetooth-debug.html" not in _zip_names(unsigned_apk)
    assert "META-INF/CERT.SF" not in _zip_names(unsigned_apk)
    assert "META-INF/CERT.RSA" not in _zip_names(unsigned_apk)
    assert "assets/other/native-config.json" in _zip_names(unsigned_apk)
    assert _read_zip(unsigned_apk, "assets/public/home.html") == b"<html>accepted home</html>\n"
    assert _read_zip(unsigned_apk, "assets/public/assets/style.css") == b"body { color: #234; }\n"


def test_replace_webview_assets_fails_without_required_l1_pages(tmp_path):
    module = _load_module()
    template_apk = tmp_path / "template.apk"
    android_www_dir = tmp_path / "android-www"
    unsigned_apk = tmp_path / "rebundled.apk"
    _write_template_apk(template_apk)
    _write_android_www(android_www_dir)
    (android_www_dir / "ai-plan.html").unlink()

    report = module.replace_webview_assets(
        template_apk=template_apk,
        android_www_dir=android_www_dir,
        output_apk=unsigned_apk,
        asset_prefix="assets/public",
    )

    assert report["summary"]["overall"] == "FAIL"
    assert report["results"][0]["gate"] == "APK-PACKAGE-INPUTS"
    assert report["results"][0]["status"] == "FAIL"
    assert report["results"][0]["detail"]["missing_required_pages"] == ["ai-plan.html"]
    assert not unsigned_apk.exists()


def test_redact_command_hides_keystore_passwords():
    module = _load_module()

    redacted = module.redact_command(
        [
            "apksigner",
            "sign",
            "--ks-pass",
            "pass:android",
            "--key-pass",
            "pass:android",
            "--ks-key-alias",
            "androiddebugkey",
            "-storepass",
            "android",
        ],
        ["android"],
    )

    assert "android" not in redacted
    assert "pass:android" not in redacted
    assert redacted == [
        "apksigner",
        "sign",
        "--ks-pass",
        "pass:<redacted>",
        "--key-pass",
        "pass:<redacted>",
        "--ks-key-alias",
        "androiddebugkey",
        "-storepass",
        "<redacted>",
    ]
