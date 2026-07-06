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


def test_phone_verification_binds_phone_to_current_account():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    start = client.post(
        "/api/rehab-arm/app/v1/account/phone-verifications",
        headers=headers,
        json={"phone": "+15550101111", "purpose": "bind_account"},
    )

    assert start.status_code == 200
    verification = start.json()["data"]
    assert verification["verification_id"]
    assert verification["masked_phone"] == "+155****1111"
    assert verification["expires_in"] == 300
    assert verification["delivery_channel"] == "debug_sms"
    assert len(verification["debug_code"]) == 6

    confirm = client.post(
        f"/api/rehab-arm/app/v1/account/phone-verifications/{verification['verification_id']}/confirm",
        headers=headers,
        json={"code": verification["debug_code"]},
    )

    assert confirm.status_code == 200
    profile = confirm.json()["data"]["profile"]
    assert profile["phone"] == "+15550101111"
    assert profile["phone_verified"] is True

    me = client.get("/api/rehab-arm/app/v1/me", headers=headers).json()["data"]
    assert me["profile"]["phone"] == "+15550101111"
    assert me["profile"]["phone_verified"] is True


def test_phone_verification_rejects_wrong_code_without_binding_phone():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)
    verification = client.post(
        "/api/rehab-arm/app/v1/account/phone-verifications",
        headers=headers,
        json={"phone": "+15550102222", "purpose": "bind_account"},
    ).json()["data"]

    confirm = client.post(
        f"/api/rehab-arm/app/v1/account/phone-verifications/{verification['verification_id']}/confirm",
        headers=headers,
        json={"code": "000000"},
    )

    assert confirm.status_code == 400
    assert confirm.json()["error"]["code"] == "PHONE_CODE_INVALID"
    me = client.get("/api/rehab-arm/app/v1/me", headers=headers).json()["data"]
    assert me["profile"]["phone"] == ""
    assert me["profile"]["phone_verified"] is False


def test_phone_verification_requires_login():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    response = client.post(
        "/api/rehab-arm/app/v1/account/phone-verifications",
        json={"phone": "+15550103333", "purpose": "bind_account"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
