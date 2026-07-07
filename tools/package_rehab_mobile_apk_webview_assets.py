#!/usr/bin/env python3
"""Package a rehab mobile staging APK with accepted WebView assets."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


SCHEMA = "rehab-mobile-apk-webview-package/v1"
DEFAULT_ASSET_PREFIX = "assets/public"
DEFAULT_KEYSTORE = Path("artifacts/rehab-mobile-apk-signing/rehab-mobile-l1-debug.keystore")
DEFAULT_KEY_ALIAS = "androiddebugkey"
DEFAULT_KEY_PASSWORD = "android"
REQUIRED_PAGES = ("home.html", "profile.html", "device.html", "ai-plan.html")


@dataclass
class Result:
    gate: str
    level: str
    status: str
    summary: str
    detail: Any = None


def _result(gate: str, ok: bool, summary: str, detail: Any = None) -> Result:
    return Result(
        gate=gate,
        level="L1",
        status="PASS" if ok else "FAIL",
        summary=summary,
        detail=detail,
    )


def _normalized_prefix(asset_prefix: str) -> str:
    return asset_prefix.strip("/").replace("\\", "/")


def _is_webview_entry(name: str, asset_prefix: str) -> bool:
    prefix = _normalized_prefix(asset_prefix)
    return name == prefix or name.startswith(f"{prefix}/")


def _is_apk_signature_entry(name: str) -> bool:
    upper = name.replace("\\", "/").upper()
    if not upper.startswith("META-INF/"):
        return False
    leaf = upper.rsplit("/", 1)[-1]
    return leaf == "MANIFEST.MF" or leaf.endswith((".SF", ".RSA", ".DSA", ".EC"))


def _android_files(android_www_dir: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    if not android_www_dir.exists() or not android_www_dir.is_dir():
        return files
    for path in sorted(item for item in android_www_dir.rglob("*") if item.is_file()):
        files[path.relative_to(android_www_dir).as_posix()] = path.read_bytes()
    return files


def _copy_zipinfo(info: zipfile.ZipInfo, filename: str | None = None) -> zipfile.ZipInfo:
    clone = zipfile.ZipInfo(filename=filename or info.filename, date_time=info.date_time)
    clone.comment = info.comment
    clone.extra = info.extra
    clone.internal_attr = info.internal_attr
    clone.external_attr = info.external_attr
    clone.create_system = info.create_system
    clone.compress_type = info.compress_type
    return clone


def _make_asset_info(filename: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(filename=filename)
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def _check_inputs(template_apk: Path, android_www_dir: Path, output_apk: Path, asset_prefix: str) -> Result:
    prefix = _normalized_prefix(asset_prefix)
    missing_required_pages = [page for page in REQUIRED_PAGES if not (android_www_dir / page).is_file()]
    ok = (
        template_apk.is_file()
        and android_www_dir.is_dir()
        and bool(prefix)
        and bool(output_apk.name)
        and not missing_required_pages
    )
    return _result(
        "APK-PACKAGE-INPUTS",
        ok,
        "Template APK, accepted Android WebView assets, and output target are available.",
        {
            "template_apk": str(template_apk),
            "template_apk_exists": template_apk.is_file(),
            "android_www_dir": str(android_www_dir),
            "android_www_dir_exists": android_www_dir.is_dir(),
            "output_apk": str(output_apk),
            "asset_prefix": prefix,
            "missing_required_pages": missing_required_pages,
        },
    )


def replace_webview_assets(
    *,
    template_apk: Path,
    android_www_dir: Path,
    output_apk: Path,
    asset_prefix: str = DEFAULT_ASSET_PREFIX,
) -> dict[str, Any]:
    template_apk = Path(template_apk)
    android_www_dir = Path(android_www_dir)
    output_apk = Path(output_apk)
    prefix = _normalized_prefix(asset_prefix)
    input_result = _check_inputs(template_apk, android_www_dir, output_apk, prefix)
    if input_result.status == "FAIL":
        return {
            "schema": SCHEMA,
            "target": {
                "template_apk": str(template_apk),
                "android_www_dir": str(android_www_dir),
                "output_apk": str(output_apk),
                "asset_prefix": prefix,
            },
            "summary": {
                "overall": "FAIL",
                "added_webview_files": 0,
                "removed_template_webview_files": 0,
                "removed_signature_files": 0,
            },
            "results": [input_result.__dict__],
        }

    android_files = _android_files(android_www_dir)
    removed_template_webview_files = 0
    removed_signature_files = 0
    kept_files = 0
    output_apk.parent.mkdir(parents=True, exist_ok=True)
    tmp_apk = output_apk.with_name(f"{output_apk.name}.tmp")
    if tmp_apk.exists():
        tmp_apk.unlink()

    with zipfile.ZipFile(template_apk) as src, zipfile.ZipFile(tmp_apk, "w") as dst:
        for info in src.infolist():
            name = info.filename.replace("\\", "/")
            if info.is_dir():
                continue
            if _is_webview_entry(name, prefix):
                removed_template_webview_files += 1
                continue
            if _is_apk_signature_entry(name):
                removed_signature_files += 1
                continue
            dst.writestr(_copy_zipinfo(info), src.read(info.filename), compress_type=info.compress_type)
            kept_files += 1
        for rel_path, data in android_files.items():
            dst.writestr(_make_asset_info(f"{prefix}/{rel_path}"), data)

    tmp_apk.replace(output_apk)
    package_result = _result(
        "APK-PACKAGE-WEBVIEW-ASSETS",
        True,
        "Template APK was rebundled with accepted WebView assets and without old signature entries.",
        {
            "kept_template_files": kept_files,
            "added_webview_files": len(android_files),
            "removed_template_webview_files": removed_template_webview_files,
            "removed_signature_files": removed_signature_files,
        },
    )
    return {
        "schema": SCHEMA,
        "target": {
            "template_apk": str(template_apk),
            "android_www_dir": str(android_www_dir),
            "output_apk": str(output_apk),
            "asset_prefix": prefix,
        },
        "summary": {
            "overall": "PASS",
            "added_webview_files": len(android_files),
            "removed_template_webview_files": removed_template_webview_files,
            "removed_signature_files": removed_signature_files,
        },
        "results": [input_result.__dict__, package_result.__dict__],
    }


def _tool(path: Path, *args: str) -> list[str]:
    if path.suffix.lower() in {".bat", ".cmd"}:
        return ["cmd.exe", "/c", str(path), *args]
    return [str(path), *args]


def redact_command(cmd: Sequence[str], secrets: Sequence[str]) -> list[str]:
    redacted: list[str] = []
    secret_values = {secret for secret in secrets if secret}
    for item in cmd:
        if item in secret_values:
            redacted.append("<redacted>")
        elif item.startswith("pass:") and item[5:] in secret_values:
            redacted.append("pass:<redacted>")
        else:
            redacted.append(item)
    return redacted


def _run(cmd: Sequence[str], *, java_home: Path | None = None, redact_values: Sequence[str] = ()) -> dict[str, Any]:
    env = os.environ.copy()
    if java_home:
        env["JAVA_HOME"] = str(java_home)
        env["PATH"] = f"{java_home / 'bin'}{os.pathsep}{env.get('PATH', '')}"
    completed = subprocess.run(cmd, text=True, capture_output=True, env=env)
    return {
        "command": redact_command(cmd, redact_values),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _ensure_debug_keystore(
    *,
    keytool: Path,
    keystore: Path,
    alias: str,
    password: str,
    java_home: Path,
) -> dict[str, Any]:
    if keystore.is_file():
        return {
            "status": "PASS",
            "created": False,
            "keystore": str(keystore),
            "command": None,
            "returncode": 0,
        }
    keystore.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(keytool),
        "-genkeypair",
        "-keystore",
        str(keystore),
        "-storepass",
        password,
        "-keypass",
        password,
        "-alias",
        alias,
        "-keyalg",
        "RSA",
        "-keysize",
        "2048",
        "-validity",
        "10000",
        "-dname",
        "CN=Android Debug,O=Android,C=US",
        "-noprompt",
    ]
    result = _run(command, java_home=java_home)
    result["command"] = redact_command(command, [password])
    result["status"] = "PASS" if result["returncode"] == 0 and keystore.is_file() else "FAIL"
    result["created"] = result["status"] == "PASS"
    result["keystore"] = str(keystore)
    return result


def package_signed_apk(
    *,
    template_apk: Path,
    android_www_dir: Path,
    output_apk: Path,
    java_home: Path,
    build_tools_dir: Path,
    keystore: Path = DEFAULT_KEYSTORE,
    alias: str = DEFAULT_KEY_ALIAS,
    password: str = DEFAULT_KEY_PASSWORD,
    asset_prefix: str = DEFAULT_ASSET_PREFIX,
) -> dict[str, Any]:
    output_apk = Path(output_apk)
    unsigned_apk = output_apk.with_name(f"{output_apk.stem}-unsigned.apk")
    aligned_apk = output_apk.with_name(f"{output_apk.stem}-aligned.apk")
    package_report = replace_webview_assets(
        template_apk=template_apk,
        android_www_dir=android_www_dir,
        output_apk=unsigned_apk,
        asset_prefix=asset_prefix,
    )
    if package_report["summary"]["overall"] != "PASS":
        return {
            "schema": SCHEMA,
            "summary": {"overall": "FAIL"},
            "package": package_report,
            "signing": {},
        }

    keytool = Path(java_home) / "bin" / ("keytool.exe" if os.name == "nt" else "keytool")
    zipalign = Path(build_tools_dir) / ("zipalign.exe" if os.name == "nt" else "zipalign")
    apksigner = Path(build_tools_dir) / ("apksigner.bat" if os.name == "nt" else "apksigner")
    tool_result = _result(
        "APK-PACKAGE-TOOLCHAIN",
        keytool.is_file() and zipalign.is_file() and apksigner.is_file(),
        "JDK keytool, Android zipalign, and apksigner are available.",
        {
            "java_home": str(java_home),
            "build_tools_dir": str(build_tools_dir),
            "keytool": str(keytool),
            "keytool_exists": keytool.is_file(),
            "zipalign": str(zipalign),
            "zipalign_exists": zipalign.is_file(),
            "apksigner": str(apksigner),
            "apksigner_exists": apksigner.is_file(),
        },
    )
    if tool_result.status == "FAIL":
        return {
            "schema": SCHEMA,
            "summary": {"overall": "FAIL"},
            "package": package_report,
            "signing": {"toolchain": tool_result.__dict__},
        }

    keystore_result = _ensure_debug_keystore(
        keytool=keytool,
        keystore=Path(keystore),
        alias=alias,
        password=password,
        java_home=Path(java_home),
    )
    zipalign_result = _run([str(zipalign), "-f", "-p", "4", str(unsigned_apk), str(aligned_apk)], java_home=Path(java_home))
    sign_result = {"returncode": 1, "stdout": "", "stderr": "zipalign did not pass"}
    verify_result = {"returncode": 1, "stdout": "", "stderr": "signing did not pass"}
    if keystore_result.get("status") == "PASS" and zipalign_result["returncode"] == 0:
        sign_result = _run(
            _tool(
                apksigner,
                "sign",
                "--ks",
                str(keystore),
                "--ks-pass",
                f"pass:{password}",
                "--key-pass",
                f"pass:{password}",
                "--ks-key-alias",
                alias,
                "--out",
                str(output_apk),
                str(aligned_apk),
            ),
            java_home=Path(java_home),
            redact_values=[password],
        )
    if sign_result["returncode"] == 0:
        verify_result = _run(_tool(apksigner, "verify", "--verbose", str(output_apk)), java_home=Path(java_home))

    webview_verification: dict[str, Any] = {}
    if output_apk.is_file():
        try:
            from verify_rehab_mobile_apk_webview_assets import verify_apk_webview_assets

            webview_verification = verify_apk_webview_assets(output_apk, android_www_dir, asset_prefix)
        except Exception as exc:  # pragma: no cover - defensive reporting for CLI use.
            webview_verification = {"summary": {"overall": "FAIL"}, "error": str(exc)}

    overall_ok = (
        keystore_result.get("status") == "PASS"
        and zipalign_result["returncode"] == 0
        and sign_result["returncode"] == 0
        and verify_result["returncode"] == 0
        and webview_verification.get("summary", {}).get("overall") == "PASS"
    )
    return {
        "schema": SCHEMA,
        "summary": {
            "overall": "PASS" if overall_ok else "FAIL",
            "output_apk": str(output_apk),
            "unsigned_apk": str(unsigned_apk),
            "aligned_apk": str(aligned_apk),
        },
        "package": package_report,
        "signing": {
            "toolchain": tool_result.__dict__,
            "keystore": keystore_result,
            "zipalign": zipalign_result,
            "sign": sign_result,
            "verify": verify_result,
        },
        "webview_verification": webview_verification,
    }


def _emit_json(payload: dict[str, Any], stdout: Any = sys.stdout) -> None:
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    buffer = getattr(stdout, "buffer", None)
    if buffer is not None:
        buffer.write(rendered.encode("utf-8"))
    else:
        stdout.write(rendered)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-apk", type=Path, required=True)
    parser.add_argument("--android-www-dir", type=Path, required=True)
    parser.add_argument("--output-apk", type=Path, required=True)
    parser.add_argument("--asset-prefix", default=DEFAULT_ASSET_PREFIX)
    parser.add_argument("--java-home", type=Path, required=True)
    parser.add_argument("--build-tools-dir", type=Path, required=True)
    parser.add_argument("--keystore", type=Path, default=DEFAULT_KEYSTORE)
    parser.add_argument("--key-alias", default=DEFAULT_KEY_ALIAS)
    parser.add_argument("--key-password", default=DEFAULT_KEY_PASSWORD)
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = package_signed_apk(
        template_apk=args.template_apk,
        android_www_dir=args.android_www_dir,
        output_apk=args.output_apk,
        java_home=args.java_home,
        build_tools_dir=args.build_tools_dir,
        keystore=args.keystore,
        alias=args.key_alias,
        password=args.key_password,
        asset_prefix=args.asset_prefix,
    )
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    _emit_json(payload)
    return 0 if payload["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
