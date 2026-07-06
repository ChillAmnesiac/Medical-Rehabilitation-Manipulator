# Stitch Prompt: Account Phone Binding Flow

Use this prompt in Google Stitch for the real app branch:

- Repository: `https://github.com/wenjunyong666/ai-`
- Branch: `app/rehab-arm-mobile-stitch`
- App path: `apps/web/public/rehab-arm-mobile/`

Important boundary:

- Do not edit backend code from Stitch.
- Keep the existing app safety model: cloud and AI provide account state, education, training-plan drafts, and evidence transport only.
- Do not add any direct motor-control UI.

## Goal

Add a polished account phone binding flow to the rehab mobile app. This should feel like a normal consumer health app account setup, not a debug form.

The first-time user journey should be:

1. Sign in with the existing account/password flow if no token exists.
2. Fetch `GET /api/rehab-arm/app/v1/me`.
3. If `data.profile.phone_verified !== true`, show a friendly phone binding step before device binding/training actions.
4. Request a verification code from the server.
5. Let the user enter the code.
6. Confirm the code.
7. Refetch `/me` and continue onboarding.

## API Base

Default backend API base:

`http://106.55.62.122:8011`

Keep the existing `rehabArmMobileApiBase` localStorage override.

## Deployed Backend Contract

Start verification:

```http
POST /api/rehab-arm/app/v1/account/phone-verifications
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "phone": "+8613800000000",
  "purpose": "bind_account"
}
```

Response:

```json
{
  "data": {
    "verification_id": "...",
    "masked_phone": "+861****0000",
    "purpose": "bind_account",
    "expires_in": 300,
    "delivery_channel": "debug_sms",
    "sms_status": "simulated_until_sms_provider_configured",
    "debug_code": "123456"
  }
}
```

Confirm verification:

```http
POST /api/rehab-arm/app/v1/account/phone-verifications/{verification_id}/confirm
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "code": "123456"
}
```

Response includes:

```json
{
  "data": {
    "profile": {
      "phone": "+8613800000000",
      "phone_verified": true,
      "phone_verified_at": "..."
    },
    "verification": {
      "status": "confirmed"
    }
  }
}
```

Bootstrap/profile now include:

- `data.profile.phone`
- `data.profile.phone_verified`
- `data.profile.phone_verified_at`
- `data.onboarding_guide.steps[0].code === "PHONE_ACCOUNT_BINDING_REQUIRED"`

## UX Requirements

- On the profile/account screen, show a clear account trust row:
  - 未绑定手机号: amber, CTA `绑定手机号`
  - 已验证: green, show masked phone
- During onboarding, phone binding should come before device binding.
- Use copy like:
  - Title: `绑定手机号`
  - Helper: `用于同步训练记录、找回账号和接收康复师建议。`
  - Button: `发送验证码`
  - Code screen title: `输入验证码`
  - Success: `手机号已验证`
- In staging, if the response includes `debug_code`, show a small developer-only hint area: `测试验证码：{debug_code}`. Hide this area behind subtle text; do not make it the primary UI.
- On error `PHONE_CODE_INVALID`, show: `验证码不正确或已过期，请重新输入。`
- On error `PHONE_INVALID`, show: `请输入有效手机号。`
- The flow must not block viewing existing read-only records, but it should block device binding, plan sync, and training start CTAs until verified.
- No full-screen red warnings for missing phone. Use calm amber "待完成" language.

## Acceptance Criteria

- User can complete phone binding using the deployed backend endpoints.
- After confirmation, `/me` is refetched and the UI changes to verified state without a manual refresh.
- Existing email/password login still works.
- Existing device, AI therapist, training, report, and Bluetooth debug flows are not broken.
- No technical words like `debug_sms`, `verification_id`, or raw endpoint names appear in normal patient UI.
- Text fits at 390px width and primary touch targets are at least 44px high.
