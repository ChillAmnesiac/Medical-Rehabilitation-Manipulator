import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("qa_rehab_mobile_acceptance.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("qa_rehab_mobile_acceptance", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_agent_model_status_accepts_cloud_and_fallback_modes():
    module = _load_module()

    assert module.agent_model_status_ok(
        {
            "data": {
                "answer": "patient answer",
                "model_status": {
                    "mode": "cloud_model",
                    "configured": True,
                    "provider": "openai_compatible",
                    "model": "rehab-cloud-model",
                },
            }
        }
    )
    assert module.agent_model_status_ok(
        {
            "data": {
                "answer": "patient answer",
                "model_status": {
                    "mode": "fallback_rule_based",
                    "configured": False,
                    "fallback_reason": "external_model_not_configured",
                },
            }
        }
    )


def test_agent_model_status_rejects_missing_or_ambiguous_status():
    module = _load_module()

    assert not module.agent_model_status_ok({"data": {"answer": "patient answer"}})
    assert not module.agent_model_status_ok({"data": {"model_status": {"mode": "unknown"}}})


def test_agent_cloud_model_readiness_reports_cloud_model_ready():
    module = _load_module()

    ok, detail = module.agent_cloud_model_readiness(
        {
            "data": {
                "model_status": {
                    "mode": "cloud_model",
                    "configured": True,
                    "provider": "openai_compatible",
                    "model": "rehab-cloud-model",
                }
            }
        }
    )

    assert ok is True
    assert detail["mode"] == "cloud_model"
    assert detail["model"] == "rehab-cloud-model"


def test_agent_cloud_model_readiness_warns_on_rule_based_fallback():
    module = _load_module()

    ok, detail = module.agent_cloud_model_readiness(
        {
            "data": {
                "model_status": {
                    "mode": "fallback_rule_based",
                    "configured": False,
                    "provider": "openai_compatible",
                    "fallback_reason": "external_model_not_configured",
                }
            }
        }
    )

    assert ok is False
    assert detail["mode"] == "fallback_rule_based"
    assert detail["reason"] == "external_model_not_configured"


def test_phone_verification_flow_uses_debug_code_to_confirm_staging_phone():
    module = _load_module()

    class FakeClient:
        def __init__(self):
            self.calls = []

        def request(self, method, path, payload=None, token=None, headers=None):
            self.calls.append({"method": method, "path": path, "payload": payload, "token": token})
            if path == "/api/rehab-arm/app/v1/account/phone-verifications":
                return 200, {
                    "data": {
                        "verification_id": "42",
                        "masked_phone": "+155****6666",
                        "expires_in": 300,
                        "delivery_channel": "debug_sms",
                        "debug_code": "426666",
                    }
                }, {}
            if path == "/api/rehab-arm/app/v1/account/phone-verifications/42/confirm":
                return 200, {"data": {"profile": {"phone_verified": True}}}, {}
            return 404, {}, {}

    ok, detail = module.run_phone_verification_flow(FakeClient(), "token", "+15550106666")

    assert ok is True
    assert detail["masked_phone"] == "+155****6666"
    assert detail["phone_verified"] is True


def test_phone_verification_flow_fails_without_debug_code_for_automated_staging():
    module = _load_module()

    class FakeClient:
        def request(self, method, path, payload=None, token=None, headers=None):
            return 200, {
                "data": {
                    "verification_id": "42",
                    "masked_phone": "+155****6666",
                    "expires_in": 300,
                    "delivery_channel": "sms",
                }
            }, {}

    ok, detail = module.run_phone_verification_flow(FakeClient(), "token", "+15550106666")

    assert ok is False
    assert detail["reason"] == "debug_code_missing"


def test_phone_delivery_readiness_reports_real_sms_ready():
    module = _load_module()

    ok, detail = module.phone_delivery_readiness(
        {
            "data": {
                "phone_verification": {
                    "delivery_status": {
                        "mode": "sms",
                        "configured": True,
                        "provider": "webhook",
                        "exposes_debug_code": False,
                    }
                }
            }
        }
    )

    assert ok is True
    assert detail["mode"] == "sms"
    assert detail["provider"] == "webhook"


def test_phone_delivery_readiness_warns_when_debug_sms_is_enabled():
    module = _load_module()

    ok, detail = module.phone_delivery_readiness(
        {
            "data": {
                "phone_verification": {
                    "delivery_status": {
                        "mode": "debug_sms",
                        "configured": False,
                        "provider": None,
                        "exposes_debug_code": True,
                        "reason": "debug_code_enabled",
                    }
                }
            }
        }
    )

    assert ok is False
    assert detail["mode"] == "debug_sms"
    assert detail["reason"] == "debug_code_enabled"


def test_device_binding_flow_binds_and_updates_same_device_idempotently():
    module = _load_module()

    class FakeClient:
        def __init__(self):
            self.calls = []

        def request(self, method, path, payload=None, token=None, headers=None):
            self.calls.append({"method": method, "path": path, "payload": payload, "token": token})
            if len(self.calls) == 1:
                return 200, {
                    "data": {
                        "id": "device-42",
                        "m33_device_id": "QA-REHAB-ARM-STAGING-001",
                        "ble_name": "LingDong Rehab QA",
                        "trust_status": "trusted",
                    }
                }, {}
            return 200, {
                "data": {
                    "id": "device-42",
                    "m33_device_id": "QA-REHAB-ARM-STAGING-001",
                    "ble_name": "LingDong Rehab QA Verified",
                    "trust_status": "trusted",
                }
            }, {}

    client = FakeClient()
    ok, detail = module.run_device_binding_flow(client, "token", "QA-REHAB-ARM-STAGING-001")

    assert ok is True
    assert detail["device_id"] == "device-42"
    assert detail["second_bind_same_device"] is True
    assert client.calls[0]["path"] == "/api/rehab-arm/app/v1/devices/bind"
    assert client.calls[0]["payload"]["m33_device_id"] == "QA-REHAB-ARM-STAGING-001"


def test_device_binding_flow_surfaces_already_bound_conflict():
    module = _load_module()

    class FakeClient:
        def request(self, method, path, payload=None, token=None, headers=None):
            return 409, {"error": {"code": "DEVICE_ALREADY_BOUND", "message": "already bound"}}, {}

    ok, detail = module.run_device_binding_flow(FakeClient(), "token", "QA-REHAB-ARM-STAGING-001")

    assert ok is False
    assert detail["reason"] == "first_bind_failed"
    assert detail["error_code"] == "DEVICE_ALREADY_BOUND"


def test_get_or_create_session_token_registers_secondary_account_after_login_failure():
    module = _load_module()

    class FakeClient:
        def __init__(self):
            self.calls = []

        def request(self, method, path, payload=None, token=None, headers=None):
            self.calls.append({"method": method, "path": path, "payload": payload})
            if path == "/api/auth/session" and len([call for call in self.calls if call["path"] == path]) == 1:
                return 401, {"error": {"code": "INVALID_CREDENTIALS"}}, {}
            if path == "/api/auth/register":
                return 200, {"data": {"id": "user-2", "email": payload["email"]}}, {}
            if path == "/api/auth/session":
                return 200, {"data": {"access_token": "secondary-token"}}, {}
            return 404, {}, {}

    token, detail = module.get_or_create_session_token(
        FakeClient(),
        "rehab-qa-secondary@example.com",
        "1234",
        "Rehab QA Secondary",
    )

    assert token == "secondary-token"
    assert detail["registered"] is True
    assert detail["login_status_code"] == 200


def test_device_already_bound_conflict_flow_rejects_second_account_claim():
    module = _load_module()

    class FakeClient:
        def __init__(self):
            self.calls = []

        def request(self, method, path, payload=None, token=None, headers=None):
            self.calls.append({"method": method, "path": path, "payload": payload, "token": token})
            if token == "owner-token":
                return 200, {
                    "data": {
                        "id": "owned-device",
                        "m33_device_id": "QA-REHAB-ARM-CONFLICT-001",
                        "ble_name": "LingDong Conflict Owner",
                    }
                }, {}
            if token == "secondary-token":
                return 409, {"error": {"code": "DEVICE_ALREADY_BOUND"}}, {}
            return 401, {"error": {"code": "AUTH_INVALID"}}, {}

    ok, detail = module.run_device_already_bound_conflict_flow(
        FakeClient(),
        "owner-token",
        "secondary-token",
        "QA-REHAB-ARM-CONFLICT-001",
    )

    assert ok is True
    assert detail["owner_bind_status_code"] == 200
    assert detail["second_bind_status_code"] == 409
    assert detail["second_error_code"] == "DEVICE_ALREADY_BOUND"
