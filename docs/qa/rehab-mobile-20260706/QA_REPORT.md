# Rehab Mobile QA Report - 2026-07-06

## Scope

- Target: `http://106.55.62.122:3001/rehab-arm-mobile/`
- API: `http://106.55.62.122:8011`
- Browser: Codex in-app browser, mobile viewport `390 x 844`
- Flow: home -> rehab therapist entry -> device -> profile
- Destination: local QA folder `docs/qa/rehab-mobile-20260706/`

## Verdict

The backend/API/package smoke is passing, but the complete app is still **not user-ready**.

The current deployed frontend does not consume the backend `data.patient_view` contract as the primary patient-facing model. A normal user still sees raw workflow state, device/debug vocabulary, a false network warning, non-working Agent entry points, and demo profile/medical content.

## Accepted Screenshots

1. `01-home-390-current.png` - Home first screen at 390px.
2. `02-agent-top-click-390.png` - Top Agent-like icon after click.
3. `03-agent-floating-click-390.png` - Floating Agent-like button after click.
4. `04-device-nav-390.png` - Device tab after navigation.
5. `05-profile-nav-390.png` - Profile tab after navigation.
6. `06-profile-resmoke-390.png` - Profile resmoke after git-managed backend QA commits.
7. `07-home-resmoke-390.png` - Home resmoke after git-managed backend QA commits.

All screenshots were opened and inspected before being used as evidence. They show the deployed cloud app, not a blank page or wrong window.

## Step Review

| Step | What Was Checked | Health | Evidence |
| --- | --- | --- | --- |
| 1 | Home first screen after loading deployed cloud app | FAIL | `01-home-390-current.png` |
| 2 | Top icon that looks like Agent/assistant entry | FAIL | `02-agent-top-click-390.png` |
| 3 | Floating assistant button at lower right | FAIL | `03-agent-floating-click-390.png` |
| 4 | Device tab from bottom navigation | FAIL | `04-device-nav-390.png` |
| 5 | Profile tab from bottom navigation | FAIL | `05-profile-nav-390.png` |
| 6 | Profile resmoke on current production frontend | FAIL | `06-profile-resmoke-390.png` |
| 7 | Home resmoke on current production frontend | FAIL | `07-home-resmoke-390.png` |

## 2026-07-06 L1 Resmoke

After committing backend/QA contract work, the deployed frontend was resmoked in the in-app browser at `390 x 844`.

Profile hit list:

- `M33`
- `避免过度伸展`
- `setup_required`
- `early_active`
- `网络未连接`

Home hit list:

- `网络未连接`
- `setup_required`
- `M33`
- `M55`
- `early_active`
- `left`
- `动作队列`
- `禁止`

Result: L1 remains `FAIL`. The backend contract is ready, but the frontend still needs Stitch changes.

## 2026-07-06 L1 Static Frontend Gate

Added a repeatable frontend gate:

```powershell
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_frontend.py
```

Current production result:

- Overall: `FAIL`
- Failed: `4`
- Total: `4`

Failed gates:

- `L1-HOME-STATIC-001`: missing `问康复师`; still contains `M33`, `M55`, and `RoboRehab Controller`.
- `L1-PROFILE-STATIC-001`: missing `我的康复档案` and `手机号`; still contains `M33`, `M55`, `患者 A`, `ID: 8829`, `避免过度伸展`, and `RoboRehab Controller`.
- `L1-DEVICE-STATIC-001`: still contains `M33`, `M55`, `UUID`, and `Gatekeeper`.
- `L1-AGENT-STATIC-001`: missing `问康复师`.

This gate is intentionally strict and should remain failing until Stitch converts normal user pages to the `patient_view` contract.

## 2026-07-06 L1 Combined Release Gate

Added a single release gate that runs backend/API/APK smoke and frontend L1 checks together:

```powershell
$env:REHAB_QA_EMAIL='<staging email>'
$env:REHAB_QA_PASSWORD='<staging password>'
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_release.py
```

Current production result:

- Overall: `FAIL`
- API overall: `PASS`
- API P0 failed: `0`
- Frontend overall: `FAIL`
- Frontend failed: `4`
- Blocking gates: `frontend_l1_gate`

This is now the L1 release decision command. A cloud deployment or APK refresh is not accepted as user-ready unless this command returns exit code `0` with `overall = PASS`.

## Findings

### P0-Home-001 - False Network Error

Evidence: `01-home-390-current.png`

The first visible status says `网络未连接，请检查后端服务`, but the API acceptance smoke passes against `http://106.55.62.122:8011`. This makes a healthy cloud deployment look broken to the patient.

Expected:

- The frontend uses the same deployed API base as the smoke test: `http://106.55.62.122:8011`.
- If an authenticated API request fails, show a specific recoverable state such as "请重新登录" or "正在同步云端资料".
- Do not show "network disconnected" while rendering live cloud data or static fallbacks.

### P0-Home-002 - Engineering Workflow Is Exposed To Patients

Evidence: `01-home-390-current.png`, `04-device-nav-390.png`

Visible patient-facing screens still expose raw or semi-raw terms:

- `setup_required`
- `M33`
- `M33 BLE`
- `M55 EMG`
- `early_active`
- `left`
- `动作队列`
- `阻塞`
- `禁止`
- `App 只显示流程证据；真实运动许可仍由 M33 最终裁决`

