# Lingdong Rehab Cloud

Backend MVP for the Stitch mobile rehab app at branch `app/rehab-arm-mobile-stitch`.

## Safety Boundary

The cloud service authenticates users, stores profile/device/session evidence, generates plan suggestions, and prepares transport frames. It never directly controls motors. Real movement remains:

`JointTrajectory -> NanoPi -> M33 safety/control layer -> motors`

## Local Run

```powershell
cd cloud/rehab-platform
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest -v
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8011/health
```

## Docker

```powershell
cd cloud/rehab-platform
docker compose up --build -d
```

The API listens on `http://SERVER_IP:8011`.

## Mobile App Contract

The backend exposes the routes already used by `apps/web/public/rehab-arm-mobile/mobile-bridge.js`:

- `POST /api/auth/session`
- `GET /api/rehab-arm/app/v1/public-config`
- `GET /api/rehab-arm/app/v1/catalog`
- `GET /api/rehab-arm/app/v1/me`
- `PUT /api/rehab-arm/app/v1/me/profile`
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

### Phone Verification

`POST /api/rehab-arm/app/v1/account/phone-verifications` creates a short-lived code for binding the signed-in account to a phone number. Staging can expose `debug_code` for automated QA with `PHONE_VERIFICATION_DEBUG_CODE_ENABLED=true`; production-like deployments should disable it and use a real SMS provider. Wrong-code attempts are capped by `PHONE_VERIFICATION_MAX_ATTEMPTS`, and immediate resend is throttled by `PHONE_VERIFICATION_RESEND_COOLDOWN_SECONDS`. A throttled resend returns `429 PHONE_CODE_RESEND_TOO_SOON` with `retry_after` seconds for the app countdown.

### Device Binding

`POST /api/rehab-arm/app/v1/devices/bind` treats `m33_device_id` as the hardware ownership key. Repeating the same bind from the signed-in account updates the existing device record and returns the same `id`. If another account already owns that `m33_device_id`, the endpoint returns `409 DEVICE_ALREADY_BOUND` so the app can show a recoverable already-bound state instead of silently claiming the device.

### Rehab Therapist Agent

`POST /api/rehab-arm/app/v1/agent/messages` uses a configured cloud model when `AGENT_MODEL_API_KEY` is set. Supported providers are:

- `openai_compatible`: chat completions endpoint, for example `AGENT_MODEL_BASE_URL=https://api.openai.com/v1`
- `gemini`: Google Gemini `generateContent`, for example `AGENT_MODEL_BASE_URL=https://generativelanguage.googleapis.com/v1beta`

If no external model is configured or the provider is unavailable, the endpoint safely falls back to a rule-based patient answer and always returns `data.model_status`.

Required response status contract:

- `model_status.mode = cloud_model` when the external model answered.
- `model_status.mode = fallback_rule_based` when the backend used the safe local fallback.
- Unsafe direct-control or safety-bypass requests still return `400 UNSAFE_MOTION_REQUEST`.

## QA Gate

Before calling a milestone complete:

1. Run `python -m pytest -v`.
2. Start the API locally and check `/health`.
3. Point the Stitch app API base to the deployed API.
4. Login, bind device, generate and accept an AI plan, sync it, and confirm a sendable legacy frame.
5. Build the install package and record artifact path plus smoke-test result.
