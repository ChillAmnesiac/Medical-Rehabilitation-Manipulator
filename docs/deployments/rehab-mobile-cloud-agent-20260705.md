# Rehab Mobile Cloud Deployment - 2026-07-05

## Scope

- Added an isolated local FastAPI MVP under `cloud/rehab-platform` with auth, profile, device binding, SPP evidence, sessions, reports, AI drafts, plan acceptance, BLE frame preparation, and rehab therapist Agent endpoints.
- Incrementally patched the existing cloud API at `ubuntu@106.55.62.122:/home/ubuntu/apps/ai-collab/apps/api` instead of replacing it, because port `8011` already serves the rehab/robot platform.
- Cloud additions:
  - `POST /api/rehab-arm/app/v1/agent/messages`
  - `POST /api/rehab-arm/app/v1/account/phone-verifications`
  - `POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm`
  - `profile.phone`, `profile.phone_verified`, and `profile.phone_verified_at` in rehab app bootstrap/profile responses
  - `onboarding_guide.steps[0] = PHONE_ACCOUNT_BINDING_REQUIRED`
  - Mobile PWA CORS allowance for `http://106.55.62.122:3001`, `http://127.0.0.1:4173`, and `http://localhost:4173`

## Verification

- Local backend tests: `21 passed, 1 warning`
- Cloud compile check: `.venv/bin/python -m py_compile app/db/models/rehab_arm_app.py app/db/models/__init__.py app/seed.py app/modules/rehab_arm/app_schemas.py app/modules/rehab_arm/app_service.py app/modules/rehab_arm/app_router.py`
- Cloud restart: uvicorn running on `0.0.0.0:8011`, PID `687286`
- Cloud live smoke:
  - `GET http://106.55.62.122:8011/health` passed.
  - `GET /api/rehab-arm/app/v1/public-config` returned the phone verification endpoint contract.
  - Login via `POST /api/auth/session` passed.
  - `POST /api/rehab-arm/app/v1/agent/messages` safe question passed in the previous cloud agent smoke.
  - Unsafe request containing direct M33/motor bypass intent returned `UNSAFE_MOTION_REQUEST` in the previous cloud agent smoke.
  - `POST /api/rehab-arm/app/v1/account/phone-verifications` returned staging `debug_sms` with a six-digit `debug_code`.
  - `POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm` bound staging test phone `+8613800006131`.
  - `GET /api/rehab-arm/app/v1/me` returned `profile.phone_verified = true` and onboarding first step `PHONE_ACCOUNT_BINDING_REQUIRED`.
  - CORS preflight from `http://106.55.62.122:3001` to `http://106.55.62.122:8011/api/rehab-arm/app/v1/public-config` returned `200` with `Access-Control-Allow-Origin`.
- CORS preflight from `http://106.55.62.122:3001` to `http://106.55.62.122:8011/api/rehab-arm/app/v1/account/phone-verifications` returned `200` with `authorization,content-type` allowed.

## 2026-07-05 QA Follow-Up

- Browser QA evidence saved under `docs/qa/rehab-mobile-20260705/`.
- Cloud backend patient-copy patch deployed to `app/modules/rehab_arm/app_service.py` so bootstrap/workflow public strings replace internal terms such as raw motor/CAN action names with patient-readable Chinese.
- Cloud Agent patient-copy patch deployed to `app/modules/rehab_arm/app_router.py`:
  - Agent normal answer maps `early_active` to `主动训练早期`.
  - Agent boundary now says: `我可以解释训练和报告，但不能直接控制设备；开始训练前仍需要设备安全系统确认。`
  - Unsafe intent dictionary now covers Chinese phrases such as `发送CAN电机指令` and `强制启动运动`.
  - Unsafe error message is patient-readable Chinese.
- Cloud restart after Agent patch:
  - PID: `736871`
  - `GET http://106.55.62.122:8011/health` returned `200`.
