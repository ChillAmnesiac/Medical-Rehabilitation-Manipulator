import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("configure_rehab_sms_delivery.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("configure_rehab_sms_delivery", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _preflight(provider="webhook", webhook_url="https://sms.example.test/send", status="ok"):
    return {
        "status": status,
        "delivery_accepted": status == "ok",
        "request": {
            "provider": provider,
            "webhook_url": webhook_url,
            "webhook_token": "<redacted>",
            "phone": "+155****1111",
            "code": "<redacted>",
        },
    }


def test_build_env_updates_disable_debug_sms_and_redact_token_in_summary():
    module = _load_module()

    updates = module.build_env_updates(
        provider="webhook",
        webhook_url="https://sms.example.test/send",
        webhook_token="secret-sms-token",
    )
    summary = module.summarize_env_updates(updates)

    assert updates == {
        "PHONE_VERIFICATION_DEBUG_CODE_ENABLED": "false",
        "PHONE_VERIFICATION_SMS_PROVIDER": "webhook",
        "PHONE_VERIFICATION_SMS_WEBHOOK_URL": "https://sms.example.test/send",
        "PHONE_VERIFICATION_SMS_WEBHOOK_TOKEN": "secret-sms-token",
    }
    assert summary["PHONE_VERIFICATION_SMS_WEBHOOK_TOKEN"] == "<redacted>"
    assert "secret-sms-token" not in json.dumps(summary, ensure_ascii=False)


def test_preflight_must_match_provider_and_webhook_url():
    module = _load_module()

    ok, detail = module.preflight_allows_config(
        _preflight(),
        provider="webhook",
        webhook_url="https://sms.example.test/send",
    )
    assert ok
    assert detail["status"] == "ok"

    mismatch_ok, mismatch_detail = module.preflight_allows_config(
        _preflight(webhook_url="https://other.example/send"),
        provider="webhook",
        webhook_url="https://sms.example.test/send",
    )
    assert not mismatch_ok
    assert mismatch_detail["reason"] == "preflight_target_mismatch"


def test_update_env_text_preserves_existing_keys_and_replaces_sms_settings():
    module = _load_module()
    existing = "APP_ENV=staging\nPHONE_VERIFICATION_DEBUG_CODE_ENABLED=true\nOTHER=value\n"
    updates = module.build_env_updates(
        provider="webhook",
        webhook_url="https://sms.example.test/send",
        webhook_token="secret-sms-token",
    )

    rendered = module.update_env_text(existing, updates)

    assert "APP_ENV=staging" in rendered
    assert "OTHER=value" in rendered
    assert "PHONE_VERIFICATION_DEBUG_CODE_ENABLED=false" in rendered
    assert "PHONE_VERIFICATION_SMS_PROVIDER=webhook" in rendered
    assert "PHONE_VERIFICATION_SMS_WEBHOOK_URL=https://sms.example.test/send" in rendered
    assert "PHONE_VERIFICATION_SMS_WEBHOOK_TOKEN=secret-sms-token" in rendered
    assert rendered.endswith("\n")


def test_cli_dry_run_requires_passing_preflight_and_does_not_write_env(tmp_path, capsys):
    module = _load_module()
    preflight_path = tmp_path / "sms-preflight.json"
    env_path = tmp_path / ".env"
    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")

    exit_code = module.main(
        [
            "--provider",
            "webhook",
            "--webhook-url",
            "https://sms.example.test/send",
            "--webhook-token",
            "secret-sms-token",
            "--preflight-json",
            str(preflight_path),
            "--env-file",
            str(env_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert not env_path.exists()
    assert "dry_run" in captured.out
    assert "secret-sms-token" not in captured.out


def test_cli_execute_writes_env_only_after_preflight_passes(tmp_path):
    module = _load_module()
    preflight_path = tmp_path / "sms-preflight.json"
    env_path = tmp_path / ".env"
    preflight_path.write_text(json.dumps(_preflight(status="provider_http_error")), encoding="utf-8")

    failed_code = module.main(
        [
            "--provider",
            "webhook",
            "--webhook-url",
            "https://sms.example.test/send",
            "--webhook-token",
            "secret-sms-token",
            "--preflight-json",
            str(preflight_path),
            "--env-file",
            str(env_path),
            "--execute",
        ]
    )

    assert failed_code == 2
    assert not env_path.exists()

    preflight_path.write_text(json.dumps(_preflight()), encoding="utf-8")
    exit_code = module.main(
        [
            "--provider",
            "webhook",
            "--webhook-url",
            "https://sms.example.test/send",
            "--webhook-token",
            "secret-sms-token",
            "--preflight-json",
            str(preflight_path),
            "--env-file",
            str(env_path),
            "--execute",
        ]
    )

    assert exit_code == 0
    assert "PHONE_VERIFICATION_DEBUG_CODE_ENABLED=false" in env_path.read_text(encoding="utf-8")
