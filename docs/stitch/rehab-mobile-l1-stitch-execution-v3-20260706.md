# Stitch Execution Prompt V3 - Rehab Mobile L1 Gate Closure

Paste this prompt into Google Stitch. It supersedes V2 for the next frontend pass.

```text
Repository: https://github.com/wenjunyong666/ai-
Branch: app/rehab-arm-mobile-stitch
Frontend path: apps/web/public/rehab-arm-mobile/

Edit only frontend files. Do not change backend code.

Use this live API:
http://106.55.62.122:8011

Use this sanitized live fixture before editing:
docs/stitch/rehab-mobile-l1-api-fixture-20260706.json

This fixture now includes:
- health
- public_config
- me.data.profile
- me.data.patient_view.home/profile/device/agent
- agent.safe_response
- agent.unsafe_response
- phone_verification.start_response
- phone_verification.confirm_response

Do not hard-code fixture values. Use the fixture only to understand response
shape and required field names. Fetch live data at runtime.

Previous complete prompt:
docs/stitch/rehab-mobile-l1-stitch-execution-v2-20260706.md

Implement all V2 requirements, plus these latest L1 gate blockers from Codex.

Current automated L1 status:
- API: PASS
- APK: PASS
- Frontend: FAIL, 5 failed gates
- Blocking gates: frontend_l1_gate and agent_cloud_model

Important: Stitch cannot clear agent_cloud_model by UI work alone. The frontend
must still render `data.agent.model_readiness` honestly:
- fallback_rule_based -> show safe-rule helper
- cloud_model_configured / cloud_model -> show cloud-model helper

Codex will clear agent_cloud_model separately after a real model relay key is
configured with:
docs/deployments/rehab-mobile-agent-model-relay-runbook-20260706.md

Frontend must clear all of these exact failures:

1. L1-HOME-STATIC-001
Current missing term:
- 问康复师
Current forbidden terms:
- M33
- M55
- RoboRehab Controller

Required home behavior:
- Render from `me.data.patient_view.home`.
- Show one dominant next action from `home.primary_action`.
- Show visible `问康复师` from `patient_view.agent.entry_label`.
- Do not show M33, M55, RoboRehab Controller, setup_required, action_queue,
  blockers, forbidden_actions, raw workflow status, or debug hardware language.
- Do not show false `网络未连接，请检查后端服务` while health/auth/me are reachable.

2. L1-PROFILE-STATIC-001
Current missing terms:
- 我的康复档案
- 手机号
- 绑定手机号
- 验证码
Current forbidden terms:
- M33
- M55
- 患者 A
- ID: 8829
- 避免过度伸展
- RoboRehab Controller

Required profile behavior:
- Title must be `我的康复档案`.
- Render from `me.data.patient_view.profile` and `me.data.profile`.
- Show cloud account, masked phone, verified state, and a visible change/bind
  phone path.
- Keep static/rendered text for a new-user path containing `绑定手机号` and
  `验证码`, even when the current QA account is already verified.
- Use the fixture `phone_verification.start_response` and
  `phone_verification.confirm_response` to wire the start/confirm flow.
- Never show demo patient, fake ID, fake warning, or engineering device fields.

Phone binding endpoints:
- POST /api/rehab-arm/app/v1/account/phone-verifications
  Body: { "phone": "...", "purpose": "bind_account" }
- POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm
  Body: { "code": "..." }

Use response `verification_id` from the start call to build the confirm URL.
In production, never show raw debug_code. In staging debug_sms mode only, a
small test-helper line may show the backend-provided test code.

3. L1-DEVICE-STATIC-001
Current missing terms:
- 绑定设备
- 打开康复设备电源
Current forbidden terms:
- M33
- M55
- UUID
- Gatekeeper

Required device behavior:
- Render from `me.data.patient_view.device`.
- Normal user page is a binding wizard, not bluetooth-debug.html.
- First visible wizard step must include `打开康复设备电源`.
- Show `绑定设备` as the normal primary action for unbound state.
- Hide M33/M55/UUID/Gatekeeper/debug transport language from normal users.
- If a debug path remains, label it `开发者调试`, keep it secondary, and do not
  route normal binding actions directly to bluetooth-debug.html.

Device bind endpoint:
- POST /api/rehab-arm/app/v1/devices/bind
  Body: { "m33_device_id": "...", "ble_name": "...", "trust_status": "trusted" }

Patient-facing copy may say:
- 设备已绑定，训练前仍会进行安全确认。
- 这台设备已绑定到其他账号。如需更换账号，请联系康复师或管理员处理。

4. L1-AGENT-STATIC-001
Current missing term:
- 问康复师

Required Agent behavior:
- Visible label and aria-label must be `问康复师`.
- Top entry and floating entry open the same chat.
- Use `me.data.patient_view.agent` for title, placeholder, quick questions,
  endpoint, unsafe copy, and boundary.
- POST messages to `/api/rehab-arm/app/v1/agent/messages` with Bearer token.
- Render `data.answer`, `data.boundary`, and `data.model_status`.
- If 400 `UNSAFE_MOTION_REQUEST`, show patient-protective Chinese copy, not a
  generic error.

5. L1-FRONTEND-INTEGRATION-001
Current missing source/API references:
- patient_view_home
- patient_view_profile
- patient_view_device
- patient_view_agent
- phone_verification_start
- phone_verification_confirm
- agent_messages

Required source wiring:
- `POST /api/auth/session`
- `GET /api/rehab-arm/app/v1/me`
- `data.patient_view.home`
- `data.patient_view.profile`
- `data.patient_view.device`
- `data.patient_view.agent`
- `POST /api/rehab-arm/app/v1/account/phone-verifications`
- `POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm`
- `POST /api/rehab-arm/app/v1/devices/bind`
- `POST /api/rehab-arm/app/v1/agent/messages`

Current browser failure screenshot:
docs/qa/rehab-mobile-20260706/screenshots/model-relay-ops-device-390.png

Codex will reject the next frontend build unless this command passes the
frontend section:

```powershell
$env:REHAB_QA_EMAIL='3245056131@qq.com'
$env:REHAB_QA_PASSWORD='1234'
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_release.py
```

After frontend deployment, Codex will also capture 390x844 browser screenshots:
- home first screen
- profile phone binding path
- device binding wizard
- Ask therapist chat
- unsafe Agent refusal
```
