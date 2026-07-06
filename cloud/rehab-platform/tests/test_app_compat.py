import json

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


def _accepted_plan(client: TestClient, headers: dict[str, str]) -> dict[str, object]:
    draft = client.post(
        "/api/rehab-arm/app/v1/ai-training-drafts/generate",
        headers=headers,
        json={"input_text": "Create a light plan.", "context_snapshot": {"movement_type": "grip"}},
    ).json()["data"]
    response = client.post(
        f"/api/rehab-arm/app/v1/ai-training-drafts/{draft['id']}/accept",
        headers=headers,
        json={},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_public_config_and_catalog_match_mobile_bridge_contract():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    public_config = client.get("/api/rehab-arm/app/v1/public-config")
    catalog = client.get("/api/rehab-arm/app/v1/catalog")

    assert public_config.status_code == 200
    config = public_config.json()["data"]
    assert config["app_name"] == "Lingdong Rehab Cloud"
    assert config["rehab_app"]["catalog_endpoint"] == "/api/rehab-arm/app/v1/catalog"
    assert config["rehab_app"]["workflow_endpoint"] == "/api/rehab-arm/app/v1/me/workflow"
    assert config["m33_legacy_spp_profile"]["service_uuid"]

    assert catalog.status_code == 200
    payload = catalog.json()["data"]
    assert payload["training_movements"][0]["code"] == "elbow_flexion"
    assert payload["m33_legacy_spp_profile"]["write_characteristic_uuid"]


def test_mobile_bootstrap_includes_patient_view_without_raw_debug_terms():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    response = client.get("/api/rehab-arm/app/v1/me", headers=headers)

    assert response.status_code == 200
    patient_view = response.json()["data"]["patient_view"]
    assert sorted(patient_view.keys()) == ["agent", "device", "home", "profile"]
    raw_text = json.dumps(patient_view, ensure_ascii=False)
    for term in ("M33", "M55", "SPP", "CAN", "UUID", "preflight", "setup_required", "early_active"):
        assert term not in raw_text
    assert patient_view["home"]["primary_action"]["label"]
    assert patient_view["agent"]["entry_label"] == "问康复师"
    assert patient_view["agent"]["endpoint"] == "/api/rehab-arm/app/v1/agent/messages"
    assert patient_view["device"]["binding_steps"][0] == "打开康复设备电源"
    assert patient_view["profile"]["phone"]["label"] == "手机号"
    assert patient_view["profile"]["rehab_stage"]["value"]
    assert patient_view["profile"]["affected_side"]["value"]
    assert patient_view["profile"]["medical_constraints"]["status"] in {"待完善", "已填写"}


def test_workflow_endpoint_reflects_current_patient_state():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    initial = client.get("/api/rehab-arm/app/v1/me/workflow", headers=headers).json()["data"]
    assert initial["next_action"]["code"] == "BIND_DEVICE"

    _bind_device(client, headers)
    with_device = client.get("/api/rehab-arm/app/v1/me/workflow", headers=headers).json()["data"]
    assert with_device["next_action"]["code"] == "GENERATE_AI_DRAFT"

    _accepted_plan(client, headers)
    with_plan = client.get("/api/rehab-arm/app/v1/me/workflow", headers=headers).json()["data"]
    assert with_plan["next_action"]["code"] == "SYNC_ACCEPTED_PLAN_TO_M33"


def test_sync_plan_and_ble_message_create_sendable_legacy_frame():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)
    device = _bind_device(client, headers)
    plan = _accepted_plan(client, headers)

    sync = client.post(
        f"/api/rehab-arm/app/v1/training-plans/{plan['id']}/sync-to-device",
        headers=headers,
        json={"device_id": device["id"]},
    )

    assert sync.status_code == 200
    assert sync.json()["data"]["plan"]["device_sync_status"] == "synced"
    assert sync.json()["data"]["plan"]["m33_status"] == "pending"

    ble = client.post(
        f"/api/rehab-arm/app/v1/devices/{device['id']}/ble/messages",
        headers=headers,
        json={"message_type": "training_plan_push", "plan_id": plan["id"]},
    )

    assert ble.status_code == 200
    message = ble.json()["data"]
    frame = message["payload"]["legacy_transport_frame"]
    assert frame["sendable"] is True
    assert frame["json"]["type"] == "training_plan_push"
    assert frame["json"]["plan_id"] == plan["id"]
    assert "M33" in frame["control_boundary"]
    assert frame["wire_text"].endswith("\n")


def test_latest_emg_comes_from_legacy_spp_sensor_evidence():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)
    device = _bind_device(client, headers)
    client.post(
        f"/api/rehab-arm/app/v1/devices/{device['id']}/legacy-spp/inbound",
        headers=headers,
        json={"raw_text": '{"type":"sensor","emg":0.51,"battery":87}'},
    )

    latest = client.get("/api/rehab-arm/app/v1/emg/latest", headers=headers)

    assert latest.status_code == 200
    payload = latest.json()["data"]
    assert payload["source"] == "legacy_spp_inbound"
    assert payload["sample"]["emg"] == 0.51
