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
17. `screenshots/stitch-packet-device-qa-430bfdf5-390.png` - Device page browser QA after the Stitch packet SMS/evidence refresh commit.
18. `screenshots/agent-cloud-ai-plan-20260706-390.jpg` - Agent page browser QA after cloud model runtime deployment.

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
| 13 | Device page resmoke after Stitch packet SMS/evidence refresh commit | FAIL | `screenshots/stitch-packet-device-qa-430bfdf5-390.png` |
| 14 | Agent page after cloud model runtime deployment | FAIL | `screenshots/agent-cloud-ai-plan-20260706-390.jpg` |

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

## Agent Cloud Model Relay Ops Follow-Up

2026-07-06 continuation work investigated the remaining `agent_cloud_model` blocker against the live cloud service:

- Cloud model relay settings are currently empty:
  - `REHAB_ARM_MODEL_RELAY_PROVIDER`
  - `REHAB_ARM_MODEL_RELAY_BASE_URL`
  - `REHAB_ARM_MODEL_RELAY_MODEL`
  - `REHAB_ARM_MODEL_RELAY_API_KEY`
  - `REHAB_ARM_MODEL_RELAY_EXTERNAL_ENABLED=false`
- XiaoZhi ASR/TTS fallback relay keys are also empty, so there is no reusable model key on this staging server.
- The cloud App Agent and AI draft planner both use the shared `REHAB_ARM_MODEL_RELAY_*` settings.
- The existing config writer clears the settings cache after API-based `.env` updates; direct server `.env` edits still require a service restart.
- Added `tools/configure_rehab_model_relay.py` to configure the relay through the privileged project API and smoke-test `/api/rehab-arm/app/v1/agent/messages`.
- Added `tools/test_configure_rehab_model_relay.py`.
- The configure tool redacts the API key and exits successfully only when the Agent smoke response reports `data.model_status.mode = cloud_model`.
- Focused tests: `5 passed`.
- Full local backend plus QA suite after this tooling change: `71 passed, 1 warning`.
- Cloud acceptance after this tooling change: API/APK `PASS`, `p0_failed = 0`, `total = 22`.
- Total L1 release gate remains `FAIL`, with blockers `frontend_l1_gate` and `agent_cloud_model`.
- Negative no-key check returned `{"error": "api_key is required"}`, proving the tool does not write partial config without a real model secret.
- Browser QA screenshot: `docs/qa/rehab-mobile-20260706/screenshots/model-relay-ops-device-390.png`.
  - Current deployed `device.html` still shows a false network warning, `setup_required`, `M33`, `M55`, and `Gatekeeper`.
  - Current deployed `device.html` contains `绑定设备` but still misses the normal-user step copy `打开康复设备电源`.
- New ops runbook: `docs/deployments/rehab-mobile-agent-model-relay-runbook-20260706.md`.

Current product decision remains unchanged: do not call this build L1 user-ready until a real model endpoint/key is configured and both `P1-AGENT-CONFIG-001` and `P1-AGENT-MODEL-001` pass.

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
- Primary Stitch prompt: `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md`

## Stitch Fixture And Prompt V3 Follow-Up

2026-07-06 continuation work refreshed the Stitch handoff package after the model-relay ops pass:

- Confirmed no callable Google Stitch tool or installable Stitch plugin is available in this Codex environment, so Codex still provides prompts and backend QA artifacts only.
- Refreshed `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json` from the live cloud API.
- The fixture now includes sanitized `phone_verification.start_response` and `phone_verification.confirm_response` examples.
- `verification_id` is preserved as `fixture-verification-id` so Stitch can wire the confirm URL without exposing raw ids.
- `debug_code`, access tokens, real email, and real phone values remain removed or masked.
- Added the current primary Stitch prompt: `docs/stitch/rehab-mobile-l1-stitch-execution-v3-20260706.md`.
- Updated the runbook to make V3 the primary frontend task.
- Verification after the V3 handoff:
  - Fixture/tool focused tests: `30 passed`.
  - Full local backend plus QA suite: `71 passed, 1 warning`.
  - Fixture safety check: passed; no real QA email, token, debug code, raw verification id, or real phone value found.
  - Cloud acceptance: API/APK `PASS`, `p0_failed = 0`, `total = 22`.
  - Total L1 release gate remains `FAIL`, with blockers `frontend_l1_gate` and `agent_cloud_model`.
  - APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.

## Frontend L1 Integration Gate Hardening Follow-Up

2026-07-06 continuation work tightened `L1-FRONTEND-INTEGRATION-001` so a frontend build cannot pass by only adding patient-facing copy or endpoint strings:

- Added required integration evidence for:
  - `auth_bearer_header`
  - `auth_token_storage`
  - `ask_therapist_accessibility`
  - `phone_resend_cooldown`
  - `phone_sms_error_states`
  - `device_already_bound`
  - `agent_unsafe_refusal`
  - `agent_model_status`
- Added a failing test first: a page bundle with the basic auth, `/me`, phone, device, and Agent endpoints passed before these interaction-state checks were introduced.
- Focused frontend/release gate tests after implementation: `10 passed`.
- Full local backend plus QA suite after this gate hardening: `72 passed, 1 warning`.
- Total L1 release gate remains `FAIL`, with API `PASS`, frontend `FAIL`, and blockers `frontend_l1_gate` and `agent_cloud_model`.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- Current deployed frontend still fails the stricter integration gate. Missing requirements now include:
  - `patient_view_home`
  - `patient_view_profile`
  - `patient_view_device`
  - `patient_view_agent`
  - `ask_therapist_accessibility`
  - `phone_verification_start`
  - `phone_verification_confirm`
  - `phone_resend_cooldown`
  - `phone_sms_error_states`
  - `device_already_bound`
  - `agent_messages`
  - `agent_unsafe_refusal`
  - `agent_model_status`
- Updated Stitch V3 prompt so the frontend generator has the exact stricter gate list.

## Objective-Level L1 Audit Follow-Up

2026-07-06 continuation work added a goal-level audit script so L1 cannot be declared complete from a broad release summary alone:

- New script: `tools/qa_rehab_mobile_l1_objective_audit.py`
- New tests: `tools/test_qa_rehab_mobile_l1_objective_audit.py`
- Red test first: the objective audit module did not exist.
- Follow-up red test caught a false positive where `device-binding-agent-390.png` could be counted as device wizard evidence; the matcher now requires `device` + `wizard`.
- Focused objective/release/frontend audit tests after implementation: `13 passed`.
- Full local backend plus QA suite after adding the objective audit: `75 passed, 1 warning`.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- Current live objective audit result:
  - Overall: `FAIL`
  - Failed requirements: `8 / 11`
  - Passing requirements: `cloud_deployment`, `login`, `apk_delivery`
  - Blocking requirements:
    - `home_next_step`
    - `phone_binding`
    - `device_binding`
    - `ask_therapist_safety`
    - `agent_cloud_model`
    - `profile_no_fake_debug`
    - `browser_qa_evidence`
    - `combined_l1_release`
- Current browser screenshot evidence is missing:
  - `ask_therapist_chat`
  - `unsafe_agent_refusal`
  - `device_binding_wizard`

## Stitch Repair Packet Follow-Up

2026-07-06 continuation work added a machine-readable repair packet so the next Stitch pass can target the exact live L1 failures instead of manually rereading the long QA report:

- New script: `tools/export_rehab_mobile_stitch_repair_packet.py`
- New tests: `tools/test_export_rehab_mobile_stitch_repair_packet.py`
- Live packet: `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`
- Source data: current cloud `tools/qa_rehab_mobile_l1_release.py` payload plus objective audit.

Fresh packet summary:

- Overall: `FAIL`
- Stitch blockers:
  - `home_next_step`
  - `phone_binding`
  - `device_binding`
  - `ask_therapist_safety`
  - `profile_no_fake_debug`
  - `browser_qa_evidence`
  - `frontend_l1_gate`
- Non-Stitch blocker:
  - `agent_cloud_model`
- Meta blocker:
  - `combined_l1_release`
- Frontend failures exported: `5`
- Integration gaps exported: `13`

The packet now prevents `combined_l1_release` from being misassigned to Stitch as a direct page task. It is kept as a meta blocker that should pass only after frontend, cloud model, and browser evidence are actually green.

Fresh verification:

- Red test first: `combined_l1_release` was initially grouped into `summary.stitch_blockers`.
- Focused repair-packet tests after implementation: `2 passed`.
- Related repair/objective/release/frontend tests: `15 passed`.
- Full local backend plus QA suite after adding the repair packet: `77 passed, 1 warning`.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` requirements failing.
- Live packet JSON parse check passed and reported `5` frontend failures plus `13` integration gaps.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## Agent Gemini Provider Follow-Up

2026-07-06 continuation work widened the backend Agent cloud-model relay so `agent_cloud_model` can be closed with either an OpenAI-compatible endpoint or Google Gemini:

- Updated backend service: `cloud/rehab-platform/app/services/agent.py`
- Updated tests: `cloud/rehab-platform/tests/test_agent.py`
- Updated config tool: `tools/configure_rehab_model_relay.py`
- Updated tests: `tools/test_configure_rehab_model_relay.py`
- Updated docs: `cloud/rehab-platform/README.md`, `cloud/rehab-platform/.env.example`, and `docs/deployments/rehab-mobile-agent-model-relay-runbook-20260706.md`

New behavior:

- `AGENT_MODEL_PROVIDER=openai_compatible` keeps the existing chat-completions path.
- `AGENT_MODEL_PROVIDER=gemini` calls Google Gemini `generateContent`.
- Gemini requests use `x-goog-api-key` and never place the key in the JSON body.
- Gemini responses are parsed from `candidates[0].content.parts[].text`.
- `tools/configure_rehab_model_relay.py --provider gemini` defaults `base_url` to `https://generativelanguage.googleapis.com/v1beta` when omitted.

Fresh verification:

- Red test first: `call_gemini_model` did not exist.
- Follow-up red test first: config payload still required `base_url` for `provider=gemini`.
- Focused Agent/config tests: `16 passed, 1 warning`.
- Full local backend plus QA suite: `97 passed, 1 warning`.
- Cloud runtime patched `app/modules/rehab_arm/app_router.py` on `106.55.62.122`; backup: `app_router.py.bak-gemini-provider-20260706`.
- Remote compile check passed: `.venv/bin/python -m py_compile app/modules/rehab_arm/app_router.py`.
- Cloud restart:
  - PID: `2052592`
  - Build SHA: `d2f81c92`
  - Build ref: `codex/rehab-mobile-backend-qa-20260706`
  - Build time: `2026-07-06T14:19:13Z`
- Cloud acceptance after deploy: `overall = PASS`, `p0_failed = 0`, `total = 22`.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.

Current product decision remains unchanged until staging is configured with a real model key and smoke-tested:

- `P1-AGENT-CONFIG-001` must be `PASS`.
- `P1-AGENT-MODEL-001` must be `PASS`.
- Agent safe answer must report `data.model_status.mode = cloud_model`.
- Do not commit, paste, screenshot, or log real model API keys.

## Agent Provider Preflight Follow-Up

2026-07-06 continuation work added a provider-direct smoke test before cloud
model relay configuration:

- New script: `tools/smoke_rehab_model_provider.py`
- New tests: `tools/test_smoke_rehab_model_provider.py`
- Updated repair packet action: `non_stitch_actions[0].preflight_command`
  now points at the smoke tool before `configure_command`.

