from pathlib import Path
import hashlib


APP_NEXT_CONFIG = Path("artifacts/external/rehab-arm-mobile-stitch/apps/web/next.config.js")
APP_DOWNLOAD_PAGE = Path("artifacts/external/rehab-arm-mobile-stitch/apps/web/public/downloads/rehab-arm/index.html")
APP_DOWNLOAD_APK = Path(
    "artifacts/external/rehab-arm-mobile-stitch/apps/web/public/downloads/rehab-arm/lingdong-rehab-arm-debug.apk"
)


def test_rehab_mobile_download_page_route_redirects_to_static_index():
    source = APP_NEXT_CONFIG.read_text(encoding="utf-8")

    assert 'source: "/downloads/rehab-arm"' in source
    assert 'destination: "/downloads/rehab-arm/index.html"' in source


def test_rehab_mobile_download_page_metadata_matches_packaged_apk_without_test_credentials():
    source = APP_DOWNLOAD_PAGE.read_text(encoding="utf-8")
    apk_bytes = APP_DOWNLOAD_APK.read_bytes()
    digest = hashlib.sha256(apk_bytes).hexdigest().upper()

    assert f"{len(apk_bytes):,} bytes" in source
    assert digest in source
    assert "3245056131@qq.com" not in source
    assert "1234" not in source
