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
- Agent model readiness is visible in public config and in Agent answers; current staging must report the configured cloud model.
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
- Browser QA screenshots are real image files at exactly `390 x 844`, with enough bytes to be real captures rather than image-header placeholders; the saved browser metrics gate must cover `home`, `profile`, `device`, and `ai-plan`, and pass with no fake copy, undersized touch targets, input overlap, overflow, vertical text, or unreachable primary controls.

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
| Deployment metadata | PASS | `P1-DEPLOY-META-001`: latest health verification exposed build SHA `a4d1c1565de3`, ref `ai/game-loop-core`, build time `2026-07-06T20:59:56Z`, and `app_env=staging` |
| Stitch API fixture | PASS | `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json` refreshed from live cloud API at `2026-07-06T21:10:05Z` with tokens, numeric codes, ids, email, and phone masked; it now proves `patient_view` core copy, phone verification start/confirm, unsafe Agent refusal, and `model_status.mode = cloud_model`, provider `qwen`, model `qwen-plus` |
| Stitch L1 UI contract | PASS | `docs/stitch/rehab-mobile-l1-ui-contract-20260707.json` now extracts a compact patient-facing contract from the live fixture for Stitch generation: four required pages, exact visible copy, POST action endpoints, phone/device/Agent states, and cloud model status. It omits broad legacy public-config payloads such as `m33_legacy_spp_profile`, raw email, access tokens, and numeric debug codes |
| Stitch repair packet and V4 prompt | PASS | `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json` generated from the live cloud L1 release gate and objective audit; `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` is generated from the packet and is now the primary Stitch handoff. The packet/prompt now show `non_stitch_blockers = []`, include SMS ops readiness, L1 evidence export, no raw staging email/password, an `Exact Release-Gated Visible Copy` section, hexadecimal HTML entity fallback snippets, and a `Stitch Browser Candidate QA Blockers` section for fake/demo names, `48 x 48` interactive targets, `48 x 48` back buttons, and `64 x 48` bottom-nav items; the frontend L1 gate also rejects common fake/demo identities |
| Stitch source scope | PASS | Real frontend branch verified as `app/rehab-arm-mobile-stitch` at commit `eaa08a40cdd3e1e62827809111f2323e7f92556f`; prompt/packet now identify web edit path `apps/web/public/rehab-arm-mobile/` and APK WebView mirror path `apps/mobile/rehab-arm-android/www/` |
| Stitch MCP generation attempt | REJECTED AFTER API-ACTION HARDENING, NOT DEPLOYED | Stitch project `projects/323711356322969905` produced a full local four-page v3 candidate: Home `767c6e263ec646f7b27664c385e3ba4c`, Profile `b1c634dd4d6640beac7fc7a9a3515cb7`, Device `aadf5ed620314ac1b0a33a27089e2cd4`, Ask Therapist `5a10e02454c044f38e60a7292064566b`. Browser QA still passes at `390 x 844` with screenshots `screenshots/stitch-full-candidate-v3-home/profile/device/ai-plan-20260707-390x844.png` and metrics report `docs/qa/rehab-mobile-20260706/browser-metrics-stitch-full-candidate-v3-20260707.json`. However the post-hardened source gate `docs/qa/rehab-mobile-20260706/frontend-l1-source-gate-stitch-full-candidate-v3-post-hardened-20260707.json` now returns `overall = FAIL`, blockers `no_mock_api_behavior`, `phone_verification_start_post`, `phone_verification_confirm_post`, `device_bind_post`, and `agent_messages_post`, with hits `mockData`, `Simulate API response`, and `In real app`. This candidate must not be deployed or copied into the real App branch until Stitch returns pages with real POST calls for phone verification, device binding, and Ask Therapist messages |
| Frontend source API-action hardening | PASS | `tools/qa_rehab_mobile_l1_frontend.py` now rejects source that only includes API contract tokens while using mocked/simulated behavior or missing POST methods on user actions. Regressions `test_frontend_integration_contract_rejects_mocked_api_behavior` and `test_frontend_integration_contract_rejects_action_endpoints_without_post_methods` failed first, then passed after adding `no_mock_api_behavior` and POST action requirements; focused frontend tests: `15 passed`. `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` was regenerated so Stitch is told not to use `mockData`, mock responses, `Simulate API response`, `In real app`, or console-only behavior, and to use `method: 'POST'` for phone start/confirm, device bind, and Agent messages |
| Frontend release packaging | PASS | `tools/qa_rehab_mobile_l1_frontend.py --source-dir --output` preflights Stitch output locally and preserves JSON evidence; `tools/prepare_rehab_mobile_frontend_release.py` refuses failing frontend sources, writes a deployable zip, and records manifest deploy/verification commands before cloud copy, including the `browser-metrics-l1-390x844.json` browser metrics gate; release manifests no longer write raw staging email/password values |
| Frontend release package verification | PASS | `tools/verify_rehab_mobile_frontend_release.py` validates the generated manifest schema, zip sha256, preflight report, required page artifacts, guarded deploy executor command, exact browser QA screenshot checklist, and a real `browser-metrics-gate.json` with `L1-BROWSER-METRICS-001 = PASS` plus full `home/profile/device/ai-plan` coverage before cloud deployment |
| APK WebView mirror verification | PASS | `tools/verify_rehab_mobile_webview_mirror.py` checks that `apps/mobile/rehab-arm-android/www/` is byte-identical to `apps/web/public/rehab-arm-mobile/`, including required pages and no stale extra files; release manifests now require this command before APK packaging |
| Frontend release deployment guard | PASS | `tools/deploy_rehab_mobile_frontend_release.py` verifies the manifest again, defaults to dry-run, refuses unsafe remote roots, and now enforces `--run-post-verify` whenever `--execute` is used, so cloud copy cannot run without post-deploy checks. The generated post-deploy objective audit now consumes `artifacts/rehab-mobile-frontend-release/browser-metrics-gate.json` explicitly instead of falling back to stale/default browser evidence |
| Frontend deployment metrics regression coverage | PASS | 2026-07-07 focused deploy/release verifier suite now covers a realistic `browser-metrics-gate.json` fixture and proves `deploy_rehab_mobile_frontend_release.py --execute` refuses to run deploy commands when that gate output is missing; fresh focused result: `16 passed` |
| L1 release evidence bundle | PASS | `tools/export_rehab_mobile_l1_evidence.py` exports one JSON snapshot with cloud health, git HEAD, combined L1 release gate, objective audit, browser evidence status, APK HEAD, and required follow-up artifacts; the exporter now records `target.browser_metrics_json` and the objective audit's `browser_evidence.browser_metrics` status |
| Patient view contract | PASS | `P0-PATIENT-VIEW-001` checks sections, Agent endpoint, device step, phone field, and no raw terms |
| Phone verification flow | PASS | `P0-PHONE-FLOW-001` requests and confirms a staging SMS code; `P1-PHONE-RESEND-001` rejects immediate resend with `retry_after` |
| Phone SMS delivery readiness | READY, PROVIDER BLOCKED | Webhook delivery path is implemented and covered locally; `tools/smoke_rehab_sms_provider.py` and `tools/configure_rehab_sms_delivery.py` now provide the preflight/configuration path. `P1-PHONE-SMS-001` still warns because current staging mode is `debug_sms`, reason `debug_code_enabled`. Runbook: `docs/deployments/rehab-mobile-sms-delivery-runbook-20260706.md` |
| Device binding flow | PASS | `P0-DEVICE-FLOW-001` repeats binding against the same record; `P0-DEVICE-CONFLICT-001` rejects a second account with `DEVICE_ALREADY_BOUND` |
| Agent backend safety | PASS | Safe answer `200` with `model_status`, unsafe direct-control requests `400 UNSAFE_MOTION_REQUEST` |
| Agent draft patient copy | PASS | AI training draft risk notes now use patient-facing Chinese and cloud smoke found no `M33`, `preflight`, `m33_accepted`, `CAN`, or `Stop` in `risk_notes` |
| Agent public config readiness | PASS | `P1-AGENT-CONFIG-001`: public config reports `data.agent.model_readiness.mode = cloud_model_configured`, provider `qwen`, model `qwen-plus`, with no API key exposed |
| Agent cloud model readiness | PASS | `P1-AGENT-MODEL-001`: safe Agent answers report `data.model_status.mode = cloud_model`, provider `qwen`, model `qwen-plus`; `agent_cloud_model` is no longer an L1 blocker |
| Agent model relay ops | PASS, CLOUD MODEL LIVE | Backend Agent supports provider config and safe fallback; current cloud runtime is configured for `qwen-plus`. Runbook: `docs/deployments/rehab-mobile-agent-model-relay-runbook-20260706.md` |
| APK delivery | PASS | APK HEAD `200`, size `4198462` bytes |
| Combined L1 release gate | FAIL | `tools/qa_rehab_mobile_l1_release.py`: API `PASS`, frontend `FAIL`, 5 failed frontend gates, blocker `frontend_l1_gate` only |
| Objective-level L1 audit | FAIL | `tools/qa_rehab_mobile_l1_objective_audit.py`: 7/11 objective requirements failing: home next step, phone UI, device UI, Ask Therapist UI, profile no-fake-data, browser evidence, combined release; browser evidence now validates exact L1 PNG/JPEG filenames, decoded `390 x 844` dimensions, minimum screenshot bytes, and `L1-BROWSER-METRICS-001 = PASS` from a saved metrics gate that covers `home`, `profile`, `device`, and `ai-plan` |
| Current-fail browser evidence | PASS | Four fresh in-app browser screenshots captured at `390 x 844` on 2026-07-07 (`current-fail-home/profile/device/ai-plan-20260707-390x844.png`) plus earlier baseline screenshots document current blockers and intentionally do not satisfy L1 success evidence |
| Home UI | FAIL | Browser screenshots plus `tools/qa_rehab_mobile_l1_frontend.py` gate `L1-HOME-STATIC-001`, now requiring both `查看康复师建议` and `问康复师` |
| Agent UI | FAIL | Visible assistant entries do not open chat; static gate `L1-AGENT-STATIC-001` missing `问康复师` |
| Device UI | FAIL | Device page still looks like debug/engineering state; latest browser evidence `screenshots/model-relay-ops-device-390.png`; static gate `L1-DEVICE-STATIC-001` requires `绑定设备` and `打开康复设备电源`, and the page still exposes `M33`, `M55`, and `Gatekeeper` |
| Profile UI | FAIL | Browser screenshots plus static gate `L1-PROFILE-STATIC-001` now also require `绑定手机号` and `验证码` |
| Frontend API integration | FAIL | `L1-FRONTEND-INTEGRATION-001` is missing `patient_view` wiring, Ask Therapist accessibility, phone verification start/confirm/cooldown/SMS error handling, device already-bound handling, Agent messages, unsafe refusal, and model-status rendering |

