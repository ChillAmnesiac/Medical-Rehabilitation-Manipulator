# Stitch Execution Prompt - Rehab Mobile Patient-Ready Fixes 2026-07-06

Use this prompt in Google Stitch. Edit only the frontend app.

```text
Repository: https://github.com/wenjunyong666/ai-
Branch: app/rehab-arm-mobile-stitch
Frontend path: apps/web/public/rehab-arm-mobile/

Production targets:
- Web: http://106.55.62.122:3001/rehab-arm-mobile/
- API: http://106.55.62.122:8011
- APK URL: http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk

Context:
Backend/API acceptance is already green. The current frontend is still not patient-ready.
Use the backend patient presentation contract as the primary source for normal user screens:

GET http://106.55.62.122:8011/api/rehab-arm/app/v1/me
Authorization: Bearer <token>

Read:
- response.data.profile
- response.data.patient_view.home
- response.data.patient_view.profile
- response.data.patient_view.device
- response.data.patient_view.agent

Do not render raw workflow/debug fields to normal users.

Authentication:
- Login endpoint: POST http://106.55.62.122:8011/api/auth/session
- Body: { "email": "...", "password": "..." }
- Store the returned bearer token for the session.
- Send Authorization: Bearer <token> on authenticated app APIs.
- If token is missing/expired, route to login or show a clear login-needed state.

Hard UX rule:
This is a rehab patient app, not an engineering console. Normal users must never see:
- M33, M55, SPP, CAN, UUID
- preflight, setup_required, early_active
- direct_motor_command, can_frame_send, m33_safety_override
- motion_permission_granted_by_app, control_boundary, payload_hint
- raw action_queue, blockers, forbidden_actions
- backend-approved frame, raw frame, transport frame

Known QA evidence from 2026-07-06:
- Home screenshot shows false "网络未连接，请检查后端服务" even though API smoke passes.
- Home exposes setup_required, early_active, left, M33, action queue, blockers, forbidden actions.
- Top assistant-like icon click does nothing and is effectively labelled like Settings.
- Floating assistant button click/focus does not open chat.
- Device page still shows workflow/debug content and hardware internals.
- Profile shows demo identity "患者 A", fake ID 8829, fake medical warning "避免过度伸展 > 120°", and M33/M55 devices.

Fix 1 - API base and cloud state:
- Use http://106.55.62.122:8011 as the deployed API base unless a local dev override is explicitly configured.
- Do not show "网络未连接，请检查后端服务" when the API is reachable.
- If profile fetch fails because the user is not authenticated, show "请先登录以同步康复档案".
- If a request is loading, keep the previous known screen visible and show a small sync state.

Fix 2 - Home:
- Render home from data.patient_view.home.
- Show:
  - greeting/account state,
  - today rehab summary,
  - one primary action,
  - safety/readiness status in plain Chinese,
  - a clear "问康复师" entry.
- Do not show raw phase.status, action_queue, blockers, forbidden_actions, control_boundary, payload_hint.
- The first screen must feel like: "我今天该做什么？是否安全？哪里可以问人？"

Fix 3 - Rehab therapist Agent:
- Replace the non-working assistant/settings icon with a real "问康复师" entry.
- Required visible label: 问康复师
- Required aria-label: 问康复师
- Minimum touch target: 44px.
- Clicking the top entry or floating entry opens the same chat sheet/page.
- Use data.patient_view.agent for title, entry label, placeholder, quick questions, and safety boundary copy.
- Send messages to:
  POST http://106.55.62.122:8011/api/rehab-arm/app/v1/agent/messages
  Headers: Authorization bearer token, Content-Type application/json
  Body: { "message": "...", "context_snapshot": { "page": currentPage, "source": "rehab-mobile" } }
- Render response.data.answer and response.data.boundary.
- For 400 error code UNSAFE_MOTION_REQUEST, show:
  "为了保护你，我不能绕过设备安全系统或发送直接运动指令。可以帮你调整训练建议或解释报告。"
- Include quick chips:
  - 今天还能训练吗？
  - 手臂酸痛怎么办？
  - 帮我解释报告
  - 生成轻量训练建议

Fix 4 - Device binding:
- Device tab must render from data.patient_view.device.
- Normal user flow must be a binding wizard, not bluetooth-debug.html.
- Wizard steps:
  1. 打开康复设备电源
  2. 手机靠近设备
  3. 选择蓝牙设备或扫码绑定
  4. 等待设备安全系统确认
- Bind endpoint:
  POST http://106.55.62.122:8011/api/rehab-arm/app/v1/devices/bind
- Success copy:
  "设备已绑定，训练前仍会进行安全确认。"
- Keep bluetooth-debug.html accessible only through a developer/debug entry.

Fix 5 - Profile:
- Profile title: 我的康复档案
- Render from data.patient_view.profile and response.data.profile.
- Show signed-in cloud account.
- If profile.phone_verified is true, show masked phone and "手机号已验证".
- If not verified, show "绑定手机号" flow.
- Missing medical constraints must be calm amber "待完善", not red danger.
- Empty copy:
  "还没有填写禁忌备注，训练前请按医生/康复师建议补充。"
- CTA:
  "添加禁忌备注"
- Do not show demo patient, demo ID, fake stage, fake medical warning, or M33/M55 device names as real user data.

Fix 6 - Phone binding:
- Add patient-facing phone verification:
  POST /api/rehab-arm/app/v1/account/phone-verifications
  Body: { "phone": "...", "purpose": "bind_account" }
- Confirm:
  POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm
  Body: { "code": "..." }
- In staging only, if backend returns delivery_channel = debug_sms and debug_code, show it in a small test-helper line.
- Hide debug_code in normal production mode.

Fix 7 - Navigation/accessibility:
- Bottom nav active state must match page: 首页, 训练, 肌电, 设备, 我的.
- No href="#" dead controls.
- Every icon-only button has a correct aria-label.
- No text overlap at 390px mobile width.
- Avoid huge debug cards on first screen.

Acceptance screenshots required after Stitch changes:
1. Home first screen at 390px, no raw terms, no false network error.
2. "问康复师" chat open at 390px.
3. Agent unsafe refusal state at 390px.
4. Device binding wizard at 390px.
5. Profile with cloud account, phone state, and "待完善" medical empty state at 390px.

Release gate:
- Do not call this complete until Codex runs tools/qa_rehab_mobile_acceptance.py and browser QA confirms all P0 frontend gates pass.
- After deployment, rebuild or refresh APK if the APK bundles frontend assets.
```
