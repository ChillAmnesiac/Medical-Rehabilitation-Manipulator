# Rehab Mobile L1 Stitch Browser QA Fix - 2026-07-07

## Purpose

Record the latest Stitch MCP attempts after current cloud browser QA confirmed
the L1 blocker is still the frontend, including the first full four-page local
candidate that passes both source and rendered browser metrics gates.

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
- Full candidate screens:
  - Home: `767c6e263ec646f7b27664c385e3ba4c`.
  - Profile: `b1c634dd4d6640beac7fc7a9a3515cb7`.
  - Device: `aadf5ed620314ac1b0a33a27089e2cd4`.
  - Ask Therapist: `5a10e02454c044f38e60a7292064566b`.

## Single-Page Fix Evidence

The first useful Stitch repair covered only `ai-plan.html`.

- Downloaded local HTML:
  `artifacts/stitch/l1-browser-qa-fix-20260707/ai-plan-stitch-fixed.html`.
- Browser screenshot:
  `docs/qa/rehab-mobile-20260706/screenshots/stitch-ai-plan-fix-candidate-v2-20260707-390x844.png`.
- Local browser QA at `390 x 844` found required Ask Therapist copy, no
  forbidden engineering/demo hits, no horizontal overflow, `64 x 48` bottom-nav
  controls, and a `21px` composer/nav gap.

This single-page artifact was not deployable because it did not cover home,
profile, device, Android WebView mirroring, cloud deployment, or APK packaging.

## Full Four-Page Candidate V3

Key product fixes:

- Home shows a clear patient next step and `问康复师` entry without fake names.
- Profile shows cloud account, phone binding, verification code input, and safe
  medical-profile empty state.
- Profile source handles `PHONE_CODE_RESEND_TOO_SOON` with `retry_after`.
- Device shows a patient binding wizard and already-bound recovery copy.
- Ask Therapist shows `云端模型：已连接` and includes source field
  `model_status`.
- Unsafe motion/control requests show protective Chinese refusal copy.

Local source gate:

- Report:
  `docs/qa/rehab-mobile-20260706/frontend-l1-source-gate-stitch-full-candidate-v3-20260707.json`.
- Result: `overall = PASS`, `failed = 0`, `total = 5`.
- Hardened report after API-mock detection:
  `docs/qa/rehab-mobile-20260706/frontend-l1-source-gate-stitch-full-candidate-v3-hardened-20260707.json`.
- Hardened result: `overall = FAIL`, blocker `no_mock_api_behavior`, with
  source hits `mockData`, `Simulate API response`, and `In real app`.

Rendered browser metrics gate:

- Viewport: `390 x 844`.
- Screenshots:
  - `docs/qa/rehab-mobile-20260706/screenshots/stitch-full-candidate-v3-home-20260707-390x844.png`.
  - `docs/qa/rehab-mobile-20260706/screenshots/stitch-full-candidate-v3-profile-20260707-390x844.png`.
  - `docs/qa/rehab-mobile-20260706/screenshots/stitch-full-candidate-v3-device-20260707-390x844.png`.
  - `docs/qa/rehab-mobile-20260706/screenshots/stitch-full-candidate-v3-ai-plan-20260707-390x844.png`.
- Report:
  `docs/qa/rehab-mobile-20260706/browser-metrics-stitch-full-candidate-v3-20260707.json`.
- Result: `overall = PASS`; all four pages covered with no fake copy,
  undersized touch targets, input overlap, overflow, or vertical text.

## Acceptance Boundary

The V3 candidate is **not accepted for deployment**. It passes visual browser
metrics but fails the hardened source gate because parts of the generated
JavaScript still simulate backend responses instead of relying only on real
cloud API responses. It also still exists as downloaded Stitch HTML in a local
artifact directory and has not been applied through the real App branch
`app/rehab-arm-mobile-stitch`, mirrored into Android WebView assets, deployed
to the cloud URL, packaged into a new APK, or verified by the combined cloud L1
release gate.

Next work is to get a new Stitch output that makes real backend calls for phone
verification, device binding, and Ask Therapist messages, then apply only that
accepted output through the real App branch, mirror Android WebView assets, run
source gate, browser metrics, release manifest verification, cloud deployment
with post-deploy checks, APK verification, and final objective audit.
