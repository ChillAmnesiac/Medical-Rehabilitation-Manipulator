# 灵动康复 App 演示账号（云端联调）

日期：2026-07-21  
API：`http://106.55.62.122:8011`  
用途：现场/开发联调「智能助手」与需登录的患者端接口；**不是**模型服务密钥，也不会写入固件。

## 账号

| 字段 | 值 |
|---|---|
| 邮箱 | `demo.rehab@lingdong.local` |
| 密码 | `DemoRehab2026!` |
| 显示名 | Demo Rehab |
| user id | `513fd154-d6aa-4b5b-ae23-8671f49a0e07` |
| 角色 | `member` |

创建接口：`POST /api/auth/register`（body 需要 `email` / `password` / `name`）。  
登录接口：`POST /api/auth/session`（body：`email` / `password`）。  
App 登录后把 `data.access_token` 存到 `localStorage.access_token`，请求头为 `Authorization: Bearer <token>`。

## 已验证

2026-07-21 对线上 API 的验证：

1. 注册成功（200）。
2. 登录成功，返回 `access_token`。
3. `POST /api/rehab-arm/app/v1/agent/messages`，消息 `测试`，返回 200：
   - 有中文 `answer`
   - `model_status.status = external_used`
   - `provider = qwen` / `model = qwen-plus`
   - 控制边界：`agent_advice_only_not_motion_permission`（仅建议，不直接动电机）

## App 内操作

1. 打开「灵动康复」→ 进入需要云端的页面（智能助手 / 个人中心登录区）。
2. 邮箱：`demo.rehab@lingdong.local`
3. 密码：`DemoRehab2026!`
4. 点登录；成功后发一句「测试」，应出现康复师回复而不是 `AUTH_REQUIRED`。

## 安全说明

- 本账号仅供演示与联调；不要用于真实患者数据。
- 若仓库公开且需轮换密码：重新 `register` 新邮箱，或在云端后台禁用该用户后更新本文。
- 模型 API Key 只在云端环境变量中，**不要**写进 App 或本文。
- 电机安全仍由 M33 执行层负责；Agent 回复不是运动许可。

## 快速 API 自检

```powershell
python -c "
import json, urllib.request
base='http://106.55.62.122:8011'
login=json.dumps({'email':'demo.rehab@lingdong.local','password':'DemoRehab2026!'}).encode()
req=urllib.request.Request(base+'/api/auth/session', data=login, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=20) as r:
    token=json.load(r)['data']['access_token']
body=json.dumps({'message':'测试','context_snapshot':{'source':'docs_smoke'}}).encode()
req=urllib.request.Request(base+'/api/rehab-arm/app/v1/agent/messages', data=body, headers={'Content-Type':'application/json','Authorization':'Bearer '+token}, method='POST')
with urllib.request.urlopen(req, timeout=60) as r:
    print(json.load(r)['data']['answer'][:200])
"
```
