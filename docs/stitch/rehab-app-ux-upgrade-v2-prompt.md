# Stitch Prompt: Rehab Mobile UX Upgrade V2

Use this prompt with Google Stitch for the real app:

```text
You are editing the existing rehab mobile app in:

Repository: https://github.com/wenjunyong666/ai-
Branch: app/rehab-arm-mobile-stitch
App path: apps/web/public/rehab-arm-mobile/
Main bridge: apps/web/public/rehab-arm-mobile/mobile-bridge.js

Important boundary:
- Preserve the existing safety model: App, cloud, and AI provide status, guidance, and training-plan drafts only.
- Do not add direct motor-control UX for normal users.
- Do not expose raw CAN, torque, current, M33 command frames, or SPP internals outside a clearly hidden debug page.
- M33 remains final motion authority.

Goal:
Transform the current app from an engineering controller into a polished patient-facing rehab companion. The user should feel: "I know what to do next, the device is safe, and I can ask a rehab therapist anytime."

Keep:
- The existing static PWA structure.
- Existing page files if possible: home.html, device.html, training-library.html, ai-plan.html, training-session.html, emg.html, report.html, profile.html, bluetooth-debug.html.
- Existing mobile-bridge.js backend integration points, but improve labels, layout, onboarding, and empty states.
- Existing localStorage keys and API base behavior unless a backend contract change is explicitly listed below.

Design principles:
- Mobile-first, 390px wide baseline.
- Quiet clinical product, not a sci-fi dashboard.
- 8px max radius for cards and controls.
- Use clear icons with text labels for primary actions.
- Avoid decorative gradients, orbs, and marketing hero layouts.
- Use calm color contrast: blue for primary, green for ready/safe, amber for attention, red only for true stop/unsafe.
- Every screen must answer "What should I do next?"
- Hide technical words from patient-facing screens: M33, SPP, Gatekeeper, backend, sync-to-device, AI draft, preflight.
- Replace them with user language:
  - M33 -> 设备安全系统
  - Gatekeeper -> 安全审核
  - SPP/BLE -> 蓝牙连接
  - backend/cloud -> 云端记录
  - AI draft -> 康复师建议
  - preflight -> 训练前检查

App information architecture:
Bottom nav should have five tabs:
1. 首页
2. 训练
3. 设备
4. 康复师
5. 我的

Home screen:
- Top: friendly greeting and account/device state.
- Primary card: "今日康复" with one clear next action:
  - 未登录: "登录并建立康复档案"
  - 已登录未绑定: "绑定康复设备"
  - 已绑定无计划: "生成今日训练建议"
  - 有计划未审核: "完成训练前检查"
  - 可训练: "开始训练"
- Show only three key facts: today's plan duration, safety state, last training result.
- Add a persistent "问康复师" quick button.
- Do not show a floating login form covering content.

Login/onboarding:
- Replace the bottom floating login panel with a full-screen or modal onboarding flow:
  1. 手机号登录
  2. 验证码
  3. 康复档案: 姓名/患侧/康复阶段/禁忌备注
  4. 绑定设备
- If the backend still only supports /api/auth/session, keep a small developer fallback, but the primary UI must be phone-code login.
- Use plain copy: "用于同步训练记录和康复师建议。"

Device screen:
- Rename to "设备管家".
- First card: device readiness with three rows:
  - 云端账号
  - 蓝牙设备
  - 安全审核
- If unbound, show a three-step binding guide:
  1. 打开设备电源
  2. 手机靠近设备
  3. 扫码或选择蓝牙设备
- Move system architecture diagram below the binding guide and make it collapsible as "了解安全链路".
- Keep bluetooth-debug.html as a developer/debug page, not the normal device page.

Rehab therapist / AI screen:
- Rename ai-plan.html experience to "康复师".
- Make it chat-first:
  - Message input: "今天哪里不舒服？想问什么？"
  - Quick chips: "今天能练吗", "手臂酸痛怎么办", "解释这次报告", "生成轻量训练"
  - Assistant response card with safety disclaimer.
- Training-plan suggestions should appear as a clear card:
  - Goal
  - Sets/reps
  - Assist level
  - Why this is suggested
  - Safety notes
  - Button: "保存为今日计划"
- Never imply the AI can directly start hardware movement.

Training library:
- Split into:
  - 今日计划
  - 可选动作
  - 康复师建议
- Each movement card should show: body part, duration, difficulty, contraindication note.
- Main CTA should be "选择为今日计划" or "查看详情", not "sync".

Training session:
- Start with a checklist:
  - 设备已绑定
  - 安全审核通过
  - 疼痛评分已确认
  - 训练计划已保存
- If blocked, present it as protection: "现在先不开始训练，是为了保护你。"
- During session, show:
  - current set/repetition
  - pain quick selector 0-10
  - fatigue selector
  - large "暂停记录" and "停止训练" buttons
- "停止训练" should record stop request and show guidance; do not imply app can release or override hardware stop.

Report:
- Make the first screen a simple summary:
  - 完成了什么
  - 有什么变化
  - 下次建议
- Add "问康复师解读这份报告" button.
- Show EMG/heart/spO2 details below fold.

Profile:
- Rename to "我的康复档案".
- Show completion meter with friendly tasks:
  - 完善康复阶段
  - 添加禁忌备注
  - 绑定康复设备
  - 添加家属/康复师联系方式
- Do not show red medical warning for missing info. Use amber "待完善".

Backend API compatibility:
The app should continue to consume these paths:
- POST /api/auth/session
- GET /api/rehab-arm/app/v1/public-config
- GET /api/rehab-arm/app/v1/catalog
- GET /api/rehab-arm/app/v1/me
- GET /api/rehab-arm/app/v1/me/workflow
- POST /api/rehab-arm/app/v1/me/workflow/actions
- GET /api/rehab-arm/app/v1/emg/latest
- POST /api/rehab-arm/app/v1/devices/bind
- POST /api/rehab-arm/app/v1/ai-training-drafts/generate
- POST /api/rehab-arm/app/v1/ai-training-drafts/{draft_id}/accept
- POST /api/rehab-arm/app/v1/training-plans/{plan_id}/sync-to-device
- POST /api/rehab-arm/app/v1/devices/{device_id}/ble/messages

New deployed API endpoints to use:
- POST /api/rehab-arm/app/v1/account/phone-verifications with { phone, purpose: "bind_account" }
- POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm with { code }
- POST /api/rehab-arm/app/v1/agent/messages with { message, context_snapshot }
- PATCH /api/rehab-arm/app/v1/me/profile

Acceptance criteria:
- No first-screen floating login panel covering content.
- Home has exactly one dominant next action.
- Device binding is understandable without knowing M33/SPP/CAN.
- AI page feels like a rehab therapist chat, not a terminal.
- Blocked training state feels protective, not broken.
- Report is readable by a non-technical patient in 10 seconds.
- Debug transport details are only in bluetooth-debug.html or behind a developer entry.
- Text does not overflow at 390px width.
- Buttons have stable 44px+ touch targets.
- All primary actions have visible labels.
- The app still works offline enough to show last known state and clear "waiting for cloud" status.
```
