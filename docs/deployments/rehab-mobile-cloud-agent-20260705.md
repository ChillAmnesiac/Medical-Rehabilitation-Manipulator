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

## 2026-07-06 Phone Verification Resend Cooldown

- Added resend throttling for phone verification:
  - Local setting: `PHONE_VERIFICATION_RESEND_COOLDOWN_SECONDS`
  - Cloud setting: `rehab_arm_phone_verification_resend_cooldown_seconds`
  - Default: `60` seconds
- Behavior:
  - First code request for a user/phone/purpose is allowed.
  - An immediate repeat request returns `429 PHONE_CODE_RESEND_TOO_SOON`.
  - Local error payload preserves `retry_after`; cloud error payload exposes `error.details.retry_after`.
  - `GET /api/rehab-arm/app/v1/public-config` exposes `data.phone_verification.resend_cooldown_seconds`.
- Acceptance gate added:
  - `P1-PHONE-RESEND-001`
- Cloud patch deployed to:
  - `app/settings.py`
  - `app/modules/rehab_arm/app_router.py`
  - `app/modules/rehab_arm/app_service.py`
- Cloud backups created:
  - `app/settings.py.bak-phone-cooldown-20260706`
  - `app/modules/rehab_arm/app_router.py.bak-phone-cooldown-20260706`
  - `app/modules/rehab_arm/app_service.py.bak-phone-cooldown-20260706`
- Cloud restart:
  - PID: `1639678`
  - API: `http://106.55.62.122:8011`
  - Database URL: `sqlite:///./ai_collab_server.db`
- Fresh verification:
  - Red backend test first showed immediate resend still returned `200`.
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests\test_phone_binding.py -q` -> `9 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py -q` -> `14 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests tools\test_qa_rehab_mobile_acceptance.py tools\test_qa_rehab_mobile_l1_frontend.py tools\test_qa_rehab_mobile_l1_release.py -q` -> `51 passed, 1 warning`
  - Remote `.venv/bin/python -m py_compile app/settings.py app/modules/rehab_arm/app_router.py app/modules/rehab_arm/app_service.py` passed.
  - Cloud public-config returned `resend_cooldown_seconds: 60`.
  - Manual cloud smoke returned `429 PHONE_CODE_RESEND_TOO_SOON` with `retry_after` on immediate resend.
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 20`
  - `P1-PHONE-RESEND-001` -> `PASS`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
  - Browser QA captured `docs/qa/rehab-mobile-20260706/screenshots/phone-cooldown-profile-390.png`.
  - APK remained reachable with size `4198462` bytes and content type `application/vnd.android.package-archive`.

## 2026-07-06 Agent Public Config Readiness

- Added public Agent readiness to the unauthenticated boot contract:
  - `GET /api/rehab-arm/app/v1/public-config`
  - `data.agent.message_endpoint`
  - `data.agent.model_readiness`
- Local behavior:
  - `cloud_model_configured` only when backend model base URL, API key, and model name are configured.
  - `fallback_rule_based` when the cloud model is not configured.
  - API keys are never returned in public config.
- Acceptance gate added:
  - `P1-AGENT-CONFIG-001`
- Cloud patch deployed to:
  - `app/modules/rehab_arm/app_router.py`
- Cloud backup created:
  - `app/modules/rehab_arm/app_router.py.bak-agent-readiness-20260706`
- Cloud restart:
  - PID: `1666259`
  - API: `http://106.55.62.122:8011`
  - Database URL: `sqlite:///./ai_collab_server.db`
