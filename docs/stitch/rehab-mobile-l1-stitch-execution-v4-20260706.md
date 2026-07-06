# Stitch Execution Prompt V4 - Rehab Mobile L1 Closure

Generated: 2026-07-06T13:45:35Z

Repository: https://github.com/wenjunyong666/ai-
Branch: app/rehab-arm-mobile-stitch
Frontend path: apps/web/public/rehab-arm-mobile/

Edit only frontend files. Do not change backend code.

Live API base: http://106.55.62.122:8011
Deployed web base: http://106.55.62.122:3001/rehab-arm-mobile
Sanitized API fixture: docs/stitch/rehab-mobile-l1-api-fixture-20260706.json
Runbook: docs/stitch/rehab-mobile-l1-stitch-runbook-20260706.md

Do not hard-code fixture values. Use the fixture only to understand response shape and required field names.

## Current Status
- Stitch blockers: home_next_step, phone_binding, device_binding, ask_therapist_safety, profile_no_fake_debug, browser_qa_evidence, frontend_l1_gate
- Non-Stitch blockers: agent_cloud_model

Important: Stitch cannot clear agent_cloud_model by UI work alone. The frontend must still render model readiness honestly.

## Current In-App Browser Failure Evidence
Use these screenshots as visual references for what must change. They are not L1 success evidence.
- home: docs\qa\rehab-mobile-20260706\browser-current-fail-20260706\current-fail-home-clip-390x844.png (390x844), counts_for_l1_success = false
- ai-plan: docs\qa\rehab-mobile-20260706\browser-current-fail-20260706\current-fail-ai-plan-clip-390x844.png (390x844), counts_for_l1_success = false
- device: docs\qa\rehab-mobile-20260706\browser-current-fail-20260706\current-fail-device-clip2-390x844.png (390x844), counts_for_l1_success = false
- profile: docs\qa\rehab-mobile-20260706\browser-current-fail-20260706\current-fail-profile-clip2-390x844.png (390x844), counts_for_l1_success = false

## Frontend Failures To Fix

### L1-HOME-STATIC-001
Summary: Home static page is patient-facing and free of raw workflow/debug terms.
Must add visible/user-facing evidence:
- 问康复师
Must remove from normal user screens:
- M33
- M55
- RoboRehab Controller
Current visible text sample to replace:
> RoboRehab Controller clinical_notes RoboRehab Controller smart_toy 晚上好，今天适合做轻量屈肘训练 medical_information 康复阶段：亚急性期 front_hand 患侧：左侧 timer 今日目标：30 分钟 M33 ACTIVE 今日目标动作 屈肘训练 时长 20 mins 强度 低 进度 45% play_arrow 开始训练 (需 M33 授权) verified_user 状态：M33 已允许执行 emergency 急停已就绪 设备状态 bluetooth M33 BLE 已连接 sensors M55 EMG 激活 precision_manufacturing Arm 安全 cloud_sync Cloud 已同步 最近训练结果快照 完成度 95% 肌肉疲劳 低 psychiatry AI 建议 "动作稳定性极佳，建议维持当前强度" robot_2 home_health 首页 exercise 训练 monitoring 肌电 precision_manufacturing 设备 per

### L1-PROFILE-STATIC-001
Summary: Profile static page is cloud-account oriented and does not show demo medical data.
Must add visible/user-facing evidence:
- 我的康复档案
- 手机号
- 绑定手机号
- 验证码
Must remove from normal user screens:
- M33
- M55
- 患者 A
- ID: 8829
- 避免过度伸展
- RoboRehab Controller
Current visible text sample to replace:
> RoboRehab Controller - My Profile clinical_notes RoboRehab Controller System OK smart_toy 患者 A ID: 8829 relax 第二阶段康复中 warning 医疗约束 避免过度伸展 > 120° 已连接设备 settings_input_component precision_manufacturing M33 康复机械臂 EXO-L-01 激活 sensors M55 肌电传感器 EMG-PATCH 激活 add 配对新设备 calendar_month 训练活动 同步后显示 登录后同步真实训练记录。 暂无本周训练记录 查看日志 cloud_sync 云端平台 同步中 record_voice_over 小智语音 已开启 supervisor_account 权限管理 康复师/家属 shield_lock 数据隐私与通知 home_health 首页 exercise 训练 monitoring 肌电 precision_manufacturing 设备 person 我的

