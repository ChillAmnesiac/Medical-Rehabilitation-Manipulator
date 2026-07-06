from fastapi.testclient import TestClient

from app.main import create_app


def test_health_exposes_deployment_metadata(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("AI_COLLAB_BUILD_SHA", "b925e316")
    monkeypatch.setenv("AI_COLLAB_BUILD_REF", "codex/rehab-mobile-backend-qa-20260706")
    monkeypatch.setenv("AI_COLLAB_BUILD_TIME", "2026-07-06T12:34:56Z")
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    response = client.get("/health")

    assert response.status_code == 200
    deployment = response.json()["data"]["deployment"]
    assert deployment == {
        "build_sha": "b925e316",
        "build_ref": "codex/rehab-mobile-backend-qa-20260706",
        "build_time": "2026-07-06T12:34:56Z",
        "app_env": "staging",
    }