- Fresh verification:
  - Red backend test first failed with missing `data.agent`.
  - Red acceptance helper tests first failed because `agent_public_config_readiness` was missing.
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests\test_agent.py::test_public_config_exposes_agent_model_readiness_without_secret -q` -> `1 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py::test_agent_public_config_readiness_reports_cloud_model_ready tools\test_qa_rehab_mobile_acceptance.py::test_agent_public_config_readiness_warns_on_fallback_config -q` -> `2 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud/rehab-platform/tests tools/test_qa_rehab_mobile_acceptance.py tools/test_qa_rehab_mobile_l1_frontend.py -q` -> `54 passed, 1 warning`
  - Remote `.venv/bin/python -m py_compile app/modules/rehab_arm/app_router.py app/settings.py` passed.
  - Cloud public-config returned `data.agent.model_readiness.mode = fallback_rule_based`, reason `external_model_not_configured`.
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 21`
  - `P1-AGENT-CONFIG-001` -> `WARN`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
  - Browser QA captured `docs/qa/rehab-mobile-20260706/screenshots/agent-readiness-ai-plan-390.png`.
  - APK remained reachable with size `4198462` bytes and content type `application/vnd.android.package-archive`.

## 2026-07-06 Deployment Metadata Gate

- Added traceable deployment metadata to the local FastAPI health response:
  - `GET /health`
  - `data.deployment.build_sha`
  - `data.deployment.build_ref`
  - `data.deployment.build_time`
  - `data.deployment.app_env`
- Added acceptance visibility:
  - `P1-DEPLOY-META-001`
- Fixed automated phone-flow QA to use a generated default staging phone number when no explicit phone is supplied, so repeated acceptance runs do not fail because of the resend cooldown from a prior run.
- Cloud restart:
  - PID: `1677646`
  - API: `http://106.55.62.122:8011`
  - Database URL: `sqlite:///./ai_collab_server.db`
  - `APP_ENV=staging`
  - `AI_COLLAB_BUILD_SHA=b925e316`
  - `AI_COLLAB_BUILD_REF=codex/rehab-mobile-backend-qa-20260706`
  - `AI_COLLAB_BUILD_TIME=2026-07-06T07:50:07Z`
- Fresh verification:
  - Red health test first failed because `data.deployment` was missing.
  - Red acceptance helper tests first failed because `deployment_metadata_readiness` was missing.
  - Red generated-phone test first failed because `default_phone_test_phone` was missing.
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests\test_health.py::test_health_exposes_deployment_metadata -q` -> `1 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py::test_deployment_metadata_readiness_reports_traceable_build tools\test_qa_rehab_mobile_acceptance.py::test_deployment_metadata_readiness_warns_on_unknown_build -q` -> `2 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py::test_phone_verification_default_phone_is_generated_for_each_acceptance_run -q` -> `1 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud/rehab-platform/tests tools/test_qa_rehab_mobile_acceptance.py tools/test_qa_rehab_mobile_l1_frontend.py tools/test_qa_rehab_mobile_l1_release.py -q` -> `60 passed, 1 warning`
  - Cloud health returned build SHA `b925e316`, ref `codex/rehab-mobile-backend-qa-20260706`, build time `2026-07-06T07:50:07Z`, and `app_env=staging`.
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 22`
  - `P1-DEPLOY-META-001` -> `PASS`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blocker `frontend_l1_gate`
  - APK remained reachable with size `4198462` bytes and content type `application/vnd.android.package-archive`.
- In-app browser QA attempt for this metadata-only backend deployment reached the browser but screenshot capture timed out; no new screenshot was accepted for this pass.

## 2026-07-06 Agent Draft Patient Copy

- Removed user-visible engineering vocabulary from AI training draft copy:
  - local `cloud/rehab-platform/app/services/agent.py` returns Chinese patient-facing title/goal/risk notes;
  - cloud `app/modules/rehab_arm/app_service.py` no longer exposes `M33`, `preflight`, or `m33_accepted` in AI draft risk notes and timeline copy touched by this pass.
- Cloud patch deployed to:
  - `app/modules/rehab_arm/app_service.py`
- Cloud backup created:
  - `app/modules/rehab_arm/app_service.py.bak-agent-draft-copy-20260706`
- Cloud restart:
  - PID: `1916595`
  - API: `http://106.55.62.122:8011`
  - Database URL: `sqlite:///./ai_collab_server.db`
  - `APP_ENV=staging`
  - `AI_COLLAB_BUILD_SHA=8e17a51d`
  - `AI_COLLAB_BUILD_REF=codex/rehab-mobile-backend-qa-20260706`
  - `AI_COLLAB_BUILD_TIME=2026-07-06T11:59:30Z`
