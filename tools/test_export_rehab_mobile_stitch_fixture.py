import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("export_rehab_mobile_stitch_fixture.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("export_rehab_mobile_stitch_fixture", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sanitize_for_stitch_removes_tokens_codes_and_masks_identity():
    module = _load_module()

    sanitized = module.sanitize_for_stitch(
        {
            "data": {
                "access_token": "secret-token",
                "verification_id": "verify-42",
                "debug_code": "123456",
                "profile": {
                    "id": "real-user-id",
                    "email": "3245056131@qq.com",
                    "phone": "+15550101111",
                    "name": "\u5eb7\u590d\u7528\u6237",
                },
            }
        }
    )
    text = json.dumps(sanitized, ensure_ascii=False)

    assert "secret-token" not in text
    assert "123456" not in text
    assert "3245056131@qq.com" not in text
    assert "+15550101111" not in text
    assert sanitized["data"]["verification_id"] == "fixture-verification-id"
    assert sanitized["data"]["profile"]["email"] == "qa-user@example.invalid"
    assert sanitized["data"]["profile"]["phone"] == "+155****0000"
    assert sanitized["data"]["profile"]["id"] == "fixture-id"
    assert sanitized["data"]["profile"]["name"] == "\u5eb7\u590d\u7528\u6237"


def test_build_fixture_includes_stitch_contract_sections_without_secret_values():
    module = _load_module()

    fixture = module.build_fixture(
        api_base="http://106.55.62.122:8011",
        health={
            "data": {
                "status": "ok",
                "deployment": {
                    "build_sha": "b925e316",
                    "build_ref": "codex/rehab-mobile-backend-qa-20260706",
                    "build_time": "2026-07-06T07:50:07Z",
                    "app_env": "staging",
                },
            }
        },
        public_config={
            "data": {
                "agent": {
                    "message_endpoint": "/api/rehab-arm/app/v1/agent/messages",
                    "model_readiness": {"mode": "fallback_rule_based"},
                }
            }
        },
        me={
            "data": {
                "profile": {"id": "real-user-id", "email": "3245056131@qq.com", "phone": "+15550101111"},
                "patient_view": {
                    "home": {"primary_action": {"label": "\u67e5\u770b\u5eb7\u590d\u5e08\u5efa\u8bae"}},
                    "agent": {
                        "entry_label": "\u95ee\u5eb7\u590d\u5e08",
                        "endpoint": "/api/rehab-arm/app/v1/agent/messages",
                    },
                    "device": {"binding_steps": ["\u6253\u5f00\u5eb7\u590d\u8bbe\u5907\u7535\u6e90"]},
                    "profile": {"phone": {"label": "\u624b\u673a\u53f7", "value": "+155****1111"}},
                },
            }
        },
        safe_agent={"data": {"answer": "\u5efa\u8bae\u5148\u964d\u4f4e\u5f3a\u5ea6", "model_status": {"mode": "fallback_rule_based"}}},
        unsafe_agent={"error": {"code": "UNSAFE_MOTION_REQUEST", "message": "\u4e0d\u80fd\u7ed5\u8fc7\u5b89\u5168\u673a\u5236"}},
        phone_verification_start={
            "data": {
                "verification_id": "real-verification-id",
                "phone": "+15550101111",
                "masked_phone": "+155****1111",
                "delivery_channel": "debug_sms",
                "debug_code": "123456",
            }
        },
        phone_verification_confirm={
            "data": {
                "phone": "+15550101111",
                "phone_verified": True,
                "verification_id": "real-verification-id",
            }
        },
        generated_at="2026-07-06T08:00:00Z",
    )
    text = json.dumps(fixture, ensure_ascii=False)

    assert fixture["metadata"]["api_base"] == "http://106.55.62.122:8011"
    assert fixture["metadata"]["contains_access_token"] is False
    assert fixture["stitch_usage"]["must_render_from"] == [
        "me.data.profile",
        "me.data.patient_view.home",
        "me.data.patient_view.profile",
        "me.data.patient_view.device",
        "me.data.patient_view.agent",
        "public_config.data.agent",
    ]
    assert fixture["me"]["data"]["patient_view"]["agent"]["entry_label"] == "\u95ee\u5eb7\u590d\u5e08"
    assert fixture["agent"]["safe_response"]["data"]["answer"] == "\u5efa\u8bae\u5148\u964d\u4f4e\u5f3a\u5ea6"
    assert fixture["phone_verification"]["start_response"]["data"]["verification_id"] == "fixture-verification-id"
    assert fixture["phone_verification"]["confirm_response"]["data"]["phone_verified"] is True
    assert "3245056131@qq.com" not in text
    assert "+15550101111" not in text
    assert "123456" not in text
    assert "real-verification-id" not in text
    assert "real-user-id" not in text


def test_sanitize_for_stitch_replaces_uuid_like_ids_and_endpoint_segments():
    module = _load_module()

    sanitized = module.sanitize_for_stitch(
        {
            "data": {
                "plan_id": "0bb027d4-a440-4e92-9347-3e2a7ef55884",
                "source_id": "5d63e24d-64bf-44d0-bf57-604fe49b030e",
                "draft_id": "f820b866-ac29-428c-8f9f-a050f20abbb1",
                "device_id": "8bf74838-2eb9-46ac-8a6d-6f1117215a90",
                "endpoint": "/api/rehab-arm/app/v1/training-plans/0bb027d4-a440-4e92-9347-3e2a7ef55884/sync-to-device",
                "standard_uuid": "00001101-0000-1000-8000-00805F9B34FB",
            }
        }
    )
    text = json.dumps(sanitized, ensure_ascii=False)

    assert "0bb027d4-a440-4e92-9347-3e2a7ef55884" not in text
    assert "5d63e24d-64bf-44d0-bf57-604fe49b030e" not in text
    assert "f820b866-ac29-428c-8f9f-a050f20abbb1" not in text
    assert "8bf74838-2eb9-46ac-8a6d-6f1117215a90" not in text
    assert "00001101-0000-1000-8000-00805F9B34FB" not in text
    assert sanitized["data"]["plan_id"] == "fixture-plan-id"
    assert sanitized["data"]["source_id"] == "fixture-source-id"
    assert sanitized["data"]["draft_id"] == "fixture-draft-id"
    assert sanitized["data"]["device_id"] == "fixture-device-id"
    assert sanitized["data"]["endpoint"] == "/api/rehab-arm/app/v1/training-plans/{fixture-id}/sync-to-device"
    assert sanitized["data"]["standard_uuid"] == "fixture-uuid"
