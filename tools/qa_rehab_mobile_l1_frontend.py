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
import urllib.parse
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


INTEGRATION_REQUIREMENTS = {
    "auth_session": (("/api/auth/session",),),
    "auth_bearer_header": (("Authorization", "Bearer"),),
    "auth_token_storage": (("access_token",),),
    "bootstrap_me": (("/api/rehab-arm/app/v1/me",),),
    "patient_view_home": (("patient_view", "home"), ("patientView", "home")),
    "patient_view_profile": (("patient_view", "profile"), ("patientView", "profile")),
    "patient_view_device": (("patient_view", "device"), ("patientView", "device")),
    "patient_view_agent": (("patient_view", "agent"), ("patientView", "agent")),
    "ask_therapist_accessibility": (("aria-label", "问康复师"), ("ariaLabel", "问康复师")),
    "phone_verification_start": (("/api/rehab-arm/app/v1/account/phone-verifications",),),
    "phone_verification_confirm": (("phone-verifications", "confirm"),),
    "phone_resend_cooldown": (("PHONE_CODE_RESEND_TOO_SOON", "retry_after"), ("PHONE_CODE_RESEND_TOO_SOON", "retryAfter")),
    "phone_sms_error_states": (("PHONE_SMS_NOT_CONFIGURED", "PHONE_SMS_DELIVERY_FAILED"),),
    "device_bind": (("/api/rehab-arm/app/v1/devices/bind",),),
    "device_already_bound": (("DEVICE_ALREADY_BOUND",),),
    "agent_messages": (("/api/rehab-arm/app/v1/agent/messages",),),
    "agent_unsafe_refusal": (("UNSAFE_MOTION_REQUEST",),),
    "agent_model_status": (("model_status",), ("modelStatus",)),
}

SCRIPT_SRC_RE = re.compile(r"""(?is)<script\b[^>]*\bsrc=["']([^"']+)["']""")


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


def _matches_requirement(source: str, alternatives: tuple[tuple[str, ...], ...]) -> bool:
    return any(all(token in source for token in alternative) for alternative in alternatives)


def check_frontend_integration_contract(sources: dict[str, str]) -> Result:
    combined_source = "\n".join(sources.get(path, "") for path in sorted(sources))
    missing_requirements = [
        name
        for name, alternatives in INTEGRATION_REQUIREMENTS.items()
        if not _matches_requirement(combined_source, alternatives)
    ]
    return Result(
        gate="L1-FRONTEND-INTEGRATION-001",
        level="L1",
        status="PASS" if not missing_requirements else "FAIL",
        summary="Frontend source is wired to the required auth, patient_view, phone, device, and Agent API contracts.",
        detail={
            "missing_requirements": missing_requirements,
            "checked_pages": sorted(sources),
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


def fetch_raw(url: str, timeout: int) -> tuple[int, str]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def local_script_urls(html: str, page_url: str) -> list[str]:
    page_parts = urllib.parse.urlparse(page_url)
    urls: list[str] = []
    for src in SCRIPT_SRC_RE.findall(html):
        resolved = urllib.parse.urljoin(page_url, src)
        resolved_parts = urllib.parse.urlparse(resolved)
        if resolved_parts.scheme in {"http", "https"} and resolved_parts.netloc == page_parts.netloc:
            urls.append(resolved)
    return urls


def fetch_source_bundle(page_url: str, timeout: int) -> str:
    status, html = fetch_raw(page_url, timeout)
    if status != 200:
        return html
    parts = [html]
    for script_url in local_script_urls(html, page_url):
        script_status, script_source = fetch_raw(script_url, timeout)
        if script_status == 200:
            parts.append(script_source)
    return "\n".join(parts)


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    results: list[Result] = []
    base = args.web_base.rstrip("/")
    sources: dict[str, str] = {}

    for path, config in PAGE_GATES.items():
        url = f"{base}/{path}"
        sources[path] = fetch_source_bundle(url, args.timeout)
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

    results.append(check_frontend_integration_contract(sources))

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
