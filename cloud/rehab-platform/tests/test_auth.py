from fastapi.testclient import TestClient

from app.main import create_app


def test_stitch_app_login_returns_token_and_me_bootstrap():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    login = client.post(
        "/api/auth/session",
        json={"email": "3245056131@qq.com", "password": "1234"},
    )

    assert login.status_code == 200
    session = login.json()["data"]
    assert session["access_token"]
    assert session["token_type"] == "bearer"

    me = client.get(
        "/api/rehab-arm/app/v1/me",
        headers={"Authorization": f"Bearer {session['access_token']}"},
    )

    assert me.status_code == 200
    payload = me.json()["data"]
    assert payload["profile"]["email"] == "3245056131@qq.com"
    assert payload["profile"]["name"] == "康复用户"
    assert payload["mobile_readiness_guide"]["next_action"]["code"] == "bind_device"
    assert payload["devices"] == []
    assert payload["training_plans"] == []


def test_me_requires_bearer_token():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    response = client.get("/api/rehab-arm/app/v1/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