Behavior:

- Supports `openai_compatible` chat completions and Gemini `generateContent`.
- Defaults Gemini base URL to `https://generativelanguage.googleapis.com/v1beta`.
- Sends the API key only in the provider-specific auth header.
- Redacts the API key from stdout and JSON summaries.
- Exits successfully only when the provider returns a usable answer.

Fresh evidence:

- Red test first: `tools/smoke_rehab_model_provider.py` did not exist.
- Focused smoke-tool tests after implementation: `4 passed`.
- Red repair-packet test first: non-Stitch actions did not include a preflight command.
- Focused repair-packet tests after implementation: `3 passed`.
- User-provided Google/Stitch key preflight result:
  - `gemini-3.5-flash`: `403 provider_http_error`, `answer_present = false`.
  - `gemini-2.5-flash`: `403 provider_http_error`, `answer_present = false`.
- No model relay config was written to staging because provider preflight failed.

Current product decision remains unchanged:

- `agent_cloud_model` remains blocked.
- `P1-AGENT-CONFIG-001` and `P1-AGENT-MODEL-001` must still become `PASS`
  before L1 user-ready staging can pass.

## Frontend Release Bundle Tool Follow-Up

2026-07-06 continuation work added a backend-owned packaging step for the moment Stitch returns updated frontend assets:

- New script: `tools/prepare_rehab_mobile_frontend_release.py`
- New tests: `tools/test_prepare_rehab_mobile_frontend_release.py`
- Updated repair packet artifact: `required_artifacts.frontend_release_tool`
- Updated V4 Stitch prompt section: `After Stitch Hands Back Frontend Files`

The tool validates that the Stitch output contains `home.html`, `profile.html`, `device.html`, and `ai-plan.html`, writes `artifacts/rehab-mobile-frontend-release/rehab-mobile-frontend-release.zip`, and records a manifest with deploy and verification commands.

Fresh verification:

- Red test first: `tools/prepare_rehab_mobile_frontend_release.py` did not exist.
- Follow-up red test first: repair packet and V4 prompt did not expose the new release bundle tool.
- Focused release-bundle/repair-packet/prompt tests: `8 passed`.
- Full local backend plus QA suite: `86 passed, 1 warning`.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## Frontend Release Manifest Verification Follow-Up

2026-07-06 continuation work added a deploy-before-copy verification gate for the moment Stitch returns updated frontend assets:

- New script: `tools/verify_rehab_mobile_frontend_release.py`
- New tests: `tools/test_verify_rehab_mobile_frontend_release.py`
- Updated release tool: `tools/prepare_rehab_mobile_frontend_release.py`
- Updated repair packet artifact: `required_artifacts.frontend_release_verifier`
- Refreshed prompt: `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md`

The verifier checks the generated frontend release manifest before any cloud copy:

- Manifest schema is `rehab-mobile-frontend-release/v1`.
- Zip exists, is non-empty, and matches the recorded sha256.
- Local frontend preflight report exists and is `PASS`.
- Required page artifacts are recorded for `home.html`, `profile.html`, `device.html`, and `ai-plan.html`.
- Deploy commands and post-deploy verification commands are present.
- Exact final browser QA screenshot filenames are preserved.

Fresh verification:

- Red test first: `tools/verify_rehab_mobile_frontend_release.py` did not exist.
- Follow-up red tests first: release manifest did not include the verifier command, and the repair packet did not expose `frontend_release_verifier`.
- Full local backend plus QA suite: `94 passed, 1 warning`.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## Frontend Release Deployment Guard Follow-Up

2026-07-06 continuation work added a guarded deploy executor for the moment
Stitch returns frontend files that pass local preflight and manifest verification:

- New script: `tools/deploy_rehab_mobile_frontend_release.py`
- New tests: `tools/test_deploy_rehab_mobile_frontend_release.py`
- Updated release manifest: `deploy.executor_command`
- Updated release verifier: `FRONTEND-RELEASE-DEPLOYMENT` now requires the
  deploy executor command.
- Updated repair packet artifact: `required_artifacts.frontend_release_deployer`
- Updated V4 Stitch prompt and runbook post-Stitch command list.

Behavior:

- Verifies the frontend release manifest before any deploy command can run.
- Defaults to dry-run and prints the `scp`, `ssh`, and post-deploy verification
  plan.
- Requires `--execute` before copying assets to the cloud server.
- Runs post-deploy checks only with `--run-post-verify`.
- Refuses unsafe `remote_web_root` values outside the expected rehab mobile web
  root.
- Bundles post-deploy PowerShell verification into one process so QA environment
  variables persist.

Fresh verification:

- Red test first: `tools/deploy_rehab_mobile_frontend_release.py` did not exist.
- Follow-up red test first: post-deploy verification commands were executed as
  separate shell commands instead of one PowerShell process.
- Focused release-deploy/manifest/packet/prompt tests: `18 passed`.
- No cloud runtime deployment was made for this tooling-only change because no
  new Stitch frontend bundle exists yet.

2026-07-06 continuation work tightened this path so Stitch output is checked before any cloud copy:

- Updated script: `tools/qa_rehab_mobile_l1_frontend.py`
- New tests: `tools/test_qa_rehab_mobile_l1_frontend_local_source.py`
- Updated release tool: `tools/prepare_rehab_mobile_frontend_release.py`
- Updated V4 Stitch prompt with `tools\qa_rehab_mobile_l1_frontend.py --source-dir apps/web/public/rehab-arm-mobile`

The local source-dir gate reuses the same page text and integration-contract rules as the deployed frontend gate. The release bundle tool now refuses to write a deployable bundle when this local preflight fails.

2026-07-06 continuation work also made this evidence persistent:

- `tools/qa_rehab_mobile_l1_frontend.py` now accepts `--output`.
- The release bundle tool writes `artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json` before creating the zip.
- The release manifest records `frontend_l1_preflight.report_path`.
- If local preflight fails, the failure report is still written so it can be fed back into Stitch.

Fresh verification after adding source-dir preflight:

- Red test first: `--source-dir` was not accepted by `tools/qa_rehab_mobile_l1_frontend.py`.
- Follow-up red test first: the release bundle tool still wrote bundles for frontend sources that failed L1.
- Follow-up red test first: `--output` was not accepted and release bundle failures did not leave a JSON report.
- Focused local-source/preflight-report/release-bundle/prompt tests: `9 passed`.
- Full local backend plus QA suite after preserving preflight evidence: `90 passed, 1 warning`.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## Browser Evidence Dimension Gate Follow-Up

2026-07-06 continuation work tightened browser QA evidence so screenshot filenames alone are no longer enough:

- Updated script: `tools/qa_rehab_mobile_l1_objective_audit.py`
- Updated tests: `tools/test_qa_rehab_mobile_l1_objective_audit.py`
- Updated repair packet exporter: `tools/export_rehab_mobile_stitch_repair_packet.py`
- Updated repair packet: `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`

Behavior:

- Browser evidence still requires the five L1 scenes: home first screen, Ask Therapist chat, unsafe refusal, device wizard, and profile account/phone/medical state.
- Matched evidence must decode to exactly `390 x 844`.
- The decoder supports PNG and JPEG headers, because the in-app browser may save JPEG bytes under a `.png` filename.
- Current `browser_evidence_current` is now exported into the Stitch repair packet.

Fresh live evidence state:

- Missing exact L1 success screenshots:
  - `home_first_screen`
  - `ask_therapist_chat`
  - `unsafe_agent_refusal`
  - `device_binding_wizard`
  - `profile_phone_medical`
- Matched L1 screenshots: none.
- Invalid dimensions: none, because no exact L1 success screenshot filenames are present.

Fresh verification:

- Red test first: wrong-size screenshot evidence was accepted before the dimension check.
- Follow-up red test first: browser JPEG screenshots with `.png` filenames were rejected before JPEG parsing was added.
- Follow-up red test first: `current-fail-*` screenshots could be counted as L1 success evidence before exact filename matching was added.
- Focused objective-audit and repair-packet tests: `8 passed`.
- Full local backend plus QA suite after adding the dimension gate: `80 passed, 1 warning`.
- Live objective audit remains `FAIL`; the browser evidence failure now reports missing exact L1 success screenshots.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## In-App Browser Current-Fail Evidence Follow-Up

2026-07-06 continuation work captured current deployed frontend failure evidence directly from the in-app browser with an explicit `390 x 844` viewport:

- `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/current-fail-home-clip-390x844.png`
- `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/current-fail-ai-plan-clip-390x844.png`
- `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/current-fail-device-clip2-390x844.png`
- `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/current-fail-profile-clip2-390x844.png`

All four accepted current-fail screenshots decode to `390 x 844`.

Fresh final verification after browser QA capture:

- Focused objective-audit and repair-packet tests: `8 passed`.
- Full local backend plus QA suite: `80 passed, 1 warning`.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`; all five exact L1 success screenshots are still missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.

These screenshots are intentionally kept outside `docs/qa/rehab-mobile-20260706/screenshots/` and use `current-fail-*` filenames, so they cannot satisfy the objective audit's required L1 success evidence. They document the current blockers only:

- Home still shows a false network warning, `setup_required`, `M33`, `M55`, and raw workflow text.
- AI page is still an AI training plan workflow rather than a normal `问康复师` chat.
- Device page still exposes `M33`, `M55`, `Gatekeeper`, and debug entry points instead of a patient binding wizard.
- Profile still shows raw stage/debug/medical constraint content instead of the final cloud account, phone, and safe medical empty-state layout.

The refreshed repair packet now reports `browser_evidence_current.matched = {}` and missing all five exact L1 success screenshot names.

## Stitch Repair Packet Current-Fail Evidence Follow-Up

2026-07-06 continuation work connected the in-app browser failure screenshots directly into the machine-readable Stitch repair packet:

- Updated script: `tools/export_rehab_mobile_stitch_repair_packet.py`
- Updated tests: `tools/test_export_rehab_mobile_stitch_repair_packet.py`
- Refreshed packet: `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`

New packet field:

- `current_fail_evidence`

It lists the current-fail screenshots for `home`, `ai-plan`, `device`, and `profile`, with decoded dimensions and `counts_for_l1_success = false`. Stitch should use these as visual failure references only.

Fresh verification:

- Red test first: `build_repair_packet(..., current_fail_dir=...)` was unsupported.
- Focused objective-audit and repair-packet tests: `9 passed`.
- Full local backend plus QA suite: `81 passed, 1 warning`.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- Live repair packet JSON parse confirms all four current-fail screenshots are listed at `390 x 844`.

## Stitch Prompt V4 Follow-Up

2026-07-06 continuation work turned the live repair packet into a generated Stitch prompt so the frontend handoff no longer drifts from the current release/objective gates:

- New script: `tools/export_rehab_mobile_stitch_prompt.py`
- New tests: `tools/test_export_rehab_mobile_stitch_prompt.py`
- Primary prompt: `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md`
- Refreshed repair packet: `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`

The V4 prompt includes:

- Current Stitch blockers: `home_next_step`, `phone_binding`, `device_binding`, `ask_therapist_safety`, `profile_no_fake_debug`, `browser_qa_evidence`, and `frontend_l1_gate`.
- Non-Stitch blocker: `agent_cloud_model`.
- All four current-fail browser screenshots with `counts_for_l1_success = false`.
- Exact required L1 success screenshot filenames, including `l1-home-390.png`.
- Final Codex verification commands for the combined L1 release gate and objective audit.

Fresh verification:

- Red test first: `tools/export_rehab_mobile_stitch_prompt.py` did not exist.
- Follow-up red test first: repair packet still pointed at V3 before `required_artifacts.stitch_prompt` was switched to V4.
- Focused repair-packet/prompt tests: `5 passed`.
- Full local backend plus QA suite: `83 passed, 1 warning`.
- Live L1 release gate remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` failing, including all five exact L1 success screenshots missing.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## L1 Evidence Bundle Follow-Up