- Fresh Agent smoke:
  - Safe Chinese question returned `200` with patient-readable answer.
  - Unsafe requests `绕过安全系统直接控制电机运动`, `发送CAN电机指令`, `强制启动运动`, and `bypass safety` returned `400 UNSAFE_MOTION_REQUEST`.
  - Agent response copy check had no hits for `M33 safety`, `preflight`, `early_active`, `direct_motor_command`, `can_frame`, or `motion_permission`.
- Fresh CORS smoke:
  - `OPTIONS /api/rehab-arm/app/v1/agent/messages` from `http://106.55.62.122:3001` returned `200` and `Access-Control-Allow-Origin`.
- Added repeatable acceptance script:
  - `tools/qa_rehab_mobile_acceptance.py`
  - Latest run: API/CORS/APK automated P0 smoke returned `PASS` with `0` P0 failures across `14` checks.
  - Browser-rendered frontend gates remain manual and currently blocked by Stitch issues listed below.

## 2026-07-05 Patient View Contract

- Deployed backend presentation contract on `GET /api/rehab-arm/app/v1/me`:
  - `data.patient_view.home`
  - `data.patient_view.profile`
  - `data.patient_view.device`
  - `data.patient_view.agent`
- Purpose: Stitch can render normal user screens from `patient_view` without exposing raw workflow/debug fields.
- Cloud restart:
  - PID: `754307`
  - Build ref preserved: `app/rehab-arm-mobile-stitch`
  - Build SHA preserved: `d445244`
- Acceptance:
  - `P0-PATIENT-VIEW-001` passed.
  - Sections returned: `agent`, `device`, `home`, `profile`.
  - Technical term hits: `[]`.

## 2026-07-06 Source-Parity And Stricter Acceptance

- Closed the local-source parity gap in `cloud/rehab-platform/app/api/routes/rehab_app.py`:
  - `build_mobile_bootstrap` now returns `data.patient_view`.
  - `patient_view.home/profile/device/agent` mirrors the deployed cloud contract shape for Stitch.
  - Patient view maps internal terms such as `early_active`, `left`, and hardware/debug words into patient-facing Chinese.
- Added local regression test:
  - `cloud/rehab-platform/tests/test_app_compat.py::test_mobile_bootstrap_includes_patient_view_without_raw_debug_terms`
  - Verified RED first: failed with missing `patient_view`.
  - Verified GREEN: focused test passed.
- Expanded `tools/qa_rehab_mobile_acceptance.py`:
  - `P0-PATIENT-VIEW-001` now checks Agent endpoint, Agent entry label, home primary action, device binding first step, profile phone label, and raw technical terms.
- Local verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest -q` -> `22 passed, 1 warning`.
  - `py_compile` passed for backend route and QA script.
- Cloud verification after stricter acceptance:
  - `overall = PASS`
  - `p0_failed = 0`
  - `total = 14`
  - Cloud PID: `758739`
  - Build SHA: `b6eac26`
  - APK still reachable with `Content-Length: 4198462` and APK content type.
- No cloud restart was performed in this follow-up because the live service already contained the patient-view contract and passed the stricter acceptance check.

## Frontend QA Blockers For Stitch

- Home still renders raw workflow/debug strings such as `setup_required`, `direct_motor_command`, `can_frame_send`, `m33_safety_override`, `motion_permission_granted_by_app`, and `M33`.
- The top `smart_toy` icon is labelled as Settings and did not open an Agent chat.
- `配对新设备` routes normal users to `bluetooth-debug.html`, which exposes UUID/SPP/CAN/debug transport details.
- Profile mixes home workflow content above the rehab profile and uses risky demo-style medical constraint copy.
- Stitch handoff prompt: `docs/stitch/rehab-mobile-qa-fixes-20260705-prompt.md`

## 2026-07-06 Agent Cloud Model Status

- Local backend source now supports an OpenAI-compatible rehab therapist Agent call:
  - Configure with `AGENT_MODEL_PROVIDER`, `AGENT_MODEL_BASE_URL`, `AGENT_MODEL_NAME`, `AGENT_MODEL_API_KEY`, timeout, temperature, and max-token settings.
  - `POST /api/rehab-arm/app/v1/agent/messages` returns `data.model_status` for every safe answer.
  - `model_status.mode = cloud_model` means the configured cloud model answered.
  - `model_status.mode = fallback_rule_based` means the safe local fallback answered.
  - Unsafe direct-control and safety-bypass requests still return `400 UNSAFE_MOTION_REQUEST`.
- Cloud patch deployed to `ubuntu@106.55.62.122:/home/ubuntu/apps/ai-collab/apps/api/app/modules/rehab_arm/app_router.py`.
- Cloud backup created at `app/modules/rehab_arm/app_router.py.bak-agent-model-status-20260706`.
- Cloud restart:
  - PID: `1409766`
  - Explicit database URL: `sqlite:///./ai_collab_server.db`
  - Build SHA label: `agent-model-status-20260706`
  - Build ref: `codex/rehab-mobile-backend-qa-20260706`
  - Build time: `2026-07-06T03:13:48Z`
  - API: `http://106.55.62.122:8011`