- Fresh verification:
  - Red regression first showed `AI rehab draft` and `M33 safety acceptance and preflight`.
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests\test_agent.py::test_ai_training_draft_uses_profile_and_recent_session_context -q` -> `1 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud\rehab-platform\tests\test_agent.py -q` -> `8 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_acceptance.py tools\test_qa_rehab_mobile_l1_release.py -q` -> `22 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud/rehab-platform/tests tools/test_qa_rehab_mobile_acceptance.py tools/test_qa_rehab_mobile_l1_frontend.py tools/test_qa_rehab_mobile_l1_release.py tools/test_export_rehab_mobile_stitch_fixture.py -q` -> `66 passed, 1 warning`
  - Remote `.venv/bin/python -m py_compile app/modules/rehab_arm/app_service.py` passed.
  - Cloud AI draft smoke returned risk notes with no `M33`, `preflight`, `m33_accepted`, `CAN`, or `Stop`.
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 22`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`
  - APK remained reachable with size `4198462` bytes and content type `application/vnd.android.package-archive`.

## 2026-07-06 Agent Model Relay Ops Tooling

- Investigated the live cloud `agent_cloud_model` blocker.
- Current server model relay env is empty for `REHAB_ARM_MODEL_RELAY_PROVIDER`, `REHAB_ARM_MODEL_RELAY_BASE_URL`, `REHAB_ARM_MODEL_RELAY_MODEL`, and `REHAB_ARM_MODEL_RELAY_API_KEY`; `REHAB_ARM_MODEL_RELAY_EXTERNAL_ENABLED=false`.
- XiaoZhi ASR/TTS model relay fallback keys are also empty, so the staging server cannot call a real model until a provider endpoint/key is configured.
- Added local ops tool:
  - `tools/configure_rehab_model_relay.py`
- Added tests:
  - `tools/test_configure_rehab_model_relay.py`
- Added runbook:
  - `docs/deployments/rehab-mobile-agent-model-relay-runbook-20260706.md`
- Fresh verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools/test_configure_rehab_model_relay.py -q` -> `5 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud/rehab-platform/tests tools/test_qa_rehab_mobile_acceptance.py tools/test_qa_rehab_mobile_l1_frontend.py tools/test_qa_rehab_mobile_l1_release.py tools/test_export_rehab_mobile_stitch_fixture.py tools/test_configure_rehab_model_relay.py -q` -> `71 passed, 1 warning`
  - `cloud\rehab-platform\.venv\Scripts\python.exe tools\configure_rehab_model_relay.py --project-id e201f41c-25a6-46e1-baf8-be6dcb83284c --email 3245056131@qq.com --password 1234 --base-url https://model.example/v1 --model rehab-cloud-model` -> `{"error": "api_key is required"}`
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 22`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`
  - APK HEAD -> `200`, size `4198462`, content type `application/vnd.android.package-archive`
  - Browser QA screenshot: `docs/qa/rehab-mobile-20260706/screenshots/model-relay-ops-device-390.png`
- No cloud runtime deployment was made for this ops-only change.
- L1 remains blocked until a real model key is configured and the Agent smoke reports `data.model_status.mode = cloud_model`.

## 2026-07-06 Stitch Fixture V3 Handoff

- Confirmed Codex has no callable Google Stitch MCP tool or installable Stitch plugin in this environment.
- Refreshed the sanitized live API fixture:
  - `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json`
- The fixture now includes phone verification examples:
  - `phone_verification.start_response`
  - `phone_verification.confirm_response`
- `verification_id` is preserved as `fixture-verification-id`; `debug_code`, tokens, raw ids, real email, and real phone values remain removed or masked.
- Added primary frontend handoff prompt:
  - `docs/stitch/rehab-mobile-l1-stitch-execution-v3-20260706.md`
