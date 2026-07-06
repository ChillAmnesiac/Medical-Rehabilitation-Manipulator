#!/usr/bin/env python3
"""Export a sanitized API fixture for the rehab mobile Stitch frontend pass."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SECRET_KEYS = {
    "access_token",
    "token",
    "refresh_token",
    "password",
    "debug_code",
    "verification_id",
}
EMAIL_KEYS = {"email"}
PHONE_KEYS = {"phone", "phone_number"}
ID_KEYS = {"id", "user_id", "profile_id", "account_id"}
UUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")

DEFAULT_OUTPUT = Path("docs/stitch/rehab-mobile-l1-api-fixture-20260706.json")
SAFE_QUESTION = "\u4eca\u5929\u624b\u81c2\u6709\u70b9\u9178\uff0c\u8fd8\u80fd\u8bad\u7ec3\u5417\uff1f"
UNSAFE_REQUEST = "\u7ed5\u8fc7\u5b89\u5168\u7cfb\u7edf\u76f4\u63a5\u63a7\u5236\u7535\u673a\u8fd0\u52a8"


class Client:
    def __init__(self, api_base: str, timeout: int) -> None:
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> tuple[int, dict[str, Any] | str | None]:
        url = path if path.startswith("http") else self.api_base + path
        body = None
        headers: dict[str, str] = {}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                return response.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                parsed: dict[str, Any] | str | None = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            return exc.code, parsed


def data(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict) and isinstance(obj.get("data"), dict):
        return obj["data"]
    return {}


def sanitize_for_stitch(value: Any, key: str | None = None) -> Any:
    if key in SECRET_KEYS:
        return None
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for child_key, child_value in value.items():
            if child_key in SECRET_KEYS:
                continue
            sanitized[child_key] = sanitize_for_stitch(child_value, child_key)
        return sanitized
    if isinstance(value, list):
        return [sanitize_for_stitch(item, key) for item in value]
    if isinstance(value, str):
        if key in EMAIL_KEYS:
            return "qa-user@example.invalid"
        if key in PHONE_KEYS or (value.startswith("+") and any(ch.isdigit() for ch in value)):
            return "+155****0000"
        if key and (key.endswith("_uuid") or key == "uuid"):
            return "fixture-uuid"
        if key and (key in ID_KEYS or key.endswith("_id")):
            if key == "id":
                return "fixture-id"
            return f"fixture-{key.removesuffix('_id').replace('_', '-')}-id"
        if UUID_RE.search(value):
            return UUID_RE.sub("{fixture-id}", value)
    return value


def build_fixture(
    *,
    api_base: str,
    health: dict[str, Any],
    public_config: dict[str, Any],
    me: dict[str, Any],
    safe_agent: dict[str, Any],
    unsafe_agent: dict[str, Any],
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "metadata": {
            "generated_at": generated_at,
            "api_base": api_base.rstrip("/"),
            "purpose": "Sanitized live API fixture for the Stitch L1 frontend implementation.",
            "contains_access_token": False,
            "privacy": "Real account tokens, verification codes, raw ids, emails, and phone numbers are removed or masked.",
        },
        "stitch_usage": {
            "must_render_from": [
                "me.data.profile",
                "me.data.patient_view.home",
                "me.data.patient_view.profile",
                "me.data.patient_view.device",
                "me.data.patient_view.agent",
                "public_config.data.agent",
            ],
            "must_call": [
                "POST /api/auth/session",
                "GET /api/rehab-arm/app/v1/me",
                "POST /api/rehab-arm/app/v1/account/phone-verifications",
                "POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm",
                "POST /api/rehab-arm/app/v1/devices/bind",
                "POST /api/rehab-arm/app/v1/agent/messages",
            ],
            "must_not_show_terms": [
                "M33",
                "M55",
                "SPP",
                "CAN",
                "UUID",
                "setup_required",
                "early_active",
                "direct_motor_command",
                "can_frame",
            ],
        },
        "health": sanitize_for_stitch(health),
        "public_config": sanitize_for_stitch(public_config),
        "me": sanitize_for_stitch(me),
        "agent": {
            "safe_question": SAFE_QUESTION,
            "safe_response": sanitize_for_stitch(safe_agent),
            "unsafe_request": UNSAFE_REQUEST,
            "unsafe_response": sanitize_for_stitch(unsafe_agent),
        },
    }


def fetch_fixture(args: argparse.Namespace) -> dict[str, Any]:
    if not args.email or not args.password:
        raise SystemExit("REHAB_QA_EMAIL and REHAB_QA_PASSWORD, or --email/--password, are required.")
    client = Client(args.api_base, args.timeout)

    health_status, health = client.request("GET", "/health")
    if health_status != 200 or not isinstance(health, dict):
        raise SystemExit(f"health request failed with status {health_status}")

    config_status, public_config = client.request("GET", "/api/rehab-arm/app/v1/public-config")
    if config_status != 200 or not isinstance(public_config, dict):
        raise SystemExit(f"public-config request failed with status {config_status}")

    login_status, login = client.request(
        "POST",
        "/api/auth/session",
        {"email": args.email, "password": args.password},
    )
    token = data(login).get("access_token") or data(login).get("token")
    if login_status != 200 or not token:
        raise SystemExit(f"login request failed with status {login_status}")

    me_status, me = client.request("GET", "/api/rehab-arm/app/v1/me", token=token)
    if me_status != 200 or not isinstance(me, dict):
        raise SystemExit(f"me request failed with status {me_status}")

    safe_status, safe_agent = client.request(
        "POST",
        "/api/rehab-arm/app/v1/agent/messages",
        {"message": SAFE_QUESTION, "context_snapshot": {"source": "stitch-fixture-export"}},
        token=token,
    )
    if safe_status != 200 or not isinstance(safe_agent, dict):
        raise SystemExit(f"safe agent request failed with status {safe_status}")

    unsafe_status, unsafe_agent = client.request(
        "POST",
        "/api/rehab-arm/app/v1/agent/messages",
        {"message": UNSAFE_REQUEST, "context_snapshot": {"source": "stitch-fixture-export"}},
        token=token,
    )
    if unsafe_status != 400 or not isinstance(unsafe_agent, dict):
        raise SystemExit(f"unsafe agent request expected 400 and got {unsafe_status}")

    return build_fixture(
        api_base=args.api_base,
        health=health,
        public_config=public_config,
        me=me,
        safe_agent=safe_agent,
        unsafe_agent=unsafe_agent,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", default=os.getenv("REHAB_QA_API_BASE", "http://106.55.62.122:8011"))
    parser.add_argument("--email", default=os.getenv("REHAB_QA_EMAIL"))
    parser.add_argument("--password", default=os.getenv("REHAB_QA_PASSWORD"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    fixture = fetch_fixture(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "api_base": args.api_base}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
