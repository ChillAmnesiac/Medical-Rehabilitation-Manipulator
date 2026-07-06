import argparse
import importlib.util
import json
import sys
import urllib.error
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("smoke_rehab_sms_provider.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("smoke_rehab_sms_provider", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _args(**overrides):
    values = {
        "provider": "webhook",
        "webhook_url": "https://sms.example.test/send",
        "webhook_token": "secret-sms-token",
        "phone": "+15550101111",
        "code": "123456",
        "purpose": "bind_account",
        "verification_id": "smoke-verification",
        "expires_in": 300,
        "timeout": 3,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_sms_smoke_posts_webhook_and_redacts_sensitive_values():
    module = _load_module()
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse(202, {"accepted": True, "message_id": "sms-123"})

    exit_code, summary = module.run(_args(), opener=fake_urlopen)

    assert exit_code == 0
    assert captured["timeout"] == 3
    assert captured["request"].full_url == "https://sms.example.test/send"
    assert captured["request"].get_header("Authorization") == "Bearer secret-sms-token"
    payload = json.loads(captured["request"].data.decode("utf-8"))
    assert payload == {
        "phone": "+15550101111",
        "code": "123456",
        "purpose": "bind_account",
        "verification_id": "smoke-verification",
        "expires_in": 300,
    }
    rendered = json.dumps(summary, ensure_ascii=False)
    assert summary["status"] == "ok"
    assert summary["delivery_accepted"] is True
    assert summary["request"]["phone"] == "+155****1111"
    assert summary["request"]["webhook_token"] == "<redacted>"
    assert "secret-sms-token" not in rendered
    assert "123456" not in rendered
    assert "+15550101111" not in rendered


def test_sms_smoke_reports_provider_http_error_without_leaking_secret():
    module = _load_module()

    def fake_urlopen(request, timeout):
        raise urllib.error.HTTPError(
            request.full_url,
            401,
            "Unauthorized",
            {},
            None,
        )

    exit_code, summary = module.run(_args(), opener=fake_urlopen)

    assert exit_code == 3
    assert summary["status"] == "provider_http_error"
    assert summary["status_code"] == 401
    assert "secret-sms-token" not in json.dumps(summary, ensure_ascii=False)


def test_sms_smoke_requires_core_fields_before_sending():
    module = _load_module()

    exit_code = module.main(
        [
            "--provider",
            "webhook",
            "--webhook-url",
            "https://sms.example.test/send",
            "--webhook-token",
            "secret-sms-token",
            "--phone",
            "+15550101111",
        ]
    )

    assert exit_code == 1
