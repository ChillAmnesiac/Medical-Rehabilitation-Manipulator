# Rehab Mobile App Completion Scorecard - 2026-07-06

## Release Levels

### L0 - API Ready

Backend can support the app, but the rendered app may still fail.

Required:

- Cloud health passes.
- Cloud health exposes traceable deployment metadata.
- Auth/session passes.
- `/api/rehab-arm/app/v1/me` returns `profile` and `patient_view`.
- Phone binding APIs pass, including immediate resend throttling.
- Phone SMS delivery readiness is visible; webhook delivery is implemented; staging warns when still using debug SMS codes.
- Device binding APIs pass, including same-account idempotency and cross-account already-bound conflict.
- Agent safe answer and unsafe refusal pass.
- Agent model readiness is visible in public config and in Agent answers; current staging warns when using fallback rules instead of a configured cloud model.
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
- Device tab shows patient binding wizard, including `绑定设备` and `打开康复设备电源`, not debug console.
- Profile shows cloud account, verified phone, `绑定手机号`/`验证码` path, rehab profile, and safe `待完善` medical empty state.
- Frontend source is wired to auth, `/me`, `patient_view`, phone verification, device binding, and Agent message APIs.
- Bottom navigation routes correctly.
- Browser QA screenshots are real image files at exactly `390 x 844` and show no overlap or unreachable primary controls.

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
| Deployment metadata | PASS | `P1-DEPLOY-META-001`: health exposes build SHA `8e17a51d`, ref `codex/rehab-mobile-backend-qa-20260706`, build time, and `app_env=staging` |
| Stitch API fixture | PASS | `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json` exported from live cloud API with tokens, codes, ids, email, and phone masked; now includes phone verification start/confirm response examples |
| Stitch repair packet and V4 prompt | PASS | `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json` generated from the live cloud L1 release gate and objective audit; `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` is generated from the packet and is now the primary Stitch handoff |
| Frontend release packaging | PASS | `tools/qa_rehab_mobile_l1_frontend.py --source-dir --output` preflights Stitch output locally and preserves JSON evidence; `tools/prepare_rehab_mobile_frontend_release.py` refuses failing frontend sources, writes a deployable zip, and records manifest deploy/verification commands before cloud copy |
| Frontend release package verification | PASS | `tools/verify_rehab_mobile_frontend_release.py` validates the generated manifest schema, zip sha256, preflight report, required page artifacts, deploy commands, and exact browser QA screenshot checklist before cloud deployment |
| Patient view contract | PASS | `P0-PATIENT-VIEW-001` checks sections, Agent endpoint, device step, phone field, and no raw terms |
| Phone verification flow | PASS | `P0-PHONE-FLOW-001` requests and confirms a staging SMS code; `P1-PHONE-RESEND-001` rejects immediate resend with `retry_after` |
| Phone SMS delivery readiness | WARN | Webhook delivery path is implemented and covered locally; `P1-PHONE-SMS-001` still warns because current staging mode is `debug_sms`, reason `debug_code_enabled` |
| Device binding flow | PASS | `P0-DEVICE-FLOW-001` repeats binding against the same record; `P0-DEVICE-CONFLICT-001` rejects a second account with `DEVICE_ALREADY_BOUND` |
| Agent backend safety | PASS | Safe answer `200` with `model_status`, unsafe direct-control requests `400 UNSAFE_MOTION_REQUEST` |
| Agent draft patient copy | PASS | AI training draft risk notes now use patient-facing Chinese and cloud smoke found no `M33`, `preflight`, `m33_accepted`, `CAN`, or `Stop` in `risk_notes` |
| Agent public config readiness | WARN | `P1-AGENT-CONFIG-001`: public-config exposes `data.agent.model_readiness`; current staging mode is `fallback_rule_based`, reason `external_model_not_configured` |
| Agent cloud model readiness | FAIL | L1 release now blocks on `agent_cloud_model` until `P1-AGENT-CONFIG-001` and `P1-AGENT-MODEL-001` are `PASS`; current staging is `fallback_rule_based`, reason `external_model_not_configured` |
| Agent model relay ops | READY TO CONFIGURE | Backend Agent now supports `openai_compatible` and `gemini`; `tools/configure_rehab_model_relay.py` performs privileged relay config plus Agent smoke and defaults Gemini base URL; runbook: `docs/deployments/rehab-mobile-agent-model-relay-runbook-20260706.md` |
| APK delivery | PASS | APK HEAD `200`, size `4198462` bytes |
| Combined L1 release gate | FAIL | `tools/qa_rehab_mobile_l1_release.py`: API `PASS`, frontend `FAIL`, 5 failed frontend gates, blockers `frontend_l1_gate` and `agent_cloud_model` |
| Objective-level L1 audit | FAIL | `tools/qa_rehab_mobile_l1_objective_audit.py`: 8/11 objective requirements failing: home next step, phone UI, device UI, Ask Therapist UI, cloud model, profile no-fake-data, browser evidence, combined release; browser evidence now validates decoded PNG/JPEG dimensions against `390 x 844` |
| Current-fail browser evidence | PASS | Four in-app browser screenshots in `docs/qa/rehab-mobile-20260706/browser-current-fail-20260706/` decode to `390 x 844`; they document current blockers and intentionally do not satisfy L1 success evidence |
| Home UI | FAIL | Browser screenshots plus `tools/qa_rehab_mobile_l1_frontend.py` gate `L1-HOME-STATIC-001` |
| Agent UI | FAIL | Visible assistant entries do not open chat; static gate `L1-AGENT-STATIC-001` missing `问康复师` |
| Device UI | FAIL | Device page still looks like debug/engineering state; latest browser evidence `screenshots/model-relay-ops-device-390.png`; static gate `L1-DEVICE-STATIC-001` requires `绑定设备` and `打开康复设备电源`, and the page still exposes `M33`, `M55`, and `Gatekeeper` |
| Profile UI | FAIL | Browser screenshots plus static gate `L1-PROFILE-STATIC-001` now also require `绑定手机号` and `验证码` |
| Frontend API integration | FAIL | `L1-FRONTEND-INTEGRATION-001` is missing `patient_view` wiring, Ask Therapist accessibility, phone verification start/confirm/cooldown/SMS error handling, device already-bound handling, Agent messages, unsafe refusal, and model-status rendering |

