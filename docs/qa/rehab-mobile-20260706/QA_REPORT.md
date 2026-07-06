# Rehab Mobile QA Report - 2026-07-06

## Scope

- Target: `http://106.55.62.122:3001/rehab-arm-mobile/`
- API: `http://106.55.62.122:8011`
- Browser: Codex in-app browser, mobile viewport `390 x 844`
- Flow: home -> rehab therapist entry -> device -> profile
- Destination: local QA folder `docs/qa/rehab-mobile-20260706/`

## Verdict

The backend/API/package smoke is passing, but the complete app is still **not user-ready**.

The current deployed frontend does not consume the backend `data.patient_view` contract as the primary patient-facing model. A normal user still sees raw workflow state, device/debug vocabulary, a false network warning, non-working Agent entry points, and demo profile/medical content.

## Accepted Screenshots

1. `01-home-390-current.png` - Home first screen at 390px.
2. `02-agent-top-click-390.png` - Top Agent-like icon after click.
3. `03-agent-floating-click-390.png` - Floating Agent-like button after click.
4. `04-device-nav-390.png` - Device tab after navigation.
5. `05-profile-nav-390.png` - Profile tab after navigation.
6. `06-profile-resmoke-390.png` - Profile resmoke after git-managed backend QA commits.
7. `07-home-resmoke-390.png` - Home resmoke after git-managed backend QA commits.
8. `screenshots/device-binding-home-390.png` - Home browser QA after device-binding deployment.
9. `screenshots/device-binding-profile-390.png` - Profile browser QA after device-binding deployment.
10. `screenshots/device-binding-device-390.png` - Device browser QA after device-binding deployment.
11. `screenshots/device-binding-agent-390.png` - Agent browser QA after device-binding deployment.
12. `screenshots/sms-readiness-device-390.png` - Device page browser QA after SMS readiness deployment.
13. `screenshots/sms-webhook-device-390.png` - Device page browser QA after SMS webhook deployment.
14. `screenshots/phone-cooldown-profile-390.png` - Profile page browser QA after phone resend cooldown deployment.
15. `screenshots/agent-readiness-ai-plan-390.png` - Agent page browser QA after public Agent readiness deployment.
16. `screenshots/continuation-device-qa-20260706-390.png` - Device page continuation browser QA at the current cloud URL.

All screenshots were opened and inspected before being used as evidence. They show the deployed cloud app, not a blank page or wrong window.

## Step Review

| Step | What Was Checked | Health | Evidence |
| --- | --- | --- | --- |
| 1 | Home first screen after loading deployed cloud app | FAIL | `01-home-390-current.png` |
| 2 | Top icon that looks like Agent/assistant entry | FAIL | `02-agent-top-click-390.png` |
| 3 | Floating assistant button at lower right | FAIL | `03-agent-floating-click-390.png` |
| 4 | Device tab from bottom navigation | FAIL | `04-device-nav-390.png` |
| 5 | Profile tab from bottom navigation | FAIL | `05-profile-nav-390.png` |
| 6 | Profile resmoke on current production frontend | FAIL | `06-profile-resmoke-390.png` |
| 7 | Home resmoke on current production frontend | FAIL | `07-home-resmoke-390.png` |
| 8 | Device page after SMS readiness deployment | FAIL | `screenshots/sms-readiness-device-390.png` |
| 9 | Device page after SMS webhook deployment | FAIL | `screenshots/sms-webhook-device-390.png` |
| 10 | Profile page after phone resend cooldown deployment | FAIL | `screenshots/phone-cooldown-profile-390.png` |
| 11 | Agent page after public Agent readiness deployment | FAIL | `screenshots/agent-readiness-ai-plan-390.png` |
| 12 | Device page continuation resmoke on current production frontend | FAIL | `screenshots/continuation-device-qa-20260706-390.png` |

## 2026-07-06 L1 Resmoke

After committing backend/QA contract work, the deployed frontend was resmoked in the in-app browser at `390 x 844`.

Profile hit list:

- `M33`
- `避免过度伸展`
- `setup_required`
- `early_active`
- `网络未连接`

Home hit list:

- `网络未连接`
- `setup_required`
- `M33`
- `M55`
- `early_active`
- `left`
- `动作队列`
- `禁止`

Result: L1 remains `FAIL`. The backend contract is ready, but the frontend still needs Stitch changes.

## 2026-07-06 L1 Static Frontend Gate

Added a repeatable frontend gate:

```powershell
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_frontend.py
```

Current production result:

- Overall: `FAIL`
- Failed: `5`
- Total: `5`

Failed gates:

- `L1-FRONTEND-INTEGRATION-001`: missing required frontend references for `patient_view.home/profile/device/agent`, phone verification start/confirm, and Agent messages.

