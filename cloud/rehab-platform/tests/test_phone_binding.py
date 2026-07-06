from fastapi.testclient import TestClient

from app.api.routes import rehab_app
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


def test_phone_verification_rate_limits_immediate_resend(monkeypatch):
    monkeypatch.setenv("PHONE_VERIFICATION_RESEND_COOLDOWN_SECONDS", "60")
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)
    payload = {"phone": "+15550106666", "purpose": "bind_account"}

    first = client.post("/api/rehab-arm/app/v1/account/phone-verifications", headers=headers, json=payload)
    second = client.post("/api/rehab-arm/app/v1/account/phone-verifications", headers=headers, json=payload)

    assert first.status_code == 200
    assert second.status_code == 429
    error = second.json()["error"]
    assert error["code"] == "PHONE_CODE_RESEND_TOO_SOON"
    assert 1 <= error["retry_after"] <= 60


def test_phone_verification_delivers_via_webhook_when_debug_sms_disabled(monkeypatch):
    deliveries = []

    def fake_post_sms_webhook(settings, payload):
        deliveries.append({"provider": settings.phone_verification_sms_provider, "payload": payload})

    monkeypatch.setenv("PHONE_VERIFICATION_DEBUG_CODE_ENABLED", "false")
    monkeypatch.setenv("PHONE_VERIFICATION_SMS_PROVIDER", "webhook")
    monkeypatch.setenv("PHONE_VERIFICATION_SMS_WEBHOOK_URL", "https://sms.example.test/send")
    monkeypatch.setenv("PHONE_VERIFICATION_SMS_WEBHOOK_TOKEN", "secret-token")
    monkeypatch.setattr(rehab_app, "_post_sms_webhook", fake_post_sms_webhook)
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    start = client.post(
        "/api/rehab-arm/app/v1/account/phone-verifications",
        headers=headers,
        json={"phone": "+15550104444", "purpose": "bind_account"},
    )

    assert start.status_code == 200
    verification = start.json()["data"]
    assert verification["delivery_channel"] == "sms"
    assert verification["delivery_provider"] == "webhook"
    assert "debug_code" not in verification
    assert len(deliveries) == 1
    assert deliveries[0]["payload"]["phone"] == "+15550104444"
    assert deliveries[0]["payload"]["code"].isdigit()
    assert len(deliveries[0]["payload"]["code"]) == 6
    assert deliveries[0]["payload"]["purpose"] == "bind_account"
    assert "secret-token" not in start.text


def test_phone_verification_fails_when_sms_not_configured_and_debug_sms_disabled(monkeypatch):
    monkeypatch.setenv("PHONE_VERIFICATION_DEBUG_CODE_ENABLED", "false")
    monkeypatch.delenv("PHONE_VERIFICATION_SMS_PROVIDER", raising=False)
    monkeypatch.delenv("PHONE_VERIFICATION_SMS_WEBHOOK_URL", raising=False)
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    start = client.post(
        "/api/rehab-arm/app/v1/account/phone-verifications",
        headers=headers,
        json={"phone": "+15550104445", "purpose": "bind_account"},
    )

    assert start.status_code == 503
    assert start.json()["error"]["code"] == "PHONE_SMS_NOT_CONFIGURED"


def test_phone_verification_reports_sms_delivery_failure(monkeypatch):
    def fake_post_sms_webhook(settings, payload):
        raise rehab_app.SmsDeliveryError("provider unavailable")

    monkeypatch.setenv("PHONE_VERIFICATION_DEBUG_CODE_ENABLED", "false")
    monkeypatch.setenv("PHONE_VERIFICATION_SMS_PROVIDER", "webhook")
    monkeypatch.setenv("PHONE_VERIFICATION_SMS_WEBHOOK_URL", "https://sms.example.test/send")
    monkeypatch.setattr(rehab_app, "_post_sms_webhook", fake_post_sms_webhook)
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)

    start = client.post(
        "/api/rehab-arm/app/v1/account/phone-verifications",
        headers=headers,
        json={"phone": "+15550104446", "purpose": "bind_account"},
    )

    assert start.status_code == 502
    assert start.json()["error"]["code"] == "PHONE_SMS_DELIVERY_FAILED"


def test_phone_verification_locks_after_max_wrong_attempts(monkeypatch):
    monkeypatch.setenv("PHONE_VERIFICATION_MAX_ATTEMPTS", "2")
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))
    headers = _auth_headers(client)
    verification = client.post(
        "/api/rehab-arm/app/v1/account/phone-verifications",
        headers=headers,
        json={"phone": "+15550105555", "purpose": "bind_account"},
    ).json()["data"]

    first = client.post(
        f"/api/rehab-arm/app/v1/account/phone-verifications/{verification['verification_id']}/confirm",
        headers=headers,
        json={"code": "000000"},
    )
    second = client.post(
        f"/api/rehab-arm/app/v1/account/phone-verifications/{verification['verification_id']}/confirm",
        headers=headers,
        json={"code": "111111"},
    )
    correct_after_lock = client.post(
        f"/api/rehab-arm/app/v1/account/phone-verifications/{verification['verification_id']}/confirm",
        headers=headers,
        json={"code": verification["debug_code"]},
    )

    assert first.status_code == 400
    assert first.json()["error"]["code"] == "PHONE_CODE_INVALID"
    assert second.status_code == 400
    assert second.json()["error"]["code"] == "PHONE_CODE_ATTEMPTS_EXCEEDED"
    assert correct_after_lock.status_code == 400
    assert correct_after_lock.json()["error"]["code"] == "PHONE_CODE_ATTEMPTS_EXCEEDED"


def test_phone_verification_requires_login():
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    response = client.post(
        "/api/rehab-arm/app/v1/account/phone-verifications",
        json={"phone": "+15550103333", "purpose": "bind_account"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"


def test_public_config_exposes_phone_delivery_readiness_without_secret(monkeypatch):
    monkeypatch.setenv("PHONE_VERIFICATION_DEBUG_CODE_ENABLED", "false")
    monkeypatch.setenv("PHONE_VERIFICATION_SMS_PROVIDER", "webhook")
    monkeypatch.setenv("PHONE_VERIFICATION_SMS_WEBHOOK_URL", "https://sms.example.test/send")
    monkeypatch.setenv("PHONE_VERIFICATION_SMS_WEBHOOK_TOKEN", "secret-token")
    client = TestClient(create_app(database_url="sqlite+pysqlite:///:memory:"))

    response = client.get("/api/rehab-arm/app/v1/public-config")

    assert response.status_code == 200
    phone_verification = response.json()["data"]["phone_verification"]
    assert phone_verification["start_endpoint"] == "/api/rehab-arm/app/v1/account/phone-verifications"
    assert phone_verification["resend_cooldown_seconds"] == 60
    delivery_status = phone_verification["delivery_status"]
    assert delivery_status == {
        "mode": "sms",
        "configured": True,
        "provider": "webhook",
        "exposes_debug_code": False,
    }
    assert "secret-token" not in response.text