### L1-DEVICE-STATIC-001
Summary: Device page avoids debug transport language in normal user flow.
Must add visible/user-facing evidence:
- 绑定设备
- 打开康复设备电源
Must remove from normal user screens:
- M33
- M55
- UUID
- Gatekeeper
Current visible text sample to replace:
> 设备连接 - RoboRehab 控制器 clinical_notes RoboRehab 控制器 smart_toy check_circle 系统状态 M33 状态：准备就绪，允许安全训练 系统架构图 smartphone 手机 APP hub 安全门控 (Gatekeeper) memory M55 dns NanoPi precision_manufacturing 机械臂 当前连接 已扫描蓝牙 bluetooth_connected M33 康复机械臂 已连接 monitor_heart 心跳状态 M33: 120ms 云端: 45ms battery_charging_80 电源状态 机械臂电量: 85% sync 一键同步训练计划 需要 M33 医疗系统授权。 bug_report 蓝牙调试 / 实机验证 bug_report 调试信息 expand_more 服务 UUID: 0000FFF0-0000-1000-8000-00805F9B34FB 发送特征值: 0000FFF1-... 收发数据包: 14205 / 8432 错误日志 (最近 1 小时): 0 rob

### L1-AGENT-STATIC-001
Summary: Agent page exposes the rehab therapist entry.
Must add visible/user-facing evidence:
- 问康复师
Current visible text sample to replace:
> 康复智能体 - 灵动康复 ArmControl arrow_back 康复智能体 云端同步 warning AI 只生成训练草稿；接受后还需要设备审核和训练前检查，不能直接启动机械臂。 terminal 智能体规划输入 肌电：等待读取 意图：等待读取 草稿：等待生成 疼痛自评 2/10 疲劳状态 轻微 中等 明显疲劳 memory 生成 AI 草稿 receipt_long 训练草稿处方 草稿 等待生成训练草稿 训练量 登录后生成 助力 / 速度 - report 安全提示： 草稿接受后仍需同步到设备、等待设备审核，并通过训练前检查后才能开始记录。 智能体状态： AI 规划会调用后端 /ai-training-drafts/generate。模型未配置时会明确显示规则回退，不伪装真实 AI 调用。 check_circle 接受为训练计划 闭环执行状态 check 生成 AI 草稿 等待后端草稿 人工确认草稿 接受后仅生成普通训练计划 生成训练计划 同步到设备 等待设备审核 Preflight 后开始记录 等待训练前检查 home_health 首页 terminal AI preci

### L1-FRONTEND-INTEGRATION-001
Summary: Frontend source is wired to the required auth, patient_view, phone, device, and Agent API contracts.
Missing source/API requirements:
- patient_view_home
- patient_view_profile
- patient_view_device
- patient_view_agent
- ask_therapist_accessibility
- phone_verification_start
- phone_verification_confirm
- phone_resend_cooldown
- phone_sms_error_states
- device_already_bound
- agent_messages
- agent_unsafe_refusal
- agent_model_status

## Integration Gaps
- patient_view_home
- patient_view_profile
- patient_view_device
- patient_view_agent
- ask_therapist_accessibility
- phone_verification_start
- phone_verification_confirm
- phone_resend_cooldown
- phone_sms_error_states
- device_already_bound
- agent_messages
- agent_unsafe_refusal
- agent_model_status

## Required Final Browser QA Evidence
Currently missing exact L1 success screenshots:
- home_first_screen
- ask_therapist_chat
- unsafe_agent_refusal
- device_binding_wizard
- profile_phone_medical
After Stitch deploys the frontend, Codex must capture these exact final screenshots:
- home_first_screen: l1-home-390.png at 390x844 showing one clear next action
- ask_therapist_chat: l1-ask-therapist-chat-390.png at 390x844 showing 问康复师, chat input, safe answer
- unsafe_agent_refusal: l1-unsafe-agent-refusal-390.png at 390x844 showing protective Chinese refusal, no direct motion control
- device_binding_wizard: l1-device-binding-wizard-390.png at 390x844 showing 绑定设备, 打开康复设备电源
- profile_phone_medical: l1-profile-phone-medical-390.png at 390x844 showing cloud account, verified phone, safe medical empty state

## After Stitch Hands Back Frontend Files
Codex will run the local frontend L1 preflight and package the generated assets before cloud deployment:
```powershell
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_frontend.py --source-dir apps/web/public/rehab-arm-mobile
.\cloud\rehab-platform\.venv\Scripts\python.exe tools/prepare_rehab_mobile_frontend_release.py --source-dir apps/web/public/rehab-arm-mobile --output-dir artifacts/rehab-mobile-frontend-release
```

## Codex Verification Commands
Codex will reject the frontend until these pass:
```powershell
$env:REHAB_QA_EMAIL='3245056131@qq.com'
$env:REHAB_QA_PASSWORD='1234'
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_release.py
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_objective_audit.py
curl.exe -I -sS http://106.55.62.122:3001/downloads/rehab-arm/lingdong-rehab-arm-debug.apk
```

Deliver a patient-facing mobile app first screen, not a debug console or engineering workflow.
