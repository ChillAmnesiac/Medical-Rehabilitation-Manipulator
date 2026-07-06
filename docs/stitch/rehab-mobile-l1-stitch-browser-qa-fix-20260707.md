# Rehab Mobile L1 Stitch Browser QA Fix - 2026-07-07

## Purpose

Record the latest Stitch MCP attempt after current cloud browser QA confirmed
the L1 blocker is still the frontend.

## Current Cloud Status

- `tools/qa_rehab_mobile_l1_release.py --timeout 60`: `overall = FAIL`.
- API side: `PASS`, `p0_failed = 0`, `total = 22`.
- Frontend side: `FAIL`, `failed = 5`.
- Objective audit still blocks on home next step, phone UI, device UI, Ask
  Therapist UI, profile cleanup, browser evidence, and combined release.
- `agent_cloud_model` is `PASS`.

## Stitch Project

- Project: `projects/323711356322969905`.
- Initial Ask Therapist screen: `9deadaaf358a4a908bd704f580e6a69f`.
- Edited/fixed Ask Therapist screen: `f1a50687ed4d429786f9d84e7e37a5cf`.
- Downloaded local HTML:
  `artifacts/stitch/l1-browser-qa-fix-20260707/ai-plan-stitch-fixed.html`.
- Browser screenshot:
  `docs/qa/rehab-mobile-20260706/screenshots/stitch-ai-plan-fix-candidate-v2-20260707-390x844.png`.

## Fixed Candidate Browser QA

At `390 x 844`:

- Required copy present: `问康复师`, `云端康复师已连接`, unsafe-control refusal.
- Forbidden hits: none for `M33`, `M55`, `SPP`, `CAN`, `UUID`,
  `setup_required`, `early_active`, `direct_motor_command`, `can_frame`,
  `Gatekeeper`, `RoboRehab Controller`, `bluetooth-debug`, `患者 A`, `ID: 8829`,
  or `避免过度伸展`.
- Horizontal overflow: none.
- Back/add/input/send controls: at least `48px` high.
- Bottom nav controls: real buttons, `64 x 48`.
- Composer/nav spacing: composer bottom `768`, nav top `789`, gap `21px`.

## Acceptance Boundary

This candidate is **not accepted for deployment** because it covers only
`ai-plan.html`. The next Stitch work must produce and QA all four real app
pages:

- `home.html`: clear next action `查看康复师建议` and visible `问康复师`.
- `profile.html`: cloud account, phone verification path, rehab profile, safe
  empty medical state.
- `device.html`: patient binding wizard led by `绑定设备` and
  `打开康复设备电源`.
- `ai-plan.html`: fixed Ask Therapist chat surface from this attempt, wired to
  the Agent API.

After Stitch returns full files, apply them only through the real App branch
`app/rehab-arm-mobile-stitch`, mirror Android WebView assets, run source gate,
browser metrics, release manifest verification, cloud deployment with
post-deploy checks, APK verification, and final objective audit.
