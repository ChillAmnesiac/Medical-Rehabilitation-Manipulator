# Rehab Mobile SMS Delivery Runbook - 2026-07-06

This runbook enables real phone verification SMS delivery for the rehab mobile app.

Current staging remains in `debug_sms` mode until a real SMS webhook endpoint and token are provided and the preflight below passes. Do not disable debug SMS on staging without a passing provider smoke test, because the phone-binding flow would otherwise return `PHONE_SMS_NOT_CONFIGURED` or `PHONE_SMS_DELIVERY_FAILED`.

## Backend Contract

The app already exposes:

- `POST /api/rehab-arm/app/v1/account/phone-verifications`
- `POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm`
- `GET /api/rehab-arm/app/v1/public-config`

When SMS is configured and debug codes are disabled, `public-config` should report:

```json
{
  "phone_verification": {
    "delivery_status": {
      "mode": "sms",
      "configured": true,
      "provider": "webhook",
      "exposes_debug_code": false
    }
  }
}
```

## Provider Preflight

Run the provider smoke before writing any staging configuration:

```powershell
cloud\rehab-platform\.venv\Scripts\python.exe tools\smoke_rehab_sms_provider.py `
  --provider webhook `
  --webhook-url <SMS_WEBHOOK_URL> `
  --webhook-token <SMS_WEBHOOK_TOKEN> `
  --phone <REAL_TEST_PHONE> `
  --code 123456 `
  --purpose bind_account `
  --verification-id sms-provider-smoke `
  --expires-in 300
```

The output must show:

- `status = ok`
- `delivery_accepted = true`
- `status_code` in the `2xx` range
- `request.webhook_token = <redacted>`
- No raw verification code, raw token, or full phone number in stdout

Save the preflight output as an artifact, for example:

```powershell
cloud\rehab-platform\.venv\Scripts\python.exe tools\smoke_rehab_sms_provider.py ... > artifacts\rehab-mobile-sms\sms-provider-preflight.json
```

## Configure Staging

Dry-run first:

```powershell
cloud\rehab-platform\.venv\Scripts\python.exe tools\configure_rehab_sms_delivery.py `
  --provider webhook `
  --webhook-url <SMS_WEBHOOK_URL> `
  --webhook-token <SMS_WEBHOOK_TOKEN> `
  --preflight-json artifacts\rehab-mobile-sms\sms-provider-preflight.json `
  --env-file cloud\rehab-platform\.env
```

Only if the dry-run reports `mode = dry_run`, `written = false`, and the preflight target matches, execute:

```powershell
cloud\rehab-platform\.venv\Scripts\python.exe tools\configure_rehab_sms_delivery.py `
  --provider webhook `
  --webhook-url <SMS_WEBHOOK_URL> `
  --webhook-token <SMS_WEBHOOK_TOKEN> `
  --preflight-json artifacts\rehab-mobile-sms\sms-provider-preflight.json `
  --env-file cloud\rehab-platform\.env `
  --execute
```

`cloud/rehab-platform/.env` is intentionally gitignored.

## Post-Config Verification

Restart the rehab cloud service after changing `.env`, then run:

```powershell
$env:REHAB_QA_EMAIL='3245056131@qq.com'
$env:REHAB_QA_PASSWORD='1234'
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_acceptance.py
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_release.py
curl.exe -I -sS http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk
```

Expected SMS-specific result after real provider configuration:

- `P1-PHONE-SMS-001 = PASS`
- `delivery_status.mode = sms`
- `delivery_status.configured = true`
- `delivery_status.exposes_debug_code = false`
- Phone verification start response does not include `debug_code`
- Wrong/failed provider states surface to frontend as `PHONE_SMS_NOT_CONFIGURED` or `PHONE_SMS_DELIVERY_FAILED`

Current 2026-07-06 staging status: provider not supplied, so production SMS is not enabled yet.
