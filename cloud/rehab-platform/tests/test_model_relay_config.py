from fastapi.testclient import TestClient

from app.main import create_app
from app.models import User
from app.security import hash_password


def _auth_headers(client: TestClient) -> dict[str, str]:
    credentials = {"email": "model-relay-test@example.com", "password": "test-password"}
    with client.app.state.session_factory() as session:
        session.add(
            User(
                email=credentials["email"],
                password_hash=hash_password(credentials["password"]),
                name="Model Relay Test User",
            )
        )
        session.commit()
    response = client.post(
        "/api/auth/session",
        json=credentials,
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_model_relay_config_requires_auth():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    response = client.put(
        "/api/rehab-arm/v1/projects/staging/model-relay/config",
        json={
            "provider": "openai_compatible",
            "base_url": "https://model.example/v1",
            "model": "rehab-cloud-model",
            "api_key": "sk-test-secret",
            "external_enabled": True,
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_model_relay_config_updates_runtime_and_persists_env_without_leaking_secret(tmp_path):
    app = create_app(database_url="sqlite+pysqlite:///:memory:")
    app.state.settings.runtime_env_path = str(tmp_path / ".env")
    client = TestClient(app)
    headers = _auth_headers(client)

    response = client.put(
        "/api/rehab-arm/v1/projects/staging/model-relay/config",
        headers=headers,
        json={
            "provider": "openai_compatible",
            "base_url": "https://model.example/v1/",
            "model": "rehab-cloud-model",
            "api_key": "sk-test-secret",
            "external_enabled": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["project_id"] == "staging"
    assert payload["model_readiness"] == {
        "mode": "cloud_model_configured",
        "configured": True,
        "provider": "openai_compatible",
        "model": "rehab-cloud-model",
        "reason": None,
    }
    assert payload["config"]["api_key"] == "<redacted>"
    assert "sk-test-secret" not in str(payload)
    assert app.state.settings.agent_model_base_url == "https://model.example/v1"
    assert app.state.settings.agent_model_name == "rehab-cloud-model"
    assert app.state.settings.agent_model_api_key == "sk-test-secret"

    env_text = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "AGENT_MODEL_PROVIDER=openai_compatible" in env_text
    assert "AGENT_MODEL_BASE_URL=https://model.example/v1" in env_text
    assert "AGENT_MODEL_NAME=rehab-cloud-model" in env_text
    assert "AGENT_MODEL_API_KEY=sk-test-secret" in env_text


def test_configured_model_relay_is_visible_to_public_config_and_agent_smoke(tmp_path, monkeypatch):
    app = create_app(database_url="sqlite+pysqlite:///:memory:")
    app.state.settings.runtime_env_path = str(tmp_path / ".env")
    client = TestClient(app)
    headers = _auth_headers(client)
    response = client.put(
        "/api/rehab-arm/v1/projects/staging/model-relay/config",
        headers=headers,
        json={
            "provider": "openai_compatible",
            "base_url": "https://model.example/v1",
            "model": "rehab-cloud-model",
            "api_key": "sk-test-secret",
            "external_enabled": True,
        },
    )
    assert response.status_code == 200

    def fake_cloud_model(_settings, _messages):
        return "可以继续低强度训练；如果疼痛升高、麻木或疲劳异常，请暂停并联系康复师。"

    monkeypatch.setattr("app.services.agent.call_openai_compatible_model", fake_cloud_model)

    public_config = client.get("/api/rehab-arm/app/v1/public-config").json()["data"]
    assert public_config["agent"]["model_readiness"]["mode"] == "cloud_model_configured"
    assert public_config["agent"]["model_readiness"]["model"] == "rehab-cloud-model"
    assert "sk-test-secret" not in str(public_config)

    smoke = client.post(
        "/api/rehab-arm/app/v1/agent/messages",
        headers=headers,
        json={"message": "今天训练后酸痛，明天还能继续吗？"},
    )
    assert smoke.status_code == 200
    body = smoke.json()["data"]
    assert body["model_status"]["mode"] == "cloud_model"
    assert body["model_status"]["model"] == "rehab-cloud-model"
    assert body["answer"].startswith("可以继续低强度训练")
    assert "sk-test-secret" not in str(body)
