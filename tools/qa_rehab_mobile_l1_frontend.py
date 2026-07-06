#!/usr/bin/env python3
"""Frontend L1 gate for the rehab mobile app.

This script checks deployed static/mobile pages for patient-facing L1 blockers
that API smoke tests cannot catch. It is intentionally strict: current
pre-Stitch frontend builds should fail until normal screens render patient_view.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from html import unescape
from typing import Any


L1_FORBIDDEN_TERMS = (
    "网络未连接",
    "setup_required",
    "early_active",
    "direct_motor_command",
    "can_frame",
    "m33_safety",
    "motion_permission",
    "M33",
    "M55",
    "SPP",
    "CAN",
    "UUID",
    "Gatekeeper",
    "动作队列",
    "阻塞",
    "禁止",
    "患者 A",
    "ID: 8829",
    "避免过度伸展",
    "RoboRehab Controller",
)


PAGE_GATES = {
    "home.html": {
        "gate": "L1-HOME-STATIC-001",
        "required_terms": ("问康复师",),
        "summary": "Home static page is patient-facing and free of raw workflow/debug terms.",
    },
    "profile.html": {
        "gate": "L1-PROFILE-STATIC-001",
        "required_terms": ("我的康复档案", "手机号", "绑定手机号", "验证码"),
        "summary": "Profile static page is cloud-account oriented and does not show demo medical data.",
    },
    "device.html": {
        "gate": "L1-DEVICE-STATIC-001",
        "required_terms": ("设备", "绑定设备", "打开康复设备电源"),
        "summary": "Device page avoids debug transport language in normal user flow.",
    },
    "ai-plan.html": {
        "gate": "L1-AGENT-STATIC-001",
        "required_terms": ("问康复师",),
        "summary": "Agent page exposes the rehab therapist entry.",
    },
}


@dataclass
class Result:
    gate: str
    level: str
    status: str
    summary: str
    detail: Any = None


def visible_text(html: str) -> str:
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return unescape(text).strip()


def check_page(
    name: str,
    text: str,
    required_terms: list[str] | tuple[str, ...],
    forbidden_terms: list[str] | tuple[str, ...],
) -> Result:
    missing_terms = [term for term in required_terms if term not in text]
    forbidden_hits = [term for term in forbidden_terms if term in text]
    ok = not missing_terms and not forbidden_hits
    return Result(
        gate=f"L1-{name.upper()}-001",
        level="L1",
        status="PASS" if ok else "FAIL",
        summary=f"{name} passes patient-facing static text gate.",
        detail={
            "missing_terms": missing_terms,
            "forbidden_hits": forbidden_hits,
        },
    )


def fetch_text(url: str, timeout: int) -> tuple[int, str, dict[str, str]]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return response.status, visible_text(raw), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, visible_text(raw), dict(exc.headers.items())


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    results: list[Result] = []
    base = args.web_base.rstrip("/")

    for path, config in PAGE_GATES.items():
        url = f"{base}/{path}"
        status, text, headers = fetch_text(url, args.timeout)
        if status != 200:
            results.append(
                Result(
                    gate=config["gate"],
                    level="L1",
                    status="FAIL",
                    summary=f"{path} is reachable.",
                    detail={"status_code": status, "url": url, "headers": headers},
                )
            )
            continue
        result = check_page(
            path.removesuffix(".html"),
            text,
            required_terms=config["required_terms"],
            forbidden_terms=L1_FORBIDDEN_TERMS,
        )
        result.gate = str(config["gate"])
        result.summary = str(config["summary"])
        result.detail = {
            **(result.detail or {}),
            "status_code": status,
            "url": url,
            "length": len(text),
            "text_prefix": text[:500],
        }
        results.append(result)

    failed = [result for result in results if result.status == "FAIL"]
    payload = {
        "summary": {
            "overall": "FAIL" if failed else "PASS",
            "failed": len(failed),
            "total": len(results),
            "web_base": base,
        },
        "results": [result.__dict__ for result in results],
    }
    return (1 if failed else 0), payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web-base", default=os.getenv("REHAB_QA_WEB_BASE", "http://106.55.62.122:3001/rehab-arm-mobile"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    exit_code, payload = run(parse_args(argv))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