- `L1-HOME-STATIC-001`: missing `问康复师`; still contains `M33`, `M55`, and `RoboRehab Controller`.
- `L1-PROFILE-STATIC-001`: missing `我的康复档案` and `手机号`; still contains `M33`, `M55`, `患者 A`, `ID: 8829`, `避免过度伸展`, and `RoboRehab Controller`.
- `L1-DEVICE-STATIC-001`: still contains `M33`, `M55`, `UUID`, and `Gatekeeper`.
- `L1-AGENT-STATIC-001`: missing `问康复师`.

This gate is intentionally strict and should remain failing until Stitch converts normal user pages to the `patient_view` contract.

2026-07-06 continuation tightened the same gate so it verifies more of the actual L1 phone/device onboarding surface:

- `L1-PROFILE-STATIC-001` now requires `绑定手机号` and `验证码` in addition to profile title and phone state.
- `L1-DEVICE-STATIC-001` now requires `绑定设备` and `打开康复设备电源` in addition to a normal device page.
- Fresh local gate tests: `4 passed`.
- Fresh full local backend plus QA suite: `53 passed, 1 warning`.
- Fresh cloud L1 release gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.
- Current stricter frontend failures:
  - Profile missing: `我的康复档案`, `手机号`, `绑定手机号`, `验证码`.
  - Device missing: `绑定设备`, `打开康复设备电源`.

2026-07-06 continuation added an integration contract sub-gate so a Stitch build cannot pass by changing copy only:

- New gate: `L1-FRONTEND-INTEGRATION-001`.
- It checks deployed page source and same-origin scripts for auth, `/me`, `patient_view` sections, phone verification, device binding, and Agent messages.
- Red tests first failed because `check_frontend_integration_contract` did not exist.
- Focused integration tests after implementation: `2 passed`.
- Full frontend gate tests after implementation: `6 passed`.
- Full local backend plus QA suite: `65 passed, 1 warning`.
- Current cloud frontend gate: `overall = FAIL`, `failed = 5`, `total = 5`.
- Current cloud integration gate missing: `patient_view_home`, `patient_view_profile`, `patient_view_device`, `patient_view_agent`, `phone_verification_start`, `phone_verification_confirm`, and `agent_messages`.
- Cloud API/APK acceptance remained `overall = PASS`, `p0_failed = 0`, `total = 22`.

2026-07-06 continuation tightened the combined L1 release gate so `闂悍澶嶅笀` cannot be accepted as L1 while it is still running safe fallback rules instead of a configured cloud model:

- New L1 blocker: `agent_cloud_model`.
- Required API gates for L1:
  - `P1-AGENT-CONFIG-001 = PASS`
  - `P1-AGENT-MODEL-001 = PASS`
- Red test first: the release summary returned `PASS` when API P0 and frontend passed even though both Agent model gates were `WARN`.
- Focused release tests after implementation: `3 passed`.
- Full local backend plus QA suite: `66 passed, 1 warning`.
- Current cloud combined L1 gate: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Current cloud Agent state remains `fallback_rule_based`, reason `external_model_not_configured`; configure cloud-model relay credentials before calling the Agent L1 user-ready.

2026-07-06 continuation browser QA rechecked the deployed cloud device page at `390 x 844`:

- Screenshot: `screenshots/continuation-device-qa-20260706-390.png`.
- URL: `http://106.55.62.122:3001/rehab-arm-mobile/device.html?v=qa-20260706-continuation`.
- Result: `FAIL`.
- Still visible on the normal device page: false network warning, `setup_required`, `M33`, `M55`, `Gatekeeper`, and a prominent `bluetooth-debug.html` developer route.
- Still missing as the primary user flow: a patient-facing device binding wizard led by `绑定设备` / `打开康复设备电源`.

## 2026-07-06 L1 Combined Release Gate

Added a single release gate that runs backend/API/APK smoke and frontend L1 checks together:

```powershell
$env:REHAB_QA_EMAIL='<staging email>'
$env:REHAB_QA_PASSWORD='<staging password>'
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_release.py
```

Current production result:

- Overall: `FAIL`
- API overall: `PASS`
- API P0 failed: `0`
- Frontend overall: `FAIL`
- Frontend failed: `5`
- Blocking gates: `frontend_l1_gate`, `agent_cloud_model`

This is now the L1 release decision command. A cloud deployment or APK refresh is not accepted as user-ready unless this command returns exit code `0` with `overall = PASS`.

## 2026-07-06 Device Binding Deployment Resmoke

After deploying `device-binding-hardening-20260706` and adding the cross-account conflict gate, the cloud API and APK smoke were rerun.

- Overall: `PASS`
- P0 failed: `0`
- Total: `18`
- Cloud PID: `1449627`
- Build SHA: `device-binding-hardening-20260706`
- Build ref: `codex/rehab-mobile-backend-qa-20260706`
- Build time: `2026-07-06T03:54:50Z`
- `P0-DEVICE-FLOW-001`: `PASS`
  - First bind status: `200`
  - Repeat bind status: `200`
  - Repeat bind reused the same device record: `true`
  - Test device: `QA-REHAB-ARM-STAGING-001`
