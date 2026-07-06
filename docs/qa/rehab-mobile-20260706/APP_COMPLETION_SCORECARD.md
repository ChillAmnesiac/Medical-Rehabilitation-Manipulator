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
| Backend API | PASS | Latest cloud acceptance resmoke on 2026-07-07 ran `tools/qa_rehab_mobile_acceptance.py --timeout 25` with staging credentials in process env only: exit code `0`, `overall = PASS`, `p0_failed = 0`, `total = 22`, failed gates none. Remaining warnings are known non-P0 items: production SMS delivery is still `debug_sms`, and rendered browser interaction evidence depends on the frontend fix |
| Deployment metadata | PASS | `P1-DEPLOY-META-001`: latest health verification exposed build SHA `a4d1c1565de3`, ref `ai/game-loop-core`, build time `2026-07-06T20:59:56Z`, and `app_env=staging` |
| Stitch API fixture | PASS | `docs/stitch/rehab-mobile-l1-api-fixture-20260706.json` refreshed from live cloud API at `2026-07-06T21:10:05Z` with tokens, numeric codes, ids, email, and phone masked; it now proves `patient_view` core copy, phone verification start/confirm, unsafe Agent refusal, and `model_status.mode = cloud_model`, provider `qwen`, model `qwen-plus` |
| Stitch L1 UI contract | PASS | `docs/stitch/rehab-mobile-l1-ui-contract-20260707.json` now extracts a compact patient-facing contract from the live fixture for Stitch generation: four required pages, exact visible copy, POST action endpoints, phone/device/Agent states, and cloud model status. It omits broad legacy public-config payloads such as `m33_legacy_spp_profile`, raw email, access tokens, and numeric debug codes |
| Stitch repair packet and V4 prompt | PASS | `docs/stitch/rehab-mobile-l1-repair-packet-20260706.json` generated from the live cloud L1 release gate, current deployed objective audit, and current deployed browser metrics; `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` is generated from the packet and is now the primary Stitch handoff. The packet/prompt now show `non_stitch_blockers = []`, include SMS ops readiness, L1 evidence export, no raw staging email/password, an `Exact Release-Gated Visible Copy` section, hexadecimal HTML entity fallback snippets, a `Stitch Browser Candidate QA Blockers` section, a `Current Deployed Browser QA Blockers` section with `docs/qa/rehab-mobile-20260706/browser-metrics-current-deployed-20260707.json`, current deployed screenshots, `M33`/`M55`/`Gatekeeper` hits, and 9 undersized touch targets, plus the release-gated `L1-FRONTEND-PRIVACY-001` rule forbidding hard-coded staging email/password, Bearer tokens, SMS debug codes, and API keys |
| Stitch source scope | PASS | Real frontend branch verified as `app/rehab-arm-mobile-stitch` at commit `eaa08a40cdd3e1e62827809111f2323e7f92556f`; prompt/packet now identify web edit path `apps/web/public/rehab-arm-mobile/` and APK WebView mirror path `apps/mobile/rehab-arm-android/www/` |
| Stitch MCP generation attempt | REJECTED AFTER API-ACTION HARDENING, NOT DEPLOYED | Stitch project `projects/323711356322969905` produced a full local four-page v3 candidate: Home `767c6e263ec646f7b27664c385e3ba4c`, Profile `b1c634dd4d6640beac7fc7a9a3515cb7`, Device `aadf5ed620314ac1b0a33a27089e2cd4`, Ask Therapist `5a10e02454c044f38e60a7292064566b`. Browser QA still passes at `390 x 844` with screenshots `screenshots/stitch-full-candidate-v3-home/profile/device/ai-plan-20260707-390x844.png` and metrics report `docs/qa/rehab-mobile-20260706/browser-metrics-stitch-full-candidate-v3-20260707.json`. However the post-hardened source gate `docs/qa/rehab-mobile-20260706/frontend-l1-source-gate-stitch-full-candidate-v3-post-hardened-20260707.json` now returns `overall = FAIL`, blockers `no_mock_api_behavior`, `phone_verification_start_post`, `phone_verification_confirm_post`, `device_bind_post`, and `agent_messages_post`, with hits `mockData`, `Simulate API response`, and `In real app`. This candidate must not be deployed or copied into the real App branch until Stitch returns pages with real POST calls for phone verification, device binding, and Ask Therapist messages |
| Stitch MCP auth resmoke | BLOCKED BY STITCH AUTH | After the V4 prompt was updated with current deployed browser QA blockers, Codex retried `mcp__stitch.list_screens(projectId = "323711356322969905")`. The Stitch MCP returned `401 invalid authentication credentials`, requiring a valid OAuth 2 access token, login cookie, or equivalent project credential. No new Stitch screen was generated, no frontend files were copied, no Android WebView assets were changed, and no cloud deployment or APK rebuild was performed in this pass |
| Frontend source API-action hardening | PASS | `tools/qa_rehab_mobile_l1_frontend.py` rejects source that only includes API contract tokens while using mocked/simulated behavior or missing POST methods on user actions. Regressions `test_frontend_integration_contract_rejects_mocked_api_behavior` and `test_frontend_integration_contract_rejects_action_endpoints_without_post_methods` failed first, then passed after adding `no_mock_api_behavior` and POST action requirements. Current focused frontend tests include API-action and privacy coverage: `14 passed`. `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` tells Stitch not to use `mockData`, mock responses, `Simulate API response`, `In real app`, or console-only behavior, and to use `method: 'POST'` for phone start/confirm, device bind, and Agent messages |
| Frontend source privacy gate | PASS | `tools/qa_rehab_mobile_l1_frontend.py` now adds `L1-FRONTEND-PRIVACY-001`, rejecting Stitch exports that hard-code staging email addresses, `REHAB_QA_EMAIL` / `REHAB_QA_PASSWORD`, literal Bearer tokens, numeric SMS `debug_code` fixtures, Google/Stitch-style API keys, or model-provider `sk-*` keys. The gate reports only hit categories, not matched secret values. Red privacy tests failed before implementation, then `tools/test_qa_rehab_mobile_l1_frontend.py` passed with `14 passed`; prompt tests passed with `4 passed`. Refreshed current deployed release evidence shows `L1-FRONTEND-PRIVACY-001 = PASS`, `privacy_hits = []`, while overall L1 remains blocked by frontend rendering and APK WebView assets |
| Frontend release packaging | PASS | `tools/qa_rehab_mobile_l1_frontend.py --source-dir --output` preflights Stitch output locally and preserves JSON evidence; `tools/prepare_rehab_mobile_frontend_release.py` refuses failing frontend sources, writes a deployable zip, and records manifest deploy/verification commands before cloud copy, including the `browser-metrics-l1-390x844.json` browser metrics gate; release manifests no longer write raw staging email/password values |
| Frontend release package verification | PASS | `tools/verify_rehab_mobile_frontend_release.py` validates the generated manifest schema, zip sha256, preflight report, required page artifacts, guarded deploy executor command, exact browser QA screenshot checklist, and a real `browser-metrics-gate.json` with `L1-BROWSER-METRICS-001 = PASS` plus full `home/profile/device/ai-plan` coverage before cloud deployment |
| APK WebView mirror verification | PASS | `tools/verify_rehab_mobile_webview_mirror.py` checks that `apps/mobile/rehab-arm-android/www/` is byte-identical to `apps/web/public/rehab-arm-mobile/`, including required pages and no stale extra files; release manifests now require this command before APK packaging |
| APK packaged WebView asset verification | TOOL READY, CURRENT APK FAILS | `tools/verify_rehab_mobile_apk_webview_assets.py` now opens the APK as a zip and verifies `assets/public/` is byte-identical to `apps/mobile/rehab-arm-android/www/`, including required pages and no stale extras. Release manifests and the combined L1 release gate now require this check before L1 acceptance. Current evidence `docs/qa/rehab-mobile-20260706/apk-webview-assets-current-20260707.json` and `docs/qa/rehab-mobile-20260706/l1-release-current-with-apk-assets-20260707.json` are `overall = FAIL` because the real App checkout currently lacks `apps/mobile/rehab-arm-android/www/`; the current APK contains 20 `assets/public` files, including stale/debug routes such as `bluetooth-debug.html` |
| Frontend release deployment guard | PASS | `tools/deploy_rehab_mobile_frontend_release.py` verifies the manifest again, defaults to dry-run, refuses unsafe remote roots, and now enforces `--run-post-verify` whenever `--execute` is used, so cloud copy cannot run without post-deploy checks. The generated post-deploy objective audit now consumes `artifacts/rehab-mobile-frontend-release/browser-metrics-gate.json` explicitly instead of falling back to stale/default browser evidence |
| Stitch frontend promotion gate | PASS | `tools/promote_rehab_mobile_stitch_frontend.py` now gates Stitch exports before they can replace real web or Android WebView assets. It runs the local L1 frontend preflight, defaults to dry-run, refuses failing candidates without copying, rejects QA/report files mixed into the promotion source, and on `--execute` mirrors accepted files into both targets before writing `webview-mirror-verification.json`. TDD coverage: `tools/test_promote_rehab_mobile_stitch_frontend.py`, `5 passed`; related release/frontend chain: `35 passed`. Current v3 candidate dry-run evidence in `docs/qa/rehab-mobile-20260706/stitch-promotion-current-candidate-20260707/` remains `overall = FAIL`, `copied = false`, because source still contains `mockData`, `Simulate API response`, `In real app`, lacks POST action evidence, and is not a clean frontend package due mixed-in `browser-*` / `frontend-l1-*` JSON reports |
| Frontend deployment metrics regression coverage | PASS | 2026-07-07 focused deploy/release verifier suite now covers a realistic `browser-metrics-gate.json` fixture and proves `deploy_rehab_mobile_frontend_release.py --execute` refuses to run deploy commands when that gate output is missing; fresh focused result: `16 passed` |
| L1 release evidence bundle | PASS | `tools/export_rehab_mobile_l1_evidence.py` exports one JSON snapshot with cloud health, git HEAD, App checkout git HEAD, combined L1 release gate, objective audit, browser evidence status, APK HEAD, APK WebView asset targets, and required follow-up artifacts; the exporter now records `target.browser_metrics_json`, `target.app_checkout_dir`, `target.apk_file`, `target.android_www_dir`, `target.apk_asset_prefix`, `app_git`, top-level `apk_webview_assets_*` summary fields, and the objective audit's `browser_evidence.browser_metrics` status. Current bundle `docs/qa/rehab-mobile-20260706/l1-evidence-current-with-apk-assets-20260707.json` now points at current deployed browser metrics `docs/qa/rehab-mobile-20260706/browser-metrics-current-deployed-20260707.json`; it is `overall = FAIL` with App checkout `app/rehab-arm-mobile-stitch` at `eaa08a40cdd3e1e62827809111f2323e7f92556f`, `dirty = false`, and release blockers `frontend_l1_gate` and `apk_webview_assets` |
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
| Combined L1 release gate | FAIL | `tools/qa_rehab_mobile_l1_release.py` now includes APK WebView asset parity. Fresh evidence `docs/qa/rehab-mobile-20260706/l1-release-current-with-apk-assets-20260707.json`: API `PASS`, frontend `FAIL`, APK WebView assets `FAIL`, blockers `frontend_l1_gate` and `apk_webview_assets` |
| Objective-level L1 audit | FAIL | `tools/qa_rehab_mobile_l1_objective_audit.py` now includes an explicit `apk_webview_assets` requirement. Fresh deployed-browser evidence `docs/qa/rehab-mobile-20260706/objective-audit-current-deployed-browser-20260707.json`: 8/12 objective requirements failing: home next step, phone UI, device UI, Ask Therapist UI, profile no-fake-data, APK WebView asset parity, browser evidence, combined release; browser evidence now consumes `docs/qa/rehab-mobile-20260706/browser-metrics-current-deployed-20260707.json`, which covers `home`, `profile`, `device`, and `ai-plan` but fails on engineering/debug copy and undersized touch targets |
| Current deployed browser evidence | CAPTURED, CURRENT FAIL | In-app browser QA captured current deployed home/profile/device screenshots at `375 x 812` and Ask Therapist/AI plan at `390 x 844`: `screenshots/current-deployed-home/profile/device-20260707-375x812.jpg` and `screenshots/current-deployed-ai-plan-20260707-390x844.jpg`. These document blockers only and intentionally do not satisfy the exact L1 success screenshot requirement |
| Home UI | FAIL | Current deployed browser metrics `docs/qa/rehab-mobile-20260706/browser-metrics-current-deployed-20260707.json` still finds `M33` and `M55` on home; screenshot `screenshots/current-deployed-home-20260707-375x812.jpg` shows `M33 ACTIVE` / `M33 授权` and no patient-first phone/device/therapist next step |
| Agent UI | FAIL | Current deployed `ai-plan` screenshot `screenshots/current-deployed-ai-plan-20260707-390x844.jpg` remains a training-draft form, not a patient-facing `问康复师` chat with safe answer/refusal evidence; browser metrics also reports undersized AI plan input/select controls |
| Device UI | FAIL | Current deployed device screenshot `screenshots/current-deployed-device-20260707-375x812.jpg` still shows engineering architecture and debug copy; browser metrics finds `M33`, `M55`, and `Gatekeeper`, while static gate `L1-DEVICE-STATIC-001` requires a patient binding wizard with `绑定设备` and `打开康复设备电源` |
| Profile UI | FAIL | Current deployed profile screenshot `screenshots/current-deployed-profile-20260707-375x812.jpg` still shows `患者 A`, `M33`, and `M55` instead of cloud account, verified phone, phone binding code path, rehab profile, and safe medical empty state |
| Frontend API integration | FAIL | `L1-FRONTEND-INTEGRATION-001` is missing `patient_view` wiring, Ask Therapist accessibility, phone verification start/confirm/cooldown/SMS error handling, device already-bound handling, Agent messages, unsafe refusal, and model-status rendering |

