# Rehab Mobile Phone And Device Runtime Binding - 2026-07-08

## Root Cause Evidence

- `profile.html` renders phone and code inputs, but the buttons have no real event handlers.
- `device.html` uses `transitionToStep2()` and `showBoundError()` to simulate search and conflict. It hardcodes `领动康复手臂 v2`.
- The packaged APK contains `assets/native-bridge.js`, but it is the standard Capacitor bridge only. `assets/capacitor.plugins.json` is `[]`, and the APK asset scan found no Bluetooth/SPP/RFCOMM/plugin symbols.
- Backend phone binding is functional: `POST /account/phone-verifications` plus confirm writes `profile.phone_verified=true`.
- Backend device binding is functional for a provided device identity: `POST /devices/bind` is idempotent for the same owner and rejects cross-account claims with `DEVICE_ALREADY_BOUND`.

## Current Non-Stitch Backend Contract

`GET /api/rehab-arm/app/v1/public-config` now exposes:

```json
{
  "device_binding": {
    "bind_endpoint": "/api/rehab-arm/app/v1/devices/bind",
    "native_bluetooth_bridge": {
      "status": "missing_in_current_apk",
      "required_for_real_pairing": true,
      "expected_bridge_names": [
        "window.RehabArmBluetoothBridge",
        "window.Capacitor.Plugins.RehabArmBluetooth"
      ],
      "required_methods": [
        "requestBluetoothPermissions",
        "scanDevices",
        "connect"
      ]
    },
    "web_fallback": "show_unavailable_state_do_not_fake_devices"
  }
}
```

## Stitch Prompt

Project: `1542023501541093471`

Screens:

- Profile: `4021fd1365914e219be2b7d85a9ec0c9`
- Device: `f41281ccb6d349ee8389f72d753faeb7`

Prompt used on 2026-07-08:

```text
请编辑这两个 390x844 移动端页面：Profile 个人中心 和 Device 绑定设备。目标不是静态视觉稿，而是可导出的、患者可用的单页 HTML。必须保留“领动康复手臂”品牌、柔和医疗 teal/sage 风格、底部导航：首页/训练/社区/消息/我的，所有中文必须横向显示，按钮触控高度 >=48px，不要出现 M33/M55/CAN/SPP/UUID/debug/mock/In real app 等工程或调试词。

全局运行约束：
- 生成的 HTML 必须自包含，不依赖 Tailwind CDN、Google Fonts 或外部图片；使用系统字体。可以用内联 CSS 和内联 JS。
- 不要硬编码真实邮箱、token、验证码、API key、手机号。access_token 只能从 localStorage.getItem('access_token') 读取。
- API base：优先 window.REHAB_API_BASE；如果没有，则使用 http://106.55.62.122:8011。所有认证 API 请求都带 Authorization: Bearer ${token}。
- 页面启动时调用 GET /api/rehab-arm/app/v1/me，并根据 data.profile / data.patient_view 渲染状态。
- 所有 fetch 的 POST 都必须明确写 method: 'POST' 和 Content-Type: application/json。

Profile 页面必须实现真实手机号绑定交互：
1. 显示云端账号状态、手机号区域、验证码输入、康复档案空状态。
2. 手机号输入按钮必须带 data-action="send-phone-code"，并通过 addEventListener('click', sendPhoneVerification) 绑定事件。
3. 绑定按钮必须带 data-action="confirm-phone-binding"，并通过 addEventListener('click', confirmPhoneVerification) 绑定事件。
4. sendPhoneVerification() 调 POST /api/rehab-arm/app/v1/account/phone-verifications，body: { phone, purpose: 'bind_account' }。
5. confirmPhoneVerification() 调 POST /api/rehab-arm/app/v1/account/phone-verifications/${verificationId}/confirm，body: { code }。
6. 需要完整状态：发送中、绑定中、60 秒倒计时 resendCooldown + setInterval、PHONE_CODE_INVALID、PHONE_CODE_ATTEMPTS_EXCEEDED、PHONE_CODE_RESEND_TOO_SOON + retry_after、PHONE_SMS_NOT_CONFIGURED、PHONE_SMS_DELIVERY_FAILED、成功后显示“手机号已验证”。代码中必须出现 phone_verified 和“手机号已验证”。
7. 测试环境如果接口返回 delivery_channel === 'debug_sms' 且 debug_code 存在，可以显示一个小号“测试验证码已生成”的辅助提示，但不要硬编码任何验证码；正式短信未配置时显示“短信服务暂不可用，请稍后重试”。

Device 页面必须改为真实蓝牙/后端绑定流程，不能再用静态假设备：
1. 删除任何 transitionToStep2()、showBoundError()、硬编码“领动康复手臂 v2”设备卡片。
2. “开始搜索设备”按钮必须带 data-action="scan-rehab-device"，并通过 addEventListener('click', scanRehabDevices) 绑定事件。
3. 设备列表中的绑定按钮必须带 data-action="bind-rehab-device"，并通过 addEventListener('click', bindSelectedDevice) 绑定事件。
4. JS 必须使用蓝牙桥：const bridge = window.RehabArmBluetoothBridge || (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.RehabArmBluetooth)。代码必须出现 RehabArmBluetoothBridge、requestBluetoothPermissions、scanDevices。
5. scanRehabDevices() 先 requestBluetoothPermissions()，再 scanDevices({ timeoutMs: 8000 })，根据返回设备数组渲染设备列表。设备对象字段兼容 id/address/deviceId/name/rssi。
6. 浏览器或 APK 未提供桥时，不要假装搜到设备；显示真实空态：“未检测到手机蓝牙能力，请使用最新版 App 并打开蓝牙权限”。代码中必须出现 bridgeMissing 或 bluetoothUnavailable，并出现“蓝牙权限”。
7. bindSelectedDevice(device) 调 POST /api/rehab-arm/app/v1/devices/bind，body: { m33_device_id: device.id || device.address || device.deviceId, ble_name: device.name || '康复设备', trust_status: 'trusted' }。
8. 绑定成功后进入第三步并显示“已绑定设备”，代码中必须出现 m33_device_id 或 deviceId。DEVICE_ALREADY_BOUND 显示“这台设备已绑定到其他账号，请联系康复师或客服协助”。
9. 页面可以显示准备/搜索/绑定完成三步进度，但所有进度必须由真实事件驱动，不允许硬编码已发现设备。

请只输出/更新这两个屏幕，不要改首页和康复师聊天页。
```

Stitch API returned a network failure on this edit attempt. Do not promote frontend assets until a successful Stitch download passes the gates below.

## Promotion Gates

```powershell
cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_frontend.py --source-dir artifacts\external\rehab-arm-mobile-stitch\apps\web\public\rehab-arm-mobile --output artifacts\rehab-mobile-frontend-release\phone-device-binding-source-gate-before.json
cloud\rehab-platform\.venv\Scripts\python.exe -m pytest tools\test_qa_rehab_mobile_l1_frontend.py tools\test_qa_rehab_mobile_l1_frontend_local_source.py cloud\rehab-platform\tests\test_app_compat.py::test_public_config_reports_current_apk_bluetooth_bridge_missing -q
```

Expected current pre-Stitch result: source gate fails on phone runtime handlers and real Bluetooth bridge requirements.
