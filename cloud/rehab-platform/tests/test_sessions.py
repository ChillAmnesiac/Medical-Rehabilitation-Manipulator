from fastapi.testclient import TestClient

from app.main import create_app


def _auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/session",
        json={"email": "3245056131@qq.com", "password": "1234"},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _bind_device(client: TestClient, headers: dict[str, str]) -> dict[str, object]:
    response = client.post(
        "/api/rehab-arm/app/v1/devices/bind",
        headers=headers,
        json={"m33_device_id": "OpenClaw-NUS", "ble_name": "OpenClaw-NUS"},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_upload_completed_training_session_creates_patient_report():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)
    device = _bind_device(client, headers)

    response = client.post(
        "/api/rehab-arm/app/v1/training-sessions",
        headers=headers,
        json={
            "device_id": device["id"],
            "plan_id": "plan-daily-grip",
            "duration_seconds": 720,
            "completed_movements": 36,
            "target_movements": 40,
            "pain_score": 2,
            "fatigue_score": 3,
            "emg_summary": {"avg": 0.38, "peak": 0.74},
            "notes": "Patient finished with stable rhythm.",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["session"]["status"] == "completed"
    assert payload["session"]["completion_rate"] == 0.9
    assert payload["report"]["title"] == "Daily rehab session"
    assert payload["report"]["pain_score"] == 2
    assert payload["report"]["safety_level"] == "normal"

    me = client.get("/api/rehab-arm/app/v1/me", headers=headers).json()["data"]
    assert me["latest_report"]["id"] == payload["report"]["id"]
    assert me["training_reports"][0]["id"] == payload["report"]["id"]
    assert me["mobile_readiness_guide"]["next_action"]["code"] == "review_report"


def test_recent_training_sessions_are_listed_newest_first():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)
    device = _bind_device(client, headers)

    for index in range(2):
        response = client.post(
            "/api/rehab-arm/app/v1/training-sessions",
            headers=headers,
            json={
                "device_id": device["id"],
                "duration_seconds": 300 + index,
                "completed_movements": 10 + index,
                "target_movements": 20,
                "pain_score": 1,
                "fatigue_score": 2,
            },
        )
        assert response.status_code == 200

    recent = client.get("/api/rehab-arm/app/v1/training-sessions/recent", headers=headers)

    assert recent.status_code == 200
    sessions = recent.json()["data"]["sessions"]
    assert [session["completed_movements"] for session in sessions] == [11, 10]
    assert sessions[0]["completion_rate"] == 0.55


def test_training_session_rejects_devices_from_other_users():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    response = client.post(
        "/api/rehab-arm/app/v1/training-sessions",
        headers=headers,
        json={
            "device_id": "999",
            "duration_seconds": 600,
            "completed_movements": 12,
            "target_movements": 20,
            "pain_score": 2,
            "fatigue_score": 3,
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEVICE_NOT_FOUND"