- Updated the Stitch runbook to point to V3.
- Fresh verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools/test_export_rehab_mobile_stitch_fixture.py tools/test_configure_rehab_model_relay.py tools/test_qa_rehab_mobile_acceptance.py tools/test_qa_rehab_mobile_l1_release.py -q` -> `30 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud/rehab-platform/tests tools/test_qa_rehab_mobile_acceptance.py tools/test_qa_rehab_mobile_l1_frontend.py tools/test_qa_rehab_mobile_l1_release.py tools/test_export_rehab_mobile_stitch_fixture.py tools/test_configure_rehab_model_relay.py -q` -> `71 passed, 1 warning`
  - Fixture safety check passed for masked `verification_id`, phone verification start/confirm examples, and no real QA email/token/debug code/raw verification id.
  - `tools\qa_rehab_mobile_acceptance.py` -> `overall = PASS`, `p0_failed = 0`, `total = 22`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`
  - APK HEAD -> `200`, size `4198462`, content type `application/vnd.android.package-archive`
- No cloud runtime deployment was made for this frontend-handoff/QA artifact change.

## 2026-07-06 Frontend L1 Integration Gate Hardening

- Tightened `tools/qa_rehab_mobile_l1_frontend.py` so `L1-FRONTEND-INTEGRATION-001` requires evidence for:
  - Bearer auth token propagation
  - Ask Therapist accessible label
  - phone resend cooldown and SMS error states
  - already-bound device conflict handling
  - unsafe Agent refusal handling
  - Agent model-status rendering
- Added regression coverage in `tools/test_qa_rehab_mobile_l1_frontend.py`.
- Updated Stitch V3 prompt with the stricter missing-requirement list.
- Fresh verification:
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools/test_qa_rehab_mobile_l1_frontend.py tools/test_qa_rehab_mobile_l1_release.py -q` -> `10 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud/rehab-platform/tests tools/test_qa_rehab_mobile_acceptance.py tools/test_qa_rehab_mobile_l1_frontend.py tools/test_qa_rehab_mobile_l1_release.py tools/test_export_rehab_mobile_stitch_fixture.py tools/test_configure_rehab_model_relay.py -q` -> `72 passed, 1 warning`
  - `tools\qa_rehab_mobile_l1_release.py` -> API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`
  - APK HEAD -> `200`, size `4198462`, content type `application/vnd.android.package-archive`
- No cloud runtime deployment was made for this QA-gate-only change.

## 2026-07-06 Objective-Level L1 Audit

- Added goal-level audit script:
  - `tools/qa_rehab_mobile_l1_objective_audit.py`
- Added tests:
  - `tools/test_qa_rehab_mobile_l1_objective_audit.py`
- The audit maps the combined release payload plus screenshot evidence to the user-facing L1 objective:
  - cloud deployment
  - login
  - home next step
  - phone binding
  - device binding
  - Ask Therapist safety
  - Agent cloud model
  - profile without fake/debug data
  - APK delivery
  - browser QA evidence
  - combined release gate
