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


def test_bind_device_makes_it_visible_in_mobile_bootstrap():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    bound = client.post(
        "/api/rehab-arm/app/v1/devices/bind",
        headers=headers,
        json={
            "m33_device_id": "AA:BB:CC:DD:EE:FF",
            "ble_name": "OpenClaw-NUS",
            "trust_status": "trusted",
        },
    )

    assert bound.status_code == 200
    device = bound.json()["data"]
    assert device["id"]
    assert device["m33_device_id"] == "AA:BB:CC:DD:EE:FF"
    assert device["ble_name"] == "OpenClaw-NUS"
    assert device["trust_status"] == "trusted"

    me = client.get("/api/rehab-arm/app/v1/me", headers=headers)
    devices = me.json()["data"]["devices"]
    assert len(devices) == 1
    assert devices[0]["id"] == device["id"]
    assert me.json()["data"]["mobile_readiness_guide"]["next_action"]["code"] == "generate_plan"


def test_legacy_spp_inbound_records_sensor_payload_for_bound_device():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)
    device = client.post(
        "/api/rehab-arm/app/v1/devices/bind",
        headers=headers,
        json={"m33_device_id": "OpenClaw-NUS", "ble_name": "OpenClaw-NUS"},
    ).json()["data"]

    inbound = client.post(
        f"/api/rehab-arm/app/v1/devices/{device['id']}/legacy-spp/inbound",
        headers=headers,
        json={
            "raw_text": '{"type":"sensor","emg":0.42,"battery":88,"status":"ok"}',
            "related_message_id": "msg-1",
            "transport_event": {"connected": True},
        },
    )

    assert inbound.status_code == 200
    payload = inbound.json()["data"]
    assert payload["status"] == "matched"
    assert payload["raw_text"] == '{"type":"sensor","emg":0.42,"battery":88,"status":"ok"}'
    assert payload["parsed"]["type"] == "sensor"
    assert payload["parsed"]["emg"] == 0.42


def test_bind_device_requires_token():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    response = client.post(
        "/api/rehab-arm/app/v1/devices/bind",
        json={"m33_device_id": "AA:BB"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
