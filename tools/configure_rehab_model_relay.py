#!/usr/bin/env python3
"""Configure and smoke-test the rehab app cloud-model relay.

The script never prints the model API key. It is intended for staging release
ops after a real OpenAI-compatible model endpoint/key is available.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_API_BASE = "http://106.55.62.122:8011"
DEFAULT_AGENT_MESSAGE = "今天训练后有点酸痛，明天还能继续训练吗？"
DEFAULT_PROVIDER_BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta",
    "google_gemini": "https://generativelanguage.googleapis.com/v1beta",
}


class Client:
    def __init__(self, api_base: str, timeout: int) -> None:
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> tuple[int, dict[str, Any] | str | None]:
        body = None
        headers: dict[str, str] = {}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(self.api_base + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, _parse_body(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, _parse_body(exc.read())


def _parse_body(raw: bytes) -> dict[str, Any] | str | None:
    text = raw.decode("utf-8", errors="replace")
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text
    return parsed


def require_text(name: str, value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        raise ValueError(f"{name} is required")
    return text


def build_config_payload(
    *,
    provider: str,
    base_url: str,
    model: str,
    api_key: str,
    external_enabled: bool = True,
) -> dict[str, Any]:
    provider_text = require_text("provider", provider)
    base_url_text = (base_url or "").strip() or DEFAULT_PROVIDER_BASE_URLS.get(provider_text.casefold())
    return {
        "provider": provider_text,
        "base_url": require_text("base_url", base_url_text).rstrip("/"),
        "model": require_text("model", model),
        "api_key": require_text("api_key", api_key),
        "external_enabled": bool(external_enabled),
    }


def summarize_config_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": payload.get("provider"),
        "base_url": payload.get("base_url"),
        "model": payload.get("model"),
        "external_enabled": payload.get("external_enabled"),
        "api_key": "<redacted>" if payload.get("api_key") else None,
    }


def model_relay_config_path(project_id: str) -> str:
    quoted = urllib.parse.quote(require_text("project_id", project_id), safe="")
    return f"/api/rehab-arm/v1/projects/{quoted}/model-relay/config"


def _data(value: Any) -> dict[str, Any]:
    if isinstance(value, dict) and isinstance(value.get("data"), dict):
        return value["data"]
    return {}


def agent_smoke_is_cloud_model(value: Any) -> tuple[bool, dict[str, Any]]:
    model_status = _data(value).get("model_status")
    if not isinstance(model_status, dict):
        return False, {"mode": None, "reason": "model_status_missing"}
    detail = {
        "mode": model_status.get("mode"),
        "configured": model_status.get("configured"),
        "provider": model_status.get("provider"),
        "model": model_status.get("model"),
        "reason": model_status.get("fallback_reason"),
    }
    return detail["mode"] == "cloud_model" and bool(detail["model"]), detail


def login(client: Client, email: str, password: str) -> str:
    status, body = client.request("POST", "/api/auth/session", {"email": email, "password": password})
    token = _data(body).get("access_token") if isinstance(body, dict) else None
    if status != 200 or not token:
        raise RuntimeError(f"login failed with status {status}")
    return str(token)


def configure_model_relay(client: Client, project_id: str, token: str, payload: dict[str, Any]) -> tuple[int, Any]:
    return client.request("PUT", model_relay_config_path(project_id), payload, token)


def smoke_agent(client: Client, token: str, message: str) -> tuple[int, Any, bool, dict[str, Any]]:
    status, body = client.request("POST", "/api/rehab-arm/app/v1/agent/messages", {"message": message}, token)
    ok, detail = agent_smoke_is_cloud_model(body)
    return status, body, ok, detail


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    payload = build_config_payload(
        provider=args.provider,
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key,
        external_enabled=not args.disable_external,
    )
    client = Client(args.api_base, args.timeout)
    token = login(client, args.email, args.password)
    config_status, config_body = configure_model_relay(client, args.project_id, token, payload)
    summary: dict[str, Any] = {
        "config_request": summarize_config_payload(payload),
        "config_status_code": config_status,
        "config_response": config_body,
    }
    if config_status < 200 or config_status >= 300:
        return 2, summary
    if args.skip_agent_smoke:
        return 0, summary
    smoke_status, smoke_body, cloud_ready, model_detail = smoke_agent(client, token, args.agent_message)
    summary["agent_smoke"] = {
        "status_code": smoke_status,
        "cloud_ready": cloud_ready,
        "model_status": model_detail,
        "answer_present": bool(_data(smoke_body).get("answer")) if isinstance(smoke_body, dict) else False,
    }
    return (0 if smoke_status == 200 and cloud_ready else 3), summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", default=os.getenv("REHAB_QA_API_BASE", DEFAULT_API_BASE))
    parser.add_argument("--project-id", default=os.getenv("REHAB_MODEL_RELAY_PROJECT_ID"))
    parser.add_argument("--email", default=os.getenv("REHAB_QA_EMAIL"))
    parser.add_argument("--password", default=os.getenv("REHAB_QA_PASSWORD"))
    parser.add_argument("--provider", default=os.getenv("REHAB_MODEL_RELAY_PROVIDER", "openai_compatible"))
    parser.add_argument("--base-url", default=os.getenv("REHAB_MODEL_RELAY_BASE_URL"))
    parser.add_argument("--model", default=os.getenv("REHAB_MODEL_RELAY_MODEL"))
    parser.add_argument("--api-key", default=os.getenv("REHAB_MODEL_RELAY_API_KEY"))
    parser.add_argument("--disable-external", action="store_true")
    parser.add_argument("--skip-agent-smoke", action="store_true")
    parser.add_argument("--agent-message", default=os.getenv("REHAB_AGENT_SMOKE_MESSAGE", DEFAULT_AGENT_MESSAGE))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REHAB_QA_TIMEOUT", "20")))
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        exit_code, summary = run(parse_args(argv))
    except (RuntimeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