Expected:

- Normal screens render `GET /api/rehab-arm/app/v1/me -> data.patient_view`.
- Raw workflow, hardware, and debug vocabulary stays behind a developer-only page.
- The first screen gives one clear next action, not an internal workflow dump.

### P0-Agent-001 - Rehab Therapist Entry Is Not Usable

Evidence: `02-agent-top-click-390.png`, `03-agent-floating-click-390.png`

The top icon is visually present but is labelled like a settings/tool button. Clicking it did not open a chat, drawer, route, or modal. The floating button received focus/click styling, but it also did not open the therapist chat.

Expected:

- A visible button labelled `问康复师`.
- `aria-label="问康复师"` and minimum 44px touch target.
- Click opens a chat sheet/page.
- Safe messages call `POST /api/rehab-arm/app/v1/agent/messages`.
- Unsafe direct-control requests show the backend protective refusal copy.

### P0-Device-001 - Device Tab Is Still A Developer Surface

Evidence: `04-device-nav-390.png`

The device page still orients around system architecture and device internals instead of a simple binding wizard. It also repeats the home workflow/debug block above the device content.

Expected:

- Device tab starts from `data.patient_view.device`.
- Primary flow is a patient-facing binding wizard:
  1. turn on rehab device,
  2. keep phone close,
  3. select Bluetooth device or scan code,
  4. wait for device safety confirmation.
- `bluetooth-debug.html` remains available only through a developer/debug entry.

### P0-Profile-001 - Profile Shows Demo Identity And Fake Medical Advice

Evidence: `05-profile-nav-390.png`

The profile page shows `患者 A`, `ID: 8829`, `第二阶段康复中`, and a red medical warning `避免过度伸展 > 120°`. It also lists `M33` and `M55` devices. This is unsafe because incomplete clinical data appears as real medical advice.

Expected:

- Profile uses `data.patient_view.profile`.
- Display the signed-in cloud account and phone verification state.
- Missing medical constraints use a calm `待完善` state.
- Do not show demo constraints as real advice.

## Backend/API Evidence

Latest API/package acceptance smoke passed:

- Overall: `PASS`
- P0 failed: `0`
- Total checks: `14`
- Cloud PID: `798697`
- Build ref: `app/rehab-arm-mobile-stitch`
- Build SHA: `b735d73`
- Build time: `2026-07-05T16:32:07Z`
- `P0-PATIENT-VIEW-001`: `PASS`
- Agent safe answer: `PASS`
- Agent unsafe refusal: `PASS`
- CORS from deployed web origin: `PASS`
- APK HEAD: `PASS`, size over 1 MB

The remaining blocker is frontend rendering and interaction.

## Backend Source-Parity Follow-Up

2026-07-06 continuation work closed a backend source-parity gap:

- Local source now includes `data.patient_view` in `cloud/rehab-platform/app/api/routes/rehab_app.py`.
- Added regression coverage in `cloud/rehab-platform/tests/test_app_compat.py`.
- Expanded `tools/qa_rehab_mobile_acceptance.py` so `P0-PATIENT-VIEW-001` checks:
  - `home/profile/device/agent` sections,
  - Agent entry label `问康复师`,
  - Agent endpoint `/api/rehab-arm/app/v1/agent/messages`,
  - device binding first step `打开康复设备电源`,
  - profile phone label `手机号`,
  - no raw technical terms.

Fresh verification:

- Red test first: missing local `patient_view` failed with `KeyError: 'patient_view'`.
- Local focused test after implementation: `1 passed, 1 warning`.
- Local backend suite: `22 passed, 1 warning`.
- Syntax checks: `py_compile` passed for backend route and QA script.
- Stricter cloud smoke: `overall = PASS`, `p0_failed = 0`, `total = 14`.

Cloud runtime already had the deployed patient-view contract, so no extra cloud code patch or restart was needed for this follow-up. Latest verified cloud PID is `798697`, build SHA `b735d73`.

## Accessibility Risks

- Agent-like icon buttons do not communicate their purpose clearly to screen-reader or touch users.
- Multiple bottom-nav labels are visible, but the current screen also shows repeated debug content above the active section, weakening reading order.
- Long debug strings and mixed language terms reduce readability at 390px.
- Screenshot-only audit cannot prove keyboard focus order, screen-reader output, or color contrast compliance. Those need DOM/assistive checks after Stitch fixes.

## Acceptance Target For The Next Stitch Build

The next deployed frontend must pass these browser checks at `390 x 844`:

1. Home shows no raw technical terms and has one dominant next action.
2. Home no longer shows false `网络未连接` when API health/auth/profile are reachable.
3. `问康复师` opens a working chat and calls the Agent endpoint.
4. Unsafe Agent requests show a protective Chinese refusal, not a generic error.
5. Device tab opens a patient binding wizard, not a debug page.
6. Profile shows cloud account, phone verification state, and safe `待完善` medical empty state.
7. Debug transport details are hidden from normal users.
8. No text overlap or unreachable primary controls at 390px.

## Current Product Decision

Do not call this build user-ready. Backend is ready for Stitch to consume, but the rendered app still fails the patient-facing P0 gates.

Stitch execution runbook:

- `docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md`
