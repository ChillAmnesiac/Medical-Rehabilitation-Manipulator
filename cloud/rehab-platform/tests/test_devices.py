from fastapi.testclient import TestClient

from app.main import create_app
from app.models import User
from app.security import hash_password


def _auth_headers(
    client: TestClient,
    email: str = "3245056131@qq.com",
    password: str = "1234",
) -> dict[str, str]:
    response = client.post(
        "/api/auth/session",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_user(app, email: str, password: str) -> None:
    with app.state.session_factory() as session:
        session.add(
            User(
                email=email,
                password_hash=hash_password(password),
                name="Second Patient",
            )
        )
        session.commit()


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


def test_bind_device_updates_existing_device_for_same_account():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    first = client.post(
        "/api/rehab-arm/app/v1/devices/bind",
        headers=headers,
        json={"m33_device_id": "REHAB-ARM-001", "ble_name": "OpenClaw-NUS"},
    )
    second = client.post(
        "/api/rehab-arm/app/v1/devices/bind",
        headers=headers,
        json={
            "m33_device_id": "REHAB-ARM-001",
            "ble_name": "LingDong-Arm",
            "trust_status": "trusted",
            "firmware_version": "2026.07.06",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200
    first_device = first.json()["data"]
    second_device = second.json()["data"]
    assert second_device["id"] == first_device["id"]
    assert second_device["ble_name"] == "LingDong-Arm"
    assert second_device["firmware_version"] == "2026.07.06"

    me = client.get("/api/rehab-arm/app/v1/me", headers=headers)
    assert len(me.json()["data"]["devices"]) == 1


def test_bind_device_rejects_hardware_id_already_bound_to_another_account():
    app = create_app(database_url="sqlite+pysqlite:///:memory:")
    client = TestClient(app)
    first_headers = _auth_headers(client)
    _create_user(app, "second-patient@example.com", "1234")
    second_headers = _auth_headers(client, "second-patient@example.com", "1234")

    first = client.post(
        "/api/rehab-arm/app/v1/devices/bind",
        headers=first_headers,
        json={"m33_device_id": "REHAB-ARM-SHARED", "ble_name": "OpenClaw-NUS"},
    )
    second = client.post(
        "/api/rehab-arm/app/v1/devices/bind",
        headers=second_headers,
        json={"m33_device_id": "REHAB-ARM-SHARED", "ble_name": "Other Phone"},
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "DEVICE_ALREADY_BOUND"

    second_me = client.get("/api/rehab-arm/app/v1/me", headers=second_headers)
    assert second_me.json()["data"]["devices"] == []


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