- `P0-DEVICE-CONFLICT-001`: `PASS`
  - Owner bind status: `200`
  - Second account bind status: `409`
  - Second account error code: `DEVICE_ALREADY_BOUND`
  - Conflict test device: `QA-REHAB-ARM-CONFLICT-001`
- `P1-AGENT-MODEL-001`: `WARN`
  - Mode: `fallback_rule_based`
  - Reason: `external_model_not_configured`
  - Meaning: safe Q&A works, but staging is not currently backed by a configured external cloud model.
- APK HEAD: `PASS`, size `4198462`, content type `application/vnd.android.package-archive`

Combined L1 release gate after this deployment:

- Overall: `FAIL`
- API overall: `PASS`
- API P0 failed: `0`
- Frontend overall: `FAIL`
- Frontend failed: `4`
- Blocking gates: `frontend_l1_gate`

Browser QA was also run in the in-app browser at `390 x 844`. The screenshots under `screenshots/device-binding-*.png` confirm the deployed frontend still shows patient-facing blockers:

- `home`: false network warning, `setup_required`, `M33`, `M55`, no `问康复师` entry.
- `profile`: false network warning and `M33`, profile screen still not centered on cloud account/phone.
- `device`: `M33`, `M55`, `Gatekeeper`, and debug-oriented device content.
- `agent`: not a normal rehab therapist chat entry; still starts from AI planning workflow and includes `M33`.

## Findings

### P0-Home-001 - False Network Error

Evidence: `01-home-390-current.png`

The first visible status says `网络未连接，请检查后端服务`, but the API acceptance smoke passes against `http://106.55.62.122:8011`. This makes a healthy cloud deployment look broken to the patient.

Expected:

- The frontend uses the same deployed API base as the smoke test: `http://106.55.62.122:8011`.
- If an authenticated API request fails, show a specific recoverable state such as "请重新登录" or "正在同步云端资料".
- Do not show "network disconnected" while rendering live cloud data or static fallbacks.

### P0-Home-002 - Engineering Workflow Is Exposed To Patients

Evidence: `01-home-390-current.png`, `04-device-nav-390.png`

Visible patient-facing screens still expose raw or semi-raw terms:

- `setup_required`
- `M33`
- `M33 BLE`
- `M55 EMG`
- `early_active`
- `left`
- `动作队列`
- `阻塞`
- `禁止`
- `App 只显示流程证据；真实运动许可仍由 M33 最终裁决`

Expected:

- Normal screens render `GET /api/rehab-arm/app/v1/me -> data.patient_view`.
- Raw workflow, hardware, and debug vocabulary stays behind a developer-only page.
- The first screen gives one clear next action, not an internal workflow dump.

### P0-Agent-001 - Rehab Therapist Entry Is Not Usable

Evidence: `02-agent-top-click-390.png`, `03-agent-floating-click-390.png`

The top icon is visually present but is labelled like a settings/tool button. Clicking it did not open a chat, drawer, route, or modal. The floating button received focus/click styling, but it also did not open the therapist chat.

Expected:

- A visible button labelled `问康复师`.
- `aria-label="问康复师"` and minimum 44px touch target.
- Click opens a chat sheet/page.
- Safe messages call `POST /api/rehab-arm/app/v1/agent/messages`.
- Unsafe direct-control requests show the backend protective refusal copy.

### P0-Device-001 - Device Tab Is Still A Developer Surface

Evidence: `04-device-nav-390.png`

The device page still orients around system architecture and device internals instead of a simple binding wizard. It also repeats the home workflow/debug block above the device content.

Expected:

- Device tab starts from `data.patient_view.device`.
- Primary flow is a patient-facing binding wizard:
  1. turn on rehab device,
  2. keep phone close,
  3. select Bluetooth device or scan code,
  4. wait for device safety confirmation.
- `bluetooth-debug.html` remains available only through a developer/debug entry.

### P0-Profile-001 - Profile Shows Demo Identity And Fake Medical Advice

Evidence: `05-profile-nav-390.png`

The profile page shows `患者 A`, `ID: 8829`, `第二阶段康复中`, and a red medical warning `避免过度伸展 > 120°`. It also lists `M33` and `M55` devices. This is unsafe because incomplete clinical data appears as real medical advice.

Expected:

- Profile uses `data.patient_view.profile`.
- Display the signed-in cloud account and phone verification state.
- Missing medical constraints use a calm `待完善` state.
- Do not show demo constraints as real advice.

## Backend/API Evidence

Latest API/package acceptance smoke passed after the Agent draft patient-copy deployment:

