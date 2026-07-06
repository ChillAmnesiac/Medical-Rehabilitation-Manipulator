#!/usr/bin/env python3
"""Smoke-test a rehab phone SMS webhook before enabling it in staging."""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable


UrlOpener = Callable[..., Any]


def require_text(name: str, value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def mask_phone(phone: str) -> str:
    text = require_text("phone", phone)
    if len(text) <= 8:
        return "***"
    return f"{text[:4]}****{text[-4:]}"


def build_sms_payload(
    *,
    phone: str,
    code: str,
    purpose: str,
    verification_id: str,
    expires_in: int,
) -> dict[str, Any]:
    return {
        "phone": require_text("phone", phone),
        "code": require_text("code", code),
        "purpose": require_text("purpose", purpose),
        "verification_id": require_text("verification_id", verification_id),
        "expires_in": int(expires_in),
    }


def summarize_request(
    *,
    provider: str,
    webhook_url: str,
    webhook_token: str | None,
    phone: str,
    code: str,
    purpose: str,
    verification_id: str,
    expires_in: int,
) -> dict[str, Any]:
    return {
        "provider": require_text("provider", provider),
        "webhook_url": require_text("webhook_url", webhook_url),
        "webhook_token": "<redacted>" if webhook_token else None,
        "phone": mask_phone(phone),
        "code": "<redacted>" if code else None,
        "purpose": purpose,
        "verification_id": verification_id,
        "expires_in": int(expires_in),
    }


def parse_body(raw: bytes) -> Any:
    text = raw.decode("utf-8", errors="replace")
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def post_sms_webhook(
    webhook_url: str,
    webhook_token: str | None,
    payload: dict[str, Any],
    timeout: int,
    opener: UrlOpener,
) -> tuple[int, Any]:
    headers = {"Content-Type": "application/json; charset=utf-8"}
    token = (webhook_token or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(require_text("webhook_url", webhook_url), data=body, headers=headers, method="POST")
    try:
        with opener(request, timeout=timeout) as response:
            return response.status, parse_body(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, parse_body(exc.read() if exc.fp else b"")
    except (urllib.error.URLError, TimeoutError):
        return 0, None


def run(args: argparse.Namespace, opener: UrlOpener = urllib.request.urlopen) -> tuple[int, dict[str, Any]]:
    provider = require_text("provider", args.provider)
    webhook_url = require_text("webhook_url", args.webhook_url)
    code = require_text("code", args.code)
    payload = build_sms_payload(
        phone=args.phone,
        code=code,
        purpose=args.purpose,
        verification_id=args.verification_id,
        expires_in=args.expires_in,
    )
    status_code, body = post_sms_webhook(webhook_url, args.webhook_token, payload, int(args.timeout), opener)
    ok = 200 <= status_code < 300
    if ok:
        status = "ok"
    elif status_code >= 400:
        status = "provider_http_error"
    else:
        status = "provider_unavailable"
    summary = {
        "request": summarize_request(
            provider=provider,
            webhook_url=webhook_url,
            webhook_token=args.webhook_token,
            phone=args.phone,
            code=code,
            purpose=args.purpose,
            verification_id=args.verification_id,
            expires_in=args.expires_in,
        ),
        "status_code": status_code,
        "status": status,
        "delivery_accepted": ok,
        "response_type": type(body).__name__ if body is not None else None,
    }
    return (0 if ok else 3), summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", default=os.getenv("REHAB_SMS_PROVIDER", "webhook"))
    parser.add_argument("--webhook-url", default=os.getenv("REHAB_SMS_WEBHOOK_URL"))
    parser.add_argument("--webhook-token", default=os.getenv("REHAB_SMS_WEBHOOK_TOKEN"))
    parser.add_argument("--phone", default=os.getenv("REHAB_SMS_SMOKE_PHONE"))
    parser.add_argument("--code", default=os.getenv("REHAB_SMS_SMOKE_CODE"))
    parser.add_argument("--purpose", default=os.getenv("REHAB_SMS_SMOKE_PURPOSE", "bind_account"))
    parser.add_argument("--verification-id", default=os.getenv("REHAB_SMS_SMOKE_VERIFICATION_ID", "sms-provider-smoke"))
    parser.add_argument("--expires-in", type=int, default=int(os.getenv("REHAB_SMS_SMOKE_EXPIRES_IN", "300")))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        exit_code, summary = run(parse_args(argv))
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
