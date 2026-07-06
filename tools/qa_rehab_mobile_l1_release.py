#!/usr/bin/env python3
"""Combined L1 release gate for the rehab mobile app.

The app reaches L1 only when both backend/API/APK smoke and frontend patient
screen gates pass. Current pre-Stitch frontend builds are expected to fail this
script even when the backend smoke is green.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qa_rehab_mobile_acceptance  # noqa: E402
import qa_rehab_mobile_l1_frontend  # noqa: E402
import verify_rehab_mobile_apk_webview_assets  # noqa: E402


L1_REQUIRED_API_GATES = {
    "P1-AGENT-CONFIG-001": "agent_cloud_model",
    "P1-AGENT-MODEL-001": "agent_cloud_model",
}


def api_gate_status(api_payload: dict[str, Any], gate: str) -> str | None:
    for result in api_payload.get("results") or []:
        if isinstance(result, dict) and result.get("gate") == gate:
            status = result.get("status")
            return status if isinstance(status, str) else None
    return None


def summarize_release(
    api_payload: dict[str, Any],
    frontend_payload: dict[str, Any],
    apk_webview_payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    api_summary = api_payload.get("summary") or {}
    frontend_summary = frontend_payload.get("summary") or {}
    apk_webview_summary = apk_webview_payload.get("summary") if isinstance(apk_webview_payload, dict) else None
    apk_webview_summary = apk_webview_summary if isinstance(apk_webview_summary, dict) else {}
    api_ok = api_summary.get("overall") == "PASS" and api_summary.get("p0_failed") == 0
    frontend_ok = frontend_summary.get("overall") == "PASS" and frontend_summary.get("failed") == 0
    apk_webview_ok = apk_webview_summary.get("overall") == "PASS" and apk_webview_summary.get("failed") == 0
    blocking_gates: list[str] = []
    if not api_ok:
        blocking_gates.append("api_smoke")
    if not frontend_ok:
        blocking_gates.append("frontend_l1_gate")
    if not apk_webview_ok:
        blocking_gates.append("apk_webview_assets")
    for gate, blocker in L1_REQUIRED_API_GATES.items():
        if api_gate_status(api_payload, gate) != "PASS" and blocker not in blocking_gates:
            blocking_gates.append(blocker)
    payload = {
        "summary": {
            "overall": "PASS" if not blocking_gates else "FAIL",
            "api_overall": api_summary.get("overall"),
            "api_p0_failed": api_summary.get("p0_failed"),
            "frontend_overall": frontend_summary.get("overall"),
            "frontend_failed": frontend_summary.get("failed"),
            "apk_webview_assets_overall": apk_webview_summary.get("overall"),
            "apk_webview_assets_failed": apk_webview_summary.get("failed"),
            "blocking_gates": blocking_gates,
        },
        "api": api_payload,
        "frontend": frontend_payload,
        "apk_webview_assets": apk_webview_payload,
    }
    return (1 if blocking_gates else 0), payload


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    api_args = qa_rehab_mobile_acceptance.parse_args(
        [
            "--api-base",
            args.api_base,
            "--web-base",
            args.web_base,
            "--web-origin",
            args.web_origin,
            "--apk-url",
            args.apk_url,
            "--timeout",
            str(args.timeout),
        ]
        + (["--email", args.email] if args.email else [])
        + (["--password", args.password] if args.password else [])
    )
    _, api_payload = qa_rehab_mobile_acceptance.run(api_args)
    frontend_args = qa_rehab_mobile_l1_frontend.parse_args(
        [
            "--web-base",
            args.web_base,
            "--timeout",
            str(args.timeout),
        ]
    )
    _, frontend_payload = qa_rehab_mobile_l1_frontend.run(frontend_args)
    apk_webview_payload = verify_rehab_mobile_apk_webview_assets.verify_apk_webview_assets(
        args.apk_file,
        args.android_www_dir,
        args.apk_asset_prefix,
    )
    return summarize_release(api_payload, frontend_payload, apk_webview_payload)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", default=os.getenv("REHAB_QA_API_BASE", "http://106.55.62.122:8011"))
    parser.add_argument("--web-base", default=os.getenv("REHAB_QA_WEB_BASE", "http://106.55.62.122:3001/rehab-arm-mobile"))
    parser.add_argument("--web-origin", default=os.getenv("REHAB_QA_WEB_ORIGIN", "http://106.55.62.122:3001"))
    parser.add_argument(
        "--apk-url",
        default=os.getenv(
            "REHAB_QA_APK_URL",
            "http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk",
        ),
    )
    parser.add_argument("--email", default=os.getenv("REHAB_QA_EMAIL"))
    parser.add_argument("--password", default=os.getenv("REHAB_QA_PASSWORD"))
    parser.add_argument(
        "--apk-file",
        type=Path,
        default=Path(os.getenv("REHAB_QA_APK_FILE", "apps/web/public/downloads/rehab-arm/lingdong-rehab-arm-debug.apk")),
    )
    parser.add_argument(
        "--android-www-dir",
        type=Path,
        default=Path(os.getenv("REHAB_QA_ANDROID_WWW_DIR", "apps/mobile/rehab-arm-android/www")),
    )
    parser.add_argument("--apk-asset-prefix", default=os.getenv("REHAB_QA_APK_ASSET_PREFIX", "assets/public"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    exit_code, payload = run(parse_args(argv))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