- Overall: `PASS`
- P0 failed: `0`
- Total checks: `22`
- Cloud PID: `1916595`
- Build ref: `codex/rehab-mobile-backend-qa-20260706`
- Build SHA: `8e17a51d`
- Build time: `2026-07-06T11:59:30Z`
- `P0-PATIENT-VIEW-001`: `PASS`
- `P1-DEPLOY-META-001`: `PASS`
- `P0-PHONE-FLOW-001`: `PASS`
- `P1-PHONE-RESEND-001`: `PASS`
- `P0-DEVICE-FLOW-001`: `PASS`
- `P0-DEVICE-CONFLICT-001`: `PASS`
- `P1-AGENT-CONFIG-001`: `WARN`, public-config exposes `data.agent.model_readiness` and current staging is `fallback_rule_based`.
- Agent safe answer with `data.model_status`: `PASS`
- Current Agent model mode: `fallback_rule_based`, reason `external_model_not_configured`
- `P1-AGENT-MODEL-001`: `WARN`, configure external cloud model credentials before claiming production-grade model-backed Agent.
- `P1-PHONE-SMS-001`: `WARN`, current staging is still `debug_sms`.
- Agent unsafe refusal: `PASS`
- CORS from deployed web origin: `PASS`
- APK HEAD: `PASS`, size over 1 MB

The remaining blocker is frontend rendering and interaction.

## Backend Agent Draft Patient-Copy Follow-Up

2026-07-06 continuation work removed engineering vocabulary from the user-visible AI training draft copy:

- Local source: `cloud/rehab-platform/app/services/agent.py`.
- Local regression: `cloud/rehab-platform/tests/test_agent.py::test_ai_training_draft_uses_profile_and_recent_session_context`.
- User-visible generated plan title changed from English `AI rehab draft` to Chinese patient copy.
- User-visible risk notes now say the user must complete device safety confirmation before real training, instead of exposing `M33`, `preflight`, or `m33_accepted`.
- Cloud patch deployed to `app/modules/rehab_arm/app_service.py` on `106.55.62.122`.
- Cloud backup: `app/modules/rehab_arm/app_service.py.bak-agent-draft-copy-20260706`.
- Cloud restart:
  - PID: `1916595`
  - API: `http://106.55.62.122:8011`
  - `APP_ENV = staging`
  - `AI_COLLAB_BUILD_SHA = 8e17a51d`
  - `AI_COLLAB_BUILD_REF = codex/rehab-mobile-backend-qa-20260706`
  - `AI_COLLAB_BUILD_TIME = 2026-07-06T11:59:30Z`

Fresh verification:

- Red test first failed because the draft title was `AI rehab draft` and risk notes still contained `M33 safety acceptance and preflight`.
- Focused regression after implementation: `1 passed, 1 warning`.
- Agent suite: `8 passed, 1 warning`.
- Acceptance and release helper tests: `22 passed`.
- Full local backend plus QA suite: `66 passed, 1 warning`.
- Remote compile: `.venv/bin/python -m py_compile app/modules/rehab_arm/app_service.py`.
- Cloud health returned build SHA `8e17a51d`.
- Cloud AI draft smoke found no `M33`, `preflight`, `m33_accepted`, `CAN`, or `Stop` in `risk_notes`.
- Cloud acceptance: `overall = PASS`, `p0_failed = 0`, `total = 22`.
- Total L1 release gate: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- APK HEAD: `200`, size `4198462` bytes, content type `application/vnd.android.package-archive`.

## Backend Deployment Metadata Follow-Up

2026-07-06 continuation work made every cloud acceptance run traceable to a deployed build:

- `GET /health` now returns `data.deployment`.
- Deployment fields:
  - `build_sha`
  - `build_ref`
  - `build_time`
  - `app_env`
- Acceptance smoke now includes `P1-DEPLOY-META-001`.
- Acceptance phone flow now generates a fresh default staging phone number per run when `--phone-test-phone` is not supplied, avoiding false P0 failures from the 60-second resend cooldown.
- Cloud restart:
  - PID: `1677646`
  - API: `http://106.55.62.122:8011`
  - `APP_ENV = staging`
  - `AI_COLLAB_BUILD_SHA = b925e316`
  - `AI_COLLAB_BUILD_REF = codex/rehab-mobile-backend-qa-20260706`
  - `AI_COLLAB_BUILD_TIME = 2026-07-06T07:50:07Z`

Fresh verification:

- Red tests first:
  - health test failed with `KeyError: 'deployment'`;
  - acceptance helper tests failed because `deployment_metadata_readiness` did not exist;
  - generated-phone test failed because `default_phone_test_phone` did not exist.