2026-07-06 continuation work added a single export command for the evidence package expected after every large task:

- New script: `tools/export_rehab_mobile_l1_evidence.py`
- New tests: `tools/test_export_rehab_mobile_l1_evidence.py`
- Default output: `artifacts/rehab-mobile-l1-evidence/rehab-mobile-l1-evidence.json`

The evidence bundle records:

- Cloud `/health` status and deployment metadata.
- Git branch, HEAD, and dirty status.
- Combined L1 release gate summary and payload.
- Objective-level L1 audit summary and payload.
- Browser evidence status, including missing exact `390 x 844` screenshots.
- APK HEAD status, size, and content type.
- Required scorecard, runbook, Stitch prompt, repair packet, frontend release, and model relay artifacts.

Fresh verification:

- Red test first: `tools/export_rehab_mobile_l1_evidence.py` did not exist.
- Follow-up red test first: `required_artifacts` did not identify the evidence exporter or default evidence output.
- Focused evidence exporter tests: `2 passed`.
- Full related backend/QA suite: `108 passed, 1 warning`.
- Live evidence export wrote `artifacts/rehab-mobile-l1-evidence/rehab-mobile-l1-evidence-20260706.json`.
- Live evidence summary: `overall = FAIL`, release `FAIL`, objective `FAIL`, `health_ok = true`, `apk_ok = true`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live evidence confirms all five exact L1 success screenshots are still missing and the exported JSON does not contain the staging password.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- The exporter returns exit code `0` by default so it can preserve failure evidence when L1 is blocked; release jobs can add `--fail-on-l1-fail`.
- No cloud runtime deployment was made for this QA/tooling-only change.

## SMS Delivery Ops Follow-Up

2026-07-06 continuation work closed the ops gap between the existing backend SMS webhook path and a safe staging configuration process:

- New provider preflight: `tools/smoke_rehab_sms_provider.py`
- New guarded config tool: `tools/configure_rehab_sms_delivery.py`
- New tests: `tools/test_smoke_rehab_sms_provider.py`, `tools/test_configure_rehab_sms_delivery.py`
- New runbook: `docs/deployments/rehab-mobile-sms-delivery-runbook-20260706.md`
- `.gitignore` now excludes `cloud/rehab-platform/.env` so real SMS tokens are not committed.

Behavior:

- The smoke tool POSTs the exact backend webhook payload shape: `phone`, `code`, `purpose`, `verification_id`, and `expires_in`.
- Smoke output redacts the webhook token, verification code, and full phone number.
- The config tool requires a passing preflight JSON for the same provider and webhook URL before it writes SMS settings.
- Default mode is dry-run; `--execute` is required before `.env` is written.
- The generated settings disable `PHONE_VERIFICATION_DEBUG_CODE_ENABLED` and configure `PHONE_VERIFICATION_SMS_PROVIDER`, `PHONE_VERIFICATION_SMS_WEBHOOK_URL`, and optional `PHONE_VERIFICATION_SMS_WEBHOOK_TOKEN`.

Fresh verification:

- Red tests first: both SMS ops tools were missing.
- Focused SMS ops tests: `8 passed`.
- Phone binding plus SMS ops focused suite: `36 passed, 1 warning`.
- Full related backend/QA suite: `116 passed, 1 warning`.
- Cloud API/APK acceptance remained `overall = PASS`, `p0_failed = 0`, `total = 22`; `P1-PHONE-SMS-001` still warns because staging is in `debug_sms` mode until a real provider is supplied.
- Live L1 release remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` failing, including phone UI wiring, device UI, Ask Therapist UI, profile cleanup, browser success evidence, and cloud model.
- L1 evidence export wrote `artifacts/rehab-mobile-l1-evidence/rehab-mobile-l1-evidence-20260706-sms-ops.json`; summary `health_ok = true`, `apk_ok = true`, and no staging password in the JSON.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- Current staging remains `debug_sms` because no real SMS provider endpoint/token has been supplied.

## Stitch Packet SMS/Evidence Refresh Follow-Up

2026-07-06 continuation work refreshed the machine-readable Stitch handoff so frontend generation receives the latest backend ops constraints:

- Updated `tools/export_rehab_mobile_stitch_repair_packet.py`.
- Updated `tools/export_rehab_mobile_stitch_prompt.py`.
- Refreshed `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`.
- Refreshed `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md`.

New packet/prompt coverage:

- `summary.ops_warnings` now includes `phone_sms_delivery` when `P1-PHONE-SMS-001` is not `PASS`.
- `non_stitch_actions` now includes the SMS provider preflight/config flow and the existing Agent cloud-model flow.
- `required_artifacts` now includes the SMS delivery runbook, SMS smoke tool, SMS config tool, and L1 evidence exporter.
- `verification_commands` now includes `tools/export_rehab_mobile_l1_evidence.py`.
- The repair packet and Stitch prompt no longer include the raw staging email or staging password; they use placeholders instead.

Fresh verification:

- Red repair-packet test first failed because `ops_warnings` was missing.
- Red prompt test first failed because `phone_sms_delivery` and SMS ops commands were not rendered.
- Follow-up red test first caught raw staging credentials in the generated packet/prompt.
- Focused repair-packet/prompt tests: `5 passed`.
- Live refreshed packet summary remains `overall = FAIL`; `ops_warnings = phone_sms_delivery`; `non_stitch_actions = agent_cloud_model, phone_sms_delivery`.
- Live refreshed packet/prompt parse confirmed SMS tools and L1 evidence export are present, with no raw staging email/password.
- Full related backend/QA suite: `116 passed, 1 warning`.
- Cloud API/APK acceptance remained `overall = PASS`, `p0_failed = 0`, `total = 22`; `P1-PHONE-SMS-001 = WARN` and `P0-APK-001 = PASS`.
- Live L1 release remains `FAIL`: API `PASS`, frontend `FAIL`, blockers `frontend_l1_gate` and `agent_cloud_model`.
- Live objective audit remains `FAIL`: `8 / 11` failing, including home next step, phone/device binding UI, Ask Therapist safety UI, profile cleanup, browser success evidence, and cloud model readiness.
- L1 evidence export wrote `artifacts/rehab-mobile-l1-evidence/rehab-mobile-l1-evidence-20260706-stitch-refresh.json`; summary `health_ok = true`, `apk_ok = true`, and no raw staging email/password in the JSON.
- APK HEAD remained `200`, size `4198462`, content type `application/vnd.android.package-archive`.
- No cloud runtime or frontend deployment was made for this tooling/handoff-only change.
- In-app browser device-page resmoke captured `screenshots/stitch-packet-device-qa-430bfdf5-390.png` at `390 x 844`; it remains current-fail evidence only.
- Visible blockers in that browser pass: false `网络未连接`, `setup_required`, `M33`, `M55`, `Gatekeeper`, and a visible `蓝牙调试 / 实机验证` route instead of a full patient device-binding wizard.

## Agent Cloud Model Runtime Follow-Up

2026-07-06 continuation work closed the backend `agent_cloud_model` blocker.
This section supersedes earlier entries in this report that listed
`agent_cloud_model` as a current blocker.

Root cause and fix:

- Cloud Agent safe-answer calls could fail before fallback when model context
  contained non-JSON-serializable values such as datetimes.
- Local regression test added: `test_rehab_agent_falls_back_when_cloud_model_path_raises_type_error`.
- Local backend now catches cloud-model `TypeError`, `ValueError`, and `OSError`
  with the same safe fallback path as provider errors.
- Cloud runtime was patched so model-context JSON serialization uses a safe
  default and provider failures still fall back safely.
- Cloud model relay env persistence was corrected so config writes land in the
  `.env` file read by the running API process.

Cloud deployment:

- Build SHA: `agent-model-env-path-20260706`.
- Build ref: `codex/rehab-mobile-backend-qa-20260706`.
- Build time: `2026-07-06T15:40:39Z`.
- API pid during verification: `2130675`.

Current live Agent state:

- Public config: `P1-AGENT-CONFIG-001 = PASS`.
- Safe Agent answer: `P1-AGENT-MODEL-001 = PASS`.
- Model mode: `cloud_model`.
- Provider/model: `qwen` / `qwen-plus`.
- API key remains configured server-side and is not exposed in public config,
  logs, repair packet, prompt, or evidence bundle.

Fresh verification:

- Focused local Agent/model relay tests: `14 passed, 1 warning`.
- Prompt regression test after removing stale `agent_cloud_model` handoff copy:
  `3 passed`.
- Full local related backend/QA suite:
  `121 passed, 1 warning`.
- Live cloud API/APK acceptance: `overall = PASS`, `p0_failed = 0`, `total = 22`.
- Live L1 release remains `FAIL`: API `PASS`, frontend `FAIL`, blocker
  `frontend_l1_gate` only.
- Live objective audit remains `FAIL`: `7 / 11` failing. Passing objectives now
  include `cloud_deployment`, `login`, `agent_cloud_model`, and `apk_delivery`.
- Refreshed Stitch repair packet now has `non_stitch_blockers = []`; remaining
  Stitch blockers are `home_next_step`, `phone_binding`, `device_binding`,
  `ask_therapist_safety`, `profile_no_fake_debug`, `browser_qa_evidence`, and
  `frontend_l1_gate`.
- In-app browser QA captured
  `docs/qa/rehab-mobile-20260706/screenshots/agent-cloud-ai-plan-20260706-390.jpg`
  at `390 x 844`; it remains current-fail evidence because the page still lacks
  `问康复师` and still exposes `setup_required`/`M33` copy.
- APK HEAD remained `200`, size `4198462`, content type
  `application/vnd.android.package-archive`.

## Stitch Source Scope And APK Mirror Follow-Up

2026-07-06 continuation work verified the real APP frontend branch and tightened
the Stitch handoff around APK parity.

Source evidence:

- Remote branch: `app/rehab-arm-mobile-stitch`.
- Remote commit verified by Codex:
  `eaa08a40cdd3e1e62827809111f2323e7f92556f`.
- Real web frontend path:
  `apps/web/public/rehab-arm-mobile/`.
- Real Android WebView asset path:
  `apps/mobile/rehab-arm-android/www/`.

Handoff updates:

- `tools/export_rehab_mobile_stitch_repair_packet.py` now records the source
  branch, source commit, web edit scope, required L1 pages, and Android WebView
  mirror path.
- `tools/export_rehab_mobile_stitch_prompt.py` now renders a `Source Scope`
  section so Stitch sees the branch, source commit, web edit path, and APK
  mirror requirement before changing frontend files.
- Refreshed `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json` and
  `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` now show
  `non_stitch_blockers = []`, `ops_warnings = phone_sms_delivery`, and the
  APK WebView mirror path.
- Updated `docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md` so it no
  longer lists `agent_cloud_model` as a current backend blocker.
- Added `docs/superpowers/plans/2026-07-06-rehab-mobile-stitch-l1-closure.md`
  as the step-by-step closure plan from Stitch input through web deploy, APK
  mirror, browser QA, evidence export, and git commit.

Fresh verification:

- Focused repair-packet/prompt tests: `6 passed`.
- Full related backend/QA suite:
  `121 passed, 1 warning`.
- Live cloud API/APK acceptance:
  `overall = PASS`, `p0_failed = 0`, `total = 22`.
- Live cloud health during this verification reported build
  `rehab-vla-fast-async-20260706`, ref `ai/game-loop-core`, build time
  `2026-07-06T15:56:40Z`, and pid `2146425`.
- Live L1 release remains `FAIL`: API `PASS`, frontend `FAIL`, blocking gate
  `frontend_l1_gate` only.
- Live objective audit remains `FAIL`: `7 / 11` failing, with blockers
  `home_next_step`, `phone_binding`, `device_binding`,
  `ask_therapist_safety`, `profile_no_fake_debug`, `browser_qa_evidence`, and
  `combined_l1_release`.
- L1 evidence bundle exported to
  `artifacts/rehab-mobile-l1-evidence/rehab-mobile-l1-evidence-20260706-stitch-source-scope.json`;
  summary remains `overall = FAIL`, `health_ok = true`, `apk_ok = true`,
  release blocker `frontend_l1_gate`.
- APK HEAD remained `200`, size `4198462`, content type
  `application/vnd.android.package-archive`.
- In-app browser QA captured two current-fail mobile screenshots at
  `390 x 844`:
  `docs/qa/rehab-mobile-20260706/screenshots/stitch-source-scope-current-ai-plan-20260706-390x844.jpg`
  and
  `docs/qa/rehab-mobile-20260706/screenshots/stitch-source-scope-current-device-20260706-390x844.jpg`.
  The Agent page still lacks `问康复师` and still shows `setup_required`/`M33`;
  the device page still shows `M33`, `M55`, and `Gatekeeper`, and still lacks
  `打开康复设备电源`.
- No cloud runtime or frontend deployment was made for this documentation and
  handoff-tooling change.

## APK WebView Mirror Gate And M33 Merge Follow-Up

2026-07-07 continuation work pulled current remotes and merged the same-history
remote baseline into the App QA branch.

Git update:

- Fetched `origin` and the verified APP frontend branch
  `app/rehab-arm-mobile-stitch`.
- `origin/M55` advanced remotely, but it has no merge base with the current App
  QA branch, so it was not merged.
- `origin/M33` has a merge base with the current branch and was merged with
  merge commit `e8cae16f`.
- Post-merge relationship: current branch is `47` commits ahead and `0`
  commits behind `origin/M33`.
- No push was performed.

APK parity guard:

- Added `tools/verify_rehab_mobile_webview_mirror.py` to verify that
  `apps/mobile/rehab-arm-android/www/` mirrors
  `apps/web/public/rehab-arm-mobile/` byte-for-byte.
- The verifier checks required pages, missing files, changed files, and stale
  extra files such as old debug pages.
- `tools/prepare_rehab_mobile_frontend_release.py` now records the WebView
  mirror verifier in release manifest verification commands.
- `tools/verify_rehab_mobile_frontend_release.py` now rejects release manifests
  that omit the WebView mirror verification command.
- Refreshed Stitch repair packet and V4 prompt now include
  `webview_mirror_verifier`, the `robocopy ... /MIR` mirror step, and
  `webview-mirror-verification.json`.

Fresh verification:

- Merge-sensitive and release-tool tests:
  `17 passed`.
- WebView mirror/release/stitch evidence focused suite:
  `21 passed`.
- Full related local backend/QA suite:
  `130 passed, 1 warning`.
- Live cloud API/APK acceptance:
  `overall = PASS`, `p0_failed = 0`, `total = 22`.
- Live L1 release remains `FAIL`: API `PASS`, frontend `FAIL`, blocking gate
  `frontend_l1_gate` only.
- APK HEAD remained `200`, size `4198462`, content type
  `application/vnd.android.package-archive`.
- No cloud runtime, deployed web frontend, or APK package was changed in this
  follow-up.

## Stitch MCP Generation Attempt Follow-Up

2026-07-07 continuation work verified that the Google Stitch MCP HTTP endpoint
is reachable from Codex and supports project/screen tools.

Stitch MCP actions:

- Initialized the Stitch MCP endpoint successfully.
- Listed available tools including `create_project`,
  `generate_screen_from_text`, and `edit_screens`.
- Created Stitch project `projects/1542023501541093471`, title
  `Rehab Mobile L1 Closure`.
- Generated and iterated mobile screen candidates for `home.html`,
  `profile.html`, `device.html`, and `ai-plan.html`.

Result:

- The Stitch-generated screens were not accepted for frontend use.
- Generated HTML avoided raw engineering/debug terms, but failed exact L1 copy
  requirements:
  - `home.html`: missing `查看康复师建议`, `问康复师`.
  - `profile.html`: missing `我的康复档案`, `绑定手机号`, `验证码`.
  - `device.html`: missing `绑定设备`, `打开康复设备电源`.
  - `ai-plan.html`: missing `问康复师`.
- No Stitch-generated HTML was copied into
  `apps/web/public/rehab-arm-mobile/` or
  `apps/mobile/rehab-arm-android/www/`.
- Detailed attempt record:
  `docs/stitch/rehab-mobile-l1-stitch-mcp-attempt-20260707.md`.

Fresh live gate after this attempt:

- `tools/qa_rehab_mobile_l1_release.py`: API `PASS`, frontend `FAIL`, blocker
  `frontend_l1_gate` only.

## 2026-07-07 Stitch MCP Home Literal Copy Resmoke

Codex used the Stitch MCP endpoint again, this time with a narrow `home.html`
prompt and then an `edit_screens` literal-copy correction prompt.

Evidence:

- Source branch mirror refreshed to
  `app/rehab-arm-mobile-stitch@eaa08a40cdd3e1e62827809111f2323e7f92556f`.
- Latest APP source local frontend gate remains `FAIL`, `failed = 5`.
- Latest APP source Android WebView mirror gate remains `FAIL`; the checkout
  has `apps/web/public/rehab-arm-mobile/`, but no
  `apps/mobile/rehab-arm-android/www/` mirror directory.
- Stitch home candidate `fd3aae8953714a058cd8b54a9217a223` generated
  `artifacts/stitch/l1-mcp-iteration-20260707/home-flash.html`.
- Stitch home edit candidate `bdcea50a83a74eb68075807aaf7120dc` generated
  `artifacts/stitch/l1-mcp-iteration-20260707/home-flash-edit-literal.html`.

Result:

- The candidate home HTML no longer contains the raw forbidden terms scanned by
  `tools/qa_rehab_mobile_l1_frontend.py`.
- The candidate still fails visible copy requirements. It renders
  `开始康复训练` and `咨询治疗师` instead of the required
  `查看康复师建议` and `问康复师`.
- No Stitch-generated HTML was copied into frontend source or the APK WebView
  mirror.

QA hardening added after this failed resmoke:

- `L1-HOME-STATIC-001` now requires `查看康复师建议` as well as `问康复师`.
- `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` now includes
  an `Exact Release-Gated Visible Copy` section listing the exact strings
  Stitch must preserve page by page.
- Fresh deployed frontend gate after the hardening still returns `overall =
  FAIL`, `failed = 5`; `home.html` is missing both `查看康复师建议` and
  `问康复师` and still exposes `M33`, `M55`, and `RoboRehab Controller`.

## 2026-07-07 Stitch MCP Home Entity Copy Resmoke

Codex ran another narrow Stitch MCP `home.html` experiment using HTML numeric
character references for the exact release-gated copy.

Evidence:

- Stitch screen: `8d43c827e5464979a08926467114eda3`,
  title `首页 - 领动康复手臂 (QA 实验版)`.
- Downloaded candidate:
  `artifacts/stitch/l1-entity-iteration-20260707/home-entity.html`.
- The downloaded candidate rendered visible text containing
  `查看康复师建议` and `问康复师`.
- Direct page-gate check using `tools/qa_rehab_mobile_l1_frontend.py` logic
  returned `PASS` for `L1-HOME-STATIC-001` with no forbidden hits.

Result:

- HTML entity copy is a working strategy for preventing Stitch from rewriting
  exact Chinese release labels.
- The generated candidate is not accepted as frontend source because it covers
  only `home.html`, includes demo wording such as `李先生`, and has not passed
  the full four-page integration gate.
- No Stitch-generated HTML was copied into frontend source or the APK WebView
  mirror.

QA hardening added after this resmoke:

- The generated Stitch V4 prompt now includes HTML entity fallback snippets for
  every exact release-gated visible string.
- `tools/qa_rehab_mobile_l1_frontend.py` now matches integration requirements
  against both raw and HTML-decoded source, so an accessibility label encoded
  as numeric HTML entities can still satisfy the `问康复师` contract when the
  browser-visible label is correct.

## 2026-07-07 Stitch MCP Four-Page Entity Candidate

Codex extended the entity-copy strategy from `home.html` to all four required
mobile pages and downloaded the candidate into
`artifacts/stitch/l1-full-entity-candidate-20260707/`.

Generated Stitch screens:

- `home.html`: `4fd2a7955ae04e528e6fa5aacc18a895`.
- `profile.html`: `f1d1fcbf9cc844b6aee6ffa1a2584b6f`.
- `device.html`: first generated as `2135179937104311b1461cbe0eb581a8`,
  then regenerated with hexadecimal entities as
  `2ec9f9b9acb545668b8d06f4b609da0a` because the decimal entity pass produced
  a typo (`绑定菮备`).
- `ai-plan.html`: `648dfa3b393b4a0ea1d3227b3686cc82`.

Source-dir gate:

- Command:
  `tools/qa_rehab_mobile_l1_frontend.py --source-dir artifacts/stitch/l1-full-entity-candidate-20260707 --output artifacts/stitch/l1-full-entity-candidate-20260707/frontend-l1-source-gate.json`
- Initial result before fake/demo identity hardening: `overall = PASS`,
  `failed = 0`, `total = 5`.
- Current hardened result after browser QA: `overall = FAIL`, `failed = 1`,
  `total = 5`.
- Current blocking gate: `L1-HOME-STATIC-001`, forbidden hit `李先生`.
- Current non-blocking candidate gates: profile `PASS`, device `PASS`, Agent
  `PASS`, integration `PASS`.

Result:

- This was the first Stitch-generated four-page artifact candidate that passed
  Codex's earlier local L1 frontend source gate.
- It is now rejected by the hardened source gate because patient-facing screens
  may not show fake/demo names.
- It was not deployed and no APK was rebuilt because the candidate has not been
  applied to the actual `app/rehab-arm-mobile-stitch` frontend branch, mirrored
  into the Android WebView bundle, or browser-QA verified.
- The candidate still needs product-copy cleanup before deployment; for example
  the home page includes demo-like wording such as `李先生`.

Prompt hardening:

- `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` now emits
  hexadecimal HTML entity fallback snippets. The device candidate showed that
  hexadecimal entities are safer for Stitch than decimal entities for the
  `绑定设备` label.

## 2026-07-07 Stitch Entity Candidate Browser QA

Codex opened the four-page Stitch entity candidate through the in-app browser
from local preview `http://127.0.0.1:4187/` and re-captured the pages with an
explicit `390 x 844` screenshot clip.