- Fresh local verification before deploy:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests -q` -> `25 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py -q` -> `2 passed`
  - `py_compile` passed for Agent config/service/router and QA script.
- Fresh cloud acceptance after deploy:
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 14`
  - `P0-AGENT-001` now checks `data.model_status`.
  - Current cloud model status: `fallback_rule_based`, `fallback_reason = external_model_not_configured`.
  - APK remains reachable: `Content-Length: 4198462`, content type `application/vnd.android.package-archive`.

## 2026-07-06 Phone Verification Hardening

- Local backend phone verification now supports:
  - `PHONE_VERIFICATION_DEBUG_CODE_ENABLED`
  - `PHONE_VERIFICATION_TTL_SECONDS`
  - `PHONE_VERIFICATION_MAX_ATTEMPTS`
- Production-like mode can hide `debug_code` while staging keeps `debug_sms` for automated QA.
- Wrong-code attempts now stop with `PHONE_CODE_ATTEMPTS_EXCEEDED` after the configured limit.
- Acceptance smoke now includes `P0-PHONE-FLOW-001`, which requests and confirms a staging code end to end.
- Cloud patch deployed to:
  - `app/settings.py`
  - `app/modules/rehab_arm/app_service.py`
- Cloud backups created:
  - `app/settings.py.bak-phone-hardening-20260706`
  - `app/modules/rehab_arm/app_service.py.bak-phone-hardening-20260706`
- Cloud restart:
  - PID: `1429532`
  - Explicit database URL: `sqlite:///./ai_collab_server.db`
  - Build SHA label: `phone-verification-hardening-20260706`
  - Build ref: `codex/rehab-mobile-backend-qa-20260706`
  - Build time: `2026-07-06T03:33:43Z`
- Fresh verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests tools\test_qa_rehab_mobile_acceptance.py tools\test_qa_rehab_mobile_l1_frontend.py tools\test_qa_rehab_mobile_l1_release.py -q` -> `35 passed, 1 warning`
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 15`
  - `P0-PHONE-FLOW-001` -> `PASS`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
  - APK remains reachable: `Content-Length: 4198462`, content type `application/vnd.android.package-archive`.

## 2026-07-06 Device Binding Hardening

- Local backend device binding now enforces hardware ownership by `m33_device_id`:
  - the same account can re-bind the same device idempotently and update metadata,
  - another account receives `409 DEVICE_ALREADY_BOUND` for an already-owned hardware ID.
- Acceptance smoke now includes `P0-DEVICE-FLOW-001`, which binds `QA-REHAB-ARM-STAGING-001` and repeats the bind to verify the same device record is reused.
- Cloud patch deployed to:
  - `app/modules/rehab_arm/app_service.py`
