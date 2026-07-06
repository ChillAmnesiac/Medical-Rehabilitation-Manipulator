#!/usr/bin/env python3
"""Export a machine-readable L1 evidence snapshot for rehab mobile."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import export_rehab_mobile_stitch_repair_packet  # noqa: E402
import qa_rehab_mobile_l1_objective_audit  # noqa: E402
import qa_rehab_mobile_l1_release  # noqa: E402


DEFAULT_API_BASE = "http://106.55.62.122:8011"
DEFAULT_WEB_BASE = "http://106.55.62.122:3001/rehab-arm-mobile"
DEFAULT_WEB_ORIGIN = "http://106.55.62.122:3001"
DEFAULT_APK_URL = "http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk"
DEFAULT_APK_FILE = Path(
    "artifacts/external/rehab-arm-mobile-stitch/apps/web/public/downloads/rehab-arm/lingdong-rehab-arm-debug.apk"
)
DEFAULT_ANDROID_WWW_DIR = Path("artifacts/external/rehab-arm-mobile-stitch/apps/mobile/rehab-arm-android/www")
DEFAULT_APK_ASSET_PREFIX = "assets/public"
DEFAULT_OUTPUT = Path("artifacts/rehab-mobile-l1-evidence/rehab-mobile-l1-evidence.json")

ReleaseRunner = Callable[[argparse.Namespace], tuple[int, dict[str, Any]]]
ObjectiveRunner = Callable[[dict[str, Any], Path], dict[str, Any]]
HealthGetter = Callable[[str, int], dict[str, Any]]
ApkHeadGetter = Callable[[str, int], dict[str, Any]]
GitGetter = Callable[[], dict[str, Any]]


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text = raw.decode("utf-16")
    elif raw.startswith(b"\xef\xbb\xbf"):
        text = raw.decode("utf-8-sig")
    else:
        text = raw.decode("utf-8")
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _display_path(path: Path) -> str:
    return path.as_posix()


def _json_response(url: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            body: Any = None
            if raw:
                try:
                    body = json.loads(raw)
                except json.JSONDecodeError:
                    body = raw
            return {
                "url": url,
                "status": response.status,
                "body": body,
                "headers": dict(response.headers.items()),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = raw
        return {
            "url": url,
            "status": exc.code,
            "body": body,
            "headers": dict(exc.headers.items()),
            "error": "http_error",
        }
    except urllib.error.URLError as exc:
        return {"url": url, "status": None, "body": None, "headers": {}, "error": str(exc.reason)}


def fetch_health(api_base: str, timeout: int) -> dict[str, Any]:
    return _json_response(f"{api_base.rstrip('/')}/health", timeout)


def _parse_content_length(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def head_apk(url: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            headers = dict(response.headers.items())
            return {
                "url": url,
                "status": response.status,
                "content_length": _parse_content_length(response.headers.get("Content-Length")),
                "content_type": response.headers.get("Content-Type"),
                "headers": headers,
            }
    except urllib.error.HTTPError as exc:
        return {
            "url": url,
            "status": exc.code,
            "content_length": _parse_content_length(exc.headers.get("Content-Length")),
            "content_type": exc.headers.get("Content-Type"),
            "headers": dict(exc.headers.items()),
            "error": "http_error",
        }
    except urllib.error.URLError as exc:
        return {
            "url": url,
            "status": None,
            "content_length": None,
            "content_type": None,
            "headers": {},
            "error": str(exc.reason),
        }


def _git(args: list[str]) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=Path.cwd(),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_info() -> dict[str, Any]:
    status = _git(["status", "--short"]) or ""
    return {
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "head": _git(["rev-parse", "HEAD"]),
        "head_short": _git(["rev-parse", "--short", "HEAD"]),
        "dirty": bool(status),
        "status_short": status.splitlines(),
    }


def _run_release_gate(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if args.release_json:
        payload = _load_json(args.release_json)
        return (0 if (payload.get("summary") or {}).get("overall") == "PASS" else 1), payload
    release_args = qa_rehab_mobile_l1_release.parse_args(
        [
            "--api-base",
            args.api_base,
            "--web-base",
            args.web_base,
            "--web-origin",
            args.web_origin,
            "--apk-url",
            args.apk_url,
            "--apk-file",
            str(args.apk_file),
            "--android-www-dir",
            str(args.android_www_dir),
            "--apk-asset-prefix",
            args.apk_asset_prefix,
            "--timeout",
            str(args.timeout),
        ]
        + (["--email", args.email] if args.email else [])
        + (["--password", args.password] if args.password else [])
    )
    return qa_rehab_mobile_l1_release.run(release_args)


def _run_objective_audit(args: argparse.Namespace, release_payload: dict[str, Any]) -> dict[str, Any]:
    if args.objective_json:
        return _load_json(args.objective_json)
    return qa_rehab_mobile_l1_objective_audit.audit_objective(
        release_payload,
        args.screenshots_dir,
        args.browser_metrics_json,
    )


def _browser_evidence(objective_payload: dict[str, Any]) -> dict[str, Any]:
    for item in objective_payload.get("requirements") or []:
        if isinstance(item, dict) and item.get("requirement") == "browser_qa_evidence":
            evidence = item.get("evidence")
            return evidence if isinstance(evidence, dict) else {}
    return {}


def _required_artifacts() -> dict[str, str]:
    artifacts = dict(export_rehab_mobile_stitch_repair_packet.DEFAULT_REQUIRED_ARTIFACTS)
    artifacts.update(
        {
            "l1_evidence_exporter": "tools/export_rehab_mobile_l1_evidence.py",
            "l1_evidence_default_output": str(DEFAULT_OUTPUT),
        }
    )
    return artifacts


def _summary(
    release_payload: dict[str, Any],
    objective_payload: dict[str, Any],
    health: dict[str, Any],
    apk_head: dict[str, Any],
) -> dict[str, Any]:
    release_summary = release_payload.get("summary") or {}
    objective_summary = objective_payload.get("summary") or {}
    health_ok = health.get("status") == 200
    apk_ok = apk_head.get("status") == 200 and (apk_head.get("content_length") or 0) > 1_000_000
    release_ok = release_summary.get("overall") == "PASS" and not release_summary.get("blocking_gates")
    objective_ok = objective_summary.get("overall") == "PASS" and not objective_summary.get("blocking_requirements")
    return {
        "overall": "PASS" if release_ok and objective_ok and health_ok and apk_ok else "FAIL",
        "release_overall": release_summary.get("overall"),
        "objective_overall": objective_summary.get("overall"),
        "apk_webview_assets_overall": release_summary.get("apk_webview_assets_overall"),
        "apk_webview_assets_failed": release_summary.get("apk_webview_assets_failed"),
        "health_ok": health_ok,
        "apk_ok": apk_ok,
        "release_blocking_gates": release_summary.get("blocking_gates") or [],
        "objective_blocking_requirements": objective_summary.get("blocking_requirements") or [],
    }


def build_evidence(
    args: argparse.Namespace,
    *,
    generated_at: str | None = None,
    release_runner: ReleaseRunner | None = None,
    objective_runner: ObjectiveRunner | None = None,
    health_getter: HealthGetter | None = None,
    apk_head_getter: ApkHeadGetter | None = None,
    git_getter: GitGetter | None = None,
) -> dict[str, Any]:
    active_release_runner = release_runner or _run_release_gate
    active_health_getter = health_getter or fetch_health
    active_apk_head_getter = apk_head_getter or head_apk
    active_git_getter = git_getter or git_info

    release_exit_code, release_payload = active_release_runner(args)
    objective_payload = (
        objective_runner(release_payload, args.screenshots_dir)
        if objective_runner
        else _run_objective_audit(args, release_payload)
    )
    health = active_health_getter(args.api_base, args.timeout)
    apk_head_payload = active_apk_head_getter(args.apk_url, args.timeout)
    return {
        "schema": "rehab-mobile-l1-evidence/v1",
        "generated_at": generated_at or _utc_now(),
        "target": {
            "api_base": args.api_base,
            "web_base": args.web_base,
            "web_origin": args.web_origin,
            "apk_url": args.apk_url,
            "apk_file": _display_path(args.apk_file),
            "android_www_dir": _display_path(args.android_www_dir),
            "apk_asset_prefix": args.apk_asset_prefix,
            "screenshots_dir": _display_path(args.screenshots_dir),
            "browser_metrics_json": _display_path(args.browser_metrics_json),
        },
        "summary": _summary(release_payload, objective_payload, health, apk_head_payload),
        "git": active_git_getter(),
        "health": health,
        "apk_head": apk_head_payload,
        "release": {"exit_code": release_exit_code, "summary": release_payload.get("summary") or {}, "payload": release_payload},
        "objective": {"summary": objective_payload.get("summary") or {}, "payload": objective_payload},
        "browser_evidence": _browser_evidence(objective_payload),
        "required_artifacts": _required_artifacts(),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-json", type=Path)
    parser.add_argument("--objective-json", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at")
    parser.add_argument("--fail-on-l1-fail", action="store_true")
    parser.add_argument("--screenshots-dir", type=Path, default=Path("docs/qa/rehab-mobile-20260706/screenshots"))
    parser.add_argument(
        "--browser-metrics-json",
        type=Path,
        default=qa_rehab_mobile_l1_objective_audit.DEFAULT_BROWSER_METRICS_JSON,
    )
    parser.add_argument("--api-base", default=os.getenv("REHAB_QA_API_BASE", DEFAULT_API_BASE))
    parser.add_argument("--web-base", default=os.getenv("REHAB_QA_WEB_BASE", DEFAULT_WEB_BASE))
    parser.add_argument("--web-origin", default=os.getenv("REHAB_QA_WEB_ORIGIN", DEFAULT_WEB_ORIGIN))
    parser.add_argument("--apk-url", default=os.getenv("REHAB_QA_APK_URL", DEFAULT_APK_URL))
    parser.add_argument("--apk-file", type=Path, default=Path(os.getenv("REHAB_QA_APK_FILE", str(DEFAULT_APK_FILE))))
    parser.add_argument(
        "--android-www-dir",
        type=Path,
        default=Path(os.getenv("REHAB_QA_ANDROID_WWW_DIR", str(DEFAULT_ANDROID_WWW_DIR))),
    )
    parser.add_argument("--apk-asset-prefix", default=os.getenv("REHAB_QA_APK_ASSET_PREFIX", DEFAULT_APK_ASSET_PREFIX))
    parser.add_argument("--email", default=os.getenv("REHAB_QA_EMAIL"))
    parser.add_argument("--password", default=os.getenv("REHAB_QA_PASSWORD"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    evidence = build_evidence(args, generated_at=args.generated_at)
    rendered = json.dumps(evidence, ensure_ascii=False, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(str(args.output))
    if args.fail_on_l1_fail and evidence["summary"]["overall"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