Candidate screenshots:

- `screenshots/stitch-entity-candidate-home-20260707-390x844.png`: `390 x 844`.
- `screenshots/stitch-entity-candidate-profile-20260707-390x844.png`: `390 x 844`.
- `screenshots/stitch-entity-candidate-device-20260707-390x844.png`: `390 x 844`.
- `screenshots/stitch-entity-candidate-ai-plan-20260707-390x844.png`: `390 x 844`.

Browser QA result: `REJECTED`.

- `home.html` still shows fake/demo identity copy: `李先生`.
- `home.html` primary actions are usable sizes: `查看康复师建议` measured
  `335 x 56`, and `问康复师` measured `335 x 48`.
- `profile.html` had no fake/debug hits in this browser pass; `绑定手机号`
  measured `119 x 50`.
- `device.html` had no fake/debug hits in this browser pass; `绑定设备` measured
  `285 x 56`.
- `ai-plan.html` had no fake/debug hits, but the header `问康复师` action
  measured only `64 x 24`, below the required `44px` minimum touch height.
- No horizontal overflow was found in the sampled first viewport checks.

This candidate remains useful because it proves the entity-copy approach can
preserve the exact required labels, but it is still not accepted for deployment.
The current hardened source gate also fails it for `李先生`. It has not been
applied to the real `app/rehab-arm-mobile-stitch` branch, mirrored into the
Android WebView assets, deployed to cloud, or packaged into a new APK.

Prompt hardening added after browser QA:

- The Stitch V4 prompt now includes a `Stitch Browser Candidate QA Blockers`
  section.
- The prompt explicitly rejects fake/demo identities such as `李先生`,
  `张先生`, `王女士`, `患者A`, and `ID: 8829`.
- The prompt requires the `问康复师` entry to be a real button or link with
  `aria-label` and a minimum `48px` touch target in both width and height.
- `tools/qa_rehab_mobile_l1_frontend.py` now rejects common fake/demo
  identities (`李先生`, `张先生`, `王女士`, `患者A`) in normal user screens.

## 2026-07-07 Stitch Clean Candidate Strict Browser Gate

Codex generated and served a cleaner four-page Stitch candidate from
`artifacts/stitch/l1-clean-candidate-20260707/`.

Source gate:

- Command:
  `tools/qa_rehab_mobile_l1_frontend.py --source-dir artifacts/stitch/l1-clean-candidate-20260707 --output artifacts/stitch/l1-clean-candidate-20260707/frontend-l1-source-gate.json`.
- Result: `overall = PASS`, `failed = 0`, `total = 5`.
- Screenshots captured at `390 x 844`:
  - `screenshots/stitch-clean-pass-home-20260707-390x844.png`.
  - `screenshots/stitch-clean-pass-profile-20260707-390x844.png`.
  - `screenshots/stitch-clean-pass-device-20260707-390x844.png`.
  - `screenshots/stitch-clean-pass-ai-plan-20260707-390x844.png`.

Strict browser gate:

- New tool:
  `tools/qa_rehab_mobile_browser_metrics.py`.
- Strict metrics input:
  `artifacts/stitch/l1-clean-candidate-20260707/browser-qa-live-strict-390x844.json`.
- Gate output:
  `artifacts/stitch/l1-clean-candidate-20260707/browser-metrics-gate-live-strict-390x844.json`.
- Committed summary:
  `docs/qa/rehab-mobile-20260706/browser-metrics-clean-candidate-live-strict-20260707.json`.
- Result: `overall = FAIL`.
- Blocking issue: `ai-plan.html` still has undersized interactive targets:
  back button `40 x 40`, plus bottom-nav links at `28 x 48`.
- Failure screenshot:
  `screenshots/stitch-clean-candidate-ai-plan-touch-fail-20260707-390x844.png`.

Stitch execution status:

- `tools/list` remains reachable from the Stitch MCP endpoint.
- `generate_screen_from_text` and `edit_screens` currently return `401` with a
  service message requiring OAuth/login credentials, so Codex could not generate
  the v4 touch-target fix in this pass.
- No generated clean candidate was copied into the real App branch, mirrored
  into Android WebView assets, deployed to cloud, or packaged into a new APK.

Prompt/tooling hardening:

- `tools/qa_rehab_mobile_browser_metrics.py` now makes browser metric failures
  machine-readable instead of relying on visual inspection alone.
- The V4 Stitch prompt now requires every interactive element to render at least
  `48 x 48`, every back button at least `48 x 48`, and every bottom navigation
  item at least `64 x 48`.

## 2026-07-07 Browser Metrics Release Gate Follow-Up

Codex promoted the strict browser metrics check from a one-off QA tool into the
frontend release packaging and verification chain.

Tooling changes:

- `tools/prepare_rehab_mobile_frontend_release.py` now records
  `required_browser_metrics_report = browser-metrics-l1-390x844.json` and the
  `qa_rehab_mobile_browser_metrics.py` command in the release manifest.
- `tools/verify_rehab_mobile_frontend_release.py` now includes
  `FRONTEND-RELEASE-BROWSER-METRICS` and rejects a release manifest that omits
  the browser metrics input/output contract or command.
- `tools/prepare_rehab_mobile_frontend_release.py` no longer writes raw staging
  email/password values into release manifest post-deploy commands; runtime
  credentials must come from the execution environment.
- `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json` and
  `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` were refreshed
  so Stitch handoff, packaging, and deployment review all require the rendered
  browser metrics gate.

Fresh verification:

- Focused release/stitch tooling suite:
- `19 passed`.

No cloud frontend deployment or APK rebuild was made for this tooling-only
follow-up.

## 2026-07-07 Browser Metrics Objective Audit Follow-Up

Codex promoted the same strict browser metrics gate into the objective-level L1
audit and evidence exporter.

Tooling changes:

- `tools/qa_rehab_mobile_l1_objective_audit.py` now requires browser evidence
  to include both exact L1 success screenshots and a saved
  `L1-BROWSER-METRICS-001` report with `overall = PASS`.
- Missing, invalid, or failing browser metrics JSON now keeps
  `browser_qa_evidence` as an objective blocker even if screenshots are present.
- `tools/export_rehab_mobile_l1_evidence.py` now records
  `target.browser_metrics_json` and preserves the objective audit's
  `browser_evidence.browser_metrics` detail in the exported evidence bundle.

Current effect:

- The clean Stitch candidate remains rejected because
  `docs/qa/rehab-mobile-20260706/browser-metrics-clean-candidate-live-strict-20260707.json`
  is `overall = FAIL`.
- Future release candidates cannot pass objective audit by providing screenshots
  alone; the rendered mobile interaction metrics must also be green.

Fresh verification:

- Red objective-audit tests first failed because `audit_objective()` did not
  accept browser metrics evidence.
- Red evidence-exporter test first failed because `target.browser_metrics_json`
  was missing from exported L1 evidence.
- Red repair-packet test first failed because objective audit ran before the
  browser metrics gate and did not pass `--browser-metrics-json`.
- Red UTF-16 loader tests first failed because saved gate payloads with
  `FF FE` BOM could not be read by the exporters.
- Red browser metrics regression first failed because re-reading an existing
  failed `L1-BROWSER-METRICS-001` gate output incorrectly returned `PASS`.
- Red browser metrics coverage test first failed because a raw metrics report
  covering only `home` could still pass.
- Focused related QA/tooling suite: `33 passed`.
- Re-running `tools/qa_rehab_mobile_browser_metrics.py` against the committed
  clean-candidate gate output now preserves `overall = FAIL` and returns exit
  code `1`.
- Evidence snapshot exported to
  `artifacts/rehab-mobile-l1-evidence/rehab-mobile-l1-evidence-20260707-browser-objective.json`;
  current staging remains `overall = FAIL`, with `health_ok = true`,
  `apk_ok = true`, release blocker `frontend_l1_gate`, and objective blocker
  `browser_qa_evidence` carrying `browser_metrics.status = FAIL`.

No cloud frontend deployment or APK rebuild was made for this tooling-only
follow-up; the APK URL was still verified separately before commit.

## 2026-07-07 Current Cloud Browser QA Resmoke

Codex reconnected the in-app browser, made it visible for QA, and fixed the
viewport to `390 x 844` before opening the current deployed cloud pages.

Fresh screenshots:

The browser runtime saved JPEG payloads under the existing `.png` screenshot
naming convention; each file below was decoded and verified at `390 x 844`.

- `screenshots/current-fail-home-20260707-390x844.png`: `390 x 844`,
  `55540` bytes.
- `screenshots/current-fail-profile-20260707-390x844.png`: `390 x 844`,
  `48959` bytes.
- `screenshots/current-fail-device-20260707-390x844.png`: `390 x 844`,
  `53156` bytes.
- `screenshots/current-fail-ai-plan-20260707-390x844.png`: `390 x 844`,
  `54552` bytes.

Fresh live release result with staging credentials supplied from the local
environment:

- `tools/qa_rehab_mobile_l1_release.py --timeout 60`: `overall = FAIL`.
- API: `PASS`, `p0_failed = 0`, `total = 22`.
- Frontend: `FAIL`, `failed = 5`.
- Blocking gate: `frontend_l1_gate`.

Fresh objective audit:

- `tools/qa_rehab_mobile_l1_objective_audit.py --timeout 60`: `overall = FAIL`.
- Blocking requirements: `home_next_step`, `phone_binding`,
  `device_binding`, `ask_therapist_safety`, `profile_no_fake_debug`,
  `browser_qa_evidence`, and `combined_l1_release`.
- `agent_cloud_model` is now `PASS`.

Browser findings:

- Home still shows `网络未连接`, `setup_required`, `M33`, and `M55`, and still
  lacks the exact L1 actions `查看康复师建议` and `问康复师`.
- Profile still exposes workflow/debug copy plus unsafe fake-medical style
  content such as `避免过度伸展`, and does not expose the profile phone
  verification path required by L1.
- Device still exposes `Gatekeeper`, `M33`, `M55`, and debug pairing affordances
  instead of a patient binding wizard led by `绑定设备` and
  `打开康复设备电源`.
- `ai-plan.html` remains an AI draft/planning page rather than a working
  `问康复师` chat surface.

## 2026-07-07 Stitch Ask Therapist Single-Page Fix

Codex used the Stitch MCP again after browser QA confirmed the current deployed
frontend was still blocked.

Stitch evidence:

- New project: `projects/323711356322969905`.
- Initial Ask Therapist screen: `9deadaaf358a4a908bd704f580e6a69f`.
- Edited/fixed Ask Therapist screen: `f1a50687ed4d429786f9d84e7e37a5cf`.
- Downloaded HTML artifact:
  `artifacts/stitch/l1-browser-qa-fix-20260707/ai-plan-stitch-fixed.html`.
- Browser screenshot:
  `screenshots/stitch-ai-plan-fix-candidate-v2-20260707-390x844.png`.

Local browser QA result for the fixed single-page candidate:

- Required copy present: `问康复师`, `云端康复师已连接`, and the unsafe-control
  refusal text.
- Forbidden engineering/demo hits: none.
- Horizontal overflow: none (`bodyWidth = 388`, viewport `390`).
- Back, add, input, send, and bottom nav controls all measured at least
  `48px` high.
- Bottom nav controls measured `64 x 48`.
- Composer bottom: `768`; nav top: `789`; visible gap: `21px`.