- Cloud backup created:
  - `app/modules/rehab_arm/app_service.py.bak-device-binding-20260706`
- Cloud restart:
  - PID: `1449627`
  - Explicit database URL: `sqlite:///./ai_collab_server.db`
  - Build SHA label: `device-binding-hardening-20260706`
  - Build ref: `codex/rehab-mobile-backend-qa-20260706`
  - Build time: `2026-07-06T03:54:50Z`
- Fresh verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests\test_devices.py -q` -> `5 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py -q` -> `6 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests\test_devices.py tools\test_qa_rehab_mobile_acceptance.py -q` -> `11 passed, 1 warning`
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 16`
  - `P0-DEVICE-FLOW-001` -> `PASS`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
  - Browser QA at `390 x 844` captured `docs/qa/rehab-mobile-20260706/screenshots/device-binding-*.png`; frontend still shows false network/error workflow text and raw hardware/debug vocabulary.
  - APK remains reachable: `Content-Length: 4198462`, content type `application/vnd.android.package-archive`.

## 2026-07-06 Device Already-Bound QA Gate

- Added acceptance coverage for the user-facing already-bound device state:
  - `P0-DEVICE-CONFLICT-001`
  - The script prepares a second QA account through `/api/auth/session` and `/api/auth/register` when needed.
  - Primary account binds `QA-REHAB-ARM-CONFLICT-001`.
  - Second account attempts to bind the same hardware ID and must receive `409 DEVICE_ALREADY_BOUND`.
- No new cloud code deployment was required in this follow-up; the deployed `device-binding-hardening-20260706` backend already enforced the conflict.
- Fresh verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py -q` -> `8 passed`
  - `py_compile` passed for `tools\qa_rehab_mobile_acceptance.py`
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 17`
  - `P0-DEVICE-CONFLICT-001` -> `PASS`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
  - Repeated run reused the second QA account login and still returned `409 DEVICE_ALREADY_BOUND`.
  - APK remains reachable: `Content-Length: 4198462`, content type `application/vnd.android.package-archive`.

## 2026-07-06 Agent Model Readiness Gate

- Added acceptance visibility for whether the rehab therapist Agent is backed by a configured external cloud model:
  - `P1-AGENT-MODEL-001`
- Current cloud runtime has no external model credentials configured:
  - `REHAB_ARM_MODEL_RELAY_API_KEY`: unset
  - `AGENT_MODEL_API_KEY`: unset
  - `OPENAI_API_KEY`: unset
- No new cloud code deployment was required; the deployed Agent already returns `data.model_status`.
- Fresh verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py -q` -> `10 passed`
  - `py_compile` passed for `tools\qa_rehab_mobile_acceptance.py`
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 18`
  - `P1-AGENT-MODEL-001` -> `WARN`, mode `fallback_rule_based`, reason `external_model_not_configured`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
- In-app browser plugin attempt: the Codex in-app browser backend was listed, but selected-tab and tab-list reads timed out, so no new rendered screenshot could be captured for this gate.

## 2026-07-06 Phone SMS Delivery Readiness Gate

- Added public runtime visibility for phone verification delivery readiness:
  - `GET /api/rehab-arm/app/v1/public-config`
  - `data.phone_verification.delivery_status`
  - Acceptance gate `P1-PHONE-SMS-001`
- Local source updates:
  - `cloud/rehab-platform/app/core/config.py`
  - `cloud/rehab-platform/app/api/routes/rehab_app.py`
  - `tools/qa_rehab_mobile_acceptance.py`
- Cloud patch deployed to:
  - `app/settings.py`
  - `app/modules/rehab_arm/app_router.py`
- Cloud backups created:
  - `app/settings.py.bak-sms-readiness-20260706`
  - `app/modules/rehab_arm/app_router.py.bak-sms-readiness-20260706`
- Cloud restart:
  - PID: `1605495`
  - Explicit database URL: `sqlite:///./ai_collab_server.db`
  - API: `http://106.55.62.122:8011`
