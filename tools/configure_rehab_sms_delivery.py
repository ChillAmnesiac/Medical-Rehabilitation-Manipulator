#!/usr/bin/env python3
"""Prepare rehab phone SMS delivery settings after a provider smoke passes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_ENV_FILE = Path("cloud/rehab-platform/.env")
SMS_ENV_KEYS = {
    "PHONE_VERIFICATION_DEBUG_CODE_ENABLED",
    "PHONE_VERIFICATION_SMS_PROVIDER",
    "PHONE_VERIFICATION_SMS_WEBHOOK_URL",
    "PHONE_VERIFICATION_SMS_WEBHOOK_TOKEN",
}


def require_text(name: str, value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def build_env_updates(*, provider: str, webhook_url: str, webhook_token: str | None) -> dict[str, str]:
    updates = {
        "PHONE_VERIFICATION_DEBUG_CODE_ENABLED": "false",
        "PHONE_VERIFICATION_SMS_PROVIDER": require_text("provider", provider),
        "PHONE_VERIFICATION_SMS_WEBHOOK_URL": require_text("webhook_url", webhook_url),
    }
    token = (webhook_token or "").strip()
    if token:
        updates["PHONE_VERIFICATION_SMS_WEBHOOK_TOKEN"] = token
    return updates


def summarize_env_updates(updates: dict[str, str]) -> dict[str, str]:
    return {
        key: ("<redacted>" if key.endswith("_TOKEN") and value else value)
        for key, value in updates.items()
    }


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def preflight_allows_config(
    preflight: dict[str, Any],
    *,
    provider: str,
    webhook_url: str,
) -> tuple[bool, dict[str, Any]]:
    request = preflight.get("request") if isinstance(preflight.get("request"), dict) else {}
    detail = {
        "status": preflight.get("status"),
        "delivery_accepted": preflight.get("delivery_accepted"),
        "provider": request.get("provider"),
        "webhook_url": request.get("webhook_url"),
    }
    if preflight.get("status") != "ok" or preflight.get("delivery_accepted") is not True:
        return False, {**detail, "reason": "preflight_not_ok"}
    if request.get("provider") != provider or request.get("webhook_url") != webhook_url:
        return False, {**detail, "reason": "preflight_target_mismatch"}
    return True, detail


def update_env_text(existing: str, updates: dict[str, str]) -> str:
    lines = existing.splitlines()
    rendered: list[str] = []
    seen: set[str] = set()
    for line in lines:
        stripped = line.strip()
        key = stripped.split("=", 1)[0] if "=" in stripped and not stripped.startswith("#") else None
        if key in SMS_ENV_KEYS:
            if key in updates and key not in seen:
                rendered.append(f"{key}={updates[key]}")
                seen.add(key)
            continue
        rendered.append(line)
    for key, value in updates.items():
        if key not in seen:
            rendered.append(f"{key}={value}")
    return "\n".join(rendered).rstrip() + "\n"


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    updates = build_env_updates(
        provider=args.provider,
        webhook_url=args.webhook_url,
        webhook_token=args.webhook_token,
    )
    preflight = _load_json(args.preflight_json)
    allowed, preflight_detail = preflight_allows_config(
        preflight,
        provider=updates["PHONE_VERIFICATION_SMS_PROVIDER"],
        webhook_url=updates["PHONE_VERIFICATION_SMS_WEBHOOK_URL"],
    )
    summary: dict[str, Any] = {
        "env_file": str(args.env_file),
        "mode": "execute" if args.execute else "dry_run",
        "preflight": preflight_detail,
        "updates": summarize_env_updates(updates),
    }
    if not allowed:
        summary["error"] = "sms preflight did not pass for this provider and webhook URL"
        return 2, summary
    if args.execute:
        existing = args.env_file.read_text(encoding="utf-8") if args.env_file.exists() else ""
        args.env_file.parent.mkdir(parents=True, exist_ok=True)
        args.env_file.write_text(update_env_text(existing, updates), encoding="utf-8")
        summary["written"] = True
    else:
        summary["written"] = False
    return 0, summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", default=os.getenv("REHAB_SMS_PROVIDER", "webhook"))
    parser.add_argument("--webhook-url", default=os.getenv("REHAB_SMS_WEBHOOK_URL"))
    parser.add_argument("--webhook-token", default=os.getenv("REHAB_SMS_WEBHOOK_TOKEN"))
    parser.add_argument("--preflight-json", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--execute", action="store_true")
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
