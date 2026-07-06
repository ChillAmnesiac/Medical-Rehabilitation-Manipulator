# Stitch Prompt: Wire The Rehab App To The Cloud Backend

Use this prompt in Google Stitch for the real mobile app branch `app/rehab-arm-mobile-stitch`.

## Goal

Turn the current debug-like rehab PWA into a patient-friendly mobile app backed by the deployed Lingdong Rehab Cloud API. Do not fake success states in the UI. Show cloud state, device trust, AI draft state, and M33 safety status clearly.

## API Base

Default backend API base:

`http://106.55.62.122:8011`

Allow a user/developer override via existing `rehabArmMobileApiBase` localStorage key.

## Required Routes

Keep using the existing `mobile-bridge.js` API wrapper and these endpoints:

- `POST /api/auth/session`
- `GET /api/rehab-arm/app/v1/public-config`
- `GET /api/rehab-arm/app/v1/catalog`
- `GET /api/rehab-arm/app/v1/me`
- `PATCH /api/rehab-arm/app/v1/me/profile`
- `POST /api/rehab-arm/app/v1/account/phone-verifications`
- `POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm`
- `GET /api/rehab-arm/app/v1/me/workflow`
- `POST /api/rehab-arm/app/v1/me/workflow/actions`
- `POST /api/rehab-arm/app/v1/devices/bind`
- `POST /api/rehab-arm/app/v1/devices/{device_id}/legacy-spp/inbound`
- `GET /api/rehab-arm/app/v1/emg/latest`
- `POST /api/rehab-arm/app/v1/ai-training-drafts/generate`
- `POST /api/rehab-arm/app/v1/ai-training-drafts/{draft_id}/accept`
- `POST /api/rehab-arm/app/v1/training-plans/{plan_id}/sync-to-device`
- `POST /api/rehab-arm/app/v1/devices/{device_id}/ble/messages`
- `POST /api/rehab-arm/app/v1/training-sessions`
- `GET /api/rehab-arm/app/v1/training-sessions/recent`
- `POST /api/rehab-arm/app/v1/agent/messages`

## UX Requirements

1. Home should feel like a daily rehab command center: next step, device status, latest report, and one primary action.
2. Account/profile should support login, phone, rehab stage, affected side, and medical constraints without looking like a debug panel.
3. Device binding should read as a safe guided flow: phone Bluetooth permission, bind trusted M33 device, sync plan, wait for M33 acceptance.
4. AI should be positioned as a rehab therapist agent. It can answer questions and draft plans, but cannot directly move hardware.
5. Replace raw technical terms in primary UI. Keep M33, preflight, and legacy SPP details in expandable technical sections.
6. Training completion should post a session summary and then show the generated report.
7. Reports/profile should render `care_timeline.items` as a friendly rehab activity log.

## Safety Copy

Always preserve this product truth:

The app and cloud suggest plans and transport evidence only. Real movement requires M33 safety acceptance and preflight.