- Current staging result:
  - `P1-PHONE-SMS-001` -> `WARN`
  - mode `debug_sms`
  - reason `debug_code_enabled`
- Fresh verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests tools\test_qa_rehab_mobile_acceptance.py tools\test_qa_rehab_mobile_l1_frontend.py tools\test_qa_rehab_mobile_l1_release.py -q` -> `46 passed, 1 warning`
  - Local `py_compile` passed for config/router/QA files
  - Remote `.venv/bin/python -m py_compile app/settings.py app/modules/rehab_arm/app_router.py` passed
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 19`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
  - Browser QA captured `docs/qa/rehab-mobile-20260706/screenshots/sms-readiness-device-390.png`; frontend still shows false network/debug workflow copy.
  - APK remained reachable with size `4198462` bytes and content type `application/vnd.android.package-archive`

## 2026-07-06 Phone SMS Webhook Delivery

- Added the backend delivery handoff for real SMS providers:
  - Local route: `cloud/rehab-platform/app/api/routes/rehab_app.py`
  - Local tests: `cloud/rehab-platform/tests/test_phone_binding.py`
- Behavior:
  - Debug SMS enabled: staging keeps returning `delivery_channel = debug_sms` with a test code.
  - Debug SMS disabled plus webhook configured: backend POSTs the code payload to the webhook and returns `delivery_channel = sms` without `debug_code`.
  - Debug SMS disabled plus no provider: backend returns `503 PHONE_SMS_NOT_CONFIGURED`.
  - Webhook failure: backend returns `502 PHONE_SMS_DELIVERY_FAILED`.
- Cloud patch deployed to:
  - `app/modules/rehab_arm/app_service.py`
- Cloud backup created:
  - `app/modules/rehab_arm/app_service.py.bak-sms-webhook-20260706`
- Cloud restart:
  - PID: `1620444`
  - API: `http://106.55.62.122:8011`
- Current staging result:
  - `P1-PHONE-SMS-001` -> `WARN`
  - mode `debug_sms`
  - reason `debug_code_enabled`
- Fresh verification:
  - Red backend tests first showed missing webhook delivery behavior and missing `PHONE_SMS_NOT_CONFIGURED`.
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests\test_phone_binding.py -q` -> `8 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests tools\test_qa_rehab_mobile_acceptance.py tools\test_qa_rehab_mobile_l1_frontend.py tools\test_qa_rehab_mobile_l1_release.py -q` -> `48 passed, 1 warning`
  - Remote `.venv/bin/python -m py_compile app/modules/rehab_arm/app_service.py` passed.
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 19`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
  - Browser QA captured `docs/qa/rehab-mobile-20260706/screenshots/sms-webhook-device-390.png`.
  - APK remained reachable with size `4198462` bytes and content type `application/vnd.android.package-archive`.

## Browser QA

- Previous browser QA after the CORS fix confirmed the cloud page could log in and show synced workflow/timeline state.
- 2026-07-05 phone-binding follow-up: in-app browser control bridge repeatedly timed out while reading the selected tab, so visual browser QA could not be completed in this pass.
- Backend public smoke and cloud API contract checks passed.

## Install Package

- Verified existing installable APK:
  - URL: `http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk`
  - Size: `4,198,462 bytes`
  - SHA256: `DB674D09F46D0CF0B8DE9717D1904A52CE042BC19E49FB1BEB45BC4548E9BB52`
- Cloud Android build refresh was not possible on the server because Gradle/Java/Android SDK are not installed there.
- Public-config still points to APK version `1.0.10`.

## Notes

- The frontend was not edited directly.
- General Stitch backend handoff prompt: `docs/stitch/rehab-backend-contract-v1-prompt.md`
- Phone-binding Stitch handoff prompt: `docs/stitch/rehab-phone-binding-stitch-prompt.md`
- Safety boundary remains: the App and cloud provide education, planning, evidence, and transport frames only; M33 remains final motion authority.