- Focused health metadata test after implementation: `1 passed, 1 warning`.
- Focused deployment metadata helper tests after implementation: `2 passed`.
- Focused generated-phone helper test after implementation: `1 passed`.
- Full local backend plus QA suite: `60 passed, 1 warning`.
- Cloud health now returns deployment metadata with build SHA `b925e316`.
- Cloud acceptance: `overall = PASS`, `p0_failed = 0`, `total = 22`.
- `P1-DEPLOY-META-001` -> `PASS`.
- APK smoke remained `PASS` with size `4198462` bytes and content type `application/vnd.android.package-archive`.
- Total L1 release gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.
- Browser QA attempt for this pass reached the in-app browser but screenshot capture timed out twice; no new screenshot was accepted for this metadata-only backend deployment. Existing screenshots and the frontend L1 static gate still document the visible frontend blockers.

## Stitch API Fixture Follow-Up

2026-07-06 continuation work exported a sanitized live API fixture so Stitch can wire the frontend from real cloud response shapes instead of guessing field names:

- New exporter: `tools/export_rehab_mobile_stitch_fixture.py`.
- New tests: `tools/test_export_rehab_mobile_stitch_fixture.py`.
- Fixture: `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json`.
- Fixture source: `http://106.55.62.122:8011`.
- Included response families:
  - `GET /health`
  - `GET /api/rehab-arm/app/v1/public-config`
  - `GET /api/rehab-arm/app/v1/me`
  - safe `POST /api/rehab-arm/app/v1/agent/messages`
  - unsafe `POST /api/rehab-arm/app/v1/agent/messages`
- Privacy check: real account tokens, verification codes, UUID-like raw ids, email addresses, and phone numbers are removed or masked.
- Stitch prompt and runbook now point to this fixture before frontend edits.

Fresh verification:

- Red tests first failed because `tools/export_rehab_mobile_stitch_fixture.py` did not exist.
- Focused fixture tests after implementation and UUID sanitizer hardening: `3 passed`.
- Full local backend plus QA suite: `63 passed, 1 warning`.
- Cloud fixture export succeeded using the staging account.
- Initial secret scan found UUID-like plan/device/draft ids embedded in live response fields and endpoints; sanitizer was tightened to replace `*_id`, `*_uuid`, and embedded UUID path segments.
- Follow-up secret scan found no real staging email, raw phone number, verification code, UUID-like id, or long Bearer token in the generated fixture.
- Cloud acceptance remained `overall = PASS`, `p0_failed = 0`, `total = 22`; APK remained reachable with size `4198462` bytes and content type `application/vnd.android.package-archive`.
- Total L1 release gate remained API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.

## Backend Agent Public Config Readiness Follow-Up

2026-07-06 continuation work exposed Agent readiness before the user sends a chat message:

- `GET /api/rehab-arm/app/v1/public-config` now returns `data.agent.message_endpoint`.
- `GET /api/rehab-arm/app/v1/public-config` now returns `data.agent.model_readiness`.
- Local readiness shape:
  - `mode = cloud_model_configured` when the backend has a base URL, API key, and model name.
  - `mode = fallback_rule_based` when the cloud model is not configured.
  - API keys are never returned in public config.
- Acceptance smoke now includes `P1-AGENT-CONFIG-001`.
- Cloud deployment patched `app/modules/rehab_arm/app_router.py` on `106.55.62.122`.
- Cloud backup: `app/modules/rehab_arm/app_router.py.bak-agent-readiness-20260706`.
- Cloud restart:
  - PID: `1666259`
  - API: `http://106.55.62.122:8011`

Fresh verification:

- Red tests first:
  - backend test failed with `KeyError: 'agent'`;
  - acceptance helper tests failed because `agent_public_config_readiness` did not exist.
- Focused backend test after implementation: `1 passed, 1 warning`.
- Focused acceptance helper tests after implementation: `2 passed`.
- Full local backend plus QA suite: `54 passed, 1 warning`.
- Remote compile: `.venv/bin/python -m py_compile app/modules/rehab_arm/app_router.py app/settings.py`.
- Cloud public-config now includes:
  - `data.agent.message_endpoint = /api/rehab-arm/app/v1/agent/messages`
  - `data.agent.model_readiness.mode = fallback_rule_based`
  - `data.agent.model_readiness.reason = external_model_not_configured`
- Cloud acceptance: `overall = PASS`, `p0_failed = 0`, `total = 21`.
- `P1-AGENT-CONFIG-001` -> `WARN`, because current staging cloud-model relay credentials are not configured.
- APK smoke remained `PASS` with size `4198462` bytes and content type `application/vnd.android.package-archive`.
- Total L1 release gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.
- Browser QA captured `docs/qa/rehab-mobile-20260706/screenshots/agent-readiness-ai-plan-390.png`; the Agent page still shows a false network warning, `setup_required`, and no visible `问康复师` entry, so Stitch still must consume the new public-config contract.

## Backend Source-Parity Follow-Up

2026-07-06 continuation work closed a backend source-parity gap:

- Local source now includes `data.patient_view` in `cloud/rehab-platform/app/api/routes/rehab_app.py`.
- Added regression coverage in `cloud/rehab-platform/tests/test_app_compat.py`.
- Expanded `tools/qa_rehab_mobile_acceptance.py` so `P0-PATIENT-VIEW-001` checks:
  - `home/profile/device/agent` sections,
  - Agent entry label `问康复师`,
  - Agent endpoint `/api/rehab-arm/app/v1/agent/messages`,
  - device binding first step `打开康复设备电源`,
  - profile phone label `手机号`,
  - no raw technical terms.

Fresh verification:

- Red test first: missing local `patient_view` failed with `KeyError: 'patient_view'`.
- Local focused test after implementation: `1 passed, 1 warning`.
- Local backend suite: `22 passed, 1 warning`.
- Syntax checks: `py_compile` passed for backend route and QA script.
- Stricter cloud smoke: `overall = PASS`, `p0_failed = 0`, `total = 14`.

Cloud runtime already had the deployed patient-view contract, so no extra cloud code patch or restart was needed for that source-parity follow-up. Later Agent and phone-verification follow-ups restarted the cloud service; latest verified cloud PID is `1429532`.

## Backend Agent Cloud-Model Follow-Up

2026-07-06 continuation work added a verified Agent model-status contract:

- Local backend `answer_patient_question` supports an OpenAI-compatible cloud model call when configured.
- If the cloud model is not configured or unavailable, the endpoint returns a safe rule-based answer.
- Every safe Agent answer now includes `data.model_status` so the app can disclose whether the response came from `cloud_model` or `fallback_rule_based`.
- Cloud deployment patched `app/modules/rehab_arm/app_router.py` on `106.55.62.122`.
- Latest cloud acceptance passed with `P0-AGENT-001` checking `model_status`.

Fresh verification:

- Red test first: `tools/test_qa_rehab_mobile_acceptance.py` failed because `agent_model_status_ok` did not exist.
- Agent focused tests: `7 passed, 1 warning`.
- Local backend suite: `25 passed, 1 warning`.
- Acceptance helper tests: `2 passed`.
- Cloud smoke: `overall = PASS`, `p0_failed = 0`, `total = 14`.
- APK smoke remained `PASS` with size `4198462` bytes.

## Backend Phone Verification Follow-Up

2026-07-06 continuation work hardened the account phone-binding flow:

- Local backend now has configurable phone verification behavior:
  - `PHONE_VERIFICATION_DEBUG_CODE_ENABLED`
  - `PHONE_VERIFICATION_TTL_SECONDS`
  - `PHONE_VERIFICATION_MAX_ATTEMPTS`
- When debug SMS is disabled, `POST /account/phone-verifications` no longer returns `debug_code`.
- Wrong code attempts now stop with `PHONE_CODE_ATTEMPTS_EXCEEDED` after the configured limit.
- Acceptance smoke now includes `P0-PHONE-FLOW-001`, which requests a staging code and confirms it end to end.
- Cloud deployment patched `app/settings.py` and `app/modules/rehab_arm/app_service.py` on `106.55.62.122`.

Fresh verification:

- Red tests first:
  - debug-code hiding failed because the API still returned `debug_sms`,
  - attempt locking failed because the API still returned `PHONE_CODE_INVALID`.
- Phone focused tests: `5 passed, 1 warning`.
- Local backend plus QA suite: `35 passed, 1 warning`.
- Cloud smoke: `overall = PASS`, `p0_failed = 0`, `total = 15`.
- Total L1 release gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.
- APK smoke remained `PASS` with size `4198462` bytes.

## Backend Device Binding Follow-Up

2026-07-06 continuation work hardened device binding ownership:

- Local backend now treats `m33_device_id` as a hardware ownership key.
- Same signed-in account can bind the same device repeatedly and update metadata without creating duplicates.
- A different account trying to bind an already-owned `m33_device_id` now receives `409 DEVICE_ALREADY_BOUND`.
- Acceptance smoke now includes `P0-DEVICE-FLOW-001`, which binds the staging device and repeats the bind to prove idempotency.
- Acceptance smoke now includes `P0-DEVICE-CONFLICT-001`, which prepares a second QA account and verifies an already-bound device returns `409 DEVICE_ALREADY_BOUND`.
- Cloud deployment patched `app/modules/rehab_arm/app_service.py` on `106.55.62.122`.

Fresh verification:

