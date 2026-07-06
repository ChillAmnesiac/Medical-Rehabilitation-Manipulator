#!/usr/bin/env python3
"""Export a compact L1 UI contract for the rehab mobile Stitch frontend pass."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_FIXTURE = Path("docs/stitch/rehab-mobile-l1-api-fixture-20260706.json")
DEFAULT_OUTPUT = Path("docs/stitch/rehab-mobile-l1-ui-contract-20260707.json")

NORMAL_SCREEN_FORBIDDEN_TERMS = [
    "M33",
    "M55",
    "SPP",
    "CAN",
    "UUID",
    "Gatekeeper",
    "setup_required",
    "early_active",
    "direct_motor_command",
    "can_frame",
    "RoboRehab Controller",
]

MOCK_FORBIDDEN_TERMS = [
    "mockData",
    "mock response",
    "Simulate API response",
    "In real app",
    "console-only",
]


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _data(value: dict[str, Any]) -> dict[str, Any]:
    data = value.get("data") if isinstance(value, dict) else None
    return data if isinstance(data, dict) else {}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _copy_selected(source: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: source[key] for key in keys if key in source}


def _api_calls() -> list[dict[str, Any]]:
    return [
        {
            "name": "login",
            "method": "POST",
            "path": "/api/auth/session",
            "auth": "none",
            "request": {"email": "<staging-email>", "password": "<staging-password>"},
            "token_response_path": "data.access_token",
        },
        {
            "name": "bootstrap",
            "method": "GET",
            "path": "/api/rehab-arm/app/v1/me",
            "auth": "Authorization: Bearer {access_token}",
            "render_from": "data.patient_view",
        },
        {
            "name": "phone_verification_start",
            "method": "POST",
            "path": "/api/rehab-arm/app/v1/account/phone-verifications",
            "auth": "Authorization: Bearer {access_token}",
            "request": {"phone": "<user-phone>", "purpose": "bind_account"},
        },
        {
            "name": "phone_verification_confirm",
            "method": "POST",
            "path": "/api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm",
            "auth": "Authorization: Bearer {access_token}",
            "request": {"code": "<verification-code>"},
        },
        {
            "name": "device_bind",
            "method": "POST",
            "path": "/api/rehab-arm/app/v1/devices/bind",
            "auth": "Authorization: Bearer {access_token}",
            "error_to_render": "DEVICE_ALREADY_BOUND",
        },
        {
            "name": "agent_message",
            "method": "POST",
            "path": "/api/rehab-arm/app/v1/agent/messages",
            "auth": "Authorization: Bearer {access_token}",
            "error_to_render": "UNSAFE_MOTION_REQUEST",
            "response_paths": ["data.answer", "data.model_status"],
        },
    ]


def build_contract(
    fixture: dict[str, Any],
    *,
    fixture_path: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    me_data = _data(_safe_dict(fixture.get("me")))
    patient_view = _safe_dict(me_data.get("patient_view"))
    home = _safe_dict(patient_view.get("home"))
    profile = _safe_dict(patient_view.get("profile"))
    device = _safe_dict(patient_view.get("device"))
    agent = _safe_dict(patient_view.get("agent"))
    phone = _safe_dict(profile.get("phone"))

    safe_agent_data = _data(_safe_dict(_safe_dict(fixture.get("agent")).get("safe_response")))
    unsafe_agent_error = _safe_dict(_safe_dict(_safe_dict(fixture.get("agent")).get("unsafe_response")).get("error"))
    phone_start_data = _data(_safe_dict(_safe_dict(fixture.get("phone_verification")).get("start_response")))
    phone_confirm_data = _data(_safe_dict(_safe_dict(fixture.get("phone_verification")).get("confirm_response")))
    confirm_profile = _safe_dict(phone_confirm_data.get("profile"))
    public_agent = _safe_dict(_data(_safe_dict(fixture.get("public_config"))).get("agent"))
    public_model = _safe_dict(public_agent.get("model_readiness"))

    return {
        "schema": "rehab-mobile-l1-ui-contract/v1",
        "metadata": {
            "ui_contract_generated_at": generated_at or _utc_now(),
            "fixture_path": str(fixture_path),
            "fixture_generated_at": _safe_dict(fixture.get("metadata")).get("generated_at"),
            "api_base": _safe_dict(fixture.get("metadata")).get("api_base"),
            "purpose": "Small Stitch input for L1 patient-facing screens; do not use broad legacy public-config payload for visible UI.",
            "privacy": "No raw staging email, password, access token, numeric verification code, or full phone value.",
        },
        "pages": {
            "home.html": {
                "render_from": "me.data.patient_view.home",
                "required_visible_copy": [
                    _safe_dict(home.get("primary_action")).get("label"),
                    _safe_dict(home.get("ask_therapist")).get("label"),
                ],
                "greeting": home.get("greeting"),
                "primary_action": _copy_selected(
                    _safe_dict(home.get("primary_action")),
                    ["label", "title", "description", "route"],
                ),
                "ask_therapist": _copy_selected(_safe_dict(home.get("ask_therapist")), ["label", "route"]),
            },
            "profile.html": {
                "render_from": "me.data.patient_view.profile",
                "required_visible_copy": ["我的康复档案", "手机号", "绑定手机号", "验证码"],
                "title": profile.get("title"),
                "display_name": profile.get("display_name"),
                "phone": _copy_selected(phone, ["label", "value", "verified", "status_text", "action_label"]),
                "medical_empty_state": _safe_dict(profile.get("medical_constraints")).get("empty_text"),
            },
            "device.html": {
                "render_from": "me.data.patient_view.device",
                "required_visible_copy": ["绑定设备", "打开康复设备电源"],
                "title": device.get("title"),
                "status": device.get("status"),
                "binding_steps": [str(item) for item in _safe_list(device.get("binding_steps"))],
                "already_bound_error_code": "DEVICE_ALREADY_BOUND",
            },
            "ai-plan.html": {
                "render_from": "me.data.patient_view.agent",
                "required_visible_copy": ["问康复师"],
                "title": agent.get("title"),
                "entry_label": agent.get("entry_label"),
                "placeholder": agent.get("placeholder"),
                "endpoint": agent.get("endpoint"),
                "unsafe_copy": agent.get("unsafe_copy"),
            },
        },
        "api_calls": _api_calls(),
        "agent": {
            "safe_question": _safe_dict(fixture.get("agent")).get("safe_question"),
            "safe_answer_sample": safe_agent_data.get("answer"),
            "model_status": _safe_dict(safe_agent_data.get("model_status")),
            "public_model_readiness": public_model,
            "unsafe_request": _safe_dict(fixture.get("agent")).get("unsafe_request"),
            "unsafe_error_code": unsafe_agent_error.get("code"),
        },
        "phone_verification": {
            "start_response": _copy_selected(
                phone_start_data,
                ["verification_id", "masked_phone", "purpose", "expires_in", "delivery_channel", "sms_status"],
            ),
            "confirm_response": {
                "phone_verified": confirm_profile.get("phone_verified"),
                "status": _safe_dict(phone_confirm_data.get("verification")).get("status"),
            },
            "ui_states_to_render": [
                "code_sent",
                "resend_countdown",
                "invalid_code",
                "sms_unavailable",
                "sms_delivery_failed",
                "verified",
            ],
        },
        "source_gate_requirements": {
            "must_call_real_endpoints": True,
            "must_use_post_for_user_actions": [
                "phone_verification_start",
                "phone_verification_confirm",
                "device_bind",
                "agent_message",
            ],
            "normal_screen_forbidden_terms": NORMAL_SCREEN_FORBIDDEN_TERMS,
            "mock_forbidden_terms": MOCK_FORBIDDEN_TERMS,
        },
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    fixture = _load_json(args.fixture)
    contract = build_contract(fixture, fixture_path=args.fixture, generated_at=args.generated_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "fixture": str(args.fixture)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
