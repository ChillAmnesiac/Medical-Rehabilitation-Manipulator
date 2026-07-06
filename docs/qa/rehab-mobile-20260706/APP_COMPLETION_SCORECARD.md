# Rehab Mobile App Completion Scorecard - 2026-07-06

## Release Levels

### L0 - API Ready

Backend can support the app, but the rendered app may still fail.

Required:

- Cloud health passes.
- Auth/session passes.
- `/api/rehab-arm/app/v1/me` returns `profile` and `patient_view`.
- Phone binding APIs pass.
- Phone SMS delivery readiness is visible; webhook delivery is implemented; staging warns when still using debug SMS codes.
- Device binding APIs pass, including same-account idempotency and cross-account already-bound conflict.
- Agent safe answer and unsafe refusal pass.
- Agent model readiness is visible; current staging warns when using fallback rules instead of a configured cloud model.
- CORS passes from deployed web origin.
- APK URL is reachable.

Current result: `PASS`.

### L1 - User-Ready Staging

A real patient can open the app, log in, understand the next step, bind account/device, ask the rehab therapist Agent, and leave without seeing debug internals.

Required P0 gates:

- Home first screen has one clear next action.
- No false `网络未连接` state when backend is healthy.
- No raw terms on normal screens: `M33`, `M55`, `SPP`, `CAN`, `UUID`, `setup_required`, `early_active`, `direct_motor_command`, `can_frame`.
- `问康复师` opens a working chat and calls Agent API.
- Unsafe Agent requests show protective Chinese copy.
- Device tab shows patient binding wizard, not debug console.
- Profile shows cloud account, verified phone, rehab profile, and safe `待完善` medical empty state.
- Bottom navigation routes correctly.
- 390px mobile screenshots show no overlap or unreachable primary controls.

Current result: `FAIL`, blocked by Stitch/frontend rendering.

### L2 - Beta Ready

The app can be used by a small test group with known limitations.

Required:

- All L1 gates pass.
- At least 90% of P1 gates pass.
- Production SMS provider is configured, debug SMS is disabled, and no verification response exposes `debug_code`.
- Phone verification UX handles invalid code, resend, success, and verified state.
- Agent chat has loading, retry, answer card, quick chips, unsafe refusal, and empty/error states.
- Device binding has success, failure, retry, and already-bound states.
- Training cannot start until account, device, plan, pain score, and safety check are ready.
- Basic accessibility checks pass for labels, target size, focus, and contrast.
- APK version, SHA256, size, and build time are recorded.

Current result: `NOT READY`.

### L3 - Production Candidate

The app can be handed to users outside the core team.

Required:

- All L2 gates pass.
- Privacy copy and data collection boundaries are reviewed.
- Backend logs contain enough request IDs for support without storing sensitive medical free text.
- Device debug pages are hidden behind developer mode.
- App has graceful offline/poor-network behavior.
- APK install and first-run flow pass on a physical Android device.
- Rollback plan exists for web assets and backend service.

Current result: `NOT READY`.

## Current Completion Summary

| Area | Status | Evidence |
| --- | --- | --- |
| Backend API | PASS | `tools/qa_rehab_mobile_acceptance.py`, `overall = PASS`, `p0_failed = 0` |
| Patient view contract | PASS | `P0-PATIENT-VIEW-001` checks sections, Agent endpoint, device step, phone field, and no raw terms |
| Phone verification flow | PASS | `P0-PHONE-FLOW-001` requests and confirms a staging SMS code end to end |
| Phone SMS delivery readiness | WARN | Webhook delivery path is implemented and covered locally; `P1-PHONE-SMS-001` still warns because current staging mode is `debug_sms`, reason `debug_code_enabled` |
| Device binding flow | PASS | `P0-DEVICE-FLOW-001` repeats binding against the same record; `P0-DEVICE-CONFLICT-001` rejects a second account with `DEVICE_ALREADY_BOUND` |
| Agent backend safety | PASS | Safe answer `200` with `model_status`, unsafe direct-control requests `400 UNSAFE_MOTION_REQUEST` |
| Agent cloud model readiness | WARN | `P1-AGENT-MODEL-001`: current staging mode is `fallback_rule_based`, reason `external_model_not_configured` |
| APK delivery | PASS | APK HEAD `200`, size `4198462` bytes |
| Combined L1 release gate | FAIL | `tools/qa_rehab_mobile_l1_release.py`: API `PASS`, frontend `FAIL`, blocking gate `frontend_l1_gate` |
| Home UI | FAIL | Browser screenshots plus `tools/qa_rehab_mobile_l1_frontend.py` gate `L1-HOME-STATIC-001` |
| Agent UI | FAIL | Visible assistant entries do not open chat; static gate `L1-AGENT-STATIC-001` missing `问康复师` |
| Device UI | FAIL | Device page still looks like debug/engineering state; static gate `L1-DEVICE-STATIC-001` hits `M33/M55/UUID/Gatekeeper` |
| Profile UI | FAIL | Browser screenshots plus static gate `L1-PROFILE-STATIC-001` show demo identity and fake medical warning |

## Next Work Order

1. Run the Stitch prompt in `docs/stitch/rehab-mobile-l1-stitch-execution-v2-20260706.md`.
2. Follow the Stitch runbook in `docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md`.
3. Deploy updated frontend web assets to `http://106.55.62.122:3001/rehab-arm-mobile/`.
4. Rebuild or refresh APK if the APK bundles frontend assets.
5. Run `tools/qa_rehab_mobile_l1_release.py`; it must return exit code `0` and `overall = PASS`.
6. If the combined gate fails, inspect the nested `api` and `frontend` sections before changing code.
7. Browser QA at 390px:
   - Home first screen.
   - `问康复师` chat open.
   - Unsafe Agent refusal.
   - Device binding wizard.
   - Profile account/phone/medical empty state.
8. Update this scorecard after every large task.

## Git Discipline

Every future code or QA artifact change should end with:

1. `git status --short`
2. Run relevant tests or smoke checks.
3. Stage only task-relevant files.
4. `git diff --cached --check`
5. Commit with a focused message.
6. Record commit hash in the final update.