- Fresh live result:
  - `tools\qa_rehab_mobile_l1_objective_audit.py` -> `FAIL`, `8 / 11` objective requirements failing.
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools/test_qa_rehab_mobile_l1_objective_audit.py tools/test_qa_rehab_mobile_l1_release.py tools/test_qa_rehab_mobile_l1_frontend.py -q` -> `13 passed`
  - `cloud\rehab-platform\.venv\Scripts\python.exe -m pytest cloud/rehab-platform/tests tools/test_qa_rehab_mobile_acceptance.py tools/test_qa_rehab_mobile_l1_frontend.py tools/test_qa_rehab_mobile_l1_release.py tools/test_export_rehab_mobile_stitch_fixture.py tools/test_configure_rehab_model_relay.py tools/test_qa_rehab_mobile_l1_objective_audit.py -q` -> `75 passed, 1 warning`
  - APK HEAD -> `200`, size `4198462`, content type `application/vnd.android.package-archive`
  - Passing objective requirements: `cloud_deployment`, `login`, `apk_delivery`.
  - Browser evidence still lacks Ask Therapist chat, unsafe refusal, and device wizard screenshots.
- No cloud runtime deployment was made for this QA-audit-only change.

## 2026-07-06 Stitch Repair Packet Export

- Added a machine-readable Stitch repair packet exporter:
  - `tools/export_rehab_mobile_stitch_repair_packet.py`
- Added tests:
  - `tools/test_export_rehab_mobile_stitch_repair_packet.py`
- Generated live repair packet:
  - `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`
- The packet is built from the live cloud L1 release gate and objective audit.
- It separates:
  - Stitch blockers: frontend/user-flow requirements and browser evidence.
  - Non-Stitch blockers: currently `agent_cloud_model`.
  - Meta blockers: currently `combined_l1_release`.
- It exports the current `5` frontend failures and `13` frontend integration gaps for Stitch.
- Fresh verification:
  - Red test first showed `combined_l1_release` was wrongly grouped with Stitch blockers.
  - Focused repair-packet tests after implementation: `2 passed`.
  - Related repair/objective/release/frontend tests: `15 passed`.
  - Full local backend plus QA suite: `77 passed, 1 warning`.
  - Live L1 release gate remained `FAIL` with API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
  - Live objective audit remained `FAIL` with `8 / 11` requirements failing.
  - Live packet JSON parse check passed.
  - APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## 2026-07-06 Browser Evidence Dimension Gate

- Tightened objective-level browser evidence validation:
  - `tools/qa_rehab_mobile_l1_objective_audit.py`
  - `tools/test_qa_rehab_mobile_l1_objective_audit.py`
- Browser screenshot evidence must now decode to exactly `390 x 844`.
- The validator supports PNG and JPEG headers, because current in-app browser captures may be JPEG bytes saved with `.png` filenames.
- Updated the Stitch repair packet exporter so `browser_evidence_current` includes matched screenshots, missing scenes, invalid dimensions, and expected dimensions.
- Refreshed:
  - `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`
  - `docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md`
  - `docs/qa/rehab-mobile-20260706/APP_COMPLETION_SCORECARD.md`
  - `docs/qa/rehab-mobile-20260706/QA_REPORT.md`
- Fresh verification:
  - Red objective-audit test first showed wrong-size screenshots were accepted.
  - Red repair-packet test first showed current browser evidence details were not exported.
  - Follow-up red objective-audit test first showed `current-fail-*` screenshots could be counted as L1 success evidence before exact filename matching was added.
  - Focused objective-audit and repair-packet tests: `8 passed`.
  - Full local backend plus QA suite: `80 passed, 1 warning`.
  - Live L1 release gate remained `FAIL` with API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
  - Live objective audit remained `FAIL` and now reports all five exact L1 success screenshots missing.
  - APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## 2026-07-06 In-App Browser Current-Fail Screenshots

- Captured current deployed frontend failure evidence from the in-app browser at explicit `390 x 844` viewport:
  - `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/current-fail-home-clip-390x844.png`
  - `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/current-fail-ai-plan-clip-390x844.png`
  - `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/current-fail-device-clip2-390x844.png`
  - `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/current-fail-profile-clip2-390x844.png`
- All four accepted current-fail screenshots decode to `390 x 844`.
- Fresh final verification after browser QA capture:
  - Focused objective-audit and repair-packet tests: `8 passed`.
  - Full local backend plus QA suite: `80 passed, 1 warning`.
  - Live L1 release gate remained `FAIL` with API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
  - Live objective audit remained `FAIL` with all five exact L1 success screenshots missing.
  - APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- They are intentionally stored outside the L1 success screenshot directory and named `current-fail-*`, so they cannot satisfy objective-audit success evidence.
- The refreshed repair packet now reports `browser_evidence_current.matched = {}` and all five required L1 success screenshots missing.
- No cloud runtime deployment was made for this browser-QA evidence-only change.

## 2026-07-06 Repair Packet Current-Fail Evidence

- Updated `tools/export_rehab_mobile_stitch_repair_packet.py` so the live repair packet includes `current_fail_evidence`.
- The field lists the current in-app browser failure screenshots for:
  - `home`
  - `ai-plan`
  - `device`
  - `profile`
- Each entry includes the screenshot path, decoded dimensions, and `counts_for_l1_success = false`.
- Refreshed `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`.
- Fresh verification:
  - Red test first showed `current_fail_dir` was unsupported.
  - Focused objective-audit and repair-packet tests: `9 passed`.
  - Full local backend plus QA suite: `81 passed, 1 warning`.
  - Live L1 release gate remained `FAIL` with API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
  - Live objective audit remained `FAIL` with `8 / 11` failing, including all five exact L1 success screenshots missing.
  - APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
  - Live repair packet JSON parse confirmed all four current-fail screenshots are listed at `390 x 844`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## 2026-07-06 Stitch Prompt V4 Export

- Added a generated Stitch prompt exporter:
  - `tools/export_rehab_mobile_stitch_prompt.py`
  - `tools/test_export_rehab_mobile_stitch_prompt.py`
- Generated the current primary Stitch handoff:
  - `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md`
- Updated the repair packet default artifact so `required_artifacts.stitch_prompt` points to V4 instead of V3.
- Refreshed:
  - `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`
  - `docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md`
  - `docs/qa/rehab-mobile-20260706/APP_COMPLETION_SCORECARD.md`
  - `docs/qa/rehab-mobile-20260706/QA_REPORT.md`
- The V4 prompt carries the current-fail browser evidence, exact L1 success screenshot filenames, Stitch blockers, and the non-Stitch `agent_cloud_model` blocker.
- Focused repair-packet/prompt tests: `5 passed`.
- Full local backend plus QA suite: `83 passed, 1 warning`.
- Live L1 release gate remained `FAIL` with API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remained `FAIL` with `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## 2026-07-06 Frontend Release Bundle Tool

