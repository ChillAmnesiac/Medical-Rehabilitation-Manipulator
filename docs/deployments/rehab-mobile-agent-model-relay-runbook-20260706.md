# Rehab Mobile Agent Model Relay Runbook - 2026-07-06

This runbook closes the `agent_cloud_model` L1 blocker after a real cloud model
endpoint and API key are available. The backend supports `openai_compatible`
chat completions and Google `gemini` generateContent.

## Current Staging State

- Cloud API: `http://106.55.62.122:8011`
- Web app: `http://106.55.62.122:3001/rehab-arm-mobile`
- Latest verified backend build: `d2f81c92`
- Current Agent mode: `fallback_rule_based`
- Current reason: `external_model_not_configured`
- Current model relay config on the server:
  - `REHAB_ARM_MODEL_RELAY_PROVIDER`: empty
  - `REHAB_ARM_MODEL_RELAY_BASE_URL`: empty
  - `REHAB_ARM_MODEL_RELAY_MODEL`: empty
  - `REHAB_ARM_MODEL_RELAY_API_KEY`: empty
  - `REHAB_ARM_MODEL_RELAY_EXTERNAL_ENABLED`: false
  - XiaoZhi ASR/TTS model keys: empty

Do not mark L1 as user-ready while the Agent is in this fallback mode.

## Preflight Provider Before Configuring

Before saving any model relay key to staging, smoke-test the provider directly.
This prevents an invalid or product-scoped key from being persisted into the app.
The preflight tool prints a JSON summary and redacts the API key.

OpenAI-compatible preflight:

```powershell
$env:REHAB_MODEL_RELAY_PROVIDER = 'openai_compatible'
$env:REHAB_MODEL_RELAY_BASE_URL = 'https://api.openai.com/v1'
$env:REHAB_MODEL_RELAY_MODEL = '<model-name>'
$env:REHAB_MODEL_RELAY_API_KEY = '<real-api-key>'
$env:REHAB_MODEL_SMOKE_MESSAGE = '今天训练后肩膀有点酸痛，明天还能继续康复训练吗？'
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\smoke_rehab_model_provider.py
```

Gemini preflight:

```powershell
$env:REHAB_MODEL_RELAY_PROVIDER = 'gemini'
$env:REHAB_MODEL_RELAY_MODEL = '<gemini-model-name>'
$env:REHAB_MODEL_RELAY_API_KEY = '<real-google-ai-api-key>'
$env:REHAB_MODEL_SMOKE_MESSAGE = '今天训练后肩膀有点酸痛，明天还能继续康复训练吗？'
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\smoke_rehab_model_provider.py
```

Only continue to `tools\configure_rehab_model_relay.py` when the preflight exits
with code `0`, `status = ok`, and `answer_present = true`.

2026-07-06 evidence: the user-provided Google/Stitch API key was tested against
Gemini `generateContent` with `gemini-3.5-flash` and `gemini-2.5-flash`. Both
preflights returned `403 provider_http_error`, so the key was not saved to
staging and `agent_cloud_model` remains blocked.

## Configure Through API

Use the project relay config endpoint. The script below logs in, updates the
relay config, and sends a real Agent smoke question. It exits successfully only
when `data.model_status.mode` is `cloud_model`.

OpenAI-compatible PowerShell:

```powershell
$env:REHAB_QA_EMAIL = '3245056131@qq.com'
$env:REHAB_QA_PASSWORD = '1234'
$env:REHAB_MODEL_RELAY_PROJECT_ID = 'e201f41c-25a6-46e1-baf8-be6dcb83284c'
$env:REHAB_MODEL_RELAY_PROVIDER = 'openai_compatible'
$env:REHAB_MODEL_RELAY_BASE_URL = 'https://api.openai.com/v1'
$env:REHAB_MODEL_RELAY_MODEL = '<model-name>'
$env:REHAB_MODEL_RELAY_API_KEY = '<real-api-key>'
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\configure_rehab_model_relay.py
```

Gemini PowerShell:

```powershell
$env:REHAB_QA_EMAIL = '3245056131@qq.com'
$env:REHAB_QA_PASSWORD = '1234'
$env:REHAB_MODEL_RELAY_PROJECT_ID = 'e201f41c-25a6-46e1-baf8-be6dcb83284c'
$env:REHAB_MODEL_RELAY_PROVIDER = 'gemini'
$env:REHAB_MODEL_RELAY_MODEL = '<gemini-model-name>'
$env:REHAB_MODEL_RELAY_API_KEY = '<real-google-ai-api-key>'
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\configure_rehab_model_relay.py
```

For `provider = gemini`, the config tool defaults `base_url` to
`https://generativelanguage.googleapis.com/v1beta` when it is not supplied.

The script redacts `REHAB_MODEL_RELAY_API_KEY` from output. Do not paste the
real key into docs, screenshots, commits, or chat.

## Configure Through Server Env

If API config is unavailable, update the cloud server `.env` with:

```dotenv
REHAB_ARM_MODEL_RELAY_PROVIDER=openai_compatible
REHAB_ARM_MODEL_RELAY_BASE_URL=https://api.openai.com/v1
REHAB_ARM_MODEL_RELAY_MODEL=<model-name>
REHAB_ARM_MODEL_RELAY_API_KEY=<real-api-key>
REHAB_ARM_MODEL_RELAY_EXTERNAL_ENABLED=true
```

Gemini server `.env` example:

```dotenv
REHAB_ARM_MODEL_RELAY_PROVIDER=gemini
REHAB_ARM_MODEL_RELAY_BASE_URL=https://generativelanguage.googleapis.com/v1beta
REHAB_ARM_MODEL_RELAY_MODEL=<gemini-model-name>
REHAB_ARM_MODEL_RELAY_API_KEY=<real-google-ai-api-key>
REHAB_ARM_MODEL_RELAY_EXTERNAL_ENABLED=true
```

Then restart the API process and verify `/health` reports the new deployment
metadata. The config API clears settings cache when it writes `.env`; direct env
edits still require a process restart.

## Acceptance Commands

```powershell
$env:REHAB_QA_EMAIL = '3245056131@qq.com'
$env:REHAB_QA_PASSWORD = '1234'
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_acceptance.py
.\cloud\rehab-platform\.venv\Scripts\python.exe tools\qa_rehab_mobile_l1_release.py
```

Expected Agent-specific results:

- `P1-AGENT-CONFIG-001`: `PASS`
- `P1-AGENT-MODEL-001`: `PASS`
- `summary.blocking_gates` does not include `agent_cloud_model`
- Agent safe answer contains `data.model_status.mode = cloud_model`
- Public config contains `data.agent.model_readiness.mode = cloud_model_configured`
- Public config and logs do not expose the API key

Frontend L1 may still fail until Stitch replaces the static/debug pages with
the `patient_view` and Agent chat contract.