- Red test first: second account bind returned `200` before the fix, but the test expected `409`.
- Device focused tests: `5 passed, 1 warning`.
- Acceptance helper tests: `6 passed`.
- Local focused combined tests: `11 passed, 1 warning`.
- Acceptance helper tests after conflict gate: `8 passed`.
- Cloud smoke: `overall = PASS`, `p0_failed = 0`, `total = 17`.
- Total L1 release gate after conflict gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`; second QA account login was reused and the second bind returned `409 DEVICE_ALREADY_BOUND`.
- Browser QA screenshots: `docs/qa/rehab-mobile-20260706/screenshots/device-binding-*.png`.
- APK smoke remained `PASS` with size `4198462` bytes.

## Backend Agent Model Readiness Follow-Up

2026-07-06 continuation work added explicit visibility for whether `问康复师` is answered by a configured cloud model or the safe local fallback:

- Acceptance smoke now includes `P1-AGENT-MODEL-001`.
- Cloud environment inspection found external model credentials unset:
  - `REHAB_ARM_MODEL_RELAY_API_KEY`: unset
  - `AGENT_MODEL_API_KEY`: unset
  - `OPENAI_API_KEY`: unset
- Current staging Agent result:
  - `model_status.mode = fallback_rule_based`
  - `fallback_reason = external_model_not_configured`

Fresh verification:

- Red test first: `agent_cloud_model_readiness` was missing and helper tests failed.
- Acceptance helper tests after implementation: `10 passed`.
- Cloud smoke: `overall = PASS`, `p0_failed = 0`, `total = 18`.
- `P1-AGENT-MODEL-001` -> `WARN`.
- Total L1 release gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.
- In-app browser plugin QA attempt: the Codex in-app browser instance was discoverable, but `selected` tab and tab-list reads timed out; no new screenshot evidence was captured in this pass.

## Backend Phone SMS Delivery Readiness Follow-Up

2026-07-06 continuation work added explicit visibility for whether phone verification can use a real SMS delivery channel or is still using staging debug codes:

- `GET /api/rehab-arm/app/v1/public-config` now returns `data.phone_verification.delivery_status`.
- Acceptance smoke now includes `P1-PHONE-SMS-001`.
- Cloud deployment patched:
  - `app/settings.py`
  - `app/modules/rehab_arm/app_router.py`
- Cloud backups:
  - `app/settings.py.bak-sms-readiness-20260706`
  - `app/modules/rehab_arm/app_router.py.bak-sms-readiness-20260706`
- Cloud restart:
  - PID: `1605495`
  - API: `http://106.55.62.122:8011`
- Current staging SMS status:
  - `mode = debug_sms`
  - `configured = false`
  - `exposes_debug_code = true`
  - `reason = debug_code_enabled`

Fresh verification:

- Red tests first:
  - `phone_delivery_readiness` was missing and helper tests failed.
  - `public-config` was missing `phone_verification` and backend test failed.
- Focused helper tests after implementation: `12 passed`.
- Focused phone backend tests after implementation: `6 passed, 1 warning`.
- Full local suite: `46 passed, 1 warning`.
- Remote compile: `.venv/bin/python -m py_compile app/settings.py app/modules/rehab_arm/app_router.py`.
- Cloud smoke: `overall = PASS`, `p0_failed = 0`, `total = 19`.
- `P1-PHONE-SMS-001` -> `WARN`.
- APK smoke remained `PASS` with size `4198462` bytes.
- Total L1 release gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.
- Browser QA captured `docs/qa/rehab-mobile-20260706/screenshots/sms-readiness-device-390.png`; the page still shows a false network warning and engineering/debug terms including `setup_required`, `M33`, `M55`, and `Gatekeeper`.

## Backend Phone SMS Webhook Delivery Follow-Up

2026-07-06 continuation work added the actual SMS provider handoff path behind phone verification:

- When `PHONE_VERIFICATION_DEBUG_CODE_ENABLED=false` and a provider/webhook URL are configured, `POST /api/rehab-arm/app/v1/account/phone-verifications` sends the verification payload to the SMS webhook and returns `delivery_channel = sms` without exposing `debug_code`.
- When debug SMS is disabled but no delivery provider is configured, the request returns `503 PHONE_SMS_NOT_CONFIGURED` instead of pretending a code was sent.
- When the configured webhook fails, the request returns `502 PHONE_SMS_DELIVERY_FAILED`.
- Webhook payload includes `phone`, `code`, `purpose`, `verification_id`, and `expires_in`; webhook tokens are sent only as an Authorization header and are not returned to the app.
- Cloud deployment patched `app/modules/rehab_arm/app_service.py` on `106.55.62.122`.
- Cloud backup: `app/modules/rehab_arm/app_service.py.bak-sms-webhook-20260706`.
- Cloud restart:
  - PID: `1620444`
  - API: `http://106.55.62.122:8011`

Fresh verification:

- Red tests first:
  - `_post_sms_webhook` was missing when the webhook-delivery test was introduced.
  - The unconfigured production-SMS path returned `200` before the fix, but the test expected `503 PHONE_SMS_NOT_CONFIGURED`.
