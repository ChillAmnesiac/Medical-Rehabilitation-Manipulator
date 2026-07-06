# Rehab Mobile Acceptance Criteria - 2026-07-05

## Result Scale

- `PASS`: verified with a fresh command, browser screenshot, or device/package check.
- `FAIL`: a P0/P1 requirement is broken or not implemented.
- `WARN`: not blocking this stage, but must be resolved before broader release.
- `NOT CHECKED`: no current evidence; cannot be treated as pass.

## Release Rule

- User-ready staging requires every `P0` item to be `PASS`.
- Experience-ready beta requires every `P0` item and at least 90% of `P1` items to be `PASS`.
- A build is not called complete unless the latest QA report includes command output and browser screenshots for the changed surface.
- After every large backend task: deploy to `106.55.62.122:8011`, run API acceptance, then verify the APK URL.
- After every Stitch/frontend task: deploy web assets, run browser QA at 390px mobile width, then rebuild or verify the APK package.

## P0 Gates

| Gate | Standard | Current Result |
| --- | --- | --- |
| Cloud health | `GET /health` returns `200`, `data.status = ok`, and the expected PID is active. | PASS |
| Auth | Test account can login and receives bearer token. | PASS |
| Phone binding | Signed-in profile has `phone_verified = true` or a working phone-code binding flow. | PASS for staging account |
| Profile bootstrap | `/api/rehab-arm/app/v1/me` returns profile, readiness, timeline, and guides without server error. | PASS |
| Patient view contract | `/api/rehab-arm/app/v1/me` returns `data.patient_view.home/profile/device/agent` with no raw technical strings. | PASS |
| Agent safe answer | `/agent/messages` answers a normal rehab question in patient-facing Chinese. | PASS |
| Agent unsafe refusal | Direct-control/safety-bypass requests return `400 UNSAFE_MOTION_REQUEST`. | PASS |
| CORS | Deployed web origin can call auth, profile, phone binding, and Agent endpoints. | PASS for Agent endpoint |
| APK delivery | APK URL returns `200`, APK content type, and content length over 1 MB. | PASS |
| Home first screen | One dominant next action; no raw workflow/debug fields on first screen. | FAIL |
| Navigation | Bottom nav routes to real pages and active state matches current page. | PARTIAL / needs browser retest |
| Ask therapist | Visible `问康复师` entry opens a working chat and calls Agent API. | FAIL |
| Device binding | Normal user enters a patient binding wizard, not `bluetooth-debug.html`. | FAIL |
| Profile medical safety | Missing medical constraints use calm "待完善" state; no fake medical warning as real advice. | FAIL |
| Mobile layout | 390px screenshots show no text overlap, unreachable controls, or hidden primary CTA. | NOT CHECKED after Stitch fix |

## P1 Gates

| Gate | Standard | Current Result |
| --- | --- | --- |
| Phone-code UX | User can request code, confirm code, see verified/masked phone, and recover from invalid code. | Backend PASS, frontend NOT CHECKED |
| Agent chat UX | Chat has input, quick chips, loading state, answer card, unsafe refusal copy, and retry state. | Frontend FAIL |
| Device empty state | Unbound device state explains steps in plain language and does not expose UUID/SPP/CAN. | Frontend FAIL |
| Training start guard | Training cannot start until account, device, plan, pain score, and safety check are ready. | NOT CHECKED |
| Report readability | First screen answers "completed what, changed what, next suggestion" in 10 seconds. | NOT CHECKED |
| Accessibility | Primary controls have 44px touch targets and correct accessible labels. | FAIL for Agent icon |
| Offline/error state | Last known state remains visible with clear "waiting for cloud" status. | NOT CHECKED |

## P2 Gates

| Gate | Standard | Current Result |
| --- | --- | --- |
| Care collaboration | Family/therapist invite flow is discoverable and permissioned. | NOT CHECKED |
| Developer mode | Debug transport pages are accessible only behind a developer entry. | FAIL |
| Analytics | Key actions can be logged without collecting sensitive medical free text. | NOT CHECKED |
| Packaging metadata | APK version, SHA256, and build time are documented after each rebuild. | PARTIAL |

## Current Verdict

The backend/API side is passing the current P0 smoke gates. The complete app is not user-ready because frontend P0 gates still fail: first-screen copy, Agent entry, device binding, and profile medical empty state.

## Latest Rendered QA - 2026-07-06

Browser QA was repeated against the deployed cloud app at `390 x 844`.

- Evidence folder: `docs/qa/rehab-mobile-20260706/`
- Report: `docs/qa/rehab-mobile-20260706/QA_REPORT.md`
- Stitch handoff prompt: `docs/stitch/rehab-mobile-stitch-execution-20260706.md`

Rendered app result remains `FAIL` for user-ready staging:

- Home still shows a false `网络未连接，请检查后端服务` state.
- Home still exposes raw workflow/debug terms such as `setup_required`, `early_active`, `left`, and `M33`.
- Agent entry buttons do not open a working rehab therapist chat.
- Device tab is still debug/engineering oriented instead of a patient binding wizard.
- Profile still shows demo identity and fake medical warning instead of `patient_view.profile`.

Latest automated command:

```powershell
$env:REHAB_QA_EMAIL='<staging email>'
$env:REHAB_QA_PASSWORD='<staging password>'
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_acceptance.py
```

Latest automated result:

- Overall API/package smoke: `PASS`
- P0 failed in automation: `0`
- Total automated checks: `14`
- Browser/manual interaction gate: `WARN`, because frontend fixes still require rendered screenshot QA.

Latest patient-view smoke:

- `P0-PATIENT-VIEW-001`: `PASS`
- Sections: `agent`, `device`, `home`, `profile`
- Agent endpoint: `/api/rehab-arm/app/v1/agent/messages`
- Agent entry label: `问康复师`
- Device first binding step: `打开康复设备电源`
- Profile phone label: `手机号`
- Technical term hits: `[]`

Next acceptance target for Stitch:

1. Home first screen has no raw technical strings and shows one next action.
2. `问康复师` opens a working chat and passes safe/unsafe Agent tests.
3. `配对新设备` opens a patient binding wizard.
4. Profile shows verified phone and safe "待完善" medical constraint state.
5. New screenshots at 390px prove the four fixes.
