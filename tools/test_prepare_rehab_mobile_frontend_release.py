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
    source_dir.mkdir(parents=True)
    for page in ("home.html", "profile.html", "device.html", "ai-plan.html"):
        (source_dir / page).write_text(f"<html><body>{page}</body></html>\n", encoding="utf-8")
    (source_dir / "mobile-bridge.js").write_text("window.__rehabBridge = true;\n", encoding="utf-8")
    (source_dir / "assets").mkdir()
    (source_dir / "assets" / "style.css").write_text("body { color: #111; }\n", encoding="utf-8")


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
    assert artifact_path.exists()
    assert manifest_path.exists()
    assert manifest["schema"] == "rehab-mobile-frontend-release/v1"
    assert manifest["source"]["required_pages_present"] is True
    assert manifest["source"]["missing_required_pages"] == []
    assert set(manifest["source"]["required_pages"]) == {"home.html", "profile.html", "device.html", "ai-plan.html"}
    assert manifest["artifact"]["file_count"] == 6
    assert manifest["artifact"]["zip_sha256"] == hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    assert manifest["deploy"]["remote_web_root"].endswith("/rehab-arm-mobile")
    assert "qa_rehab_mobile_l1_release.py" in "\n".join(manifest["verification"]["powershell"])
    assert "scp" in "\n".join(manifest["deploy"]["commands"])

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
