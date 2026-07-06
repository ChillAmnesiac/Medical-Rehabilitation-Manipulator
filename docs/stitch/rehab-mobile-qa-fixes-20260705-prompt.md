# Stitch Prompt: Rehab Mobile QA Fixes 2026-07-05

Use this prompt in Google Stitch. Edit only the frontend app:

```text
Repository: https://github.com/wenjunyong666/ai-
Branch: app/rehab-arm-mobile-stitch
App path: apps/web/public/rehab-arm-mobile/

Context:
Codex has QA-tested the cloud deployment at http://106.55.62.122:3001/rehab-arm-mobile/ and backend at http://106.55.62.122:8011.
Do not change backend URLs. The backend is ready for auth, phone binding, profile, workflow, device binding, and rehab therapist Agent APIs.
New backend presentation contract is available:
- GET /api/rehab-arm/app/v1/me returns `data.patient_view`.
- `data.patient_view` has four patient-facing sections: `home`, `profile`, `device`, `agent`.
- Use `data.patient_view` as the primary UI source for normal screens.
- Do not render raw workflow fields such as `phase.status`, `action_queue`, `control_boundary`, or `payload_hint` in patient-facing UI.

Hard rule:
This is a patient-facing rehab app. Do not expose raw engineering or safety-boundary internals on normal user screens.
Hide or translate these terms everywhere outside a developer/debug page:
- M33, M55, SPP, CAN, UUID, preflight, setup_required
- direct_motor_command, can_frame_send, m33_safety_override, motion_permission_granted_by_app
- backend-approved frame, raw frame, transport frame, control_boundary

Global copy replacements:
- M33 / safety authority -> 设备安全系统
- preflight -> 训练前检查
- setup_required -> 完成首次设置
- BLE/SPP -> 蓝牙连接
- backend/cloud -> 云端记录
- AI draft -> 康复师建议
- direct motor/CAN commands -> 底层设备指令

Fix 1: Home first screen
- Show one dominant next action, not a raw workflow dump.
- Prefer `data.patient_view.home.primary_action`, `data.patient_view.home.facts`, and `data.patient_view.home.ask_therapist`.
- If the API says the account needs setup/device binding, primary CTA should be "绑定康复设备" or "完善康复档案".
- Do not render raw `phase.status`, `action_queue`, `blockers`, `forbidden_actions`, `control_boundary`, or `payload_hint`.
- A patient should see:
  - greeting/account state
  - today rehab summary
  - one next action
  - safety state in plain Chinese
  - "问康复师" entry

Fix 2: Rehab therapist Agent
- The current `smart_toy` icon is labelled Settings and click does nothing. Replace it with a visible, accessible button:
  - Label: "问康复师"
  - aria-label: "问康复师"
  - Minimum touch size: 44px
- Use `data.patient_view.agent` for title, entry label, placeholder, quick questions, unsafe copy, and boundary copy.
- Clicking it must open a chat sheet or navigate to the rehab therapist page.
- Chat input placeholder: "今天哪里不舒服？想问什么？"
- Quick chips:
  - "今天还能训练吗？"
  - "手臂酸痛怎么办？"
  - "帮我解释报告"
  - "生成轻量训练建议"
- Send messages to:
  POST /api/rehab-arm/app/v1/agent/messages
  Body: { "message": "...", "context_snapshot": { "page": currentPage, "source": "rehab-mobile" } }
- Render `data.answer`, `data.boundary`, and unsafe errors in patient-friendly cards.
- If the backend returns `400 UNSAFE_MOTION_REQUEST`, show:
  "为了保护你，我不能绕过设备安全系统或发送直接运动指令。可以帮你调整训练建议或解释报告。"

Fix 3: Device binding
- "配对新设备" must not send normal users directly to `bluetooth-debug.html`.
- Use `data.patient_view.device.status`, `readiness_rows`, `binding_steps`, and `primary_action`.
- Create a patient-facing binding wizard:
  1. 打开康复设备电源
  2. 手机靠近设备
  3. 选择蓝牙设备或扫码绑定
  4. 等待设备安全系统确认
- Use:
  POST /api/rehab-arm/app/v1/devices/bind
- Show success as "设备已绑定，训练前仍会进行安全确认".
- Keep `bluetooth-debug.html` accessible only behind a developer/debug entry such as "开发者调试".

Fix 4: Profile
- Profile title should be "我的康复档案".
- Use `data.patient_view.profile` for title, display name, phone state, rehab stage, affected side, and medical constraints.
- Show cloud account and phone verification:
  - If `profile.phone_verified` is true, display masked phone and "手机号已验证".
  - If false, show "绑定手机号" and use the phone verification APIs.
- Missing medical constraints must not be red by default.
  - Empty state: amber "待完善"
  - Copy: "还没有填写禁忌备注，训练前请按医生/康复师建议补充。"
  - CTA: "添加禁忌备注"
- Do not show demo constraints as real medical advice.

Fix 5: Phone binding/onboarding
- Add a user-facing phone verification path:
  POST /api/rehab-arm/app/v1/account/phone-verifications
  Body: { "phone": "...", "purpose": "bind_account" }
  Then:
  POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm
  Body: { "code": "..." }
- In staging, backend may return `debug_code`; show it only in a small "测试验证码" helper when `delivery_channel = debug_sms`.

Fix 6: Navigation and accessibility
- Bottom nav items must have real destinations or reliable route handlers:
  首页, 训练, 设备, 康复师, 我的.
- Do not rely on `href="#"` without route handling.
- Active state must match the current page.
- All icon-only buttons must have correct accessible labels; do not label the Agent as Settings.
- Text must not overflow at 390px width.

Backend endpoints available:
- POST /api/auth/session
- GET /api/rehab-arm/app/v1/public-config
- GET /api/rehab-arm/app/v1/catalog
- GET /api/rehab-arm/app/v1/me
- GET /api/rehab-arm/app/v1/me/workflow
- POST /api/rehab-arm/app/v1/me/workflow/actions
- POST /api/rehab-arm/app/v1/account/phone-verifications
- POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm
- POST /api/rehab-arm/app/v1/devices/bind
- POST /api/rehab-arm/app/v1/agent/messages

Patient-view contract example:
```json
{
  "patient_view": {
    "home": {
      "greeting": "康复用户，今天按步骤来",
      "primary_action": { "label": "绑定康复设备", "route": "device.html" },
      "facts": [],
      "ask_therapist": { "label": "问康复师", "route": "ai-plan.html" }
    },
    "profile": {
      "title": "我的康复档案",
      "phone": { "status_text": "手机号已验证" },
      "medical_constraints": { "status": "待完善" }
    },
    "device": {
      "title": "设备管家",
      "binding_steps": ["打开康复设备电源", "手机靠近设备", "选择蓝牙设备或扫码绑定", "等待设备安全系统确认"]
    },
    "agent": {
      "title": "康复师助手",
      "entry_label": "问康复师",
      "placeholder": "今天哪里不舒服？想问什么？"
    }
  }
}
```

Acceptance checks:
- Home first screen has no raw technical terms.
- "问康复师" opens a working chat and calls the backend Agent endpoint.
- Unsafe Agent requests show protective Chinese copy, not a generic error.
- "配对新设备" starts a patient binding wizard, not the debug page.
- Profile shows cloud account, phone verification, and editable rehab profile state.
- Debug transport details are hidden from normal users.
- 390px mobile screenshot has no overlapping text or unreachable buttons.

Release gate:
- Treat this as failed until all P0 frontend gates in `docs/qa/rehab-mobile-20260705/ACCEPTANCE_CRITERIA.md` pass.
- Run `tools/qa_rehab_mobile_acceptance.py` after deployment; current backend acceptance includes `P0-PATIENT-VIEW-001`.
- After editing, deploy the web app, rebuild/refresh the APK if web assets are bundled, and provide screenshots for:
  1. Home first screen
  2. Ask therapist chat open
  3. Agent unsafe refusal
  4. Device binding wizard
  5. Profile phone/medical empty state
```