Result: useful partial frontend progress, but **not deployable**. It covers
only `ai-plan.html`; it has not been applied to the real
`app/rehab-arm-mobile-stitch` branch, wired to live API integration, mirrored
into Android WebView assets, verified as part of all four pages, deployed to
cloud, or packaged into a new APK.

## 2026-07-07 Browser Metrics Consumer Coverage Follow-Up

Codex tightened the consumers of browser metrics evidence, not only the metrics
producer.

Tooling changes:

- `tools/qa_rehab_mobile_l1_objective_audit.py` now independently requires the
  saved metrics gate to cover `home`, `profile`, `device`, and `ai-plan`.
- `tools/verify_rehab_mobile_frontend_release.py` now performs the same
  independent coverage check before cloud deployment.
- A hand-written metrics file with `summary.overall = PASS` and
  `L1-BROWSER-METRICS-001.status = PASS` is still rejected when
  `checked_pages` does not cover all required L1 pages or `missing_pages` is
  non-empty.

Fresh verification:

- Red objective-audit test first failed because a `PASS` metrics file covering
  only `home` still cleared `browser_qa_evidence`.
- Red release-verifier test first failed because the same incomplete metrics
  gate still cleared `FRONTEND-RELEASE-BROWSER-METRICS`.
- Focused objective/verifier tests: `19 passed`.

No cloud frontend deployment or APK rebuild was made for this tooling-only
follow-up; the APK URL was still verified separately before commit.

## 2026-07-07 Browser Screenshot Evidence Hardening Follow-Up

Codex tightened the final browser screenshot evidence gate so an L1 audit cannot
be satisfied by image-header placeholders with the right dimensions.

Tooling changes:

- `tools/qa_rehab_mobile_l1_objective_audit.py` now records
  `minimum_screenshot_bytes = 1024` and rejects exact-name browser evidence
  files that are smaller than that threshold.
- Rejected small files are reported under
  `browser_qa_evidence.evidence.invalid_files`, next to existing
  `missing` and `invalid_dimensions` details.
- `tools/export_rehab_mobile_l1_evidence.py` preserves those fields in the L1
  evidence bundle, so final handoff JSON shows whether the screenshots are
  real captures or placeholders.

Fresh verification:

- Red objective-audit test first failed because header-only `390 x 844` PNG
  files still counted as L1 browser evidence.
- Focused objective/evidence exporter tests: `12 passed`.

No cloud frontend deployment or APK rebuild was made for this tooling-only
follow-up; the APK URL was still verified separately before commit.

## 2026-07-07 Browser Metrics Deploy Verification Follow-Up

Codex tightened the deployment-preflight chain so a prepared frontend release
cannot pass verification by only listing the browser metrics command.

Tooling changes:

- `tools/verify_rehab_mobile_frontend_release.py` now opens the declared
  `browser-metrics-gate.json` next to the release manifest and requires:
  `summary.overall = PASS`, `summary.failed = 0`, and
  `L1-BROWSER-METRICS-001.status = PASS`.
- Missing or failing browser metrics gate output now fails
  `FRONTEND-RELEASE-BROWSER-METRICS`.
- `tools/prepare_rehab_mobile_frontend_release.py` now orders post-package
  commands so `qa_rehab_mobile_browser_metrics.py` runs before
  `verify_rehab_mobile_frontend_release.py`.
- The generated V4 Stitch prompt's `After Stitch Hands Back Frontend Files`
  section uses the same order, preventing a manual release review from checking
  the manifest before metrics evidence exists.

Fresh verification:

- Red release-verifier tests first failed because missing and failing
  `browser-metrics-gate.json` files still produced `overall = PASS`.
- Red release-manifest ordering test first failed because the verifier command
  came before the metrics command.
- Red Stitch prompt ordering test first failed for the same old command order.
- Focused release/prompt tests: `16 passed`.

No cloud frontend deployment or APK rebuild was made for this tooling-only
follow-up; the APK URL was still verified separately before commit.

## 2026-07-07 Stitch Full Four-Page Candidate V3

Codex used Stitch MCP project `projects/323711356322969905` to produce a full
four-page local candidate after the earlier single-page Ask Therapist fix.

Generated/final Stitch screens:

- Home: `767c6e263ec646f7b27664c385e3ba4c`.
- Profile: `b1c634dd4d6640beac7fc7a9a3515cb7`.
- Device: `aadf5ed620314ac1b0a33a27089e2cd4`.
- Ask Therapist: `5a10e02454c044f38e60a7292064566b`.

Local source gate:

- Command:
  `tools/qa_rehab_mobile_l1_frontend.py --source-dir artifacts/stitch/l1-full-browser-qa-candidate-20260707 --output artifacts/stitch/l1-full-browser-qa-candidate-20260707/frontend-l1-source-gate-v3.json`.
- Committed report:
  `docs/qa/rehab-mobile-20260706/frontend-l1-source-gate-stitch-full-candidate-v3-20260707.json`.
- Result: `overall = PASS`, `failed = 0`, `total = 5`.
- The integration gate now includes phone resend cooldown source tokens
  `PHONE_CODE_RESEND_TOO_SOON` plus `retry_after`, and Agent model-status source
  token `model_status`.

In-app browser QA:

- Viewport: `390 x 844`.
- Local preview: `http://127.0.0.1:4194/`.
- Screenshots:
  - `screenshots/stitch-full-candidate-v3-home-20260707-390x844.png`.
  - `screenshots/stitch-full-candidate-v3-profile-20260707-390x844.png`.
  - `screenshots/stitch-full-candidate-v3-device-20260707-390x844.png`.
  - `screenshots/stitch-full-candidate-v3-ai-plan-20260707-390x844.png`.
- Browser metrics report:
  `docs/qa/rehab-mobile-20260706/browser-metrics-stitch-full-candidate-v3-20260707.json`.
- Result: `overall = PASS`; checked pages were `home`, `profile`, `device`, and
  `ai-plan`.
- No fake/demo copy hits, undersized touch targets, input/nav overlap,
  horizontal overflow, or vertical text issues were found.

Acceptance boundary:

- This is the first local Stitch candidate in this project that passes both the
  L1 source gate and the strict browser metrics gate across all four required
  pages.
- It is **not** counted as deployed L1 success yet. The generated HTML has not
  been applied to the real `app/rehab-arm-mobile-stitch` branch, mirrored into
  the Android WebView asset bundle, deployed to the cloud URL, packaged into a
  new APK, or verified by the combined cloud L1 release gate.

## 2026-07-07 API-Mock Source Gate Hardening

After inspecting the v3 Stitch candidate, Codex found that the candidate still
contained simulated frontend behavior. For example, Profile used `mockData` and
a `Simulate API response` comment for phone verification instead of relying only
on the real backend response.

Tooling changes:

- `tools/qa_rehab_mobile_l1_frontend.py` now rejects source that includes
  `mockData`, mock response language, `Simulate API response`, `In real app`,
  or console-only behavior in the frontend integration contract.
- New regression:
  `tools/test_qa_rehab_mobile_l1_frontend.py::test_frontend_integration_contract_rejects_mocked_api_behavior`.
- `tools/export_rehab_mobile_stitch_prompt.py` now tells Stitch that generated
  JavaScript must call real backend endpoints and may not use mock/simulated
  API behavior for phone verification, device binding, or Ask Therapist
  messages.
- `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` was regenerated
  with this hard rule.

Fresh verification:

- Red regression first failed because a v3-style page with all source tokens
  but `mockData` still returned `PASS`.
- Focused frontend gate tests after implementation: `14 passed`.
- Focused Stitch prompt tests after implementation: `4 passed`.
- Hardened v3 source-gate report:
  `docs/qa/rehab-mobile-20260706/frontend-l1-source-gate-stitch-full-candidate-v3-hardened-20260707.json`.
- Hardened v3 result: `overall = FAIL`, blocking requirement
  `no_mock_api_behavior`, forbidden source hits `mockData`,
  `Simulate API response`, and `In real app`.

Result:

- The v3 candidate remains useful visual/browser evidence, but is now rejected
  for deployment. The next accepted Stitch output must make real cloud API calls
  before it can be copied into the real App branch, deployed, or packaged into
  an APK.

## 2026-07-07 API Action POST Gate Hardening

Codex tightened the same frontend source gate again so generated pages cannot
pass by merely mentioning endpoint strings. Critical user actions must now show
source evidence of real POST requests.

Tooling changes:

- `tools/qa_rehab_mobile_l1_frontend.py` now requires POST source evidence for:
  - `phone_verification_start_post`
  - `phone_verification_confirm_post`
  - `device_bind_post`
  - `agent_messages_post`
- `tools/export_rehab_mobile_stitch_prompt.py` now tells Stitch to use
  `method: 'POST'` for phone verification start/confirm, device binding, and
  Ask Therapist messages.
- `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` was regenerated
  with the POST requirement.

Fresh verification:

- Red regression first failed because a source bundle that mentioned every
  endpoint and error code, but omitted POST methods, still returned `PASS`.
- Focused frontend gate tests after implementation: `15 passed`.
- Focused Stitch prompt tests after implementation: `4 passed`.
- Release/prepare/deploy verifier suite after implementation: `20 passed`.
- Post-hardened v3 source-gate report:
  `docs/qa/rehab-mobile-20260706/frontend-l1-source-gate-stitch-full-candidate-v3-post-hardened-20260707.json`.
- Post-hardened v3 result: `overall = FAIL`, blocking requirements
  `no_mock_api_behavior`, `phone_verification_start_post`,
  `phone_verification_confirm_post`, `device_bind_post`, and
  `agent_messages_post`.

Stitch status:

- Stitch MCP still returns `401 invalid authentication credentials` for
  `list_screens`, so Codex could not request a new production API-integrated
  frontend candidate in this pass.
- The real App branch `app/rehab-arm-mobile-stitch` remains clean and unchanged.

## 2026-07-07 Live API Fixture Refresh And Stitch Auth Resmoke

Codex refreshed the Stitch API fixture from the live cloud staging API after the
POST-action gate hardening, without touching frontend source.

Fresh live evidence:

- `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json` regenerated at
  `2026-07-06T21:10:05Z`.
- Fixture privacy check passed: no raw staging email, password, access token
  value, or numeric `debug_code` value.
- Fixture still contains the exact user-facing `patient_view` core copy:
  `问康复师`, `查看康复师建议`, `打开康复设备电源`, and `手机号`.
- Agent safe response now reports `model_status.mode = cloud_model`, provider
  `qwen`, model `qwen-plus`.
- Unsafe Agent request still returns `UNSAFE_MOTION_REQUEST`.
- Phone verification start/confirm remains runnable in staging and the confirm
  response reports `phone_verified = true`.

Fresh gates:

- `tools/qa_rehab_mobile_l1_release.py --timeout 30`: `overall = FAIL`,
  API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate` only.
- `tools/qa_rehab_mobile_l1_objective_audit.py --timeout 30
  --browser-metrics-json docs/qa/rehab-mobile-20260706/browser-metrics-stitch-full-candidate-v3-20260707.json`:
  `overall = FAIL`, `7 / 11` requirements failing. `agent_cloud_model`,
  `cloud_deployment`, `login`, and `apk_delivery` pass.
- `/health` reports deployment metadata build SHA `a4d1c1565de3`, ref
  `ai/game-loop-core`, build time `2026-07-06T20:59:56Z`, `app_env=staging`.
- `/api/rehab-arm/app/v1/public-config` reports Agent model readiness
  `cloud_model_configured`, provider `qwen`, model `qwen-plus`; phone delivery
  remains `debug_sms`, reason `debug_code_enabled`.

Stitch status:

- `list_screens` on project `323711356322969905` still returns
  `401 invalid authentication credentials`.
- Because no accepted Stitch output exists, Codex did not deploy frontend
  assets or rebuild the APK in this pass.

## 2026-07-07 L1 UI Contract Handoff Tightening

Codex found that the full sanitized API fixture is still too broad for direct
Stitch UI generation. It is useful for raw response shape, but it also carries
legacy/public-config material such as device protocol and debug readiness
fields that should not influence normal patient screens.

New handoff artifact:

- Added `tools/export_rehab_mobile_stitch_ui_contract.py`.
- Added `docs/stitch/rehab-mobile-l1-ui-contract-20260707.json`, generated from
  `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json` at
  `2026-07-07T06:20:00Z`.
- The UI contract is `6679` bytes and contains only the L1 page contract,
  action API calls, phone verification states, device conflict code, Agent safe
  answer/unsafe refusal contract, and cloud model status.
- The UI contract verifies the required action methods:
  `login = POST`, `bootstrap = GET`, `phone_verification_start = POST`,
  `phone_verification_confirm = POST`, `device_bind = POST`,
  `agent_message = POST`.
- The UI contract omits `m33_legacy_spp_profile`, `debug_code`, raw staging
  email, and access-token values.

Prompt/packet updates:

- `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json` now lists the UI
  contract as a required artifact.
- `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` now tells
  Stitch to use the L1 UI contract for visible copy, page fields, and action
  API wiring, and to use the full fixture only for raw response shape.

Fresh verification:

- Red tests first failed because the UI-contract exporter did not exist and the
  Stitch prompt did not reference the contract.
- `tools/test_export_rehab_mobile_stitch_ui_contract.py`: `2 passed`.
- `tools/test_export_rehab_mobile_stitch_prompt.py` focused prompt test:
  `1 passed`.
- `tools/test_export_rehab_mobile_stitch_repair_packet.py` focused repair
  packet test: `1 passed`.
- Stitch `list_screens` on project `323711356322969905` still returns
  `401 invalid authentication credentials`, so no new frontend candidate was
  generated or deployed in this pass.

## 2026-07-07 Post-Deploy Objective Audit Evidence Path Hardening

Codex tightened the frontend release manifest post-deploy commands so the
objective audit uses the browser metrics gate generated during the same release
instead of relying on the objective audit default path.

Tooling change:

- `tools/prepare_rehab_mobile_frontend_release.py` now emits:
  `tools\qa_rehab_mobile_l1_objective_audit.py --browser-metrics-json artifacts/rehab-mobile-frontend-release/browser-metrics-gate.json`.
- `tools/test_prepare_rehab_mobile_frontend_release.py` and
  `tools/test_deploy_rehab_mobile_frontend_release.py` now require that command
  in the release manifest and deploy plan.

Fresh verification:

- Red tests first failed because the release manifest only called
  `qa_rehab_mobile_l1_objective_audit.py` without `--browser-metrics-json`.
- Focused tests passed after implementation.
- Release/verify/deploy suite: `20 passed`.
- Frontend/prompt/repair packet suite: `23 passed`.
- APK HEAD still returns `200 OK`, content length `4198462`.

No cloud deploy or APK rebuild was performed because this pass changed only
QA/release tooling and documentation, not frontend runtime assets.

## 2026-07-07 Stitch Frontend Promotion Gate

Codex added a conservative promotion gate between Stitch output and the real App
branch so a visual candidate cannot be copied into production web assets or the
Android WebView bundle unless it first passes the local L1 source gate.

Tooling changes:

- Added `tools/promote_rehab_mobile_stitch_frontend.py`.
- The tool requires an explicit `--stitch-source-dir`, runs
  `tools/qa_rehab_mobile_l1_frontend.py --source-dir` first, and writes
  `stitch-frontend-l1-preflight.json`.
- Dry-run is the default. It writes `stitch-frontend-promotion.json` with the
  files that would be promoted, but does not copy anything.
- `--execute` is only allowed after the preflight passes. It replaces both
  `apps/web/public/rehab-arm-mobile/` and `apps/mobile/rehab-arm-android/www/`
  from the accepted Stitch source, then writes
  `webview-mirror-verification.json` from
  `tools/verify_rehab_mobile_webview_mirror.py`.
- The promotion source must also be a clean frontend package. The tool rejects
  mixed-in QA/release reports such as `browser-qa*.json`,
  `browser-metrics*.json`, `frontend-l1-*.json`,
  `stitch-frontend-*.json`, `webview-mirror-verification.json`, and
  `rehab-mobile-frontend-release-manifest.json`.
- Unsafe cases are blocked before copying, including failing L1 preflight,
  filesystem-root targets, targets inside the Stitch source, and output
  directories inside replace targets.

Fresh verification:

- Red test first failed because
  `tools/promote_rehab_mobile_stitch_frontend.py` did not exist.
- Red dry-run test then failed because a passing Stitch source still returned
  `passing_source_promotion_not_implemented`.
- Red execute test then failed because accepted source files were not copied or
  mirrored.
- Red safety test then failed because `--execute` with `--output-dir` inside a
  replace target raised an exception after the tool had already started writing
  reports; the check now runs before any filesystem write.
- Red package-cleanliness test then failed because a source directory with a
  passing L1 preflight and an extra `frontend-l1-source-gate-v3.json` report
  still dry-ran as `PASS`; the tool now returns `overall = FAIL` and reports
  `package_cleanliness.status = FAIL`.
- Focused promotion tests:
  `tools/test_promote_rehab_mobile_stitch_frontend.py` -> `5 passed`.
- Related frontend/release chain:
  `tools/test_promote_rehab_mobile_stitch_frontend.py`,
  `tools/test_qa_rehab_mobile_l1_frontend.py`,
  `tools/test_qa_rehab_mobile_l1_frontend_local_source.py`,
  `tools/test_verify_rehab_mobile_webview_mirror.py`,
  `tools/test_prepare_rehab_mobile_frontend_release.py`, and
  `tools/test_deploy_rehab_mobile_frontend_release.py` -> `35 passed`.
- Stitch MCP status before this follow-up remained blocked: both
  `list_screens(projects/323711356322969905)` and `create_project` returned
  `401 invalid authentication credentials`, so no new frontend screen could be
  generated in this pass.

Current Stitch candidate dry-run:

- Command:
  `tools/promote_rehab_mobile_stitch_frontend.py --stitch-source-dir artifacts/stitch/l1-full-browser-qa-candidate-20260707 --web-dir artifacts/external/rehab-arm-mobile-stitch/apps/web/public/rehab-arm-mobile --android-www-dir artifacts/external/rehab-arm-mobile-stitch/apps/mobile/rehab-arm-android/www --output-dir docs/qa/rehab-mobile-20260706/stitch-promotion-current-candidate-20260707`
- Result: `overall = FAIL`, `copied = false`.
- Committed evidence:
  `docs/qa/rehab-mobile-20260706/stitch-promotion-current-candidate-20260707/stitch-frontend-l1-preflight.json`
  and
  `docs/qa/rehab-mobile-20260706/stitch-promotion-current-candidate-20260707/stitch-frontend-promotion.json`.
- Remaining source blockers: `no_mock_api_behavior`,
  `phone_verification_start_post`, `phone_verification_confirm_post`,
  `device_bind_post`, and `agent_messages_post`, with forbidden source hits
  `mockData`, `Simulate API response`, and `In real app`.
- Package cleanliness blockers: current local candidate directory also contains
  QA reports (`browser-metrics-*`, `browser-qa-*`, and `frontend-l1-*` JSON
  files). A future accepted Stitch output must be exported to a clean
  frontend-only directory before promotion.

Acceptance boundary:

- No frontend assets were copied into the real App checkout.
- No cloud deployment or APK rebuild was performed in this pass because the only
  runtime candidate was rejected and the committed work is QA/release tooling
  plus evidence.

## 2026-07-07 APK WebView Asset Verification Gate

Codex added a package-level APK verifier so L1 acceptance cannot rely only on
`curl -I` returning `200` for an APK URL. The APK must now prove that its bundled
WebView assets match the accepted Android WebView source directory.

Tooling changes:

- Added `tools/verify_rehab_mobile_apk_webview_assets.py`.
- The verifier opens the APK as a zip, reads files under `assets/public/`, and
  compares them against `apps/mobile/rehab-arm-android/www/`.
- Required L1 pages checked inside the APK:
  `home.html`, `profile.html`, `device.html`, and `ai-plan.html`.
- The verifier fails on missing required pages, changed bytes, missing files,
  or stale extra files in the APK asset prefix.
- `tools/prepare_rehab_mobile_frontend_release.py` now emits a post-deploy
  verification command for this gate:
  `tools\verify_rehab_mobile_apk_webview_assets.py --apk apps/web/public/downloads/rehab-arm/lingdong-rehab-arm-debug.apk --android-www-dir apps/mobile/rehab-arm-android/www --asset-prefix assets/public --output artifacts/rehab-mobile-frontend-release/apk-webview-assets-verification.json`.
- `tools/verify_rehab_mobile_frontend_release.py` now rejects a release
  manifest that omits the APK WebView asset verification command.

Fresh verification:

- Red APK verifier tests first failed because
  `tools/verify_rehab_mobile_apk_webview_assets.py` did not exist.
- Red release-manifest tests then failed because the generated manifest did not
  include the APK verifier command and the release verifier did not require it.
- Focused APK verifier tests:
  `tools/test_verify_rehab_mobile_apk_webview_assets.py` -> `3 passed`.
- Focused prepare/release verifier tests:
  `tools/test_prepare_rehab_mobile_frontend_release.py` and
  `tools/test_verify_rehab_mobile_frontend_release.py` -> `14 passed`.
- Related release chain:
  `tools/test_verify_rehab_mobile_apk_webview_assets.py`,
  `tools/test_prepare_rehab_mobile_frontend_release.py`,
  `tools/test_verify_rehab_mobile_frontend_release.py`,
  `tools/test_deploy_rehab_mobile_frontend_release.py`,
  `tools/test_verify_rehab_mobile_webview_mirror.py`, and
  `tools/test_promote_rehab_mobile_stitch_frontend.py` -> `33 passed`.

Current APK evidence:

- Command:
  `tools/verify_rehab_mobile_apk_webview_assets.py --apk artifacts/external/rehab-arm-mobile-stitch/apps/web/public/downloads/rehab-arm/lingdong-rehab-arm-debug.apk --android-www-dir artifacts/external/rehab-arm-mobile-stitch/apps/mobile/rehab-arm-android/www --asset-prefix assets/public --output docs/qa/rehab-mobile-20260706/apk-webview-assets-current-20260707.json`.
- Result: `overall = FAIL`, `failed = 3`, `total = 3`.
- The APK exists and contains `20` files under `assets/public/`.
- The real App checkout currently has no
  `apps/mobile/rehab-arm-android/www/` directory, so the verifier cannot prove
  Android source-to-APK parity.
- The current APK asset prefix includes stale/debug routes such as
  `bluetooth-debug.html`, `emg.html`, `report.html`,
  `training-library.html`, and `training-session.html`. These must not remain
  in a final L1 APK unless they are intentionally mirrored from the accepted
  Android WebView source and hidden from normal user flows.

Acceptance boundary:

- No cloud deployment or APK rebuild was performed in this pass because this
  work only adds release verification tooling and records that the current APK
  does not yet satisfy the new package-level asset gate.

## 2026-07-07 L1 Release Gate APK Asset Integration

Codex connected the APK WebView asset verifier to the actual L1 decision path,
not just the release manifest.

Tooling changes:

- `tools/qa_rehab_mobile_l1_release.py` now imports
  `tools/verify_rehab_mobile_apk_webview_assets.py` and includes its result in
  the combined L1 payload under `apk_webview_assets`.
- The release summary now includes:
  `apk_webview_assets_overall`, `apk_webview_assets_failed`, and blocker
  `apk_webview_assets`.
- New release gate CLI args:
  `--apk-file`, `--android-www-dir`, and `--apk-asset-prefix`, with matching
  environment-variable fallbacks.
- `tools/qa_rehab_mobile_l1_objective_audit.py` now adds an explicit
  `apk_webview_assets` objective requirement requiring
  `APK-WEBVIEW-INPUTS`, `APK-WEBVIEW-REQUIRED-PAGES`, and
  `APK-WEBVIEW-FILE-PARITY` to pass.
- The objective audit CLI forwards `--apk-file`, `--android-www-dir`, and
  `--apk-asset-prefix` into the release gate.

Fresh verification:

- Red release summary tests first failed because `summarize_release()` accepted
  only API and frontend payloads and could still pass without APK asset
  evidence.
- Red objective-audit test first failed because a release with
  `apk_webview_assets` blocker only reported `combined_l1_release`, not an
  explicit APK asset requirement.
- Focused release tests:
  `tools/test_qa_rehab_mobile_l1_release.py` -> `5 passed`.
- Focused objective audit tests:
  `tools/test_qa_rehab_mobile_l1_objective_audit.py` -> `11 passed`.

Current L1 evidence with staging credentials supplied from the local
environment:

- Release gate:
  `docs/qa/rehab-mobile-20260706/l1-release-current-with-apk-assets-20260707.json`.
- Result: `overall = FAIL`.
- API: `PASS`, `p0_failed = 0`.
- Frontend: `FAIL`, `failed = 5`.
- APK WebView assets: `FAIL`, `failed = 3`.
- Blocking gates: `frontend_l1_gate`, `apk_webview_assets`.

Current objective audit:

- Evidence:
  `docs/qa/rehab-mobile-20260706/objective-audit-current-with-apk-assets-20260707.json`.
- Result: `overall = FAIL`, `8 / 12` requirements failing.
- Blocking requirements:
  `home_next_step`, `phone_binding`, `device_binding`,
  `ask_therapist_safety`, `profile_no_fake_debug`, `apk_webview_assets`,
  `browser_qa_evidence`, and `combined_l1_release`.

Acceptance boundary:

- No cloud deployment or APK rebuild was performed in this pass because this
  work changes release/audit tooling and records the current APK as failing the
  new L1 gate.

## 2026-07-07 L1 Evidence Bundle APK Asset Targets

Codex tightened the final L1 evidence exporter so the evidence bundle now proves
which local APK and Android WebView source directory were used for the packaged
asset parity gate.

Tooling changes:

- `tools/export_rehab_mobile_l1_evidence.py` now records these target fields:
  `apk_file`, `android_www_dir`, and `apk_asset_prefix`.
- The exporter forwards `--apk-file`, `--android-www-dir`, and
  `--apk-asset-prefix` into `tools/qa_rehab_mobile_l1_release.py`, so the
  combined release gate and objective audit inspect the same APK/WebView asset
  pair described in the evidence JSON.
- The evidence summary now surfaces `apk_webview_assets_overall` and
  `apk_webview_assets_failed` at top level.
- Default local APK/WebView paths now point at the real App checkout under
  `artifacts/external/rehab-arm-mobile-stitch/`, matching the branch
  `app/rehab-arm-mobile-stitch`.
- The evidence bundle now includes an `app_git` section for the real App
  checkout, separate from the main QA/tooling repository `git` section.

Fresh verification:

- Red exporter tests first failed because `target.apk_file` was missing and
  `_run_release_gate()` did not pass APK WebView asset arguments into the
  combined release gate.
- Focused exporter tests:
  `tools/test_export_rehab_mobile_l1_evidence.py` -> `4 passed`.
- Related L1/APK regression suite:
  `tools/test_export_rehab_mobile_l1_evidence.py`,
  `tools/test_qa_rehab_mobile_l1_release.py`,
  `tools/test_qa_rehab_mobile_l1_objective_audit.py`, and
  `tools/test_verify_rehab_mobile_apk_webview_assets.py` -> `23 passed`.
- Follow-up red exporter tests first failed because `app_git_getter` and
  `target.app_checkout_dir` did not exist; focused exporter tests now pass with
  `5 passed`.

Current evidence bundle:

- Evidence:
  `docs/qa/rehab-mobile-20260706/l1-evidence-current-with-apk-assets-20260707.json`.
- Result: `overall = FAIL`.
- Health: `health_ok = true`.
- APK URL: `apk_ok = true`.
- App checkout: `app/rehab-arm-mobile-stitch`,
  `eaa08a40cdd3e1e62827809111f2323e7f92556f`, `dirty = false`.
- Release blockers: `frontend_l1_gate`, `apk_webview_assets`.
- Objective blockers:
  `home_next_step`, `phone_binding`, `device_binding`,
  `ask_therapist_safety`, `profile_no_fake_debug`, `apk_webview_assets`,
  `browser_qa_evidence`, and `combined_l1_release`.

Acceptance boundary:

- No cloud deployment or APK rebuild was performed in this pass because this
  work changes QA/evidence tooling only and the generated evidence still shows
  current L1 failure.

## 2026-07-07 Current Deployed Browser QA Refresh

Codex re-ran browser QA against the deployed cloud frontend at
`http://106.55.62.122:3001/rehab-arm-mobile/` using the in-app browser.