## Next Work Order

1. Obtain a new Stitch output for the real App branch `app/rehab-arm-mobile-stitch`; it must use the L1 UI contract and must not contain mock/simulated API behavior.
2. Export or copy the Stitch output into a clean frontend-only directory containing web assets only; do not use a QA work directory that contains `browser-*`, `frontend-l1-*`, release manifest, or promotion report JSON files.
3. Run `tools/promote_rehab_mobile_stitch_frontend.py --stitch-source-dir <clean-stitch-output> --web-dir apps/web/public/rehab-arm-mobile --android-www-dir apps/mobile/rehab-arm-android/www --output-dir artifacts/rehab-mobile-stitch-promotion/<stamp>` as dry-run first. It must return `overall = PASS`, `copied = false`, and `package_cleanliness.status = PASS`.
4. Only after dry-run PASS, run the same command with `--execute`; it must return `overall = PASS`, `copied = true`, and write `webview-mirror-verification.json`.
5. Run `tools/qa_rehab_mobile_l1_frontend.py --source-dir apps/web/public/rehab-arm-mobile --output artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json`.
6. Run `tools/verify_rehab_mobile_webview_mirror.py --web-dir apps/web/public/rehab-arm-mobile --android-www-dir apps/mobile/rehab-arm-android/www --output artifacts/rehab-mobile-frontend-release/webview-mirror-verification.json`; it must return exit code `0` and `summary.overall = PASS`.
7. Package updated frontend web assets with `tools/prepare_rehab_mobile_frontend_release.py`.
8. Verify the generated release manifest with `tools/verify_rehab_mobile_frontend_release.py` before any cloud copy.
9. Dry-run `tools/deploy_rehab_mobile_frontend_release.py` and review the planned `scp`, `ssh`, and post-deploy verification commands.
10. Deploy the reviewed frontend bundle with `tools/deploy_rehab_mobile_frontend_release.py --execute --run-post-verify`.
11. Rebuild or refresh APK if the APK bundles frontend assets.
12. Run `tools/verify_rehab_mobile_apk_webview_assets.py --apk apps/web/public/downloads/rehab-arm/lingdong-rehab-arm-debug.apk --android-www-dir apps/mobile/rehab-arm-android/www --asset-prefix assets/public --output artifacts/rehab-mobile-frontend-release/apk-webview-assets-verification.json`; it must return exit code `0` and `summary.overall = PASS`.
13. Re-run Agent model smoke only when rotating the model provider/key; current staging cloud model is live.
14. Run `tools/qa_rehab_mobile_l1_release.py`; it must return exit code `0` and `overall = PASS`.
15. Run `tools/qa_rehab_mobile_l1_objective_audit.py`; it must return exit code `0` and every objective requirement must be `PASS`.
16. If either gate fails, inspect the nested `api`, `frontend`, and `requirements` sections before changing code.
17. Export the L1 evidence bundle with `tools/export_rehab_mobile_l1_evidence.py`; use `--fail-on-l1-fail` in CI/release jobs.
18. Browser QA at exactly `390 x 844`:
   - Home first screen.
   - `问康复师` chat open.
   - Unsafe Agent refusal.
   - Device binding wizard.
   - Profile account/phone/medical empty state.
19. Run `tools/qa_rehab_mobile_browser_metrics.py` against the saved browser
    metrics JSON; it must return exit code `0` with `overall = PASS`, and pass that
    output to `tools/qa_rehab_mobile_l1_objective_audit.py --browser-metrics-json`.
20. Update this scorecard after every large task.

## Git Discipline

Every future code or QA artifact change should end with:

1. `git status --short`
2. Run relevant tests or smoke checks.
3. Stage only task-relevant files.
4. `git diff --cached --check`
5. Commit with a focused message.
6. Record commit hash in the final update.
