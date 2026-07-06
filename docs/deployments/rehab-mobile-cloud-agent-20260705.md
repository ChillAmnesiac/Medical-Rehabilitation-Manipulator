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