- Focused phone backend tests after implementation: `8 passed, 1 warning`.
- Full local backend plus QA suite: `48 passed, 1 warning`.
- Remote compile: `.venv/bin/python -m py_compile app/modules/rehab_arm/app_service.py`.
- Cloud smoke after deployment: `overall = PASS`, `p0_failed = 0`, `total = 19`.
- `P0-PHONE-FLOW-001` -> `PASS`.
- `P1-PHONE-SMS-001` -> `WARN`, because current staging is intentionally still `debug_sms`.
- APK smoke remained `PASS` with size `4198462` bytes and content type `application/vnd.android.package-archive`.
- Total L1 release gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.
- Browser QA captured `docs/qa/rehab-mobile-20260706/screenshots/sms-webhook-device-390.png`; the device page still shows `setup_required`, `M33`, `M55`, `Gatekeeper`, and debug-oriented device content.

## Backend Phone Verification Resend Cooldown Follow-Up

2026-07-06 continuation work added resend throttling so a user cannot repeatedly trigger phone verification sends by tapping too quickly:

- Local backend setting: `PHONE_VERIFICATION_RESEND_COOLDOWN_SECONDS`, default `60`.
- Cloud setting: `rehab_arm_phone_verification_resend_cooldown_seconds`, default `60`.
- `GET /api/rehab-arm/app/v1/public-config` now exposes `data.phone_verification.resend_cooldown_seconds`.
- Immediate repeat requests for the same signed-in user, phone, and purpose now return `429 PHONE_CODE_RESEND_TOO_SOON`.
- Local error responses preserve `retry_after`; cloud AppError responses expose it under `error.details.retry_after`.
- Acceptance smoke now includes `P1-PHONE-RESEND-001`.
- Cloud deployment patched:
  - `app/settings.py`
  - `app/modules/rehab_arm/app_router.py`
  - `app/modules/rehab_arm/app_service.py`
- Cloud backups:
  - `app/settings.py.bak-phone-cooldown-20260706`
  - `app/modules/rehab_arm/app_router.py.bak-phone-cooldown-20260706`
  - `app/modules/rehab_arm/app_service.py.bak-phone-cooldown-20260706`
- Cloud restart:
  - PID: `1639678`
  - API: `http://106.55.62.122:8011`

Fresh verification:

- Red test first: immediate resend returned `200` before cooldown enforcement.
- Intermediate root cause: local error wrapping initially dropped `retry_after`; `cloud/rehab-platform/app/main.py` now preserves controlled extra error fields.
- Focused phone backend tests: `9 passed, 1 warning`.
- Acceptance helper tests: `14 passed`.
- Full local backend plus QA suite: `51 passed, 1 warning`.
- Remote compile: `.venv/bin/python -m py_compile app/settings.py app/modules/rehab_arm/app_router.py app/modules/rehab_arm/app_service.py`.
- Cloud public-config shows `resend_cooldown_seconds = 60`.
- Manual cloud resend smoke: second request returned `429 PHONE_CODE_RESEND_TOO_SOON` with `retry_after`.
- Cloud acceptance: `overall = PASS`, `p0_failed = 0`, `total = 20`.
- `P1-PHONE-RESEND-001` -> `PASS`.
- APK smoke remained `PASS` with size `4198462` bytes and content type `application/vnd.android.package-archive`.
- Total L1 release gate: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate`.
- Browser QA captured `docs/qa/rehab-mobile-20260706/screenshots/phone-cooldown-profile-390.png`; the profile page still misses the phone field and shows demo/engineering content, so Stitch must consume the phone contract before L1 can pass.

## Accessibility Risks

- Agent-like icon buttons do not communicate their purpose clearly to screen-reader or touch users.
- Multiple bottom-nav labels are visible, but the current screen also shows repeated debug content above the active section, weakening reading order.
- Long debug strings and mixed language terms reduce readability at 390px.
- Screenshot-only audit cannot prove keyboard focus order, screen-reader output, or color contrast compliance. Those need DOM/assistive checks after Stitch fixes.

## Acceptance Target For The Next Stitch Build

The next deployed frontend must pass these browser checks at `390 x 844`:

1. Home shows no raw technical terms and has one dominant next action.
2. Home no longer shows false `网络未连接` when API health/auth/profile are reachable.
3. `问康复师` opens a working chat and calls the Agent endpoint.
4. Unsafe Agent requests show a protective Chinese refusal, not a generic error.
5. Device tab opens a patient binding wizard, not a debug page.
6. Profile shows cloud account, phone verification state, and safe `待完善` medical empty state.
7. Debug transport details are hidden from normal users.
8. No text overlap or unreachable primary controls at 390px.

## Current Product Decision

Do not call this build user-ready. Backend is ready for Stitch to consume, but the rendered app still fails the patient-facing P0 gates.

Stitch execution runbook:

- `docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md`
- Primary Stitch prompt: `docs/stitch/rehab-mobile-l1-stitch-execution-v2-20260706.md`
