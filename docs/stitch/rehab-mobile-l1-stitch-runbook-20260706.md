# Rehab Mobile L1 Stitch Runbook - 2026-07-06

## Purpose

Move the deployed rehab mobile app from `L0 API Ready` to `L1 User-Ready Staging`.

Codex owns backend, QA, deployment verification, APK verification, and git commits. Stitch owns frontend edits.

## Current State

- Backend/API: `PASS`
- APK delivery: `PASS`
- Frontend L1: `FAIL`
- Sanitized live API fixture: `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json`
- Fixture now includes sanitized phone-verification `start_response` and `confirm_response` examples, with `verification_id` preserved as `fixture-verification-id` and debug codes removed.
- Latest browser evidence:
  - `docs/qa/rehab-mobile-20260706/06-profile-resmoke-390.png`
  - `docs/qa/rehab-mobile-20260706/07-home-resmoke-390.png`
  - `docs/qa/rehab-mobile-20260706/screenshots/device-binding-home-390.png`
  - `docs/qa/rehab-mobile-20260706/screenshots/device-binding-profile-390.png`
  - `docs/qa/rehab-mobile-20260706/screenshots/device-binding-device-390.png`
  - `docs/qa/rehab-mobile-20260706/screenshots/device-binding-agent-390.png`
  - `docs/qa/rehab-mobile-20260706/screenshots/continuation-device-qa-20260706-390.png`
  - `docs/qa/rehab-mobile-20260706/screenshots/model-relay-ops-device-390.png`

Latest visible frontend blockers:

- Home/profile still show `网络未连接，请检查后端服务`.
- Home still exposes `setup_required`, `early_active`, `left`, `M33`, action queue, blockers, forbidden actions.
- Profile still shows demo patient content and fake medical warning.
- Normal screens still expose `M33/M55` device names.
- Device still exposes `setup_required`, `Gatekeeper`, and a prominent `bluetooth-debug.html` developer route instead of a patient binding wizard.
- Assistant buttons do not provide the required working `问康复师` chat.

## Stitch Input

Use this prompt as the primary frontend task:

- `docs/stitch/rehab-mobile-l1-stitch-execution-v3-20260706.md`

Historical prompt kept for reference:

- `docs/stitch/rehab-mobile-l1-stitch-execution-v2-20260706.md`
- `docs/stitch/rehab-mobile-stitch-execution-20260706.md`

Use this scorecard as the release gate:

- `docs/qa/rehab-mobile-20260706/APP_COMPLETION_SCORECARD.md`

Use this sanitized live API fixture as the field-shape reference:

- `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json`

The fixture was exported from `http://106.55.62.122:8011` and masks tokens, verification codes, raw ids, email addresses, and phone numbers. Stitch should use it to understand response shapes, not hard-code its values.

Use these screenshots as current failure evidence:

- `docs/qa/rehab-mobile-20260706/01-home-390-current.png`
- `docs/qa/rehab-mobile-20260706/02-agent-top-click-390.png`
- `docs/qa/rehab-mobile-20260706/03-agent-floating-click-390.png`
- `docs/qa/rehab-mobile-20260706/04-device-nav-390.png`
- `docs/qa/rehab-mobile-20260706/05-profile-nav-390.png`
- `docs/qa/rehab-mobile-20260706/06-profile-resmoke-390.png`
- `docs/qa/rehab-mobile-20260706/07-home-resmoke-390.png`
- `docs/qa/rehab-mobile-20260706/screenshots/device-binding-home-390.png`
- `docs/qa/rehab-mobile-20260706/screenshots/device-binding-profile-390.png`
- `docs/qa/rehab-mobile-20260706/screenshots/device-binding-device-390.png`
- `docs/qa/rehab-mobile-20260706/screenshots/device-binding-agent-390.png`
- `docs/qa/rehab-mobile-20260706/screenshots/continuation-device-qa-20260706-390.png`

## Required Frontend Output

Stitch must edit only:

- `apps/web/public/rehab-arm-mobile/`

Stitch must not change backend endpoints.

Stitch must render normal user pages from:

```text
GET http://106.55.62.122:8011/api/rehab-arm/app/v1/me
Authorization: Bearer <token>
```

Required data source:

- `data.profile`
- `data.patient_view.home`
- `data.patient_view.profile`
- `data.patient_view.device`
- `data.patient_view.agent`

## L1 Pass Criteria

The next frontend build is not accepted until all checks pass:

1. Home first screen has one clear primary action.
2. Home does not show false `网络未连接` when API smoke is green.
3. Normal screens do not show raw terms:
   - `M33`
   - `M55`
   - `SPP`
   - `CAN`
   - `UUID`
   - `setup_required`
   - `early_active`
   - `direct_motor_command`
   - `can_frame`
4. `问康复师` opens a chat UI.
5. Chat sends safe questions to `/api/rehab-arm/app/v1/agent/messages`.
6. Unsafe direct-control requests show protective Chinese copy.
7. Device tab shows a patient binding wizard, not debug transport UI.
8. Profile shows cloud account, verified phone state, rehab profile, and calm `待完善` medical empty state.
9. No demo patient, fake ID, fake stage, or fake medical warning appears as real data.
10. Source/included same-origin scripts reference required live API contracts: auth session, `/me`, `patient_view` sections, phone verification start/confirm, device bind, and Agent messages.
11. 390px mobile screenshots show no overlap or unreachable primary controls.

## Codex Verification After Stitch

After Stitch changes are available and deployed, Codex must run:

```powershell
$env:REHAB_QA_EMAIL='<staging email>'
$env:REHAB_QA_PASSWORD='<staging password>'
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_release.py
```

Required combined result:

- Exit code `0`
- `summary.overall = PASS`
- `summary.api_overall = PASS`
- `summary.frontend_overall = PASS`
- `summary.blocking_gates = []`
- `P1-AGENT-CONFIG-001 = PASS`
- `P1-AGENT-MODEL-001 = PASS`
- `agent_cloud_model` is not listed in `summary.blocking_gates`.
- `L1-FRONTEND-INTEGRATION-001` has no missing API contract requirements.

If this combined gate fails, inspect the nested `api` and `frontend` sections. Do not accept the frontend build, cloud deployment, or refreshed APK as L1 user-ready while `frontend_l1_gate` or `api_smoke` is listed as a blocker.

Then Codex must capture browser screenshots at `390 x 844`:

1. Home first screen.
2. `问康复师` chat open.
3. Agent unsafe refusal.
4. Device binding wizard.
5. Profile account/phone/medical empty state.

Then Codex must:

1. Update `docs/qa/rehab-mobile-20260706/QA_REPORT.md`.
2. Update `docs/qa/rehab-mobile-20260706/APP_COMPLETION_SCORECARD.md`.
3. Verify APK URL still returns `200`, APK content type, and size over 1 MB.
4. Stage only task-relevant files.
5. Commit with a focused message.

## Current Next Action

Run Stitch with `docs/stitch/rehab-mobile-l1-stitch-execution-v3-20260706.md`, deploy the generated frontend assets, then hand control back to Codex for browser QA and git-managed closeout.
