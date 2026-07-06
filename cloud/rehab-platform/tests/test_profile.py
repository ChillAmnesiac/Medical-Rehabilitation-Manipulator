from fastapi.testclient import TestClient

from app.main import create_app


def _login(client: TestClient) -> str:
    response = client.post(
        "/api/auth/session",
        json={"email": "3245056131@qq.com", "password": "1234"},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def test_profile_update_is_reflected_in_mobile_bootstrap():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    token = _login(client)
    headers = {"Authorization": f"Bearer {token}"}

    update = client.put(
        "/api/rehab-arm/app/v1/me/profile",
        headers=headers,
        json={
            "name": "王小明",
            "phone": "13800000000",
            "rehab_stage": "恢复期",
            "affected_side": "右侧",
            "medical_constraints": ["避免过度伸展", "训练中疼痛超过 5 分立即停止"],
        },
    )

    assert update.status_code == 200
    profile = update.json()["data"]["profile"]
    assert profile["name"] == "王小明"
    assert profile["phone"] == "13800000000"
    assert profile["rehab_stage"] == "恢复期"
    assert profile["affected_side"] == "右侧"
    assert profile["medical_constraints"] == ["避免过度伸展", "训练中疼痛超过 5 分立即停止"]

    me = client.get("/api/rehab-arm/app/v1/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["data"]["profile"] == profile


def test_profile_update_requires_token():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    response = client.put(
        "/api/rehab-arm/app/v1/me/profile",
        json={"name": "未登录用户"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