Artifacts:

- Raw browser metrics:
  `docs/qa/rehab-mobile-20260706/browser-metrics-current-deployed-20260707-raw.json`.
- Standard browser metrics gate:
  `docs/qa/rehab-mobile-20260706/browser-metrics-current-deployed-20260707.json`.
- Objective audit using current deployed browser metrics:
  `docs/qa/rehab-mobile-20260706/objective-audit-current-deployed-browser-20260707.json`.
- Refreshed L1 evidence bundle:
  `docs/qa/rehab-mobile-20260706/l1-evidence-current-with-apk-assets-20260707.json`.

Screenshots captured in the in-app browser:

- Home:
  `docs/qa/rehab-mobile-20260706/screenshots/current-deployed-home-20260707-375x812.jpg`.
- Profile:
  `docs/qa/rehab-mobile-20260706/screenshots/current-deployed-profile-20260707-375x812.jpg`.
- Device:
  `docs/qa/rehab-mobile-20260706/screenshots/current-deployed-device-20260707-375x812.jpg`.
- Ask Therapist / AI plan:
  `docs/qa/rehab-mobile-20260706/screenshots/current-deployed-ai-plan-20260707-390x844.jpg`.

Current browser metrics result:

- `L1-BROWSER-METRICS-001 = FAIL`.
- Checked pages: `home`, `profile`, `device`, `ai-plan`.
- Missing pages: none.
- Engineering/debug copy still visible:
  `M33` and `M55` on home/profile/device; `Gatekeeper` on device.
- Touch target issues remain on home/profile/device/ai-plan, including the
  header icon buttons and AI plan input/select controls below the 48 px minimum.
- No overflow, input-overlap, or vertical-text issues were detected in this
  pass.

Current objective audit with deployed browser metrics:

- Result: `overall = FAIL`, `8 / 12` requirements failing.
- Blocking requirements:
  `home_next_step`, `phone_binding`, `device_binding`,
  `ask_therapist_safety`, `profile_no_fake_debug`, `apk_webview_assets`,
  `browser_qa_evidence`, and `combined_l1_release`.

Acceptance boundary:

- No cloud deployment or APK rebuild was performed in this pass because this
  work captures the current deployed failure state only.

## 2026-07-07 Stitch Handoff Uses Deployed Browser QA

Codex updated the Stitch repair packet and V4 execution prompt so the next
frontend generation receives the current deployed browser QA blockers directly,
not only the older candidate-source failures.

Tooling changes:

- `tools/export_rehab_mobile_stitch_repair_packet.py` now accepts
  `--deployed-browser-metrics-json` and
  `--deployed-browser-metrics-raw-json`.
- The repair packet now includes `deployed_browser_qa` with:
  checked pages, status, fake/debug copy hits, undersized touch targets,
  issue counts, raw metrics path, and deployed screenshot paths.
- `tools/export_rehab_mobile_stitch_prompt.py` now renders a
  `Current Deployed Browser QA Blockers` section.

Fresh handoff artifacts:

- Repair packet:
  `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`.
- Stitch prompt:
  `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md`.

New Stitch blockers exposed in the prompt:

- Current deployed metrics:
  `docs/qa/rehab-mobile-20260706/browser-metrics-current-deployed-20260707.json`.
- Current deployed raw metrics/screenshots:
  `docs/qa/rehab-mobile-20260706/browser-metrics-current-deployed-20260707-raw.json`.
- Fake/debug copy: `M33`, `M55`, and `Gatekeeper` on normal patient screens.
- Touch target issues: `9` total, including header buttons and AI plan input
  controls below the 48 px minimum.
- Current deployed screenshot references for home/profile/device/ai-plan are
  included, with `375 x 812` failure captures clearly not counted as final L1
  success evidence.

Fresh verification:

- Red repair-packet test first failed because `build_repair_packet()` had no
  deployed browser metrics inputs.
- Red prompt test first failed because the V4 prompt did not include
  `Current Deployed Browser QA Blockers`.
- Focused Stitch packet/prompt tests:
  `tools/test_export_rehab_mobile_stitch_repair_packet.py` and
  `tools/test_export_rehab_mobile_stitch_prompt.py` -> `9 passed`.

Acceptance boundary:

- No cloud deployment or APK rebuild was performed in this pass because this
  work updates the Stitch handoff and QA tooling only.

## 2026-07-07 Stitch MCP Auth Resmoke After Deployed QA Handoff

Codex retried the real Stitch project after the V4 handoff prompt was updated
to include current deployed browser QA blockers.

Stitch call:

```text
mcp__stitch.list_screens(projectId = "323711356322969905")
```

Result: `401 invalid authentication credentials`.

Interpretation:

- The Stitch tool schema is reachable in this Codex session.
- The configured Stitch connection still cannot authenticate project reads or
  generation actions.
- The service requires a valid OAuth 2 access token, login cookie, or equivalent
  credential for the project.

L1 impact:

- No new frontend candidate was generated.
- No frontend files were copied into the real App branch
  `app/rehab-arm-mobile-stitch`.
- No Android WebView assets were mirrored.
- No cloud deployment or APK rebuild was performed.
- The current L1 blocker remains the frontend/App package path, not the backend
  API or cloud Agent model.

Next unblock:

- Restore Stitch MCP authentication for project `323711356322969905`, or
  provide a clean exported Stitch package containing only the four L1 web pages
  and their assets.
- The package must pass `tools/promote_rehab_mobile_stitch_frontend.py` dry-run
  before any real App files, cloud deployment, or APK package are touched.
