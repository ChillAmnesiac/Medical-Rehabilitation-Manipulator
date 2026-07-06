import pytest

import configure_rehab_model_relay as module


def test_build_config_payload_requires_all_model_fields():
    with pytest.raises(ValueError) as exc:
        module.build_config_payload(
            provider="openai_compatible",
            base_url="https://model.example/v1",
            model="",
            api_key="test-api-key",
        )

    assert "model" in str(exc.value)


def test_build_config_payload_keeps_secret_out_of_summary():
    payload = module.build_config_payload(
        provider="openai_compatible",
        base_url="https://model.example/v1/",
        model="rehab-cloud-model",
        api_key="test-api-key-value",
    )
    summary = module.summarize_config_payload(payload)

    assert payload == {
        "provider": "openai_compatible",
        "base_url": "https://model.example/v1",
        "model": "rehab-cloud-model",
        "api_key": "test-api-key-value",
        "external_enabled": True,
    }
    assert "test-api-key-value" not in str(summary)
    assert summary["api_key"] == "<redacted>"


def test_build_config_payload_defaults_gemini_base_url():
    payload = module.build_config_payload(
        provider="gemini",
        base_url="",
        model="gemini-1.5-flash",
        api_key="test-api-key-value",
    )

    assert payload["provider"] == "gemini"
    assert payload["base_url"] == "https://generativelanguage.googleapis.com/v1beta"
    assert payload["model"] == "gemini-1.5-flash"


def test_model_relay_config_path_quotes_project_id():
    assert (
        module.model_relay_config_path("project id/with spaces")
        == "/api/rehab-arm/v1/projects/project%20id%2Fwith%20spaces/model-relay/config"
    )


def test_agent_smoke_requires_cloud_model_status():
    ok, detail = module.agent_smoke_is_cloud_model(
        {
            "data": {
                "answer": "safe answer",
                "model_status": {
                    "mode": "cloud_model",
                    "configured": True,
                    "provider": "openai_compatible",
                    "model": "rehab-cloud-model",
                },
            }
        }
    )

    assert ok
    assert detail["mode"] == "cloud_model"


def test_agent_smoke_rejects_fallback_status():
    ok, detail = module.agent_smoke_is_cloud_model(
        {
            "data": {
                "answer": "safe fallback",
                "model_status": {
                    "mode": "fallback_rule_based",
                    "configured": False,
                    "provider": "openai_compatible",
                    "fallback_reason": "external_model_not_configured",
                },
            }
        }
    )

    assert not ok
    assert detail["mode"] == "fallback_rule_based"
    assert detail["reason"] == "external_model_not_configured"