## Next Work Order

1. Apply the Stitch full-candidate v3 design through the real App branch `app/rehab-arm-mobile-stitch`; do not manually hand-edit frontend source outside the approved Stitch/app-branch path.
2. Mirror accepted web assets into `apps/mobile/rehab-arm-android/www/` before APK packaging.
3. Run `tools/qa_rehab_mobile_l1_frontend.py --source-dir apps/web/public/rehab-arm-mobile --output artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json`.
4. Run `tools/verify_rehab_mobile_webview_mirror.py --web-dir apps/web/public/rehab-arm-mobile --android-www-dir apps/mobile/rehab-arm-android/www --output artifacts/rehab-mobile-frontend-release/webview-mirror-verification.json`; it must return exit code `0` and `summary.overall = PASS`.
5. Package updated frontend web assets with `tools/prepare_rehab_mobile_frontend_release.py`.
6. Verify the generated release manifest with `tools/verify_rehab_mobile_frontend_release.py` before any cloud copy.
7. Dry-run `tools/deploy_rehab_mobile_frontend_release.py` and review the planned `scp`, `ssh`, and post-deploy verification commands.
8. Deploy the reviewed frontend bundle with `tools/deploy_rehab_mobile_frontend_release.py --execute --run-post-verify`.
9. Rebuild or refresh APK if the APK bundles frontend assets.
10. Re-run Agent model smoke only when rotating the model provider/key; current staging cloud model is live.
11. Run `tools/qa_rehab_mobile_l1_release.py`; it must return exit code `0` and `overall = PASS`.
12. Run `tools/qa_rehab_mobile_l1_objective_audit.py`; it must return exit code `0` and every objective requirement must be `PASS`.
13. If either gate fails, inspect the nested `api`, `frontend`, and `requirements` sections before changing code.
14. Export the L1 evidence bundle with `tools/export_rehab_mobile_l1_evidence.py`; use `--fail-on-l1-fail` in CI/release jobs.
15. Browser QA at exactly `390 x 844`:
   - Home first screen.
   - `问康复师` chat open.
   - Unsafe Agent refusal.
   - Device binding wizard.
   - Profile account/phone/medical empty state.
16. Run `tools/qa_rehab_mobile_browser_metrics.py` against the saved browser
    metrics JSON; it must return exit code `0` with `overall = PASS`, and pass that
    output to `tools/qa_rehab_mobile_l1_objective_audit.py --browser-metrics-json`.
17. Update this scorecard after every large task.

## Git Discipline

Every future code or QA artifact change should end with:

1. `git status --short`
2. Run relevant tests or smoke checks.
3. Stage only task-relevant files.
4. `git diff --cached --check`
5. Commit with a focused message.
6. Record commit hash in the final update.
