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