## Next Work Order

1. Run the Stitch prompt in `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` with `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json`.
2. Follow the Stitch runbook in `docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md`.
3. Run `tools/qa_rehab_mobile_l1_frontend.py --source-dir apps/web/public/rehab-arm-mobile --output artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json`.
4. Package updated frontend web assets with `tools/prepare_rehab_mobile_frontend_release.py`.
5. Verify the generated release manifest with `tools/verify_rehab_mobile_frontend_release.py` before any cloud copy.
6. Deploy the reviewed frontend bundle to `http://106.55.62.122:3001/rehab-arm-mobile/`.
7. Rebuild or refresh APK if the APK bundles frontend assets.
8. Configure the real Agent cloud model relay with `tools/configure_rehab_model_relay.py` after a real model endpoint/key is available.
9. Run `tools/qa_rehab_mobile_l1_release.py`; it must return exit code `0` and `overall = PASS`.
10. Run `tools/qa_rehab_mobile_l1_objective_audit.py`; it must return exit code `0` and every objective requirement must be `PASS`.
11. If either gate fails, inspect the nested `api`, `frontend`, and `requirements` sections before changing code.
12. Browser QA at exactly `390 x 844`:
   - Home first screen.
   - `问康复师` chat open.
   - Unsafe Agent refusal.
   - Device binding wizard.
   - Profile account/phone/medical empty state.
13. Update this scorecard after every large task.

## Git Discipline

Every future code or QA artifact change should end with:

1. `git status --short`
2. Run relevant tests or smoke checks.
3. Stage only task-relevant files.
4. `git diff --cached --check`
5. Commit with a focused message.
6. Record commit hash in the final update.