- Added a local packaging tool for Stitch output:
  - `tools/prepare_rehab_mobile_frontend_release.py`
  - `tools/test_prepare_rehab_mobile_frontend_release.py`
- The tool validates required frontend pages before deployment:
  - `home.html`
  - `profile.html`
  - `device.html`
  - `ai-plan.html`
- It writes a deployable zip plus `rehab-mobile-frontend-release-manifest.json` containing the bundle SHA256, source file count, SSH copy commands, L1 release/objective commands, APK HEAD command, and required browser screenshot filenames.
- Updated the live repair packet and V4 Stitch prompt so the release bundle tool is part of the normal post-Stitch handoff.
- Focused release-bundle/repair-packet/prompt tests: `8 passed`.
- Full local backend plus QA suite: `86 passed, 1 warning`.
- Live L1 release gate remained `FAIL` with API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remained `FAIL` with `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## 2026-07-06 Frontend Local Preflight Gate

- Added local source support to the frontend L1 gate:
  - `tools/qa_rehab_mobile_l1_frontend.py --source-dir apps/web/public/rehab-arm-mobile`
  - `tools/test_qa_rehab_mobile_l1_frontend_local_source.py`
- The source-dir mode uses the same page copy and integration-contract checks as the deployed HTTP gate.
- Updated `tools/prepare_rehab_mobile_frontend_release.py` so a deployable frontend bundle is not written when the local L1 preflight fails.
- Added JSON evidence output:
  - `tools/qa_rehab_mobile_l1_frontend.py --output artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json`
  - release bundle manifest field `frontend_l1_preflight.report_path`
  - failed local preflights also write the JSON report for Stitch follow-up.
- Updated the V4 Stitch prompt and runbook so Codex runs the local gate before cloud copy.
- Focused local-source/preflight-report/release-bundle/prompt tests: `9 passed`.
- Full local backend plus QA suite after preserving preflight evidence: `90 passed, 1 warning`.
- Live L1 release gate remained `FAIL` with API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remained `FAIL` with `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

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
