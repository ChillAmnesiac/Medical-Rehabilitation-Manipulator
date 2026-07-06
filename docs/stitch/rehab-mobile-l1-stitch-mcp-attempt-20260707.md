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
