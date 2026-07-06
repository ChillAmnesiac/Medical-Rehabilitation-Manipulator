# Rehab Mobile L1 Stitch MCP Attempt - 2026-07-07

## Result

Status: `NOT ACCEPTED`.

Codex successfully reached the Google Stitch MCP HTTP endpoint and created a
dedicated Stitch project, but the generated mobile screens did not satisfy the
existing L1 frontend text gates. No generated Stitch HTML was copied into the
frontend source or Android WebView mirror.

## Stitch Project

- Project: `projects/1542023501541093471`
- Title: `Rehab Mobile L1 Closure`
- Purpose: Generate patient-facing mobile screens for the rehab arm App without
  Codex directly editing frontend files.

## Generated Screens

Latest strict screen candidates:

| Page | Screen ID | Title | Accepted |
| --- | --- | --- | --- |
| `home.html` | `95ba17bb7c9e4434b8369b6464ed82a6` | `首页 - 领动康复手臂` | No |
| `profile.html` | `b2f455802fa447068e91f0be2242f3e4` | `个人中心 - 领动康复手臂` | No |
| `device.html` | `5055d3ee85ca49b3bc6119a92378259a` | `设备连接 - 领动康复手臂` | No |
| `ai-plan.html` | `c6a0aab827f64175beb450a33d065892` | `康复助手 - 领动康复手臂 (更新版)` | No |

Downloaded local artifacts, not committed:

- `artifacts/stitch/rehab-mobile-stitch-l1-home.html`
- `artifacts/stitch/rehab-mobile-stitch-l1-profile.html`
- `artifacts/stitch/rehab-mobile-stitch-l1-device.html`
- `artifacts/stitch/rehab-mobile-stitch-l1-agent.html`

## QA Findings

Automated text QA on downloaded Stitch HTML:

| Page | Missing Required Text | Forbidden Debug Text |
| --- | --- | --- |
| `home.html` | `查看康复师建议`, `问康复师` | None |
| `profile.html` | `我的康复档案`, `绑定手机号`, `验证码` | None |
| `device.html` | `绑定设备`, `打开康复设备电源` | None |
| `ai-plan.html` | `问康复师` | None |

The screens are directionally patient-facing and clean of raw engineering terms,
but they cannot be accepted because current L1 gates require exact visible copy.

## 2026-07-07 Home Literal Copy Iteration

Codex ran one narrower Stitch MCP iteration focused only on `home.html`.

Artifacts, not committed as frontend source:

- `artifacts/stitch/l1-mcp-iteration-20260707/home-flash.html`
- `artifacts/stitch/l1-mcp-iteration-20260707/home-flash-edit-literal.html`
- `artifacts/stitch/l1-mcp-iteration-20260707/home-flash.jpg`
- `artifacts/stitch/l1-mcp-iteration-20260707/home-flash-edit-literal.jpg`

Generated screens:

| Page | Screen ID | Title | Accepted |
| --- | --- | --- | --- |
| `home.html` | `fd3aae8953714a058cd8b54a9217a223` | `首页 - 领动康复手臂` | No |
| `home.html` | `bdcea50a83a74eb68075807aaf7120dc` | `首页 - 领动康复手臂 (QA 修正版)` | No |

Result:

- Stitch removed raw engineering terms from the home candidate.
- Stitch kept basic source references for `/api/auth/session`,
  `/api/rehab-arm/app/v1/me`, `patient_view`, `Authorization`, and `Bearer`.
- Stitch still rewrote the exact release-gated visible copy:
  - Expected: `查看康复师建议`, `问康复师`.
  - Actual: `开始康复训练`, `咨询治疗师`.
- No generated HTML was copied into `apps/web/public/rehab-arm-mobile/` or
  `apps/mobile/rehab-arm-android/www/`.

Follow-up hardening:

- `tools/qa_rehab_mobile_l1_frontend.py` now requires both
  `查看康复师建议` and `问康复师` on `home.html`.
- `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` now includes
  an `Exact Release-Gated Visible Copy` section so Stitch cannot treat these as
  optional UX labels.

## 2026-07-07 Home HTML Entity Copy Iteration

Codex ran a second narrow Stitch MCP iteration for `home.html`, this time
asking Stitch to copy HTML numeric character references for the exact release
copy.

Artifacts, not committed as frontend source:

- `artifacts/stitch/l1-entity-iteration-20260707/home-entity.html`
- `artifacts/stitch/l1-entity-iteration-20260707/home-entity.jpg`
- `artifacts/stitch/l1-entity-iteration-20260707/home-entity-generate-response.json`

Generated screen:

| Page | Screen ID | Title | Accepted |
| --- | --- | --- | --- |
| `home.html` | `8d43c827e5464979a08926467114eda3` | `首页 - 领动康复手臂 (QA 实验版)` | No |

Result:

- The generated visible text decoded to `查看康复师建议` and `问康复师`.
- The generated home candidate passed `L1-HOME-STATIC-001` when checked through
  `tools/qa_rehab_mobile_l1_frontend.py` page-gate logic.
- The candidate did not hit raw forbidden terms in the home HTML.
- The candidate is still not accepted as frontend source because it is only one
  page, includes demo wording such as `李先生`, and has not passed the full
  four-page integration gate.
- No generated HTML was copied into `apps/web/public/rehab-arm-mobile/` or
  `apps/mobile/rehab-arm-android/www/`.

Follow-up hardening:

- `docs/stitch/rehab-mobile-l1-stitch-execution-v4-20260706.md` now includes
  HTML entity fallback snippets for exact release-gated copy.
- `tools/qa_rehab_mobile_l1_frontend.py` now accepts HTML-decoded source when
  checking integration requirements, so an accessible label written as numeric
  HTML entities can still satisfy the `问康复师` accessibility contract.

## 2026-07-07 Four-Page Entity Candidate

Codex generated a four-page Stitch candidate using the HTML entity strategy and
downloaded it to:

- `artifacts/stitch/l1-full-entity-candidate-20260707/home.html`
- `artifacts/stitch/l1-full-entity-candidate-20260707/profile.html`
- `artifacts/stitch/l1-full-entity-candidate-20260707/device.html`
- `artifacts/stitch/l1-full-entity-candidate-20260707/ai-plan.html`
- `artifacts/stitch/l1-full-entity-candidate-20260707/frontend-l1-source-gate.json`

Generated screens:

| Page | Screen ID | Title | Source Gate |
| --- | --- | --- | --- |
| `home.html` | `4fd2a7955ae04e528e6fa5aacc18a895` | `首页 - 领动康复手臂 (QA 实验版)` | PASS |
| `profile.html` | `f1d1fcbf9cc844b6aee6ffa1a2584b6f` | `个人中心 - 领动康复手臂 (L1 规范版)` | PASS |
| `device.html` | `2ec9f9b9acb545668b8d06f4b609da0a` | `设备绑定 - 领动康复手臂 (QA 实验版)` | PASS |
| `ai-plan.html` | `648dfa3b393b4a0ea1d3227b3686cc82` | `问康复师 - 领动康复手臂` | PASS |

Source-dir gate:

```powershell
$env:PYTHONIOENCODING='utf-8'
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_frontend.py --source-dir artifacts\stitch\l1-full-entity-candidate-20260707 --output artifacts\stitch\l1-full-entity-candidate-20260707\frontend-l1-source-gate.json
```

Result: `overall = PASS`, `failed = 0`, `total = 5`.

Notes:

- This is the first Stitch-generated four-page candidate to pass the local L1
  source gate.
- It is not accepted as the deployed frontend because the files are still only
  Stitch artifacts, not changes applied to the real frontend branch.
- It has not been mirrored into `apps/mobile/rehab-arm-android/www/`.
- It has not been deployed to cloud, packaged into an APK, or verified by final
  browser QA screenshots.
- The home candidate still includes demo-like wording such as `李先生`, so the
  next Stitch pass should replace any personal demo names with neutral text
  before deployment.

## Next Stitch Prompt Delta

The next Stitch iteration should be even more constrained:

```text
Do not rename these exact Chinese strings. They are automated release gates and
must appear verbatim in visible HTML:

home.html: 查看康复师建议, 问康复师
profile.html: 我的康复档案, 手机号, 绑定手机号, 验证码
device.html: 绑定设备, 打开康复设备电源
ai-plan.html: 问康复师

Do not substitute 康复助手, 咨询治疗师, 开始康复训练, 个人中心, or 设备连接
for these required strings.
```

After Stitch produces passing HTML, Codex should run:

```powershell
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_frontend.py --source-dir apps/web/public/rehab-arm-mobile --output artifacts/rehab-mobile-frontend-release/frontend-l1-preflight.json
robocopy apps\web\public\rehab-arm-mobile apps\mobile\rehab-arm-android\www /MIR
if ($LASTEXITCODE -le 7) { $global:LASTEXITCODE = 0 }
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\verify_rehab_mobile_webview_mirror.py --web-dir apps/web/public/rehab-arm-mobile --android-www-dir apps/mobile/rehab-arm-android/www --output artifacts/rehab-mobile-frontend-release/webview-mirror-verification.json
```
